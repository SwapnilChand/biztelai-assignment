"""The question -> answer pipeline: retrieve, gate, ask the LLM, verify sources."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from . import llm
from .ingest import Chunk, Document, load_corpus
from .retrieval import Hit, Retriever

TOP_K = 5
# Below this dense similarity nothing in the documents is even close to the
# question, so we answer "not in the documents" without calling the LLM.
# Started at 0.55; that wrongly refused "Who is the plant head?" (0.47, the
# answer sits in a document header). The LLM refuses reliably on its own
# (canteen timing, spindle speed), so the gate now only drops clearly
# off-topic questions ("what's the weather", "tell me a joke").
MIN_COSINE = 0.40
# How many sections of an older revision to compare the answer against.
OLD_TOP_K = 2

NOT_FOUND = (
    "I couldn't find this in the plant documents I have. "
    "Please check with your shift supervisor or the QMS before acting on it."
)

SYSTEM_PROMPT = """You are a copilot for supervisors on a manufacturing shop floor.
You answer ONLY from the CURRENT document excerpts given to you. Supervisors act on
your answers, so a wrong answer is worse than no answer.

Rules:
- Use only facts written in the CURRENT excerpts. Never use general knowledge, never
  guess, never fill gaps. If the excerpts do not contain the answer, set found=false
  and answer with one short sentence saying what is missing.
- If only part of the question is answered by the excerpts, answer that part and say
  clearly which part is not covered.
- Be short and practical: the reader is on a phone, on the floor. Lead with the
  direct answer (numbers with units, who, when). Use short numbered steps for
  procedures. Keep exact values, codes, form numbers and names as written.
- If the excerpt has a safety step that applies (for example lockout/tagout before
  maintenance), include it.
- If an excerpt covers a special case of the same situation (the person is absent,
  a document is missing, the alarm repeats), always add it as a second short line
  starting "If ...". The supervisor is usually asking because the normal case
  does not apply.
- sources: the ids (like "S2") of the excerpts you actually used. Do not write
  these ids inside the answer text; the app shows the sources itself.

Reply as JSON: {"found": bool, "answer": str, "sources": [str], "revision_note": ""}"""

REVISION_PROMPT = """People on a shop floor often still follow an old printout of a procedure.
You get a question, the answer from the CURRENT revision of a document, and excerpts from an
OLDER revision of the same document. Decide what someone reading only the OLD excerpts would do
for this question. If the old excerpts give a different instruction than the current answer
(a different number, rule, form, location, person or time limit), set changed=true and write ONE
sentence starting "Old Rev XX said ..." stating the old instruction. If the old excerpts say the
same thing or do not cover the question, set changed=false and note="".

Reply as JSON: {"changed": bool, "note": str}"""


@dataclass
class Source:
    id: str
    doc_no: str
    revision: str
    title: str
    section: str
    page: int
    file: str
    text: str
    current: bool
    superseded_by: str | None = None


@dataclass
class Answer:
    question: str
    found: bool
    answer: str
    sources: list[Source] = field(default_factory=list)
    revision_note: str = ""
    superseded_sources: list[Source] = field(default_factory=list)
    model: str = ""
    latency_ms: int = 0
    gated: bool = False  # true when the retrieval gate answered without the LLM
    safety: bool = False  # the answer rests on a safety procedure (LOTO etc.)


def _source(sid: str, c: Chunk) -> Source:
    d = c.doc
    return Source(sid, d.doc_no, d.revision, d.title, c.section, c.page, d.file, c.text,
                  d.is_current, d.superseded_by)


class Copilot:
    def __init__(self, docs_dir: Path):
        self.docs, self.chunks = load_corpus(docs_dir)
        self.retriever = Retriever(self.chunks)

    @property
    def documents(self) -> list[Document]:
        return self.docs

    def _revision_note(self, question: str, answer: str, cited: list[Source],
                       old: list[Source], provider: str | None) -> str:
        """The improvement: a focused second check of the answer against the old revision.

        Asking the main call to also fill a revision note was unreliable (the same
        question got the note on one run and not the next), so this is its own call
        with one job. It only runs when an older revision of a cited document matched.
        """
        if not old:
            return ""
        user = (f"Question: {question}\n\nCurrent answer ({cited[0].doc_no} Rev {cited[0].revision}): {answer}\n\n"
                + "\n\n".join(f"OLD excerpt ({o.doc_no} Rev {o.revision}, section {o.section}):\n{o.text}" for o in old))
        out = llm.complete_json(REVISION_PROMPT, user, provider, schema=llm.REVISION_SCHEMA)
        return (out.get("note") or "").strip() if out.get("changed") else ""

    def ask(self, question: str, provider: str | None = None) -> Answer:
        t0 = time.perf_counter()
        hits = self.retriever.search(question)
        current = [h for h in hits if h.chunk.doc.is_current][:TOP_K]
        best_cos = max(h.cosine for h in hits)

        def done(a: Answer) -> Answer:
            a.latency_ms = int((time.perf_counter() - t0) * 1000)
            return a

        if best_cos < MIN_COSINE:
            return done(Answer(question, False, NOT_FOUND, gated=True))

        sources = {f"S{i + 1}": _source(f"S{i + 1}", h.chunk) for i, h in enumerate(current)}

        parts = []
        for s in sources.values():
            parts.append(f"[{s.id}] CURRENT | {s.doc_no} Rev {s.revision} | {s.title} | "
                         f"section {s.section} | page {s.page}\n{s.text}")
        user = "Document excerpts:\n\n" + "\n\n---\n\n".join(parts) + f"\n\nQuestion: {question}"

        out = llm.complete_json(SYSTEM_PROMPT, user, provider)
        # models like to print non-breaking hyphens (SAF‑SOP‑003); keep codes searchable
        out["answer"] = (out.get("answer") or "").replace("\u2011", "-").replace("\u2010", "-").replace("\u00a0", " ").replace("\u202f", " ")
        found = bool(out.get("found"))
        cited = [sources[i] for i in out.get("sources", []) if i in sources]
        if found and not cited:
            # an answer with no valid current source is not trusted
            found = False
        if not found:
            return done(Answer(question, False, out.get("answer") or NOT_FOUND,
                               model=out.get("_model", "")))
        # Older revisions of the documents the answer came from, best matching first.
        cited_docs = {c.doc_no for c in cited}
        old = [_source(f"OLD{i + 1}", h.chunk) for i, h in enumerate(
            [h for h in hits if not h.chunk.doc.is_current and h.chunk.doc.doc_no in cited_docs][:OLD_TOP_K])]
        note = self._revision_note(question, out.get("answer", ""), cited, old, provider)
        safety = any(s.doc_no.startswith("SAF-") or "SAF-SOP" in s.text for s in cited)
        return done(Answer(
            question, True, out.get("answer", "").strip(), cited,
            revision_note=note,
            superseded_sources=old if note else [],
            model=out.get("_model", ""),
            safety=safety,
        ))
