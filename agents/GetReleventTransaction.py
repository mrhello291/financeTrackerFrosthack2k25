from typing import Literal, Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_groq import ChatGroq
# from langchain_huggingface import HuggingFaceEndpoint
# from langchain_community.llms import HuggingFaceEndpoint
from dotenv import load_dotenv, find_dotenv
import os
import json
import re
from datetime import datetime
from uagents import Agent, Bureau, Context, Model
# from langchain_google_genai import ChatGoogleGenerativeAI
from utils.asiChat import llmChat
from utils.DriveJSONRetriever import upload_my_file



load_dotenv(find_dotenv())
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_PROJECT'] = 'advanced-rag'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGSMITH_API_KEY")
# os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
# os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
# os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")


# Function to get relevant transactions based on user query
def get_relevance(user_query: str) -> List[str]:
    """
    Filters transactions based on user query and returns a list containing:
    [relevant key, initial date, final date]
    """
    #TODO: Make this prompt dynamic for current date. Also maybe give this prompt some context from processed output. to give a good date range.
    
    prompt_template = ChatPromptTemplate.from_messages([
    ("system",
        "You have a dictionary containing transactions grouped by months. Keys are in the format 'Jan-25', 'Feb-25', 'May-18' etc. "
        "Each key maps to a list of transactions, each with the fields: 'Date', 'Particulars', 'Deposit', 'Withdrawal', and 'Balance'.\n\n"
        "Transaction example:\n"
        "{{{{\n"
        '  "Date": "01-02-2025",\n'
        '  "Particulars": "UPI/DR/...",\n'
        '  "Deposit": 100.0,\n'
        '  "Withdrawal": null,\n'
        '  "Balance": 13913.0\n'
        "}}}}\n\n"
        "Current year is 2025 and the current month is April. This is for context of current time, if its is required anywhere, otherwise donot use it.\n\n"
        "If user asks for starting date, then take it as 01-01-1999.\n"
        "Instructions:\n"
        "- Based on the user query, extract all relevant date ranges (in **DD-MM-YYYY** format) that cover the transactions of interest. \n"
        "- Consider all transactions in the dictionary and return only the date ranges that are relevant. "
        "- Return the result strictly in JSON with the following format:\n"
        "Output format:\n"
        "{{{{\n"
        '  "date_ranges": [\n'
        '    {{"start": "<earliest_date>", "end": "<latest_date>"}},\n'
        '    ...\n'
        '  ]\n'
        "}}}}"

        "DO NOT include any text outside the JSON."
        # "You have a dictionary containing transactions grouped by months. Keys are in the format 'Jan-25', 'Feb-25', 'May-18' etc. "
        # "Remember Current Year is 2025 and month is april\n\n"
        # "Each key represents a list of transactions corresponding to a specific month and year. The values are lists of transactions, each having the fields: "
        # "'Date', 'Particulars', 'Deposit', 'Withdrawal', and 'Balance'.\n\n"
        # "Example of a transaction:\n"
        # "{{\n"
        # '    "Date": "01-02-2025",\n'
        # '    "Particulars": "UPI/DR/503291190852/PIYUSH KU/PPIW/**86231@FAM/UPI//S BIA261AE17B77646879B30D18 8C204C9B6/01/02/2025 12:49:21",\n'
        # '    "Deposit": 100.0,\n'
        # '    "Withdrawal": null,\n'
        # '    "Balance": 13913.0\n'
        # "}}\n\n"
        # "Instructions:\n"
        # "- Identify the relevant month and year from the user query and return only the matching key (e.g., 'Jan-25').\n"
        # "- Infer the date(s) based on the user's query and return them in the format **DD-MM-YYYY**.\n"
        # "- The response must be **strictly** in JSON format with only the required key and date range.\n"
        # "- The output must contain **nothing else**—no explanations, headers, or extra text.\n\n"
        # "Format the output as:\n"
        # "{{\n"
        # '    "key": "<month-year>",\n'
        # '    "date_range": {{"start": "<earliest_date>", "end": "<latest_date>"}}\n'
        # "}}"
    ),
    ("user", "User query: {query}")
    ])



    
    # model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    # model = HuggingFaceEndpoint(
    # repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",  # ✅ Correct model
    # temperature=0.7,
    # max_length=200
    # )

    # model = ChatGoogleGenerativeAI(
    # model="gemini-2.0-flash",
    # temperature=0,
    # timeout=None,
    # max_retries=2,
    # # other params...
# )
    
    prompt = prompt_template.format_messages(query=user_query)
    # response = model.invoke(prompt)
    response = llmChat(prompt)  # Clean up response
    
    return response

# Example usage
# user_query = "what i did in march this year betweeen 3rd and 5th"
# result = get_relevance(user_query)
# print("Raw result:", result[8:-1])
# print("Type of result:", type(result))

# def get_relevant_transactions(user_query: str):
    # result = get_relevance(user_query)
    
# def get_relevant_transactions(result,database):
#     # res = result["choices"][0]["message"]["content"]
#     # Parse the outer JSON response first
#     try:
#         outer_response = json.loads(result)
#     except json.JSONDecodeError as e:
#         print(f"Error decoding outer JSON: {e}")
#         return []
    
#     try:
#         message_content = outer_response["choices"][0]["message"]["content"]
#     except (KeyError, IndexError) as e:
#         print("Unexpected response structure:", e)
#         return []

#     match = re.search(r'\{.*\}', message_content, re.DOTALL)  # Find JSON inside curly brackets
#     parsed_result = None
#     if match:
#         clean_json = match.group(0)
#         try:
#             parsed_result = json.loads(clean_json)
#         except json.JSONDecodeError as e:
#             print("Error decoding extracted JSON:", e)
#             parsed_result = {"key": "", "date_range": {"start": "", "end": ""}}
#     else:
#         # No valid JSON found: set default empty values
#         print("No valid JSON found in result; using default empty values.")
#         parsed_result = {"key": "", "date_range": {"start": "", "end": ""}}

#     # with open("INFO/processed_output.json", "r") as file:
#     #     database = json.load(file)
#     print(parsed_result)
#     key = parsed_result["key"]  # Example: "mar_2023.pdf"
#     start_date = parsed_result["date_range"]["start"]  # Example: "03-03-2023"
#     end_date = parsed_result["date_range"]["end"]  # Example: "05-03-2023"
    
#     if not key or not start_date or not end_date:
#         print("Missing key or date range in parsed JSON.")
#         return []
    
#     try:
#         start_dt = datetime.strptime(start_date, "%d-%m-%Y")
#         end_dt = datetime.strptime(end_date, "%d-%m-%Y")
#     except Exception as e:
#         print("Error parsing dates:", e)
#         return []
    
#     if key in database:
#         transactions = database[key]
#         filtered_transactions = [
#             txn for txn in transactions
#             if start_dt <= datetime.strptime(txn["Date"], "%d-%m-%Y") <= end_dt
#         ]
#         return filtered_transactions
#     else:
#         print(f"No transactions found for {key}")
#         return []
    # start_dt = datetime.strptime(start_date, "%d-%m-%Y")
    # end_dt = datetime.strptime(end_date, "%d-%m-%Y")
    

    # if key in database:
    #     transactions = database[key]  

    #     filtered_transactions = [
    #         txn for txn in transactions
    #         if start_dt <= datetime.strptime(txn["Date"], "%d-%m-%Y") <= end_dt
    #     ]
    #     # print("Filtered Transactions:", json.dumps(filtered_transactions, indent=4))
    #     return filtered_transactions
    #     # return json.dumps(filtered_transactions, indent=4)
    
    #     # output_file = "INFO/filtered_transactions.json"
    #     # with open(output_file, "w") as file:
    #     #     json.dump(filtered_transactions, file, indent=4)
    #     # print(f"Filtered transactions saved to {output_file}")
        
    # else:
    #     print(f"No transactions found for {key}")

#UPDATED CODE

def get_month_keys_in_range(start_dt: datetime, end_dt: datetime) -> List[str]:
    """Return a list of month keys in the format '%b-%y' from start_dt to end_dt (inclusive)."""
    keys = []
    # Set current to the first day of the start month
    current = datetime(start_dt.year, start_dt.month, 1)
    # Continue until the current month exceeds the end date
    while current <= end_dt:
        keys.append(current.strftime("%b-%y"))
        # Move to the next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
    return keys


def get_relevant_transactions(result: str, database: dict):
    try:
        # If result is not parsed yet
        outer_response = json.loads(result) if isinstance(result, str) else result
        message_content = outer_response["choices"][0]["message"]["content"]
        print(message_content)
    except Exception as e:
        print("Error reading response content:", e)
        return []

    # Extract only the JSON part
    match = re.search(r'\{.*\}', message_content, re.DOTALL)
    if not match:
        print("No valid JSON found.")
        return []
    
    try:
        parsed = json.loads(match.group(0))
        date_ranges = parsed.get("date_ranges") or [parsed.get("date_range")]
        if not date_ranges or date_ranges[0] is None:
            raise ValueError("Missing date ranges.")
    except Exception as e:
        print("Error parsing LLM JSON output:", e)
        return []

    all_filtered = []
    # For each provided date range, compute which month keys are relevant.
    for dr in date_ranges:
        try:
            start_dt = datetime.strptime(dr["start"], "%d-%m-%Y")
            end_dt = datetime.strptime(dr["end"], "%d-%m-%Y")
        except Exception as e:
            print("Error parsing dates in range:", dr, e)
            continue

        # Get month keys between start_dt and end_dt
        month_keys = get_month_keys_in_range(start_dt, end_dt)
        print(f"For date range {dr}, month keys to check: {month_keys}")

        for key in month_keys:
            if key in database:
                transactions = database[key]
                # Filter transactions in this key that lie within the date range
                for txn in transactions:
                    try:
                        txn_date = datetime.strptime(txn["Date"], "%d-%m-%Y")
                    except Exception:
                        continue
                    if start_dt <= txn_date <= end_dt:
                        all_filtered.append(txn)
    return all_filtered


    # if key not in database:
    #     print(f"No transactions found for {key}")
    #     return []

    # try:
    #     all_filtered = []
    #     transactions = database[key]

    #     for range_ in date_ranges:
    #         start = datetime.strptime(range_["start"], "%d-%m-%Y")
    #         end = datetime.strptime(range_["end"], "%d-%m-%Y")

    #         filtered = [
    #             txn for txn in transactions
    #             if start <= datetime.strptime(txn["Date"], "%d-%m-%Y") <= end
    #         ]
    #         all_filtered.extend(filtered)

    #     return all_filtered
    # except Exception as e:
    #     print("Error filtering transactions:", e)
    #     return []
    
    
    
class ReleventDocumentAgentMessage(Model):
    # message: str
    message : str
    # ftd : dict

class ReleventDocumentAgentResponse(Model):
    fld : list

ReleventDocumentAgent = Agent(name="ReleventDocumentAgent", seed="ReleventDocumentAgent recovery phrase", port=8003, mailbox=True)

@ReleventDocumentAgent.on_rest_post("/rest/post", ReleventDocumentAgentMessage, ReleventDocumentAgentResponse)
async def relevent_document_agent(ctx: Context , message: ReleventDocumentAgentMessage)-> ReleventDocumentAgentResponse:
    """
    Handles the relevant document agent's message.

    Args:
        context (Context): The context of the agent.
        sender (str): The sender of the message.
        message (InputReaderAgentMessage): The message from the relevant document agent.
    """
    # print(ReleventDocumentAgent.address)
    print("\n ------Getting relevant transactions---------. \n")
    with open("INFO/processed_output.json", "r") as file:
        ftd2 = json.load(file)

    print("\n ------Getting relevant transactions---------. \n")
    flq = get_relevance(message.message)
    # fld = get_relevant_transactions(flq, message.ftd)
    fld = get_relevant_transactions(flq,ftd2)
    print("\n ------Got relevant transactions successfully---------. \n")
    with open("INFO/filtered_transactions.json", "w") as file:
            json.dump(fld, file, indent=4)
    # upload_my_file("filtered_transactions.json", fld)
    
    
    # await ctx.send(sender, fld)
    return ReleventDocumentAgentResponse(fld=fld)

if __name__ == "__main__":
    # Run the agent
    ReleventDocumentAgent.run()

