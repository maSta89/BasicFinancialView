# import all necessary library
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os
import sqlite3

from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

ticker_symbol = input("Enter ticker symbol like KO for CocaCola").strip().upper()

database_name = f"{ticker_symbol}_stock_data.db"


def initialize_database(database):
    if not os.path.exists(database):
        print(f"DB file {database} does not exists. Preparing")
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                open_price REAL,
                close_price REAL,
                volume INTEGER
                )
            """)

            connection.commit()
    else:
        print(f"DB {database} is ready")

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


# Get the data from online source ,download the data from Yahoo Finance
data = yf.download(ticker_symbol, start=start_date, end=end_date, interval="1d")
data.columns = data.columns.get_level_values(0)
data = data.dropna(subset=['Open', 'Close'])
data = data.reset_index()
data['Date'] = pd.to_datetime(data['Date']).dt.date

print(data)
print(data.columns)



def insert_stock_data(rawdata):
    for _, row in rawdata.iterrows():
        cursor.execute("""
        INSERT INTO stock_prices (date, open_price, close_price, volume)
        VALUES (?, ?, ?, ?)
        """, (row["Date"], row["Open"], row["Close"], row["Volume"]))
    connection.commit()


insert_stock_data(data)

cursor.close()
connection.close()

# split data into separate files
existing_open_data = pd.read_excel(open_price_file, sheet_name="Open Prices")
combined_open_data = pd.concat([existing_open_data, data[["Date", "Open"]]])
combined_open_data.to_excel(open_price_file, sheet_name="Open Prices", index=False)

existing_close_data = pd.read_csv(close_price_file)
combined_close_data = pd.concat([existing_close_data, data[['Date', 'Close']]])
combined_close_data.to_csv(close_price_file, index=False)

# prediction block
csv_data = pd.read_csv(close_price_file, parse_dates=["Date"])
csv_data.set_index("Date", inplace=True)
time_series = csv_data['Close']  # base data
time_series = time_series.asfreq("B")
prediction_model = ARIMA(time_series, order=(1, 1, 1)).fit()
forecast_steps = 10  # number of predictions
forecast = prediction_model.forecast(steps=forecast_steps)
forecast_index = pd.date_range(start=time_series.index[-1] + pd.Timedelta(days=1), periods=forecast_steps, freq='D')

# graph block
plt.figure(figsize=(12, 6))
plt.plot(time_series.index, time_series, label="Original Time Series", color="blue")
plt.plot(forecast_index, forecast, label="Forecasted Prices", color="orange", marker='o')
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.title("Stock Price Forecast with ARIMA")
plt.legend()
plt.show()
