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

from kb_detector import (
    DEFAULT_KEYWORD_FILE,
    detect_keywords,
    parse_keywords_from_text,
    read_keywords,
    write_outputs,
)

app = FastAPI(title="Keyword-based Post-detection PoC")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# naive in-memory job store (local demo only)
JOBS: dict[str, dict[str, Any]] = {}


def _default_output_basename(input_filename: str) -> str:
    stem = Path(input_filename).stem
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stem}_keyword_detection_{ts}"


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        keywords = read_keywords(DEFAULT_KEYWORD_FILE)
        kw_text = "\n".join(keywords)
    except Exception:
        kw_text = ""

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "kw_text": kw_text,
        },
    )


@app.post("/run", response_class=HTMLResponse)
async def run_detection(
    request: Request,
    input_xlsx: UploadFile = File(...),
    keywords_text: str = Form(""),
    output_basename: str = Form(""),
    preview_rows: int = Form(200),
    topn: int = Form(10),
):
    # read keywords
    try:
        keywords = parse_keywords_from_text(keywords_text)
    except Exception as e:
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "kw_text": keywords_text,
                "error": f"키워드 입력 오류: {e}",
            },
            status_code=400,
        )

    # read excel bytes
    raw = await input_xlsx.read()
    if not raw:
        return TEMPLATES.TemplateResponse(
            "index.html",
            {
                "request": request,
                "kw_text": keywords_text,
                "error": "업로드된 파일이 비어있습니다.",
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
                "kw_text": keywords_text,
                "error": f"엑셀 로드 실패: {e}",
            },
            status_code=400,
        )

    # output name
    output_basename = (output_basename or "").strip() or _default_output_basename(input_xlsx.filename or "input")

    # run detection
    result = detect_keywords(df, keywords)

    # create temp artifacts
    job_id = uuid.uuid4().hex
    job_dir = Path(tempfile.gettempdir()) / f"kb_post_detection_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)

    combined_path = job_dir / f"{output_basename}.xlsx"
    dept_dir = job_dir / f"{output_basename}_by_dept"
    dept_paths = write_outputs(result, combined_path, dept_files_dir=dept_dir)

    # zip dept files
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
        "preview": result.df_hits.head(int(preview_rows)).to_dict(orient="records"),
        "columns": list(result.df_hits.columns),
        "output_basename": output_basename,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    stats = result.stats
    dept_top = list(stats.get("dept_counts", {}).items())[: int(topn)]
    kw_top = list(stats.get("keyword_counts", {}).items())[: int(topn)]

    return TEMPLATES.TemplateResponse(
        "result.html",
        {
            "request": request,
            "job_id": job_id,
            "elapsed": result.elapsed_sec,
            "stats": stats,
            "dept_top": dept_top,
            "kw_top": kw_top,
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
