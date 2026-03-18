# filename: keyword-based_detection.py
# usage: python keyword-based_detection.py sample.xlsx
# (optional) python keyword-based_detection.py sample.xlsx detection_keywords.md

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from kb_detector import DEFAULT_KEYWORD_FILE, detect_keywords, read_keywords, write_outputs


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python keyword-based_detection.py <input.xlsx> [keywords.md]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path.resolve()}")

    keyword_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_KEYWORD_FILE
    keywords = read_keywords(keyword_path)

    df = pd.read_excel(input_path, sheet_name=0)
    result = detect_keywords(df, keywords)

    print(f"총 행 수: {result.stats['total_rows']}")
    print(f"히트 행 수: {result.stats['hit_rows']}")

    out_path = input_path.parent / "keyword_based_detection_by_dept.xlsx"
    write_outputs(result, out_path, dept_files_dir=None)

    print(f"출력 파일: {out_path.resolve()}")
    print(f"처리 시간: {result.elapsed_sec:.2f}초")


if __name__ == "__main__":
    main()
