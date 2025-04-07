import json
import re
import os

# Load JSON data
with open("INFO/output.json", "r", encoding="utf-8") as file:
    info_data = json.load(file)

# Improved Regex Pattern
transaction_pattern = re.compile(
    r"(\d{2}-\d{2}-\d{4})\s+"     # Date (dd-mm-yyyy)
    r"([\s\S]*?)\s+"              # Particulars (multi-line, non-greedy)
    r"(?:Chq:\s*\d+\s+)?"         # Optional cheque reference
    r"([\d,]+\.\d{2})?\s*"        # Deposits (optional, with commas)
    r"([\d,]+\.\d{2})?\s*"        # Withdrawals (optional, with commas)
    r"([\d,]+\.\d{2})"            # Balance (mandatory, with commas)
)

def extract_transactions(page_content):
    transactions = []
    
    matches = transaction_pattern.findall(page_content)
    for match in matches:
        date, particulars, deposit, withdrawal, balance = match

        transactions.append({
            "Date": date,
            "Particulars": particulars.strip().replace("\n", " "),
            "Deposit": float(deposit.replace(",", "")) if deposit else None,
            "Withdrawal": float(withdrawal.replace(",", "")) if withdrawal else None,
            "Balance": float(balance.replace(",", ""))
        })

    return transactions

def process_all_files(info_data, fileNAme):
    processed_data = {}

    for file_name, pages in info_data.items():
        # Convert list of pages into a single text block
        full_text = " ".join([" ".join(page) if isinstance(page, list) else page for page in pages])

        # Ensure processing starts from where the transaction table begins
        start_idx = full_text.find("Date Particulars Deposits Withdrawals Balance")
        if start_idx == -1:
            continue  # Skip if no transaction table is found

        transactions = extract_transactions(full_text[start_idx:])
        processed_data[file_name] = transactions

    # with open("INFO/processed_output.json", "w", encoding="utf-8") as outfile:
    #     json.dump(processed_data, outfile, indent=4)
    output_file = "INFO/processed_output.json"

    # Load existing data if the file exists
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as infile:
            try:
                existing_data = json.load(infile)
                if not isinstance(existing_data, dict):
                    existing_data = {}  # Ensure it's a dictionary
            except json.JSONDecodeError:
                existing_data = {}  # Handle invalid JSON cases
    else:
        existing_data = {}

    # Append new data to the existing dictionary
    existing_data.update(processed_data)

    # Write the updated data back to the file
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(existing_data, outfile, indent=4)

    return processed_data

if __name__ == "__main__":
   # Run processing
    processed_transactions = process_all_files(info_data)

    # Save processed transactions
    with open("INFO/processed_output.json", "w", encoding="utf-8") as outfile:
        json.dump(processed_transactions, outfile, indent=4)

    print("✅ Processing complete! Transactions saved to INFO/processed_output.json")
