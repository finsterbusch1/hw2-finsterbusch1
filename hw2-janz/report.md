# report.md – Homework 2 Report

## Business Use Case

The Janz Corporation is a Service-Disabled Veteran-Owned Small Business that sells medical equipment primarily to VA hospitals and government healthcare facilities. When a customer requests a quote, a JANZ staff member must manually locate the manufacturer's pricing, copy each line item into JANZ's own quote template, apply a markup percentage, and format everything with JANZ branding and contact information. For a quote with 3–5 line items, this process takes 15–30 minutes and is prone to transcription errors — especially when manufacturer quotes use inconsistent formatting or embed discounts in complex ways.

This prototype automates that process: the user pastes or provides the manufacturer quote as text, and the system calls a large language model (LLM) to extract line items, apply the markup, and produce a formatted JANZ quote ready for review.

---

## Model Choice

I used **Google Gemini 2.0 Flash** via the Google AI Studio API for this assignment. Gemini Flash was chosen because it is fast, free at low usage volumes, and handles structured extraction tasks well. I did not test other models extensively, but during informal comparison I found that the same prompt sent to a smaller model (Gemini 1.5 Flash 8B) was more likely to include markdown in its JSON response and less consistent about following the schema exactly. Gemini 2.0 Flash was more reliable for structured output.

---

## Baseline vs. Final Design

**Baseline (Prompt Version 1):**  
The initial prompt was vague — it asked for JSON but specified no schema. Results were inconsistent: field names changed between runs, prices sometimes used list price instead of discounted extended price, and $0.00 bundled items cluttered the output. The quote also contained no bill-to/ship-to information.

**Final Design (Prompt Version 3):**  
After two rounds of prompt iteration, the final prompt includes an explicit JSON schema, a rule excluding $0.00 items, instructions to use extended (post-discount) price, a requirement to capture bill-to and ship-to addresses, and guidance to write clean customer-facing descriptions. The output is now consistently parseable and substantially more complete.

| Metric | Baseline | Final |
|--------|----------|-------|
| JSON parse success rate | ~60% | ~95% |
| Correct price (extended vs. list) | ~50% | ~95% |
| $0.00 items excluded | Never | Consistently |
| Bill-to/ship-to captured | No | Yes |
| Description quality | Raw manufacturer text | Clean, professional |

---

## Where the Prototype Still Fails or Requires Human Review

The system requires human review in several situations. First, when manufacturer quotes contain ambiguous or missing prices (as in Eval Case 4), the model may estimate or omit items — the output must be verified before sending. Second, address formatting is inconsistent: Gemini sometimes combines address fields differently than expected, and the user should always confirm the bill-to and ship-to fields are correct. Third, the prototype does not handle multi-page PDFs or scanned images — it requires text input, so the user must copy and paste from a PDF. Finally, any quote with unusual discount structures (tiered pricing, conditional discounts, trade-in credits) should be reviewed carefully, as the model may misidentify which price is the "extended" price.

---

## Deployment Recommendation

I would recommend deploying this workflow in a **human-in-the-loop** configuration — meaning the AI produces a draft quote that a staff member reviews and approves before sending to the customer. The prototype reliably handles the most time-consuming part of the process (extracting and reformatting line items) but is not accurate enough on edge cases to be deployed fully autonomously. Key conditions for deployment:

1. A human reviews every output before it is sent to a customer
2. The input is clean text (not a scanned image)
3. The markup percentage is configurable and auditable
4. Any quote flagged as ambiguous (missing prices, unusual discount structure) is escalated to a senior staff member

Under these conditions, the workflow could reduce quote preparation time by 50–70% while maintaining accuracy. Fully automated deployment without human review would not be appropriate at this stage.
