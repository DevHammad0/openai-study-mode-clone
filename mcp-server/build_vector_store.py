# build_vector_store.py
import os, glob
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from pydantic import SecretStr

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set")


# Loads all .txt documents recursively from the knowledge-base3/ directory using DirectoryLoader.
# Each document is enriched with a doc_type metadata field based on its filename (excluding extension)
documents = []
folders = glob.glob("knowledge-base/")
encoding_loader = {'encoding': 'utf-8'}
# encoding_loader={'autodetect_encoding': True}
for folder in folders:  
    docs_loader = DirectoryLoader(folder, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs=encoding_loader)
    docs_folder = docs_loader.load()
    for doc in docs_folder:
        file_name = os.path.basename(doc.metadata["source"])
        doc.metadata["page_title"] = os.path.splitext(file_name)[0]
        documents.append(doc)
    
print(f"[INFO] Loaded {len(documents)} documents")    
        
# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)

print(f"[INFO] Split {len(chunks)} chunks")

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=SecretStr(gemini_api_key))

# Check and delete the previous chroma datastore
ds_name = "vector_store"
if os.path.exists(ds_name):
    import shutil
    print(f"[INFO] Removing existing vector store directory: {ds_name}")
    shutil.rmtree(ds_name)

# Create the vector datastore with chunk embedding
vector_store = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=ds_name, client_settings=Settings(anonymized_telemetry=False))
print(f"Vector store created with {vector_store._collection.count()} chunks")
