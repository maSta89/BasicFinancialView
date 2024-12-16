import yfinance as yf
import pandas as pd
import sqlite3
import os

from datetime import datetime, timedelta


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


def store_yahoo_data(database, tickersymbol, startdate, enddate):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT date FROM stock_prices ORDER BY date asc
    """)
    existing_dates = {datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()}

    if existing_dates:
        start_date_obj = startdate
        end_date_obj = enddate

        missing_start_date = start_date_obj
        while missing_start_date in existing_dates:
            missing_start_date += timedelta(days=1)

        if missing_start_date > end_date_obj:
            print("All data is up to date.")
            cursor.close()
            connection.close()

        startdate = missing_start_date
    get_yahoo_data(tickersymbol, startdate, enddate, database)


def get_yahoo_data(tickersymbol, startdate, enddate, database):
    # Get the data from online source ,download the data from Yahoo Finance
    data = yf.download(tickersymbol, start=startdate, end=enddate, interval="1d")
    data.columns = data.columns.get_level_values(0)
    data = data.dropna(subset=['Open', 'Close'])
    # data = data.reset_index()
    # data['Date'] = pd.to_datetime(data['Date']).dt.date
    data.index = pd.to_datetime(data.index).dt.date
    print(data)
    print(data.columns)
    insert_stock_data(database, data)
    return data


def insert_stock_data(database, rawdata):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("""SELECT date FROM stock_prices""")
        existing_dates = {row[0] for row in cursor.fetchall()}

        new_data = rawdata[~rawdata["Date"].isin(existing_dates)]

        for date, row in new_data.iterrows():
            cursor.execute("""
            INSERT INTO stock_prices (date, open_price, close_price, volume)
            VALUES (?, ?, ?, ?)
            """, (date, row["Open"], row["Close"], row["Volume"]))
        connection.commit()
