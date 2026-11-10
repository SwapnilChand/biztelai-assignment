"""FastAPI app: the API, the phone UI and the source PDFs, on one port."""

from __future__ import annotations

import json
import os
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import llm
from .copilot import Copilot

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = Path(os.getenv("DOCS_DIR", ROOT / "data" / "docs"))
STATIC = Path(__file__).parent / "static"
# Every question and what the copilot did with it, without any user name.
# "Not found" rows are the list of gaps in the documents to give the QMS owner.
LOG = Path(os.getenv("ASK_LOG", ROOT / "data" / "asked.jsonl"))

state: dict[str, Copilot] = {}
# fastembed and the small local model are not built for parallel calls;
# one question at a time is plenty for a handful of supervisors.
ask_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["copilot"] = Copilot(DOCS_DIR)
    yield


app = FastAPI(title="Shopfloor Copilot", lifespan=lifespan)


class AskIn(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.get("/api/health")
def health():
    cp = state.get("copilot")
    return {"ok": cp is not None, "model": llm.model_name()}


@app.get("/api/documents")
def documents():
    return [
        {"file": d.file, "doc_no": d.doc_no, "revision": d.revision, "title": d.title,
         "effective_date": d.effective_date, "current": d.is_current, "superseded_by": d.superseded_by}
        for d in state["copilot"].documents
    ]


@app.post("/api/ask")
def ask(body: AskIn):
    with ask_lock:
        try:
            a = state["copilot"].ask(body.question.strip())
        except Exception as e:  # LLM down, rate limited, bad JSON
            raise HTTPException(503, f"The copilot could not answer right now ({type(e).__name__}). Try again.")
    with LOG.open("a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "q": a.question, "found": a.found,
                            "sources": [f"{s.doc_no} Rev {s.revision} {s.section}" for s in a.sources],
                            "revision_note": bool(a.revision_note), "ms": a.latency_ms}) + "\n")
    return asdict(a)


@app.get("/files/{name}")
def pdf(name: str):
    path = (DOCS_DIR / name).resolve()
    if path.parent != DOCS_DIR.resolve() or path.suffix.lower() != ".pdf" or not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="application/pdf")


app.mount("/", StaticFiles(directory=STATIC, html=True), name="ui")
