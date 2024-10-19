import os
import pandas as pd

# Define the path to the dataset
DATA_DIR = './PS_DATA/'

# Function to read CSV files from different folders
def load_data(file_path):
    df = pd.DataFrame()
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                temp_df = pd.read_csv(file_path)
                df = pd.concat([df, temp_df], ignore_index=True)
    return df

# Load data from each category
aggregators_data = load_data(os.path.join(DATA_DIR, 'Output Ref/Aggregators'))
inventory_data = load_data(os.path.join(DATA_DIR, 'Output Ref/Inventory'))
department_data = load_data(os.path.join(DATA_DIR, 'Output Ref/Departments'))
sales_data = load_data(os.path.join(DATA_DIR, 'Output Ref/Sales'))

# View the data structure for each dataset
print("Aggregators Data:", aggregators_data.head())
print("Inventory Data:", inventory_data.head())
print("Department Data:", department_data.head())
print("Sales Data:", sales_data.head())
