from langgraph.graph import StateGraph, START, END
from nodes import *

graph = StateGraph(agentstate)

graph.add_node("extract", extract_node)
graph.add_node("database", db_node)
graph.add_node("rag", rag_node)

graph.add_edge(START, "extract")
graph.add_edge("extract", "database")
graph.add_edge("database", "rag")
graph.add_edge("rag", END)

app = graph.compile()

