"""Context-based post-detection core logic.

Shared core for CLI and Web UI.

Notes
- Uses OpenAI python SDK (AsyncOpenAI) Responses API.
- Reads defaults from .env via dotenv, but web can override some values.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd
from dotenv import load_dotenv

try:
    from openai import AsyncOpenAI
except Exception as e:
    raise RuntimeError(
        "Missing dependency 'openai'. Install with: pip install openai python-dotenv pandas openpyxl"
    ) from e


# -----------------------------
# Helpers: env
# -----------------------------

def env_str(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return default if v is None or v == "" else v


def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return int(v)


def env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return float(v)


def env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


# -----------------------------
# Base64 / HTML strip
# -----------------------------

BASE64_RE = re.compile(
    r"data:image/[^;]+;base64,[A-Za-z0-9+/=\n\r]+",
    re.IGNORECASE,
)

HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    return HTML_TAG_RE.sub(" ", text)


def safe_str(x) -> str:
    return "" if pd.isna(x) else str(x)


def truncate_body(body: str, max_chars: int, mode: str) -> str:
    if max_chars <= 0:
        return body
    if len(body) <= max_chars:
        return body
    if mode == "head_only":
        return body[:max_chars]
    half = max_chars // 2
    return body[:half] + "\n...<TRUNCATED>...\n" + body[-half:]


# -----------------------------
# Candidate scoring (simple)
# -----------------------------

REQUEST_INTENT_TERMS = [
    "요청",
    "부탁",
    "회신",
    "확인 부탁",
    "검토",
    "검토 요청",
    "확인 요청",
    "회신 요청",
    "가능",
    "일정",
    "기한",
    "납기",
    "입고",
    "긴급",
    "전달 부탁",
    "공유 부탁",
    "please review",
    "review request",
    "reply",
    "feedback",
    "asap",
    "deadline",
]

TECH_ARTIFACT_HINTS = [
    "도면",
    "설계",
    "회로",
    "공정",
    "사양",
    "규격",
    "검사",
    "성적서",
    "BOM",
    "part list",
    "spec",
    "drawing",
    "schematic",
    "layout",
    "gerber",
    "firmware",
    "log",
]

STRONG_EXTENSIONS = {"dwg", "dxf", "stp", "step", "igs", "iges", "x_t", "zip", "rar", "7z", "gerber"}


def count_term_hits(text: str, terms: list[str]) -> int:
    t = (text or "").lower()
    n = 0
    for term in terms:
        if term.lower() in t:
            n += 1
    return n


def attachment_signal(attach_text: str) -> int:
    t = (attach_text or "").lower()
    hits = 0
    for ext in STRONG_EXTENSIONS:
        if f".{ext}" in t or t.endswith(ext) or f"_{ext}" in t:
            hits += 1
    return hits


# -----------------------------
# Cache
# -----------------------------

def make_cache_key(row: pd.Series, key_col: str, title_col: str, body_col: str, a1_col: str, a2_col: str) -> str:
    if key_col and key_col in row and not pd.isna(row[key_col]) and str(row[key_col]).strip() != "":
        return str(row[key_col]).strip()
    raw = "|".join(
        [
            safe_str(row.get(title_col, "")),
            safe_str(row.get(a1_col, "")),
            safe_str(row.get(a2_col, "")),
            safe_str(row.get(body_col, "")),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def cache_path(cache_dir: Path, key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", key)
    return cache_dir / f"{safe}.json"


# -----------------------------
# LLM
# -----------------------------

@dataclass
class LLMConfig:
    api_key: str
    model: str
    temperature: float
    max_output_tokens: int
    timeout_seconds: int
    max_retries: int
    retry_backoff_seconds: float
    concurrency: int


def load_prompt_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path.resolve()}")
    return path.read_text(encoding="utf-8")


def build_prompt(template: str, title: str, body: str, attachments: str, meta: Dict[str, str]) -> str:
    meta_lines = "\n".join([f"- {k}: {v}" for k, v in meta.items() if v])

    prompt = template
    prompt = prompt.replace("{{META}}", meta_lines)
    prompt = prompt.replace("{{TITLE}}", title)
    prompt = prompt.replace("{{ATTACHMENTS}}", attachments)
    prompt = prompt.replace("{{BODY}}", body)

    return prompt.strip()


async def call_llm(client: AsyncOpenAI, cfg: LLMConfig, prompt: str) -> Dict[str, Any]:
    last_err = None
    for attempt in range(cfg.max_retries + 1):
        try:
            resp = await client.responses.create(
                model=cfg.model,
                input=prompt,
                temperature=cfg.temperature,
                max_output_tokens=cfg.max_output_tokens,
            )
            text = resp.output_text
            return json.loads(text)
        except Exception as e:
            last_err = e
            if attempt >= cfg.max_retries:
                break
            await asyncio.sleep(cfg.retry_backoff_seconds * (attempt + 1))
    raise RuntimeError(f"LLM call failed after retries: {last_err}")


# -----------------------------
# Public API
# -----------------------------

@dataclass
class ContextDetectionSettings:
    # LLM
    openai_api_key: str
    openai_model: str = "gpt-5.2"
    openai_temperature: float = 0.1
    openai_max_output_tokens: int = 1200
    openai_timeout_seconds: int = 60
    openai_max_retries: int = 3
    openai_retry_backoff_seconds: float = 2.0
    openai_concurrency: int = 5

    # Candidate selection
    candidate_ratio: float = 0.05
    candidate_min_rows: int = 200
    candidate_max_rows: int = 10000

    keyword_weight: int = 25
    request_intent_weight: int = 35
    attachment_signal_weight: int = 40

    hit_risk_level_threshold: int = 3

    # Columns
    col_title: str = "제목"
    col_body: str = "본문내용"
    col_attach_samsung: str = "일반자료명: 삼성등록"
    col_attach_vendor: str = "일반자료명: 협력사등록"
    col_dept: str = "발신자부서명"

    col_out_keyword: str = "detected-keyword"
    col_out_context_score: str = "context_risk_score"
    col_out_context_level: str = "context_risk_level"
    col_out_intent: str = "context_intent"
    col_out_artifact: str = "context_artifact_type"
    col_out_evidence: str = "context_evidence"
    col_out_reason: str = "context_reason"

    # Keyword file / prompt
    keywords: list[str] | None = None
    prompt_template: str | None = None

    # Text clean
    base64_placeholder: str = "<BASE64_IMAGE>"
    body_max_chars: int = 10000
    body_trim_mode: str = "head_tail"

    # Cache
    cache_enabled: bool = True
    cache_dir: Path = Path("./cache_context_detection")
    cache_key_col: str = "전송코드"


@dataclass
class ContextDetectionResult:
    df_all: pd.DataFrame
    df_candidates: pd.DataFrame
    df_hits: pd.DataFrame
    elapsed_sec: float
    stats: dict


def load_defaults_from_env(env_path_dir: Path | None = None) -> ContextDetectionSettings:
    # load_dotenv from cwd by default
    if env_path_dir is None:
        load_dotenv()
    else:
        load_dotenv(dotenv_path=str(env_path_dir / ".env"), override=False)

    api_key = env_str("OPENAI_API_KEY", "")

    s = ContextDetectionSettings(
        openai_api_key=api_key,
        openai_model=env_str("OPENAI_MODEL", "gpt-5.2"),
        openai_temperature=env_float("OPENAI_TEMPERATURE", 0.1),
        openai_max_output_tokens=env_int("OPENAI_MAX_OUTPUT_TOKENS", 1200),
        openai_timeout_seconds=env_int("OPENAI_TIMEOUT_SECONDS", 60),
        openai_max_retries=env_int("OPENAI_MAX_RETRIES", 3),
        openai_retry_backoff_seconds=env_float("OPENAI_RETRY_BACKOFF_SECONDS", 2.0),
        openai_concurrency=env_int("OPENAI_CONCURRENCY", 5),
        candidate_ratio=env_float("CANDIDATE_RATIO", 0.05),
        candidate_min_rows=env_int("CANDIDATE_MIN_ROWS", 200),
        candidate_max_rows=env_int("CANDIDATE_MAX_ROWS", 10000),
        keyword_weight=env_int("KEYWORD_WEIGHT", 25),
        request_intent_weight=env_int("REQUEST_INTENT_WEIGHT", 35),
        attachment_signal_weight=env_int("ATTACHMENT_SIGNAL_WEIGHT", 40),
        hit_risk_level_threshold=env_int("HIT_RISK_LEVEL_THRESHOLD", 3),
        col_title=env_str("COL_TITLE", "제목"),
        col_body=env_str("COL_BODY", "본문내용"),
        col_attach_samsung=env_str("COL_ATTACH_SAMSUNG", "일반자료명: 삼성등록"),
        col_attach_vendor=env_str("COL_ATTACH_VENDOR", "일반자료명: 협력사등록"),
        col_dept=env_str("COL_DEPT", "발신자부서명"),
        col_out_keyword=env_str("COL_OUT_KEYWORD", "detected-keyword"),
        col_out_context_score=env_str("COL_OUT_CONTEXT_SCORE", "context_risk_score"),
        col_out_context_level=env_str("COL_OUT_CONTEXT_LEVEL", "context_risk_level"),
        col_out_intent=env_str("COL_OUT_INTENT", "context_intent"),
        col_out_artifact=env_str("COL_OUT_ARTIFACT", "context_artifact_type"),
        col_out_evidence=env_str("COL_OUT_EVIDENCE", "context_evidence"),
        col_out_reason=env_str("COL_OUT_REASON", "context_reason"),
        base64_placeholder=env_str("BASE64_PLACEHOLDER", "<BASE64_IMAGE>"),
        body_max_chars=env_int("BODY_MAX_CHARS", 10000),
        body_trim_mode=env_str("BODY_TRIM_MODE", "head_tail"),
        cache_enabled=env_bool("CACHE_ENABLED", True),
        cache_dir=Path(env_str("CACHE_DIR", "./cache_context_detection")),
        cache_key_col=env_str("CACHE_KEY_COL", "전송코드"),
    )

    # load files if available
    kw_path = Path(env_str("KEYWORD_FILE_PATH", "./detection_keywords.md"))
    if kw_path.exists():
        s.keywords = [ln.strip() for ln in kw_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    prompt_path = Path(env_str("PROMPT_FILE_PATH", "./prompt_context_detection.md"))
    if prompt_path.exists():
        s.prompt_template = prompt_path.read_text(encoding="utf-8")

    return s


def _ensure_columns(df: pd.DataFrame, cols: Iterable[str]) -> None:
    for c in cols:
        if c not in df.columns:
            df[c] = ""


def _sanitize_sheet(name: str) -> str:
    bad = [":", "\\", "/", "?", "*", "[", "]"]
    for ch in bad:
        name = name.replace(ch, "_")
    name = name.strip() or "UNKNOWN"
    return name[:31]


async def detect_context_async(df: pd.DataFrame, settings: ContextDetectionSettings) -> ContextDetectionResult:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is empty. Please set it in .env (or provide in Web UI)")
    if not settings.prompt_template:
        raise RuntimeError("Prompt template is empty. Check prompt_context_detection.md")
    if not settings.keywords:
        raise RuntimeError("Keyword list is empty. Check detection_keywords.md")

    start = time.perf_counter()

    # ensure required columns
    _ensure_columns(df, [settings.col_title, settings.col_body, settings.col_attach_samsung, settings.col_attach_vendor])
    if settings.col_dept not in df.columns:
        df[settings.col_dept] = ""

    keywords = settings.keywords

    def kw_hits(row) -> str:
        text = " ".join(
            [
                safe_str(row.get(settings.col_title)),
                safe_str(row.get(settings.col_attach_samsung)),
                safe_str(row.get(settings.col_attach_vendor)),
                safe_str(row.get(settings.col_body)),
            ]
        )
        if "base64," in text:
            text = BASE64_RE.sub(settings.base64_placeholder, text)
        return ",".join([kw for kw in keywords if kw in text])

    df[settings.col_out_keyword] = df.apply(kw_hits, axis=1)

    def candidate_score(row) -> int:
        title = safe_str(row.get(settings.col_title))
        body = safe_str(row.get(settings.col_body))
        attach = f"{safe_str(row.get(settings.col_attach_samsung))} {safe_str(row.get(settings.col_attach_vendor))}".strip()

        if "base64," in body:
            body = BASE64_RE.sub(settings.base64_placeholder, body)
        body_clean = strip_html(body)
        body_clean = truncate_body(body_clean, settings.body_max_chars, settings.body_trim_mode)

        kw = safe_str(row.get(settings.col_out_keyword))
        kw_signal = 1 if kw.strip() else 0

        intent_hits = count_term_hits(f"{title} {body_clean}", REQUEST_INTENT_TERMS)
        artifact_hits = count_term_hits(f"{title} {body_clean} {attach}", TECH_ARTIFACT_HINTS)
        attach_hits = attachment_signal(attach)

        score = 0
        score += settings.keyword_weight * kw_signal
        score += min(100, intent_hits) * (settings.request_intent_weight // 10)
        score += min(100, (artifact_hits + attach_hits)) * (settings.attachment_signal_weight // 10)
        return int(min(100, score))

    df["candidate_score"] = df.apply(candidate_score, axis=1)

    n = len(df)
    k = int(max(settings.candidate_min_rows, min(settings.candidate_max_rows, round(n * settings.candidate_ratio))))
    k = min(k, n)

    df_candidates = df.sort_values("candidate_score", ascending=False).head(k).copy()

    # cache
    if settings.cache_enabled:
        settings.cache_dir.mkdir(parents=True, exist_ok=True)

    llm_cfg = LLMConfig(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=settings.openai_temperature,
        max_output_tokens=settings.openai_max_output_tokens,
        timeout_seconds=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
        retry_backoff_seconds=settings.openai_retry_backoff_seconds,
        concurrency=settings.openai_concurrency,
    )

    client = AsyncOpenAI(api_key=llm_cfg.api_key, timeout=llm_cfg.timeout_seconds)
    sem = asyncio.Semaphore(max(1, llm_cfg.concurrency))

    async def process_one(idx: int, row: pd.Series):
        key = make_cache_key(
            row,
            settings.cache_key_col,
            settings.col_title,
            settings.col_body,
            settings.col_attach_samsung,
            settings.col_attach_vendor,
        )

        if settings.cache_enabled:
            p = cache_path(settings.cache_dir, key)
            if p.exists():
                try:
                    return idx, json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass

        title = safe_str(row.get(settings.col_title))
        attach = f"{safe_str(row.get(settings.col_attach_samsung))} {safe_str(row.get(settings.col_attach_vendor))}".strip()
        body = safe_str(row.get(settings.col_body))

        if "base64," in body:
            body = BASE64_RE.sub(settings.base64_placeholder, body)
        body = strip_html(body)
        body = truncate_body(body, settings.body_max_chars, settings.body_trim_mode)

        meta = {
            "발신자부서명": safe_str(row.get(settings.col_dept)),
            "키워드히트": safe_str(row.get(settings.col_out_keyword)),
            "candidate_score": str(row.get("candidate_score", "")),
        }

        prompt = build_prompt(
            template=settings.prompt_template or "",
            title=title,
            body=body,
            attachments=attach,
            meta=meta,
        )

        async with sem:
            res = await call_llm(client, llm_cfg, prompt)

        res["llm_model"] = llm_cfg.model

        if settings.cache_enabled:
            p = cache_path(settings.cache_dir, key)
            try:
                p.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass

        return idx, res

    tasks = [process_one(i, row) for i, row in df_candidates.iterrows()]
    results: Dict[int, Dict[str, Any]] = {}
    for fut in asyncio.as_completed(tasks):
        idx, res = await fut
        results[idx] = res

    # fill outputs
    # NOTE: Pandas 3.x may infer strict 'str' dtype when assigning ""; then ints cannot be assigned.
    # Use explicit dtypes.
    if settings.col_out_context_score not in df.columns:
        df[settings.col_out_context_score] = pd.Series([pd.NA] * len(df), dtype="Int64")
    else:
        df[settings.col_out_context_score] = pd.Series([pd.NA] * len(df), dtype="Int64")

    if settings.col_out_context_level not in df.columns:
        df[settings.col_out_context_level] = pd.Series([pd.NA] * len(df), dtype="Int64")
    else:
        df[settings.col_out_context_level] = pd.Series([pd.NA] * len(df), dtype="Int64")

    for col in [
        settings.col_out_intent,
        settings.col_out_artifact,
        settings.col_out_evidence,
        settings.col_out_reason,
        "llm_model",
    ]:
        df[col] = pd.Series([None] * len(df), dtype="object")

    def _to_int(v):
        try:
            if v is None or v == "":
                return pd.NA
            return int(v)
        except Exception:
            return pd.NA

    for idx, res in results.items():
        df.at[idx, settings.col_out_context_score] = _to_int(res.get("risk_score", ""))
        df.at[idx, settings.col_out_context_level] = _to_int(res.get("risk_level", ""))
        df.at[idx, settings.col_out_intent] = str(res.get("intent", "") or "")
        df.at[idx, settings.col_out_artifact] = str(res.get("artifact_type", "") or "")
        ev = res.get("evidence", [])
        if isinstance(ev, list):
            df.at[idx, settings.col_out_evidence] = " | ".join([str(x) for x in ev if x])
        else:
            df.at[idx, settings.col_out_evidence] = str(ev or "")
        df.at[idx, settings.col_out_reason] = str(res.get("reason", "") or "")
        df.at[idx, "llm_model"] = str(res.get("llm_model", llm_cfg.model) or llm_cfg.model)

    def is_hit(v) -> bool:
        try:
            return int(v) >= int(settings.hit_risk_level_threshold)
        except Exception:
            return False

    df_hits = df[df[settings.col_out_context_level].apply(is_hit)].copy()

    elapsed = time.perf_counter() - start

    # stats
    total_rows = int(len(df))
    cand_rows = int(len(df_candidates))
    hit_rows = int(len(df_hits))
    hit_rate = (hit_rows / total_rows) if total_rows else 0.0

    dept_counts = {}
    if settings.col_dept in df_hits.columns:
        dept_counts = (
            df_hits[settings.col_dept].fillna("UNKNOWN").astype(str).value_counts().to_dict()
        )

    intent_counts = Counter([safe_str(x) for x in df_hits[settings.col_out_intent].fillna("").tolist() if safe_str(x)])
    artifact_counts = Counter([safe_str(x) for x in df_hits[settings.col_out_artifact].fillna("").tolist() if safe_str(x)])

    stats = {
        "total_rows": total_rows,
        "candidate_rows": cand_rows,
        "hit_rows": hit_rows,
        "hit_rate": hit_rate,
        "dept_counts": dept_counts,
        "intent_counts": dict(intent_counts.most_common()),
        "artifact_counts": dict(artifact_counts.most_common()),
        "model": settings.openai_model,
        "threshold": settings.hit_risk_level_threshold,
    }

    return ContextDetectionResult(
        df_all=df,
        df_candidates=df_candidates,
        df_hits=df_hits,
        elapsed_sec=elapsed,
        stats=stats,
    )


def write_outputs(
    result: ContextDetectionResult,
    out_combined_xlsx: Path,
    split_by_dept: bool = True,
    include_sheet1: bool = True,
    dept_files_dir: Path | None = None,
    dept_col: str = "발신자부서명",
) -> list[Path]:
    """Write combined xlsx and optionally dept-per-file xlsx.

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
        if include_sheet1:
            result.df_all.to_excel(writer, index=False, sheet_name="Sheet1")

        hits_df = result.df_hits

        if not split_by_dept:
            hits_df.to_excel(writer, index=False, sheet_name="HITS")
        else:
            if dept_col not in hits_df.columns:
                hits_df.to_excel(writer, index=False, sheet_name="HITS")
            else:
                for dept, grp in hits_df.groupby(hits_df[dept_col].map(_safe_dept)):
                    sheet = _sanitize_sheet(dept)
                    base = sheet
                    i = 2
                    while sheet in writer.book.sheetnames:
                        suffix = f"_{i}"
                        sheet = (base[: 31 - len(suffix)] + suffix)[:31]
                        i += 1
                    grp.to_excel(writer, index=False, sheet_name=sheet)

                    if dept_files_dir is not None:
                        dept_files_dir.mkdir(parents=True, exist_ok=True)
                        fname = _sanitize_sheet(dept)
                        dept_path = dept_files_dir / f"{fname}.xlsx"
                        with pd.ExcelWriter(dept_path, engine="openpyxl") as w2:
                            grp.to_excel(w2, index=False, sheet_name="HITS")
                        dept_paths.append(dept_path)

    return dept_paths


def default_output_basename(input_filename: str) -> str:
    stem = Path(input_filename).stem
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stem}_context_detection_{ts}"
