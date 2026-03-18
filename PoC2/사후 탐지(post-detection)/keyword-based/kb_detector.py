"""Keyword-based post-detection core logic.

This module is shared by both CLI and Web UI.
"""

from __future__ import annotations

import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

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

COL_DEPT = "발신자부서명"

COL_OUT = "detected-keyword"
COL_OUT_TITLE = "detected-title"
COL_OUT_ATTACH = "detected-attachment"
COL_OUT_BODY = "detected-body"


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


def parse_keywords_from_text(text: str) -> list[str]:
    # treat as one keyword per line
    keywords = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    if not keywords:
        raise ValueError("No keywords provided")
    return keywords


def safe_str(x) -> str:
    return "" if pd.isna(x) else str(x)


def sanitize_sheet_name(name: str) -> str:
    # Excel sheet name rules: max 31 chars, cannot contain: : \ / ? * [ ]
    bad = [":", "\\", "/", "?", "*", "[", "]"]
    for ch in bad:
        name = name.replace(ch, "_")
    name = name.strip()
    if not name:
        name = "UNKNOWN"
    return name[:31]


@dataclass
class DetectionResult:
    df_all: pd.DataFrame
    df_hits: pd.DataFrame
    elapsed_sec: float
    stats: dict


def _ensure_columns(df: pd.DataFrame, cols: Iterable[str]) -> None:
    for c in cols:
        if c not in df.columns:
            df[c] = ""


def detect_keywords(df: pd.DataFrame, keywords: list[str]) -> DetectionResult:
    start = time.perf_counter()

    _ensure_columns(df, [COL_TITLE, COL_SAMSUNG, COL_VENDOR, COL_BODY])

    def find_keywords_in_text(text: str) -> list[str]:
        # keep original keyword order (keywords list)
        return [kw for kw in keywords if kw and kw in text]

    def find_keywords_in_row(row):
        title = safe_str(row.get(COL_TITLE))
        samsung = safe_str(row.get(COL_SAMSUNG))
        vendor = safe_str(row.get(COL_VENDOR))
        body = safe_str(row.get(COL_BODY))

        if "base64," in body:
            body = BASE64_RE.sub("<BASE64_IMAGE>", body)

        attachment_text = f"{samsung} {vendor}".strip()

        hit_title = find_keywords_in_text(title)
        hit_attach = find_keywords_in_text(attachment_text)
        hit_body = find_keywords_in_text(body)

        # union (preserve order in keywords)
        seen = set()
        combined_hits: list[str] = []
        for part in (hit_title, hit_attach, hit_body):
            for kw in part:
                if kw not in seen:
                    combined_hits.append(kw)
                    seen.add(kw)

        return ",".join(hit_title), ",".join(hit_attach), ",".join(hit_body), ",".join(combined_hits)

    hits = df.apply(find_keywords_in_row, axis=1, result_type="expand")
    hits.columns = [COL_OUT_TITLE, COL_OUT_ATTACH, COL_OUT_BODY, COL_OUT]
    df[[COL_OUT_TITLE, COL_OUT_ATTACH, COL_OUT_BODY, COL_OUT]] = hits

    # hit-only
    df_hits = df[df[COL_OUT].fillna("").astype(str).str.len() > 0].copy()

    elapsed = time.perf_counter() - start

    # basic stats
    total_rows = int(len(df))
    hit_rows = int(len(df_hits))
    hit_rate = (hit_rows / total_rows) if total_rows else 0.0

    dept_counts = {}
    if COL_DEPT in df_hits.columns:
        dept_counts = (
            df_hits[COL_DEPT]
            .fillna("UNKNOWN")
            .astype(str)
            .value_counts()
            .to_dict()
        )

    # keyword hit counts (by detected-keyword union column)
    kw_counter: Counter[str] = Counter()
    for s in df_hits[COL_OUT].fillna("").astype(str).tolist():
        for kw in [p.strip() for p in s.split(",") if p.strip()]:
            kw_counter[kw] += 1

    stats = {
        "total_rows": total_rows,
        "hit_rows": hit_rows,
        "hit_rate": hit_rate,
        "dept_counts": dept_counts,
        "keyword_counts": dict(kw_counter.most_common()),
        "keywords_used": keywords,
    }

    return DetectionResult(df_all=df, df_hits=df_hits, elapsed_sec=elapsed, stats=stats)


def write_outputs(
    result: DetectionResult,
    out_combined_xlsx: Path,
    dept_files_dir: Path | None = None,
) -> list[Path]:
    """Write combined xlsx with dept sheets, and optionally dept-per-file xlsx files.

    Returns: list of generated dept file paths (empty if dept_files_dir is None)
    """

    out_combined_xlsx.parent.mkdir(parents=True, exist_ok=True)

    def _safe_dept(val) -> str:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "UNKNOWN"
        s = str(val).strip()
        return s if s else "UNKNOWN"

    dept_paths: list[Path] = []

    with pd.ExcelWriter(out_combined_xlsx, engine="openpyxl") as writer:
        result.df_all.to_excel(writer, index=False, sheet_name="Sheet1")

        hits_df = result.df_hits

        if COL_DEPT not in hits_df.columns:
            hits_df.to_excel(writer, index=False, sheet_name="HITS")
        else:
            for dept, grp in hits_df.groupby(hits_df[COL_DEPT].map(_safe_dept)):
                sheet = sanitize_sheet_name(dept)
                base = sheet
                i = 2
                while sheet in writer.book.sheetnames:
                    suffix = f"_{i}"
                    sheet = (base[: 31 - len(suffix)] + suffix)[:31]
                    i += 1
                grp.to_excel(writer, index=False, sheet_name=sheet)

                if dept_files_dir is not None:
                    dept_files_dir.mkdir(parents=True, exist_ok=True)
                    fname = sanitize_sheet_name(dept)
                    dept_path = dept_files_dir / f"{fname}.xlsx"
                    # individual file: only hit rows for that dept
                    with pd.ExcelWriter(dept_path, engine="openpyxl") as w2:
                        grp.to_excel(w2, index=False, sheet_name="HITS")
                    dept_paths.append(dept_path)

    return dept_paths
