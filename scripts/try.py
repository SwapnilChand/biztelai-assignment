"""Ask questions from the command line: uv run scripts/try.py "question" ..."""
import json, sys
from dataclasses import asdict
from pathlib import Path
from shopfloor_copilot.copilot import Copilot

cp = Copilot(Path(__file__).resolve().parent.parent / "data" / "docs")
for q in sys.argv[1:]:
    a = cp.ask(q)
    print(f"\nQ: {q}\nfound={a.found} gated={a.gated} {a.model} {a.latency_ms}ms\n{a.answer}")
    for s in a.sources: print(f"  - {s.doc_no} Rev {s.revision} / {s.section} / p{s.page}")
    if a.revision_note: print("  NOTE:", a.revision_note)
