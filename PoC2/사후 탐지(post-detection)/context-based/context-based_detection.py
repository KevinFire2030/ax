# filename: context-based_detection.py
# usage: python "context-based_detection.py" input.xlsx
# notes:
# - Loads settings from .env (python-dotenv)
# - Builds candidate set from keyword hits + simple request-intent signals + attachment signals
# - Sends ONLY candidate rows to LLM (gpt-5.2) with concurrency
# - Caches LLM results to disk to avoid repeated calls

import asyncio
import hashlib
import json
import os
import re
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

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
# Base64 strip
# -----------------------------

BASE64_RE = re.compile(
    r"data:image/[^;]+;base64,[A-Za-z0-9+/=\n\r]+",
    re.IGNORECASE,
)

HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    # lightweight: remove tags only
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
    # head_tail
    half = max_chars // 2
    return body[:half] + "\n...<TRUNCATED>...\n" + body[-half:]


# -----------------------------
# Candidate scoring (simple)
# -----------------------------

REQUEST_INTENT_TERMS = [
    # Korean: request / review / reply / schedule
    "요청", "부탁", "회신", "확인 부탁", "검토", "검토 요청", "확인 요청", "회신 요청",
    "가능", "일정", "기한", "납기", "입고", "긴급", "전달 부탁", "공유 부탁",
    # English-ish patterns
    "please review", "review request", "reply", "feedback", "asap", "deadline",
]

TECH_ARTIFACT_HINTS = [
    "도면", "설계", "회로", "공정", "사양", "규격", "검사", "성적서", "BOM", "part list",
    "spec", "drawing", "schematic", "layout", "gerber", "firmware", "log",
]

STRONG_EXTENSIONS = {"dwg", "dxf", "stp", "step", "igs", "iges", "x_t", "zip", "rar", "7z", "gerber"}


def count_term_hits(text: str, terms: list[str]) -> int:
    t = text.lower()
    n = 0
    for term in terms:
        if term.lower() in t:
            n += 1
    return n


def attachment_signal(attach_text: str) -> int:
    # returns 0/1/2...
    t = attach_text.lower()
    hits = 0
    # extension hits
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
    # safe filename
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
            # Using Responses API style via openai python
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
# Main
# -----------------------------


async def run(input_path: Path) -> None:
    load_dotenv()  # loads .env from cwd

    # LLM config
    api_key = env_str("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is empty. Please set it in .env")

    llm_cfg = LLMConfig(
        api_key=api_key,
        model=env_str("OPENAI_MODEL", "gpt-5.2"),
        temperature=env_float("OPENAI_TEMPERATURE", 0.1),
        max_output_tokens=env_int("OPENAI_MAX_OUTPUT_TOKENS", 1200),
        timeout_seconds=env_int("OPENAI_TIMEOUT_SECONDS", 60),
        max_retries=env_int("OPENAI_MAX_RETRIES", 3),
        retry_backoff_seconds=env_float("OPENAI_RETRY_BACKOFF_SECONDS", 2.0),
        concurrency=env_int("OPENAI_CONCURRENCY", 5),
    )

    # Prompt template
    prompt_path = Path(env_str("PROMPT_FILE_PATH", "./prompt_context_detection.md"))
    prompt_template = load_prompt_template(prompt_path)

    # Candidate settings
    candidate_ratio = env_float("CANDIDATE_RATIO", 0.05)
    cand_min = env_int("CANDIDATE_MIN_ROWS", 200)
    cand_max = env_int("CANDIDATE_MAX_ROWS", 10000)

    w_keyword = env_int("KEYWORD_WEIGHT", 25)
    w_request = env_int("REQUEST_INTENT_WEIGHT", 35)
    w_attach = env_int("ATTACHMENT_SIGNAL_WEIGHT", 40)

    hit_level_threshold = env_int("HIT_RISK_LEVEL_THRESHOLD", 3)

    # columns
    col_title = env_str("COL_TITLE", "제목")
    col_body = env_str("COL_BODY", "본문내용")
    col_a1 = env_str("COL_ATTACH_SAMSUNG", "일반자료명: 삼성등록")
    col_a2 = env_str("COL_ATTACH_VENDOR", "일반자료명: 협력사등록")
    col_dept = env_str("COL_DEPT", "발신자부서명")

    col_out_keyword = env_str("COL_OUT_KEYWORD", "detected-keyword")
    col_out_score = env_str("COL_OUT_CONTEXT_SCORE", "context_risk_score")
    col_out_level = env_str("COL_OUT_CONTEXT_LEVEL", "context_risk_level")
    col_out_intent = env_str("COL_OUT_INTENT", "context_intent")
    col_out_artifact = env_str("COL_OUT_ARTIFACT", "context_artifact_type")
    col_out_evidence = env_str("COL_OUT_EVIDENCE", "context_evidence")
    col_out_reason = env_str("COL_OUT_REASON", "context_reason")

    keyword_file = Path(env_str("KEYWORD_FILE_PATH", "./detection_keywords.md"))
    if not keyword_file.exists():
        raise FileNotFoundError(f"KEYWORD_FILE_PATH not found: {keyword_file.resolve()}")
    keywords = [line.strip() for line in keyword_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    # text settings
    placeholder = env_str("BASE64_PLACEHOLDER", "<BASE64_IMAGE>")
    body_max_chars = env_int("BODY_MAX_CHARS", 10000)
    body_trim_mode = env_str("BODY_TRIM_MODE", "head_tail")

    # output
    out_name = env_str("OUTPUT_XLSX_NAME", "context_based_detection_by_dept.xlsx")
    # Append timestamp to output filename to avoid overwriting
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    p = Path(out_name)
    out_name = f"{p.stem}_{ts}{p.suffix or '.xlsx'}"
    split_by_dept = env_bool("OUTPUT_SPLIT_BY_DEPT", True)
    include_sheet1 = env_bool("OUTPUT_INCLUDE_SHEET1", True)

    # cache
    cache_enabled = env_bool("CACHE_ENABLED", True)
    cache_dir = Path(env_str("CACHE_DIR", "./cache_context_detection"))
    cache_key_col = env_str("CACHE_KEY_COL", "전송코드")

    if cache_enabled:
        cache_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    df = pd.read_excel(input_path, sheet_name=0)
    for c in [col_title, col_body, col_a1, col_a2]:
        if c not in df.columns:
            df[c] = ""
    if col_dept not in df.columns:
        df[col_dept] = ""

    # 1) keyword hits (simple)
    def kw_hits(row) -> str:
        text = " ".join([safe_str(row.get(col_title)), safe_str(row.get(col_a1)), safe_str(row.get(col_a2)), safe_str(row.get(col_body))])
        if "base64," in text:
            text = BASE64_RE.sub(placeholder, text)
        return ",".join([kw for kw in keywords if kw in text])

    print(f"총 행 수: {len(df)}")
    df[col_out_keyword] = df.apply(kw_hits, axis=1)

    # 2) candidate score
    def candidate_score(row) -> int:
        title = safe_str(row.get(col_title))
        body = safe_str(row.get(col_body))
        attach = f"{safe_str(row.get(col_a1))} {safe_str(row.get(col_a2))}".strip()

        # clean
        if "base64," in body:
            body = BASE64_RE.sub(placeholder, body)
        body_clean = strip_html(body)
        body_clean = truncate_body(body_clean, body_max_chars, body_trim_mode)

        # signals
        kw = safe_str(row.get(col_out_keyword))
        kw_signal = 1 if kw.strip() else 0

        intent_hits = count_term_hits(f"{title} {body_clean}", REQUEST_INTENT_TERMS)
        artifact_hits = count_term_hits(f"{title} {body_clean} {attach}", TECH_ARTIFACT_HINTS)
        attach_hits = attachment_signal(attach)

        # score
        score = 0
        score += w_keyword * kw_signal
        score += min(100, intent_hits) * (w_request // 10)  # scale down
        score += min(100, (artifact_hits + attach_hits)) * (w_attach // 10)
        return int(min(100, score))

    df["candidate_score"] = df.apply(candidate_score, axis=1)

    # Determine candidate rows
    n = len(df)
    k = int(max(cand_min, min(cand_max, round(n * candidate_ratio))))
    k = min(k, n)

    candidates = df.sort_values("candidate_score", ascending=False).head(k).copy()
    print(f"후보군: {k}행 (ratio={candidate_ratio})")

    # LLM client
    client = AsyncOpenAI(api_key=llm_cfg.api_key, timeout=llm_cfg.timeout_seconds)

    sem = asyncio.Semaphore(max(1, llm_cfg.concurrency))

    async def process_one(idx: int, row: pd.Series) -> Tuple[int, Dict[str, Any]]:
        key = make_cache_key(row, cache_key_col, col_title, col_body, col_a1, col_a2)

        if cache_enabled:
            p = cache_path(cache_dir, key)
            if p.exists():
                try:
                    return idx, json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass

        title = safe_str(row.get(col_title))
        attach = f"{safe_str(row.get(col_a1))} {safe_str(row.get(col_a2))}".strip()
        body = safe_str(row.get(col_body))

        if "base64," in body:
            body = BASE64_RE.sub(placeholder, body)
        body = strip_html(body)
        body = truncate_body(body, body_max_chars, body_trim_mode)

        meta = {
            "발신자부서명": safe_str(row.get(col_dept)),
            "키워드히트": safe_str(row.get(col_out_keyword)),
            "candidate_score": str(row.get("candidate_score", "")),
        }

        prompt = build_prompt(template=prompt_template, title=title, body=body, attachments=attach, meta=meta)

        async with sem:
            result = await call_llm(client, llm_cfg, prompt)

        # add model tag
        result["llm_model"] = llm_cfg.model

        if cache_enabled:
            p = cache_path(cache_dir, key)
            try:
                p.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass

        return idx, result

    # Run tasks
    tasks = [process_one(i, row) for i, row in candidates.iterrows()]
    results: Dict[int, Dict[str, Any]] = {}

    # stream-like gather
    for fut in asyncio.as_completed(tasks):
        idx, res = await fut
        results[idx] = res

    # Fill outputs (default empty)
    df[col_out_score] = ""
    df[col_out_level] = ""
    df[col_out_intent] = ""
    df[col_out_artifact] = ""
    df[col_out_evidence] = ""
    df[col_out_reason] = ""
    df["llm_model"] = ""

    for idx, res in results.items():
        df.at[idx, col_out_score] = res.get("risk_score", "")
        df.at[idx, col_out_level] = res.get("risk_level", "")
        df.at[idx, col_out_intent] = res.get("intent", "")
        df.at[idx, col_out_artifact] = res.get("artifact_type", "")
        ev = res.get("evidence", [])
        if isinstance(ev, list):
            df.at[idx, col_out_evidence] = " | ".join([str(x) for x in ev if x])
        else:
            df.at[idx, col_out_evidence] = str(ev)
        df.at[idx, col_out_reason] = res.get("reason", "")
        df.at[idx, "llm_model"] = res.get("llm_model", llm_cfg.model)

    # Hit rows defined by risk level threshold
    def is_hit(v) -> bool:
        try:
            return int(v) >= hit_level_threshold
        except Exception:
            return False

    hit_mask = df[col_out_level].apply(is_hit)
    hit_df = df[hit_mask].copy()

    print(f"LLM 처리 행 수: {len(candidates)}")
    print(f"HIT 행 수(context_risk_level>={hit_level_threshold}): {len(hit_df)}")

    # Write excel
    out_path = input_path.parent / out_name

    def sanitize_sheet(name: str) -> str:
        bad = [":", "\\", "/", "?", "*", "[", "]"]
        for ch in bad:
            name = name.replace(ch, "_")
        name = name.strip() or "UNKNOWN"
        return name[:31]

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        if include_sheet1:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

        if split_by_dept:
            if col_dept not in hit_df.columns:
                hit_df.to_excel(writer, index=False, sheet_name="HITS")
            else:
                for dept, grp in hit_df.groupby(hit_df[col_dept].fillna("UNKNOWN").astype(str)):
                    s = sanitize_sheet(dept)
                    base = s
                    j = 2
                    while s in writer.book.sheetnames:
                        suffix = f"_{j}"
                        s = (base[:31 - len(suffix)] + suffix)[:31]
                        j += 1
                    grp.to_excel(writer, index=False, sheet_name=s)
        else:
            hit_df.to_excel(writer, index=False, sheet_name="HITS")

    elapsed = time.perf_counter() - start
    print(f"출력 파일: {out_path.resolve()}")
    print(f"처리 시간: {elapsed:.2f}초")


def main():
    if len(os.sys.argv) < 2:
        print('Usage: python "context-based_detection.py" <input.xlsx>')
        raise SystemExit(1)

    input_path = Path(os.sys.argv[1])
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path.resolve()}")

    asyncio.run(run(input_path))


if __name__ == "__main__":
    main()
