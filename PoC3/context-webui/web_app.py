from __future__ import annotations

import argparse
import io
import tempfile
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from detector_core import Columns, Settings, candidate_indices, call_one, pick_random_row, read_keywords, read_prompt
from llm_client import client_from_env

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="PoC3 Context WebUI")

# static is optional; mount only if exists
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# in-memory stores (demo only)
STATE: Dict[str, Any] = {
    "df": None,
    "sample_path": None,
    "keywords_text": "",
    "prompt_text": "",
}
JOBS: Dict[str, Dict[str, Any]] = {}


def load_df(sample_xlsx: Path, sheet: Any = 0) -> pd.DataFrame:
    if not sample_xlsx.exists():
        raise FileNotFoundError(f"Sample xlsx not found: {sample_xlsx}")
    return pd.read_excel(sample_xlsx, sheet_name=sheet, engine="openpyxl")


def _cols_from_env() -> Columns:
    import os

    return Columns(
        title=os.getenv("COL_TITLE", "제목"),
        body=os.getenv("COL_BODY", "본문내용"),
        a1=os.getenv("COL_ATTACH_SAMSUNG", "일반자료명: 삼성등록"),
        a2=os.getenv("COL_ATTACH_VENDOR", "일반자료명: 협력사등록"),
        dept=os.getenv("COL_DEPT", "발신자부서명"),
    )


def _settings_from_env() -> Settings:
    import os

    return Settings(
        candidate_ratio=float(os.getenv("CANDIDATE_RATIO", "0.05")),
        candidate_min_rows=int(os.getenv("CANDIDATE_MIN_ROWS", "1")),
        candidate_max_rows=int(os.getenv("CANDIDATE_MAX_ROWS", "10")),
        hit_level_threshold=int(os.getenv("HIT_RISK_LEVEL_THRESHOLD", "4")),
        cache_enabled=str(os.getenv("CACHE_ENABLED", "true")).lower() in ("1", "true", "yes", "y", "on"),
        cache_dir=Path(os.getenv("CACHE_DIR", "./cache_context_detection")),
        cache_key_col=os.getenv("CACHE_KEY_COL", "전송코드"),
    )


def _load_defaults() -> None:
    import os

    kpath = Path(os.getenv("KEYWORD_FILE_PATH", "./detection_keywords.md"))
    ppath = Path(os.getenv("PROMPT_FILE_PATH", "./prompt_context_detection.md"))
    STATE["keywords_text"] = "\n".join(read_keywords(kpath)) if kpath.exists() else ""
    STATE["prompt_text"] = read_prompt(ppath) if ppath.exists() else ""


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    df: pd.DataFrame | None = STATE.get("df")
    cols = _cols_from_env()
    s = _settings_from_env()

    row_idx = None
    row = None
    if df is not None and len(df) > 0:
        row_idx, row = pick_random_row(df)

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "sample_path": str(STATE.get("sample_path") or ""),
            "df_rows": int(len(df)) if df is not None else 0,
            "keywords_text": STATE.get("keywords_text", ""),
            "prompt_text": STATE.get("prompt_text", ""),
            "row_idx": row_idx,
            "row": row,
            "cols": asdict(cols),
            "settings": asdict(s),
            "provider": (request.query_params.get("provider") or "").strip(),
        },
    )


@app.post("/random", response_class=HTMLResponse)
def random_pick(request: Request):
    # just redirect to GET / (fresh random)
    return RedirectResponse(url="/", status_code=303)


@app.post("/run_random", response_class=HTMLResponse)
def run_random(
    request: Request,
    # editable fields
    title: str = Form(""),
    body: str = Form(""),
    attachments: str = Form(""),
    dept: str = Form(""),
    keywords_text: str = Form(""),
    prompt_text: str = Form(""),
):
    cols = _cols_from_env()
    s = _settings_from_env()
    llm = client_from_env()

    keywords = [ln.strip() for ln in (keywords_text or "").splitlines() if ln.strip()]
    prompt_template = (prompt_text or "").strip()

    # Build a fake row series
    row = pd.Series({cols.title: title, cols.body: body, cols.a1: attachments, cols.a2: "", cols.dept: dept})

    try:
        res = call_one(
            llm=llm,
            prompt_template=prompt_template,
            keywords=keywords,
            row_idx=0,
            row=row,
            cols=cols,
            s=s,
        )
        return TEMPLATES.TemplateResponse(
            "random_result.html",
            {
                "request": request,
                "result": res,
            },
        )
    except Exception as e:
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"랜덤 검사 실패: {e}",
                "sample_path": str(STATE.get("sample_path") or ""),
                "df_rows": int(len(STATE.get("df"))) if STATE.get("df") is not None else 0,
                "keywords_text": keywords_text,
                "prompt_text": prompt_text,
                "row_idx": None,
                "row": None,
                "cols": asdict(cols),
                "settings": asdict(s),
            },
            status_code=400,
        )


@app.post("/run_all", response_class=HTMLResponse)
def run_all(
    request: Request,
    keywords_text: str = Form(""),
    prompt_text: str = Form(""),
    # candidate/hit settings override
    candidate_ratio: float = Form(0.05),
    candidate_min_rows: int = Form(1),
    candidate_max_rows: int = Form(10),
    hit_level_threshold: int = Form(4),
):
    df: pd.DataFrame | None = STATE.get("df")
    if df is None:
        return RedirectResponse(url="/", status_code=303)

    cols = _cols_from_env()
    ensure_df = df.copy()

    s = _settings_from_env()
    s.candidate_ratio = float(candidate_ratio)
    s.candidate_min_rows = int(candidate_min_rows)
    s.candidate_max_rows = int(candidate_max_rows)
    s.hit_level_threshold = int(hit_level_threshold)

    llm = client_from_env()
    keywords = [ln.strip() for ln in (keywords_text or "").splitlines() if ln.strip()]
    prompt_template = (prompt_text or "").strip()

    # mark outputs
    out_cols = {
        "context_risk_score": pd.Series([pd.NA] * len(ensure_df), dtype="Int64"),
        "context_risk_level": pd.Series([pd.NA] * len(ensure_df), dtype="Int64"),
        "context_intent": pd.Series([None] * len(ensure_df), dtype="object"),
        "context_artifact_type": pd.Series([None] * len(ensure_df), dtype="object"),
        "context_evidence": pd.Series([None] * len(ensure_df), dtype="object"),
        "context_reason": pd.Series([None] * len(ensure_df), dtype="object"),
        "llm_model": pd.Series([None] * len(ensure_df), dtype="object"),
    }
    for k, v in out_cols.items():
        ensure_df[k] = v

    start = datetime.now()
    cand = candidate_indices(ensure_df, cols, s, keywords)

    processed = 0
    for idx in cand:
        row = ensure_df.loc[idx]
        res = call_one(llm=llm, prompt_template=prompt_template, keywords=keywords, row_idx=idx, row=row, cols=cols, s=s)
        ensure_df.at[idx, "context_risk_score"] = int(res.get("risk_score", 0)) if str(res.get("risk_score", "")).isdigit() else pd.NA
        ensure_df.at[idx, "context_risk_level"] = int(res.get("risk_level", 0)) if str(res.get("risk_level", "")).isdigit() else pd.NA
        ensure_df.at[idx, "context_intent"] = str(res.get("intent", "") or "")
        ensure_df.at[idx, "context_artifact_type"] = str(res.get("artifact_type", "") or "")
        ev = res.get("evidence", [])
        if isinstance(ev, list):
            ensure_df.at[idx, "context_evidence"] = " | ".join([str(x) for x in ev if x])
        else:
            ensure_df.at[idx, "context_evidence"] = str(ev or "")
        ensure_df.at[idx, "context_reason"] = str(res.get("reason", "") or "")
        ensure_df.at[idx, "llm_model"] = str(res.get("llm_model", "") or "")
        processed += 1

    elapsed = (datetime.now() - start).total_seconds()

    # write outputs to temp
    job_id = uuid.uuid4().hex
    job_dir = Path(tempfile.gettempdir()) / f"poc3_ctx_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)

    out_xlsx = job_dir / f"context_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    # dept split
    hit_df = ensure_df[ensure_df["context_risk_level"].fillna(0).astype(int) >= int(s.hit_level_threshold)].copy()

    def _sanitize_sheet(name: str) -> str:
        bad = [":", "\\", "/", "?", "*", "[", "]"]
        for ch in bad:
            name = name.replace(ch, "_")
        name = name.strip() or "UNKNOWN"
        return name[:31]

    dept_paths = []
    dept_dir = job_dir / "by_dept"

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        ensure_df.to_excel(writer, index=False, sheet_name="Sheet1")
        if cols.dept in hit_df.columns and len(hit_df) > 0:
            for dept, grp in hit_df.groupby(hit_df[cols.dept].fillna("UNKNOWN").astype(str)):
                sheet = _sanitize_sheet(dept)
                grp.to_excel(writer, index=False, sheet_name=sheet)
                dept_dir.mkdir(parents=True, exist_ok=True)
                p = dept_dir / f"{sheet}.xlsx"
                with pd.ExcelWriter(p, engine="openpyxl") as w2:
                    grp.to_excel(w2, index=False, sheet_name="HITS")
                dept_paths.append(p)
        else:
            hit_df.to_excel(writer, index=False, sheet_name="HITS")

    dept_zip = job_dir / "dept_files.zip"
    if dept_paths:
        import zipfile

        with zipfile.ZipFile(dept_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in dept_paths:
                zf.write(p, arcname=p.name)

    JOBS[job_id] = {
        "xlsx": str(out_xlsx),
        "zip": str(dept_zip),
        "elapsed": elapsed,
        "cand": len(cand),
        "processed": processed,
        "hit": int(len(hit_df)),
    }

    return TEMPLATES.TemplateResponse(
        "result.html",
        {
            "request": request,
            "job_id": job_id,
            "elapsed": elapsed,
            "cand": len(cand),
            "processed": processed,
            "hit": int(len(hit_df)),
        },
    )


@app.get("/download/xlsx/{job_id}")
def download_xlsx(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return RedirectResponse(url="/", status_code=303)
    p = Path(job["xlsx"])
    return FileResponse(p, filename=p.name)


@app.get("/download/deptzip/{job_id}")
def download_zip(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return RedirectResponse(url="/", status_code=303)
    p = Path(job["zip"])
    if not p.exists():
        return RedirectResponse(url=f"/download/xlsx/{job_id}", status_code=303)
    return FileResponse(p, filename=p.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-xlsx", required=False, default=None)
    parser.add_argument("--sheet", required=False, default=None)
    args = parser.parse_args()

    load_dotenv()

    import os

    sample = args.sample_xlsx or os.getenv("SAMPLE_XLSX_PATH", "")
    sheet = args.sheet if args.sheet is not None else os.getenv("SAMPLE_SHEET", "0")

    if not sample:
        raise SystemExit("Missing sample xlsx. Set SAMPLE_XLSX_PATH in .env or pass --sample-xlsx")

    sample_path = Path(sample)
    df = load_df(sample_path, sheet=0 if str(sheet).isdigit() else sheet)

    STATE["df"] = df
    STATE["sample_path"] = str(sample_path)
    _load_defaults()


# init on import if env has path (optional)
try:
    load_dotenv()
    import os

    sp = os.getenv("SAMPLE_XLSX_PATH", "").strip()
    if sp:
        main()
except Exception:
    pass
