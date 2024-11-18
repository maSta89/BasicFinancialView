# import all necessary library
import os
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

ticker_symbol = "KO"
open_price_file = "CocaCola_Open_Prices.xlsx"
close_price_file = "CocaCola_Close_Prices.csv"

# last data in data
def get_last_date(file_path, date_col):
    if os.path.exists(file_path):
        if file_path.endswith(".xlsx"):
            data = pd.read_excel(file_path, sheet_name="Open Prices")
        elif file_path.endswith(".csv"):
            data = pd.read_csv(file_path)
        last_date = pd.to_datetime(data[date_col].iloc[-1])
        return last_date
    return None


last_date = get_last_date(open_price_file, "Date")
if last_date is None:
    start_date = "2022-01-01"
else:
    start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")

# Get the data from online source here

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
new_data['Date'] = new_data['Date'].dt.date



data[['Date', 'Open']].to_excel("CocaCola_Open_Prices.xlsx", sheet_name="Open Prices")



data[['Date', 'Close']].to_csv("CocaCola_Close_Prices.csv", index=False)




# graph block
plt.figure(figsize=(12, 6))
plt.plot(time_series.index, time_series, label="Original Time Series", color="blue")
plt.plot(forecast_index, forecast, label="Forecasted Prices", color="orange", marker='o')
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.title("Stock Price Forecast with ARIMA")
plt.legend()
plt.show()


