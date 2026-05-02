# eval_set.md – Evaluation Set

This file contains 5 test cases used to evaluate the quote converter. Each case is run through `app.py` and the output is checked against the "what a good output should do" criteria.

---

## Case 1 – Normal Case: Multi-line Equipment Quote

**Input summary:**  
MPI UltraScan Versa Premier quote (QUO236257) with 3 line items, one of which is $0.00. Customer is Harry S. Truman Memorial Veterans' Hospital. Qty: 4 units.

**Input file:** `eval_case1_mpi.txt` (the full MPI quote text from the uploaded PDF)

**What a good output should do:**
- Capture all 3 products but drop the $0.00 base unit
- Show 2 line items: 292 table ($9,154.88 × 1.10 = $10,070.37) and Dual Push Handles ($95.00 × 1.10 = $104.50)
- Correctly populate bill-to and ship-to with Harry S. Truman Memorial Veterans' Hospital
- Show mfr quote number QUO236257
- Grand total should be approximately $40,562.98 (4 × $10,070.37 + 4 × $104.50)

---

## Case 2 – Normal Case: Single-item Quote

**Input summary:**  
A simple one-line quote from a manufacturer for a single piece of equipment, no discounts.

**Input text:**
```
QUOTATION
Supplier: MedEquip Co.
Quote #: ME-10042
Date: 04/15/2026

Bill To / Ship To:
Bay Pines VA Healthcare System
10000 Bay Pines Blvd, Bay Pines, FL 33744

Line Items:
Product ID: CHAIR-500
Bariatric Patient Chair, 500lb Capacity, Power Lift
Unit Price: $3,200.00 | Qty: 2 | Extended: $3,200.00 | Total: $6,400.00
```

**What a good output should do:**
- Capture 1 line item correctly
- Apply 10% markup: $3,200 → $3,520.00 per unit
- Line total: $7,040.00
- Populate bill-to/ship-to correctly
- No errors or hallucinated items

---

## Case 3 – Edge Case: Quote with Multiple Discounts and a Free Item

**Input summary:**  
A manufacturer quote where some items have volume discounts and one item is free (bundled accessory).

**Input text:**
```
QUOTATION
Supplier: Hausted Medical
Quote #: H-7821
Date: 04/20/2026
Expires: 07/20/2026

Bill To:
Tuscaloosa VA Medical Center
3701 Loop Rd E, Tuscaloosa, AL 35404

Line Items:
Product ID: STRETCHER-300
Transport Stretcher, Hydraulic, Stainless Rails
List Price: $5,500.00 | Discount: $825.00 | Extended: $4,675.00 | Qty: 3 | Total: $14,025.00

Product ID: MATTRESS-STD
Standard Foam Mattress (included free with stretcher)
Unit Price: $0.00 | Qty: 3 | Total: $0.00

Product ID: IV-POLE-KIT
IV Pole Kit, Dual Hook
List Price: $145.00 | Discount: $0.00 | Extended: $145.00 | Qty: 3 | Total: $435.00

Total: $14,460.00
```

**What a good output should do:**
- Drop the $0.00 mattress line
- Show 2 line items: Stretcher at $5,142.50 (10% markup on $4,675) and IV Pole at $159.50
- NOT use list price ($5,500) — must use the discounted extended price ($4,675)
- Human note: The "free mattress" exclusion should be flagged for human review to ensure it's truly bundled and not a separate deliverable

---

## Case 4 – Likely Failure Case: Ambiguous or Missing Prices

**Input summary:**  
A poorly formatted manufacturer email with missing extended prices — the model may hallucinate or refuse.

**Input text:**
```
Hi,

Attached is our pricing for the requested items. Please see below:

- Model X100 Infusion Pump: $2,100 each, you get the government rate
- Model AC-20 IV Stand: around $300, we can work on price
- Installation & Training: call us for pricing

Ship to: Gainesville VAMC, 1601 SW Archer Rd, Gainesville FL 32608

Thanks,
Sales Team
```

**What a good output should do:**
- Attempt to extract X100 ($2,100) and AC-20 (~$300) with a note that prices are approximate
- Flag that installation/training has no price and cannot be included
- NOT hallucinate a price for installation
- This case almost certainly requires human review before sending

---

## Case 5 – Edge Case: International/Non-VA Customer

**Input summary:**  
A manufacturer quote for a non-VA hospital customer to verify that bill-to/ship-to fields work for non-government customers.

**Input text:**
```
QUOTATION
Supplier: Stryker Medical
Quote #: STR-99201
Date: 03/01/2026
Expires: 06/01/2026

Bill To:
HCA Healthcare – Riverside Medical Center
3948 3rd St S, Jacksonville Beach, FL 32250
Attn: Purchasing Dept

Ship To:
Same as Bill To

Line Items:
Product ID: FL28-BED
Acute Care Electric Hospital Bed, Full Electric
List Price: $7,800.00 | GPO Discount: $1,170.00 | Extended: $6,630.00 | Qty: 10 | Total: $66,300.00

Product ID: BED-RAIL-STD
Standard Side Rails (set of 4)
Unit Price: $210.00 | Qty: 10 | Total: $2,100.00

Total: $68,400.00
```

**What a good output should do:**
- Correctly show a non-VA customer in bill-to/ship-to
- Apply 10% markup: $6,630 → $7,293.00 and $210 → $231.00
- Grand total: $75,240.00
- Handle "same as bill to" correctly — ship-to should mirror bill-to
