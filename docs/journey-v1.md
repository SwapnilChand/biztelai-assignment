# User journey, first draft (before any AI critique)

Persona: Ravi, shift supervisor, CNC shaft line, Hosur plant. 8 to 15 years on the floor, came up from operator. Runs 15 to 25 operators and 6 machines (CNC-04 to CNC-09) on a shift. Android phone in his pocket, gloves on half the time, noisy floor, patchy mobile data but the plant Wi-Fi works near the line.

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
- He types in short forms, Tamil-English mix, or with typos.
- A long answer he can't read quickly on a small screen.
- Sensitive plant documents going to an outside AI service.
