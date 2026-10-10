import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("MODEL_EMBEDDING","embedding-3")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "course_knowledge"
KNOWLEDGE_FILE = "knowledge.txt" 

zhipu_client = OpenAI(
    api_key = os.getenv("ZHIPU_API_KEY"),
    base_url= os.getenv("ZHIPU_BASE_URL")
)

def build_knowledge_base() -> str :
    chroma_client = chromadb.PersistentClient(CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    if collection.count()>0:
        return f"该知识库已存在{collection.count()},跳过建库。"
    with open(KNOWLEDGE_FILE,"r",encoding="utf-8") as con :
        text =  con.read()
    documents = [ document.strip() for document in text.split("\n") if document.strip()]
    resp = zhipu_client.embeddings.create(
        model = MODEL,
        input = documents
    )
    embeddings = [ data.embedding for data in resp.data]
    ids=[]
    for number in range(0,len(documents)):
        ids.append(f"chunk-{number}")
    collection.add(ids = ids,documents=documents,embeddings=embeddings)
    return f"本次知识库创建{len(documents)}条"

def retrieve_knowledge(query : str,top_k : int = 3) -> str:
    chroma_client = chromadb.PersistentClient(CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    resp = zhipu_client.embeddings.create(
        model=MODEL,
        input=query
    )
    query_embeddings = [resp.data[0].embedding]
    results = collection.query(query_embeddings=query_embeddings,n_results=top_k)
    text = results["documents"][0]
    final_text = "\n\n".join(text)
    if not final_text:
        return "没有查找到相关知识点"
    return final_text
if __name__ == "__main__":
    print(build_knowledge_base())
    print(retrieve_knowledge("云服务器有哪几种服务模式？",3))