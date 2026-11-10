"""Run the sample questions and our own questions against the running app and
write the answers as markdown: uv run scripts/answers.py > docs/answers.md"""
import sys
import httpx

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
SAMPLE = [
    "What is the recommended coolant concentration for the TX-200 CNC turning centre?",
    "The machine is showing alarm AL-104. What does it mean and what should the operator do?",
    "Who is allowed to remove a lockout lock from a machine?",
    "What is the outer diameter tolerance for the BH-220 bearing housing?",
    "How often should spindle runout be checked, and who does it?",
]
OWN = [
    "How many samples do I take from a lot of 200 castings?",
    "Where do I keep rejected material?",
    "The supplier did not send the material test certificate. Can we still inspect the lot?",
    "How do I replace a hydraulic hose on the TX-200?",
    "What is the maximum spindle speed of the TX-200?",
]


def block(q: str) -> str:
    a = httpx.post(f"{URL}/api/ask", json={"question": q}, timeout=300).json()
    out = [f"**Q: {q}**", "", f"> {'Found' if a['found'] else 'Not in the documents'}: " + a["answer"].replace("\n", "\n> ")]
    if a["revision_note"]:
        out += [">", f"> Changed in the latest revision: {a['revision_note']}"]
    if a.get("safety"):
        out += [">", "> Safety procedure banner shown."]
    for s in a["sources"]:
        out.append(f"- Source: {s['doc_no']} Rev {s['revision']}, section \"{s['section']}\", page {s['page']}")
    out.append(f"- {a['model'] or 'retrieval gate, no LLM call'}, {a['latency_ms'] / 1000:.1f} s")
    return "\n".join(out) + "\n"


print("## Sample questions\n")
for q in SAMPLE:
    print(block(q))
print("## Our own 5 questions\n")
for q in OWN:
    print(block(q))
