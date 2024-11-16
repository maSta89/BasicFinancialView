# import all necessary library
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

# Get the data from online source here
ticker_symbol = "KO"
open_price_file = "CocaCola_Open_Prices.xlsx"
close_price_file = "CocaCola_Close_Prices.csv"


def get_last_date(file_path, date_col):
    file_data = None
    if os.path.exists(file_path):
        if file_path.endswith(".xlsx"):
            file_data = pd.read_excel(file_path, sheet_name="Open Prices")
        elif file_path.endswith(".csv"):
            file_data = pd.read_csv(file_path)
        last_day = pd.to_datetime(file_data[date_col].iloc[-1])
        return last_day
    return None


last_date = get_last_date(open_price_file, "Date")
if last_date is None:
    start_date = "2022-01-01"
else:
    start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")

end_date = "2024-01-01"
data = yf.download(ticker_symbol, start=start_date, end=end_date, interval="1d")
data = data.asfreq('D')
# print(data.columns)
data[['Open', 'Close']] = data[['Open', 'Close']].ffill()  # missing values added to ensure daily frequency
# print(data)


# prediction block
time_series = data['Close']  # base data
prediction_model = ARIMA(time_series, order=(1, 1, 1)).fit()
forecast_steps = 10  # number of predictions
forecast = prediction_model.forecast(steps=forecast_steps)
forecast_index = pd.date_range(start=time_series.index[-1] + pd.Timedelta(days=1), periods=forecast_steps, freq='D')

# split data into separate files
new_data = data.reset_index()
new_data['Date'] = data['Date'].dt.date

if os.path.exists(open_price_file):
    existing_open_data = pd.read_excel(open_price_file, sheet_name="Open Prices")
    combined_open_data = pd.concat([existing_open_data, new_data[["Date", "Open"]]])
else:
    combined_open_data = new_data[["Date", "Open"]]

combined_open_data.to_excel("CocaCola_Open_Prices.xlsx", sheet_name="Open Prices")

if os.path.exists(close_price_file):
    existing_close_data = pd.read_csv(close_price_file)
    combined_close_data = pd.concat([existing_close_data, new_data[['Date', 'Close']]])
else:
    combined_close_data = new_data[['Date', 'Close']]

combined_close_data.to_csv(close_price_file, index=False)

# graph block
plt.figure(figsize=(12, 6))
plt.plot(time_series.index, time_series, label="Original Time Series", color="blue")
plt.plot(forecast_index, forecast, label="Forecasted Prices", color="orange", marker='o')
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.title("Stock Price Forecast with ARIMA")
plt.legend()
plt.show()


