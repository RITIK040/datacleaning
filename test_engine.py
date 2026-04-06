from data_engine import QuantEngine
import pandas as pd

def test_engine():
    engine = QuantEngine()
    
    ticker = "AAPL"
    print(f"Testing Fetch for {ticker}...")
    data = engine.fetch_data(ticker, period="1mo")
    
    if data.empty:
        print("Fetch failed!")
        return
    
    print(f"Fetched {len(data)} rows.")
    
    print("Testing Clean...")
    options = {
        'structural': True,
        'missing': True,
        'outliers': True,
        'returns': True,
        'look_ahead': True
    }
    cleaned = engine.clean_data(data, options)
    print(f"Cleaned columns: {cleaned.columns.tolist()}")
    
    if 'Daily_Return' in cleaned.columns:
        print("Return conversion successful.")
    
    print("Testing Validation...")
    val = engine.validate_data(cleaned)
    print(f"Validation Status: {val['status']}")
    
    print("Testing Regime Detection...")
    regime = engine.detect_regime(cleaned)
    print(f"Detected Regime: {regime}")
    
    print("Testing Options Fetch...")
    calls, puts = engine.fetch_options(ticker)
    if not calls.empty:
        print(f"Options fetch successful. Calls: {len(calls)}, Puts: {len(puts)}")
    else:
        print("Options fetch returned empty (expected if no market data).")

    print("\nAudit Log Summary:")
    for entry in engine.audit_log:
        print(f"[{entry['action']}] {entry['details']}")

if __name__ == "__main__":
    test_engine()
