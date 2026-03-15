"""Context Detection Agent (Webhook) - PoC

목적
- CPCex 훅(또는 시뮬레이터)에서 들어오는 요청을 웹훅으로 수신
- LLM(ChatGPT gpt-5.2)을 호출해 '문맥 기반 탐지'를 수행
- 결과를 policy_action(allow/warn/block) 포함 JSON으로 반환

실행
  1) .env에 OPENAI_API_KEY, OPENAI_MODEL 등 설정
  2) 서버 실행:
     python detection_agent_webhook.py
  3) 테스트(다른 터미널):
     python cpcex_hook_simulator.py sample_data_raw.xlsx http://127.0.0.1:8000/check

의존성
  pip install fastapi uvicorn openai python-dotenv

주의
- PoC 골격 코드입니다. 보안/인증(서명검증), PII 마스킹, 로깅/감사, 레이트리밋은 별도 설계 필요.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from openai import OpenAI


# -----------------------------
# Settings
# -----------------------------

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2").strip()
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
OPENAI_MAX_OUTPUT_TOKENS = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "1200"))

# 정책 임계값(간단 PoC)
HIT_RISK_LEVEL_THRESHOLD = int(os.getenv("HIT_RISK_LEVEL_THRESHOLD", "4"))
WARN_RISK_LEVEL_THRESHOLD = int(os.getenv("WARN_RISK_LEVEL_THRESHOLD", "2"))

PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH", ".\\prompt_context_detection.md")
BASE64_PLACEHOLDER = os.getenv("BASE64_PLACEHOLDER", "<BASE64_IMAGE>")

UI_HTML_PATH = os.getenv("UI_HTML_PATH", ".\\ui_mail_demo.html")
APPROVAL_ROUTING_PATH = os.getenv("APPROVAL_ROUTING_PATH", ".\\approval_routing.json")
SAMPLE_XLSX_PATH = os.getenv("SAMPLE_XLSX_PATH", ".\\sample_data_raw.xlsx")

BASE64_RE = re.compile(
    r"data:image/[^;]+;base64,[A-Za-z0-9+/=\n\r]+",
    re.IGNORECASE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    return HTML_TAG_RE.sub(" ", text)


def load_prompt_template() -> str:
    p = Path(PROMPT_FILE_PATH)
    if not p.exists():
        raise FileNotFoundError(f"Prompt file not found: {p.resolve()}")
    return p.read_text(encoding="utf-8")


PROMPT_TEMPLATE = load_prompt_template()


def load_approval_routing() -> dict:
    p = Path(APPROVAL_ROUTING_PATH)
    if not p.exists():
        return {
            "default": {
                "stage1_team_compliance": "(팀별 준법담당) TBD",
                "stage2_biz_compliance": "(사업부 준법담당) TBD",
                "stage3_dept_head": "(부서장) TBD",
            },
            "by_sender_dept": {},
        }
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {
            "default": {
                "stage1_team_compliance": "(팀별 준법담당) TBD",
                "stage2_biz_compliance": "(사업부 준법담당) TBD",
                "stage3_dept_head": "(부서장) TBD",
            },
            "by_sender_dept": {},
        }


APPROVAL_ROUTING = load_approval_routing()


def load_sample_df() -> "pd.DataFrame":
    # Lazy import to avoid hard dependency when not used
    import pandas as pd

    p = Path(SAMPLE_XLSX_PATH)
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(p, sheet_name=0)
    except Exception:
        return pd.DataFrame()


_SAMPLE_DF = None


def get_sample_df():
    global _SAMPLE_DF
    if _SAMPLE_DF is None:
        _SAMPLE_DF = load_sample_df()
    return _SAMPLE_DF


def build_approval_route(sender_dept: str) -> list[str]:
    sender_dept = (sender_dept or "").strip()
    default = APPROVAL_ROUTING.get("default", {})
    by_dept = APPROVAL_ROUTING.get("by_sender_dept", {})
    rule = by_dept.get(sender_dept, {}) if isinstance(by_dept, dict) else {}

    s1 = rule.get("stage1_team_compliance") or default.get("stage1_team_compliance") or "(팀별 준법담당) TBD"
    s2 = rule.get("stage2_biz_compliance") or default.get("stage2_biz_compliance") or "(사업부 준법담당) TBD"
    s3 = rule.get("stage3_dept_head") or default.get("stage3_dept_head") or "(부서장) TBD"

    return [f"1) 합의 - 팀별 준법담당: {s1}", f"2) 합의 - 사업부 준법담당: {s2}", f"3) 결재 - 부서장: {s3}"]


def build_prompt(meta: Dict[str, str], title: str, body: str, attachments: str) -> str:
    meta_lines = "\n".join([f"- {k}: {v}" for k, v in meta.items() if v])
    prompt = PROMPT_TEMPLATE
    prompt = prompt.replace("{{META}}", meta_lines)
    prompt = prompt.replace("{{TITLE}}", title)
    prompt = prompt.replace("{{ATTACHMENTS}}", attachments)
    prompt = prompt.replace("{{BODY}}", body)
    return prompt.strip()


def decide_policy_action(risk_level: int) -> str:
    # allow / warn / block
    if risk_level >= HIT_RISK_LEVEL_THRESHOLD:
        return "block"
    if risk_level >= WARN_RISK_LEVEL_THRESHOLD:
        return "warn"
    return "allow"


# -----------------------------
# API Models
# -----------------------------


class Recipient(BaseModel):
    recipient_id: Optional[str] = None
    recipient_company: Optional[str] = None
    is_external: Optional[bool] = None


class Attachment(BaseModel):
    filename: str
    extension: Optional[str] = ""


class CheckRequest(BaseModel):
    mail_id: str
    sender_dept: Optional[str] = None
    sender_id: Optional[str] = None
    subject: str
    body_text: str
    recipients: List[Recipient] = Field(default_factory=list)
    attachments: List[Attachment] = Field(default_factory=list)
    timestamp: Optional[str] = None


class SendRequest(BaseModel):
    payload: Dict[str, Any]
    mode: str = "allow"  # allow | warn_override


class ApproveRequest(BaseModel):
    payload: Dict[str, Any]
    lastCheck: Optional[Dict[str, Any]] = None


# -----------------------------
# FastAPI app
# -----------------------------

app = FastAPI(title="Context Detection Agent (PoC)")


@app.get("/health")
def health():
    return {
        "ok": True,
        "time": datetime.now().isoformat(),
        "model": OPENAI_MODEL,
    }


@app.get("/ui", response_class=HTMLResponse)
def ui():
    # serve demo UI page
    p = Path(UI_HTML_PATH)
    if not p.exists():
        return HTMLResponse(f"<h3>UI file not found</h3><pre>{p.resolve()}</pre>", status_code=404)
    return HTMLResponse(p.read_text(encoding="utf-8"))


@app.get("/sample/random")
def sample_random():
    """Return a random sample row mapped to UI fields."""
    df = get_sample_df()
    if df is None or df.empty:
        return {
            "ok": False,
            "error": f"Sample xlsx not found or empty: {Path(SAMPLE_XLSX_PATH).resolve()}",
        }

    row = df.sample(1).iloc[0]

    def s(col: str) -> str:
        v = row.get(col, "")
        return "" if v is None else str(v)

    attachments_raw = ", ".join([x for x in [s("일반자료명: 삼성등록"), s("일반자료명: 협력사등록")] if x and x != 'nan'])

    payload = {
        "sender_dept": s("발신자부서명"),
        "sender_id": s("발신자_ID"),
        "recipient_company": s("수신자_회사명"),
        "is_external": True,
        "subject": s("제목"),
        "body": s("본문내용"),
        "attachments": attachments_raw,
        "mail_id": s("전송코드"),
    }

    return {"ok": True, "sample": payload}


@app.post("/check")
def check(req: CheckRequest):
    if not OPENAI_API_KEY:
        return {
            "ok": False,
            "error": "OPENAI_API_KEY is empty",
        }

    client = OpenAI(api_key=OPENAI_API_KEY)

    title = req.subject or ""
    body = req.body_text or ""

    # Normalize: strip base64 blobs + html tags
    if "base64," in body:
        body = BASE64_RE.sub(BASE64_PLACEHOLDER, body)
    body = strip_html(body)

    attachments_text = ", ".join([a.filename for a in req.attachments])

    is_external = any((r.is_external is True) for r in req.recipients)

    meta = {
        "mail_id": req.mail_id,
        "sender_dept": req.sender_dept or "",
        "sender_id": req.sender_id or "",
        "has_external_recipient": str(is_external),
        "attachment_count": str(len(req.attachments)),
    }

    prompt = build_prompt(meta=meta, title=title, body=body, attachments=attachments_text)

    # LLM call (sync)
    try:
        resp = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=OPENAI_TEMPERATURE,
            max_output_tokens=OPENAI_MAX_OUTPUT_TOKENS,
        )
        text = resp.output_text
        data = json.loads(text)
    except Exception as e:
        return {
            "ok": False,
            "error": f"LLM failure: {e}",
            "mail_id": req.mail_id,
        }

    risk_level = int(data.get("risk_level", 0) or 0)
    risk_score = int(data.get("risk_score", 0) or 0)

    policy_action = decide_policy_action(risk_level)

    approval_route = []
    if policy_action == "block":
        approval_route = build_approval_route(req.sender_dept or "")

    # Return enriched result
    return {
        "ok": True,
        "mail_id": req.mail_id,
        "policy_action": policy_action,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "intent": data.get("intent"),
        "artifact_type": data.get("artifact_type"),
        "evidence": data.get("evidence", []),
        "reason": data.get("reason"),
        "approval_route": approval_route,
        "model": OPENAI_MODEL,
    }


@app.post("/send")
def send(req: SendRequest):
    # PoC: 실제 전송 대신 로그/응답만 반환
    # mode=warn_override이면 "경고 무시하고 전송" 케이스로 기록한다고 가정
    return {
        "ok": True,
        "action": "sent",
        "mode": req.mode,
        "mail_id": (req.payload or {}).get("mail_id"),
        "timestamp": datetime.now().isoformat(),
        "note": "PoC 데모: 실제 전송은 수행하지 않았습니다(로그만 남기는 것으로 가정).",
    }


@app.post("/approve")
def approve(req: ApproveRequest):
    sender_dept = (req.payload or {}).get("sender_dept") or ""
    route = build_approval_route(sender_dept)
    return {
        "ok": True,
        "action": "approval_requested",
        "mail_id": (req.payload or {}).get("mail_id"),
        "approval_route": route,
        "timestamp": datetime.now().isoformat(),
        "note": "PoC 데모: 승인 요청만 생성(실제 티켓/결재 시스템 연동은 미구현).",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
