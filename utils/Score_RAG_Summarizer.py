# import os
# import json
# from typing import List
# from typing_extensions import TypedDict
# from langchain_community.vectorstores import PathwayVectorClient
# from langchain_core.output_parsers import StrOutputParser, JsonOutputToolsParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain import hub
# from pydantic import BaseModel, Field
# from langgraph.graph import END, StateGraph, START
# from asi_chat import llmChat  # Make sure this matches your file path
# # from langchain_huggingface import HuggingFaceEndpoint
# # from langchain_google_genai import ChatGoogleGenerativeAI


# os.environ['LANGCHAIN_TRACING_V2'] = os.getenv("LANGSMITH_TRACING")
# os.environ['LANGCHAIN_ENDPOINT'] = os.getenv("LANGSMITH_ENDPOINT")
# os.environ['LANGCHAIN_PROJECT'] = os.getenv("LANGSMITH_PROJECT")
# os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGSMITH_API_KEY")
# os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")


# host = "127.0.0.1"
# port = 8666


# client = PathwayVectorClient(host=host, port=port)

# retriever = client.as_retriever()

# def parse_grade_response(response):
#     """Manual parser for ASI's response structure"""
#     response_json = json.loads(response)
#     try:
#         content = response_json["choices"][0]["message"]["content"]
#         return {"score": "yes" if "yes" in content.lower() else "no"}
#     except (KeyError, IndexError):
#         return {"score": "no"}



# # Data model
# class GradeDocuments(BaseModel):
#     """Binary score for relevance check on retrieved documents."""

#     binary_score: str = Field(
#         description="Documents are relevant to the question, 'yes' or 'no'"
#     )


# # llm = ChatGoogleGenerativeAI(
# #     model="gemini-2.0-flash",
# #     temperature=0,
# #     timeout=None,
# #     max_retries=2,
# #     # other params...
# # )


# structured_llm = llm.bind_tools([GradeDocuments])
# # structured_llm_grader_docs = llm.with_structured_output(GradeDocuments)

# # Prompt
# system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
#     It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
#     If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
#     Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
# grade_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
#     ]
# )

# retrieval_grader = grade_prompt | llmChat | JsonOutputToolsParser()


# # question = "self rag performance"
# # docs = retriever.get_relevant_documents(question)
# # doc_txt = docs[1].page_content
# # print(retrieval_grader.invoke({"question": question, "document": doc_txt}))



# # Prompt
# prompt = hub.pull("rlm/rag-prompt")


# # # Post-processing
# # def format_docs(docs):
# #     return "\n\n".join(doc.page_content for doc in docs)


# # # Chain
# rag_chain = prompt | llm | StrOutputParser()

# # # Run
# # generation = rag_chain.invoke({"context": docs, "question": question})
# # print(generation)


# class GradeHallucinations(BaseModel):
#     """Binary score for hallucination present in generation answer."""

#     binary_score: str = Field(
#         description="Answer is grounded in the facts, 'yes' or 'no'"
#     )

# structured_llm_grader_hall = llm.bind_tools([GradeHallucinations])



# # Prompt
# system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
#      Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
# hallucination_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
#     ]
# )

# # hallucination_grader = hallucination_prompt | structured_llm_grader_hall
# hallucination_grader = hallucination_prompt | structured_llm_grader_hall | JsonOutputToolsParser()
# # hallucination_grader.invoke({"documents": docs, "generation": generation})


# class GradeAnswer(BaseModel):
#     """Binary score to assess answer addresses question."""

#     binary_score: str = Field(
#         description="Answer addresses the question, 'yes' or 'no'"
#     )


# # structured_llm_grader_ans = llm.with_structured_output(GradeAnswer)
# structured_llm_grader_ans = llm.bind_tools([GradeAnswer])


# # Prompt
# system = """You are a grader assessing whether an answer addresses / resolves a question \n 
#      Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
# answer_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
#     ]
# )

# # answer_grader = answer_prompt | structured_llm_grader_ans
# answer_grader = answer_prompt | structured_llm_grader_ans | JsonOutputToolsParser()
# # answer_grader.invoke({"question": question, "generation": generation})


# # Prompt
# system = """You a question re-writer that converts an input question to a better version that is optimized \n 
#      for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
# re_write_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         (
#             "human",
#             "Here is the initial question: \n\n {question} \n Formulate an improved question.",
#         ),
#     ]
# )

# question_rewriter = re_write_prompt | llm | StrOutputParser()
# # question_rewriter.invoke({"question": question})




# class GraphState(TypedDict):
#     """
#     Represents the state of our graph.

#     Attributes:
#         question: question
#         generation: LLM generation
#         documents: list of documents
#     """

#     question: str
#     generation: str
#     documents: List[str]

# def retrieve(state):
#     """
#     Retrieve documents

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): New key added to state, documents, that contains retrieved documents
#     """
#     print("---RETRIEVE---")
#     question = state["question"]

#     # Retrieval
#     documents = retriever.get_relevant_documents(question)
#     return {"documents": documents, "question": question}


# def generate(state):
#     """
#     Generate answer

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): New key added to state, generation, that contains LLM generation
#     """
#     print("---GENERATE---")
#     question = state["question"]
#     documents = state["documents"]

#     # RAG generation
#     generation = rag_chain.invoke({"context": documents, "question": question})
#     return {"documents": documents, "question": question, "generation": generation}


# def grade_documents(state):
#     """
#     Determines whether the retrieved documents are relevant to the question.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): Updates documents key with only filtered relevant documents
#     """

#     print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
#     question = state["question"]
#     documents = state["documents"]

#     # Score each doc
#     filtered_docs = []
#     for d in documents:
#         score = retrieval_grader.invoke(
#             {"question": question, "document": d.page_content}
#         )
#         grade = score.binary_score
#         if grade == "yes":
#             print("---GRADE: DOCUMENT RELEVANT---")
#             filtered_docs.append(d)
#         else:
#             print("---GRADE: DOCUMENT NOT RELEVANT---")
#             continue
#     return {"documents": filtered_docs, "question": question}


# def transform_query(state):
#     """
#     Transform the query to produce a better question.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): Updates question key with a re-phrased question
#     """

#     print("---TRANSFORM QUERY---")
#     question = state["question"]
#     documents = state["documents"]

#     # Re-write question
#     better_question = question_rewriter.invoke({"question": question})
#     return {"documents": documents, "question": better_question}


# ### Edges


# def decide_to_generate(state):
#     """
#     Determines whether to generate an answer, or re-generate a question.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         str: Binary decision for next node to call
#     """

#     print("---ASSESS GRADED DOCUMENTS---")
#     state["question"]
#     filtered_documents = state["documents"]

#     if not filtered_documents:
#         # All documents have been filtered check_relevance
#         # We will re-generate a new query
#         print(
#             "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
#         )
#         return "transform_query"
#     else:
#         # We have relevant documents, so generate answer
#         print("---DECISION: GENERATE---")
#         return "generate"


# def grade_generation_v_documents_and_question(state):
#     """
#     Determines whether the generation is grounded in the document and answers question.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         str: Decision for next node to call
#     """

#     print("---CHECK HALLUCINATIONS---")
#     question = state["question"]
#     documents = state["documents"]
#     generation = state["generation"]

#     score = hallucination_grader.invoke(
#         {"documents": documents, "generation": generation}
#     )
#     grade = score.binary_score

#     # Check hallucination
#     if grade == "yes":
#         print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
#         # Check question-answering
#         print("---GRADE GENERATION vs QUESTION---")
#         score = answer_grader.invoke({"question": question, "generation": generation})
#         grade = score.binary_score
#         if grade == "yes":
#             print("---DECISION: GENERATION ADDRESSES QUESTION---")
#             return "useful"
#         else:
#             print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
#             return "not useful"
#     else:
#         print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
#         return "not supported"



# workflow = StateGraph(GraphState)

# # Define the nodes
# workflow.add_node("retrieve", retrieve)  # retrieve
# workflow.add_node("grade_documents", grade_documents)  # grade documents
# workflow.add_node("generate", generate)  # generatae
# workflow.add_node("transform_query", transform_query)  # transform_query

# # Build graph
# workflow.add_edge(START, "retrieve")
# workflow.add_edge("retrieve", "grade_documents")
# workflow.add_conditional_edges(
#     "grade_documents",
#     decide_to_generate,
#     {
#         "transform_query": "transform_query",
#         "generate": "generate",
#     },
# )
# workflow.add_edge("transform_query", "generate")
# workflow.add_conditional_edges(
#     "generate",
#     grade_generation_v_documents_and_question,
#     {
#         "not supported": "generate",
#         "useful": END,
#         "not useful": END,
#     },
# )

# # Compile
# app = workflow.compile()


# inputs = {}

# financial_expert_template = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             (
#                 "You are a highly knowledgeable financial expert. "
#                 "You provide extremely accurate reports with precise calculations and detailed data analysis. "
#                 "Your responses include comprehensive context and well-supported predictions."
#                 "Your answer includes all the analysis over the data that you can possibly do. Donot wait for user to reprompt you."
#             ),
#         ),
#         ("human", "{question}"),
#     ]
# )

# def run(query):
#     # First, use the new template to reformat (or 'refine') the user's query.
#     refined_question = financial_expert_template.format(question=query)
#     # Set the refined query in the input state
#     inputs["question"] = refined_question  
#     result = app.invoke(inputs)
#     return result["generation"]

# # # Example usage:
# # user_query = input("Enter your query: ")
# # result = run(user_query)
# # print("Raw result:", result[8:-1])
# # print("Type of result:", type(result))


import os
import json
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langchain_community.vectorstores import PathwayVectorClient
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from langchain_core.runnables import RunnableParallel
from langgraph.graph import END, StateGraph, START
from utils.asiChat import llmChat


MAX_RETRIES = 0 # Maximum number of retries for document grading
K = 8  # Number of documents to retrieve

# Custom parser for ASI responses
def parse_asi_response(response: str) -> Dict[str, Any]:
    """Parse ASI API response and extract content with error handling"""
    try:
        response_data = json.loads(response)
        return {
            "content": response_data["choices"][0]["message"]["content"],
            "thoughts": response_data.get("thought", [])
        }
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        return {"content": "", "thoughts": []}

# Custom grader parser
# def parse_grade_response(response: str) -> dict:
#     try:
#         parsed = json.loads(response)
#         thoughts = parsed.get("thoughts", [])
#         return {
#             "binary_score": parsed.get("binary_score", "no"),
#             "reason": thoughts[0] if thoughts else "No reason provided"
#         }
#     except Exception as e:
#         print(f"Error parsing response: {e}")
#         return {
#             "binary_score": "no",
#             "reason": "Failed to parse thoughts"
#         }

# New parser for summary scoring (expects a numeric score as string, returns float)
def parse_summary_score(response: str) -> float:
    try:
        response_data = json.loads(response)
        # Extract the numeric string from the assistant's message.
        numeric_str = response_data["choices"][0]["message"]["content"].strip()
        score = float(numeric_str)
        return score
    except Exception as e:
        print(f"Error parsing summary score: {e}")
        return 0.0


def call_llm_chat_with_prompt(prompt_value):
    messages = [{"role": m.type if m.type != "human" else "user", "content": m.content} for m in prompt_value.messages]
    return llmChat(messages, temperature=0.4)


# Initialize components
host = "127.0.0.1"
port = 8666
client = PathwayVectorClient(host=host, port=port)
retriever = client.as_retriever(search_kwargs={"k": K})

# Grading prompts and chains
def create_grader_chain(system_prompt: str, input_template: str):
    """Factory for creating grader chains"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", input_template)
    ])
    return prompt | call_llm_chat_with_prompt | parse_summary_score


# # Document relevance grader
# document_grader = create_grader_chain(
#     system_prompt=(
#         "You are a grader assessing whether a retrieved financial document contains information that could be useful "
#         "for generating a clear, concise summary in response to a user query. \n\n"
#         "This is not a strict relevance check — even partial or indirect connections to the query are valuable if they offer "
#         "useful context, trends, patterns, or financial signals. \n\n"
#         "Grade 'yes' if the document includes data or insights that might help in forming an overview or summary. "
#         "Grade 'no' only if the document is clearly unrelated or off-topic."
#     ),
#     input_template="Retrieved Document: {document}\nUser Query: {question}"
# )

# # Summary quality grader
# summary_grader = create_grader_chain(
#     system_prompt="""You evaluate summaries. Mark as 'yes' if the summary provides a useful, accurate, and clear high-level answer to the question.""",
#     input_template="User Question: {question}\n Summary: {generation}"
# )

# Create a new summary scorer chain (rates summary quality on a scale of 1 to 10)
summary_score_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a grader who rates the quality of a financial summary on a scale from 1 to 10. Provide only the numeric rating."),
    ("human", "Summary: {generation}\nRate the quality of this summary.")
])
summary_scorer = summary_score_prompt | call_llm_chat_with_prompt | parse_summary_score


# RAG chain
prompt = hub.pull("rlm/rag-prompt")
rag_chain = (
    {"context": lambda x: x["documents"], "question": lambda x: x["question"]}
    | prompt
    | call_llm_chat_with_prompt
    | parse_asi_response
)

# Query rewriter
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", "You're helping improve summary clarity. Given a user query, rephrase it to be clearer, broader, or easier to summarize. Look at the input and try to reason about the underlying semantic intent/meaning."),
    ("human", "Here is the initial question: \n\n {question} \n Formulate an improved question.")
])
question_rewriter = rewrite_prompt | call_llm_chat_with_prompt | parse_asi_response

# State management
class GraphState(TypedDict):
    question: str
    generation: Dict[str, Any]
    documents: List[Any]
    grade: Dict[str, str]
    retries: int  # NEW
    best_score: float      # store best summary score
    best_summary: str      # store best summary text
    score: float           # current summary score


# Workflow nodes
def retrieve(state: GraphState):
    print("---RETRIEVING DOCUMENTS---")
    documents = retriever.get_relevant_documents(state["question"], k=K)
    return {**state, "documents": documents}

# def grade_documents(state: GraphState):
#     print("---GRADING DOCUMENTS---")
#     filtered = []
#     for doc in state["documents"]:
#         result = document_grader.invoke({
#             "question": state["question"],
#             "document": doc.page_content
#         })
#         print(f"Grade result: {result}")
#         if result["binary_score"] == "yes":
#             filtered.append(doc)
    
#     # If no good docs and retry limit not hit
#     retries = state.get("retries", 0)
#     if not filtered and retries < MAX_RETRIES:
#         return {**state, "documents": [], "retries": retries + 1}
    
#     return {**state, "documents": filtered}


def generate(state: GraphState):
    print("---GENERATING ANSWER---")
    response = rag_chain.invoke({
        "question": state["question"],
        "documents": state["documents"]
    })
    # Store thoughts in generation trace
    if "trace" not in state:
        state["trace"] = []
    state["trace"].append({"thoughts": response.get("thoughts", [])})
    return {**state, "generation": response}

# def check_summary_quality(state: GraphState):
#     print("---CHECKING SUMMARY QUALITY---")
#     result = summary_grader.invoke({
#         "question": state["question"],
#         "generation": state["generation"]["content"]
#     })
#     return {**state, "grade": result}

def score_summary(state: GraphState):
    print("---SCORING SUMMARY---")
    current_score = summary_scorer.invoke({
        "generation": state["generation"]["content"]
    })
    # Update best summary if current score is higher or equal to the stored best
    if "best_score" not in state or current_score >= state["best_score"]:
        state["best_score"] = current_score
        state["best_summary"] = state["generation"]["content"]
    state["score"] = current_score
    print(f"Current summary score: {current_score}, Best score so far: {state.get('best_score', 'N/A')}")
    return state


def transform_query(state: GraphState):
    print("---IMPROVING QUESTION---")
    result = question_rewriter.invoke({"question": state["question"]})
    return {
        **state,
        "question": result["content"],  # use improved question
        "retries": state.get("retries", 0) + 1  # increment retry count
    }


# Decision logic
# def decide_to_generate(state: GraphState):
#     if not state["documents"]:
#         print("---NO RELEVANT DOCS: TRANSFORM QUERY---")
#         return "transform_query"
#     print("---DOCS AVAILABLE: GENERATE---")
#     return "generate"

def final_decision(state: GraphState):
    if state.get("retries", 0) >= MAX_RETRIES:
        print("---MAX RETRIES REACHED---")
        best_score = state.get("best_score", 0)
        if best_score >= 5:
            print(f"---Returning best stored summary with score: {best_score}")
            state["generation"]["content"] = state["best_summary"]
        else:
            print(f"---Best summary score ({best_score}) is below threshold. Clearing summary output.")
            state["generation"]["content"] = ""
        return END
    else:
        if state.get("score", 0) >= 5:
            print("---Current summary score is sufficient. Ending workflow.")
            return END
        print("---Summary needs improvement. Transforming query.")
        return "transform_query"



# Build workflow
workflow = StateGraph(GraphState)
# workflow.add_node("retrieve", retrieve)
# workflow.add_node("grade_docs", grade_documents)
# workflow.add_node("generate", generate)
# workflow.add_node("check_summary", check_summary_quality)
# workflow.add_node("transform_query", transform_query)

# workflow.set_entry_point("retrieve")
# workflow.add_edge("retrieve", "grade_docs")
# workflow.add_conditional_edges(
#     "grade_docs",
#     decide_to_generate,
#     {"transform_query": "transform_query", "generate": "generate"}
# )
# workflow.add_edge("generate", "check_summary")
# workflow.add_conditional_edges(
#     "check_summary",
#     final_decision,
#     {"transform_query": "transform_query", END: END}
# )
# workflow.add_edge("transform_query", "retrieve")
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.add_node("score_summary", score_summary)  # Node to score the generated summary
workflow.add_node("transform_query", transform_query)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "score_summary")
workflow.add_conditional_edges(
    "score_summary",
    final_decision,
    {END: END, "transform_query": "transform_query"}
)
workflow.add_edge("transform_query", "retrieve")


app = workflow.compile()

# Financial expert integration
def run(query: str):
    financial_prompt = ChatPromptTemplate.from_messages([
        ("system",
            "You are a financial summarizer assistant. Given documents and a query, "
            "generate a **clear, concise overview** with key takeaways, trends, and insights. "
            "Do not include detailed calculations unless crucial. Focus on high-level clarity.",
        ),
        ("human", "{question}")
    ])
    refined_query = financial_prompt.format(question=query)
    result = app.invoke({"question": refined_query})

    return result.get("generation", {})
