# Usage Methods Comparison

## Three Ways to Use the Hybrid RAG System

---

## 1. Interactive Demo (RECOMMENDED) ⭐

### What It Is
A user-friendly command-line interface for asking questions interactively.

### How to Run
```bash
source .venv/bin/activate
python scripts/interactive_demo.py

# Or use the shortcut
./ask.sh
```

### Features
- ✅ Ask unlimited questions in a conversation
- ✅ Type `help` for example questions
- ✅ Type `stats` to see system info
- ✅ Shows source documents for each answer
- ✅ Easy to use, no configuration needed
- ✅ **NO MCP or Claude Desktop required**

### When to Use
- **Learning the system**
- **Exploring your data**
- **Quick testing**
- **Daily use without Claude Desktop**

### Example Session
```
❓ Your question: What OLED TVs are available?

🤔 Thinking...

📚 Sources:
   [1] product_catalog.csv
   [2] customer_feedback_q4_2024.md

💡 Answer:
We have OLED TVs available in sizes 42", 48", 55", 65", 77", and 83".
The OLED 55" TV Premium is priced at $1,299.99 with 135 units in stock.
Customer feedback indicates exceptional picture quality.

----------------------------------------------------------------------
❓ Your question: Which products are low in stock?

🤔 Thinking...
[... answer ...]
```

---

## 2. Basic Demo Script

### What It Is
Simple script that runs predefined queries and shows results.

### How to Run
```bash
source .venv/bin/activate
python scripts/run_demo.py
```

### Features
- ✅ Quick system test
- ✅ Shows retrieval + answer generation
- ✅ Good for verifying installation
- ⚠️ Only runs 2 hardcoded queries
- ⚠️ No interactivity

### When to Use
- **Verifying the system works**
- **Testing after changes**
- **Understanding the code flow**

### Output
```
✅ Configuration loaded from config/config.yaml
📂 Loading documents...
✅ Loaded 43835 chunks from 13 files
✅ Connected to Ollama
✅ Vector Store Created
✅ Hybrid Retriever Created
✅ RAG Chain Constructed

======================================================================
🔥 Executing Hybrid Query: 'What information is available?'
======================================================================

--- Retrieved Context (Hybrid Results) ---
[1] Source: product_catalog.csv
    Product_ID,Product_Name,Category,Screen_Size...
[2] Source: customer_feedback_q4_2024.md
    Customer Feedback Q4 2024...

--- Final LLM Answer ---
These documents contain product catalogs, inventory data, sales records,
warranty claims, production schedules, supplier pricing, shipping manifests,
customer feedback, market analysis, quality control reports, return policies,
support tickets, and product specifications...
```

---

## 3. MCP Server (Claude Desktop Integration)

### What It Is
Exposes RAG system as tools that Claude Desktop can use seamlessly.

### How to Run
1. Configure in `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "hybrid-rag-project": {
      "command": "/path/to/python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

2. Restart Claude Desktop

3. Ask Claude to query your documents

### Features
- ✅ Seamless integration with Claude Desktop
- ✅ Natural language interface
- ✅ Tools appear in Claude's UI
- ✅ Claude can query your docs automatically
- ⚠️ Requires Claude Desktop (not free)
- ⚠️ More complex setup

### When to Use
- **Production workflow with Claude**
- **Integrating docs into Claude conversations**
- **Team environments using Claude Desktop**

### Example Usage in Claude
```
You: "Can you check my documents for OLED TV inventory?"

Claude: I'll search your documents for OLED TV inventory information.

[Claude uses query_documents tool automatically]

Claude: Based on your documents, here's the OLED TV inventory:
- OLED 42": 201 units across 3 warehouses
- OLED 48": 166 units
- OLED 55": 135 units
...
```

---

## Feature Comparison

| Feature | Interactive Demo | Basic Demo | MCP Server |
|---------|-----------------|------------|------------|
| **Easy to Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Setup Time** | 30 seconds | 30 seconds | 5-10 minutes |
| **Ask Multiple Questions** | ✅ Unlimited | ❌ Only 2 | ✅ Unlimited |
| **Custom Questions** | ✅ Yes | ❌ No | ✅ Yes |
| **Shows Sources** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Claude Desktop Required** | ❌ No | ❌ No | ✅ Yes |
| **Works Offline** | ✅ Yes | ✅ Yes | ✅ Yes* |
| **Command Line** | ✅ Yes | ✅ Yes | ❌ No |
| **GUI Interface** | ❌ No | ❌ No | ✅ Yes (Claude) |
| **Single Question Mode** | ✅ Yes | ❌ No | ✅ Yes |
| **System Statistics** | ✅ Yes | ❌ No | ✅ Limited |
| **Best For** | Daily use | Testing | Claude integration |

*Still requires local Ollama running

---

## Technical Comparison

### Interactive Demo (`interactive_demo.py`)
```python
# Start system
rag = InteractiveRAG()

# Interactive loop
while True:
    question = input("Your question: ")
    response = rag.query(question, show_sources=True)
    print(response['answer'])

# Or single question
python interactive_demo.py --query "Your question here"
```

**Code:** ~400 lines with rich CLI experience

---

### Basic Demo (`run_demo.py`)
```python
# Load config
config = load_config()

# Initialize components
loader = DocumentLoaderUtility(data_path, config)
documents = loader.load_documents()
embeddings = OllamaEmbeddings(...)
vectorstore = Chroma.from_documents(...)
retriever = create_document_type_aware_retriever(...)
qa_chain = create_retrieval_chain(...)

# Run queries
for query in sample_queries:
    response = qa_chain.invoke({"input": query})
    print(response['answer'])
```

**Code:** ~200 lines, straightforward RAG pipeline

---

### MCP Server (`mcp_server.py`)
```python
# MCP protocol server
app = Server("hybrid-rag-project")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="query_documents", ...),
        Tool(name="list_documents", ...),
        Tool(name="get_stats", ...)
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_documents":
        return query_system(arguments["query"])
    # ...

# Run server (stdio communication)
await app.run()
```

**Code:** ~300 lines with MCP protocol handling

---

## Decision Guide

### Choose Interactive Demo If:
- ✅ You want to explore the system quickly
- ✅ You need to ask many questions
- ✅ You want statistics and help commands
- ✅ You don't have Claude Desktop
- ✅ You prefer terminal-based tools

### Choose Basic Demo If:
- ✅ You want to test the installation
- ✅ You're learning how RAG works
- ✅ You want to see the code flow
- ✅ You're developing new features

### Choose MCP Server If:
- ✅ You use Claude Desktop regularly
- ✅ You want conversational interface
- ✅ You need Claude to access your docs
- ✅ You want seamless integration
- ✅ You're building a team workflow

---

## Startup Time Comparison

### First Time (Cold Start - Embedding Generation)
All methods have similar startup time:

```
Interactive Demo:  ~9 minutes (41K records)
Basic Demo:        ~9 minutes (41K records)
MCP Server:        ~9 minutes (41K records)
```

**Why?** All need to generate embeddings for 41,000+ records.

### Subsequent Runs (Warm Start - Cached Embeddings)
```
Interactive Demo:  10-20 seconds
Basic Demo:        10-20 seconds
MCP Server:        15-30 seconds (includes MCP startup)
```

**Why?** Embeddings are cached in `chroma_db/`, only loading required.

---

## Memory Usage

All methods use similar memory:

```
Document Loading:    ~400 MB
Vector Store:        ~650 MB
Total Runtime:       ~1.1 GB
```

No significant difference between methods.

---

## When NOT to Use MCP Server

MCP server is **optional** and not needed if:

- ❌ You don't have Claude Desktop
- ❌ You prefer command-line tools
- ❌ You want simpler setup
- ❌ You're just learning/testing
- ❌ You want more control over queries

**The Interactive Demo does everything MCP does, without the complexity!**

---

## Recommended Learning Path

### Day 1: Get Started
```bash
./ask.sh
```
Use interactive demo, ask questions, explore your data.

### Day 2: Understand the Code
```bash
python scripts/run_demo.py
```
Read the code, see how RAG works.

### Day 3: Advanced Features
Read `ARCHITECTURE.md`, tune `config.yaml`, run boundary tests.

### Week 2: Production (Optional)
Set up MCP server if using Claude Desktop regularly.

---

## Summary

**✅ You DO NOT need MCP to use this project!**

The **Interactive Demo** (`interactive_demo.py`) provides everything you need:
- Ask unlimited questions
- See sources
- Get statistics
- Easy to use
- No complex setup

The **MCP Server** is just an **optional enhancement** for Claude Desktop users.

**Simplest command:**
```bash
./ask.sh
```

That's all you need to start querying 41,000+ records!
