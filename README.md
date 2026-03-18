# IFRS Accounting Copilot v2

Part of the **Exploring AI in Finance** series by Akshita Gagrani.

## Features

### Three Analysis Modes
1. **Quick Treatment** — Full IFRS treatment: applicable standard, recognition, measurement, journal entries, disclosure drafts, practical notes, common errors
2. **Audit Memo** — Structured technical memo: Issue → Guidance → Analysis → Conclusion → Alternative Views → Audit Considerations (Q&A format)
3. **Compare Treatments** — Side-by-side comparison of two treatments: P&L impact, balance sheet impact, ratio impact, recommendation

### Context-Aware Analysis
- Industry selection (Banking, Real Estate, SaaS, Manufacturing, etc.)
- Jurisdiction (UAE, KSA, EU, India/Ind AS, UK, etc.) with known carve-outs flagged
- Entity type (Listed, Private, SME, Government)
- Functional currency
- Reporting period

### Additional Features
- 20 pre-loaded example transactions across all 3 modes
- IFRS paragraph references (cited only when high confidence)
- Disclosure draft with audit-ready policy wording
- Common errors section
- Jurisdiction-specific notes (UAE RERA, India Ind AS carve-outs, EU endorsement differences)
- Export to HTML report (downloadable)
- Full disclaimer and reference guidance

## Setup

### 1. Get Google AI API Key (free)
Go to https://aistudio.google.com/app/apikey

### 2. Local
```bash
pip install -r requirements.txt
```
Add key to `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your-key"
```
Run:
```bash
streamlit run app.py
```

### 3. Deploy to Streamlit Cloud
1. Push to GitHub
2. Connect at https://share.streamlit.io
3. Add GOOGLE_API_KEY in Settings → Secrets
4. Deploy

## Tech Stack
- Streamlit (frontend)
- Google Gemini 2.0 Flash (LLM)
- No database — stateless per query

## Disclaimer
AI-generated indicative guidance. Not a substitute for professional accounting advice.
