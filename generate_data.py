import pandas as pd
import random
from datetime import datetime, timedelta

def generate_datasets(num_rows=50):
    start_date = datetime(2026, 9, 1)
    
    ledger_data = []
    bank_data = []
    
    companies = ["Aditya Corp", "Tech Solutions", "Global Industries", "Startup Inc", 
                 "Local Cafe", "Alpha Retail", "Beta Logistics", "Gamma Software"]
    gateways = ["STRIPE*", "WIRE TRANS*", "PAYPAL*", "RZP*", "SQUARE*"]

    for i in range(1, num_rows + 1):
        txn_id = f"TXN-{1000 + i}"
        # Spread dates across the first week of September
        ledger_date = start_date + timedelta(days=random.randint(0, 6))
        company = random.choice(companies)
        amount = round(random.uniform(500.0, 50000.0), 2)
        
        # 1. Always add to internal ledger
        ledger_data.append({
            "transaction_id": txn_id,
            "date": ledger_date.strftime("%Y-%m-%d"),
            "customer_name": company,
            "amount": amount
        })

        # Decide what happens in the bank statement (to create realistic anomalies)
        scenario = random.random()

        if scenario < 0.70:
            # 70% chance: Normal match (with 1-3 day delay and 1-2.5% fee)
            bank_date = ledger_date + timedelta(days=random.randint(1, 3))
            gateway = random.choice(gateways)
            fee = random.uniform(0.01, 0.025)
            bank_amount = round(amount * (1 - fee), 2)
            bank_desc = f"{gateway}{company[:8].upper()}"
            
            bank_data.append({
                "bank_date": bank_date.strftime("%Y-%m-%d"),
                "description": bank_desc,
                "deposit_amount": bank_amount
            })
            
        elif scenario < 0.85:
            # 15% chance: Missing from bank entirely (Failed payout / intentional exception)
            pass 
            
        else:
            # 15% chance: Extreme anomaly (Huge fee error to trigger your deterministic fallback)
            bank_date = ledger_date + timedelta(days=random.randint(1, 3))
            gateway = random.choice(gateways)
            # Create a 10% discrepancy, which the LLM might match by name, but your Python logic should reject
            bank_amount = round(amount * 0.90, 2) 
            bank_desc = f"{gateway}{company[:8].upper()}"
            
            bank_data.append({
                "bank_date": bank_date.strftime("%Y-%m-%d"),
                "description": bank_desc,
                "deposit_amount": bank_amount
            })

    # Shuffle the bank data so it doesn't align row-by-row perfectly with the ledger
    random.shuffle(bank_data)

    pd.DataFrame(ledger_data).to_csv("internal_ledger.csv", index=False)
    pd.DataFrame(bank_data).to_csv("bank_statement.csv", index=False)
    print(f"Successfully generated 50 ledger rows and {len(bank_data)} bank statement rows.")

if __name__ == "__main__":
    generate_datasets()