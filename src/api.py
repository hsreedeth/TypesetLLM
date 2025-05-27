from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
from tempfile import NamedTemporaryFile
import asyncio
import re

from src.cli import convert as convert_md_to_pdf
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# --- App Setup ------------------------------------------------
app = FastAPI(
    title="Markdown to PDF Conversion API",
    version="0.2.0",
)

# Rate limiter: 60 requests per hour per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["60/hour"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(status_code=429, detail="Rate limit exceeded"))

# Templates
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
DEFAULT_TEMPLATE = TEMPLATES_DIR / "vintage.tex"

# Dangerous LaTeX commands to strip
DANGEROUS_PATTERN = re.compile(r"\\(write18|input|include|openin|openout)")

# --- Models ---------------------------------------------------
class ConversionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    theme: str = Field("vintage")

# --- Helpers --------------------------------------------------
def sanitize(text: str) -> str:
    """
    Remove potentially dangerous LaTeX commands.
    """
    return DANGEROUS_PATTERN.sub("", text)

# --- Endpoint -------------------------------------------------
@app.post("/convert", response_class=FileResponse)
@limiter.limit("60/hour")
async def convert_endpoint(
    request: Request,
    payload: ConversionRequest,
    background_tasks: BackgroundTasks
):
    # Sanitize input
    cleaned_text = sanitize(payload.text)

    # Template selection (fallback to default)
    template_path = TEMPLATES_DIR / f"{payload.theme}.tex"
    if not template_path.exists():
        template_path = DEFAULT_TEMPLATE
        if not template_path.exists():
            raise HTTPException(status_code=500, detail="Default template not found")

    # Write Markdown to temp file
    with NamedTemporaryFile("w+", delete=False, suffix=".md", encoding="utf-8") as md_file:
        md_file.write(cleaned_text)
        md_path = Path(md_file.name)

    # Prepare PDF temp file
    temp_pdf = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = Path(temp_pdf.name)
    temp_pdf.close()

    # Perform conversion in thread executor
    try:
        await asyncio.to_thread(convert_md_to_pdf, md_path, pdf_path)
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            raise Exception("PDF generation failed")
    except Exception as e:
        md_path.unlink(missing_ok=True)
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    # Schedule cleanup
    background_tasks.add_task(md_path.unlink, True)
    background_tasks.add_task(pdf_path.unlink, True)

    # Return PDF file
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename="converted_document.pdf"
    )

# To run manually: uvicorn src.api:app --reload
