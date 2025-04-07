from pathwayServer import run_server
from uagents import Agent, Context, Model



class ActivateVectorStoreAgentMessage(Model):
    message: str

class EmptyResponse(Model):
    pass

ActivateVectorStoreAgent = Agent(name="ActivateVectorStoreAgent", seed="ActivateVectorStoreAgent recovery phrase", port=8005, mailbox=True)


@ActivateVectorStoreAgent.on_rest_post("/docstore", ActivateVectorStoreAgentMessage, EmptyResponse)
async def query_vector_store_agent(ctx: Context, message: ActivateVectorStoreAgentMessage) -> EmptyResponse:
    """
    Handles the query vector store agent's message.

    Args:
        context (Context): The context of the agent.
        sender (str): The sender of the message.
        message (ActivateVectorStoreAgentMessage): The message from the query vector store agent.
    """
    run_server()
    
if __name__ == "__main__":
    ActivateVectorStoreAgent.run()