"""
MCP Server for Hybrid RAG System
Provides APIs for document ingestion and querying.
"""
import sys
import yaml
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers import EnsembleRetriever
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.hybrid_rag import DocumentLoaderUtility, configure_logging

# Configure logging at module load time to suppress warnings
configure_logging()


# Load configuration
def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Pydantic models for API
class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    context: List[Dict[str, str]]


class IngestResponse(BaseModel):
    status: str
    message: str
    documents_loaded: int


# Global variables for RAG components
config = load_config()

# RAG components (initialized on startup)
embeddings = None
llm = None
vectorstore = None
rag_chain = None
documents = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("🚀 Starting Hybrid RAG REST API Server...")
    if initialize_rag_system():
        print("✅ RAG system initialized successfully")
    else:
        print("⚠️  RAG system initialization failed - please check Ollama connection")

    yield

    # Shutdown
    print("\n🛑 Shutting down server...")
    global vectorstore
    if vectorstore:
        print("💾 Closing vector store...")
        vectorstore = None
    print("✅ Shutdown complete")


app = FastAPI(
    title="Hybrid RAG REST API Server",
    version="1.0.0",
    lifespan=lifespan
)


def initialize_rag_system():
    """Initialize the RAG system with embeddings, LLM, and retrievers."""
    global embeddings, llm, vectorstore, rag_chain, documents

    try:
        # Initialize Ollama embeddings and LLM
        ollama_url = config['ollama']['base_url']
        embedding_model = config['ollama']['embedding_model']
        llm_model = config['ollama']['llm_model']

        embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        llm = OllamaLLM(model=llm_model, base_url=ollama_url)

        print("✅ Ollama embeddings and LLM initialized.")
        return True
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return False


def build_rag_chain():
    """Build the RAG chain with hybrid retrieval."""
    global vectorstore, rag_chain, documents

    if not documents:
        raise ValueError("No documents loaded. Please ingest documents first.")

    # Create vector store
    persist_dir = config['vector_store']['persist_directory']
    vectorstore = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=persist_dir
    )
    vector_k = config['retrieval']['vector_search_k']
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": vector_k})

    # Create BM25 retriever
    keyword_retriever = BM25Retriever.from_documents(documents)
    keyword_k = config['retrieval']['keyword_search_k']
    keyword_retriever.k = keyword_k

    # Create hybrid retriever
    hybrid_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, keyword_retriever]
    )

    # Define prompt
    prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Answer the user's question based ONLY on the provided context.
If the context does not contain the answer, state clearly that the information is not available in the documents.

<context>
{context}
</context>

Question: {input}
""")

    # Create RAG chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(hybrid_retriever, document_chain)

    print("✅ RAG chain built successfully.")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "running",
        "service": "Hybrid RAG MCP Server",
        "version": "1.0.0"
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents():
    """
    Ingest documents from the data directory.
    Loads all supported files and builds the RAG chain.
    """
    global documents

    try:
        # Load documents
        data_dir = config['data']['directory']
        loader = DocumentLoaderUtility(data_dir)
        documents = loader.load_documents()

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No documents found in data directory. Please add files to the data/ folder."
            )

        # Build RAG chain
        build_rag_chain()

        return IngestResponse(
            status="success",
            message="Documents ingested successfully",
            documents_loaded=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the ingested documents using hybrid search.

    Args:
        request: QueryRequest containing the query string

    Returns:
        QueryResponse with answer and context
    """
    global rag_chain

    if rag_chain is None:
        raise HTTPException(
            status_code=400,
            detail="RAG chain not initialized. Please ingest documents first using /ingest endpoint."
        )

    try:
        # Execute query
        response = rag_chain.invoke({"input": request.query})

        # Format context
        context = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get('source_file', 'unknown'),
                "type": doc.metadata.get('file_type', 'unknown')
            }
            for doc in response['context']
        ]

        return QueryResponse(
            answer=response['answer'],
            context=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/status")
async def get_status():
    """Get the current status of the RAG system."""
    return {
        "rag_initialized": rag_chain is not None,
        "documents_loaded": len(documents),
        "config": {
            "ollama_url": config['ollama']['base_url'],
            "embedding_model": config['ollama']['embedding_model'],
            "llm_model": config['ollama']['llm_model'],
            "data_directory": config['data']['directory']
        }
    }


def main():
    """Run the REST API server with graceful shutdown."""
    host = config['mcp_server']['host']
    port = config['mcp_server']['port']

    print(f"🌐 Starting REST API server on {host}:{port}")
    print("💡 Press Ctrl+C to stop the server")

    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⌨️  Keyboard interrupt received")
    finally:
        print("👋 Server stopped")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
