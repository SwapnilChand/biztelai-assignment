"""Small repeatable check: each question, N runs, against what the documents say.
uv run scripts/eval.py [runs]   (talks to the copilot directly, no server needed)"""
import sys
import time
from pathlib import Path
from shopfloor_copilot.copilot import Copilot

# question, must the copilot find it, words the answer must contain, must it warn about an old revision
CASES = [
    ("What is the recommended coolant concentration for the TX-200 CNC turning centre?", True, ["6", "8"], False),
    ("The machine is showing alarm AL-104. What does it mean and what should the operator do?", True, ["lube", "VG 68", "RESET"], False),
    ("Who is allowed to remove a lockout lock from a machine?", True, ["own", "Production Manager", "Safety Officer"], False),
    ("What is the outer diameter tolerance for the BH-220 bearing housing?", True, ["0.050"], False),
    ("How often should spindle runout be checked, and who does it?", True, ["onthly", "echnician"], False),
    ("How many samples do I take from a lot of 200 castings?", True, ["13"], True),
    ("Where do I keep rejected material?", True, ["Q1"], True),
    ("The supplier did not send the material test certificate. Can we still inspect the lot?", True, ["HOLD"], True),
    ("How do I replace a hydraulic hose on the TX-200?", True, ["SAF-SOP-003", "zero"], False),
    ("What is the maximum spindle speed of the TX-200?", False, [], False),
    ("What is the canteen timing for the night shift?", False, [], False),
    ("Who is the plant head?", True, ["Krishnan"], False),
]

runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
cp = Copilot(Path(__file__).resolve().parent.parent / "data" / "docs")
ok_total, n_total, lat, models = 0, 0, [], set()
for q, found, words, rev in CASES:
    ok = 0
    for _ in range(runs):
        a = cp.ask(q)
        time.sleep(4)  # stay under the free tier tokens-per-minute cap
        lat.append(a.latency_ms)
        models.add(a.model or "gate")
        good = (a.found == found
                and all(w.lower() in a.answer.lower() for w in words)
                and (bool(a.revision_note) == rev or not found))
        ok += good
        if not good:
            print(f"  MISS: {q}\n    found={a.found} note={a.revision_note!r}\n    {a.answer[:200]}")
    print(f"{ok}/{runs}  {q}")
    ok_total += ok
    n_total += runs
lat.sort()
print(f"\nmodels: {sorted(models)}")
print(f"{ok_total}/{n_total} correct, median {lat[len(lat) // 2] / 1000:.1f} s, worst {lat[-1] / 1000:.1f} s")
