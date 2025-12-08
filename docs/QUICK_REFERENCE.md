# Quick Reference Card

## Installation (5 Minutes)

```bash
# 1. Extract the zip file
unzip hybrid-rag-project_*.zip
cd hybrid-rag-project

# 2. Run setup (installs everything)
./setup.sh

# 3. Add your documents
cp /path/to/your/files/* data/

# 4. Test it
source .venv/bin/activate
python hybrid_rag.py
```

Done! System is ready.

## Three Ways to Use

### 1. Command Line (Simplest)
```bash
source .venv/bin/activate
python hybrid_rag.py
```
Runs demo queries on your documents.

### 2. REST API (For Apps)
```bash
# Start server
python mcp_server.py

# Ingest docs (do once)
curl -X POST http://localhost:8000/ingest

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question"}'
```

### 3. Claude Desktop (Conversational)
1. Edit Claude Desktop config (see INSTALLATION.md)
2. Restart Claude Desktop
3. Ask Claude: "Ingest my documents"
4. Ask Claude: "What's in these documents?"

## Common Tasks

### Add Documents
```bash
cp ~/Documents/*.pdf data/
cp ~/data.csv data/
```

### Query CSV Data
In Claude Desktop:
```
"List datasets"
"Count people named John in contacts"
"Show all Microsoft employees"
```

### Query Text Documents
```
"What are the main topics?"
"Summarize the key points"
"Explain the vacation policy"
```

### Check Status
```
"Get ingestion status"  # Check progress
"Get system status"     # Check config
```

### Stop Servers
```bash
Ctrl+C  # In any running server terminal
```

## File Formats Supported

- ✅ `.txt` - Text files
- ✅ `.pdf` - PDF documents
- ✅ `.md` - Markdown files
- ✅ `.docx` - Word documents
- ✅ `.csv` - CSV spreadsheets

## Configuration

Edit `config.yaml` to change:
- Ollama models
- Data directory location
- Retrieval parameters
- Server port

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ollama connection error" | Run: `ollama serve` |
| "No documents found" | Add files to `data/` folder |
| "Module not found" | Run: `source .venv/bin/activate` |
| "Permission denied" | Run: `chmod +x setup.sh` |
| MCP not working | Check absolute paths in config |

## Key Commands

```bash
# Setup
./setup.sh

# Activate environment (always do this first!)
source .venv/bin/activate

# Run demo
python hybrid_rag.py

# Start REST API
python mcp_server.py

# Install new models
ollama pull <model-name>

# List installed models
ollama list

# Stop server
Ctrl+C
```

## Documentation

- `START_HERE.txt` - First steps
- `INSTALLATION.md` - Full installation
- `README.md` - Complete guide
- `STRUCTURED_QUERIES.md` - CSV queries
- `ASYNC_INGESTION.md` - Progress tracking
- `SHUTDOWN.md` - Server management

## URLs

- Local API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama: https://ollama.ai
- LangChain: https://python.langchain.com

## Tips

💡 Always activate the virtual environment first: `source .venv/bin/activate`

💡 Use structured queries for CSV (exact counts), semantic search for text (concepts)

💡 Check ingestion status while documents are loading

💡 The vector database is cached in `chroma_db/` for fast reuse

💡 Your data never leaves your computer - everything runs locally

## Help

For detailed help, see the documentation files above.
For setup issues, see INSTALLATION.md troubleshooting section.
