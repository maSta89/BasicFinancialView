# import all necessary library
import sqlite3
from datetime import datetime, timedelta
from database_utils import initialize_database, store_yahoo_data
from database_utils import print_table_content
from graph_functions import db_data, visualize_stock_data

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
default_start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")


def date_input(message, date):
    while True:
        print(f"{message} or press Enter to use default:", date)
        user_input = input().strip() or date
        # Validate date format check
        try:
            datetime.strptime(user_input, "%Y-%m-%d")
            return user_input
        except ValueError:
            print(f"Invalid date format. {user_input} Please enter the date in YYYY-MM-DD format.")


start_date = date_input("Enter the start date (YYYY-MM-DD)", default_start)
end_date = date_input("Enter the end date (YYYY-MM-DD)", today)


# Ensure end_date is after start_date
if start_date > end_date:
    raise ValueError("Start date must be earlier than end date.")

store_yahoo_data(database_name, ticker_symbol, start_date, end_date)


data = db_data(database_name)
visualize_stock_data(data)


# table_name = "stock_prices"
# print_table_content(database_name, table_name)




