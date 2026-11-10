## Sample questions

**Q: What is the recommended coolant concentration for the TX-200 CNC turning centre?**

> Found: Recommended coolant concentration: 6 % – 8 % (mix).
- Source: MNT-MAN-CNC-02 Rev 02, section "3. Normal Operating Parameters", page 1
- groq/openai/gpt-oss-120b, 0.6 s

**Q: The machine is showing alarm AL-104. What does it mean and what should the operator do?**

> Found: AL-104 means the way lube oil level is low. The operator should top up with ISO VG 68 oil to the MAX mark, then press RESET. The machine can continue after reset.
- Source: MNT-MAN-CNC-02 Rev 02, section "6. Common Alarms", page 1
- groq/openai/gpt-oss-20b, 0.8 s

**Q: Who is allowed to remove a lockout lock from a machine?**

> Found: Only an authorised person may remove a lock, and only their own lock. If the lock owner is absent, the Production Manager and Safety Officer must both authorise the removal.
>
> Safety procedure banner shown.
- Source: SAF-SOP-003 Rev 05, section "5. Removing Locks", page 1
- Source: SAF-SOP-003 Rev 05, section "6. Removal of a Lock When the Owner Is Absent", page 1
- groq/openai/gpt-oss-20b, 0.6 s

**Q: What is the outer diameter tolerance for the BH-220 bearing housing?**

> Found: The outer diameter tolerance is +/- 0.050 mm.
- Source: QC-SOP-014 Rev 04, section "6. Inspection Dimensions - BH-220 Bearing Housing (Machined, from sub-contractor)", page 2
- groq/openai/gpt-oss-20b, 0.8 s

**Q: How often should spindle runout be checked, and who does it?**

> Found: Monthly, by a Maintenance technician.
- Source: MNT-MAN-CNC-02 Rev 02, section "4. Preventive Maintenance Schedule", page 1
- groq/openai/gpt-oss-20b, 0.5 s

## Our own 5 questions

**Q: How many samples do I take from a lot of 200 castings?**

> Found: Take 13 samples.
>
> Changed in the latest revision: Old Rev 03 said draw 5 samples at random from every lot, irrespective of lot size.
- Source: QC-SOP-014 Rev 04, section "4. Sampling Plan", page 1
- groq/openai/gpt-oss-20b, 0.8 s

**Q: Where do I keep rejected material?**

> Found: Rejected material is tagged RED and moved to Quarantine Cage Q1 in Stores Bay 3. The cage is locked; the key is held by the Shift QC Supervisor.
>
> Changed in the latest revision: Old Rev 03 said rejected material is tagged RED and kept in the Red Bin area near Gate 2 until it is returned to the supplier.
- Source: QC-SOP-014 Rev 04, section "5. Procedure", page 2
- groq/openai/gpt-oss-20b, 13.1 s

**Q: The supplier did not send the material test certificate. Can we still inspect the lot?**

> Found: No, the lot must be put on HOLD and cannot be inspected or accepted until the Material Test Certificate (MTC) is received.
>
> Changed in the latest revision: Old Rev 03 said the lot could be inspected and accepted based on sampling even if the supplier test certificate was not available.
- Source: QC-SOP-014 Rev 04, section "5. Procedure", page 2
- groq/openai/gpt-oss-20b, 17.1 s

**Q: How do I replace a hydraulic hose on the TX-200?**

> Found: 1. Isolate the machine per SAF-SOP-003 and release stored hydraulic pressure.
> 2. Confirm the panel pressure gauge reads zero before loosening any fitting.
> 3. Place a drip tray under the hose and loosen the fittings slowly.
> 4. Fit a new hose of the same rating and tighten the fittings.
> 5. Remove locks per SAF-SOP-003, start the hydraulic unit and confirm pressure returns to 3.5-4.0 MPa with no leaks.
> If the machine is running, first lockout/tagout as per SAF-SOP-003 before starting the procedure.
>
> Safety procedure banner shown.
- Source: MNT-MAN-CNC-02 Rev 02, section "7. Replacing a Hydraulic Hose", page 2
- Source: MNT-MAN-CNC-02 Rev 02, section "2. Safety First", page 1
- groq/openai/gpt-oss-20b, 9.2 s

**Q: What is the maximum spindle speed of the TX-200?**

> Not in the documents: Maximum spindle speed not specified in the provided excerpts.
- groq/openai/gpt-oss-20b, 11.1 s

