# import all necessary library
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os
import sqlite3

from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

ticker_symbol = input("Enter ticker symbol like KO for CocaCola").strip().upper()
open_price_file = f"{ticker_symbol}_Open_Prices.xlsx"
close_price_file = f"{ticker_symbol}_Close_Prices.csv"

#  set up empty files for data
if not os.path.exists(open_price_file):
    pd.DataFrame(columns=["Date", "Open"]).to_excel(open_price_file, sheet_name="Open Prices", index=False)

if not os.path.exists(close_price_file):
    pd.DataFrame(columns=["Date", "Close"]).to_csv(close_price_file, index=False)


# check for last date in file
def get_last_date(file_path, date_col):
    file_data = None
    if os.path.exists(file_path):
        if file_path.endswith(".xlsx"):
            file_data = pd.read_excel(file_path, sheet_name="Open Prices")
        # Check if the file is not empty
        if not file_data.empty:
            bottom_date = pd.to_datetime(file_data[date_col].iloc[-1])
            return bottom_date
    return None


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

last_date = get_last_date(open_price_file, "Date")
if last_date is None:
    start_date = default_start  # Default start date if no data exists
else:
    start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")  # Start from the day after the last recorded date

# Get the data from online source ,download the data from Yahoo Finance
data = yf.download(ticker_symbol, start=start_date, end=end_date, interval="1d")
data.columns = data.columns.get_level_values(0)
data = data.dropna(subset=['Open', 'Close'])
data = data.reset_index()
data['Date'] = pd.to_datetime(data['Date']).dt.date

print(data)
print(data.columns)

database_name = f"{ticker_symbol}_stock_data.db"
connection = sqlite3.connect(database_name)
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
