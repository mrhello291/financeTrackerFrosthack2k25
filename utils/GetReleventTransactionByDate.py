import json
import re
from datetime import datetime

with open("INFO/processed_output.json", "r") as file:
        database = json.load(file)

def get_filtered_transactions(key, start_date, end_date):
    """
    Filters transactions based on the given key (filename), start_date, and end_date.

    Parameters:
        key (str): The filename associated with the transactions (e.g., "mar_2023.pdf").
        start_date (str): The start date in "DD-MM-YYYY" format.
        end_date (str): The end date in "DD-MM-YYYY" format.
        database (dict): Dictionary containing transaction data.

    Returns:
        list: Filtered transactions within the given date range.
    """
    try:
        start_dt = datetime.strptime(start_date, "%d-%m-%Y")
        end_dt = datetime.strptime(end_date, "%d-%m-%Y")

        if key in database:
            transactions = database[key]

            filtered_transactions = [
                txn for txn in transactions
                if start_dt <= datetime.strptime(txn["Date"], "%d-%m-%Y") <= end_dt
            ]
            return filtered_transactions
        else:
            print(f"⚠️ No transactions found for {key}")
            return []
    except ValueError as e:
        print(f"❌ Error: Invalid date format. {e}")
        return []
