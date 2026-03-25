import os
import json
import uuid
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .models import AnalyzeRequest, AnalyzeResponse
from .dlp import detect, risk_score, split_sentences, mask_sensitive, unmask
from .policy import decide_route, POLICY_VERSION
from .router import route_call
from .postcheck import check_output
from .logger import write_audit, tail_logs

load_dotenv()

app = FastAPI(title="Security LLM Gateway MVP")

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
WEB_DIR = os.path.join(BASE_DIR, "web")
SAMPLES_PATH = os.path.join(BASE_DIR, "samples", "input_examples.json")
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


@app.get("/")
def index():
    with open(os.path.join(WEB_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    rid = str(uuid.uuid4())[:8]
    findings = detect(req.text)
    score = risk_score(req.text, findings)
    route = decide_route(score, req.force_mode)

    sentence_scores = [risk_score(s, detect(s)) for s in split_sentences(req.text)]

    masked, mapping = mask_sensitive(req.text)
    routed_input = masked if route in {"external", "hybrid"} else req.text

    output_raw, fallback_used, model_ids = route_call(route, routed_input, sentence_scores)
    output = unmask(output_raw, mapping)

    post = check_output(output)
    blocked = post["blocked"]
    if blocked:
        output = "[BLOCKED] 민감정보 또는 정책 위반 가능성이 탐지되었습니다."

    audit = {
        "request_id": rid,
        "timestamp": datetime.now().isoformat(),
        "risk_score": score,
        "route": route,
        "fallback_used": fallback_used,
        "blocked": blocked,
        "reasons": findings,
        "policy_version": POLICY_VERSION,
        "input_preview": req.text[:180],
        "output_preview": output[:180],
        "model_ids": model_ids,
    }
    write_audit(audit)

    return AnalyzeResponse(
        request_id=rid,
        risk_score=score,
        findings=findings,
        route=route,
        fallback_used=fallback_used,
        blocked=blocked,
        output=output,
        postcheck=post,
        policy_version=POLICY_VERSION,
    )


@app.get("/api/logs")
def logs(limit: int = 20):
    return {"items": tail_logs(limit)}


@app.get("/api/examples")
def examples():
    if not os.path.exists(SAMPLES_PATH):
        return {"items": []}
    with open(SAMPLES_PATH, "r", encoding="utf-8") as f:
        return {"items": json.load(f)}
