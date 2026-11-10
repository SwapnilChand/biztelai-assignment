# THINKING

**How this was made, honestly.** I (Swapnil) built this with a lot of help from my AI assistant, which runs on Claude. The assistant wrote most of the code and the first drafts of everything in this file. The AI challenge in section 3 is a separate Claude session asked to play a skeptical PM, run against that first draft. So the "write the first draft yourself, before using AI" step was not done the way you asked, and I would rather say so than pretend. The first draft is saved as it was in [docs/journey-v1.md](docs/journey-v1.md), and the raw critique is in [docs/ai-critique-raw.md](docs/ai-critique-raw.md).

## Assumptions

- The four PDFs stand in for a plant with hundreds of them. They are clean, text based PDFs with a consistent controlled document layout (Document No., Revision, Effective Date, numbered sections). Real plants also have scanned pages and photos of whiteboards. I did not handle those.
- "Current revision" means the highest revision number for a Document No. There is no QMS to ask, so the folder is the source of truth.
- Supervisors use Android phones on plant Wi-Fi, in English. SOPs are in English.
- Questions are read only. The copilot does not log actions, raise tickets or change anything.
- A hosted LLM (Groq) is fine for this exercise because the documents are fictional. For a real plant I assume they would want it on premises (Ollama path is there).

## 1. Understand the user

**Who.** A shift supervisor on the shaft machining line at a mid sized auto component plant in Hosur. Came up from operator or diploma technician, 8 to 15 years on the floor. Runs one shift: 15 to 25 operators, six TX-200 CNC turning centres, incoming material checks, and whoever from maintenance is around. Knows the machines well. Did not write the SOPs and has not read most of them end to end.

**What they're trying to do.** Keep the line running and hit the shift target without a quality escape or a safety incident. Most of the shift is small decisions that someone brings to them: an alarm on a machine, a truck of castings at receiving, a maintenance tech who wants to open a machine, a part that measures just out.

**When they need the documents.** Not to learn. To settle a specific question in under a minute, while someone is waiting: "can I reset this alarm and keep running?", "how many pieces do we check from this lot?", "can I cut this lock, the guy went home?".

**What frustrates them today.**
- The answer exists but is far away: in the QMS on the office PC, or in a binder at the QC office.
- Printouts at the stations go stale. QC-SOP-014 changed in July 2026 (sample size, form, where rejects go, MTC now mandatory). A station printout of Rev 03 is still "the SOP" to anyone who reads it. The footer even says "Uncontrolled copy when printed".
- Asking a senior is fast but depends on who is on shift and on memory.
- Getting it wrong is expensive in both directions: stopping a line for nothing, or letting through a lot or a lock removal that the procedure forbids.

**What they need from a copilot.** A short, exact answer, the document behind it so they can show it to someone who argues, and a plain "I don't know" when the documents don't cover it. Speed matters, but trust matters more: one confident wrong answer and they stop using it.

## 2. User journey (first draft, before the AI critique)

This is the first draft as it was written. Changes after the critique are in section 3.

Persona: Ravi, shift supervisor, CNC shaft line, Hosur plant. Android phone in his pocket, gloves on half the time, noisy floor, patchy mobile data but the plant Wi-Fi works near the line.

1. An operator walks up: "CNC-06 is showing AL-104, can I keep running?"
2. Ravi takes out his phone, opens the copilot (bookmark on the home screen, plant Wi-Fi).
3. He types "AL-104 meaning" or taps a recent question.
4. The copilot answers in two lines: way lube oil low, top up ISO VG 68 to MAX, press RESET, machine can continue. Under it: MNT-MAN-CNC-02 Rev 02, section 6, page number.
5. If he wants to be sure, he taps the source and sees the exact table row from the manual.
6. He tells the operator and goes back to the line. Under a minute, no walk to the office.

Second moment: a truck of castings arrives, 200 pieces, and the inspector asks how many to check.

7. Ravi asks "how many samples for 200 castings". The copilot says 13, from QC-SOP-014 Rev 04.
8. The inspector still has the Rev 03 printout that says 5. The copilot shows a yellow note: "Old Rev 03 said 5 for every lot. Follow Rev 04."

What could go wrong:
- The answer is wrong or made up, and someone acts on it. For safety (lockout) this can hurt a person.
- The question is not covered by the documents and the copilot still answers from general knowledge.
- Two revisions of the same SOP disagree and the copilot answers from the old one.
- Wi-Fi drops on the floor and the app hangs.
- It is too slow (more than a few seconds) so he goes back to asking a senior.
- He types in short forms, Tamil English mix, or with typos.
- A long answer he can't read quickly on a small screen.
- Sensitive plant documents going to an outside AI service.

## 3. AI challenge

Tool: Claude (Sonnet) in a fresh session. Prompt: *"You are a skeptical product manager at a company that sells AI copilots to Indian manufacturing plants, and you have also worked as a shop-floor supervisor. Critique this user journey... Be blunt. What is unrealistic, what is missing, what would make a supervisor stop using it after a week, and what one feature matters most?"* followed by the draft above. Full reply in [docs/ai-critique-raw.md](docs/ai-critique-raw.md). Key parts:

> **1.** The "under a minute, no walk to the office" claim is untested. Phone out, unlock, find bookmark, load, type with gloves, read. Typing "AL-104 meaning" in gloves on a noisy floor is not realistic. ... Voice input in Hindi/Tamil/English mix, or a tap-to-pick alarm list per machine, is what's missing.

> **3.** The journey has no safety class. A lube alarm and a lockout/tagout question can't get the same confident two-liner. Safety questions need a hard "stop, call maintenance or EHS", not a generated answer.

> **4.** No "I don't know" moment. The journey only shows hits. In real use maybe 30% of questions won't be in the SOPs... The refusal has to be a designed screen that says who to call. Otherwise one bad answer ends trust.

> **5.** The Rev 03 vs Rev 04 scenario is too clean. In reality printouts sit at stations, PDFs are scanned images, tables are mangled, and nobody knows which rev is live. Who uploads a new rev? Who retires the old one?

> **8.** Why he quits after a week: two wrong or "not found" answers on real problems. It's slower than asking Murugan, the senior operator, who is always right. He feels exposed: management can see he asked...

> **10.** The one feature that matters most: every answer must be traceable to a source and refuse when unsure... one confident wrong answer kills it and can injure someone. Trust is the product.

### Reflection

**Agreed, and changed:**
- *Safety class (point 3).* Right. A lockout answer and a lube top-up should not look the same. Answers that rest on the LOTO SOP now carry a red banner: follow every step of the full SOP, not the summary, and call the Safety Officer if unsure. I did not go as far as refusing to answer safety questions. The supervisor still needs to know who may remove a lock; hiding that would push them back to guessing.
- *The refusal is a designed screen (point 4).* The "not in the documents" card now says nothing was guessed and who to ask, instead of only "not found".
- *Traceability first (point 10).* This was already the core of the design and it confirmed the priority: every answer must cite a real section or it is shown as not found, and the source is one tap away with the PDF page.
- *Being exposed (point 8).* The question log records questions with no user name. It is there to find gaps in the documents, not to watch people.

**Agreed, but not built (too big for this exercise, it's in "what next"):** voice input in Tamil, Hindi and English (point 1); per machine context so CNC-06 is preselected (point 2); a handoff to a maintenance ticket; an offline cache of the alarm table (point 7).

**Disagreed:**
- *"The Rev 03 vs Rev 04 scenario is too clean" (point 5).* The data in this exercise is clean, true. But the underlying problem is exactly the messy one the critique describes: stale printouts at stations that nobody has retired. That made me more sure it is the right improvement, not less. Document ownership (who uploads, who retires) is a customer question, not something the app can solve, so it went into section 6.
- *"Sample 13 of 200 depends on the AQL level, the customer and the part" (point 6).* In general yes, but this plant's SOP gives one table for all incoming lots. The copilot should answer what the plant's SOP says, not second guess it with general quality knowledge. That is the whole point of answering only from documents.

**What I changed in the journey:** step 4 now ends with the safety banner when the answer comes from LOTO; the journey gets a third moment where the answer is not in the documents (Ravi asks the TX-200 maximum spindle speed, the copilot says it is not in the SOPs, and he calls maintenance); and step 8 is the core of the improvement below.

## 4. The improvement: revision aware answers

**What it does.** When a document exists in more than one revision, only the newest is used to answer. After answering, a second, focused LLM call reads the old revision's matching sections and asks one thing: *would someone following the old printout do something different here?* If yes, the answer shows a yellow box: "Changed in the latest revision. Old Rev 03 said ... Follow the current revision, and replace any old printout." The old sections are listed under the source, marked OLD REVISION.

**Why this one.**
1. It is in the data on purpose. Two revisions of QC-SOP-014 that disagree on sample size, the form, where rejects go and whether an MTC is mandatory. A plain RAG app can easily answer "5 samples" from Rev 03, which is confidently wrong.
2. It is the failure the user journey found: the supervisor's question often comes *because* someone is holding an old printout. Telling them "13" is not enough; they need to know why their colleague thinks it's 5, so they can settle it on the spot and pull the old printout.
3. It turns the copilot into something that improves document control, not just search: each yellow box is a station printout that needs replacing.

**How, and what went wrong on the way.** The first version asked the main answer call to also fill a "revision note". It was unreliable: the same question got the note on one run and not the next. Splitting it into its own call, with one job and a strict "same or different" output, made it consistent (it now appears on every run for the sampling, reject location and MTC questions in `scripts/eval.py`, and correctly does not appear for the BH-220 question, which Rev 03 doesn't cover). It costs one extra short LLM call, only when an older revision of a cited document exists.

## 5. Deploying on the local network

`uv run shopfloor-copilot` binds to `0.0.0.0:8000`, works out the laptop's Wi-Fi IP and prints it with a QR code. The phone on the same Wi-Fi opens that address. No HTTPS, no login: fine for a demo on a trusted network, not for a plant (see below). The UI is one HTML file with no framework and no build step, so it loads fast on a weak connection, and it is built for a phone first: big tap targets, inputs that don't zoom the page, the ask box pinned to the bottom within thumb reach, safe area padding for notches.

## 6. Final reflection

**What I'd build next, in order.**
1. **On premises by default.** BiztelAI's customers don't want documents leaving the plant. Retrieval is already fully local. The LLM is the gap: on this laptop a 3B model takes 90 seconds. On a plant server with a modest GPU, a 7 to 8B model with this same prompt and the citation check is the default I'd test first, and I'd measure accuracy on the eval set before switching.
2. **Ingestion for real documents.** Scanned PDFs (OCR), tables that span pages (the alarm table here runs from page 1 to 2, and the source shows page 1), and documents without the neat header block. Revision status should come from the QMS, not from file names in a folder.
3. **Machine context.** A QR sticker on each machine that opens the copilot with that machine preselected, so "AL-104" means the alarm on *this* controller.
4. **Voice input**, in Tamil, Hindi and English, for gloved hands. Then test it on a real floor; I'm not sure speech recognition holds up next to a running CNC.
5. **Feedback loop.** A thumbs down on an answer, plus the "not found" log, sent weekly to the document owner.
6. **Access and audit.** Login, HTTPS on the plant network, and an audit trail of what was asked and answered, for when someone asks "who told you to do that?".

**What I'm unsure about.**
- Whether the "not in the documents" gate is tuned right. With these embeddings even off topic questions ("tell me a joke") score about 0.5 similarity, so the similarity gate only catches nonsense. The LLM is doing the real refusing, and it did it every time on the eval, but 12 questions is not proof.
- Whether supervisors want a short answer or the SOP text itself. I chose a short answer with the full section one tap away.
- How the revision check behaves when the change is subtle (a tolerance tightened by 0.01) instead of obvious. The sample data only has obvious changes.
- Hosted model quality versus local. The fallback model (gpt-oss-20b) was a bit terser than the main one and dropped a step on the lockout answer sometimes ("Shift Supervisor tries to call the owner first").

**What I'd ask the customer.**
1. Where do the documents live today (QMS, shared drive, paper), and who owns each one? Who publishes a new revision and who pulls the old printouts?
2. Can anything leave the plant network? If not, what hardware can run the model?
3. What are the 20 questions supervisors actually ask most? Can we sit on a shift for a day and write them down?
4. Which languages do supervisors and operators actually read and speak on the floor?
5. Which topics should never get a summary, only the SOP and a call to a person?
6. If the copilot is wrong and someone acts on it, who is accountable? What does the safety team need to see before rollout?

**Challenges while building and deploying, and how I handled them.**

*Biggest challenge: getting the same correct answer every time, not just once.* The first runs looked perfect, so I wrote `scripts/eval.py` to run 12 questions several times and check each answer against the PDFs. It found real problems:
- The revision note showed up on some runs and not others. Fixed by giving it its own LLM call (section 4).
- The lockout answer sometimes left out what to do when the lock owner has gone home, which is usually the reason a supervisor is asking. Fixed with a prompt rule: always add the special case for the same situation as a second "If ..." line.
- "Who is the plant head?" was refused. The answer is in a document header (A. Krishnan, Plant Head), but the similarity gate threshold I started with (0.55) blocked it at 0.47. Testing showed off topic questions also score about 0.5 with this embedding model, so the gate could not separate them anyway. I lowered it to 0.40 and let the LLM, which refused reliably, make the call.
- The model wrote codes with non-breaking hyphens ("SAF‑SOP‑003"), which looks the same but breaks search and copy paste. Normalised in the answer.
After the fixes the eval was 24/24 on the latest run. Earlier runs were 29/36 and 30/36.

*Free tier limits.* Groq's free tier allows 8,000 tokens a minute and 200,000 a day for gpt-oss-120b. Each question is one or two calls of about 2,000 tokens, so a fast demo hits the per minute cap, and a day of testing hit the daily cap. The first version just failed with an error. Now it waits for the per minute window, and when the daily cap is hit it switches to gpt-oss-20b (separate cap) and shows which model answered. In a plant this goes away with a local model, which is another reason it should be the default there.

*Reading the PDFs.* Plain text extraction lost the table layout and split headings like "6. Inspection Dimensions - BH-220 Bearing Housing (Machined, from / sub-contractor)" across lines. Layout mode extraction plus a small heading parser (numbered top level headings, joining a heading that wraps) gives one chunk per section. A heading at the very bottom of a page was getting the wrong page number; fixed by taking the page where the section's text starts.

*Deploying to the phone.* Binding to 0.0.0.0 and printing the LAN IP was easy. The things that usually go wrong are a firewall on the laptop and guest Wi-Fi that blocks devices from seeing each other; both are in the README.

*Docker.* I wrote a Dockerfile but Docker wasn't running on this laptop, so it is untested. I'd rather say that than claim the bonus.
