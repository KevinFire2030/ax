from .dlp import detect


def check_output(text: str):
    findings = detect(text)
    violations = [f for f in findings if f.startswith("kw:") or f in {"rrn_like"}]
    blocked = len(violations) > 0
    return {
        "violations": violations,
        "blocked": blocked,
    }
