"""CPCex Internal Pre-check Simulator (PoC)

- 훅 서버 없이(CPCex 내부에서) 전송 직전 LLM 호출하는 흐름을 샘플 엑셀로 시뮬레이션

사용법
  python cpcex_internal_simulator.py sample_data_raw.xlsx

출력
- 콘솔 요약
- jsonl 로그: internal_precheck_result_YYYYMMDD_HHMMSS.jsonl

의존성
  pip install pandas openpyxl openai python-dotenv
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from cpcex_internal_precheck import precheck_mail, load_settings


def build_payload_from_row(row: pd.Series) -> dict:
    def s(col: str) -> str:
        v = row.get(col, "")
        return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)

    attach_s = s("일반자료명: 삼성등록")
    attach_v = s("일반자료명: 협력사등록")

    attachments = []
    for raw in [attach_s, attach_v]:
        if not raw or raw == 'nan':
            continue
        for name in [x.strip() for x in raw.split(",") if x.strip()]:
            ext = name.split(".")[-1].lower() if "." in name else ""
            attachments.append({"filename": name, "extension": ext})

    return {
        "mail_id": s("전송코드") or f"poc-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "전송코드": s("전송코드"),
        "sender_dept": s("발신자부서명"),
        "sender_id": s("발신자_ID"),
        "subject": s("제목"),
        "body_text": s("본문내용"),
        "recipients": [
            {
                "recipient_company": s("수신자_회사명"),
                "is_external": True,
            }
        ],
        "attachments": attachments,
        "timestamp": datetime.now().isoformat(),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python cpcex_internal_simulator.py <input.xlsx>")
        raise SystemExit(1)

    input_path = Path(sys.argv[1])
    df = pd.read_excel(input_path, sheet_name=0)

    settings = load_settings()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).resolve().parent / f"internal_precheck_result_{ts}.jsonl"

    print(f"rows: {len(df)}")
    print(f"log_file: {out_path}")

    with out_path.open("w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            payload = build_payload_from_row(row)
            result = precheck_mail(payload, settings=settings)

            record = {
                "row_index": int(i),
                "payload": payload,
                "result": result,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

            # console summary
            print(f"[{i}] {result.get('policy_action')} level={result.get('risk_level')} score={result.get('risk_score')} mail_id={payload.get('mail_id')}")


if __name__ == "__main__":
    main()
