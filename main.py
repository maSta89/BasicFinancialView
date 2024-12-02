# import all necessary library
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os
import sqlite3

from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
from database_utils import initialize_database, store_yahoo_data

ticker_symbol = input("Enter ticker symbol like KO for CocaCola").strip().upper()

database_name = f"{ticker_symbol}_stock_data.db"

initialize_database(database_name)


def get_last_date():
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT MAX(date) FROM stock_prices
        """)
        result = cursor.fetchone()
        return result[0] if result[0] else None


# User input for time period
today = datetime.now().strftime("%Y-%m-%d")
default_start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

print("Enter the start date (YYYY-MM-DD) or press Enter to use default:", default_start)
start_date = input().strip() or default_start

print("Enter the end date (YYYY-MM-DD) or press Enter to use today's date:", today)
end_date = input().strip() or today

# Validate date format
try:
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")
except ValueError:
    raise ValueError("Invalid date format. Please enter dates in YYYY-MM-DD format.")

# Ensure end_date is after start_date
if start_date > end_date:
    raise ValueError("Start date must be earlier than end date.")

store_yahoo_data(database_name, ticker_symbol, start_date, end_date)


# prediction block
# csv_data = pd.read_csv(close_price_file, parse_dates=["Date"])
# csv_data.set_index("Date", inplace=True)
# time_series = csv_data['Close']  # base data
# time_series = time_series.asfreq("B")
# prediction_model = ARIMA(time_series, order=(1, 1, 1)).fit()
# forecast_steps = 10  # number of predictions
# forecast = prediction_model.forecast(steps=forecast_steps)
# forecast_index = pd.date_range(start=time_series.index[-1] + pd.Timedelta(days=1), periods=forecast_steps, freq='D')

# graph block
# plt.figure(figsize=(12, 6))
# plt.plot(time_series.index, time_series, label="Original Time Series", color="blue")
# plt.plot(forecast_index, forecast, label="Forecasted Prices", color="orange", marker='o')
# plt.xlabel("Date")
# plt.ylabel("Stock Price")
# plt.title("Stock Price Forecast with ARIMA")
# plt.legend()
# plt.show()
