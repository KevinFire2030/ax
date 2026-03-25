import os
import json
import argparse
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

DEFAULT_URL = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"


def build_params(api_key: str, args):
    # KIPRIS 문서 기준 파라미터 (필요한 것만 먼저 사용)
    params = {
        "ServiceKey": api_key,  # 문서 샘플 표기 우선
        "word": args.word,
        "inventionTitle": args.invention_title,
        "astrtCont": args.astrt_cont,
        "applicationNumber": args.application_number,
        "openNumber": args.open_number,
        "publicationNumber": args.publication_number,
        "registerNumber": args.register_number,
        "applicant": args.applicant,
        "inventors": args.inventors,
        "agent": args.agent,
        "rightHoler": args.right_holer,
        "patent": str(args.patent).lower(),
        "utility": str(args.utility).lower(),
        "lastvalue": args.lastvalue,
        "pageNo": args.page,
        "numOfRows": args.rows,
        "sortSpec": args.sort_spec,
        "descSort": str(args.desc_sort).lower(),
    }

    # 빈 값 제거
    return {k: v for k, v in params.items() if v not in (None, "")}


def main():
    load_dotenv()

    api_key = os.getenv("KIPRIS_API_KEY", "").strip()
    default_url = os.getenv("KIPRIS_TEST_URL", DEFAULT_URL).strip() or DEFAULT_URL

    parser = argparse.ArgumentParser(description="KIPRIS getAdvancedSearch 테스트")
    parser.add_argument("--url", default=default_url, help="API URL")

    # 주요 검색 파라미터
    parser.add_argument("--word", default="", help="자유검색")
    parser.add_argument("--invention-title", default="", help="발명의명칭")
    parser.add_argument("--astrt-cont", default="", help="초록")

    # 선택 파라미터
    parser.add_argument("--application-number", default="")
    parser.add_argument("--open-number", default="")
    parser.add_argument("--publication-number", default="")
    parser.add_argument("--register-number", default="")
    parser.add_argument("--applicant", default="")
    parser.add_argument("--inventors", default="")
    parser.add_argument("--agent", default="")
    parser.add_argument("--right-holer", default="")

    parser.add_argument("--patent", default=True, type=lambda x: str(x).lower() == "true")
    parser.add_argument("--utility", default=True, type=lambda x: str(x).lower() == "true")
    parser.add_argument("--lastvalue", default="", help="행정처분 코드")

    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--rows", type=int, default=20)
    parser.add_argument("--sort-spec", default="PD", help="PD/AD/GD/OPD/FD/FOD/RD")
    parser.add_argument("--desc-sort", default=True, type=lambda x: str(x).lower() == "true")

    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--save", action="store_true", help="응답 파일 저장")
    args = parser.parse_args()

    if not api_key:
        raise SystemExit("[오류] KIPRIS_API_KEY가 비어 있습니다. E:/ax/kipris/.env에 입력하세요.")

    params = build_params(api_key, args)

    print("[요청 URL]", args.url)
    print("[요청 파라미터]")
    print(json.dumps(params, ensure_ascii=False, indent=2))

    resp = requests.get(args.url, params=params, timeout=args.timeout)
    print("[HTTP 상태]", resp.status_code)
    print("[Content-Type]", resp.headers.get("content-type", ""))

    body = resp.text
    print("\n[응답 미리보기]\n")
    print(body[:2000])

    if args.save:
        out_dir = Path(__file__).resolve().parent / "samples"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"advanced_search_{ts}.xml"
        out_path.write_text(body, encoding="utf-8")
        print(f"\n[저장 완료] {out_path}")


if __name__ == "__main__":
    main()
