"""
app.py - Manufacturer Quote to JANZ Quote Converter
Homework 2 - GenAI Workflow

What this script does:
  1. Reads a manufacturer quote (plain text pasted below, or from a .txt file)
  2. Sends it to Google Gemini with a system prompt
  3. Gemini extracts line items and reformats them into a JANZ-style quote
  4. Applies a 10% markup to all prices
  5. Saves the output to janz_quote_output.txt

HOW TO RUN:
  python app.py
  python app.py --input my_quote.txt
  python app.py --input my_quote.txt --markup 15
"""

import argparse
import os
import json
from google import genai
from datetime import date, timedelta

# ── 1. Configuration ──────────────────────────────────────────────────────────

# Paste your Gemini API key here, or set it as an environment variable:
#   Windows:  set GEMINI_API_KEY=your_key_here
#   Mac/Linux: export GEMINI_API_KEY=your_key_here
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# Default markup percentage applied to all manufacturer prices
DEFAULT_MARKUP_PERCENT = 10.0

# JANZ company info (printed on every quote)
JANZ_INFO = {
    "company":   "The Janz Corporation",
    "address":   "275 Outerbelt Street",
    "city":      "Columbus OH 43213-1529",
    "phone":     "(614) 759-7700",
    "fax":       "(614) 754-5234",
    "website":   "www.janzcorporation.com",
    "email":     "orders@janzcorporation.com",
    "duns":      "103534595",
    "cage":      "55CB9",
    "sales_rep": "Brian L Finsterbusch",
    "sdvosb":    "Service-Disabled Veteran-Owned Small Business",
}

# ── 2. System Prompt (loaded from prompts.md revision 2) ─────────────────────

SYSTEM_PROMPT = """You are a quoting assistant for The Janz Corporation, a government medical equipment distributor.

Your job is to read a manufacturer's quotation and convert it into a structured JANZ quote.

RULES:
1. Extract every line item: item/product ID, short description, quantity, and the manufacturer's EXTENDED price (the final per-unit price after any discounts shown).
2. DO NOT include $0.00 items unless they are required accessories explicitly bundled in.
3. Return your answer ONLY as a valid JSON object. No extra text, no markdown, no explanation.
4. Use this exact JSON structure:

{
  "manufacturer": "<name of manufacturer>",
  "mfr_quote_number": "<quote number from manufacturer doc>",
  "mfr_quote_date": "<date from manufacturer doc>",
  "bill_to_name": "<customer name from manufacturer doc>",
  "bill_to_address": "<full address>",
  "ship_to_name": "<ship-to name if different, else same as bill_to>",
  "ship_to_address": "<full address>",
  "line_items": [
    {
      "line": 1,
      "item_id": "<product ID>",
      "description": "<clean, customer-facing description>",
      "quantity": <number>,
      "mfr_unit_price": <number>
    }
  ],
  "notes": "<any important quote notes, terms, or conditions worth flagging>"
}

Important:
- mfr_unit_price should be the per-unit extended price (after discount), not the line total.
- descriptions should be professional and readable — clean up any internal codes.
- If bill_to and ship_to are the same, duplicate the info in both fields.
"""

# ── 3. Build the JANZ Quote from Gemini's JSON ────────────────────────────────

def apply_markup(price: float, markup_pct: float) -> float:
    """Add a percentage markup to a price and round to 2 decimal places."""
    return round(price * (1 + markup_pct / 100), 2)

def build_janz_quote(gemini_data: dict, markup_pct: float) -> str:
    """
    Takes the parsed JSON from Gemini and formats it as a readable JANZ quote.
    Returns a formatted text string.
    """
    today = date.today()
    expiration = today + timedelta(days=60)  # 60-day quote validity

    lines = []
    lines.append("=" * 70)
    lines.append(f"  {JANZ_INFO['company']}")
    lines.append(f"  {JANZ_INFO['address']}, {JANZ_INFO['city']}")
    lines.append(f"  Phone: {JANZ_INFO['phone']}  |  Fax: {JANZ_INFO['fax']}")
    lines.append(f"  {JANZ_INFO['website']}  |  {JANZ_INFO['email']}")
    lines.append(f"  DUNS: {JANZ_INFO['duns']}  |  Cage Code: {JANZ_INFO['cage']}")
    lines.append(f"  {JANZ_INFO['sdvosb']}")
    lines.append("=" * 70)
    lines.append(f"\n  QUOTE")
    lines.append(f"  Date:        {today.strftime('%m/%d/%Y')}")
    lines.append(f"  Expiration:  {expiration.strftime('%m/%d/%Y')}")
    lines.append(f"  Sales Rep:   {JANZ_INFO['sales_rep']}")
    lines.append(f"\n  Manufacturer:      {gemini_data.get('manufacturer','')}")
    lines.append(f"  Mfr Quote #:       {gemini_data.get('mfr_quote_number','')}")
    lines.append(f"  Mfr Quote Date:    {gemini_data.get('mfr_quote_date','')}")
    lines.append("\n" + "-" * 70)
    lines.append("  BILL TO:")
    lines.append(f"    {gemini_data.get('bill_to_name','')}")
    lines.append(f"    {gemini_data.get('bill_to_address','')}")
    lines.append("\n  SHIP TO:")
    lines.append(f"    {gemini_data.get('ship_to_name','')}")
    lines.append(f"    {gemini_data.get('ship_to_address','')}")
    lines.append("\n" + "-" * 70)

    # Column headers
    lines.append(f"\n  {'LINE':<5} {'ITEM ID':<20} {'QTY':<6} {'UNIT PRICE':>12} {'TOTAL':>12}")
    lines.append(f"  {'DESCRIPTION'}")
    lines.append("  " + "-" * 66)

    grand_total = 0.0
    for item in gemini_data.get("line_items", []):
        mfr_price  = float(item.get("mfr_unit_price", 0))
        janz_price = apply_markup(mfr_price, markup_pct)
        qty        = int(item.get("quantity", 1))
        line_total = round(janz_price * qty, 2)
        grand_total += line_total

        lines.append(
            f"\n  {item['line']:<5} {item['item_id']:<20} {qty:<6} "
            f"${janz_price:>10,.2f} ${line_total:>10,.2f}"
        )
        lines.append(f"  {item['description']}")

    lines.append("\n" + "-" * 70)
    lines.append(f"  {'SUBTOTAL':>56} ${grand_total:>10,.2f}")
    lines.append(f"  {'SHIPPING':>56} {'TBD':>11}")
    lines.append(f"  {'TOTAL':>56} ${grand_total:>10,.2f}")
    lines.append("\n" + "=" * 70)
    lines.append(f"\n  Markup applied: {markup_pct}% over manufacturer pricing")
    lines.append(f"  Credit card payments over $11,000 subject to 3.5% fee.")

    notes = gemini_data.get("notes", "").strip()
    if notes:
        lines.append(f"\n  Notes: {notes}")

    lines.append("\n" + "=" * 70)
    lines.append("  Email orders to: orders@janzcorporation.com")
    lines.append("  Questions? Call Brian L Finsterbusch at (614) 759-7700")
    lines.append("=" * 70)

    return "\n".join(lines)

# ── 4. Main Function ──────────────────────────────────────────────────────────

def main():
    # --- Parse command-line arguments ---
    parser = argparse.ArgumentParser(
        description="Convert a manufacturer quote to a JANZ quote using Gemini AI."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to a .txt file containing the manufacturer quote. "
             "If not provided, uses the built-in sample quote.",
        default=None
    )
    parser.add_argument(
        "--markup", "-m",
        type=float,
        default=DEFAULT_MARKUP_PERCENT,
        help=f"Markup percentage to apply (default: {DEFAULT_MARKUP_PERCENT}%%)"
    )
    parser.add_argument(
        "--output", "-o",
        default="janz_quote_output.txt",
        help="Output filename (default: janz_quote_output.txt)"
    )
    args = parser.parse_args()

    # --- Load manufacturer quote text ---
    if args.input:
        print(f"Reading manufacturer quote from: {args.input}")
        with open(args.input, "r") as f:
            quote_text = f.read()
    else:
        # Built-in sample quote for testing (the MPI quote from the assignment)
        print("No input file specified. Using built-in MPI sample quote.")
        quote_text = """
QUOTATION - Medical Positioning, Inc.
Quote Number: QUO236257
Expires: 05/23/2026
Date Created: 06/10/2025

Bill To / Ship To:
Harry S. Truman Memorial Veterans' Hospital
800 Hospital Drive, Columbia MO 65201-5297

MPI Contact: Patrick Baker (PBaker@medicalpositioning.com)

Line Items:
Product ID: 292
292_UltraScan Versa Premier Table, Height/Fowler/Trendelenburg, Dual Imaging Drop Sections
Unit Price: $12,495.00 | Discount: $3,340.12 | Extended Price: $9,154.88 | Qty: 4 | Total: $36,619.52

Product ID: 9000_UVP
9000_UltraScan Versa Premier Single Pedal Braking Base
Unit Price: $0.00 | Extended Price: $0.00 | Qty: 4 | Total: $0.00

Product ID: 15844
Dual Push Handles
Unit Price: $95.00 | Extended Price: $95.00 | Qty: 4 | Total: $380.00

Subtotal: $50,360.00
After Discount Total: $36,999.52

Notes: SDVOSB and ECAT quotes available upon request.
Terms: GSA Agreement 36F79722DOO75
"""

    # --- Configure Gemini ---
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\nERROR: Please set your Gemini API key!")
        print("  Option 1: Edit app.py and replace YOUR_API_KEY_HERE")
        print("  Option 2: Set environment variable GEMINI_API_KEY=your_key")
        return

    client=genai.Client(api_key=API_KEY)
    print(f"\nSending quote to Gemini... (markup: {args.markup}%)")
    response = client.models.generate_content(model="gemini-2.5-flash",contents=quote_text,config={"system_instruction":SYSTEM_PROMPT})
    raw_text = response.text.strip()

    # --- Parse JSON from Gemini ---
    # Strip markdown code fences if Gemini adds them
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    try:
        gemini_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"\nERROR: Gemini returned invalid JSON: {e}")
        print("Raw response:")
        print(raw_text)
        return

    # --- Build JANZ quote ---
    janz_quote = build_janz_quote(gemini_data, args.markup)

    # --- Save output ---
    with open(args.output, "w") as f:
        f.write(janz_quote)

    print(f"\nSuccess! JANZ quote saved to: {args.output}")
    print("\n" + "=" * 50)
    print(janz_quote)

if __name__ == "__main__":
    main()
