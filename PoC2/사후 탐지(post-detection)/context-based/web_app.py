from __future__ import annotations

import io
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cb_detector import (
    ContextDetectionSettings,
    default_output_basename,
    detect_context_async,
    load_defaults_from_env,
    write_outputs,
)

app = FastAPI(title="Context-based Post-detection PoC")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# local demo in-memory job store
JOBS: dict[str, dict[str, Any]] = {}


def _merge_settings(base: ContextDetectionSettings, overrides: dict) -> ContextDetectionSettings:
    for k, v in overrides.items():
        if v is None:
            continue
        if hasattr(base, k):
            setattr(base, k, v)
    return base


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    defaults = load_defaults_from_env(BASE_DIR)

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "defaults": defaults,
            "prompt_text": defaults.prompt_template or "",
            "keywords_text": "\n".join(defaults.keywords or []),
        },
    )


@app.post("/run", response_class=HTMLResponse)
async def run_detection(
    request: Request,
    input_xlsx: UploadFile = File(...),
    output_basename: str = Form(""),
    # API key can be provided or read from .env
    openai_api_key: str = Form(""),
    openai_model: str = Form("gpt-5.2"),
    candidate_ratio: float = Form(0.05),
    candidate_min_rows: int = Form(200),
    candidate_max_rows: int = Form(10000),
    hit_risk_level_threshold: int = Form(3),
    concurrency: int = Form(5),
    preview_rows: int = Form(200),
    topn: int = Form(10),
    keywords_text: str = Form(""),
    prompt_text: str = Form(""),
):
    raw = await input_xlsx.read()
    if not raw:
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "defaults": load_defaults_from_env(BASE_DIR),
                "error": "업로드된 파일이 비어있습니다.",
                "prompt_text": prompt_text,
                "keywords_text": keywords_text,
            },
            status_code=400,
        )

    try:
        df = pd.read_excel(io.BytesIO(raw), sheet_name=0)
    except Exception as e:
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "defaults": load_defaults_from_env(BASE_DIR),
                "error": f"엑셀 로드 실패: {e}",
                "prompt_text": prompt_text,
                "keywords_text": keywords_text,
            },
            status_code=400,
        )

    defaults = load_defaults_from_env(BASE_DIR)

    # output name
    output_basename = (output_basename or "").strip() or default_output_basename(input_xlsx.filename or "input")

    # settings
    keywords = [ln.strip() for ln in (keywords_text or "").splitlines() if ln.strip()]
    if not keywords:
        keywords = defaults.keywords or []

    prompt_template = (prompt_text or "").strip() or (defaults.prompt_template or "")

    s = _merge_settings(
        defaults,
        {
            "openai_api_key": (openai_api_key or "").strip() or defaults.openai_api_key,
            "openai_model": openai_model,
            "candidate_ratio": float(candidate_ratio),
            "candidate_min_rows": int(candidate_min_rows),
            "candidate_max_rows": int(candidate_max_rows),
            "hit_risk_level_threshold": int(hit_risk_level_threshold),
            "openai_concurrency": int(concurrency),
            "keywords": keywords,
            "prompt_template": prompt_template,
        },
    )

    try:
        result = await detect_context_async(df, s)
    except Exception as e:
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "defaults": defaults,
                "error": f"실행 실패: {e}",
                "prompt_text": prompt_text,
                "keywords_text": keywords_text,
            },
            status_code=400,
        )

    job_id = uuid.uuid4().hex
    job_dir = Path(tempfile.gettempdir()) / f"cb_post_detection_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)

    combined_path = job_dir / f"{output_basename}.xlsx"
    dept_dir = job_dir / f"{output_basename}_by_dept"

    dept_paths = write_outputs(
        result,
        combined_path,
        split_by_dept=True,
        include_sheet1=True,
        dept_files_dir=dept_dir,
        dept_col=s.col_dept,
    )

    dept_zip = job_dir / f"{output_basename}_dept_files.zip"
    if dept_paths:
        import zipfile

        with zipfile.ZipFile(dept_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in dept_paths:
                zf.write(p, arcname=p.name)

    JOBS[job_id] = {
        "job_dir": str(job_dir),
        "combined": str(combined_path),
        "dept_zip": str(dept_zip),
        "elapsed": result.elapsed_sec,
        "stats": result.stats,
        "columns": list(result.df_hits.columns),
        "preview": result.df_hits.head(int(preview_rows)).to_dict(orient="records"),
        "output_basename": output_basename,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    stats = result.stats
    dept_top = list(stats.get("dept_counts", {}).items())[: int(topn)]
    intent_top = list(stats.get("intent_counts", {}).items())[: int(topn)]
    artifact_top = list(stats.get("artifact_counts", {}).items())[: int(topn)]

    return TEMPLATES.TemplateResponse(
        "result.html",
        {
            "request": request,
            "job_id": job_id,
            "elapsed": result.elapsed_sec,
            "stats": stats,
            "dept_top": dept_top,
            "intent_top": intent_top,
            "artifact_top": artifact_top,
            "preview_rows": JOBS[job_id]["preview"],
            "columns": JOBS[job_id]["columns"],
            "output_basename": output_basename,
        },
    )


@app.get("/download/combined/{job_id}")
def download_combined(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return RedirectResponse(url="/")
    path = Path(job["combined"])
    return FileResponse(path, filename=path.name)


@app.get("/download/deptzip/{job_id}")
def download_dept_zip(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return RedirectResponse(url="/")
    path = Path(job["dept_zip"])
    if not path.exists():
        return RedirectResponse(url=f"/download/combined/{job_id}")
    return FileResponse(path, filename=path.name)
