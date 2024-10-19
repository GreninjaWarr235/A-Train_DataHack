import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Define directories
DATA_DIR = './PS_DATA'
RAW_DATA_DIR = os.path.join(DATA_DIR, 'Raw')
PREPARED_DATA_DIR = os.path.join(DATA_DIR, 'Prepared from Raw')
OUTPUT_DIR = os.path.join(DATA_DIR, 'Output Ref')

def load_data(data_dir):
    """Load raw data from directory."""
    data_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.csv')]
    dataframes = [pd.read_csv(file, low_memory=False) for file in data_files]
    return pd.concat(dataframes, ignore_index=True)

def preprocess_data(df):
    """Basic preprocessing to clean and prepare data."""
    # Drop rows where the target is missing
    df = df.dropna(subset=['Order_Status_z'])
    
    # Drop other rows with missing values
    df = df.dropna()
    
    # Convert categorical columns to numeric
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category').cat.codes
    
    return df

def train_model(df):
    """Train a simple model on the processed data."""
    X = df.drop('Order_Status_z', axis=1)  # Replace 'Status' with the actual target column name
    y = df['Order_Status_z']
    
    # Make sure there is a minimum number of samples for the split
    if len(df) < 5:  # Arbitrary threshold, adjust as needed
        print("Not enough data to perform the split.")
        return None
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    return model

def save_output(model, output_dir):
    """Save model or predictions as needed."""
    joblib.dump(model, os.path.join(output_dir, 'model.pkl'))
    print("Model saved!")

def main():
    # Load raw data
    raw_data = load_data(RAW_DATA_DIR)
    print("Data loaded successfully.")
    
    # Preprocess data
    prepared_data = preprocess_data(raw_data)
    print(f"Number of samples after preprocessing: {len(prepared_data)}")
    
    # Proceed if there are enough samples
    if len(prepared_data) > 0:
        # Train model
        model = train_model(prepared_data)
        
        # Save output
        save_output(model, OUTPUT_DIR)
        print("Pipeline completed.")
    else:
        print("No data available for training after preprocessing.")

if __name__ == '__main__':
    main()
