import os
from crewai import  LLM
from crewai_tools import (PDFSearchTool,
                          DOCXSearchTool,
                          TXTSearchTool,
                          CSVSearchTool,
                          WebsiteSearchTool,
                          ScrapeWebsiteTool)



def resetChroma():
    
    import chromadb
    from chromadb.config import Settings
    path ="db/" 
    if os.path.isdir(path):
        client = chromadb.PersistentClient(path=path, settings=Settings(allow_reset=True))

        client.reset()  # Réinitialise la base de données
        state = True
    else : 
        state = False
    print(f"Chromadb reset : {state}")
    return state

def ChooseLLM(name=""):
    
    if name == "" : 
        name = "openai"

    if name=="local":
        # selected_llm = ChatOpenAI(model="mistral-7b-local", base_url="http://localhost:1552/v1")
        
        selected_llm = LLM(
            model="ollama/mistral",
            base_url="http://localhost:11434"
        )

    elif name=="mistral":
        # API_KEY = os.getenv("MISTRAL_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/mixtral-8x7b-32768")
        selected_llm = LLM(
            model="mistral/mistral-medium-latest",
            temperature=0.2
        )
        
    elif name=="groq":
        # API_KEY = os.getenv("GROQ_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/mixtral-8x7b-32768")
        selected_llm = LLM(
            model="groq/mixtral-8x7b-32768",
            temperature=0.2
        )
    
    elif name=="groq-llama":
        # API_KEY = os.getenv("GROQ_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/llama-3.1-70b-versatile")
        selected_llm = LLM(
            model="groq/llama-3.1-70b-versatile",
            temperature=0.2
        )
    elif name=="groq-llama3":
        # API_KEY = os.getenv("GROQ_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/llama-3.1-70b-versatile")
        selected_llm = LLM(
            model="groq/llama3-8b-8192",
            temperature=0.2
        )
    elif name=="openai":
        selected_llm = LLM(
            model="gpt-4",
            temperature=0.2
        )
        
    elif name=="claude":
        selected_llm = LLM(
            model="claude-3-5-sonnet-20240620",
            temperature=0.2
        )

    else:
        selected_llm = LLM(
            model="gpt-3.5-turbo",
            temperature=0.2
        )
    return selected_llm




def choose_tool(src):
    """Choisit le bon outil en fonction de l'extension du fichier."""
    _, extension = os.path.splitext(src)
    extension = extension.lower()

    if src.startswith('http'):
        print("[INFO] Outil sélectionné : ScrapeWebsiteTool")
        return ScrapeWebsiteTool(website_url=src)
    elif src.endswith('.chat'):
        print("[INFO] Outil sélectionné : Pas de fichier")
        return None
    
    if extension == '.pdf':
        print("[INFO] Outil sélectionné : PDFSearchTool")
        return PDFSearchTool(pdf=src)
    elif extension == '.txt':
        print("[INFO] Outil sélectionné : TXTSearchTool")
        return TXTSearchTool(txt=src)
    elif extension == '.csv':
        print("[INFO] Outil sélectionné : CSVSearchTool")
        return CSVSearchTool(csv=src)
    elif extension == '.docx':
        print("[INFO] Outil sélectionné : DOCXSearchTool")
        return DOCXSearchTool(docx=src)
    else:
        return WebsiteSearchTool(website=src)
    
