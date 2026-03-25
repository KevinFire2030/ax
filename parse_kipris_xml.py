import argparse
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET

FIELDS = [
    "indexNo",
    "registerStatus",
    "inventionTitle",
    "ipcNumber",
    "registerNumber",
    "registerDate",
    "applicationNumber",
    "applicationDate",
    "openNumber",
    "openDate",
    "publicationNumber",
    "publicationDate",
    "astrtCont",
    "drawing",
    "bigDrawing",
    "applicantName",
]


def parse_items(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    items = []

    for item in root.findall(".//body/items/item"):
        row = {}
        for f in FIELDS:
            el = item.find(f)
            row[f] = (el.text or "").strip() if el is not None and el.text else ""
        items.append(row)

    count = {
        "numOfRows": (root.findtext(".//count/numOfRows") or "").strip(),
        "pageNo": (root.findtext(".//count/pageNo") or "").strip(),
        "totalCount": (root.findtext(".//count/totalCount") or "").strip(),
    }
    return items, count


def main():
    parser = argparse.ArgumentParser(description="KIPRIS XML -> CSV/JSON 변환")
    parser.add_argument("--input", required=True, help="입력 XML 파일 경로")
    parser.add_argument("--csv", default="", help="출력 CSV 파일 경로")
    parser.add_argument("--json", default="", help="출력 JSON 파일 경로")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"[오류] 입력 파일이 없습니다: {in_path}")

    items, count = parse_items(in_path)

    out_csv = Path(args.csv) if args.csv else in_path.with_suffix(".csv")
    out_json = Path(args.json) if args.json else in_path.with_suffix(".json")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(items)

    payload = {
        "count": count,
        "items": items,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[완료] XML:  {in_path}")
    print(f"[완료] CSV:  {out_csv}")
    print(f"[완료] JSON: {out_json}")
    print(f"[건수] items={len(items)}, totalCount={count.get('totalCount','')}")


if __name__ == "__main__":
    main()
