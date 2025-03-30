from uagents import Agent, Bureau, Context, Model
import json
from agents.DocumentParsingAgent import process_pdfs
from agents.DocumentParsingAgent2 import extract_transactions, process_all_files
from agents.GetReleventTransaction import get_relevance, get_relevant_transactions
from agents.GetUserQueryOutput import answerQuery


#kis tarah ke message se trigger hoga 
class InputReaderAgentMessage(Model):
    message: str

class InputReaderAgentMessageResponse(Model):
    ftd: dict

class ReleventDocumentAgentMessage(Model):
    # message: str
    message : str
    # ftd : dict

class ReleventDocumentAgentResponse(Model):
    fld : list


class QueryAnswerAgentMessage(Model):
    message: str
    # query : str
    # fld : dict

class QueryAnswerAgentMessageResponse(Model):
    ans: str

QueryAnswerAgent = Agent(name="QueryAnswerAgent", seed="QueryAnswerAgent recovery phrase", port=8000)

ReleventDocumentAgent = Agent(name="ReleventDocumentAgent", seed="ReleventDocumentAgent recovery phrase", port=8000)

InputReaderParseAgent = Agent(name="InputReaderAgent", seed="InputReaderAgent recovery phrase", port=8000)



# @InputReaderParseAgent.on_message(model=InputReaderAgentMessage)
# @InputReaderParseAgent.on_query(model=InputReaderAgentMessage)
@InputReaderParseAgent.on_rest_post("/nest/post",InputReaderAgentMessage,InputReaderAgentMessageResponse)
async def input_reader_agent(ctx: Context, message: InputReaderAgentMessage) -> InputReaderAgentMessageResponse:
    """
    Handles the input reader agent's message.

    Args:
        context (Context): The context of the agent.
        sender (str): The sender of the message.
        message (InputReaderAgentMessage): The message from the input reader agent.
    """
    
    print("\n ------Parsing the input---------. \n")
    ptd = process_pdfs("INFO/data",message.message)
    ftd = process_all_files(ptd, message.message)
    # with open("INFO/processed_output.json", "w", encoding="utf-8") as outfile:
    #     json.dump(ftd, outfile, indent=4)
    print("\n ------Parsed the input successfully---------. \n")
    print(InputReaderParseAgent.address)
    
    # await ctx.send(sender, ftd)
    return InputReaderAgentMessageResponse(ftd=ftd)



# @ReleventDocumentAgent.on_message(model=ReleventDocumentAgentMessage)
# @ReleventDocumentAgent.on_query(model=ReleventDocumentAgentMessage)
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
    
    # await ctx.send(sender, fld)
    return ReleventDocumentAgentResponse(fld=fld)


# @QueryAnswerAgent.on_message(model=QueryAnswerAgentMessage)
# @QueryAnswerAgent.on_query(model=QueryAnswerAgentMessage, replies={QueryAnswerAgentMessageResponse})
@QueryAnswerAgent.on_rest_post("/pest/post", QueryAnswerAgentMessage, QueryAnswerAgentMessageResponse)
async def query_answer_agent(ctx: Context , message: QueryAnswerAgentMessage) -> QueryAnswerAgentMessageResponse:
    """
    Handles the query answer agent's message.

    Args:
        context (Context): The context of the agent.
        sender (str): The sender of the message.
        message (InputReaderAgentMessage): The message from the query answer agent.
    """
    
    print("\n ------Getting relevant transactions---------. \n")
    fld2= {}
    with open("INFO/filtered_transactions.json", "r") as file:
        fld2 = json.load(file)
    print("\n ------Getting answer to the query---------. \n")
    ans = answerQuery(message.message, fld2)
    print("\n ------Got answer to the query successfully---------. \n")
    
    # await ctx.send(sender, ans)
    return QueryAnswerAgentMessageResponse(ans=ans)


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
bureau.add(QueryAnswerAgent)
bureau.add(InputReaderParseAgent)
bureau.add(ReleventDocumentAgent)
# bureau.add(DemoAgent)

if __name__ == "__main__":
    bureau.run()
    # InputReaderParseAgent.run()
    # ReleventDocumentAgent.run()
    # QueryAnswerAgent.run()