from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from dotenv import load_dotenv

load_dotenv()

#loaded the rules pdf
pdf_path = r"C:\Users\karth\OneDrive\Desktop\PROJECTS\digital_border_sys\info_files\usa.pdf"

loader = PyPDFLoader(pdf_path)
pages = loader.load()

#splitting it into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
chunks = splitter.split_documents(pages)

#embedding and storing
embedder = OpenAIEmbeddings(model = "text-embedding-3-small")
vector_db = FAISS.from_documents(chunks, embedder)

#retriever 
retriever = vector_db.as_retriever(search_type = "similarity",search_kwargs={"k" : 20})

def rag_model(info):
    
    if isinstance(info, dict):
        retrieved_docs = retriever.invoke("Basis of allowing a traveler inside and include source metadata (page numbers) in results so the LLM can cite “page X” in verdicts.")
    else:
        retrieved_docs = retriever.invoke(info)
    
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])

    model = ChatOpenAI(model = "gpt-4o")

    if isinstance(info, dict):
        prompt = PromptTemplate(
            template = """
                Take this info about the traveler - 
                {info}
                and the relavent data -
                {data}
                Cross-check the details of this traveler with the RULES to decide if -
                    1. Let them Enter
                    2. Don't let them enter
                    3. Scrutinize even more with extensive security checks. 

                You can also refer to history of chats if available.
                Show me how you think and analyze with the given info but don't make it VERY big. Then give the final verdict
                include source metadata (page numbers) in results so the LLM can cite “page X” in verdicts.
                DO NOT HALLUCINATE.
            """,
            input_variables=['info','data']
        )
    else:
        prompt = PromptTemplate(
            template = """
                Take this query - 
                {info}
                and the relavent data -
                {data}
                and answer it accordingly 
                Include source metadata (page numbers) in results so the LLM can cite “page X” in verdicts.
            """,
            input_variables=['info','data']
        )

    chain = prompt | model
    result = chain.invoke({"info" : info, "data" : context_text})

    return result
    
