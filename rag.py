import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("MODEL_EMBEDDING","embedding-3")
CHROMA_PATH = 


zhipu_client = OpenAI(
    api_key = os.getenv("ZHIPU_API_KEY"),
    base_url= os.getenv("ZHIPU_BASE_URL")
)

def build_knowledge_base() -> str :
    chromadb.PersistentClient()
    with open("knowledge.txt","r",encoding="utf-8") as con :
        text =  con.read()
    final_text = [ waiting_text.strip() for waiting_text in text.split("\n") if waiting_text.strip()]
    resp = zhipu_client.embeddings.create(
        model = MODEL,
        input = final_text
    )
    chromadb_client = 

    return len(final_text)

if __name__ == "__main__":
    build_knowledge_base()