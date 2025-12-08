#!/bin/bash
# Package the Hybrid RAG Project for distribution
# Creates a clean zip file ready to send

set -e

echo "📦 Packaging Hybrid RAG Project for Distribution"
echo "================================================"
echo ""

# Configuration
PROJECT_NAME="hybrid-rag-project"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/dist"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="${PROJECT_NAME}_${TIMESTAMP}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📋 Preparing package..."

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/$PROJECT_NAME"

echo "📁 Copying files to temporary directory..."
mkdir -p "$PACKAGE_DIR"

# Copy root files
cp -r \
    requirements.txt \
    setup.sh \
    README.md \
    .gitignore \
    "$PACKAGE_DIR/"

# Copy config directory
mkdir -p "$PACKAGE_DIR/config"
cp config/*.yaml "$PACKAGE_DIR/config/"
cp config/*.json "$PACKAGE_DIR/config/" 2>/dev/null || true

# Copy src directory
mkdir -p "$PACKAGE_DIR/src/hybrid_rag"
cp src/hybrid_rag/*.py "$PACKAGE_DIR/src/hybrid_rag/"

# Copy scripts directory
mkdir -p "$PACKAGE_DIR/scripts"
cp scripts/*.py "$PACKAGE_DIR/scripts/"

# Copy docs directory
mkdir -p "$PACKAGE_DIR/docs"
cp docs/*.md "$PACKAGE_DIR/docs/" 2>/dev/null || true

# Copy setup.py if exists
cp setup.py "$PACKAGE_DIR/" 2>/dev/null || true

# Create data directory with examples
mkdir -p "$PACKAGE_DIR/data"
cp data/EXAMPLES.md "$PACKAGE_DIR/data/" 2>/dev/null || echo "No EXAMPLES.md found, skipping..."

# Create empty directories
mkdir -p "$PACKAGE_DIR/chroma_db"
touch "$PACKAGE_DIR/chroma_db/.gitkeep"

# Create a START_HERE.txt file
cat > "$PACKAGE_DIR/START_HERE.txt" << 'EOF'
HYBRID RAG PROJECT - QUICK START GUIDE
======================================

Welcome! This is a generalized RAG (Retrieval-Augmented Generation) system
that lets you query your own documents using AI.

QUICK START (macOS/Linux):
--------------------------
1. Open Terminal in this directory
2. Run: ./setup.sh
3. Add your documents to the data/ folder
4. Run: source .venv/bin/activate && python scripts/run_demo.py

QUICK START (Windows):
----------------------
1. Install Python 3.9+ from python.org
2. Install Ollama from ollama.ai
3. Open PowerShell in this directory
4. Run: python -m venv .venv
5. Run: .venv\Scripts\activate
6. Run: pip install -r requirements.txt
7. Add documents to data\ folder
8. Run: python scripts\run_demo.py

WHAT THIS DOES:
---------------
- Loads YOUR documents (PDFs, text files, CSVs, etc.)
- Creates a searchable AI-powered knowledge base
- Lets you query your data with natural language
- Works 100% locally (your data never leaves your computer)
- Supports both semantic search AND structured queries

DOCUMENTATION:
--------------
- docs/INSTALLATION.md - Detailed setup instructions
- README.md - Complete user guide
- docs/STRUCTURED_QUERIES.md - How to query CSV files
- docs/ASYNC_INGESTION.md - Progress tracking guide

REQUIREMENTS:
-------------
- Python 3.9 or higher
- Ollama (free, runs AI models locally)
- 8GB RAM minimum (16GB recommended)
- 5GB disk space for models

CLAUDE DESKTOP INTEGRATION:
---------------------------
If you use Claude Desktop, you can connect it to this system:
- See docs/INSTALLATION.md for Claude Desktop setup
- Allows Claude to query your local documents
- Your data stays on your computer

NEED HELP?
----------
1. Read docs/INSTALLATION.md for step-by-step setup
2. Check README.md for usage examples
3. See EXAMPLES.md in data/ folder for sample queries

Created with ❤️  - Enjoy!
EOF

# Create a version info file
cat > "$PACKAGE_DIR/VERSION.txt" << EOF
Hybrid RAG Project
Version: 2.0.0
Package Date: $(date +"%Y-%m-%d %H:%M:%S")
Python Required: 3.9+

Features:
- Hybrid search (semantic + keyword)
- Multi-format support (TXT, PDF, MD, DOCX, CSV)
- Async document ingestion with progress tracking
- Structured data queries for CSV files
- REST API server
- MCP server for Claude Desktop integration
- Graceful shutdown handling
- Configuration-driven architecture

Dependencies:
- LangChain (LLM framework)
- Ollama (local AI models)
- ChromaDB (vector database)
- FastAPI (REST API)
- Pandas (structured queries)
- And more (see requirements.txt)
EOF

# Make setup.sh executable
chmod +x "$PACKAGE_DIR/setup.sh"

# Create README for the package
cat > "$PACKAGE_DIR/README_FIRST.txt" << 'EOF'
📦 HYBRID RAG PROJECT
====================

Thank you for using the Hybrid RAG Project!

🎯 WHAT TO DO FIRST:
-------------------
1. Read START_HERE.txt (in this folder)
2. Follow the setup instructions
3. Add your documents to the data/ folder
4. Start querying!

📚 DOCUMENTATION:
-----------------
All documentation is included:
- START_HERE.txt - Quick start guide
- docs/INSTALLATION.md - Detailed setup
- README.md - Complete documentation
- VERSION.txt - Package information

🚀 QUICK SETUP:
---------------
macOS/Linux:  Run ./setup.sh
Windows:      See docs/INSTALLATION.md

💡 FEATURES:
------------
✓ Query your documents with AI
✓ Works completely offline (after setup)
✓ Supports PDFs, text, CSV, Word docs
✓ Exact counts for CSV data
✓ Semantic search for text documents
✓ Claude Desktop integration
✓ REST API for programmatic access

Need help? See docs/INSTALLATION.md

Enjoy! 🎉
EOF

echo "🗜️  Creating archive..."
cd "$TEMP_DIR"
zip -r "$PACKAGE_NAME.zip" "$PROJECT_NAME" -q

# Move to output directory
mv "$PACKAGE_NAME.zip" "$OUTPUT_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

# Calculate size
SIZE=$(du -h "$OUTPUT_DIR/$PACKAGE_NAME.zip" | cut -f1)

echo ""
echo "✅ Package created successfully!"
echo ""
echo "📦 Package: $OUTPUT_DIR/$PACKAGE_NAME.zip"
echo "💾 Size: $SIZE"
echo ""
echo "📧 Ready to send!"
echo ""
echo "Your brother can:"
echo "  1. Extract the zip file"
echo "  2. Run ./setup.sh (or follow docs/INSTALLATION.md)"
echo "  3. Add documents to data/ folder"
echo "  4. Run: python scripts/run_demo.py"
echo ""
echo "All documentation is included in the package."
echo ""
