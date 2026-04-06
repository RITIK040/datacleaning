import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_engine import QuantEngine
import datetime

# ── Ticker Database ─────────────────────────────────────────────────────────
TICKER_DB = {
    "Indian Large-Cap Stocks": [
        ("RELIANCE.NS", "Reliance Industries"),
        ("TCS.NS",      "Tata Consultancy Services"),
        ("HDFCBANK.NS", "HDFC Bank"),
        ("INFY.NS",     "Infosys"),
        ("HINDUNILVR.NS", "Hindustan Unilever"),
        ("ICICIBANK.NS", "ICICI Bank"),
        ("SBIN.NS",     "State Bank of India"),
        ("BAJFINANCE.NS", "Bajaj Finance"),
        ("BHARTIARTL.NS", "Bharti Airtel"),
        ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
        ("LT.NS",       "Larsen & Toubro"),
        ("WIPRO.NS",    "Wipro"),
        ("HCLTECH.NS",  "HCL Technologies"),
        ("AXISBANK.NS", "Axis Bank"),
        ("MARUTI.NS",   "Maruti Suzuki"),
        ("SUNPHARMA.NS", "Sun Pharmaceutical"),
        ("TITAN.NS",    "Titan Company"),
        ("ULTRACEMCO.NS", "UltraTech Cement"),
        ("ONGC.NS",     "Oil & Natural Gas Corp"),
        ("POWERGRID.NS", "Power Grid Corp"),
        ("NTPC.NS",     "NTPC Limited"),
        ("M&M.NS",      "Mahindra & Mahindra"),
        ("BAJAJFINSV.NS", "Bajaj Finserv"),
        ("ADANIENT.NS", "Adani Enterprises"),
        ("ADANIPORTS.NS", "Adani Ports & SEZ"),
    ],
    "Indian Mid-Cap Stocks": [
        ("PERSISTENT.NS", "Persistent Systems"),
        ("COFORGE.NS",  "Coforge"),
        ("MPHASIS.NS",  "Mphasis"),
        ("ZOMATO.NS",   "Zomato"),
        ("PAYTM.NS",    "Paytm"),
        ("NAUKRI.NS",   "Info Edge (Naukri)"),
        ("DMART.NS",    "Avenue Supermarts"),
        ("TATAPOWER.NS", "Tata Power"),
        ("IRCTC.NS",    "IRCTC"),
        ("HAL.NS",      "Hindustan Aeronautics"),
        ("CHOLAFIN.NS", "Cholamandalam Finance"),
        ("PIIND.NS",    "PI Industries"),
    ],
    "US Large-Cap Stocks": [
        ("AAPL",  "Apple"),
        ("MSFT",  "Microsoft"),
        ("GOOGL", "Alphabet (Google)"),
        ("AMZN",  "Amazon"),
        ("NVDA",  "NVIDIA"),
        ("META",  "Meta Platforms"),
        ("TSLA",  "Tesla"),
        ("NFLX",  "Netflix"),
        ("ADBE",  "Adobe"),
        ("CRM",   "Salesforce"),
        ("ORCL",  "Oracle"),
        ("AMD",   "Advanced Micro Devices"),
        ("INTC",  "Intel"),
        ("BRKB",  "Berkshire Hathaway B"),
        ("JPM",   "JPMorgan Chase"),
        ("GS",    "Goldman Sachs"),
        ("V",     "Visa"),
        ("MA",    "Mastercard"),
        ("JNJ",   "Johnson & Johnson"),
        ("PFE",   "Pfizer"),
    ],
    "Crypto": [
        ("BTC-USD",  "Bitcoin"),
        ("ETH-USD",  "Ethereum"),
        ("SOL-USD",  "Solana"),
        ("BNB-USD",  "Binance Coin"),
        ("XRP-USD",  "Ripple"),
        ("ADA-USD",  "Cardano"),
        ("DOGE-USD", "Dogecoin"),
        ("AVAX-USD", "Avalanche"),
        ("DOT-USD",  "Polkadot"),
        ("LINK-USD", "Chainlink"),
        ("MATIC-USD","Polygon"),
        ("LTC-USD",  "Litecoin"),
    ],
    "Forex": [
        ("EURUSD=X",  "EUR / USD"),
        ("GBPUSD=X",  "GBP / USD"),
        ("USDJPY=X",  "USD / JPY"),
        ("USDINR=X",  "USD / INR"),
        ("AUDUSD=X",  "AUD / USD"),
        ("USDCAD=X",  "USD / CAD"),
        ("USDCHF=X",  "USD / CHF"),
        ("EURGBP=X",  "EUR / GBP"),
        ("GBPINR=X",  "GBP / INR"),
        ("EURINR=X",  "EUR / INR"),
    ],
    "Commodities & Futures": [
        ("GC=F",  "Gold Futures"),
        ("SI=F",  "Silver Futures"),
        ("CL=F",  "Crude Oil WTI"),
        ("BZ=F",  "Brent Crude"),
        ("NG=F",  "Natural Gas"),
        ("HG=F",  "Copper Futures"),
        ("PL=F",  "Platinum Futures"),
        ("ZW=F",  "Wheat Futures"),
        ("ZC=F",  "Corn Futures"),
        ("ES=F",  "S&P 500 Futures (ES)"),
        ("NQ=F",  "Nasdaq 100 Futures (NQ)"),
    ],
    "Indices": [
        ("^NSEI",  "Nifty 50"),
        ("^BSESN", "BSE Sensex"),
        ("^NSEBANK", "Bank Nifty"),
        ("^GSPC",  "S&P 500"),
        ("^DJI",   "Dow Jones"),
        ("^IXIC",  "Nasdaq Composite"),
        ("^RUT",   "Russell 2000"),
        ("^FTSE",  "FTSE 100"),
        ("^N225",  "Nikkei 225"),
        ("^HSI",   "Hang Seng"),
    ],
}

# Page config
st.set_page_config(
    page_title="Quant Data Tool",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS — ROG (Orbitron) body font + UnifrakturMaguntia title font
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap" rel="stylesheet">
    <style>
    /* ── Old English / blackletter title ── */
    .qdp-title {
        font-family: 'UnifrakturMaguntia', cursive !important;
        font-size: 28rem;
        color: #ff4b4b;
        letter-spacing: 0.25em;
        word-spacing: 0.5em;
        line-height: 1.3;
        display: block;
        width: 100%;
        text-align: center;
        padding: 0.2em 0;
        margin-bottom: 0;
        transform: scaleY(1.2);
        transform-origin: top center;
    }
    /* ── Page background ── */
    .main { background-color: #0e1117; }
    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    /* ── Status cards ── */
    .status-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e2130;
        border: 1px solid #3e4150;
        margin-bottom: 10px;
    }
    .metric-label {
        color: #808495;
        font-size: 0.8em;
    }
    .metric-value {
        color: #ffffff;
        font-size: 1.5em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# App Title — rendered as HTML so the Old English font class applies
st.markdown('<p class="qdp-title">Quant Data Pro</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.header("Navigation")
app_mode = st.sidebar.radio("View Mode", ["Market Data", "F&O Dashboard", "Ticker Browser"])

if app_mode == "Market Data":
    st.sidebar.subheader("Quick Select Examples")
    categories = {
        "Commodities": "GC=F, CL=F, SI=F",
        "Crypto": "BTC-USD, ETH-USD, SOL-USD",
        "Forex": "EURUSD=X, GBPUSD=X, USDINR=X",
        "Indian Market": "RELIANCE.NS, TCS.NS, ^NSEI",
    }
    selected_cat = st.sidebar.selectbox("Choose a Category", ["None"] + list(categories.keys()))
    if selected_cat != "None":
        ticker = st.sidebar.text_input("Enter Ticker(s)", categories[selected_cat], key="ticker_input_cat")
    else:
        # Pre-fill from Ticker Browser selection
        default_ticker = st.session_state.get("selected_ticker", "RELIANCE.NS")
        ticker = st.sidebar.text_input("Enter Ticker(s) (e.g., RELIANCE.NS, ES=F)", default_ticker, key="ticker_input_default")

    period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], index=4)
    interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

    st.sidebar.subheader("Data Cleaning Options")
    clean_structural = st.sidebar.checkbox("Remove Structural Errors", True)
    clean_missing = st.sidebar.checkbox("Handle Missing Values", True)
    clean_outliers = st.sidebar.checkbox("Remove Outliers/Noise", True)
    convert_returns = st.sidebar.checkbox("Convert Price to Return", True)
    remove_bias = st.sidebar.checkbox("Remove Look-Ahead Bias", True)

    # Initialize Engine
    engine = QuantEngine()

    # State management
    if 'raw_data' not in st.session_state:
        st.session_state.raw_data = None
    if 'cleaned_data' not in st.session_state:
        st.session_state.cleaned_data = None

    # Actions
    if st.sidebar.button("Fetch and Process Data"):
        with st.spinner(f"Downloading data for {ticker}..."):
            st.session_state.raw_data = engine.fetch_data(ticker, period, interval)
            if not st.session_state.raw_data.empty:
                cleaning_options = {
                    'structural': clean_structural,
                    'missing': clean_missing,
                    'outliers': clean_outliers,
                    'returns': convert_returns,
                    'look_ahead': remove_bias
                }
                st.session_state.cleaned_data = engine.clean_data(st.session_state.raw_data, cleaning_options)
            else:
                st.error("No data found. Please check the ticker symbol.")

    # Main Layout
    col1, col2, col3 = st.columns(3)

    if st.session_state.cleaned_data is not None:
        # Metrics
        with col1:
            regime = engine.detect_regime(st.session_state.cleaned_data)
            st.markdown(f'<div class="status-card"><div class="metric-label">Market Regime</div><div class="metric-value">{regime}</div></div>', unsafe_allow_html=True)
        
        with col2:
            val = engine.validate_data(st.session_state.cleaned_data)
            st.markdown(f'<div class="status-card"><div class="metric-label">Audit Status</div><div class="metric-value">{val["status"]}</div></div>', unsafe_allow_html=True)
            
        with col3:
            rows = len(st.session_state.cleaned_data)
            st.markdown(f'<div class="status-card"><div class="metric-label">Data Points</div><div class="metric-value">{rows}</div></div>', unsafe_allow_html=True)

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Charts", "Cleaned Data", "F&O Chain", "Audit Log"])

        with tab1:
            # Check if data is multi-indexed (multiple tickers)
            is_multi = isinstance(st.session_state.cleaned_data.columns, pd.MultiIndex)
            
            if is_multi:
                tickers_found = st.session_state.cleaned_data.columns.get_level_values(0).unique()
                selected_chart_ticker = st.selectbox("Select Ticker for Chart", tickers_found)
                chart_df = st.session_state.cleaned_data[selected_chart_ticker]
            else:
                chart_df = st.session_state.cleaned_data
                selected_chart_ticker = ticker

            # Plotly Candlestick
            fig = go.Figure(data=[go.Candlestick(x=chart_df.index,
                                                open=chart_df['Open'] if 'Open' in chart_df.columns else None,
                                                high=chart_df['High'] if 'High' in chart_df.columns else None,
                                                low=chart_df['Low'] if 'Low' in chart_df.columns else None,
                                                close=chart_df['Close'] if 'Close' in chart_df.columns else None)])
            
            # Add Volume Bar if available
            if 'Volume' in chart_df.columns and chart_df['Volume'].any():
                fig.add_trace(go.Bar(x=chart_df.index, y=chart_df['Volume'], name="Volume", yaxis="y2", opacity=0.3))
                fig.update_layout(yaxis2=dict(title="Volume", overlaying="y", side="right"))

            fig.update_layout(template="plotly_dark", title=f"{selected_chart_ticker} Price Action", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            if 'Daily_Return' in chart_df.columns:
                st.subheader(f"{selected_chart_ticker} Returns Distribution")
                fig_ret = go.Figure(data=[go.Histogram(x=chart_df['Daily_Return'].dropna())])
                fig_ret.update_layout(template="plotly_dark")
                st.plotly_chart(fig_ret, use_container_width=True)

        with tab2:
            st.dataframe(st.session_state.cleaned_data, use_container_width=True)
            csv = st.session_state.cleaned_data.to_csv().encode('utf-8')
            st.download_button("Download Cleaned Data", data=csv, file_name=f"{ticker}_cleaned.csv", mime='text/csv')

        with tab3:
            st.subheader("Options Information")
            if st.button("Load Nearest Option Chain"):
                calls, puts = engine.fetch_options(ticker)
                if not calls.empty:
                    st.write("Calls")
                    st.dataframe(calls, use_container_width=True)
                    st.write("Puts")
                    st.dataframe(puts, use_container_width=True)
                else:
                    st.info("No options data available for this ticker.")

        with tab4:
            st.table(engine.audit_log)

    else:
        st.info("Enter a ticker and click 'Fetch and Process Data' to begin.")
        st.markdown("""
        ### Features:
        - **Automated Cleaning**: Structural errors, missing values, outliers.
        - **Advanced Transform**: Price to return conversion, bias checking.
        - **Regime Detection**: Integrated market state analysis.
        - **F&O Support**: Full chains for compatible tickers.
        - **Audit Trial**: Every step recorded and validated.
        """)

elif app_mode == "Ticker Browser":
    st.header("Ticker Browser")
    st.markdown("Browse all supported tickers. Click **Use** to load a ticker directly into Market Data.")

    # Search bar
    search_query = st.text_input("Search by symbol or name", "").strip().lower()

    any_results = False
    for category, tickers in TICKER_DB.items():
        # Filter by search
        filtered = [
            (sym, name) for sym, name in tickers
            if not search_query or search_query in sym.lower() or search_query in name.lower()
        ]
        if not filtered:
            continue
        any_results = True

        with st.expander(f"{category}  ({len(filtered)} tickers)", expanded=bool(search_query)):
            # Build a display DataFrame
            rows = []
            for sym, name in filtered:
                rows.append({"Symbol": sym, "Name": name})
            df_tickers = pd.DataFrame(rows)
            st.dataframe(df_tickers, use_container_width=True, hide_index=True)

            # Quick-load buttons  (one per row in groups of 4)
            cols_per_row = 4
            batch = [filtered[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]
            for row_batch in batch:
                btn_cols = st.columns(cols_per_row)
                for idx, (sym, name) in enumerate(row_batch):
                    if btn_cols[idx].button(f"{sym}", key=f"btn_{sym}", help=name):
                        st.session_state["selected_ticker"] = sym
                        st.success(f"Ticker **{sym}** selected. Switch to **Market Data** to fetch.")

    if not any_results:
        st.warning("No tickers found matching your search.")

    # Show currently selected ticker
    if "selected_ticker" in st.session_state:
        st.markdown("---")
        st.info(f"Selected ticker ready for Market Data: **{st.session_state['selected_ticker']}**")

else:
    # F&O Dashboard
    st.sidebar.subheader("F&O Config")
    f_ticker = st.sidebar.text_input("Enter Ticker (e.g., RELIANCE.NS, ES=F)", "RELIANCE.NS")
    
    engine = QuantEngine()
    
    fo_tab1, fo_tab2 = st.tabs(["Options Chain", "Futures Analysis"])
    
    with fo_tab1:
        st.subheader(f"Options Chain for {f_ticker}")
        expirations = engine.get_option_expirations(f_ticker)
        
        if expirations:
            selected_exp = st.selectbox("Select Expiration", expirations)
            if st.button("Load Chain"):
                calls, puts = engine.fetch_option_chain(f_ticker, selected_exp)
                
                if not calls.empty or not puts.empty:
                    col_calls, col_puts = st.columns(2)
                    with col_calls:
                        st.write("### Calls")
                        st.dataframe(calls, use_container_width=True)
                    with col_puts:
                        st.write("### Puts")
                        st.dataframe(puts, use_container_width=True)
                else:
                    st.warning("Could not retrieve chain data.")
        else:
            st.info("No options data found for this ticker.")
            
    with fo_tab2:
        st.subheader(f"Futures Analysis for {f_ticker}")
        f_period = st.selectbox("History Period", ["1mo", "3mo", "6mo", "1y"], index=0)
        
        if st.button("Fetch Futures Data"):
            f_data = engine.fetch_futures(f_ticker, f_period)
            if not f_data.empty:
                st.write("### Historical Data")
                st.dataframe(f_data, use_container_width=True)
                
                if 'Basis' in f_data.columns:
                    st.write("### Basis Analysis")
                    fig_basis = go.Figure()
                    fig_basis.add_trace(go.Scatter(x=f_data.index, y=f_data['Basis'], name="Basis"))
                    fig_basis.update_layout(template="plotly_dark", title="Basis Over Time (Future - Spot)")
                    st.plotly_chart(fig_basis, use_container_width=True)
            else:
                st.error("No data found. Ensure it is a valid futures ticker or supported ticker.")
