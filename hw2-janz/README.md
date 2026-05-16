# HW2 – Manufacturer Quote → JANZ Quote Converter

**Course:** JHU GenAI Workflow  
**Student:** [Brian Finsterbusch]  
**Video Walkthrough:** [https://youtu.be/qkYbOtyWHZk]
---

## Business Workflow

**Workflow chosen:** Manufacturer quote reformatting  
**Who the user is:** A sales or quoting staff member at The Janz Corporation  
**Input:** A manufacturer's quotation (plain text or pasted content) containing product IDs, descriptions, quantities, and discounted prices  
**Output:** A formatted JANZ Corporation quote with JANZ branding, contact info, a 10% markup applied to manufacturer prices, and a 60-day expiration date  

**Why automate this?**  
Currently, JANZ staff manually re-enter each line item from a manufacturer quote into their own quote template. This takes 15–30 minutes per quote and introduces transcription errors. A GenAI workflow can extract the structured data, apply the markup formula, and produce a draft quote in seconds — freeing staff to review and approve rather than retype.

---

## Setup Instructions

### 1. Install dependencies
```bash
pip install google-generativeai
```

### 2. Get a free Gemini API key
- Go to [https://aistudio.google.com](https://aistudio.google.com)
- Sign in and click **Get API Key**
- Copy your key

### 3. Set your API key
**Windows:**
```
set GEMINI_API_KEY=your_key_here
```
**Mac/Linux:**
```
export GEMINI_API_KEY=your_key_here
```

### 4. Run the app
```bash
# Use built-in sample quote (MPI UltraScan Versa Premier)
python app.py

# Use your own quote text file
python app.py --input my_quote.txt

# Custom markup percentage
python app.py --input my_quote.txt --markup 12
```

Output is saved to `janz_quote_output.txt` and also printed to the terminal.

---

## Repository Structure

```
hw2-janz/
├── README.md          ← this file (includes video link)
├── app.py             ← main Python script
├── prompts.md         ← prompt versions and iteration notes
├── eval_set.md        ← 5 test cases with expected outcomes
└── report.md          ← final report
```

---

## Files

| File | Purpose |
|------|---------|
| `app.py` | Main script — reads manufacturer quote, calls Gemini, outputs JANZ quote |
| `prompts.md` | Three prompt versions with notes on what changed and why |
| `eval_set.md` | 5 evaluation cases including edge cases |
| `report.md` | Business case, model choice, evaluation results, recommendation |

Initial commit - all project files
