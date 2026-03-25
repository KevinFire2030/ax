import json
from datetime import datetime
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def write_audit(item: dict):
    p = LOG_DIR / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def tail_logs(limit: int = 20):
    files = sorted(LOG_DIR.glob("audit_*.jsonl"), reverse=True)
    out = []
    for fp in files:
        for line in reversed(fp.read_text(encoding="utf-8").splitlines()):
            if line.strip():
                out.append(json.loads(line))
            if len(out) >= limit:
                return out
    return out
