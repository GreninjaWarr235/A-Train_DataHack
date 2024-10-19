import os
import pandas as pd

# Define the path to the dataset
DATA_DIR = './PS_DATA/'

# Function to read CSV files from the sales folder
def load_sales_data(file_path):
    df = pd.DataFrame()
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                temp_df = pd.read_csv(file_path)
                df = pd.concat([df, temp_df], ignore_index=True)
    return df

# Load sales data
sales_data = load_sales_data(os.path.join(DATA_DIR, 'Output Ref/Sales'))

# Define thresholds for suspicious activities
LOW_SALES_THRESHOLD = 5000  # Example threshold

# Function to detect low sales
def detect_low_sales(sales_df):
    low_sales = sales_df[sales_df['Total_Sales'] < LOW_SALES_THRESHOLD]
    return low_sales

# Detect low sales
low_sales = detect_low_sales(sales_data)

# Print the detected low sales transactions
print("Low Sales Detected:")
print(low_sales)
