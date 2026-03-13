from typing import TypedDict, Dict
from tools import *
from langchain_core.messages import HumanMessage, AIMessage

class agentstate(TypedDict):
    person_id: str 
    scanned_data: Dict
    db_data: Dict
    rag_response: str
    action: str  
    manual_inputs: Dict 

def extract_node(state: agentstate) -> agentstate:
    scanned = image_extractor.invoke({"id": state["person_id"]})   
    if "manual_inputs" in state and state["manual_inputs"]:
        scanned.update(state["manual_inputs"])
    state["scanned_data"] = scanned
    return state

def db_node(state: agentstate) -> agentstate:
    action = state.get("action")
    if action == "enter":
        enter.invoke({"id": state["person_id"], "info": state["scanned_data"]})
    elif action == "exit":
        exit.invoke({"id": state["person_id"], "info": state["scanned_data"]})
    elif action == "retrieve":
        state["db_data"] = retrieve_data.invoke({"id": state["person_id"]})
    return state

def rag_node(state: agentstate) -> agentstate:
    info_to_pass = state.get("scanned_data") or state.get("db_data")
    state["rag_response"] = rag_system.invoke({"info": info_to_pass})
    return state