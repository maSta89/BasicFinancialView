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
                date DATE PRIMARY KEY,
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

    data = data.reset_index()
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.set_index('Date')
    # data.index = data.index.date
    # data.index = data.index.map(lambda x: x.date())

    print(data.index)
    print(type(data.index[0]))
    # print(data.columns)

    insert_stock_data(database, data)
    return data


def insert_stock_data(database, rawdata):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("""SELECT date FROM stock_prices""")
        existing_dates = {datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()}
        # firstitem = next(iter(existing_dates))
        # print(type(firstitem))

        print(rawdata.index)
        print("Columns:", rawdata.columns)

        if not isinstance(rawdata.index, pd.DatetimeIndex):
            raise ValueError("rawdata.index must be a DatetimeIndex for proper date handling.")

        rawdata.index = rawdata.index.map(lambda x: x.date())

        print(f"rawdata.index type: {type(rawdata.index)}")

        new_data = rawdata[~rawdata.index.isin(existing_dates)]
        new_data = new_data.sort_index()
        # print(type(next(iter(rawdata.index))))

        for date, row in new_data.iterrows():
            cursor.execute("""
            INSERT INTO stock_prices (date, open_price, close_price, volume)
            VALUES (?, ?, ?, ?)
            """, (date, row["Open"], row["Close"], row["Volume"]))
        connection.commit()

        print(f"this a data inserted in DB {new_data}")


def print_table_content(database, table_name):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        # Fetch all rows from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [description[0] for description in cursor.description]

        # Print column names
        print(" | ".join(column_names))
        print("-" * (len(" | ".join(column_names)) + 5))

        # Print each row
        for row in rows:
            print(" | ".join(map(str, row)))

