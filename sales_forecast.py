import os
import pandas as pd
from prophet import Prophet
from hijri_converter import convert as hijri_convert
import numpy as np

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
                if not temp_df.empty:  # Check if DataFrame is not empty before concatenation
                    df = pd.concat([df, temp_df], ignore_index=True)
    return df

# Load sales data
sales_data = load_sales_data(os.path.join(DATA_DIR, 'Output Ref/Sales'))

# Check the structure of the loaded data
print("Loaded Sales Data:")
print(sales_data.head())

# Check if 'Date' and 'Total_Sales' columns are present
required_columns = ['Date', 'Total_Sales']
for column in required_columns:
    if column not in sales_data.columns:
        raise KeyError(f"Missing required column: {column}")

# Convert 'Date' column to datetime
sales_data['Date'] = pd.to_datetime(sales_data['Date'], errors='coerce')

# Check for NaT values after conversion
if sales_data['Date'].isnull().any():
    print("Warning: Some dates could not be converted. These rows will be dropped.")
    print(sales_data[sales_data['Date'].isnull()])

# Function to convert Gregorian date to Islamic (Hijri) date
def convert_to_hijri(date):
    if pd.isnull(date):  # Check for invalid dates
        return np.nan  # Return NaN for invalid dates
    try:
        # Ensure the date is in a reasonable range
        hijri_date = hijri_convert.Gregorian(int(date.year), int(date.month), int(date.day)).to_hijri()
        return f"{hijri_date.year}-{hijri_date.month}-{hijri_date.day}"
    except Exception as e:
        print(f"Error converting date {date}: {e}")
        return np.nan  # Return NaN if there's an error in conversion

# Prepare forecast data for different calendar systems
# Function to prepare forecast data for different calendar systems
def prepare_forecast_data(sales_df, calendar='gregorian'):
    # Convert the Date column
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')

    # Remove rows where the date conversion resulted in NaT (Not a Time)
    sales_df = sales_df.dropna(subset=['Date'])

    # Filter for valid dates within a specific range
    min_date = pd.Timestamp('1900-01-01')  # Set a minimum valid date
    max_date = pd.Timestamp('2100-12-31')  # Set a maximum valid date
    sales_df = sales_df[(sales_df['Date'] >= min_date) & (sales_df['Date'] <= max_date)]

    if sales_df.empty:
        print("Warning: No valid data available for forecasting.")
        return pd.DataFrame(columns=['ds', 'y'])  # Return an empty DataFrame

    # Group the data by date and sum the sales
    forecast_data = sales_df[['Date', 'Total_Sales']].groupby('Date').sum().reset_index()
    forecast_data.columns = ['ds', 'y']  # Prophet requires 'ds' (date) and 'y' (sales) columns
    return forecast_data

print("Original Date Values:")
print(sales_data['Date'].head(10))  # Print the first 10 values


# Function to train and predict using Prophet
def forecast_sales(forecast_data, periods=30):
    if forecast_data.empty:
        print("No data available for forecasting.")
        return None

    model = Prophet()
    model.fit(forecast_data)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

# Prepare Gregorian forecast data
gregorian_forecast_data = prepare_forecast_data(sales_data, calendar='gregorian')
gregorian_forecast = forecast_sales(gregorian_forecast_data)

# Prepare Islamic (Hijri) forecast data
islamic_forecast_data = prepare_forecast_data(sales_data, calendar='islamic')
islamic_forecast = forecast_sales(islamic_forecast_data)

# Print the last 5 predictions for each calendar system
if gregorian_forecast is not None:
    print("Gregorian Calendar Forecast:")
    print(gregorian_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

if islamic_forecast is not None:
    print("\nIslamic Calendar Forecast:")
    print(islamic_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
