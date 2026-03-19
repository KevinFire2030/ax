from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from llm_client import LLMClient

BASE64_RE = re.compile(r"data:image/[^;]+;base64,[A-Za-z0-9+/=\n\r]+", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")


def safe_str(x) -> str:
    return "" if pd.isna(x) else str(x)


def strip_html(text: str) -> str:
    return HTML_TAG_RE.sub(" ", text or "")


def truncate_body(body: str, max_chars: int = 10000) -> str:
    if max_chars <= 0:
        return body
    if len(body) <= max_chars:
        return body
    half = max_chars // 2
    return body[:half] + "\n...<TRUNCATED>...\n" + body[-half:]


@dataclass
class Columns:
    title: str
    body: str
    a1: str
    a2: str
    dept: str


@dataclass
class Settings:
    candidate_ratio: float
    candidate_min_rows: int
    candidate_max_rows: int
    hit_level_threshold: int
    cache_enabled: bool
    cache_dir: Path
    cache_key_col: str
    base64_placeholder: str = "<BASE64_IMAGE>"
    body_max_chars: int = 10000


def read_keywords(path: Path) -> List[str]:
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]


def read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_prompt(template: str, *, meta: Dict[str, str], title: str, body: str, attachments: str) -> str:
    meta_lines = "\n".join([f"- {k}: {v}" for k, v in meta.items() if v])
    p = template
    p = p.replace("{{META}}", meta_lines)
    p = p.replace("{{TITLE}}", title)
    p = p.replace("{{ATTACHMENTS}}", attachments)
    p = p.replace("{{BODY}}", body)
    return p.strip()


def make_cache_key(row: pd.Series, key_col: str, cols: Columns) -> str:
    if key_col and key_col in row and not pd.isna(row[key_col]) and str(row[key_col]).strip() != "":
        return str(row[key_col]).strip()
    raw = "|".join(
        [
            safe_str(row.get(cols.title, "")),
            safe_str(row.get(cols.a1, "")),
            safe_str(row.get(cols.a2, "")),
            safe_str(row.get(cols.body, "")),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def cache_path(cache_dir: Path, key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", key)
    return cache_dir / f"{safe}.json"


def ensure_cols(df: pd.DataFrame, cols: Columns) -> None:
    for c in [cols.title, cols.body, cols.a1, cols.a2, cols.dept]:
        if c not in df.columns:
            df[c] = ""


def pick_random_row(df: pd.DataFrame) -> Tuple[int, Dict[str, Any]]:
    idx = random.choice(list(df.index))
    row = df.loc[idx]
    return int(idx), row.to_dict()


def build_row_text(row: Dict[str, Any], cols: Columns, s: Settings) -> Tuple[str, str, str]:
    title = safe_str(row.get(cols.title, ""))
    body = safe_str(row.get(cols.body, ""))
    a1 = safe_str(row.get(cols.a1, ""))
    a2 = safe_str(row.get(cols.a2, ""))
    attach = f"{a1} {a2}".strip()

    if "base64," in body:
        body = BASE64_RE.sub(s.base64_placeholder, body)
    body = strip_html(body)
    body = truncate_body(body, s.body_max_chars)

    return title, body, attach


def candidate_indices(df: pd.DataFrame, cols: Columns, s: Settings, keywords: List[str]) -> List[int]:
    # simple scoring: keyword hits count
    def kw_hits(row) -> int:
        text = " ".join([
            safe_str(row.get(cols.title)),
            safe_str(row.get(cols.a1)),
            safe_str(row.get(cols.a2)),
            safe_str(row.get(cols.body)),
        ])
        if "base64," in text:
            text = BASE64_RE.sub(s.base64_placeholder, text)
        return sum(1 for kw in keywords if kw and kw in text)

    scores = df.apply(kw_hits, axis=1)
    n = len(df)
    k = int(max(s.candidate_min_rows, min(s.candidate_max_rows, round(n * s.candidate_ratio))))
    k = min(k, n)
    top = scores.sort_values(ascending=False).head(k)
    return [int(i) for i in top.index.tolist()]


def call_one(
    *,
    llm: LLMClient,
    prompt_template: str,
    keywords: List[str],
    row_idx: int,
    row: pd.Series,
    cols: Columns,
    s: Settings,
) -> Dict[str, Any]:
    # cache
    key = make_cache_key(row, s.cache_key_col, cols)
    if s.cache_enabled:
        s.cache_dir.mkdir(parents=True, exist_ok=True)
        p = cache_path(s.cache_dir, key)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass

    title, body, attach = build_row_text(row.to_dict(), cols, s)
    meta = {
        cols.dept: safe_str(row.get(cols.dept, "")),
        "candidate": "1",
        "keyword_hits": str(sum(1 for kw in keywords if kw and kw in (title + body + attach))),
    }
    prompt = build_prompt(prompt_template, meta=meta, title=title, body=body, attachments=attach)

    start = time.perf_counter()
    res = llm.call_json(prompt)
    res["elapsed_sec"] = time.perf_counter() - start

    if s.cache_enabled:
        try:
            cache_path(s.cache_dir, key).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    return res
