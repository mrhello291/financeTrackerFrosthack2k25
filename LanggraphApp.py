from typing_extensions import TypedDict
from typing import List
from utils.DocumentParsingAgent import process_pdfs
from utils.DocumentParsingAgent2 import extract_transactions, process_all_files
from agents.GetReleventTransaction import get_relevance, get_relevant_transactions
from agents.GetUserQueryOutput import answerQuery
from langgraph.graph import END, StateGraph
from pprint import pprint


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        query: query
        JsonGeneration: LLM JSonGeneration
        FilterJsonGeneration: LLM JSonGeneration
        Output: str
    """
    query : str
    JSonGeneration : List
    FilterJsonGeneration : List
    Output : str


#define nodes 

def parse(state):
    """
    Parses the input using the DocumentParsingAgent2.

    Args:
        state (GraphState): The state of the graph.

    Returns:
        GraphState: The updated state of the graph.
    """
    
    print("\n ------Parsing the input---------. \n")
    ptd = process_pdfs("INFO/data")
    ftd = process_all_files(ptd)
    state["JSonGeneration"] = ftd
    print("\n ------Parsed the input successfully---------. \n")
    return state

    
def relevance(state):
    """
    Gets the relevant transactions using the GetReleventTransaction agent.

    Args:
        state (GraphState): The state of the graph.

    Returns:
        GraphState: The updated state of the graph.
    """
    
    print("\n ------Getting relevant transactions---------. \n")
    flq = get_relevance(state["query"])
    fld = get_relevant_transactions(flq, state["JSonGeneration"])
    state["FilterJsonGeneration"] = fld
    print("\n ------Got relevant transactions successfully---------. \n")
    return state


def ans(state):
    """
    Answers the user's query using the GetUserQueryOutput agent.

    Args:
        state (GraphState): The state of the graph.

    Returns:
        GraphState: The updated state of the graph.
    """
    
    print("\n ------Answering the query---------. \n")
    an = answerQuery(state["query"], state["FilterJsonGeneration"])
    print("\n ------Answer of the query---------. \n",an,"\n")
    state["Output"] = an
    print("\n ------Answered the query successfully---------. \n")
    return state


# Define the state graph
graph = StateGraph(GraphState)
graph.add_node("parse", parse)
graph.add_node("relevance", relevance)
graph.add_node("ans", ans)

graph.set_entry_point("parse")

graph.add_edge("parse", "relevance")
graph.add_edge("relevance", "ans")
# Define the initial state
initial_state = GraphState(
    query="",
    JSonGeneration=[],
    FilterJsonGeneration=[],
    Output=""
)
# Define the main function
def main():
    """
    Main function to run the state graph.
    """
    
    # Get user input
    query = input("Enter your query: ")
    initial_state["query"] = query

    # Run the state graph
    app = graph.compile()
    
    for answer in app.stream(initial_state):
        for key,value in answer.items():
            pprint(f"NODE: {key}")
        pprint("--------------------------------------------------")
    pprint("Final Answer:")
    pprint(value["Output"])

if __name__ == "__main__":
    main()