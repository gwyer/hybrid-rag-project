# Quick Start Guide - Hybrid RAG System

## 🚀 Three Ways to Use This Project

You do **NOT** need Claude Desktop or MCP to use this project! Here are your options:

---

## Option 1: Interactive Demo (EASIEST) ⭐

**No MCP required!** Just run and ask questions.

### Two Flavors:

#### A. Simple Mode (No Memory)
Each question is independent - great for exploring different topics.

```bash
# Activate virtual environment
source .venv/bin/activate

# Run interactive demo
python scripts/interactive_demo.py
```

#### B. Conversational Mode (WITH Memory) 💬
Maintains conversation history - perfect for follow-up questions!

```bash
# Activate virtual environment
source .venv/bin/activate

# Run conversational demo
python scripts/conversational_demo.py
```

**New to RAG?** Start with conversational mode - it feels more natural!

📖 **See [CONVERSATION_MEMORY.md](CONVERSATION_MEMORY.md)** to understand the difference.

### What You'll See
```
======================================================================
🚀 HYBRID RAG SYSTEM - INTERACTIVE DEMO
======================================================================

Initializing system...

✅ Configuration loaded
📂 Loading documents from: /Users/.../data
✅ Loaded 43835 chunks from 13 files
✅ Connected to Ollama at http://localhost:11434
   • Embedding model: nomic-embed-text
   • LLM model: llama3.1:latest
🔧 Creating vector store (this may take a few minutes)...
✅ Vector store created with 43835 embeddings
✅ Hybrid retriever ready (semantic + keyword search)
✅ QA chain constructed

======================================================================
✅ SYSTEM READY - You can now ask questions!
======================================================================

💬 INTERACTIVE MODE
   • Type your questions and press Enter
   • Type 'exit' or 'quit' to stop
   • Type 'help' for example questions
   • Type 'stats' for system statistics

❓ Your question: _
```

### Example Session
```bash
❓ Your question: What OLED TVs are available?

🤔 Thinking...

📚 Sources:
   [1] product_catalog.csv
   [2] customer_feedback_q4_2024.md

💡 Answer:
We have OLED TVs available in multiple sizes: 42", 48", 55", 65", 77",
and 83". The OLED 55" TV Premium (TV-OLED-55-001) is priced at $1,299.99
and we have 135 units in stock across our warehouses. Customer feedback
indicates exceptional picture quality with perfect blacks.

----------------------------------------------------------------------
❓ Your question: exit

👋 Goodbye!
```

### Single Question Mode
```bash
# Ask one question and exit
python scripts/interactive_demo.py --query "What products are low in stock?"

# Ask without showing sources
python scripts/interactive_demo.py --query "Show me products" --no-sources
```

---

## Option 2: Basic Demo Script

**Original demo** - runs predefined queries.

```bash
source .venv/bin/activate
python scripts/run_demo.py
```

This runs 2 sample queries and shows results. Good for testing the system.

---

## Option 3: Claude Desktop Integration (MCP)

**Optional!** For seamless integration with Claude Desktop.

### Setup
1. Install Claude Desktop
2. Configure MCP server in Claude settings:
```json
{
  "mcpServers": {
    "hybrid-rag-project": {
      "command": "/Users/your-username/.../python",
      "args": ["/Users/your-username/.../mcp_server.py"]
    }
  }
}
```

3. Restart Claude Desktop
4. Ask Claude to use the `query_documents` tool

**See:** `docs/MCP_SETUP.md` for detailed instructions

---

## Prerequisites (All Methods)

### 1. Ollama Must Be Running
```bash
# Start Ollama server
ollama serve

# Pull required models (one-time setup)
ollama pull nomic-embed-text
ollama pull llama3.1:latest
```

### 2. Virtual Environment Activated
```bash
source .venv/bin/activate
```

### 3. Documents in data/ Directory
The project already includes 13 sample files with 41,000+ records:
- ✅ product_catalog.csv
- ✅ inventory_levels.csv
- ✅ sales_orders_november.csv
- ✅ warranty_claims_q4.csv
- ✅ And 9 more files...

**To use your own data:**
```bash
# Add files to data directory
cp your_file.csv data/
cp your_document.md data/

# Supported formats: .csv, .md, .txt, .pdf, .docx
```

---

## Comparison of Options

| Feature | Interactive Demo | Basic Demo | MCP Server |
|---------|-----------------|------------|------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Easiest | ⭐⭐⭐⭐ Easy | ⭐⭐ Complex |
| **Setup Required** | Just run it | Just run it | Configure Claude |
| **Ask Multiple Questions** | ✅ Yes | ❌ No | ✅ Yes |
| **Claude Desktop Required** | ❌ No | ❌ No | ✅ Yes |
| **Use in Terminal** | ✅ Yes | ✅ Yes | ❌ No |
| **Best For** | Exploration | Testing | Production use with Claude |

---

## Recommended Workflow

### For Learning & Testing
1. **Start here:** `python scripts/interactive_demo.py`
2. Ask lots of questions
3. Type `stats` to see system info
4. Type `help` for example questions

### For Development
1. Use `interactive_demo.py` for quick testing
2. Modify `config/config.yaml` to tune parameters
3. Run `python scripts/boundary_testing.py` for performance testing

### For Production
1. Set up MCP server for Claude Desktop integration
2. Or build a web API around the RAG system
3. Or integrate into your application via Python imports

---

## Troubleshooting

### "Connection refused to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Verify in another terminal
curl http://localhost:11434
```

### "No documents found"
```bash
# Check data directory
ls -la data/

# Make sure files are supported formats
# Supported: .csv, .md, .txt, .pdf, .docx
```

### "ModuleNotFoundError: No module named 'hybrid_rag'"
```bash
# Activate virtual environment
source .venv/bin/activate

# Install in development mode
pip install -e .
```

### First Run is Slow
**This is normal!** The system needs to:
1. Load all documents (~5 seconds for 41K records)
2. Generate embeddings (~9 minutes for 41K records)
3. Build vector index

**Subsequent runs are much faster** because:
- Embeddings are cached in `chroma_db/`
- Only new documents need embedding

---

## Example Questions (Based on Sample Data)

### Product Queries
- "What OLED TVs are available?"
- "Show me all 65 inch displays"
- "Which monitors are best for gaming?"

### Inventory Queries
- "What products are low in stock?"
- "Which warehouse has the most inventory?"
- "Show me products in Warehouse-East"

### Sales Queries
- "What were the largest orders in November?"
- "Which sales rep had the most sales?"
- "Show me orders to retail customers"

### Quality Queries
- "What are common warranty claim types?"
- "Show me products with high defect rates"
- "Which shipping routes have delays?"

### Cross-Document Queries
- "Which products have both high sales and high warranty claims?"
- "What do customers say about delivery times?"
- "Compare OLED vs LCD warranty rates"

---

## Next Steps

### Customize for Your Data
1. **Add your files** to `data/` directory
2. **Run interactive demo** to test
3. **Tune parameters** in `config/config.yaml`:
   - Adjust `vector_search_k` for more/fewer results
   - Modify `csv_weight` vs `text_weight` ratio
   - Change `chunk_size` for different granularity

### Extend the System
- Add new document types (see `ARCHITECTURE.md`)
- Implement new retrieval strategies
- Build a web interface (Flask/FastAPI)
- Add authentication and access control

### Learn More
- **ARCHITECTURE.md** - Detailed technical documentation
- **TESTING_RESULTS.md** - Performance benchmarks
- **BOUNDARY_TESTING_SUGGESTIONS.md** - Advanced testing ideas

---

## Performance Expectations

**With 41,000 records (current dataset):**
- **First-time setup:** 5-10 minutes (one-time embedding generation)
- **Subsequent startups:** 10-30 seconds (loading cached embeddings)
- **Query latency:** 0.5-2 seconds per question
- **Memory usage:** ~1-2 GB

**Scaling:**
- System handles 100K+ documents
- Linear scaling for document loading
- Sub-linear scaling for queries (vector search is O(log n))

---

## Summary

**✅ You DO NOT need MCP or Claude Desktop to use this project!**

**Simplest way to get started:**
```bash
source .venv/bin/activate
python scripts/interactive_demo.py
```

That's it! Ask questions and get answers from your 41,000+ record dataset.

The MCP server is just an **optional enhancement** for Claude Desktop users who want seamless integration.
