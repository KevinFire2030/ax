"""CPCex Hook Call Simulator (PoC)

목적
- CPCex 내 '전송 직전 훅'을 흉내내는 스크립트
- 샘플 엑셀을 한 행씩 읽어서 입력값(payload) 추출
- 탐지 에이전트(Webhook)로 API 호출
- 리턴(policy_action)에 따라 Allow/Warn/Block 분기 결정을 콘솔에 출력

사용법
  python cpcex_hook_simulator.py sample_data_raw.xlsx http://127.0.0.1:8000/check

의존성
  pip install pandas openpyxl requests python-dotenv

주의
- 실제 CPCex 연동은 아님(훅 호출 흐름/입출력 포맷만 PoC로 확인용)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv


def safe_str(x) -> str:
    return "" if pd.isna(x) else str(x)


def build_payload(row: pd.Series) -> dict:
    # CPCex 전송 직전 훅에서 보낼 법한 최소 payload
    subject = safe_str(row.get("제목"))
    body = safe_str(row.get("본문내용"))

    # 첨부파일명은 현재 데이터에 '일반자료명: 삼성등록/협력사등록'에 들어있음
    attach_s = safe_str(row.get("일반자료명: 삼성등록"))
    attach_v = safe_str(row.get("일반자료명: 협력사등록"))

    # 단순히 콤마 분리 (데이터 형태에 따라 개발팀이 강화)
    attachments = []
    for raw in [attach_s, attach_v]:
        if not raw:
            continue
        for name in [x.strip() for x in raw.split(",") if x.strip()]:
            ext = name.split(".")[-1].lower() if "." in name else ""
            attachments.append({"filename": name, "extension": ext})

    payload = {
        "mail_id": safe_str(row.get("전송코드")) or f"poc-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "sender_dept": safe_str(row.get("발신자부서명")),
        "sender_id": safe_str(row.get("발신자_ID")),
        "subject": subject,
        "body_text": body,
        "recipients": [
            {
                "recipient_id": safe_str(row.get("수신자ID")),
                "recipient_company": safe_str(row.get("수신자_회사명")),
                # PoC: 외부여부는 시스템에서 판단 가능하다고 했으니 boolean을 넣는 자리만 마련
                "is_external": True,
            }
        ],
        "attachments": attachments,
        "timestamp": datetime.now().isoformat(),
    }
    return payload


def decide_branch(result: dict) -> str:
    # 에이전트가 리턴한 policy_action 기준 분기
    action = (result.get("policy_action") or "").lower()

    if action == "allow":
        return "ALLOW: 즉시 전송"
    if action == "warn":
        return "WARN: 팝업 표시 후 전송은 허용(override 로그 남김)"
    if action == "block":
        return "BLOCK: 전송 중지 + 승인 프로세스(3단계)로 이동"

    return f"UNKNOWN_ACTION('{action}'): 기본정책(Warn 등) 적용 필요"


def main():
    load_dotenv()

    if len(sys.argv) < 3:
        print("Usage: python cpcex_hook_simulator.py <input.xlsx> <agent_url>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    agent_url = sys.argv[2]

    # Output jsonl file in the same folder as this script
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).resolve().parent / f"cpcex_sim_result_{ts}.jsonl"

    df = pd.read_excel(input_path, sheet_name=0)
    print(f"rows: {len(df)}")
    print(f"log_file: {out_path}")

    with out_path.open("w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            payload = build_payload(row)

            try:
                r = requests.post(agent_url, json=payload, timeout=60)
                r.raise_for_status()
                result = r.json()
            except Exception as e:
                record = {
                    "row_index": int(i),
                    "payload": payload,
                    "ok": False,
                    "error": str(e),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"[{i}] ERROR calling agent: {e}")
                continue

            branch = decide_branch(result)

            # write jsonl record
            record = {
                "row_index": int(i),
                "payload": payload,
                "ok": True,
                "result": result,
                "branch": branch,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

            # console output
            print("=" * 80)
            print(f"[{i}] mail_id={payload['mail_id']}")
            print(f"subject: {payload['subject']}")
            print(f"attachments: {[a['filename'] for a in payload['attachments']]}")
            print("agent_result:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("branch:", branch)


if __name__ == "__main__":
    main()
