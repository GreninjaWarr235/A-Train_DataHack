import pandas as pd
import numpy as np
import holidays
from hijri_converter import convert
from convertdate import indian_civil
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

def load_data(swiggy_file_path, zomato_file_path):
    """ Load Swiggy and Zomato datasets from CSV files """
    swiggy_data = pd.read_csv(swiggy_file_path)
    zomato_data = pd.read_csv(zomato_file_path)

    # Convert date columns to datetime
    swiggy_data['Date_s'] = pd.to_datetime(swiggy_data['Date_s'])
    zomato_data['Date_z'] = pd.to_datetime(zomato_data['Date_z'])

    # Rename Zomato columns to match Swiggy
    zomato_data = zomato_data.rename(columns={'Date_z': 'Date_s', 'Total_z': 'Total_s'})

    # Combine Swiggy and Zomato data
    combined_data = pd.concat([swiggy_data[['Date_s', 'Total_s']], zomato_data[['Date_s', 'Total_s']]])

    # Handle missing values
    combined_data.fillna(0, inplace=True)
    combined_data = combined_data.sort_values(by='Date_s')

    return combined_data

def add_calendar_features(data):
    """ Add Gregorian, Islamic, Hindu calendar features and holiday information """
    data['gregorian_year'] = data['Date_s'].dt.year
    data['gregorian_month'] = data['Date_s'].dt.month
    data['gregorian_day'] = data['Date_s'].dt.day
    data['day_of_week'] = data['Date_s'].dt.dayofweek

    # Islamic Calendar
    data['islamic_date'] = data['Date_s'].apply(lambda x: convert.Gregorian(x.year, x.month, x.day).to_hijri())
    data['islamic_year'] = data['islamic_date'].apply(lambda x: x.year)
    data['islamic_month'] = data['islamic_date'].apply(lambda x: x.month)
    data['islamic_day'] = data['islamic_date'].apply(lambda x: x.day)

    # Hindu Calendar
    data['hindu_date'] = data['Date_s'].apply(lambda x: indian_civil.from_gregorian(x.year, x.month, x.day))
    data['hindu_year'] = data['hindu_date'].apply(lambda x: x[0])
    data['hindu_month'] = data['hindu_date'].apply(lambda x: x[1])
    data['hindu_day'] = data['hindu_date'].apply(lambda x: x[2])

    # Indian holidays
    india_holidays = holidays.India()
    data['is_holiday'] = data['Date_s'].apply(lambda x: 1 if x in india_holidays else 0)

    return data

def train_model(X, y):
    """ Train a RandomForestRegressor model on the data """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, X_test, y_test

def predict_future_sales(model, future_days=30):
    """ Predict sales for future dates """
    # Generate future dates
    future_dates = pd.date_range(start=pd.Timestamp.today(), periods=future_days, freq='D')

    # Create DataFrame for future dates
    future_df = pd.DataFrame({'Date_s': future_dates})
    
    # Add calendar features
    future_df = add_calendar_features(future_df)

    # Select features
    X_future = future_df[['gregorian_year', 'gregorian_month', 'gregorian_day', 'day_of_week',
                          'islamic_year', 'islamic_month', 'islamic_day',
                          'hindu_year', 'hindu_month', 'hindu_day', 'is_holiday']]

    # Make predictions
    future_predictions = model.predict(X_future)

    return future_df['Date_s'], future_predictions

def plot_predictions(dates, predictions, title="Predicted Sales"):
    """ Plot predictions """
    plt.figure(figsize=(12, 6))
    plt.plot(dates, predictions, label="Predicted Sales", color='green', marker='o')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Predicted Sales")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main(swiggy_file_path, zomato_file_path, future_days=30):
    # Load and preprocess data
    data = load_data(swiggy_file_path, zomato_file_path)
    data = add_calendar_features(data)

    # Define features and target
    X = data[['gregorian_year', 'gregorian_month', 'gregorian_day', 'day_of_week',
              'islamic_year', 'islamic_month', 'islamic_day',
              'hindu_year', 'hindu_month', 'hindu_day', 'is_holiday']]
    y = data['Total_s']

    # Train the model
    model, _, _ = train_model(X, y)

    # Predict future sales
    future_dates, future_predictions = predict_future_sales(model, future_days=future_days)

    # Plot future sales predictions
    plot_predictions(future_dates, future_predictions, title="Future Sales Prediction")

# Example usage: Call main function with file paths and desired future days to predict
swiggy_file_path = 'PS_DATA\Prepared from Raw\SWIGGY_MASTERDATA.csv'  # Replace with actual path
zomato_file_path = 'PS_DATA\Prepared from Raw\ZOMATO_MASTERDATA.csv'  # Replace with actual path
future_days_to_predict = 30  # Number of future days to predict

main(swiggy_file_path, zomato_file_path, future_days=future_days_to_predict)
