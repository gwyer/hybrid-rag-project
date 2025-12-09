#!/usr/bin/env python3
"""
MCP Server for Claude Desktop/API Integration
Allows Claude to query the hybrid RAG system via Model Context Protocol.
"""
import asyncio
import signal
import sys
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers import EnsembleRetriever

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.hybrid_rag import (
    DocumentLoaderUtility,
    StructuredQueryEngine,
    configure_logging,
    create_document_type_aware_retriever
)

# Configure logging to suppress warnings
configure_logging()

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.parent.absolute()

# Load configuration
def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = SCRIPT_DIR / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Global RAG system components
config = load_config()
embeddings = None
llm = None
vectorstore = None
rag_chain = None
documents = []
structured_query_engine = None

# Ingestion status tracking
ingestion_status = {
    "status": "not_started",  # not_started, in_progress, completed, failed
    "progress": 0,  # 0-100
    "current_file": "",
    "files_processed": 0,
    "total_files": 0,
    "documents_loaded": 0,
    "error_message": None,
    "stage": ""  # loading_files, building_index, completed
}
ingestion_task = None


def initialize_rag_system():
    """Initialize the RAG system with embeddings, LLM, and retrievers."""
    global embeddings, llm, structured_query_engine

    try:
        ollama_url = config['ollama']['base_url']
        embedding_model = config['ollama']['embedding_model']
        llm_model = config['ollama']['llm_model']

        embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        llm = OllamaLLM(model=llm_model, base_url=ollama_url)

        # Initialize structured query engine
        data_dir = config['data']['directory']
        if not Path(data_dir).is_absolute():
            data_dir = str(SCRIPT_DIR / data_dir)
        structured_query_engine = StructuredQueryEngine(data_dir)

        return True
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        return False


def build_rag_chain():
    """Build the RAG chain with document-type-aware hybrid retrieval."""
    global vectorstore, rag_chain, documents

    if not documents:
        raise ValueError("No documents loaded. Please ingest documents first.")

    # Create vector store
    persist_dir = config['vector_store']['persist_directory']
    # Convert to absolute path if it's relative
    if not Path(persist_dir).is_absolute():
        persist_dir = str(SCRIPT_DIR / persist_dir)
    vectorstore = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=persist_dir
    )

    # Check if we should use separate retrievers
    use_separate = config.get('document_processing', {}).get('use_separate_retrievers', False)

    if use_separate:
        # Use the new document-type-aware retriever
        print("🔧 Using document-type-aware retriever (CSV vs Text separation)")
        hybrid_retriever = create_document_type_aware_retriever(
            documents=documents,
            vectorstore=vectorstore,
            config=config
        )
    else:
        # Use traditional ensemble retriever (backward compatible)
        print("🔧 Using traditional ensemble retriever")
        vector_k = config['retrieval']['vector_search_k']
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": vector_k})

        keyword_retriever = BM25Retriever.from_documents(documents)
        keyword_k = config['retrieval']['keyword_search_k']
        keyword_retriever.k = keyword_k

        hybrid_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever]
        )

    # Define prompt - simplified for Claude to use the context
    prompt = ChatPromptTemplate.from_template("""
Use the following context to answer the question. If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {input}
""")

    # Create RAG chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(hybrid_retriever, document_chain)


def update_ingestion_progress(current: int, total: int, filename: str):
    """Callback to update ingestion progress."""
    global ingestion_status
    ingestion_status["files_processed"] = current
    ingestion_status["total_files"] = total
    ingestion_status["current_file"] = filename
    # Progress is 80% for file loading, 20% for index building
    file_progress = int((current / total) * 80) if total > 0 else 0
    ingestion_status["progress"] = file_progress


async def ingest_documents_async():
    """Async function to ingest documents in the background."""
    global documents, ingestion_status

    try:
        # Reset status
        ingestion_status.update({
            "status": "in_progress",
            "progress": 0,
            "current_file": "",
            "files_processed": 0,
            "total_files": 0,
            "documents_loaded": 0,
            "error_message": None,
            "stage": "loading_files"
        })

        data_dir = config['data']['directory']
        # Convert to absolute path if it's relative
        if not Path(data_dir).is_absolute():
            data_dir = str(SCRIPT_DIR / data_dir)

        loader = DocumentLoaderUtility(data_dir, config=config)

        # Load documents with progress callback
        documents = await asyncio.to_thread(
            loader.load_documents,
            progress_callback=update_ingestion_progress
        )

        if not documents:
            ingestion_status.update({
                "status": "failed",
                "error_message": "No documents found in data directory",
                "progress": 0
            })
            return

        ingestion_status.update({
            "progress": 80,
            "stage": "building_index",
            "documents_loaded": len(documents)
        })

        # Build RAG chain
        await asyncio.to_thread(build_rag_chain)

        ingestion_status.update({
            "status": "completed",
            "progress": 100,
            "stage": "completed"
        })

    except Exception as e:
        ingestion_status.update({
            "status": "failed",
            "error_message": str(e),
            "progress": 0
        })


async def ingest_documents() -> Dict[str, Any]:
    """Start document ingestion as a background task."""
    global ingestion_task, ingestion_status

    # Check if ingestion is already in progress
    if ingestion_status["status"] == "in_progress":
        return {
            "success": False,
            "message": "Ingestion already in progress",
            "progress": ingestion_status["progress"]
        }

    # Start async ingestion task
    ingestion_task = asyncio.create_task(ingest_documents_async())

    return {
        "success": True,
        "message": "Document ingestion started. Use get_ingestion_status to monitor progress.",
        "status": "in_progress"
    }


async def query_documents(query: str) -> Dict[str, Any]:
    """Query the ingested documents using hybrid search."""
    global rag_chain

    if rag_chain is None:
        return {
            "success": False,
            "answer": "RAG system not initialized. Please ingest documents first.",
            "context": []
        }

    try:
        response = rag_chain.invoke({"input": query})

        context = [
            {
                "content": doc.page_content[:500],  # Limit context length
                "source": doc.metadata.get('source_file', 'unknown'),
                "type": doc.metadata.get('file_type', 'unknown')
            }
            for doc in response['context']
        ]

        return {
            "success": True,
            "answer": response['answer'],
            "context": context
        }
    except Exception as e:
        return {
            "success": False,
            "answer": f"Error processing query: {str(e)}",
            "context": []
        }


# Create MCP server
server = Server("hybrid-rag-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for Claude to use."""
    return [
        Tool(
            name="ingest_documents",
            description="Start loading and indexing documents from the data directory asynchronously. "
                       "This will scan the data/ directory for supported files (txt, pdf, md, docx, csv) "
                       "and create a hybrid search index. Use get_ingestion_status to monitor progress.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_ingestion_status",
            description="Get the current status and progress of document ingestion. "
                       "Returns progress percentage, current file being processed, and overall status. "
                       "Use this to monitor the ingestion process started by ingest_documents.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="query_documents",
            description="Query the ingested documents using hybrid search (semantic + keyword). "
                       "Returns relevant context from the documents and an answer generated by the local LLM. "
                       "Use this to retrieve information from the loaded documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or query to search for in the documents"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_status",
            description="Get the current status of the RAG system, including whether documents are loaded "
                       "and system configuration.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_datasets",
            description="List all available structured datasets (CSV files) with their columns and row counts. "
                       "Use this to discover what data is available before querying.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="count_by_field",
            description="Count rows in a dataset where a field matches a value. "
                       "Perfect for queries like 'how many people named Michael' or 'count of entries from Company X'. "
                       "Returns exact count and sample results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset": {
                        "type": "string",
                        "description": "Name of the dataset (e.g., 'contacts' for contacts.csv)"
                    },
                    "field": {
                        "type": "string",
                        "description": "Column name to filter on (e.g., 'First Name', 'Company')"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to match (case-insensitive, supports partial matches)"
                    }
                },
                "required": ["dataset", "field", "value"]
            }
        ),
        Tool(
            name="filter_dataset",
            description="Get all rows from a dataset where a field matches a value. "
                       "Use this to retrieve all records matching criteria (e.g., 'all people named Michael'). "
                       "Returns up to 100 rows by default.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset": {
                        "type": "string",
                        "description": "Name of the dataset"
                    },
                    "field": {
                        "type": "string",
                        "description": "Column name to filter on"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to match"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (default: 100)"
                    }
                },
                "required": ["dataset", "field", "value"]
            }
        ),
        Tool(
            name="get_dataset_stats",
            description="Get statistics and metadata about a dataset including row count, columns, and sample data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset": {
                        "type": "string",
                        "description": "Name of the dataset"
                    }
                },
                "required": ["dataset"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from Claude."""
    global ingestion_status, structured_query_engine

    if name == "ingest_documents":
        result = await ingest_documents()
        return [
            TextContent(
                type="text",
                text=f"Ingestion {'started' if result['success'] else 'failed'}.\n"
                     f"Message: {result['message']}"
            )
        ]

    elif name == "get_ingestion_status":
        status = ingestion_status.copy()

        # Format status message
        if status["status"] == "not_started":
            status_text = "Ingestion Status: Not started\nUse ingest_documents to begin loading documents."
        elif status["status"] == "in_progress":
            status_text = f"""Ingestion Status: In Progress
Progress: {status['progress']}%
Stage: {status['stage']}
Files Processed: {status['files_processed']}/{status['total_files']}
Current File: {status['current_file']}
Documents Loaded: {status['documents_loaded']}"""
        elif status["status"] == "completed":
            status_text = f"""Ingestion Status: Completed ✅
Progress: 100%
Total Files Processed: {status['files_processed']}
Total Documents Loaded: {status['documents_loaded']}

You can now use query_documents to search the documents."""
        elif status["status"] == "failed":
            status_text = f"""Ingestion Status: Failed ❌
Error: {status['error_message']}
Files Processed: {status['files_processed']}/{status['total_files']}"""
        else:
            status_text = f"Unknown status: {status['status']}"

        return [TextContent(type="text", text=status_text)]

    elif name == "query_documents":
        query = arguments.get("query", "")
        if not query:
            return [TextContent(type="text", text="Error: Query parameter is required")]

        result = await query_documents(query)

        if not result['success']:
            return [TextContent(type="text", text=f"Error: {result['answer']}")]

        # Format response with context
        context_text = "\n\n".join([
            f"Source: {ctx['source']}\n{ctx['content']}"
            for ctx in result['context']
        ])

        response_text = f"Answer: {result['answer']}\n\n---\n\nContext used:\n{context_text}"

        return [TextContent(type="text", text=response_text)]

    elif name == "get_status":
        status = {
            "rag_initialized": rag_chain is not None,
            "documents_loaded": len(documents),
            "ollama_url": config['ollama']['base_url'],
            "embedding_model": config['ollama']['embedding_model'],
            "llm_model": config['ollama']['llm_model'],
            "data_directory": config['data']['directory']
        }

        status_text = "\n".join([f"{key}: {value}" for key, value in status.items()])
        return [TextContent(type="text", text=f"RAG System Status:\n{status_text}")]

    elif name == "list_datasets":

        if structured_query_engine is None:
            return [TextContent(type="text", text="Structured query engine not initialized")]

        datasets = structured_query_engine.get_available_datasets()

        if not datasets:
            return [TextContent(type="text", text="No CSV datasets found in the data directory")]

        dataset_text = "Available Datasets:\n\n"
        for ds in datasets:
            dataset_text += f"📊 **{ds['name']}**\n"
            dataset_text += f"   Rows: {ds['rows']:,}\n"
            dataset_text += f"   Columns ({ds['column_count']}): {', '.join(ds['columns'][:10])}"
            if ds['column_count'] > 10:
                dataset_text += f" ... and {ds['column_count'] - 10} more"
            dataset_text += "\n\n"

        return [TextContent(type="text", text=dataset_text)]

    elif name == "count_by_field":

        if structured_query_engine is None:
            return [TextContent(type="text", text="Structured query engine not initialized")]

        dataset = arguments.get("dataset", "")
        field = arguments.get("field", "")
        value = arguments.get("value", "")

        result = await asyncio.to_thread(
            structured_query_engine.count_by_field,
            dataset, field, value
        )

        if not result["success"]:
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        response_text = f"""Count Result:
Dataset: {dataset}
Field: {field}
Value: {value}
Count: {result['count']:,} out of {result['total_rows']:,} total rows

Sample Results ({min(5, len(result['sample']))} of {result['count']}):"""

        for i, record in enumerate(result['sample'], 1):
            response_text += f"\n\n[{i}] "
            response_text += " | ".join([f"{k}: {v}" for k, v in list(record.items())[:5]])

        return [TextContent(type="text", text=response_text)]

    elif name == "filter_dataset":

        if structured_query_engine is None:
            return [TextContent(type="text", text="Structured query engine not initialized")]

        dataset = arguments.get("dataset", "")
        field = arguments.get("field", "")
        value = arguments.get("value", "")
        limit = arguments.get("limit", 100)

        result = await asyncio.to_thread(
            structured_query_engine.filter_by_field,
            dataset, field, value, limit
        )

        if not result["success"]:
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        response_text = f"""Filter Results:
Dataset: {dataset}
Field: {field}
Value: {value}
Found: {result['count']:,} rows
Showing: {len(result['results'])} rows"""

        if result.get('truncated'):
            response_text += f" (truncated to {limit})"

        response_text += "\n\n"

        for i, record in enumerate(result['results'], 1):
            response_text += f"\n[{i}] "
            response_text += " | ".join([f"{k}: {v}" for k, v in record.items()])

        return [TextContent(type="text", text=response_text)]

    elif name == "get_dataset_stats":

        if structured_query_engine is None:
            return [TextContent(type="text", text="Structured query engine not initialized")]

        dataset = arguments.get("dataset", "")

        result = await asyncio.to_thread(
            structured_query_engine.get_stats,
            dataset
        )

        if not result["success"]:
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        response_text = f"""Dataset Statistics:
Dataset: {result['dataset']}
Total Rows: {result['rows']:,}
Total Columns: {result['columns']}
Memory Usage: {result['memory_usage']}

Columns: {', '.join(result['column_names'])}

Sample Row:"""

        for k, v in result['sample_row'].items():
            response_text += f"\n  {k}: {v}"

        return [TextContent(type="text", text=response_text)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def cleanup():
    """Cleanup function to run on shutdown."""
    global ingestion_task, vectorstore

    print("\n🛑 Shutting down MCP server...")

    # Cancel any running ingestion task
    if ingestion_task and not ingestion_task.done():
        print("⏸️  Cancelling ingestion task...")
        ingestion_task.cancel()
        try:
            await ingestion_task
        except asyncio.CancelledError:
            pass

    # Clean up vector store connection if exists
    if vectorstore:
        print("💾 Closing vector store...")
        try:
            # ChromaDB doesn't require explicit cleanup, but this is here for future use
            vectorstore = None
        except Exception as e:
            print(f"⚠️  Error closing vector store: {e}")

    print("✅ Cleanup complete")


async def main():
    """Run the MCP server with graceful shutdown handling."""
    # Track if we're shutting down
    shutdown_event = asyncio.Event()

    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}")
        shutdown_event.set()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize RAG system on startup
        print("Initializing Hybrid RAG MCP Server...")
        if initialize_rag_system():
            print("✅ RAG system initialized successfully")
        else:
            print("⚠️  RAG system initialization failed - please check Ollama connection")

        print("🚀 Starting MCP server for Claude...")
        print("💡 Press Ctrl+C to stop the server")

        async with stdio_server() as (read_stream, write_stream):
            # Create task for server
            server_task = asyncio.create_task(
                server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="hybrid-rag-mcp",
                        server_version="1.0.0",
                        capabilities=server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
            )

            # Wait for either server to complete or shutdown signal
            shutdown_task = asyncio.create_task(shutdown_event.wait())
            done, pending = await asyncio.wait(
                [server_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    except KeyboardInterrupt:
        print("\n⌨️  Keyboard interrupt received")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always run cleanup
        await cleanup()
        print("👋 Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
