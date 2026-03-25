import os
from typing import List


def _internal_call(text: str) -> str:
    return f"[INTERNAL] {text[:600]}"


def _external_call(text: str) -> str:
    if os.getenv("EXTERNAL_FAIL_SIMULATE", "false").lower() == "true" or "FORCE_FALLBACK" in text:
        raise RuntimeError("Simulated external failure")
    return f"[EXTERNAL] {text[:600]}"


def route_call(route: str, text: str, sentence_scores: List[int] | None = None):
    fallback_used = False
    model_ids = []

    if route == "internal":
        model_ids.append("internal-mock-v1")
        return _internal_call(text), fallback_used, model_ids

    if route == "external":
        try:
            model_ids.append("external-mock-v1")
            return _external_call(text), fallback_used, model_ids
        except Exception:
            fallback_used = True
            model_ids.append("internal-mock-v1")
            return _internal_call(text), fallback_used, model_ids

    # hybrid
    parts = [p for p in text.split("\n") if p.strip()]
    if not parts:
        parts = [text]
    out_parts = []
    for i, p in enumerate(parts):
        s = sentence_scores[i] if sentence_scores and i < len(sentence_scores) else 50
        if s >= 70:
            out_parts.append(_internal_call(p))
            model_ids.append("internal-mock-v1")
        else:
            try:
                out_parts.append(_external_call(p))
                model_ids.append("external-mock-v1")
            except Exception:
                fallback_used = True
                out_parts.append(_internal_call(p))
                model_ids.append("internal-mock-v1")
    return "\n".join(out_parts), fallback_used, model_ids
