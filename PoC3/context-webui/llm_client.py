from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from rate_limiter import RateLimiter


class LLMError(RuntimeError):
    pass


def _extract_json_text(s: str) -> str:
    t = (s or "").strip()
    if t.lower().startswith("json"):
        t = t[4:].lstrip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
        if t.lower().startswith("json"):
            t = t[4:].lstrip()
    if "{" in t and "}" in t:
        a = t.find("{")
        b = t.rfind("}")
        if 0 <= a < b:
            t = t[a : b + 1]
    return t


@dataclass
class GaussConfig:
    endpoint_url: str
    client_header: str
    token_header: str
    user_email: str = ""
    text_model_id: str = ""
    system_prompt: str = ""
    rpm: int = 3
    timeout_seconds: int = 60
    max_retries: int = 2
    retry_backoff_seconds: float = 2.0


@dataclass
class OpenAICompatConfig:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int = 60
    max_retries: int = 2
    retry_backoff_seconds: float = 2.0
    rpm: int = 0


class LLMClient:
    def __init__(self, provider: str, *, gauss: GaussConfig | None = None, openai: OpenAICompatConfig | None = None, rpm: int = 0):
        self.provider = (provider or "gauss").strip().lower()
        self.gauss = gauss
        self.openai = openai
        effective_rpm = int(rpm) if int(rpm) > 0 else int((gauss.rpm if self.provider == "gauss" and gauss else 0) or (openai.rpm if self.provider == "openai" and openai else 0) or 0)
        self.limiter = RateLimiter(effective_rpm)

    def call_json(self, prompt: str) -> Dict[str, Any]:
        if self.provider == "gauss":
            if not self.gauss:
                raise LLMError("Gauss config missing")
            return self._call_gauss(prompt)
        if self.provider == "openai":
            if not self.openai:
                raise LLMError("OpenAI config missing")
            return self._call_openai_compat(prompt)
        raise LLMError(f"Unknown provider: {self.provider}")

    def _call_gauss(self, prompt: str) -> Dict[str, Any]:
        cfg = self.gauss
        assert cfg is not None

        if not cfg.endpoint_url or not cfg.client_header or not cfg.token_header or not cfg.text_model_id:
            raise LLMError("Gauss env missing: endpoint/client/token/modelId")

        url = cfg.endpoint_url.rstrip("/") + "/openapi/chat/v1/messages"
        headers = {
            "x-generative-ai-client": cfg.client_header,
            "x-openapi-token": cfg.token_header,
            "Content-Type": "application/json",
        }
        if cfg.user_email:
            headers["x-generative-ai-user-email"] = cfg.user_email

        payload: Dict[str, Any] = {
            "modelIds": [cfg.text_model_id],
            "contents": [prompt],
            "isStream": False,
        }
        if cfg.system_prompt:
            payload["systemPrompt"] = cfg.system_prompt

        last_err: Exception | None = None

        for attempt in range(cfg.max_retries + 1):
            try:
                self.limiter.wait()
                r = requests.post(url, headers=headers, json=payload, timeout=cfg.timeout_seconds)
                if r.status_code == 429:
                    # best effort: respect Retry-After
                    ra = r.headers.get("Retry-After")
                    sleep_sec = float(ra) if ra and ra.isdigit() else max(5.0, self.limiter.interval_sec)
                    time.sleep(sleep_sec)
                    raise LLMError(f"429 Too Many Requests (slept {sleep_sec}s)")
                r.raise_for_status()
                resp = r.json()
                content = resp.get("content", "")
                if not isinstance(content, str):
                    content = str(content)
                cleaned = _extract_json_text(content)
                data = json.loads(cleaned)
                data["llm_model"] = "gauss"
                data["gauss_status"] = resp.get("status")
                data["gauss_responseCode"] = resp.get("responseCode")
                return data
            except Exception as e:
                last_err = e
                if attempt >= cfg.max_retries:
                    break
                time.sleep(cfg.retry_backoff_seconds * (attempt + 1))

        raise LLMError(f"Gauss call failed: {last_err}")

    def _call_openai_compat(self, prompt: str) -> Dict[str, Any]:
        cfg = self.openai
        assert cfg is not None
        if not cfg.api_key or not cfg.base_url or not cfg.model:
            raise LLMError("OpenAI env missing: api_key/base_url/model")

        # OpenAI Chat Completions compatible
        url = cfg.base_url.rstrip("/") + "/v1/chat/completions"
        headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": cfg.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }

        last_err: Exception | None = None
        for attempt in range(cfg.max_retries + 1):
            try:
                self.limiter.wait()
                r = requests.post(url, headers=headers, json=payload, timeout=cfg.timeout_seconds)
                if r.status_code == 429:
                    ra = r.headers.get("Retry-After")
                    sleep_sec = float(ra) if ra and ra.isdigit() else max(5.0, self.limiter.interval_sec)
                    time.sleep(sleep_sec)
                    raise LLMError(f"429 Too Many Requests (slept {sleep_sec}s)")
                r.raise_for_status()
                resp = r.json()
                text = resp["choices"][0]["message"]["content"]
                cleaned = _extract_json_text(text)
                data = json.loads(cleaned)
                data["llm_model"] = cfg.model
                return data
            except Exception as e:
                last_err = e
                if attempt >= cfg.max_retries:
                    break
                time.sleep(cfg.retry_backoff_seconds * (attempt + 1))

        raise LLMError(f"OpenAI call failed: {last_err}")


def client_from_env() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "gauss").strip().lower()
    rpm = int(os.getenv("RPM", "0") or 0)

    gauss = GaussConfig(
        endpoint_url=os.getenv("GAUSS_ENDPOINT_URL", "").strip(),
        client_header=os.getenv("GAUSS_CLIENT_HEADER", "").strip(),
        token_header=os.getenv("GAUSS_TOKEN_HEADER", "").strip(),
        user_email=os.getenv("GAUSS_USER_EMAIL", "").strip(),
        text_model_id=os.getenv("GAUSS_TEXT_MODEL_ID", "").strip(),
        system_prompt=os.getenv("GAUSS_SYSTEM_PROMPT", "").strip(),
        rpm=int(os.getenv("GAUSS_RPM", "3") or 3),
        timeout_seconds=int(os.getenv("OPENAI_TIMEOUT_SECONDS", "60") or 60),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2") or 2),
        retry_backoff_seconds=float(os.getenv("OPENAI_RETRY_BACKOFF_SECONDS", "2.0") or 2.0),
    )

    openai = OpenAICompatConfig(
        api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
        model=os.getenv("OPENAI_MODEL", "gpt-5.4").strip(),
        timeout_seconds=int(os.getenv("OPENAI_TIMEOUT_SECONDS", "60") or 60),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2") or 2),
        retry_backoff_seconds=float(os.getenv("OPENAI_RETRY_BACKOFF_SECONDS", "2.0") or 2.0),
        rpm=0,
    )

    return LLMClient(provider, gauss=gauss, openai=openai, rpm=rpm)
