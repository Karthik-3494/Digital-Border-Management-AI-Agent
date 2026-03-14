from langchain_core.tools import tool

from image_extract import convert
from mongodb_connect import entry_db, exit_db, get_data
from RAG_rules import rag_model

@tool
def image_extractor(id):
    """Scans the uploaded image to get text data from it"""
    return convert(id)

@tool
def enter(id,info):
    """Used to update the database when some traveler enters"""
    entry_db(id, info)

@tool
def exit(id,info):
    """Used to update the database when some traveler exits"""
    exit_db(id, info)

@tool
def retrieve_data(id):
    """Used to retrieve data from database"""
    retrieved_data = get_data(id)
    return retrieved_data

@tool
def rag_system(info, action = None):
    """Used to compare the retrieved or given dictionary info about traveler with the legal documents in the vector database in RAG system to check if the person must be allowed or not"""
    response = rag_model(info,action = None)
    return response

    