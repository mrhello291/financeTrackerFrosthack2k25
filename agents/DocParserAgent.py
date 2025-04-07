import os
import re
import json
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from uagents import Agent, Context, Model
from utils.DocToGDrive import grivePipe
from utils.asiChat import llmChat


#############################################
# Step 1: PDF Parsing (per page)
#############################################
def process_pdf_file(file_path):
    """Load a PDF and return a list of page texts."""
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    # Return each page's text as an element in a list.
    pages_text = [page.page_content for page in pages]
    return pages_text

#############################################
# Step 2: LLM Extraction of Transaction Table per Page
#############################################
def extract_transactions_from_page(page_text):
    """
    Send a single page's text to the LLM to extract any transaction data.
    The LLM is expected to return a JSON array of transaction objects with keys:
    Date, Particulars, Deposit, Withdrawal, and Balance.
    Transactions without a valid date should be ignored.
    """
    prompt = """
You are an assistant that extracts transaction data from a financial document page input.
The page may contain transactions presented in a table.
Please extract all transactions that have a valid date (format dd-mm-yyyy) and output a JSON array of objects.
Please go over all the text in the page and extract all transactions.
Each object must contain exactly the following keys:
- "Date": (string in dd-mm-yyyy format)
- "Particulars": (string describing the transaction; if missing, use an empty string)
- "Deposit": (a number or null if missing)
- "Withdrawal": (a number or null if missing)
- "Balance": (a number or null if missing)

Ignore any transaction that does not have a valid date. Don't confuse 0.0 with null.
Return ONLY a valid JSON array. No commentary or code blocks.

If the page does not contain any transactions, return an empty JSON array.
"""
    response = llmChat([
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"Page text:\n {page_text}"}
                        ],
                       temperature=0.2,
                       max_tokens=10000)
    try:
        res = json.loads(response)["choices"][0]["message"]["content"]
        json_text_match = re.search(r"```json\n(.*?)```", res, re.DOTALL)
        json_text = json_text_match.group(1) if json_text_match else response

        transactions = json.loads(json_text)

        # Replace None with math.nan in numeric fields
        for txn in transactions:
            for field in ["Deposit", "Withdrawal", "Balance"]:
                if txn.get(field) is None:
                    txn[field] = None
        print(transactions)
    except Exception as e:
        print("Error parsing LLM output for page. Using empty transactions. Error:", e)
        transactions = []
    return transactions

# def extract_transaction_table(pages_text):
#     """
#     Process pages in groups of two. For each pair of pages, join their text
#     and call the LLM once. If an odd number of pages exists, the last group will
#     contain only one page.
#     Combine transactions from all groups into a single table.
#     """
#     all_transactions = []
#     num_pages = len(pages_text)
#     i = 0
#     while i < num_pages:
#         if i + 1 < num_pages:
#             joined_text = pages_text[i] + "\n" + pages_text[i+1]
#             print(f"Processing pages {i+1} and {i+2} via LLM...")
#         else:
#             joined_text = pages_text[i]
#             print(f"Processing page {i+1} via LLM...")
#         transactions = extract_transactions_from_page(joined_text)
#         print(f"Extracted {len(transactions)} transactions from pages {i+1} and {i+2}.")
#         print("Transactions:", transactions)
#         if isinstance(transactions, list):
#             all_transactions.extend(transactions)
#         i += 2
#     return all_transactions

def extract_transaction_table(pages_text):
    """
    Process each page individually by calling the LLM to extract transactions.
    Combine the results from all pages into a single table.
    """
    all_transactions = []
    for i, page_text in enumerate(pages_text):
        print(f"Processing page {i+1} via LLM...")
        transactions = extract_transactions_from_page(page_text)
        if isinstance(transactions, list):
            all_transactions.extend(transactions)
    return all_transactions


#############################################
# Step 4: Append the Table into processed_output.json by Month-Year
#############################################
def update_processed_output(table, output_file="INFO/processed_output.json"):
    # Load existing data if the file exists, else start with an empty dict.
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as infile:
                data = json.load(infile)
                if not isinstance(data, dict):
                    data = {}
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    # For each transaction, determine the month and year from the Date field and append.
    for txn in table:
        date_str = txn.get("Date", "")
        try:
            dt = datetime.strptime(date_str, "%d-%m-%Y")
            month_year = dt.strftime("%b-%y")  # e.g., "Dec-24", "Jan-25"
        except Exception:
            continue  # Skip transactions with invalid or missing dates.
        if month_year not in data:
            data[month_year] = []
        data[month_year].append(txn)
        #TODO: Change deposit and withdrawal to float and make sure that they are stored as 'deposited to bank' and 'withdrawn from bank'
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=4)
    print("Processed output updated in", output_file)


#############################################
# Main function tying steps 1-5 together for a PDF file.
#############################################
def process_pdf_and_extract_transactions(file_path):
    print(f"Processing file: {file_path}")
    # Step 1: Parse PDF into pages (each page as a separate text)
    pages_text = process_pdf_file(file_path)
    
    # Step 2: Extract Transaction Table via LLM on each page and combine results.
    transaction_table = extract_transaction_table(pages_text)
    
    # Step 3: (The table is now stored in transaction_table.)
    
    # Step 4: Update processed_output.json by Month-Year
    update_processed_output(transaction_table)
    
    # Step 5: Upload table chunks to Google Drive
    grivePipe(transaction_table)
    
    return transaction_table

#############################################
# Making agent
#############################################

class InputReaderAgentMessage(Model):
    message: str

class InputReaderAgentMessageResponse(Model):
    ftd: list

InputReaderParseAgent = Agent(name="InputReaderAgent", seed="InputReaderAgent recovery phrase", port=8002, mailbox=True)

@InputReaderParseAgent.on_rest_post("/parse",InputReaderAgentMessage,InputReaderAgentMessageResponse)
async def input_reader_agent(ctx: Context, message: InputReaderAgentMessage) -> InputReaderAgentMessageResponse:
    """
    Handles the input reader agent's message.
    
    This agent processes the given PDF file by:
      1. Parsing the PDF into pages.
      2. Extracting the transaction table via LLM (one call per page).
      3. Combining transactions from all pages.
      4. Updating the processed_output.json by Month-Year.
      5. Uploading transaction table chunks to Google Drive.
    
    Args:
        ctx (Context): The context of the agent.
        message (InputReaderAgentMessage): The message containing the filename to process.
    
    Returns:
        InputReaderAgentMessageResponse: The response containing the processed transaction data.
    """
    
    print("\n ------Parsing the input---------. \n")
    
    # Assume message.message contains the filename to process
    file_name = message.message
    file_path = os.path.join("INFO/data", file_name)
    
    # Call the unified function that processes the PDF and does all steps.
    ftd = process_pdf_and_extract_transactions(file_path)
    
    print("\n ------Parsed the input successfully---------. \n")
    print(InputReaderParseAgent.address)
    
    return InputReaderAgentMessageResponse(ftd=ftd)


#############################################
# Example usage: Process all PDFs in a folder.
#############################################
if __name__ == "__main__":
    InputReaderParseAgent.run()
    # pdf_folder = "INFO/data"
    # for filename in os.listdir(pdf_folder):
    #     if filename.lower().endswith(".pdf"):
    #         file_path = os.path.join(pdf_folder, filename)
    #         process_pdf_and_extract_transactions(file_path)
    # print("All PDFs processed.")
    
    
