# Finance Tracker - AI-powered Financial Analysis

## Overview
This project is an AI-powered financial analysis system that processes and analyzes transaction data to provide insights and answer user queries. It integrates LangChain, Fetch.ai, and Pathway for efficient data processing and retrieval.

## video 
- https://www.youtube.com/watch?v=DY6-u3Y996Q

## Features
- Parses and extracts financial transactions from documents.
- Stores structured financial data for quick retrieval.
- Provides financial insights based on user queries.
- Implements advanced retrieval-augmented generation (RAG) techniques.
- Uses Fetch.ai and Pathway for efficient data processing.
- Supports visualization of financial data trends.

## Project Structure
```
├── agent_fetchai.py  #fetchAI Agents
├── agents
│   ├── DocToGDrive.py
│   ├── DocumentParsingAgent2.py
│   ├── DocumentParsingAgent.py
│   ├── GetReleventTransactionByDate.py
│   ├── GetReleventTransaction.py
│   ├── GetUserQueryOutput.py
│   ├── IsContextNeeded.py
│   └── __pycache__
├── app.py  
├── Cache
│   ├── 1-0-0
│   └── 1-0-1
├── credentials.json
├── data
│   └── finance_docs_extracted.csv
├── INFO
│   ├── data
│   ├── filtered_transactions.json
│   ├── output.json
│   ├── processed_output.json
│   ├── staticPlots
├── LanggraphApp.py
├── output_chunks
├── pathwayF
│   ├── baseModel.py
│   ├── langchainPathwayClient.py
│   ├── pathwayServer.py
│   ├── pdfToCSVByLLM.py
│   └── __pycache__
├── README.md
├── requirements.txt
└── staticVisualizationAgent.py
```

## App Diagrams

### Project Diagram
![alt text](https://github.com/mrhello291/financeTrackerFrosthack2k25/blob/main/app-diagram.png?raw=true)

### Fetch-AI Agent Diagram
![alt text](https://github.com/mrhello291/financeTrackerFrosthack2k25/blob/main/agent-diagram.png?raw=true)


## Installation

### 1. Set Environment Variables
Before running the application, configure the following environment variables:
```bash
export PATHWAY_KEY=""
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY=""
export LANGSMITH_PROJECT=""
export GEMINI_API_KEY="--"
export GROQ_API_KEY=""
export TAVILY_API_KEY=""
export DEEPSEEK_API_KEY=""
export HUGGINGFACEHUB_API_TOKEN=""
export GDRIVEFOLDERID=""
```

### 2. Set Up `credentials.json`
Create a `credentials.json` file in the root directory and populate it with your Google Cloud credentials:
```json
{
  "type": "service_account",
  "project_id": "rag-app-frosthack",
  "private_key_id": "<PRIVATE_KEY_ID>",
  "private_key": "-----BEGIN PRIVATE KEY-----\n<PRIVATE_KEY>\n-----END PRIVATE KEY-----\n",
  "client_email": "<CLIENT_EMAIL>",
  "client_id": "<CLIENT_ID>",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/<SERVICE_ACCOUNT>.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```
_Note: Replace `<PRIVATE_KEY>`, `<CLIENT_EMAIL>`, `<CLIENT_ID>`, and `<SERVICE_ACCOUNT>` with your actual credentials._

### 3. Install Dependencies
Run the following command to install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application
Follow these steps to start the application:

1. **Start the Fetch.AI Agents**
   ```bash
   python -m agents.ActivateVectorStore
   python -m agents.DocParserAgent
   python -m agents.getReleventTransaction
   python -m agents.GetUserQueryOutput
   python -m agents.GraphingAgent
   python -m agents.IsContextNeeded
   ```

2. **Run the Streamlit App**
   ```bash
   streamlit run app.py
   ```


## Relevant Resources
- [FetchAi with LangChain](https://fetch.ai/docs/examples/rag/langchain-rag)
- [Pathway with LangChain](https://pathway.com/blog/langchain-integration)
- [Pathway Adaptive RAG with LangGraph](https://github.com/pathwaycom/llm-app/blob/main/cookbooks/self-rag-agents/pathway_langgraph_agentic_rag.ipynb)
- [Pathway as a Vector Store in LangChain](https://python.langchain.com/docs/integrations/vectorstores/pathway/)
- [Pathway Unstructured to Structured SQL Queries](https://github.com/pathwaycom/llm-app/tree/main/examples/pipelines/unstructured_to_sql_on_the_fly)
- [Pathway INTERIIT Project](https://github.com/Stormbreakerr20/Pathway_InterIIT_13.0/tree/master/code/Rag_application)
- [Google Drive with Additional Files](https://drive.google.com/drive/folders/14cPcPF19g3LPGojMTRhoNCFTAx8sTV0a)

## Contributing
Feel free to open issues and submit pull requests for improvements.
