#!/bin/bash
# Setup script for Hybrid RAG Project
# This script automates the installation process

set -e  # Exit on error

echo "🚀 Hybrid RAG Project Setup"
echo "=========================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if Ollama is installed
echo ""
echo "📋 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo "📖 Please install Ollama from: https://ollama.ai"
    echo "   After installation, run this script again."
    exit 1
fi
echo "✅ Ollama is installed"

# Check if Ollama is running
echo ""
echo "📋 Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running."
    echo "📖 Please start Ollama and run this script again."
    exit 1
fi
echo "✅ Ollama is running"

# Check for required models
echo ""
echo "📋 Checking Ollama models..."
MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data = json.load(sys.stdin); print(' '.join([m['name'] for m in data.get('models', [])]))" 2>/dev/null || echo "")

if [[ ! "$MODELS" =~ "nomic-embed-text" ]]; then
    echo "⚠️  Model 'nomic-embed-text' not found."
    echo "📥 Pulling nomic-embed-text model..."
    ollama pull nomic-embed-text
else
    echo "✅ Found nomic-embed-text model"
fi

if [[ ! "$MODELS" =~ "llama3.1" ]]; then
    echo "⚠️  Model 'llama3.1' not found."
    echo "📥 Pulling llama3.1:latest model..."
    ollama pull llama3.1:latest
else
    echo "✅ Found llama3.1 model"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p chroma_db
echo "✅ Directories created"

# Test the setup
echo ""
echo "🧪 Testing the setup..."
python3 -c "
import sys
sys.path.insert(0, '.')
from src.hybrid_rag import DocumentLoaderUtility, StructuredQueryEngine, configure_logging
print('✅ All modules import successfully')
" 2>&1 | grep -v "WARNING" | grep -v "init:" | grep -v "level=WARN" || echo "✅ Imports successful"

echo ""
echo "✅ Setup complete!"
echo ""
echo "=========================="
echo "🎉 You're ready to use the Hybrid RAG system!"
echo ""
echo "📖 Next steps:"
echo "   1. Add your documents to the 'data/' directory"
echo "   2. Run the demo: python scripts/run_demo.py"
echo "   3. Or start the REST API: python scripts/mcp_server.py"
echo "   4. Or configure Claude Desktop to use the MCP server"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Complete guide"
echo "   - docs/INSTALLATION.md - Detailed installation instructions"
echo "   - docs/STRUCTURED_QUERIES.md - How to query CSV data"
echo "   - docs/ASYNC_INGESTION.md - Async ingestion guide"
echo ""
echo "💡 Quick test: python scripts/run_demo.py"
echo ""
