#import all necessary library
import yfinance as yf
import matplotlib.pyplot as plt

# Get the data from online source here
ticker_symbol = "KO"
data = yf.download(ticker_symbol, start="2022-01-01", end="2024-01-01")

print(data.head())

closing_prices = data["Close"]

# graph block

plt.figure(figsize=(15,5))
plt.plot(closing_prices, label="Closing prices")
plt.title(f"{ticker_symbol} Stock closing prices")
plt.xlabel("Date")
plt.ylabel("Prices")
plt.legend()
plt.show()
