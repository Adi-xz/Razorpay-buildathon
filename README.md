# 🏦 Reconciler Edge: AI Finance Controller

**Razorpay AI Buildathon 2026 - Data & Backend Track Submission**

## 📌 The Problem
When a customer pays an invoice, payment gateways (Stripe, Razorpay, etc.) deduct a processing fee and often delay settlement. Consequently, the internal sales ledger ($1,000) rarely matches the final bank deposit ($975 from "STRIPE*TECH SOL" three days later). Traditional deterministic software fails to match these asynchronous, fuzzy records, requiring hundreds of hours of manual accounting work.

## 🚀 The Solution
Reconciler Edge is a hybrid AI financial pipeline. It utilizes **Gemini 3.7 Flash** as a semantic engine to perform fuzzy matching on misaligned transaction text and dates. 

Crucially, it implements **Deterministic AI Bounding**. To prevent LLM financial hallucinations, a strict Python verification layer recalculates the fee percentages of the AI's proposed matches. If a matched fee discrepancy exceeds the standard 2.5% gateway tolerance, the system rejects the AI's judgment and flags the transaction for human review.

## 🏗️ Architecture & Features
* **Semantic Data Pairing:** LLM-driven reconciliation of internal ledgers vs. bank statements.
* **Deterministic Code Gates:** Mathematical validation layer that strictly bounds AI output (rejecting hallucinated matches > 2.5% variance).
* **Resilient API Handling:** Custom retry loops built into the pipeline to intercept `503 UNAVAILABLE` traffic spikes and silently retry without breaking the UI.
* **Streamlit Operations Dashboard:** Clean, CSS-injected UI for the finance ops team to upload CSVs and review flagged exceptions.

## ⚙️ Local Setup

1. **Clone the repository and install dependencies:**
   ```bash
   pip install -r requirements.txt
2.Generate the synthetic test data (50 rows of fuzzy financial records):
 ```bash
 python generate_data.py
```
3.Launch the Reconciler Edge Dashboard:
```bash
python -m streamlit run frontend.py
```
