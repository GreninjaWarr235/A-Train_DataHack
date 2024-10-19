import pandas as pd
import numpy as np
from datetime import datetime
from hijri_converter import convert  # Install using 'pip install hijri-converter'
import holidays  # Install using 'pip install holidays'
from fbprophet import Prophet  # For forecasting, install Prophet using 'pip install prophet'

# Step 1: Load the datasets
swiggy_df = pd.read_csv('swiggy_data.csv')  # Assuming Swiggy dataset is saved as swiggy_data.csv
zomato_df = pd.read_csv('zomato_data.csv')  # Assuming Zomato dataset is saved as zomato_data.csv

# Step 2: Preprocessing
swiggy_df['Invoice_Date_s'] = pd.to_datetime(swiggy_df['Invoice_Date_s'])
zomato_df['Invoice_Date_z'] = pd.to_datetime(zomato_df['Invoice_Date_z'])

# Merge Swiggy and Zomato datasets
combined_df = pd.concat([swiggy_df[['Invoice_Date_s', 'Total_s']].rename(columns={'Invoice_Date_s': 'Date', 'Total_s': 'Sales'}),
                         zomato_df[['Invoice_Date_z', 'Total_z']].rename(columns={'Invoice_Date_z': 'Date', 'Total_z': 'Sales'})])

combined_df['Date'] = pd.to_datetime(combined_df['Date'])
combined_df = combined_df.groupby('Date')['Sales'].sum().reset_index()  # Aggregate sales by date

# Step 3: Add Gregorian, Hindu, and Islamic calendar features
# Add Gregorian calendar features
combined_df['Gregorian_Month'] = combined_df['Date'].dt.month
combined_df['Gregorian_Weekday'] = combined_df['Date'].dt.weekday

# Add Hindu festival features (using holidays package for India)
india_holidays = holidays.India()
combined_df['Is_Hindu_Festival'] = combined_df['Date'].apply(lambda x: 1 if x in india_holidays else 0)

# Add Islamic festival features using Hijri calendar conversion
def is_islamic_festival(date):
    hijri_date = convert.Gregorian(date.year, date.month, date.day).to_hijri()
    # Example: Eid dates (simple check based on common Hijri dates for Eid al-Fitr and Eid al-Adha)
    eid_fitr_dates = [(10, 1)]  # Eid al-Fitr is on 1st of Shawwal
    eid_adha_dates = [(12, 10)]  # Eid al-Adha is on 10th of Dhu al-Hijjah
    return 1 if (hijri_date.month, hijri_date.day) in eid_fitr_dates or (hijri_date.month, hijri_date.day) in eid_adha_dates else 0

combined_df['Is_Islamic_Festival'] = combined_df['Date'].apply(is_islamic_festival)

# Step 4: Model Building - Prophet for time series forecasting
# Prophet expects columns 'ds' for date and 'y' for the value to predict
df_prophet = combined_df.rename(columns={'Date': 'ds', 'Sales': 'y'})

# Instantiate the model
model = Prophet()

# Add special days as holidays
# You can define your own holidays based on Hindu and Islamic festivals
holidays_df = pd.DataFrame({
    'holiday': 'festival',
    'ds': pd.to_datetime([
        '2024-04-10',  # Example: Hindu festival
        '2024-05-24',  # Example: Eid festival
    ]),
    'lower_window': 0,
    'upper_window': 1,
})
model.add_country_holidays(country_name='IN')  # For Hindu festivals (India)
model.add_regressor('Gregorian_Month')
model.add_regressor('Is_Hindu_Festival')
model.add_regressor('Is_Islamic_Festival')

# Fit the model
model.fit(df_prophet)

# Step 5: Make future predictions
future_dates = model.make_future_dataframe(periods=365)  # Predict for the next 1 year
future_dates['Gregorian_Month'] = future_dates['ds'].dt.month
future_dates['Is_Hindu_Festival'] = future_dates['ds'].apply(lambda x: 1 if x in india_holidays else 0)
future_dates['Is_Islamic_Festival'] = future_dates['ds'].apply(is_islamic_festival)

# Predict
forecast = model.predict(future_dates)

# Step 6: Plot results
model.plot(forecast)
