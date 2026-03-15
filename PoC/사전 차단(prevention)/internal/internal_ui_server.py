"""Internal UI Server (PoC)

목적
- external(훅 호출 방식)처럼 실감나는 웹 UI를 제공하되,
- 검사 로직은 webhook 호출이 아니라 "CPCex 내부에서 LLM 직접 호출" 방식으로 수행

구성
- GET  /ui      : 메일 작성/전송 데모 페이지(한 페이지)
- POST /check   : cpcex_internal_precheck.precheck_mail(payload) 호출
- POST /send    : allow 또는 warn_override 전송 데모(로그만)
- POST /approve : block 케이스 승인 요청 생성 데모(3단계 라우팅 반환)

실행
  cd /d E:\ax\상생\사전 차단\internal
  pip install fastapi uvicorn python-dotenv
  python internal_ui_server.py

접속
  http://127.0.0.1:8001/ui
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cpcex_internal_precheck import precheck_mail, load_settings


load_dotenv()

UI_HTML_PATH = os.getenv("UI_HTML_PATH", ".\\ui_mail_demo.html")

app = FastAPI(title="CPCex Internal Precheck UI (PoC)")


class CheckRequest(BaseModel):
    mail_id: str
    sender_dept: Optional[str] = None
    sender_id: Optional[str] = None
    subject: str
    body_text: str
    recipients: list = []
    attachments: list = []
    timestamp: Optional[str] = None


class SendRequest(BaseModel):
    payload: Dict[str, Any]
    mode: str = "allow"  # allow | warn_override


class ApproveRequest(BaseModel):
    payload: Dict[str, Any]
    lastCheck: Optional[Dict[str, Any]] = None


SETTINGS = None


def get_settings():
    global SETTINGS
    if SETTINGS is None:
        SETTINGS = load_settings()
    return SETTINGS


@app.get("/health")
def health():
    s = get_settings()
    return {
        "ok": True,
        "time": datetime.now().isoformat(),
        "model": s.model,
        "mode": "internal_precheck",
    }


@app.get("/ui", response_class=HTMLResponse)
def ui():
    p = Path(UI_HTML_PATH)
    if not p.exists():
        return HTMLResponse(f"<h3>UI file not found</h3><pre>{p.resolve()}</pre>", status_code=404)
    return HTMLResponse(p.read_text(encoding="utf-8"))


@app.post("/check")
def check(req: CheckRequest):
    payload = req.model_dump()
    # ensure internal precheck sees expected keys
    payload.setdefault("mail_id", payload.get("mail_id"))

    result = precheck_mail(payload, settings=get_settings())
    return result


@app.post("/send")
def send(req: SendRequest):
    return {
        "ok": True,
        "action": "sent",
        "mode": req.mode,
        "mail_id": (req.payload or {}).get("mail_id"),
        "timestamp": datetime.now().isoformat(),
        "note": "PoC 데모: 내부 방식. 실제 전송은 수행하지 않았습니다(로그만 가정).",
    }


@app.post("/approve")
def approve(req: ApproveRequest):
    # PoC: 승인 요청 생성만 흉내내고 라우팅 반환
    sender_dept = (req.payload or {}).get("sender_dept") or ""
    # precheck_mail이 쓰는 라우팅 함수를 재사용하려면 lastCheck에 approval_route가 포함되어 있음
    route = []
    if req.lastCheck and isinstance(req.lastCheck, dict):
        route = req.lastCheck.get("approval_route") or []

    return {
        "ok": True,
        "action": "approval_requested",
        "mail_id": (req.payload or {}).get("mail_id"),
        "approval_route": route,
        "timestamp": datetime.now().isoformat(),
        "note": "PoC 데모: 승인 요청만 생성(실제 결재 시스템/조직도 연동은 미구현).",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
