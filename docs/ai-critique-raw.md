1. The "under a minute, no walk to the office" claim is untested. Phone out, unlock, find bookmark, load, type with gloves, read. Typing "AL-104 meaning" in gloves on a noisy floor is not realistic. Half the time he'll just shout across to a senior. Voice input in Hindi/Tamil/English mix, or a tap-to-pick alarm list per machine, is what's missing.

2. Ravi doesn't ask "what does AL-104 mean." He asks "can I keep running?" The answer "top up oil, press RESET, continue" is a liability. Who signs off on that? Same alarm on a different machine or controller (Fanuc vs Siemens) means something else. The journey ignores machine model. CNC-06 should be pre-selected, or the copilot must ask.

3. The journey has no safety class. A lube alarm and a lockout/tagout question can't get the same confident two-liner. Safety questions need a hard "stop, call maintenance or EHS", not a generated answer.

4. No "I don't know" moment. The journey only shows hits. In real use maybe 30% of questions won't be in the SOPs: tribal knowledge, a new tool, a customer-specific deviation. The refusal has to be a designed screen that says who to call. Otherwise one bad answer ends trust.

5. The Rev 03 vs Rev 04 scenario is too clean. In reality printouts sit at stations, PDFs are scanned images, tables are mangled, and nobody knows which rev is live. Who uploads a new rev? Who retires the old one? No document owner is named. If this isn't controlled, the copilot is confidently wrong on day 30.

6. "Sample 13 of 200" depends on the AQL level, the customer and the part. The journey skips the follow-up question that a good answer would ask.

7. Missing entirely: language (SOPs are English, operators speak Tamil/Hindi), logging (who asked what, what was done, for audits), a handoff to the maintenance ticket when the answer is "call maintenance", and what happens when Wi-Fi drops. The offline case needs a cached top-50 alarm list.

8. Why he quits after a week:
- Two wrong or "not found" answers on real problems.
- It's slower than asking Murugan, the senior operator, who is always right.
- He feels exposed: management can see he asked.
- Typing.
- Login or session expiry mid-shift.

9. Nobody asked the buyer's question: who is accountable when the copilot is wrong? Plant heads will want an audit trail and a disclaimer before rollout.

10. The one feature that matters most: every answer must be traceable to a source and refuse when unsure. That means a page-cited answer, a visible "not found in SOPs, ask X" fallback, and a hard escalation on safety topics. Everything else (voice, Tamil, offline) improves adoption, but one confident wrong answer kills it and can injure someone. Trust is the product.
