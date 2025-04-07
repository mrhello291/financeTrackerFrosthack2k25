import os
from uagents import Agent, Bureau, Context, Model
import json
from typing import List
# from agents.DocumentParsingAgent import process_pdfs
# from agents.DocumentParsingAgent2 import extract_transactions, process_all_files
# from agents.GetReleventTransaction import get_relevance, get_relevant_transactions
# from agents.GetUserQueryOutput import answerQuery
# from agents.GetReleventTransactionByDate import get_filtered_transactions
# from agents.IsContextNeeded import CheckQuery
# from pathwayServer import run_server

#kis tarah ke message se trigger hoga 
# class ReleventDocumentAgentMessage(Model):
#     # message: str
#     message : str
#     # ftd : dict

# class ReleventDocumentAgentResponse(Model):
#     fld : list


# class QueryAnswerAgentMessage(Model):
#     message: str
#     # query : str
#     # fld : dict

# class QueryAnswerAgentMessageResponse(Model):
#     ans: str

# class FetchReleventDocbydateAgentMessage(Model):
#     key: str
#     start_date: str
#     end_date: str

# class FetchReleventDocbydateAgentResponse(Model):
#     filtered_transactions: list

# class ActivateVectorStoreAgentMessage(Model):
#     message: str

# class IsContextNeededAgentMessage(Model):
#     message: str

# class IsContextNeededAgentResponse(Model):
#     ans: str


# QueryAnswerAgent = Agent(name="QueryAnswerAgent", seed="QueryAnswerAgent recovery phrase", port=8000)

# ReleventDocumentAgent = Agent(name="ReleventDocumentAgent", seed="ReleventDocumentAgent recovery phrase", port=8000)


# FetchReleventDocbydateAgent = Agent(name="FetchReleventDocbydateAgent", seed="FetchReleventDocbydateAgent recovery phrase", port=8000)

# IsContextNeededAgent = Agent(name="IsContextNeededAgent", seed="IsContextNeededAgent recovery phrase", port=8000)

# ActivateVectorStoreAgent = Agent(name="ActivateVectorStoreAgent", seed="ActivateVectorStoreAgent recovery phrase", port=8000)

# GraphingAgent = Agent(name="GraphingAgent", seed="GraphingAgent recovery phrase", port=8000)

# @ActivateVectorStoreAgent.on_rest_post("/query", ActivateVectorStoreAgentMessage, None)
# async def query_vector_store_agent(ctx: Context, message: ActivateVectorStoreAgentMessage) -> None:
#     """
#     Handles the query vector store agent's message.

#     Args:
#         context (Context): The context of the agent.
#         sender (str): The sender of the message.
#         message (ActivateVectorStoreAgentMessage): The message from the query vector store agent.
#     """
#     run_server()



# @IsContextNeededAgent.on_rest_post("/context/post", IsContextNeededAgentMessage, IsContextNeededAgentResponse)
# async def is_context_needed_agent(ctx: Context, message: IsContextNeededAgentMessage) -> IsContextNeededAgentResponse:
#     """
#     Handles the is context needed agent's message.

#     Args:
#         context (Context): The context of the agent.
#         sender (str): The sender of the message.
#         message (IsContextNeededAgentMessage): The message from the is context needed agent.
#     """
    
#     print("\n ------Checking if context is needed---------. \n")
#     ans = CheckQuery(message.message)
#     print("\n ------Checked if context is needed successfully---------. \n")
    
#     return IsContextNeededAgentResponse(ans=ans)

# @FetchReleventDocbydateAgent.on_rest_post("/search", FetchReleventDocbydateAgentMessage, FetchReleventDocbydateAgentResponse)
# async def fetch_relevent_doc_by_date_agent(ctx: Context, message: FetchReleventDocbydateAgentMessage) -> FetchReleventDocbydateAgentResponse:
#     """
#     Handles the fetch relevant document by date agent's message.

#     Args:
#         context (Context): The context of the agent.
#         sender (str): The sender of the message.
#         message (FetchReleventDocbydateAgentMessage): The message from the fetch relevant document by date agent.
#     """
    
#     print("\n ------Getting filtered transactions---------. \n")
#     filtered_transactions = get_filtered_transactions(message.key, message.start_date, message.end_date)
#     print("\n ------Got filtered transactions successfully---------. \n")
    
#     return FetchReleventDocbydateAgentResponse(filtered_transactions=filtered_transactions)


# @InputReaderParseAgent.on_message(model=InputReaderAgentMessage)
# @InputReaderParseAgent.on_query(model=InputReaderAgentMessage)
# @InputReaderParseAgent.on_rest_post("/nest/post",InputReaderAgentMessage,InputReaderAgentMessageResponse)
# async def input_reader_agent(ctx: Context, message: InputReaderAgentMessage) -> InputReaderAgentMessageResponse:
#     """
#     Handles the input reader agent's message.

#     Args:
#         context (Context): The context of the agent.
#         sender (str): The sender of the message.
#         message (InputReaderAgentMessage): The message from the input reader agent.
#     """
    
#     print("\n ------Parsing the input---------. \n")
#     ptd = process_pdfs("INFO/data", message.message)
#     ftd = process_all_files(ptd, message.message)
#     grivePipe()
#     # with open("INFO/processed_output.json", "w", encoding="utf-8") as outfile:
#     #     json.dump(ftd, outfile, indent=4)
#     print("\n ------Parsed the input successfully---------. \n")
#     print(InputReaderParseAgent.address)
    
#     # await ctx.send(sender, ftd)
#     return InputReaderAgentMessageResponse(ftd=ftd)




# @ReleventDocumentAgent.on_message(model=ReleventDocumentAgentMessage)
# @ReleventDocumentAgent.on_query(model=ReleventDocumentAgentMessage)
# @ReleventDocumentAgent.on_rest_post("/rest/post", ReleventDocumentAgentMessage, ReleventDocumentAgentResponse)
# async def relevent_document_agent(ctx: Context , message: ReleventDocumentAgentMessage)-> ReleventDocumentAgentResponse:
#     """
#     Handles the relevant document agent's message.

#     Args:
#         context (Context): The context of the agent.
#         sender (str): The sender of the message.
#         message (InputReaderAgentMessage): The message from the relevant document agent.
#     """
#     # print(ReleventDocumentAgent.address)
#     print("\n ------Getting relevant transactions---------. \n")
#     with open("INFO/processed_output.json", "r") as file:
#         ftd2 = json.load(file)

#     print("\n ------Getting relevant transactions---------. \n")
#     flq = get_relevance(message.message)
#     # fld = get_relevant_transactions(flq, message.ftd)
#     fld = get_relevant_transactions(flq,ftd2)
#     print("\n ------Got relevant transactions successfully---------. \n")
#     with open("INFO/filtered_transactions.json", "w") as file:
#             json.dump(fld, file, indent=4)
    
#     # await ctx.send(sender, fld)
#     return ReleventDocumentAgentResponse(fld=fld)


# @QueryAnswerAgent.on_message(model=QueryAnswerAgentMessage)
# @QueryAnswerAgent.on_query(model=QueryAnswerAgentMessage, replies={QueryAnswerAgentMessageResponse})
# @QueryAnswerAgent.on_rest_post("/pest/post", QueryAnswerAgentMessage, QueryAnswerAgentMessageResponse)
# async def query_answer_agent(ctx: Context , message: QueryAnswerAgentMessage) -> QueryAnswerAgentMessageResponse:
#     """
#     Handles the query answer agent's message.

#     Args:
#         context (Context): The context of the agent.
#         sender (str): The sender of the message.
#         message (InputReaderAgentMessage): The message from the query answer agent.
#     """
    
#     print("\n ------Getting relevant transactions---------. \n")
#     fld2= {}
#     with open("INFO/filtered_transactions.json", "r") as file:
#         fld2 = json.load(file)
#     print("\n ------Getting answer to the query---------. \n")
#     ans = answerQuery(message.message, fld2)
#     print("\n ------Got answer to the query successfully---------. \n")
    
#     # await ctx.send(sender, ans)
#     return QueryAnswerAgentMessageResponse(ans=ans)

# @GraphingAgent.on_rest_post("/rest/graph", GraphingAgentMessage, GraphingAgentMessageResponse)
# async def graphing_agent(ctx: Context, message: GraphingAgentMessage) -> GraphingAgentMessageResponse:
#     """
#     Handles the graphing agent's message.
#     It generates a graph based on the user query and returns the graph in JSON format.
#     """
#     print("\n------ Generating dynamic graphs ---------\n")
#     graphs = generate_graphs(message.message)
#     print("\n------ Generated dynamic graphs successfully ---------\n")
#     return GraphingAgentMessageResponse(graphs=graphs)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# database = {}
# with open("INFO/processed_output.json", "r") as file:
#         database = json.load(file)
# filtereDdatabase = {}
# with open("INFO/processed_output.json", "r") as file:
#         filtereDdatabase = json.load(file)

# demo agent who calls input_reader_agent 
# class DemoAgentMessage(Model):
#     message: str

# DemoAgent = Agent(name="DemoAgent", seed="DemoAgent recovery phrase", port=8000)

# @DemoAgent.on_event("startup")
# async def startup(ctx: Context):
#     """
#     Handles the startup event of the demo agent.

#     Args:
#         context (Context): The context of the agent.
#     """
#     print("Demo agent started.")
#     await ctx.send(QueryAnswerAgent.address, QueryAnswerAgentMessage(message="demo", query="What i do between 1 feb and 10 feb", fld=filtereDdatabase))

bureau = Bureau()
# bureau.add(QueryAnswerAgent)
# bureau.add(InputReaderParseAgent)
# bureau.add(ReleventDocumentAgent)
# bureau.add(FetchReleventDocbydateAgent)
# bureau.add(IsContextNeededAgent)
# bureau.add(ActivateVectorStoreAgent)
# bureau.add(DemoAgent)

if __name__ == "__main__":
    bureau.run()
    # InputReaderParseAgent.run()
    # ReleventDocumentAgent.run()
    # QueryAnswerAgent.run()