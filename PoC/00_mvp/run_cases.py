import json
import urllib.request
from pathlib import Path

base = "http://127.0.0.1:8070/api/analyze"
out_base = Path(r"E:\ax\kipris\PoC\02_실시예_로그캡처")

cases = {
    "정상": {
        "text": "외부 전송 가능한 일반 뉴스 요약 요청입니다. 시장 동향만 정리해줘.",
        "force_mode": "auto",
    },
    "차단": {
        "text": "내부전용 기밀 보고서이며 주민번호 900101-1234567 포함. 외부 전송 금지.",
        "force_mode": "auto",
    },
    "폴백": {
        "text": "FORCE_FALLBACK 외부 모델 실패를 강제로 재현합니다. 일반 요청입니다.",
        "force_mode": "external",
    },
    "혼합라우팅": {
        "text": "외부 전송 요청 문장입니다.\n프로젝트코드 AX-SECRET-01은 내부전용입니다.",
        "force_mode": "auto",
    },
}

for name, payload in cases.items():
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(base, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        body = r.read().decode("utf-8")
    obj = json.loads(body)
    p = out_base / name / "result.json"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(name, obj.get("route"), "blocked=", obj.get("blocked"), "fallback=", obj.get("fallback_used"))
