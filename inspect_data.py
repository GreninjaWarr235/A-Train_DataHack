import os
import pandas as pd

# Define directories
RAW_DATA_DIR = './PS_DATA/Raw'

def load_data(data_dir):
    """Load raw data from directory."""
    data_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.csv')]
    dataframes = [pd.read_csv(file) for file in data_files]
    return pd.concat(dataframes, ignore_index=True)

def inspect_data(df):
    """Inspect data to understand its structure."""
    print("Columns in the dataset:")
    print(df.columns)
    print("\nSample data:")
    print(df.head())
    print("\nData types of columns:")
    print(df.dtypes)
    print("\nSummary statistics:")
    print(df.describe(include='all'))

def main():
    # Load raw data
    raw_data = load_data(RAW_DATA_DIR)
    print("Data loaded successfully.")
    
    # Inspect data
    inspect_data(raw_data)

if __name__ == '__main__':
    main()
