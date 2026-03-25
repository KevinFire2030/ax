import re
from typing import List, Tuple

SENSITIVE_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b01[0-9]-?\d{3,4}-?\d{4}\b",
    "rrn_like": r"\b\d{6}-?[1-4]\d{6}\b",
}

SENSITIVE_KEYWORDS = [
    "프로젝트코드", "원가", "수율", "고객사", "기밀", "내부전용", "미공개", "사번"
]


def detect(text: str) -> List[str]:
    findings: List[str] = []
    for k, p in SENSITIVE_PATTERNS.items():
        if re.search(p, text):
            findings.append(k)
    for kw in SENSITIVE_KEYWORDS:
        if kw in text:
            findings.append(f"kw:{kw}")
    return findings


def risk_score(text: str, findings: List[str]) -> int:
    score = min(100, len(findings) * 15)
    # simple contextual risk heuristic
    if "전송" in text and "외부" in text:
        score += 20
    if "첨부" in text and "보고서" in text:
        score += 10
    return min(100, score)


def split_sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?]|[。！？])\s+|\n+", text.strip())
    return [c for c in chunks if c]


def mask_sensitive(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    mapping = []
    masked = text
    idx = 1
    for k, p in SENSITIVE_PATTERNS.items():
        for m in re.findall(p, masked):
            token = f"{k.upper()}_{idx}"
            masked = masked.replace(m, token)
            mapping.append((token, m))
            idx += 1
    return masked, mapping


def unmask(text: str, mapping: List[Tuple[str, str]]) -> str:
    out = text
    for token, raw in mapping:
        out = out.replace(token, raw)
    return out
