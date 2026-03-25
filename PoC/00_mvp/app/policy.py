import os

POLICY_VERSION = os.getenv("POLICY_VERSION", "v0.1")
RISK_LOW = int(os.getenv("RISK_LOW", "30"))
RISK_HIGH = int(os.getenv("RISK_HIGH", "70"))


def decide_route(score: int, force_mode: str = "auto") -> str:
    if force_mode in {"internal", "external", "hybrid"}:
        return force_mode
    if score < RISK_LOW:
        return "external"
    if score >= RISK_HIGH:
        return "internal"
    return "hybrid"
