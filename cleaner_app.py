import streamlit as st
import pandas as pd
import yfinance as yf
from cleaner_engine import DataCleaner
import io

# Page Config
st.set_page_config(page_title="Data Clean & Download Pro", page_icon="🧹", layout="wide")

# Custom Styles
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stHeader { color: #f63366; }
    .status-box { 
        padding: 20px; 
        border-radius: 10px; 
        background-color: #1e2130; 
        border: 1px solid #3e4150;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("🧹 Data Clean & Download Pro")
    st.info("Search a ticker or upload a CSV to apply the 11-step cleaning pipeline and download the results.")

    # Sidebar Navigation
    st.sidebar.header("1. Input Data")
    input_method = st.sidebar.radio("Select Source", ["Ticker Search", "File Upload"])

    raw_df = None
    filename = "data_export"

    if input_method == "Ticker Search":
        ticker = st.sidebar.text_input("Enter Ticker (e.g. AAPL, BTC-USD, RELIANCE.NS)", "RELIANCE.NS")
        period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
        if st.sidebar.button("Fetch Data"):
            with st.spinner(f"Fetching {ticker}..."):
                raw_df = yf.download(ticker, period=period)
                if not raw_df.empty:
                    st.session_state.raw_df = raw_df
                    st.session_state.filename = f"{ticker}_{period}"
                    st.success(f"Successfully fetched {len(raw_df)} rows for {ticker}")
                else:
                    st.error("No data found. Please check the ticker symbol.")

    else:
        uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            raw_df = pd.read_csv(uploaded_file)
            st.session_state.raw_df = raw_df
            st.session_state.filename = uploaded_file.name.split('.')[0]
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Processing Section
    if 'raw_df' in st.session_state:
        df_to_clean = st.session_state.raw_df
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Raw Data Preview")
            st.dataframe(df_to_clean.head(10), use_container_width=True)
            st.write(f"Shape: {df_to_clean.shape}")

        if st.button("🚀 Apply 11-Step Cleaning Pipeline"):
            cleaner = DataCleaner()
            with st.spinner("Executing cleaning logic..."):
                cleaned_df = cleaner.clean(df_to_clean)
                st.session_state.cleaned_df = cleaned_df
                st.balloons()

        if 'cleaned_df' in st.session_state:
            with col2:
                st.subheader("✨ Cleaned Data Preview")
                st.dataframe(st.session_state.cleaned_df.head(10), use_container_width=True)
                st.write(f"Shape: {st.session_state.cleaned_df.shape}")

            st.markdown("---")
            st.subheader("💾 Download results")
            
            # Format selection
            format = st.selectbox("Select Export Format", ["CSV", "Excel"])
            
            if format == "CSV":
                csv = st.session_state.cleaned_df.to_csv(index=True).encode('utf-8')
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv,
                    file_name=f"{st.session_state.filename}_cleaned.csv",
                    mime='text/csv',
                )
            else:
                # Excel buffering
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    st.session_state.cleaned_df.to_excel(writer, index=True, sheet_name='CleanedData')
                
                st.download_button(
                    label="📥 Download Cleaned Excel",
                    data=buffer,
                    file_name=f"{st.session_state.filename}_cleaned.xlsx",
                    mime="application/vnd.ms-excel"
                )

if __name__ == "__main__":
    main()
