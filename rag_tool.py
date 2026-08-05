from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool




load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)


embeddings = GoogleGenerativeAIEmbeddings(
	model = "gemini-embedding-001"
)

vector_store = ""

def ingest_rag_document(file_path):
	DB_PATH = "faiss_db"
	loader = PyPDFLoader(file_path)
	docs = loader.load()
	splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
	chunks = splitter.split_documents(docs)
	vector_store = FAISS.from_documents(chunks,embeddings)
	vector_store.save_local(DB_PATH)



def retrieval_rag_document():
	DB_PATH = "faiss_db"
	vector_store = FAISS.load_local(
		folder_path=DB_PATH,
		embeddings=embeddings,
		allow_dangerous_deserialization=True
	)
	retriever = vector_store.as_retriever(search_type="similarity",search_kwargs={'k':4})
	return retriever