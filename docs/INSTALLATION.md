# Installation Guide

Complete step-by-step instructions for setting up the Hybrid RAG Project on your local machine.

## System Requirements

### Operating Systems
- macOS (10.15 or later)
- Linux (Ubuntu 20.04+, or similar)
- Windows 10/11 (with WSL2 recommended)

### Software Requirements
- **Python 3.9 or higher**
- **8GB RAM minimum** (16GB recommended for large datasets)
- **5GB disk space** (for models and dependencies)
- **Internet connection** (for initial setup only)

## Quick Setup (Automated)

### For macOS/Linux

1. **Download the project** (extract the zip file you received)

2. **Open Terminal** and navigate to the project:
```bash
cd /path/to/hybrid-rag-project
```

3. **Run the setup script**:
```bash
./setup.sh
```

The script will:
- ✅ Check Python version
- ✅ Install and verify Ollama
- ✅ Download required AI models
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Test the installation

4. **Add your documents**:
```bash
cp /path/to/your/files/* data/
```

5. **Run a test**:
```bash
source .venv/bin/activate
python hybrid_rag.py
```

Done! The system is ready to use.

## Manual Setup (Step-by-Step)

### Step 1: Install Python

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

**Verify installation:**
```bash
python3 --version
# Should show: Python 3.9.0 or higher
```

### Step 2: Install Ollama

Ollama runs the AI models locally on your computer.

**macOS/Linux:**
```bash
# Visit https://ollama.ai and download the installer
# Or use curl:
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai)

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
# Should return JSON with available models
```

### Step 3: Download AI Models

Download the required models (this may take 5-10 minutes):

```bash
# Embedding model (~275MB)
ollama pull nomic-embed-text

# LLM model (~4.7GB)
ollama pull llama3.1:latest
```

**Verify models are installed:**
```bash
ollama list
# Should show both models
```

### Step 4: Set Up the Project

1. **Extract the project** to your preferred location

2. **Navigate to the project directory:**
```bash
cd /path/to/hybrid-rag-project
```

3. **Create virtual environment:**
```bash
python3 -m venv .venv
```

4. **Activate virtual environment:**

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

Your prompt should now show `(.venv)` prefix.

5. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages (~500MB).

### Step 5: Verify Installation

**Test the components:**
```bash
python3 -c "
from document_loader import DocumentLoaderUtility
from structured_query import StructuredQueryEngine
print('✅ All modules loaded successfully')
"
```

**Check configuration:**
```bash
cat config.yaml
```

Verify the settings match your setup (usually defaults are fine).

### Step 6: Add Your Documents

1. **Copy files to the data directory:**
```bash
cp /path/to/your/documents/*.pdf data/
cp /path/to/your/documents/*.txt data/
cp /path/to/your/documents/*.csv data/
```

2. **Verify files are there:**
```bash
ls -lh data/
```

Supported formats: .txt, .pdf, .md, .docx, .csv

### Step 7: Run Your First Query

**Option A: Command Line Demo**
```bash
python hybrid_rag.py
```

This will load your documents and run sample queries.

**Option B: REST API Server**
```bash
# Terminal 1: Start server
python mcp_server.py

# Terminal 2: Ingest documents
curl -X POST http://localhost:8000/ingest

# Terminal 3: Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What information is available?"}'
```

**Option C: Claude Desktop Integration**
See "Claude Desktop Setup" section below.

## Claude Desktop Setup

If you want to use Claude Desktop to query your documents:

### Step 1: Find Your Config File

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add MCP Server Configuration

Add this to your `claude_desktop_config.json` (replace `/absolute/path/to/` with your actual path):

```json
{
  "mcpServers": {
    "hybrid-rag": {
      "command": "/absolute/path/to/hybrid-rag-project/.venv/bin/python",
      "args": [
        "/absolute/path/to/hybrid-rag-project/mcp_server_claude.py"
      ],
      "env": {
        "PATH": "/absolute/path/to/hybrid-rag-project/.venv/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```

**For macOS example:**
```json
{
  "mcpServers": {
    "hybrid-rag": {
      "command": "/Users/yourname/hybrid-rag-project/.venv/bin/python",
      "args": [
        "/Users/yourname/hybrid-rag-project/mcp_server_claude.py"
      ],
      "env": {
        "PATH": "/Users/yourname/hybrid-rag-project/.venv/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

### Step 4: Test in Claude

In Claude Desktop, you should now see MCP tools available. Try:

```
"List available datasets"
"Ingest my documents"
"Check ingestion status"
"Count people named Michael in contacts"
```

## Troubleshooting

### Python Not Found
```bash
# Install Python
# macOS:
brew install python@3.11

# Linux:
sudo apt install python3.11

# Windows: Download from python.org
```

### Ollama Not Starting
```bash
# macOS: Check if running
pgrep ollama

# Start Ollama
ollama serve

# In new terminal, verify
curl http://localhost:11434/api/tags
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Module Import Errors
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Permission Denied on setup.sh
```bash
chmod +x setup.sh
./setup.sh
```

### Ollama Models Not Downloading
```bash
# Check internet connection
# Check disk space (need ~5GB)
df -h

# Retry download
ollama pull nomic-embed-text
ollama pull llama3.1:latest
```

### Claude Desktop MCP Not Working
1. Verify the absolute paths are correct (no ~, use full paths)
2. Ensure .venv/bin/python exists: `ls -la /path/to/project/.venv/bin/python`
3. Test MCP server manually: `/path/to/.venv/bin/python mcp_server_claude.py`
4. Check Claude Desktop logs for errors
5. Restart Claude Desktop completely

### "No documents found"
```bash
# Check data directory
ls -la data/

# Add sample documents
echo "This is a test document." > data/test.txt

# Verify supported formats
# Supported: .txt, .pdf, .md, .docx, .csv
```

## Configuration

### Changing Ollama Models

Edit `config.yaml`:

```yaml
ollama:
  embedding_model: "nomic-embed-text"  # Or another embedding model
  llm_model: "llama3.1:latest"         # Or: llama2, mistral, codellama, etc.
```

Available models: https://ollama.ai/library

### Adjusting Performance

For better performance, edit `config.yaml`:

```yaml
retrieval:
  vector_search_k: 3  # More results = better context, slower
  keyword_search_k: 3
```

For large datasets (>10,000 documents), consider:
- Using smaller embedding models
- Reducing k values
- Adding more RAM

## System Architecture

After installation, your system will have:

```
hybrid-rag-project/
├── data/              ← Your documents go here
├── chroma_db/         ← Vector database (auto-created)
├── .venv/             ← Python virtual environment
└── [Python scripts]   ← Ready to run
```

## Quick Start Commands

```bash
# Always activate the environment first
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Run demo
python hybrid_rag.py

# Start REST API
python mcp_server.py

# Test structured queries
python -c "
from structured_query import StructuredQueryEngine
engine = StructuredQueryEngine('./data')
print('Datasets:', [ds['name'] for ds in engine.get_available_datasets()])
"
```

## Getting Help

### Documentation Files
- `README.md` - Main documentation
- `INSTALLATION.md` - This file
- `STRUCTURED_QUERIES.md` - CSV querying guide
- `ASYNC_INGESTION.md` - Async ingestion details
- `SHUTDOWN.md` - Server management

### Common Issues

**"Module not found"** → Activate virtual environment
**"Ollama connection error"** → Start Ollama: `ollama serve`
**"No documents found"** → Add files to `data/` directory
**"Out of memory"** → Reduce dataset size or increase RAM

### Support Resources
- Ollama Docs: https://ollama.ai/docs
- LangChain Docs: https://python.langchain.com/
- Python Virtual Environments: https://docs.python.org/3/tutorial/venv.html

## Updating the System

To update dependencies:
```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

To update Ollama models:
```bash
ollama pull nomic-embed-text
ollama pull llama3.1:latest
```

## Uninstalling

To remove the system:
```bash
# Deactivate virtual environment
deactivate

# Remove the project directory
cd ..
rm -rf hybrid-rag-project

# Optionally remove Ollama models
ollama rm nomic-embed-text
ollama rm llama3.1:latest
```

## Success Checklist

Before you start using the system, verify:

- ✅ Python 3.9+ installed (`python3 --version`)
- ✅ Ollama installed (`ollama --version`)
- ✅ Ollama running (`curl http://localhost:11434/api/tags`)
- ✅ Models downloaded (`ollama list`)
- ✅ Virtual environment created (`.venv/` directory exists)
- ✅ Dependencies installed (`pip list | grep langchain`)
- ✅ Data directory ready (`ls data/`)
- ✅ Test script runs (`python hybrid_rag.py`)

If all items are checked, you're ready to go!

## Next Steps

1. **Add your documents** to the `data/` directory
2. **Read the README.md** for usage examples
3. **Run `python hybrid_rag.py`** to test with your data
4. **Explore the API** with `python mcp_server.py`
5. **Set up Claude Desktop** to query via MCP

Happy querying!
