import os
import pandas as pd
from google import genai
from google.genai import types

# 1. Initialize the Gemini Client
# Remember to remove your key before uploading to GitHub!
client = genai.Client(api_key="YOUR_API_KEY_HERE") 

def main():
    print("Loading CSV files...")
    
    # Automatically get the folder where this Python script is saved
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the absolute paths to the CSV files
    ledger_path = os.path.join(script_dir, "internal_ledger.csv")
    bank_path = os.path.join(script_dir, "bank_statement.csv")

    try:
        ledger_df = pd.read_csv(ledger_path)
        bank_df = pd.read_csv(bank_path)
    except FileNotFoundError:
        print(f"Error: Could not find the CSV files.")
        print(f"Python is looking exactly here:\n{ledger_path}")
        print("If the files are there, ensure Notepad didn't accidentally save them as 'internal_ledger.csv.txt'.")
        return

    # Convert the CSV data to strings so we can send them to the LLM
    ledger_data = ledger_df.to_dict(orient="records")
    bank_data = bank_df.to_dict(orient="records")

    # ... (The rest of the Gemini API prompt and call remains exactly the same below this)

    # 3. Create the Prompt
    prompt = f"""
    You are an expert AI Finance Controller. Reconcile these internal sales ledger records with the messy bank statement records.

    Internal Ledger:
    {ledger_data}

    Bank Statement:
    {bank_data}

    Rules for matching:
    1. Dates in the bank statement may be 1 to 3 days LATER than the internal ledger date.
    2. Names may be abbreviated or include processor tags (e.g., "STRIPE*").
    3. The bank deposit amount may be up to 2.5% LESS than the ledger amount due to payment gateway fees.

    You must return a JSON object with two arrays: "matches" and "exceptions". 
    - "matches": list of objects with 'transaction_id', 'bank_description', and 'confidence_score' (High, Medium, Low).
    - "exceptions": list of objects with 'transaction_id' and 'reason' for any ledger record that doesn't have a confident match.
    """

    print("Sending data to Gemini for reconciliation. Please wait...")
    
    # 4. Call the Gemini API and force structured JSON output
    response = client.models.generate_content(
        model='gemini-3.7-flash', # Update this line right here
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    # 5. Output the results
    print("\n--- RECONCILIATION RESULTS ---\n")
    print(response.text)
    
    # Write the results to a file for your proof-of-work submission
    with open("reconciliation_output.json", "w") as f:
        f.write(response.text)
    print("\nResults saved to 'reconciliation_output.json'.")

if __name__ == "__main__":
    main()