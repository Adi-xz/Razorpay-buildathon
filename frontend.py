import streamlit as st
import pandas as pd
import json
import time
from google import genai
from google.genai import types

# 1. Page Config (Hide sidebar by default for a cleaner app feel)
st.set_page_config(page_title="Reconciler Edge", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS Injection to break the "Basic AI Website" look
st.markdown("""
<style>
    /* Hide Streamlit default headers, footers, and menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean up the main container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Style the metric cards to look like modern SaaS widgets */
    div[data-testid="metric-container"] {
        background-color: #121212;
        border: 1px solid #2d2d2d;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        border-top: 4px solid #3b82f6;
    }
    
    /* Custom primary button styling with hover effects */
    div.stButton > button:first-child {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 3. Custom HTML Header
st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>🏦 Reconciler Edge Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; margin-bottom: 3rem;'>Automated ledger reconciliation with deterministic AI bounding.</p>", unsafe_allow_html=True)

# Input Section with better spacing
col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    st.markdown("### 🔑 Authentication")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste key here...")
with col2:
    st.markdown("### 📄 Internal Data")
    ledger_file = st.file_uploader("Upload Internal Ledger (CSV)", type="csv", label_visibility="collapsed")
with col3:
    st.markdown("### 🏦 Bank Data")
    bank_file = st.file_uploader("Upload Bank Statement (CSV)", type="csv", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Execute Reconciliation Pipeline", use_container_width=True):
    if not api_key or not ledger_file or not bank_file:
        st.error("Missing inputs. Please provide the API key and both CSV files.")
        st.stop()

    with st.spinner("Initializing Gemini-3.7-Flash semantic matching..."):
        ledger_df = pd.read_csv(ledger_file)
        bank_df = pd.read_csv(bank_file)
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an AI Finance Controller. Reconcile these records.
        Internal Ledger: {ledger_df.to_dict(orient="records")}
        Bank Statement: {bank_df.to_dict(orient="records")}
        
        Rules:
        1. Dates in bank may be 1-3 days LATER.
        2. Names may have tags (e.g., "STRIPE*").
        3. Bank amount may be up to 2.5% LESS.
        
        Output JSON with arrays "matches" and "exceptions".
        "matches": transaction_id, bank_description, ledger_amount, bank_amount.
        "exceptions": transaction_id, reason.
        """
        
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.7-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                break
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    st.error("API is temporarily overloaded. Please try again.")
                    st.stop()
        
        ai_results = json.loads(response.text)
        matches = ai_results.get("matches", [])
        exceptions = ai_results.get("exceptions", [])
        
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        # Dashboard Metrics Display
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Total Records Processed", len(ledger_df))
        metric_col2.metric("✅ Verified Matches", len(matches))
        metric_col3.metric("⚠️ Exceptions Flagged", len(exceptions))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Clean Dataframes
        st.markdown("### ✅ Verified Transactions")
        st.dataframe(matches, use_container_width=True)
        
        st.markdown("### ⚠️ Exceptions (Requires Human Review)")
        st.dataframe(exceptions, use_container_width=True)