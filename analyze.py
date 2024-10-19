import os
import pandas as pd

# Define directories
RAW_DATA_DIR = './PS_DATA/Raw'

def load_data(data_dir):
    """Load raw data from directory."""
    data_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.csv')]
    dataframes = [pd.read_csv(file, low_memory=False) for file in data_files]
    return pd.concat(dataframes, ignore_index=True)

def analyze_columns(df):
    """Analyze columns to understand potential target choices."""
    for col in df.columns:
        unique_values = df[col].nunique()
        print(f"Column: {col}, Unique Values: {unique_values}")
        if unique_values < 20:  # If fewer than 20 unique values, display them
            print(f"Sample values for {col}: {df[col].unique()[:10]}")
        print("-" * 50)

def main():
    # Load raw data
    raw_data = load_data(RAW_DATA_DIR)
    print("Data loaded successfully.")
    
    # Analyze columns
    analyze_columns(raw_data)

if __name__ == '__main__':
    main()



