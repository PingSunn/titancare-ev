from data_connectors.pdf_connector import get_brochure_vectorstore
from langchain_core.tools import tool

@tool
def search_brochures_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about car details from unstructured PDF brochures.
    """
    vectorstore = get_brochure_vectorstore()
    if vectorstore is None:
        return "No PDF brochures are currently available. Please add PDF files to the data directory."

    # Retrieve relevant documents
    docs = vectorstore.similarity_search(query_str, k=3)
    if not docs:
        return "No relevant information found in the brochures."

    return "\n\n".join([doc.page_content for doc in docs])
