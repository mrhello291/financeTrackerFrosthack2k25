import streamlit as st
import requests
import os
from typing import List
import plotly.express as px
import plotly.io as pio
import pandas as pd
import json

def render_response(response):
    try:
        result = response.json()
        ans_str = result.get("ans")
        if not ans_str:
            st.error("No answer received from the API.")
            return

        # Parse the nested JSON string
        parsed_ans = json.loads(ans_str)

        # Extract the refined final answer
        final_answer = parsed_ans["choices"][0]["message"]["content"]

        # Extract model thoughts if available
        thoughts = parsed_ans.get("thought", [])

        # Display final answer
        st.markdown("### Final Answer")
        st.markdown(final_answer)

        # Display internal thoughts in an expander
        if thoughts:
            with st.expander("Show Model Thought Process"):
                for t in thoughts:
                    st.write(t)
        return final_answer

    except Exception as e:
        st.error(f"Error processing response: {e}")
        st.write(response.text)


# Create the directory if it doesn't exist
DATA_DIR = "INFO/data"
os.makedirs(DATA_DIR, exist_ok=True)

def upload_page():
    """Page for uploading a file & viewing transaction graphs"""
    st.title("📂 Upload & View Transactions")

    ### 🔹 Section 1: Upload Feature
    st.header("🚀 Upload File")
    uploaded_files = st.file_uploader("Choose a PDF file", type=["pdf"], accept_multiple_files=True)

    # if uploaded_file:
    #     file_path = os.path.join(DATA_DIR, uploaded_file.name)
    #     with open(file_path, "wb") as f:
    #         f.write(uploaded_file.getbuffer())
    #     st.success(f"✅ File '{uploaded_file.name}' saved successfully!")

    #     # Store filename in session state
    #     st.session_state["uploaded_filename"] = uploaded_file.name

    # if st.button("🔄 Add File Data"):
    #     if "uploaded_filename" in st.session_state:
    #         response = requests.post(
    #             "http://0.0.0.0:8000/nest/post",
    #             json={"message": st.session_state["uploaded_filename"]}
    #         )
    #         st.write(response.json())
    #         st.write("📌 Button clicked!")
    #     else:
    #         st.warning("⚠️ Please upload a file before clicking 'Add File Data'.")
    # UPDATED CODE
    if uploaded_files:
        # Save each uploaded file
        for uploaded_file in uploaded_files:
            file_path = os.path.join(DATA_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ File '{uploaded_file.name}' saved successfully!")
        # Store the list of filenames in session state
        st.session_state["uploaded_filenames"] = [f.name for f in uploaded_files]

    if st.button("🔄 Add File Data"):
        if "uploaded_filenames" in st.session_state:
            responses = []
            # Loop over each filename and send an individual call
            for fname in st.session_state["uploaded_filenames"]:
                response = requests.post(
                    "http://0.0.0.0:8000/nest/post",
                    json={"message": fname}
                )
                responses.append(response.json())
            st.write("Responses:")
            st.write(responses)
            st.write("📌 Button clicked!")
        else:
            st.warning("⚠️ Please upload file(s) before clicking 'Add File Data'.")

    ### 🔹 Section 2: Show Graphs for Transactions
    st.header("📊 Transaction Analytics")

    json_path = "INFO/processed_output.json"

    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)  # Load JSON file

        # Show dropdown to select a file (Month)
        pdf_names = list(data.keys())
        selected_pdf = st.selectbox("📅 Select a Month:", pdf_names)

        if selected_pdf in data:
            transactions = data[selected_pdf]  # Get transactions for selected PDF

            if transactions:
                df = pd.DataFrame(transactions)  # Convert to DataFrame
                df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

                # Show Raw Data
                st.subheader("📜 Transaction Data")
                st.dataframe(df)

                # 1️⃣ Line Chart: Balance Over Time
                st.subheader("📈 Balance Over Time")
                fig_balance = px.line(df, x="Date", y="Balance", title="Balance Trend", markers=True)
                st.plotly_chart(fig_balance)

                # 2️⃣ Bar Chart: Deposit vs Withdrawal
                st.subheader("💰 Deposit vs Withdrawal")
                df["Deposit"] = df["Deposit"].fillna(0)
                df["Withdrawal"] = df["Withdrawal"].fillna(0)

                fig_bar = px.bar(df, x="Date", y=["Deposit", "Withdrawal"], 
                                 title="Deposits & Withdrawals", 
                                 barmode="group")
                st.plotly_chart(fig_bar)

                # 3️⃣ Area Chart: Cumulative Deposits & Withdrawals
                st.subheader("📊 Cumulative Deposits & Withdrawals")
                df["Cumulative Deposit"] = df["Deposit"].cumsum()
                df["Cumulative Withdrawal"] = df["Withdrawal"].cumsum()

                fig_area = px.area(df, x="Date", y=["Cumulative Deposit", "Cumulative Withdrawal"],
                                   title="Cumulative Deposits vs Withdrawals")
                st.plotly_chart(fig_area)

                # 4️⃣ Histogram: Transactions Per Day
                st.subheader("📊 Daily Transaction Count")
                df["Transaction Count"] = 1  

                fig_hist = px.histogram(df, x="Date", y="Transaction Count", 
                                        title="Transactions Per Day", nbins=len(df["Date"].unique()))
                st.plotly_chart(fig_hist)

            else:
                st.warning(f"⚠️ No transactions found for '{selected_pdf}'.")
    else:
        st.warning("⚠️ Processed transaction data not found!")


def query_page():
    """Page for querying transactions"""
    st.title("🔍 Query Transactions")

    query = st.text_input("🔎 Enter your query")

    if st.button("📌 Get Relevant Transactions"):
        if query:
            response = requests.post("http://0.0.0.0:8000/rest/post", json={"message": query})
            data = response.json()

            if "fld" in data and isinstance(data["fld"], list) and len(data["fld"]) > 0:
                transactions = data["fld"]
                
                # Convert to DataFrame
                df = pd.DataFrame(transactions)
                df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

                # Show transactions in table format
                st.subheader("📜 Query Results")
                st.dataframe(df)

                # Line Chart: Balance Over Time
                st.subheader("📈 Balance Trend")
                fig_balance = px.line(df, x="Date", y="Balance", title="Balance Trend", markers=True)
                st.plotly_chart(fig_balance)

            else:
                st.warning("⚠️ No transactions found for your query!")

        else:
            st.warning("⚠️ Please enter a query before clicking the button.")

    # if st.button("Get Answer"):
    #     if query:
    #         response = requests.post("http://0.0.0.0:8000/pest/post", json={"message": query})
    #         st.write(response.json())
    #     else:
    #         st.warning("Please enter a query before clicking the button.")

def chat_page():
    """Page for chatting with the model"""
    st.title("Chat with Model")

    query = st.text_input("Enter your query")
    
    # New checkbox to decide whether to generate graphs
    visualize = st.checkbox("Visualize data", value=False)


    if st.button("Get Answer"):
        if query:
            # Get context: returns "Yes" or "No"
            response00 = requests.post("http://0.0.0.0:8000/context/post", json={"message": query})
            context_ans = response00.json().get("ans")
            
            if context_ans.lower() == "yes":
                # Call endpoints for the refined answer
                # (Assuming /rest/post and /pest/post are both used; adjust as needed)
                response0 = requests.post("http://0.0.0.0:8000/rest/post", json={"message": query})
                response = requests.post("http://0.0.0.0:8000/pest/post", json={"message": query})
                
                answer_text = render_response(response)
            else:
                answer_text = render_response(response00)
            
            # If we received a valid chat answer, send it to the graphing agent.
            if answer_text:
                if visualize:
                    st.info("Generating graphs...")
                    graph_message = (
                        f"User Query: {query}\n"
                        f"Chat Answer: {answer_text}\n"
                        "Generate multiple relevant graphs (e.g., line charts, bar charts, pie charts, histograms) that best represent the underlying transaction data."
                    )
                    graph_response = requests.post("http://0.0.0.0:8000/rest/graph", json={"message": graph_message})
                    try:
                        graph_data = graph_response.json()
                    except Exception as e:
                        st.error("Error parsing graph response: " + str(e))
                        return
                    if "graphs" in graph_data:
                        graphs_list = graph_data["graphs"]
                        if not isinstance(graphs_list, list):
                            graphs_list = [graphs_list]
                        st.write(f"Generated {len(graphs_list)} graphs:")
                        for i, graph_json in enumerate(graphs_list):
                            try:
                                # Try to parse the graph JSON string
                                parsed_graph = json.loads(graph_json)
                                # If it's an error message, display it and skip rendering.
                                if isinstance(parsed_graph, dict) and "error" in parsed_graph:
                                    st.error(f"Graph {i+1} error: {parsed_graph['error']}")
                                    continue
                                # Otherwise, try to render the figure.
                                fig = pio.from_json(graph_json)
                                st.plotly_chart(fig)
                            except Exception as e:
                                st.error(f"Error rendering graph {i+1}: {e}")
                    else:
                        st.error("Graph data not found in response.")
                else:
                    st.info("Graph visualization disabled.")
            else:
                st.error("No answer received from chat agent to generate graphs.")
        else:
            st.warning("Please enter a query before clicking the button.")


def search_page():
    """New Page for Searching"""
    st.header("🔍 Search Transactions")

    key = st.text_input("📂 Key / Month (e.g., mar_2025.pdf)")
    start_date = st.text_input("📅 Start Date (DD-MM-YYYY)")
    end_date = st.text_input("📅 End Date (DD-MM-YYYY)")

    if st.button("🚀 Search"):
        if key and start_date and end_date:
            response = requests.post(
                "http://0.0.0.0:8000/search", 
                json={"key": key, "start_date": start_date, "end_date": end_date}
            )
            data = response.json()  

            # Extract transactions from "filtered_transactions" key
            transactions = data.get("filtered_transactions", [])

            if isinstance(transactions, list) and len(transactions) > 0:
                df = pd.DataFrame(transactions)  # Convert JSON to DataFrame
                
                # Convert 'Date' to datetime for plotting
                df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

                # Show raw data
                st.subheader("📊 Raw Transaction Data")
                st.dataframe(df)

                # 1️⃣ Line Chart: Account Balance Over Time
                st.subheader("📈 Balance Over Time")
                fig_balance = px.line(df, x="Date", y="Balance", title="Balance Trend", markers=True)
                st.plotly_chart(fig_balance)

                # 2️⃣ Bar Chart: Deposit vs Withdrawal
                st.subheader("💰 Deposit vs Withdrawal")
                df["Deposit"] = df["Deposit"].fillna(0)  # Handle NaN values
                df["Withdrawal"] = df["Withdrawal"].fillna(0)

                fig_bar = px.bar(df, x="Date", y=["Deposit", "Withdrawal"], 
                                 title="Deposits & Withdrawals", 
                                 barmode="group")
                st.plotly_chart(fig_bar)

                # 3️⃣ Area Chart: Cumulative Deposits & Withdrawals
                st.subheader("📊 Cumulative Deposits & Withdrawals")
                df["Cumulative Deposit"] = df["Deposit"].cumsum()
                df["Cumulative Withdrawal"] = df["Withdrawal"].cumsum()

                fig_area = px.area(df, x="Date", y=["Cumulative Deposit", "Cumulative Withdrawal"],
                                   title="Cumulative Deposits vs Withdrawals")
                st.plotly_chart(fig_area)

                # 4️⃣ Histogram: Transactions Per Day
                st.subheader("📊 Daily Transaction Count")
                df["Transaction Count"] = 1  # Each row is a transaction

                fig_hist = px.histogram(df, x="Date", y="Transaction Count", 
                                        title="Transactions Per Day", nbins=len(df["Date"].unique()))
                st.plotly_chart(fig_hist)

            else:
                st.warning("⚠️ No transactions found for the given inputs.")
        else:
            st.warning("⚠️ Please fill in all fields before searching.")
            
def dynamic_graph_page():
    st.title("📊 Dynamic Transaction Graphs")
    st.write("Enter a query to generate a custom graph based on transaction data.")
    
    
    user_query = st.text_input("Enter your query (e.g., 'show me balance trends')")
    
    if st.button("Generate Graph"):
        if user_query:
            response = requests.post("http://0.0.0.0:8000/rest/graph", json={"message": user_query})
            try:
                data = response.json()
            except Exception as e:
                st.error("Error parsing response: " + str(e))
                return
            print(data)
            if "graph" in data:
                graph_json = data["graph"]
                try:
                    # Convert the JSON string back to a Plotly figure.
                    fig = pio.from_json(graph_json)
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error("Error rendering graph: " + str(e))
            else:
                st.error("Graph not found in response.")
        else:
            st.warning("Please enter a query.")



def main():
    """Main function to handle navigation with sidebar"""
    st.sidebar.title("🔗 Navigation")
    page = st.sidebar.radio("Go to", ["📂 Upload File", "🔎 Query Transactions","💬 Chat" ,"🔍 Search", "📊 Dynamic Graph"])

    if page == "📂 Upload File":
        upload_page()
    elif page == "🔎 Query Transactions":
        query_page()
    elif page == "🔍 Search":
        search_page()
    elif page == "💬 Chat":
        chat_page()
    elif page == "📊 Dynamic Graph":
        dynamic_graph_page()


if __name__ == "__main__":
    main()