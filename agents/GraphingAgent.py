import os
import re
import json
from typing import List
from datetime import datetime
from uuid import uuid4
import pandas as pd
from uagents import Agent, Context, Model
from utils.asiChat import llmChat
from utils.DriveJSONRetriever import retrieve_data_from_gdrive


def sanitize_graph_json(graph_json: str) -> list:
    """
    Parses and sanitizes the graph JSON string.
    - Removes markdown code fences if present.
    - Strips leading/trailing whitespace.
    - Replaces 'NaN' with 'null'.
    - Ensures the output is a list of valid Plotly figure JSON strings.
    - Removes any 'error' property from each trace.
    """
    try:
        # Remove markdown code fences if present.
        pattern = r"```json\s*(.*?)\s*```"
        match = re.search(pattern, graph_json, re.DOTALL)
        if match:
            graph_json = match.group(1)
        # Strip whitespace
        graph_json = graph_json.strip()
        # Replace NaN with null
        graph_json = graph_json.replace("NaN", "null")
        
        # Try to parse the JSON.
        parsed = json.loads(graph_json)
        # If parsed is not a list, wrap it in a list.
        if not isinstance(parsed, list):
            parsed = [parsed]
        
        cleaned_graphs = []
        for item in parsed:
            # If item is a string, try parsing it
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except Exception as e:
                    print("Error parsing inner item:", e)
                    continue
            # Remove invalid property 'error' from traces
            if "data" in item and isinstance(item["data"], list):
                for trace in item["data"]:
                    trace.pop("error", None)
            cleaned_graphs.append(json.dumps(item))
        return cleaned_graphs
    except Exception as e:
        print("Sanitization failed:", e)
        return []


def generate_graphs(query: str) -> List[str]:
    """
    Generates a Plotly graph based on the user query and processed transaction data.
    Loads the filtered transactions from "INFO/filtered_transactions.json",
    converts them to a DataFrame, and creates an interactive Plotly figure.
    Returns the figure as a JSON string.
    """
    data_file = "INFO/filtered_transactions.json"
    if not os.path.exists(data_file):
        return [json.dumps({"error": "Processed transactions file not found."})]
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # data = retrieve_data_from_gdrive('filtered_transactions.json')
    
    # Flatten transactions: if data is a list, use it directly; if it's a dict, merge all values.
    if isinstance(data, list):
        all_transactions = data
    elif isinstance(data, dict):
        all_transactions = []
        for key, txns in data.items():
            all_transactions.extend(txns)
    else:
        return [json.dumps({"error": "Unexpected data format."})]
    
    if not all_transactions:
        return [json.dumps({"error": "No transactions available."})]
    
    # Convert to DataFrame
    df = pd.DataFrame(all_transactions)
    try:
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    except Exception as e:
        print("Error converting dates:", e)
    
    # Prepare a prompt instructing the LLM to generate multiple Plotly graphs.
    prompt = """
You are a Python expert and data visualization specialist.
Assume you have a pandas DataFrame called 'df' that contains transaction data with the following columns:
    'Date', 'Particulars', 'Deposit', 'Withdrawal', and 'Balance'.
Based on the user query which contains this df in list format, each transaction is a dictionary with the above keys,
Please produce a JSON array where each element is a valid JSON string generated by calling Plotly's figure.to_json() method. 
Each element should represent a different visualization (for example, a line chart, bar chart, pie chart, histogram, etc.) that best represents the underlying transaction data.
IMPORTANT:
    - Return ONLY the JSON array with no additional text, explanation, or markdown formatting.
    - Do NOT include any extra keys such as "error" or "warning".
    - Ensure that the output is exactly parseable by json.loads().
    - For line charts, do not use the trace type "line". Instead, use "scatter" with "mode": "lines".
    - Return empty JSON array if no graphs can be generated or if you can't find any transactions in query.
Example of the expected output format:
[
"{\\"data\\": [...], \\"layout\\": {...}, \\"config\\": {...}}",
"{\\"data\\": [...], \\"layout\\": {...}, \\"config\\": {...}}"
]
"""
    
    # Call LLM via llmChat. The response is expected to be a JSON array wrapped in markdown code fences.
    response = llmChat([{"role": "system", "content": prompt}, {"role": "user", "content": query}], temperature=0.4)
    res = json.loads(response)["choices"][0]["message"]["content"]
    # Combine the system prompt with the user query.    
    match = re.search(r"```json\s*(.*?)\s*```", res, re.DOTALL)
    json_text = match.group(1) if match else res.strip()
    
    # # Strip any extra whitespace/newlines.
    # json_text = json_text.strip()
    # # Handle possible double-encoding: if the string starts and ends with a quote, unquote it.
    # if (json_text.startswith('"') and json_text.endswith('"')):
    #     try:
    #         json_text = json.loads(json_text)
    #     except Exception as e:
    #         print("Error unquoting JSON text:", e)
    
    try:
        graphs = json.loads(json_text)
        if not isinstance(graphs, list):
            graphs = [str(graphs)]
    except Exception as e:
        print("Error parsing generated graph JSON:", e)
        graphs = [json_text]
    
    print("Generated graphs:", graphs)
    
    # Sanitize each graph JSON string.
    sanitized_graphs = []
    for graph_json in graphs:
        sanitized = sanitize_graph_json(graph_json)
        sanitized_graphs.extend(sanitized)
        
    # If no graphs were generated, return an explicit error graph.
    if not sanitized_graphs:
        sanitized_graphs = [json.dumps({"error": "No graphs generated."})]
    
    print(sanitized_graphs)
    
    return sanitized_graphs

# --- New Helper: prepare_graphs_response ---
def prepare_graphs_response(query: str) -> List[str]:
    """
    Generates graphs using generate_graphs(), then processes the output:
      - Parses the returned JSON array.
      - Filters out any graphs that contain an error field.
      - If no valid graphs remain, returns a list with an explicit error JSON.
    """
    graphs = generate_graphs(query)
    valid_graphs = []
    
    for graph_json in graphs:
        try:
            # Attempt to parse the graph JSON.
            graph_obj = json.loads(graph_json)
            if isinstance(graph_obj, dict) and "error" in graph_obj:
                print("Skipping graph due to error:", graph_obj["error"])
                continue
            valid_graphs.append(graph_json)
        except Exception as e:
            print("Error parsing graph JSON:", e)
            continue
    
    if not valid_graphs:
        valid_graphs = [json.dumps({"error": "No valid graphs generated."})]
    
    return valid_graphs


class GraphingAgentMessage(Model):
    message: str
class GraphingAgentMessageResponse(Model):
    graphs: List[str]  # A list of Plotly figure JSON strings

GraphingAgent = Agent(name="GraphingAgent", seed="GraphingAgent recovery phrase", port=8001, mailbox=True)


@GraphingAgent.on_rest_post("/graph", GraphingAgentMessage, GraphingAgentMessageResponse)
async def graphing_agent(ctx: Context, message: GraphingAgentMessage) -> GraphingAgentMessageResponse:
    """
    Handles the graphing agent's message.
    It generates a graph based on the user query and returns the graph in JSON format.
    """
    print("\n------ Generating dynamic graphs ---------\n")
    graphs = prepare_graphs_response(message.message)
    print("\n------ Generated dynamic graphs successfully ---------\n")
    return GraphingAgentMessageResponse(graphs=graphs)


if __name__ == "__main__":
    # Start the GraphingAgent server
    print("Graphing Agent is running...")
    GraphingAgent.run()