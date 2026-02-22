from data_connectors.pdf_connector import get_brochure_vectorstore
from langchain_core.tools import tool
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from core_agents.llm_config import local_llm

@tool
def search_brochures_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about car details from unstructured PDF brochures.
    Synthesizes an answer based strictly on the retrieved document context.
    """
    try:
        vectorstore = get_brochure_vectorstore()
        if vectorstore is None:
            return "No PDF brochures are currently available. Please add PDF files to the data directory."

        # Setup RAG chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        prompt = ChatPromptTemplate.from_template('''Answer the following question based only on the provided context. If the answer is not in the context, say so.
        
<context>
{context}
</context>

Question: {input}''')

        document_chain = create_stuff_documents_chain(local_llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        response = retrieval_chain.invoke({"input": query_str})
        
        return response.get("answer", "Failed to retrieve an answer from the brochures.")
        
    except Exception as e:
        return f"Brochure search failed: {e}. Please ask the user to rephrase their question."
