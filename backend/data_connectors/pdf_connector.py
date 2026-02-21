import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Configure global generic embedding model for RAG so everything uses localhost
# This requires no API keys, runs purely locally
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Path where PDFs will be stored
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def get_brochure_index():
    """
    Reads all PDF files from the data directory and builds an in-memory 
    VectorStoreIndex using local HuggingFace embeddings.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory at {DATA_DIR}. Please add PDFs here.")
        # Return an empty index to prevent crashing if directory is initially empty
        return VectorStoreIndex.from_documents([])

    try:
        # SimpleDirectoryReader automatically uses PyMuPDF under the hood for PDFs
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        if not documents:
            print("No documents found in data directory.")
            return VectorStoreIndex.from_documents([])
        
        index = VectorStoreIndex.from_documents(documents)
        return index
    except Exception as e:
        print(f"Error loading documents for RAG: {e}")
        return VectorStoreIndex.from_documents([])

def search_brochures_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about car details from unstructured PDF brochures.
    """
    index = get_brochure_index()
    query_engine = index.as_query_engine()
    response = query_engine.query(query_str)
    return str(response)
