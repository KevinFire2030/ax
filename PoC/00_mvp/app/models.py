from pydantic import BaseModel
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    text: str
    force_mode: str = "auto"  # auto|internal|external|hybrid


class AnalyzeResponse(BaseModel):
    request_id: str
    risk_score: int
    findings: List[str]
    route: str
    fallback_used: bool
    blocked: bool
    output: str
    postcheck: dict
    policy_version: str


class LogItem(BaseModel):
    request_id: str
    timestamp: str
    risk_score: int
    route: str
    fallback_used: bool
    blocked: bool
    reasons: List[str]
    policy_version: str
    input_preview: str
    output_preview: str
    model_ids: List[str]
