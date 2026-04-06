import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

class DataCleaner:
    def __init__(self):
        self.scaler = StandardScaler()

    def clean(self, df_raw):
        """
        Applies the professional 11-step cleaning pipeline.
        """
        df = df_raw.copy()

        # 2. Column names
        df.columns = (df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace(r'[^\w]', '', regex=True))

        # 3. Types (Intelligent guessing for specific columns if they exist)
        # We look for date-like or price-like keywords
        for col in df.columns:
            if 'date' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            if any(k in col for k in ['price', 'close', 'open', 'high', 'low']):
                df[col] = pd.to_numeric(df[col], errors='coerce')
            if 'category' in col or 'type' in col:
                 df[col] = df[col].astype('category')

        # 4. Missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['category', 'object']).columns
        
        for col in numeric_cols:
            df[col].fillna(df[col].median(), inplace=True)
        
        for col in categorical_cols:
            if df[col].dtype.name == 'category':
                if 'unknown' not in df[col].cat.categories:
                    df[col] = df[col].cat.add_categories('unknown')
            df[col].fillna('unknown', inplace=True)

        # 5. Duplicates
        id_cols = [c for c in df.columns if 'id' in c]
        if id_cols:
            df = df.drop_duplicates(subset=[id_cols[0]])
        else:
            df = df.drop_duplicates()

        # 6. Text cleaning (Title case and normalize)
        for col in categorical_cols:
            # Convert to string for cleaning regardless of current type
            df[col] = df[col].astype(str).str.strip().str.title()
            df[col] = df[col].replace({'N/A':'Unknown', 'Na':'Unknown', 'Nan':'Unknown', 'Unknown':'Unknown'})
            # Re-convert to category
            df[col] = df[col].astype('category')

        # 7. Outliers (IQR method for all numeric price/volume-like columns)
        for col in numeric_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
            
            # Avoid breaking if IQR is 0 (constant data)
            if IQR > 0:
                df.loc[(df[col] < lower) | (df[col] > upper), col] = np.nan
                df[col].fillna(df[col].median(), inplace=True)

        # 8. Scaling (Price-like columns)
        target_cols = [c for c in numeric_cols if any(k in c for k in ['price', 'close', 'adj_close'])]
        if target_cols:
            df[[f'{c}_scaled' for c in target_cols]] = self.scaler.fit_transform(df[target_cols])

        # 9. Encode categoricals (Only if cardinality is low enough to prevent blowup)
        # For simplicity in this tool, we'll encode columns with < 10 categories
        to_encode = [c for c in categorical_cols if df[c].nunique() < 10]
        if to_encode:
            df = pd.get_dummies(df, columns=to_encode, drop_first=True)

        # 10. Validation (Standard checks)
        # Ensure no nulls left
        for col in df.columns:
            if df[col].isnull().any():
                df[col].fillna(0, inplace=True)

        return df
