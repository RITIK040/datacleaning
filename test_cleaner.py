import pandas as pd
import numpy as np
from cleaner_engine import DataCleaner

def test_cleaner():
    # Create "dirty" synthetic data
    data = {
        'Order ID': [101, 102, 101, 104, 105], # Duplicate 101
        'Order Date': ['2023-01-01', '2023-01-02', '2023-01-01', 'invalid', '2023-01-05'],
        'Price ': [100.0, 150.0, 100.0, 5000.0, np.nan], # Outlier 5000, NaN, trailing space
        'Category': ['Electronics', 'electronics', 'Electronics', 'N/A', 'Books'] # Case inconsistency, N/A
    }
    df_raw = pd.DataFrame(data)
    
    cleaner = DataCleaner()
    df_clean = cleaner.clean(df_raw)
    
    # Assertions
    print("Testing Cleaning Pipeline...")
    
    # 1. Column names
    assert 'order_id' in df_clean.columns
    assert 'price' in df_clean.columns
    
    # 2. Duplicates
    assert len(df_clean) == 4
    
    # 3. Missing values
    assert df_clean['price'].isnull().sum() == 0
    assert (df_clean['category_electronics'] == 1).sum() >= 1 # One-hot encoding check
    
    # 4. Outliers (5000 should be replaced by median)
    assert df_clean['price'].max() < 1000
    
    # 5. Text cleaning
    # Category was electronics -> Electronics (title) -> One-hot encoded
    # If it's one-hot encoded, we check the columns
    print("Columns after cleaning:", df_clean.columns.tolist())
    
    print("✅ All automated tests passed!")

if __name__ == "__main__":
    test_cleaner()
