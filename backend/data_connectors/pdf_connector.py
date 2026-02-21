import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Path where PDFs will be stored
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Initialize the embedding model (runs locally, no API keys needed)
_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
_vectorstore = None

def get_brochure_vectorstore():
    """
    Loads all PDF files from the data directory and builds an in-memory
    FAISS VectorStore using local HuggingFace embeddings.
    Returns the FAISS retriever, or None if no documents are found.
    """
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory at {DATA_DIR}. Please add PDFs here.")
        return None

    all_docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                loader = PyMuPDFLoader(filepath)
                all_docs.extend(loader.load())
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    if not all_docs:
        print("No PDF documents found in data directory.")
        return None

    _vectorstore = FAISS.from_documents(all_docs, _embeddings)
    return _vectorstore
