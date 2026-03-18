from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


def _env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return default if v is None else str(v)


def _headers() -> Dict[str, str]:
    # NOTE: .env keys are literally header names to keep it simple.
    h: Dict[str, str] = {
        "x-generative-ai-client": _env("x-generative-ai-client").strip(),
        "x-openapi-token": _env("x-openapi-token").strip(),
    }
    email = _env("x-generative-ai-user-email").strip()
    if email:
        h["x-generative-ai-user-email"] = email

    missing = [k for k, v in h.items() if not v]
    if missing:
        raise SystemExit(f"Missing required env(s): {', '.join(missing)} (check .env)")

    return h


def _endpoint(path: str) -> str:
    base = _env("ENDPOINT_URL").strip().rstrip("/")
    if not base:
        raise SystemExit("Missing ENDPOINT_URL in .env")
    return f"{base}{path}"


def get_models() -> Any:
    url = _endpoint("/openapi/chat/v1/models")
    r = requests.get(url, headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def get_all_models() -> Any:
    url = _endpoint("/openapi/chat/v1/all-models")
    r = requests.get(url, headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def post_messages(model_id: str, contents: List[str], is_stream: bool = False) -> Any:
    url = _endpoint("/openapi/chat/v1/messages")

    payload: Dict[str, Any] = {
        "modelIds": [model_id],
        "contents": contents,
        "isStream": bool(is_stream),
    }

    r = requests.post(url, headers={**_headers(), "Content-Type": "application/json"}, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


def _pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def main() -> None:
    load_dotenv()

    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  python gauss_quickcheck.py models\n"
            "  python gauss_quickcheck.py all-models\n"
            "  python gauss_quickcheck.py chat [MODEL_ID] [MESSAGE]\n"
        )
        raise SystemExit(1)

    cmd = sys.argv[1].strip().lower()

    if cmd == "models":
        data = get_models()
        print(_pretty(data))
        # best-effort show first modelId
        try:
            first = data[0]["modelId"] if isinstance(data, list) and data else None
        except Exception:
            first = None
        if first:
            print("\nTIP: set GAUSS_TEXT_MODEL_ID in .env for quick chat")
            print(f"     GAUSS_TEXT_MODEL_ID={first}")
        return

    if cmd == "all-models":
        data = get_all_models()
        print(_pretty(data))
        return

    if cmd == "chat":
        model_id = sys.argv[2].strip() if len(sys.argv) >= 3 and sys.argv[2].strip() else _env("GAUSS_TEXT_MODEL_ID").strip()
        if not model_id:
            raise SystemExit("MODEL_ID missing. Provide arg or set GAUSS_TEXT_MODEL_ID in .env")

        msg = " ".join(sys.argv[3:]).strip() if len(sys.argv) >= 4 else _env("DEFAULT_PROMPT").strip() or "안녕하세요"
        data = post_messages(model_id=model_id, contents=[msg], is_stream=False)
        print(_pretty(data))
        return

    raise SystemExit(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
