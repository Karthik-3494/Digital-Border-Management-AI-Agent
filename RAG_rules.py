from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from dotenv import load_dotenv

load_dotenv()

pdf_path = r"C:\Users\karth\OneDrive\Desktop\PROJECTS\digital_border_sys\info_files\usa.pdf"

loader = PyPDFLoader(pdf_path)
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
chunks = splitter.split_documents(pages)

embedder = OpenAIEmbeddings(model = "text-embedding-3-small")
vector_db = FAISS.from_documents(chunks, embedder)

retriever = vector_db.as_retriever(search_type = "similarity",search_kwargs={"k" : 20})

def rag_model(info, action):
    
    if isinstance(info, dict):
        retrieved_docs = retriever.invoke("Basis of allowing a traveler inside and include source metadata (page numbers) in results so the LLM can cite “page X” in verdicts.")
    else:
        retrieved_docs = retriever.invoke(info)
    
    context_text = "\n\n".join([f"Page {doc.metadata.get('page', 'Unknown')}: {doc.page_content}" for doc in retrieved_docs])

    model = ChatOpenAI(model = "gpt-4o")

    if isinstance(info, dict):
        prompt = PromptTemplate(
            template="""
            Traveler Action: {action}

            Traveler Information:
            {info}

            Relevant Immigration Rules:
            {data}

            If the traveler action is enter, decide:
            1. Allow Entry
            2. Deny Entry
            3. Send for Further Scrutiny

            If the traveler action is exit, decide:
            1. Allow Exit
            2. Stop Exit (legal or immigration violation)
            3. Send for Investigation

            Provide a decent reasoning based on the rules and then give the final verdict. sho your thinking

            Always cite the rule page numbers like: (Page X)

            DO NOT hallucinate rules.
            """,
            input_variables=["info", "data", "action"]
        )
    else:
        prompt = PromptTemplate(
            template = """
                Take this query - 
                {info}
                and the relevant data -
                {data}
                and answer it accordingly 
                Include source metadata (page numbers) in results so the LLM can cite “page X” in verdicts.
                If the user wants to leave and explicitly tells bye or something related to that, then just give a one
                word response "exit" from your side.
            """,
            input_variables=['info','data']
        )

    chain = prompt | model
    result = chain.invoke({"info" : info, "data" : context_text, "action":action})

    return result
    
