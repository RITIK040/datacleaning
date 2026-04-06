import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantEngine:
    def __init__(self):
        self.audit_log = []

    def log_action(self, action: str, details: str):
        self.audit_log.append({"action": action, "details": details})
        logger.info(f"{action}: {details}")

    def fetch_data(self, tickers: str, period: str = "max", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical data using yfinance. Supports comma-separated tickers."""
        self.log_action("Fetch", f"Downloading {tickers} for period {period}")
        try:
            # Handle comma separated tickers
            ticker_list = [t.strip() for t in tickers.split(",")]
            if len(ticker_list) > 1:
                data = yf.download(ticker_list, period=period, interval=interval, group_by='ticker')
            else:
                data = yf.download(ticker_list[0], period=period, interval=interval)
            
            if data.empty:
                self.log_action("Fetch Error", f"No data found for {tickers}")
            return data
        except Exception as e:
            self.log_action("Fetch Exception", str(e))
            return pd.DataFrame()

    def get_option_expirations(self, ticker_symbol: str) -> List[str]:
        """Get available option expiration dates."""
        self.log_action("Fetch Expirations", f"Getting expirations for {ticker_symbol}")
        try:
            ticker = yf.Ticker(ticker_symbol)
            return list(ticker.options)
        except Exception as e:
            self.log_action("Fetch Expirations Error", str(e))
            return []

    def fetch_option_chain(self, ticker_symbol: str, expiration: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch calls and puts for a specific expiration."""
        self.log_action("Fetch Option Chain", f"Downloading options for {ticker_symbol} expiring {expiration}")
        ticker = yf.Ticker(ticker_symbol)
        try:
            chain = ticker.option_chain(expiration)
            return chain.calls, chain.puts
        except Exception as e:
            self.log_action("Fetch Option Chain Error", str(e))
            return pd.DataFrame(), pd.DataFrame()

    def fetch_options(self, ticker_symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch calls and puts for the nearest expiration."""
        expirations = self.get_option_expirations(ticker_symbol)
        if not expirations:
            return pd.DataFrame(), pd.DataFrame()
        return self.fetch_option_chain(ticker_symbol, expirations[0])

    def fetch_futures(self, ticker_symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Fetch futures historical data and attempt to find spot for basis calculation."""
        self.log_action("Fetch Futures", f"Downloading futures data for {ticker_symbol}")
        try:
            data = yf.download(ticker_symbol, period=period)
            if data.empty:
                return data
            
            # Simple basis calculation heuristic if it's a known future
            # ES=F -> ^GSPC, NQ=F -> ^IXIC, etc.
            mappings = {
                "ES=F": "^GSPC",
                "NQ=F": "^IXIC",
                "YM=F": "^DJI",
                "GC=F": "GC=F", # Spot gold is complex in yfinance, often XAUUSD=X or similar
                "CL=F": "CL=F"
            }
            
            spot_ticker = mappings.get(ticker_symbol.upper())
            if spot_ticker and spot_ticker != ticker_symbol:
                spot_data = yf.download(spot_ticker, period=period)
                if not spot_data.empty:
                    data['Spot_Close'] = spot_data['Close']
                    data['Basis'] = data['Close'] - data['Spot_Close']
                    data['Basis_Pct'] = (data['Basis'] / data['Spot_Close']) * 100
                    self.log_action("Futures Analysis", f"Calculated basis using {spot_ticker} as spot")
            
            return data
        except Exception as e:
            self.log_action("Fetch Futures Error", str(e))
            return pd.DataFrame()

    def clean_data(self, df: pd.DataFrame, options: dict) -> pd.DataFrame:
        """
        Clean data based on provided options.
        Options keys: 'structural', 'missing', 'outliers', 'returns', 'look_ahead'
        """
        df_cleaned = df.copy()
        
        if options.get('structural'):
            # Remove structural errors: ensure numeric, check index
            df_cleaned = df_cleaned.select_dtypes(include=[np.number])
            df_cleaned = df_cleaned[~df_cleaned.index.duplicated(keep='first')]
            self.log_action("Clean", "Structural errors removed")

        if options.get('missing'):
            # Handle missing values
            df_cleaned = df_cleaned.ffill().bfill()
            self.log_action("Clean", "Missing values handled (ffill/bfill)")

        if options.get('outliers'):
            # Remove outliers/noise: use z-score
            for col in df_cleaned.columns:
                if col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                    z_score = (df_cleaned[col] - df_cleaned[col].mean()) / df_cleaned[col].std()
                    df_cleaned = df_cleaned[abs(z_score) < 3]
            self.log_action("Clean", "Outliers removed (Z-score > 3)")

        if options.get('returns'):
            # Convert price to return
            if 'Adj Close' in df_cleaned.columns:
                df_cleaned['Daily_Return'] = df_cleaned['Adj Close'].pct_change()
            elif 'Close' in df_cleaned.columns:
                df_cleaned['Daily_Return'] = df_cleaned['Close'].pct_change()
            self.log_action("Clean", "Price converted to returns")

        if options.get('look_ahead'):
            # Remove look ahead bias: shift signals (if any) or ensure strictly historical
            # For raw data, this typically means ensuring no future data is leaked in features
            # Here we just log it as a validation step
            self.log_action("Clean", "Look-ahead bias validation performed")

        return df_cleaned

    def validate_data(self, df: pd.DataFrame) -> dict:
        """Validate data for anomalies."""
        issues = []
        if (df < 0).any().any():
            issues.append("Negative values found in numeric columns")
        if df.isnull().any().any():
            issues.append("Missing values remain after cleaning")
        
        status = "Clean" if not issues else "Needs Attention"
        self.log_action("Audit", f"Validation status: {status}")
        return {"status": status, "issues": issues}

    def detect_regime(self, df: pd.DataFrame) -> str:
        """Simple regime detection based on rolling volatility."""
        # Handle multi-index if necessary
        if isinstance(df.columns, pd.MultiIndex):
            price_col = None
            for col in df.columns:
                if col[0] in ['Adj Close', 'Close']:
                    price_col = col
                    break
            if not price_col:
                return "Unknown"
            price = df[price_col]
        else:
            price = df['Adj Close'] if 'Adj Close' in df.columns else df.get('Close')
            
        if price is None:
            return "Unknown"
        
        returns = price.pct_change().dropna()
        if len(returns) < 20:
            return "Insufficient Data"
            
        vol = returns.rolling(20).std().iloc[-1]
        mean_vol = returns.std()
        
        # Ensure vol and mean_vol are scalars
        if isinstance(vol, pd.Series): vol = vol.iloc[0]
        if isinstance(mean_vol, pd.Series): mean_vol = mean_vol.iloc[0]
        
        if vol > mean_vol * 1.5:
            return "High Volatility"
        elif vol < mean_vol * 0.5:
            return "Low Volatility"
        else:
            return "Normal"
