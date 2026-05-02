# prompts.md – Prompt Iteration Log

This file documents three versions of the system prompt used in `app.py`, along with notes on what changed and why.

---

## Version 1 – Initial Prompt

```
You are a quoting assistant. Read the manufacturer quote and reformat it as a JANZ Corporation quote.
Extract line items with item IDs, descriptions, quantities, and prices.
Return the result as JSON.
```

**What I observed:**
- Gemini sometimes returned prices without applying the discount shown (used list price instead of extended price)
- JSON structure was inconsistent between runs — sometimes "items", sometimes "line_items", sometimes "products"
- Descriptions were copied verbatim from the manufacturer (included internal model codes the customer doesn't need)
- $0.00 bundled items (like the base unit) were sometimes included, sometimes dropped — unpredictable

**Problems to fix:**
- No explicit JSON schema → inconsistent field names
- No instruction about which price to use (list vs. discounted extended)
- No guidance on cleaning up descriptions

---

## Version 2 – Added JSON Schema + Price Clarification

```
You are a quoting assistant for The Janz Corporation, a government medical equipment distributor.

Read the manufacturer's quotation and convert it into a structured JANZ quote.

RULES:
1. Extract every line item: product ID, description, quantity, and the EXTENDED price (after discount).
2. Return ONLY valid JSON. No extra text. Use this structure exactly:

{
  "manufacturer": "...",
  "mfr_quote_number": "...",
  "line_items": [
    {
      "line": 1,
      "item_id": "...",
      "description": "...",
      "quantity": 0,
      "mfr_unit_price": 0.00
    }
  ]
}
```

**What changed:** Added an explicit JSON schema and clarified to use extended (discounted) price.  
**What improved:** JSON structure became consistent and parseable every run. Prices were now correct.  
**What stayed the same / got worse:** Gemini still included $0.00 items. Descriptions were still raw manufacturer text. No bill-to/ship-to info was captured.

---

## Version 3 – Final Prompt (used in app.py)

```
You are a quoting assistant for The Janz Corporation, a government medical equipment distributor.

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
  "bill_to_name": "<customer name>",
  "bill_to_address": "<full address>",
  "ship_to_name": "<ship-to name if different>",
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
  "notes": "<any important quote notes, terms, or conditions>"
}

Important:
- mfr_unit_price should be the per-unit extended price (after discount), not the line total.
- Descriptions should be professional and readable — clean up any internal codes.
- If bill_to and ship_to are the same, duplicate the info in both fields.
```

**What changed:** Added explicit $0.00 exclusion rule, added bill-to/ship-to fields, added notes field, told the model to write clean customer-facing descriptions.  
**What improved:** $0.00 base unit no longer appears in output. Bill-to and ship-to are captured correctly. Descriptions are cleaner. Notes/terms from the manufacturer are preserved.  
**What stayed the same:** Occasional formatting of addresses varies slightly — human review of the output is still recommended before sending to a customer.

Step 5 - prompt iteration documented
