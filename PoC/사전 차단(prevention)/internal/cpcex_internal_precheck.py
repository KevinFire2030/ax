"""CPCex Internal Pre-check (PoC)

목적
- CPCex '전송 직전' 서버 로직에서 LLM(OpenAI)을 직접 호출해 사전 검사 수행
- 훅(Webhook) 서버 호출 없이, CPCex 내부에서 allow/warn/block 결정을 내리는 형태

입력(예시 payload)
{
  "mail_id": "DX...",
  "sender_dept": "부품품질그룹(MX)",
  "sender_id": "user",
  "subject": "...",
  "body_text": "...",
  "recipients": [{"recipient_company":"...", "is_external": true}],
  "attachments": [{"filename":"a.x_t", "extension":"x_t"}],
  "timestamp": "..."
}

출력
{
  "ok": true,
  "policy_action": "allow|warn|block",
  "risk_level": 0-5,
  "risk_score": 0-100,
  "evidence": [...],
  "reason": "...",
  "approval_route": [..]  # block일 때
}

의존성
  pip install openai python-dotenv

주의
- PoC 골격 코드입니다. 운영 시에는 보안(키관리), 로깅/감사, PII 마스킹, 레이트리밋, 장애대응 필요.
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


BASE64_RE = re.compile(
    r"data:image/[^;]+;base64,[A-Za-z0-9+/=\n\r]+",
    re.IGNORECASE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    return HTML_TAG_RE.sub(" ", text)


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(str(path.resolve()))
    return path.read_text(encoding="utf-8")


def load_approval_routing(path: Path) -> dict:
    if not path.exists():
        return {"default": {}, "by_sender_dept": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def build_approval_route(sender_dept: str, routing: dict) -> List[str]:
    sender_dept = (sender_dept or "").strip()
    default = routing.get("default", {})
    by_dept = routing.get("by_sender_dept", {})
    rule = by_dept.get(sender_dept, {}) if isinstance(by_dept, dict) else {}

    s1 = rule.get("stage1_team_compliance") or default.get("stage1_team_compliance") or "(팀별 준법담당) TBD"
    s2 = rule.get("stage2_biz_compliance") or default.get("stage2_biz_compliance") or "(사업부 준법담당) TBD"
    s3 = rule.get("stage3_dept_head") or default.get("stage3_dept_head") or "(부서장) TBD"

    return [
        f"1) 합의 - 팀별 준법담당: {s1}",
        f"2) 합의 - 사업부 준법담당: {s2}",
        f"3) 결재 - 부서장: {s3}",
    ]


@dataclass
class Settings:
    api_key: str
    model: str
    temperature: float
    max_output_tokens: int
    timeout_seconds: int
    fail_open_policy: str
    warn_level: int
    block_level: int
    prompt_template: str
    approval_routing: dict
    cache_enabled: bool
    cache_dir: Path
    cache_key_col: str


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is empty")

    model = os.getenv("OPENAI_MODEL", "gpt-5.2").strip()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    max_output_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "1200"))
    timeout_seconds = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "5"))

    fail_open_policy = os.getenv("FAIL_OPEN_POLICY", "warn").strip().lower()
    warn_level = int(os.getenv("WARN_RISK_LEVEL_THRESHOLD", "2"))
    block_level = int(os.getenv("BLOCK_RISK_LEVEL_THRESHOLD", "4"))

    prompt_path = Path(os.getenv("PROMPT_FILE_PATH", ".\\prompt_context_detection.md"))
    routing_path = Path(os.getenv("APPROVAL_ROUTING_PATH", ".\\approval_routing.json"))

    prompt_template = load_text(prompt_path)
    approval_routing = load_approval_routing(routing_path)

    cache_enabled = os.getenv("CACHE_ENABLED", "true").strip().lower() in ("1", "true", "yes", "y", "on")
    cache_dir = Path(os.getenv("CACHE_DIR", ".\\cache_internal"))
    cache_key_col = os.getenv("CACHE_KEY_COL", "전송코드").strip()

    if cache_enabled:
        cache_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        timeout_seconds=timeout_seconds,
        fail_open_policy=fail_open_policy,
        warn_level=warn_level,
        block_level=block_level,
        prompt_template=prompt_template,
        approval_routing=approval_routing,
        cache_enabled=cache_enabled,
        cache_dir=cache_dir,
        cache_key_col=cache_key_col,
    )


def render_prompt(template: str, *, meta: Dict[str, str], title: str, body: str, attachments: str) -> str:
    meta_lines = "\n".join([f"- {k}: {v}" for k, v in meta.items() if v])
    return (
        template.replace("{{META}}", meta_lines)
        .replace("{{TITLE}}", title)
        .replace("{{ATTACHMENTS}}", attachments)
        .replace("{{BODY}}", body)
        .strip()
    )


def decide_policy_action(risk_level: int, warn_level: int, block_level: int) -> str:
    if risk_level >= block_level:
        return "block"
    if risk_level >= warn_level:
        return "warn"
    return "allow"


def cache_key(payload: dict, key_col: str) -> str:
    # Prefer stable id from CPCex (e.g., 전송코드)
    k = (payload.get(key_col) or payload.get("mail_id") or "").strip()
    if k:
        return k
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def cache_file(cache_dir: Path, key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", key)
    return cache_dir / f"{safe}.json"


def precheck_mail(payload: dict, settings: Optional[Settings] = None) -> dict:
    """Core function CPCex would call before sending a mail."""
    s = settings or load_settings()

    # Prepare text
    title = str(payload.get("subject") or "")
    body = str(payload.get("body_text") or "")
    if "base64," in body:
        body = BASE64_RE.sub(os.getenv("BASE64_PLACEHOLDER", "<BASE64_IMAGE>"), body)
    body = strip_html(body)

    attachments = payload.get("attachments") or []
    attachments_text = ", ".join([a.get("filename", "") for a in attachments if isinstance(a, dict)])

    sender_dept = str(payload.get("sender_dept") or "")
    is_external = any((r.get("is_external") is True) for r in (payload.get("recipients") or []) if isinstance(r, dict))

    meta = {
        "mail_id": str(payload.get("mail_id") or ""),
        "sender_dept": sender_dept,
        "sender_id": str(payload.get("sender_id") or ""),
        "has_external_recipient": str(is_external),
        "attachment_count": str(len(attachments)),
    }

    # Cache
    ck = cache_key(payload, s.cache_key_col)
    if s.cache_enabled:
        p = cache_file(s.cache_dir, ck)
        if p.exists():
            try:
                cached = json.loads(p.read_text(encoding="utf-8"))
                cached["cached"] = True
                return cached
            except Exception:
                pass

    prompt = render_prompt(s.prompt_template, meta=meta, title=title, body=body, attachments=attachments_text)

    client = OpenAI(api_key=s.api_key, timeout=s.timeout_seconds)

    try:
        resp = client.responses.create(
            model=s.model,
            input=prompt,
            temperature=s.temperature,
            max_output_tokens=s.max_output_tokens,
        )
        data = json.loads(resp.output_text)

        risk_level = int(data.get("risk_level", 0) or 0)
        risk_score = int(data.get("risk_score", 0) or 0)
        policy_action = decide_policy_action(risk_level, s.warn_level, s.block_level)

        result = {
            "ok": True,
            "mail_id": payload.get("mail_id"),
            "policy_action": policy_action,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "intent": data.get("intent"),
            "artifact_type": data.get("artifact_type"),
            "evidence": data.get("evidence", []),
            "reason": data.get("reason"),
            "model": s.model,
            "cached": False,
        }

        if policy_action == "block":
            result["approval_route"] = build_approval_route(sender_dept, s.approval_routing)
        else:
            result["approval_route"] = []

    except Exception as e:
        # Fail-open handling
        result = {
            "ok": False,
            "error": f"LLM failure: {e}",
            "mail_id": payload.get("mail_id"),
            "policy_action": s.fail_open_policy,
            "risk_level": None,
            "risk_score": None,
            "intent": None,
            "artifact_type": None,
            "evidence": [],
            "reason": "LLM 호출 실패로 기본정책 적용",
            "model": s.model,
            "cached": False,
            "approval_route": [],
        }

    if s.cache_enabled:
        try:
            p = cache_file(s.cache_dir, ck)
            p.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    return result
