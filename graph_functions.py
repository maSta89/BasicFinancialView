import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def db_data(database):
    with sqlite3.connect(database) as connection:
        query = "SELECT date, open_price, close_price, volume FROM stock_prices ORDER BY date"
        data = pd.read_sql_query(query, connection)
    return data


def visualize_stock_data(data):
    data["date"] = pd.to_datetime(data["date"])
    plt.figure(figsize=(12, 6))

    plt.plot(data['date'], data['open_price'], label="Open price", color="blue", marker="o")
    plt.plot(data['date'], data['close_price'], label='Close Price', color='red', marker='x')

    plt.title("Stock Prices Over Time", fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)

    plt.tight_layout()
    plt.show()
