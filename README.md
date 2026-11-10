# Shopfloor Copilot

Ask a question about the plant's SOPs from your phone and get a short answer with the exact document, revision, section and page it came from. If the documents don't cover it, it says so and guesses nothing.

Built for the BiztelAI take home: FastAPI, a plain HTML phone UI, and RAG over the four sample PDFs from "Kaveri Precision Components, Hosur Plant". Thinking, user journey, AI critique and reflection are in [THINKING.md](THINKING.md).

**Demo video (2 min 18 s):** https://drive.google.com/file/d/1dqw8MvYqbUZMGYsIJWmky4q6crKnIL9J/view?usp=sharing (me using it on the laptop with narration, then on my phone over Wi-Fi, then the revision warning and the safety banner).

> How this was made: built with a lot of AI help. Swapnil's AI assistant (running on Claude) wrote most of the code and the first drafts of these docs. Details in THINKING.md.

## What it does

- **Answers only from the documents.** Hybrid retrieval (BM25 for codes like `AL-104` and `BH-220`, plus local embeddings for paraphrases) picks the top 5 sections. The LLM must answer from them and cite which ones it used. An answer that cites no real section is thrown away and shown as "not in the documents".
- **Shows the source.** Document number, revision, section and page, the full section text one tap away, and a link that opens the PDF at that page.
- **Says when it doesn't know.** "Not in the documents" plus who to ask. Nothing is guessed.
- **The improvement: revision aware answers.** QC-SOP-014 exists as Rev 03 (2023) and Rev 04 (2026). Only the newest revision of a document is used to answer. Then a second, focused check compares the answer with the old revision, and if an old printout would tell someone to do something different, the app says so in a yellow box: *"Old Rev 03 said draw 5 samples from every lot. Follow the current revision."* Why this one is in THINKING.md.
- **Safety banner.** Answers that rest on the lockout/tagout SOP get a red "follow every step of the full SOP" banner (came out of the AI critique).
- **Question log.** Every question goes to `data/asked.jsonl` with no user name. The "not found" rows are a list of gaps in the documents for the QMS owner.

## Run it

Needs Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/SwapnilChand/biztelai-assignment
cd biztelai-assignment
uv sync

# Option A: Groq (free key from console.groq.com), fast
export GROQ_API_KEY=...
uv run shopfloor-copilot

# Option B: fully local with Ollama, nothing leaves the laptop (slow on CPU, see below)
ollama pull granite4.2:3b
LLM_PROVIDER=ollama uv run shopfloor-copilot
```

On start it prints the laptop's Wi-Fi address and a QR code:

```
Open on your phone (same Wi-Fi): http://192.168.0.223:8000
```

Scan it with the phone (same Wi-Fi network) and ask away. If the phone can't reach it, the usual cause is the laptop firewall blocking port 8000 (on Linux with ufw: `sudo ufw allow 8000/tcp`), or a guest Wi-Fi network that isolates devices from each other.

The first start downloads the embedding model (BAAI/bge-small-en-v1.5, about 70 MB) once. After that, retrieval runs offline.

Settings (environment variables): `LLM_PROVIDER` (`groq` or `ollama`), `GROQ_MODEL` (default `openai/gpt-oss-120b`), `GROQ_FALLBACK_MODEL` (default `openai/gpt-oss-20b`, used when the free daily cap of the main model runs out), `OLLAMA_MODEL` (default `granite4.2:3b`), `PORT` (8000), `DOCS_DIR` (point it at another folder of PDFs).

### Docker (bonus, not tested)

There is a `Dockerfile`. Docker wasn't running on the laptop this was built on, so I could not build and test it. Treat it as a starting point:

```bash
docker build -t shopfloor-copilot .
docker run -p 8000:8000 -e GROQ_API_KEY -e PUBLIC_URL=http://<laptop-ip>:8000 shopfloor-copilot
```

### Command line and checks

```bash
uv run scripts/try.py "what does AL-210 mean?"     # ask without the UI
uv run scripts/eval.py 3                            # 12 questions x 3 runs, checked against the PDFs
uv run scripts/answers.py > docs/answers.md         # regenerate the answers below (server must be running)
```

## How it works

```
PDFs ──> ingest.py: split by numbered section (a whole table or procedure per chunk),
         read Document No. / Revision / Effective Date from the header,
         mark older revisions of the same Document No. as superseded
    ──> retrieval.py: BM25 + bge-small embeddings (fastembed, ONNX on CPU), fused by rank
    ──> copilot.py: top 5 CURRENT sections -> LLM -> JSON {found, answer, sources}
         reject answers with no valid source
         if an older revision of a cited document exists -> second LLM call:
         "would someone following the old printout do something different?"
    ──> server.py: /api/ask, /api/documents, /files/<pdf>, and the UI in static/index.html
```

Why sections and not fixed size chunks: these documents are controlled SOPs with numbered sections. A section is the unit a supervisor reads (the whole alarm table, the whole lock removal procedure), so retrieval never returns half a table. Sections longer than 2,200 characters are split on blank lines.

## Answers

Sample questions and our own 5 (one the documents can't answer). Generated by `scripts/answers.py` against the running app on Nov 10 2026. Most ran on the fallback model `gpt-oss-20b` because the free daily cap for `gpt-oss-120b` had run out after a day of testing, which is a real world finding in itself (see THINKING.md).

### Sample questions

**Q: What is the recommended coolant concentration for the TX-200 CNC turning centre?**
> Found: Recommended coolant concentration: 6 % to 8 %.
- Source: MNT-MAN-CNC-02 Rev 02, section "3. Normal Operating Parameters", page 1

**Q: The machine is showing alarm AL-104. What does it mean and what should the operator do?**
> Found: AL-104 means the way lube oil level is low. The operator should top up with ISO VG 68 oil to the MAX mark, then press RESET. The machine can continue after reset.
- Source: MNT-MAN-CNC-02 Rev 02, section "6. Common Alarms", page 1 (the table continues onto page 2)

**Q: Who is allowed to remove a lockout lock from a machine?**
> Found: Only an authorised person may remove a lock, and only their own lock. If the lock owner is absent, the Production Manager and Safety Officer must both authorise the removal.
> Safety procedure banner shown.
- Source: SAF-SOP-003 Rev 05, section "5. Removing Locks", page 1
- Source: SAF-SOP-003 Rev 05, section "6. Removal of a Lock When the Owner Is Absent", page 1

**Q: What is the outer diameter tolerance for the BH-220 bearing housing?**
> Found: The outer diameter tolerance is +/- 0.050 mm.
- Source: QC-SOP-014 Rev 04, section "6. Inspection Dimensions - BH-220 Bearing Housing", page 2

**Q: How often should spindle runout be checked, and who does it?**
> Found: Monthly, by a Maintenance technician.
- Source: MNT-MAN-CNC-02 Rev 02, section "4. Preventive Maintenance Schedule", page 1

### Our own 5 questions

**1. How many samples do I take from a lot of 200 castings?** (tests the revision warning)
> Found: Take 13 samples.
> Changed in the latest revision: Old Rev 03 said draw 5 samples at random from every lot, irrespective of lot size.
- Source: QC-SOP-014 Rev 04, section "4. Sampling Plan", page 1

**2. Where do I keep rejected material?** (the location moved between revisions)
> Found: Rejected material is tagged RED and moved to Quarantine Cage Q1 in Stores Bay 3. The cage is locked; the key is held by the Shift QC Supervisor.
> Changed in the latest revision: Old Rev 03 said rejected material is tagged RED and kept in the Red Bin area near Gate 2 until it is returned to the supplier.
- Source: QC-SOP-014 Rev 04, section "5. Procedure", page 2

**3. The supplier did not send the material test certificate. Can we still inspect the lot?** (a real "what now" question, not a lookup)
> Found: No, the lot must be put on HOLD and cannot be inspected or accepted until the Material Test Certificate (MTC) is received.
> Changed in the latest revision: Old Rev 03 said the lot could be inspected and accepted based on sampling even if the supplier test certificate was not available.
- Source: QC-SOP-014 Rev 04, section "5. Procedure", page 2

**4. How do I replace a hydraulic hose on the TX-200?** (procedure that depends on a second document)
> Found:
> 1. Isolate the machine per SAF-SOP-003 and release stored hydraulic pressure.
> 2. Confirm the panel pressure gauge reads zero before loosening any fitting.
> 3. Place a drip tray under the hose and loosen the fittings slowly.
> 4. Fit a new hose of the same rating and tighten the fittings.
> 5. Remove locks per SAF-SOP-003, start the hydraulic unit and confirm pressure returns to 3.5-4.0 MPa with no leaks.
>
> Safety procedure banner shown.
- Source: MNT-MAN-CNC-02 Rev 02, section "7. Replacing a Hydraulic Hose", page 2
- Source: MNT-MAN-CNC-02 Rev 02, section "2. Safety First", page 1

**5. What is the maximum spindle speed of the TX-200?** (not in the documents, but sounds like it should be, which is exactly when a model is tempted to make up a number)
> Not in the documents: Maximum spindle speed not specified in the provided excerpts.
> Nothing was guessed. Ask your shift supervisor or the document owner, and check the QMS.

The raw output, with timings and model per answer, is in [docs/answers.md](docs/answers.md).

### Repeat runs

`scripts/eval.py` asks 12 questions (the 5 samples, the 5 above, "canteen timing for the night shift" and "who is the plant head?") several times and checks each answer against the PDFs: found or not, the key facts present, and the revision warning present when it should be. Latest run: 24/24 ([docs/eval-latest.txt](docs/eval-latest.txt)). Earlier runs during the build were not perfect, and those misses drove the fixes listed in THINKING.md.

## Local model (Ollama)

Supported and tested, but slow on this laptop (Intel i5 with integrated graphics, no usable GPU, 15 GB RAM): granite4.2:3b took about 90 to 100 seconds per answer. It got the facts right on the two questions tried, but on one of them it did not cite its sources, so the app (correctly) refused to trust it. On a plant server with a small GPU this would be the right default. On this laptop Groq is the default for speed.

## Project layout

```
src/shopfloor_copilot/
  ingest.py      PDF -> sections with document metadata and revision status
  retrieval.py   BM25 + embeddings, rank fusion
  copilot.py     prompts, the answer pipeline, the revision check
  llm.py         Groq / Ollama backends, rate limit handling, fallback model
  server.py      FastAPI app
  static/index.html   the phone UI (no framework, no build step)
scripts/         try.py, eval.py, answers.py
demo/            the scripts used to record the demo video
docs/            first journey draft, raw AI critique, answers, eval output
data/docs/       the four sample PDFs
```
