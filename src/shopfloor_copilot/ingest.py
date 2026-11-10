"""Turn the plant PDFs into section-level chunks with document metadata.

The sample documents all follow the same controlled-document layout:
a header block (Document No., Revision, Effective Date), numbered top-level
sections ("4. Lockout Procedure") and a footer on every page. We use that
structure instead of fixed-size chunks so a retrieved chunk is always a whole
section (a full table, a full procedure) that a supervisor can read on its own.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

HEADING_RE = re.compile(r"^ (\d{1,2})\. (\S.{1,90})$")
FOOTER_RE = re.compile(r"^.*Uncontrolled copy when printed.*$", re.MULTILINE)
MAX_CHUNK_CHARS = 2200


@dataclass
class Document:
    file: str
    doc_no: str
    revision: str
    title: str
    effective_date: str
    pages: int
    superseded_by: str | None = None  # e.g. "Rev 04", set after all docs are loaded

    @property
    def label(self) -> str:
        return f"{self.doc_no} Rev {self.revision}"

    @property
    def is_current(self) -> bool:
        return self.superseded_by is None


@dataclass
class Chunk:
    id: str
    doc: Document
    section: str
    page: int
    text: str
    # text used for retrieval: section text plus document context, so a query
    # like "TX-200 coolant" still matches a section that never repeats "TX-200"
    search_text: str = field(repr=False, default="")


def _field(header: str, name: str) -> str:
    m = re.search(rf"{name}\s{{2,}}(.+?)(?:\s{{2,}}|$)", header, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _clean(text: str) -> str:
    text = text.replace("\x7f", "•")
    text = FOOTER_RE.sub("", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _split_long(body: str) -> list[str]:
    """Split an oversized section on blank lines, keeping parts under the limit."""
    if len(body) <= MAX_CHUNK_CHARS:
        return [body]
    parts, cur = [], ""
    for para in body.split("\n\n"):
        if cur and len(cur) + len(para) > MAX_CHUNK_CHARS:
            parts.append(cur)
            cur = ""
        cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        parts.append(cur)
    return parts


def load_pdf(path: Path) -> tuple[Document, list[Chunk]]:
    reader = PdfReader(path)
    page_texts = [_clean(p.extract_text(extraction_mode="layout")) for p in reader.pages]

    first = page_texts[0]
    lines = [l.strip() for l in first.splitlines() if l.strip()]
    title = lines[1] if len(lines) > 1 else path.stem
    doc = Document(
        file=path.name,
        doc_no=_field(first, "Document No.") or path.stem,
        revision=_field(first, "Revision") or "?",
        title=title,
        effective_date=_field(first, "Effective Date"),
        pages=len(page_texts),
    )

    # Walk every line with its page number, cutting at top-level headings.
    sections: list[tuple[str, int, list[str]]] = []
    cur_title, cur_page, cur_lines = "Header", 1, []
    pending_title = None
    for page_no, text in enumerate(page_texts, start=1):
        for line in text.splitlines():
            if pending_title is not None:
                # heading wrapped onto a second line, e.g. "(Machined, from" / "sub-contractor)"
                if line.strip():
                    cur_title = f"{pending_title} {line.strip()}"
                    pending_title = None
                continue
            m = HEADING_RE.match(line)
            if m and not m.group(2).rstrip().endswith("."):
                sections.append((cur_title, cur_page, cur_lines))
                cur_title, cur_page, cur_lines = f"{m.group(1)}. {m.group(2).strip()}", page_no, []
                if cur_title.count("(") > cur_title.count(")"):
                    pending_title = cur_title
                continue
            if line.strip() and not any(l.strip() for l in cur_lines):
                # a heading at the very bottom of a page: its text starts on the next one
                cur_page = page_no
            cur_lines.append(line)
    sections.append((cur_title, cur_page, cur_lines))

    chunks: list[Chunk] = []
    for title_, page, body_lines in sections:
        body = "\n".join(body_lines).strip()
        if not body:
            continue
        for i, part in enumerate(_split_long(body)):
            cid = f"{doc.doc_no}-r{doc.revision}-s{len(chunks)}"
            chunks.append(Chunk(id=cid, doc=doc, section=title_, page=page, text=part))
    return doc, chunks


def _rev_key(rev: str) -> tuple[int, str]:
    return (int(rev), rev) if rev.isdigit() else (-1, rev)


def _date_key(d: str) -> datetime:
    try:
        return datetime.strptime(d, "%d-%b-%Y")
    except ValueError:
        return datetime.min


def load_corpus(folder: Path) -> tuple[list[Document], list[Chunk]]:
    docs, chunks = [], []
    for path in sorted(folder.glob("*.pdf")):
        d, c = load_pdf(path)
        docs.append(d)
        chunks.extend(c)

    # Revision control: when the same document number exists in several
    # revisions, only the newest one is current. Older ones stay searchable
    # (so we can warn about changes) but are never used as the answer.
    by_no: dict[str, list[Document]] = {}
    for d in docs:
        by_no.setdefault(d.doc_no, []).append(d)
    for group in by_no.values():
        group.sort(key=lambda d: (_rev_key(d.revision), _date_key(d.effective_date)))
        newest = group[-1]
        for old in group[:-1]:
            old.superseded_by = f"Rev {newest.revision} ({newest.effective_date})"

    for c in chunks:
        c.search_text = f"{c.doc.title} | {c.doc.doc_no} | {c.section}\n{c.text}"
    return docs, chunks
