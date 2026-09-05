import os
import json
import pandas as pd
from google import genai
from google.genai import types

def main():
    print("Loading datasets...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        ledger_df = pd.read_csv(os.path.join(script_dir, "internal_ledger.csv"))
        bank_df = pd.read_csv(os.path.join(script_dir, "bank_statement.csv"))
    except FileNotFoundError:
        print("Error: Run generate_data.py first to create the CSVs.")
        return

    client = genai.Client(api_key="YOUR_API_KEY_HERE")

    prompt = f"""
    You are an AI Finance Controller. Reconcile these internal sales records with the messy bank deposits.

    Internal Ledger:
    {ledger_df.to_dict(orient="records")}

    Bank Statement:
    {bank_df.to_dict(orient="records")}

    Rules:
    1. Dates in the bank statement may be 1 to 3 days LATER.
    2. Names may be abbreviated with processor tags (e.g., "STRIPE*").
    3. The bank amount may be up to 2.5% LESS than the ledger amount.

    Output a JSON object with two arrays: "matches" and "exceptions". 
    "matches" must contain: 'transaction_id', 'bank_description', 'ledger_amount', and 'bank_amount'.
    "exceptions" must contain: 'transaction_id' and 'reason'.
    """

    print("Sending 50-record batch to Gemini-3.7-Flash...")
    response = client.models.generate_content(
        model='gemini-3.7-flash',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    # Parse the LLM's JSON output
    ai_results = json.loads(response.text)
    
    verified_matches = []
    deterministic_exceptions = ai_results.get("exceptions", [])

    print("\n--- RUNNING DETERMINISTIC VALIDATION LAYER ---")
    # AI Judgment: Do not blindly trust the LLM. Verify the math in Python.
    for match in ai_results.get("matches", []):
        ledger_amt = float(match['ledger_amount'])
        bank_amt = float(match['bank_amount'])
        
        # Calculate actual fee percentage
        fee_percentage = ((ledger_amt - bank_amt) / ledger_amt) * 100
        
        if fee_percentage > 2.5 or fee_percentage < 0:
            print(f"⚠️ REJECTED BY CODE: {match['transaction_id']} (LLM hallucinated a match with {fee_percentage:.1f}% discrepancy)")
            deterministic_exceptions.append({
                "transaction_id": match["transaction_id"],
                "reason": f"System rejected LLM match. Fee discrepancy ({fee_percentage:.1f}%) exceeds 2.5% bound."
            })
        else:
            verified_matches.append(match)

    # Compile the final hardened report
    final_report = {
        "metrics": {
            "total_ledger_records": len(ledger_df),
            "verified_matches": len(verified_matches),
            "exceptions_flagged": len(deterministic_exceptions)
        },
        "verified_matches": verified_matches,
        "exceptions": deterministic_exceptions
    }

    # Force the JSON file to save in the exact same folder as the script
    output_path = os.path.join(script_dir, "reconciliation_report.json")
    with open(output_path, "w") as f:
        json.dump(final_report, f, indent=2)
        
    print(f"\nFinal run complete. Report saved exactly here: {output_path}")

if __name__ == "__main__":
    main()