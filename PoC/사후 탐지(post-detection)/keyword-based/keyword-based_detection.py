# filename: keyword-based detection.py
# usage: python "keyword-based detection.py" sample.xlsx
# (optional) python "keyword-based detection.py" sample.xlsx detection_keywords.md

import sys
import re
import time
from pathlib import Path
import pandas as pd


BASE64_RE = re.compile(
    r"data:image/[^;]+;base64,[A-Za-z0-9+/=\n\r]+",
    re.IGNORECASE,
)

DEFAULT_KEYWORD_FILE = Path("detection_keywords.md")

COL_TITLE = "제목"
COL_BODY = "본문내용"
COL_SAMSUNG = "일반자료명: 삼성등록"
COL_VENDOR = "일반자료명: 협력사등록"
COL_OUT = "detected-keyword"
COL_OUT_TITLE = "detected-title"
COL_OUT_ATTACH = "detected-attachment"
COL_OUT_BODY = "detected-body"

COL_DEPT = "발신자부서명"


def read_keywords(md_path: Path) -> list[str]:
    if not md_path.exists():
        raise FileNotFoundError(f"Keyword file not found: {md_path.resolve()}")

    keywords: list[str] = []
    with md_path.open("r", encoding="utf-8") as f:
        for line in f:
            kw = line.strip()
            if kw:
                keywords.append(kw)

    if not keywords:
        raise ValueError(f"No keywords found in: {md_path.resolve()}")

    return keywords


def safe_str(x) -> str:
    return "" if pd.isna(x) else str(x)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python "keyword-based detection.py" <input.xlsx> [keywords.md]')
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path.resolve()}")

    keyword_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_KEYWORD_FILE
    keywords = read_keywords(keyword_path)

    start = time.perf_counter()

    df = pd.read_excel(input_path, sheet_name=0)

    # If any required column missing, add as empty to avoid crashing
    for c in [COL_TITLE, COL_SAMSUNG, COL_VENDOR, COL_BODY]:
        if c not in df.columns:
            df[c] = ""

    def find_keywords_in_text(text: str) -> str:
        found = [kw for kw in keywords if kw in text]
        return ",".join(found)

    def find_keywords_in_row(row):
        title = safe_str(row.get(COL_TITLE))
        samsung = safe_str(row.get(COL_SAMSUNG))
        vendor = safe_str(row.get(COL_VENDOR))
        body = safe_str(row.get(COL_BODY))

        # strip base64 image blobs (body only)
        if "base64," in body:
            body = BASE64_RE.sub("<BASE64_IMAGE>", body)

        attachment_text = f"{samsung} {vendor}".strip()

        hit_title = find_keywords_in_text(title)
        hit_attach = find_keywords_in_text(attachment_text)
        hit_body = find_keywords_in_text(body)

        # union (preserve keyword order in KEYWORDS)
        combined_hits = []
        seen = set()
        for part in (hit_title, hit_attach, hit_body):
            if not part:
                continue
            for kw in part.split(','):
                if kw and kw not in seen:
                    combined_hits.append(kw)
                    seen.add(kw)

        return hit_title, hit_attach, hit_body, ",".join(combined_hits)

    print(f"총 행 수: {len(df)}")

    # Apply and expand to 4 columns
    hits = df.apply(find_keywords_in_row, axis=1, result_type='expand')
    hits.columns = [COL_OUT_TITLE, COL_OUT_ATTACH, COL_OUT_BODY, COL_OUT]
    df[[COL_OUT_TITLE, COL_OUT_ATTACH, COL_OUT_BODY, COL_OUT]] = hits

    hit_rows = (df[COL_OUT].fillna("").astype(str).str.len() > 0).sum()
    print(f"히트 행 수: {hit_rows}")

    out_path = input_path.parent / "keyword_based_detection_by_dept.xlsx"

    # Write: full data to Sheet1 + hit rows split by department into separate sheets
    def sanitize_sheet_name(name: str) -> str:
        # Excel sheet name rules: max 31 chars, cannot contain: : \ / ? * [ ]
        bad = [':', '\\', '/', '?', '*', '[', ']']
        for ch in bad:
            name = name.replace(ch, '_')
        name = name.strip()
        if not name:
            name = 'UNKNOWN'
        return name[:31]

    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        # Only hit rows
        hits_df = df[df[COL_OUT].fillna('').astype(str).str.len() > 0].copy()

        if COL_DEPT not in hits_df.columns:
            # If department column missing, write a single sheet
            hits_df.to_excel(writer, index=False, sheet_name='HITS')
        else:
            for dept, grp in hits_df.groupby(hits_df[COL_DEPT].fillna('UNKNOWN').astype(str)):
                sheet = sanitize_sheet_name(dept)
                # Avoid collision if two names sanitize to same 31 chars
                base = sheet
                i = 2
                while sheet in writer.book.sheetnames:
                    suffix = f"_{i}"
                    sheet = (base[:31-len(suffix)] + suffix)[:31]
                    i += 1
                grp.to_excel(writer, index=False, sheet_name=sheet)

    print(f"출력 파일: {out_path.resolve()}")

    elapsed = time.perf_counter() - start
    print(f"처리 시간: {elapsed:.2f}초")


if __name__ == "__main__":
    main()
