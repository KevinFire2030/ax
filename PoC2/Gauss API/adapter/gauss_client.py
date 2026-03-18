from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class GaussApiError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


@dataclass
class GaussConfig:
    endpoint_url: str
    client_header: str
    token_header: str
    user_email: str | None = None
    default_model_id: str | None = None

    timeout_seconds: int = 60
    max_retries: int = 2
    retry_backoff_seconds: float = 1.5


def _env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return default if v is None else str(v)


def load_config_from_env() -> GaussConfig:
    endpoint = _env("ENDPOINT_URL").strip().rstrip("/")
    if not endpoint:
        raise GaussApiError("Missing ENDPOINT_URL in .env")

    client_header = _env("x-generative-ai-client").strip()
    token_header = _env("x-openapi-token").strip()
    if not client_header or not token_header:
        raise GaussApiError("Missing required headers in .env: x-generative-ai-client, x-openapi-token")

    user_email = _env("x-generative-ai-user-email").strip() or None
    default_model_id = _env("GAUSS_TEXT_MODEL_ID").strip() or None

    timeout_seconds = int(_env("HTTP_TIMEOUT_SECONDS", "60"))
    max_retries = int(_env("HTTP_MAX_RETRIES", "2"))
    retry_backoff_seconds = float(_env("HTTP_RETRY_BACKOFF_SECONDS", "1.5"))

    return GaussConfig(
        endpoint_url=endpoint,
        client_header=client_header,
        token_header=token_header,
        user_email=user_email,
        default_model_id=default_model_id,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )


class GaussClient:
    """Minimal Gauss Chat APIs client.

    - Uses: POST /openapi/chat/v1/messages
    - Non-stream only (isStream=false) for PoC simplicity.
    """

    def __init__(self, cfg: GaussConfig):
        self.cfg = cfg

    def _headers(self) -> Dict[str, str]:
        h = {
            "x-generative-ai-client": self.cfg.client_header,
            "x-openapi-token": self.cfg.token_header,
        }
        if self.cfg.user_email:
            h["x-generative-ai-user-email"] = self.cfg.user_email
        return h

    def _url(self, path: str) -> str:
        return f"{self.cfg.endpoint_url}{path}"

    def get_models(self) -> Any:
        url = self._url("/openapi/chat/v1/models")
        return self._request_json("GET", url)

    def get_all_models(self) -> Any:
        url = self._url("/openapi/chat/v1/all-models")
        return self._request_json("GET", url)

    def messages(
        self,
        *,
        contents: List[str],
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        is_stream: bool = False,
    ) -> Dict[str, Any]:
        if is_stream:
            # Keep adapter simple for PoC.
            raise GaussApiError("Streaming(isStream=true) is not supported by this PoC adapter")

        mid = (model_id or self.cfg.default_model_id or "").strip()
        if not mid:
            raise GaussApiError("Missing model_id. Provide arg or set GAUSS_TEXT_MODEL_ID in .env")

        payload: Dict[str, Any] = {
            "modelIds": [mid],
            "contents": contents,
            "isStream": False,
        }
        if system_prompt:
            payload["systemPrompt"] = system_prompt
        if llm_config:
            payload["llmConfig"] = llm_config

        url = self._url("/openapi/chat/v1/messages")
        return self._request_json("POST", url, json_body=payload)

    def generate_text(
        self,
        prompt: str,
        *,
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        resp = self.messages(
            contents=[prompt],
            model_id=model_id,
            system_prompt=system_prompt,
            llm_config=llm_config,
            is_stream=False,
        )
        # spec response: { content: "..." }
        return str(resp.get("content", ""))

    def generate_json(
        self,
        prompt: str,
        *,
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = self.generate_text(prompt, model_id=model_id, system_prompt=system_prompt, llm_config=llm_config)
        try:
            return json.loads(text)
        except Exception as e:
            raise GaussApiError(
                f"Model output is not valid JSON: {e}",
                status_code=None,
                response_text=text,
            )

    def _request_json(self, method: str, url: str, json_body: Dict[str, Any] | None = None) -> Any:
        last_err: Exception | None = None

        for attempt in range(self.cfg.max_retries + 1):
            try:
                if method.upper() == "GET":
                    r = requests.get(url, headers=self._headers(), timeout=self.cfg.timeout_seconds)
                else:
                    r = requests.request(
                        method.upper(),
                        url,
                        headers={**self._headers(), "Content-Type": "application/json"},
                        json=json_body,
                        timeout=self.cfg.timeout_seconds,
                    )

                if r.status_code >= 400:
                    raise GaussApiError(
                        f"HTTP {r.status_code} calling {url}",
                        status_code=r.status_code,
                        response_text=r.text,
                    )

                # Some APIs return 200 with responseCode != R20000. We don't enforce here.
                return r.json()

            except GaussApiError as e:
                last_err = e
            except Exception as e:
                last_err = e

            if attempt < self.cfg.max_retries:
                time.sleep(self.cfg.retry_backoff_seconds * (attempt + 1))

        if isinstance(last_err, GaussApiError):
            raise last_err
        raise GaussApiError(f"Request failed after retries: {last_err}")
