#import all necessary library
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

# Get the data from online source here
ticker_symbol = "KO"
data = yf.download(ticker_symbol, start="2022-01-01", end="2024-01-01", interval="1d")
data = data.asfreq('D')
#print(data.columns)
data[['Open', 'Close']] = data[['Open', 'Close']].ffill()  # missing values added to ensure daily frequency
#print(data)


# prediction block
time_series = data['Close'] # base data
prediction_model = ARIMA(time_series, order=(1, 1, 1)).fit()
forecast_steps = 10 # number of predictions
forecast = prediction_model.forecast(steps=forecast_steps)
forecast_index = pd.date_range(start=time_series.index[-1] + pd.Timedelta(days=1), periods=forecast_steps, freq='D')

# split data into separate files
data = data.reset_index()
data['Date'] = data['Date'].dt.date
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

