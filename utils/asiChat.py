import json
import os
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())
api_key = os.getenv("ASI_API_KEY")
if not api_key:
    raise ValueError("ASI_API_KEY not found in .env")


def llmChat(messages, model="asi1-mini", max_tokens=8000, temperature=0, stream=False):
    url = "https://api.asi1.ai/v1/chat/completions"
    # Convert LangChain Message objects to dicts
    if hasattr(messages[0], 'type'):  # Detects if these are LangChain messages
        messages = [{"role": m.type, "content": m.content} for m in messages]
        
    # Map any non-standard roles to OpenAI-style roles
    role_map = {
        "human": "user",
        "user": "user",
        "ai": "assistant",
        "assistant": "assistant",
        "system": "system"
    }
    
    formatted_messages = []
    for m in messages:
        # Determine the original role and content
        if isinstance(m, dict):
            orig_role = m.get("role", "").lower()
            content = m.get("content", "")
        else:
            orig_role = getattr(m, "type", "").lower()
            content = getattr(m, "content", "")

        # Map to valid role or default to "user"
        role = role_map.get(orig_role, "user")

        formatted_messages.append({"role": role, "content": content})
    payload = json.dumps({
        "model": model,
        "messages": formatted_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f"Bearer {api_key}"
    }

    response = requests.post(url, headers=headers, data=payload, timeout=100)
    print("Status:", response.status_code)
    # print("Response:", response.text)
    
    return response.text

# import os
# import json
# import requests
# from dotenv import load_dotenv, find_dotenv
# from uagents import Agent, Context, Model


# # Load API Key
# load_dotenv(find_dotenv())
# api_key = os.getenv("ASI_API_KEY")
# if not api_key:
#     raise ValueError("ASI_API_KEY not found in .env")

# # Input model from client, now including additional parameters and messages list.
# class ASI1Query(Model):
#     messages: list  # list of messages; each message can be a dict with 'role' and 'content'
#     sender_address: str
#     temperature: float = 0.0
#     max_tokens: int = 8000
#     model: str = "asi1-mini"
#     stream: bool = False

# # Output model to send to client
# class ASI1Response(Model):
#     response: str

# # Server agent setup
# llmChatAgent = Agent(
#     name='asi1_server_agent',
#     port=5080,
#     seed='asi1_server_seed',
#     mailbox=True,
# )


# @llmChatAgent.on_event('startup')
# def startup_handler(ctx: Context):
#     ctx.logger.info(f"Server Agent {ctx.agent.name} started at {ctx.agent.address}")

# @llmChatAgent.on_rest_post("/chat", ASI1Query, ASI1Response)
# def handle_chat_via_rest(ctx: Context, msg: ASI1Query) -> ASI1Response:
#     ctx.logger.info("Received REST chat request")

#     # Role mapping as per your previous implementation
#     role_map = {
#         "human": "user",
#         "user": "user",
#         "ai": "assistant",
#         "assistant": "assistant",
#         "system": "system"
#     }

#     # Format the messages list using the role mapping.
#     formatted_messages = []
#     for m in msg.messages:
#         # Check if m is a dict, otherwise try to access attributes.
#         if isinstance(m, dict):
#             orig_role = m.get("role", "").lower()
#             content = m.get("content", "")
#         else:
#             orig_role = getattr(m, "type", "").lower()
#             content = getattr(m, "content", "")
#         role = role_map.get(orig_role, "user")
#         formatted_messages.append({"role": role, "content": content})

#     # Prepare request payload with dynamic parameters.
#     payload = json.dumps({
#         "model": msg.model,
#         "messages": formatted_messages,
#         "temperature": msg.temperature,
#         "max_tokens": msg.max_tokens,
#         "stream": msg.stream
#     })

#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json',
#         'Authorization': f"Bearer {api_key}"
#     }

#     try:
#         response = requests.post("https://api.asi1.ai/v1/chat/completions",
#                                  headers=headers, data=payload, timeout=100)
#         ctx.logger.info(f"ASI API status: {response.status_code}")

#         if response.status_code == 200:
#             completion = response.json()['choices'][0]['message']['content']
#         else:
#             completion = f"Error {response.status_code}: {response.text}"
#     except Exception as e:
#         completion = f"Exception during API call: {str(e)}"

#     return ASI1Response(response=completion)


# if __name__ == "__main__":
#     llmChatAgent.run()
#     # Address -> agent1qwrjuyn35uus6nn8cyjsn8v80y3hqrvfatcny4tjhjpywg7jev26xm2lh0m
