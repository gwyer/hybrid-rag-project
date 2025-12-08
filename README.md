# Hybrid RAG Project

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A generalized Retrieval-Augmented Generation (RAG) system with hybrid search capabilities that works with any documents you provide. Combines semantic (dense vector) search and keyword (sparse BM25) search for optimal document retrieval, with an MCP server API for easy integration.

> 🎯 **Key Features**: Multi-format support • Local LLM • Claude Desktop integration • Structured data queries • Document-type-aware retrieval

## Overview

This project implements a hybrid RAG system that combines:
- **Semantic Search**: Dense vector embeddings for understanding meaning and context
- **Keyword Search**: BM25 sparse retrieval for exact keyword matching
- **Hybrid Fusion**: Reciprocal Rank Fusion (RRF) to combine results from both methods
- **MCP Server**: Both REST API and Model Context Protocol server for Claude integration
- **Multi-format Support**: Automatically loads documents from various file formats

The hybrid approach ensures better retrieval accuracy by leveraging the strengths of both search methods.

## Features

- Vector-based semantic search using Chroma and Ollama embeddings
- BM25 keyword search for exact term matching
- Ensemble retriever with Reciprocal Rank Fusion (RRF)
- Integration with local Ollama LLM for answer generation
- Support for multiple document formats (TXT, PDF, MD, DOCX, CSV)
- Automated document loading from data directory
- RESTful API server with `/ingest` and `/query` endpoints
- Model Context Protocol (MCP) server for Claude Desktop/API integration
- Configuration-driven architecture (no hardcoded values)
- Persistent vector store for faster subsequent queries

## Architecture

```
User Documents → data/ directory
                      ↓
            Document Loader
                      ↓
Query → Hybrid Retriever → [Vector Retriever + BM25 Retriever]
                         → RRF Fusion
                         → Retrieved Context
                         → LLM (Ollama)
                         → Final Answer
```

## Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running locally
3. Required Ollama models:
   - `llama3.1:latest` (or another LLM model)
   - `nomic-embed-text` (or another embedding model)

### Installing Ollama

Visit [ollama.ai](https://ollama.ai) to download and install Ollama for your platform.

After installation, pull the required models:

```bash
ollama pull llama3.1:latest
ollama pull nomic-embed-text
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd hybrid-rag-project
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
hybrid-rag-project/
├── src/
│   └── hybrid_rag/            # Core application package
│       ├── __init__.py        # Package initialization
│       ├── document_loader.py # Document loading utility
│       ├── structured_query.py# CSV query engine
│       └── utils.py           # Logging and utility functions
├── scripts/
│   ├── run_demo.py            # Main demonstration script
│   ├── mcp_server.py          # REST API server
│   └── mcp_server_claude.py   # MCP server for Claude integration
├── config/
│   ├── config.yaml            # Configuration file
│   └── claude_desktop_config.json # Sample Claude Desktop MCP config
├── docs/
│   ├── INSTALLATION.md        # Detailed installation guide
│   ├── STRUCTURED_QUERIES.md  # CSV query documentation
│   ├── ASYNC_INGESTION.md     # Async ingestion guide
│   └── SHUTDOWN.md            # Shutdown handling guide
├── data/                      # Drop your documents here
├── chroma_db/                 # Vector store (auto-created)
├── tests/                     # Unit tests (future)
├── setup.py                   # Package setup file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
├── SampleData.py.backup       # Original sample code (backup)
├── .gitignore                 # Git ignore rules
└── .venv/                     # Virtual environment (not tracked)
```

## Configuration

All settings are managed in `config/config.yaml`:

```yaml
# Ollama Configuration
ollama:
  base_url: "http://localhost:11434"
  embedding_model: "nomic-embed-text"
  llm_model: "llama3.1:latest"

# Data Configuration
data:
  directory: "./data"
  supported_formats:
    - "txt"
    - "pdf"
    - "md"
    - "docx"
    - "csv"

# Retrieval Configuration
retrieval:
  vector_search_k: 2
  keyword_search_k: 2

# MCP Server Configuration
mcp_server:
  host: "0.0.0.0"
  port: 8000

# Vector Store Configuration
vector_store:
  persist_directory: "./chroma_db"
```

Modify this file to:
- Use different Ollama models
- Change the data directory location
- Adjust retrieval parameters (k values)
- Configure server host/port
- Change vector store persistence location

## Usage

### Option 1: Command Line Script

1. **Add your documents** to the `data/` directory:
```bash
cp /path/to/your/documents/*.pdf data/
cp /path/to/your/documents/*.txt data/
```

2. **Run the script**:
```bash
python scripts/run_demo.py
```

The script will:
- Load all supported documents from the `data/` directory
- Initialize Ollama embeddings and LLM
- Create vector and BM25 retrievers
- Build the hybrid RAG chain
- Execute sample queries and display results

### Option 2: REST API Server

1. **Start the REST API server**:
```bash
python scripts/mcp_server.py
```

The server will start on `http://localhost:8000`

**To stop the server:** Press `Ctrl+C` for graceful shutdown

2. **Ingest documents** (do this first):
```bash
curl -X POST http://localhost:8000/ingest
```

Response:
```json
{
  "status": "success",
  "message": "Documents ingested successfully",
  "documents_loaded": 15
}
```

3. **Query documents**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of these documents?"}'
```

Response:
```json
{
  "answer": "Based on the documents...",
  "context": [
    {
      "content": "Document text...",
      "source": "example.pdf",
      "type": ".pdf"
    }
  ]
}
```

4. **Check server status**:
```bash
curl http://localhost:8000/status
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/ingest` | POST | Load documents from data/ directory |
| `/query` | POST | Query documents with hybrid search |
| `/status` | GET | Get system status and configuration |

### Option 3: Claude Desktop/API via MCP

The MCP (Model Context Protocol) server allows Claude to directly query your local RAG system.

#### Setup for Claude Desktop

1. **First, add documents to your data directory**:
```bash
cp /path/to/your/documents/*.pdf data/
```

2. **Edit the `config/claude_desktop_config.json` file** to use the correct absolute path:
```json
{
  "mcpServers": {
    "hybrid-rag": {
      "command": "python",
      "args": [
        "/absolute/path/to/hybrid-rag-project/scripts/mcp_server_claude.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/hybrid-rag-project"
      }
    }
  }
}
```

3. **Add this configuration to Claude Desktop**:

   **On macOS**:
   ```bash
   # Copy the configuration
   mkdir -p ~/Library/Application\ Support/Claude
   # Edit the file and add your MCP server configuration
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   **On Windows**:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

   **On Linux**:
   ```
   ~/.config/Claude/claude_desktop_config.json
   ```

4. **Restart Claude Desktop**

5. **In Claude Desktop, you'll now see the MCP tools available**. You can ask Claude:
   - "Use the ingest_documents tool to load my documents"
   - "Query my documents about [your question]"
   - "Check the status of the RAG system"

#### Available MCP Tools

Claude will have access to these tools:

**Document Ingestion & Search:**
- **`ingest_documents`**: Start loading and indexing documents asynchronously from the data/ directory
- **`get_ingestion_status`**: Monitor the progress of document ingestion (percentage, current file, stage)
- **`query_documents`**: Query the documents using hybrid search (semantic + keyword)
- **`get_status`**: Check the RAG system status

**Structured Data Queries (for CSV files):**
- **`list_datasets`**: List all available CSV datasets with columns and row counts
- **`count_by_field`**: Count rows where a field matches a value (e.g., "count people named Michael")
- **`filter_dataset`**: Get all rows matching field criteria (e.g., "all people from Company X")
- **`get_dataset_stats`**: Get statistics about a dataset (rows, columns, memory usage)

#### Async Ingestion with Progress Tracking

The ingestion process now runs asynchronously with real-time progress updates:

- **Non-blocking**: Ingestion runs in the background
- **Progress tracking**: See percentage complete (0-100%)
- **File-level updates**: Know which file is currently being processed
- **Stage information**: Loading files (0-80%) → Building index (80-100%) → Completed
- **Status monitoring**: Check progress at any time with `get_ingestion_status`

#### Example Usage with Claude

```
You: "Please start ingesting my documents"
Claude: [Uses ingest_documents tool]
        "Ingestion started. Use get_ingestion_status to monitor progress."

You: "Check the ingestion status"
Claude: [Uses get_ingestion_status tool]
        "Ingestion Status: In Progress
         Progress: 45%
         Stage: loading_files
         Files Processed: 9/20
         Current File: document.pdf
         Documents Loaded: 15"

You: "Check status again"
Claude: [Uses get_ingestion_status tool]
        "Ingestion Status: Completed ✅
         Progress: 100%
         Total Files Processed: 20
         Total Documents Loaded: 35

         You can now use query_documents to search the documents."

You: "What are the main topics in my documents?"
Claude: [Uses query_documents tool with your question]
        "Based on the documents, the main topics are..."
```

#### Structured Data Queries

For CSV files, use structured query tools for exact counts and filtering:

```
You: "List available datasets"
Claude: [Uses list_datasets tool]
        "Available Datasets:
         📊 contacts
            Rows: 24,697
            Columns (7): First Name, Last Name, URL, Email Address, Company, Position, Connected On"

You: "Count how many people are named Michael in the contacts dataset"
Claude: [Uses count_by_field tool with dataset="contacts", field="First Name", value="Michael"]
        "Count Result:
         Dataset: contacts
         Field: First Name
         Value: Michael
         Count: 226 out of 24,697 total rows (0.92%)"

You: "Show me all the Michaels"
Claude: [Uses filter_dataset tool]
        "Filter Results:
         Found: 226 rows
         Showing: 100 rows (truncated to 100)

         [1] First Name: Michael | Last Name: Randel | Company: Randel Consulting Associates ..."
```

**When to use each approach:**
- **Structured queries** (`count_by_field`, `filter_dataset`): For exact counts, filtering, and structured data
- **Semantic search** (`query_documents`): For conceptual questions, understanding content, summarization

## Supported File Formats

The system automatically loads and processes these formats:
- `.txt` - Plain text files
- `.pdf` - PDF documents
- `.md` - Markdown files
- `.docx` - Microsoft Word documents
- `.csv` - CSV files

Simply drop any supported files into the `data/` directory!

## How It Works

### Document Loading

The `DocumentLoaderUtility` class:
1. Scans the `data/` directory recursively
2. Identifies supported file formats
3. Uses appropriate loaders for each format
4. Adds metadata (source file, file type) to each document
5. Returns a list of `Document` objects ready for indexing

### Hybrid Retrieval

The `EnsembleRetriever` uses Reciprocal Rank Fusion (RRF) to:
1. Retrieve top-k results from vector search (semantic)
2. Retrieve top-k results from BM25 search (keyword)
3. Assign reciprocal rank scores to each result
4. Combine scores to produce a unified ranking
5. Return the most relevant documents overall

This approach handles:
- Semantic queries ("How do I request time off?")
- Keyword queries ("PTO form HR-42")
- Complex queries benefiting from both methods

## Customization

### Using Different Models

Edit `config/config.yaml` to change models:

```yaml
ollama:
  embedding_model: "your-embedding-model"
  llm_model: "your-llm-model"
```

### Adjusting Retrieval Parameters

Modify the `k` values in `config/config.yaml`:

```yaml
retrieval:
  vector_search_k: 5   # Return top 5 from semantic search
  keyword_search_k: 5  # Return top 5 from keyword search
```

### Adding More File Format Support

Edit `src/hybrid_rag/document_loader.py` to add more loaders:

```python
self.supported_loaders = {
    '.txt': TextLoader,
    '.pdf': PyPDFLoader,
    '.json': JSONLoader,  # Add this
    # ... more formats
}
```

### Customizing the Prompt

Edit the prompt template in `scripts/run_demo.py` or `scripts/mcp_server.py`:

```python
prompt = ChatPromptTemplate.from_template("""
Your custom prompt here...

<context>
{context}
</context>

Question: {input}
""")
```

## Development Workflow

1. **Add documents** to `data/` directory
2. **Modify configuration** in `config/config.yaml` as needed
3. **Test with command line**: `python scripts/run_demo.py`
4. **Deploy MCP server**: `python scripts/mcp_server.py`
5. **Integrate via API** in your applications

## Troubleshooting

### "Error connecting to Ollama"

- Ensure Ollama is installed and running
- Check that the Ollama service is accessible at the configured URL
- Verify models are downloaded: `ollama list`

### "No documents found in data directory"

- Add files to the `data/` directory
- Ensure files have supported extensions (.txt, .pdf, .md, .docx, .csv)
- Check the `config/config.yaml` data directory path is correct

### "ModuleNotFoundError"

- Ensure virtual environment is activated: `source .venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Poor Retrieval Results

- Add more relevant documents to the `data/` directory
- Adjust `k` values in `config/config.yaml`
- Try different embedding models
- Ensure query terminology matches document content

### API Errors

- Ensure you call `/ingest` before `/query`
- Check server logs for detailed error messages
- Verify Ollama is running and accessible
- Check that documents were successfully loaded

## Example: Complete Workflow

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Add your documents
cp ~/my-docs/*.pdf data/

# 3. Start MCP server
python scripts/mcp_server.py &

# 4. Ingest documents
curl -X POST http://localhost:8000/ingest

# 5. Query your documents
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the key points"}'

# 6. Check status
curl http://localhost:8000/status
```

## Dependencies

Core libraries:
- `langchain`: Framework for LLM applications
- `langchain-community`: Community integrations
- `langchain-ollama`: Ollama integration
- `chromadb`: Vector database for embeddings
- `rank-bm25`: BM25 implementation for keyword search
- `fastapi`: Web framework for API
- `uvicorn`: ASGI server
- `pyyaml`: YAML configuration parsing

Document loaders:
- `pypdf`: PDF processing
- `python-docx`: Word document processing
- `unstructured`: Markdown and other formats

## Performance Tips

1. **Vector Store Persistence**: The vector store is persisted to disk (`chroma_db/`) after ingestion, making subsequent queries faster.

2. **Batch Processing**: When adding many documents, use the `/ingest` endpoint once rather than multiple times.

3. **Retrieval Parameters**: Lower `k` values (e.g., 2-3) are faster and often sufficient for small document sets.

4. **Model Selection**: Smaller embedding models are faster but may sacrifice some accuracy.

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

## Changelog

### Version 2.0.0
- Generalized system to work with any documents
- Added `data/` directory for document ingestion
- Created `DocumentLoaderUtility` for multi-format support
- Restructured project to follow Python best practices (src layout)
- Moved all configuration to `config/` directory
- Moved all documentation to `docs/` directory
- Created proper Python package structure with `setup.py`
- Organized scripts into `scripts/` directory
- Updated all import paths and documentation

### Version 1.0.0
- Initial implementation with sample HR documents
- Basic hybrid search with vector and BM25 retrievers
