# Demo Scripts - Quick Reference

## 🚀 Quick Start

```bash
./ask.sh                    # Conversational mode (recommended)
./ask.sh --simple          # Simple mode (no memory)
```

---

## 📝 Available Demo Scripts

### 1. **conversational_demo.py** - WITH Memory 💬 (RECOMMENDED)

**Best for:** Natural conversations, follow-up questions

```bash
python scripts/conversational_demo.py
```

**Features:**
- ✅ Remembers conversation history
- ✅ Handles "it", "them", "that one" references
- ✅ Perfect for drilling down on topics
- ✅ Commands: `history`, `clear`, `help`, `stats`

**Example:**
```
You: What OLED TVs are available?
AI: We have OLED in sizes 42", 48", 55"...

You: Which is cheapest?          ← "Which" refers to OLED TVs
AI: The 42" model at $899.99

You: How many in stock?           ← "How many" refers to 42" OLED
AI: 201 units across 3 warehouses
```

---

### 2. **interactive_demo.py** - No Memory

**Best for:** Exploring different unrelated topics

```bash
python scripts/interactive_demo.py

# Or single question:
python scripts/interactive_demo.py --query "What OLED TVs are available?"
```

**Features:**
- ✅ Fast and simple
- ✅ Each question is independent
- ✅ Commands: `help`, `stats`
- ❌ No conversation memory

---

### 3. **run_demo.py** - Basic Demo

**Best for:** Testing the system

```bash
python scripts/run_demo.py
```

**Features:**
- ✅ Runs 2 predefined queries
- ✅ Shows retrieval process
- ❌ No interactivity

---

## 🎮 Commands (in interactive/conversational modes)

| Command | Conversational | Interactive | Description |
|---------|---------------|-------------|-------------|
| `help` | ✅ | ✅ | Show example questions |
| `stats` | ✅ | ✅ | System statistics |
| `history` | ✅ | ❌ | Show conversation history |
| `clear` | ✅ | ❌ | Clear conversation memory |
| `exit`, `quit` | ✅ | ✅ | Exit the program |

---

## 📊 Comparison

| Feature | Conversational | Interactive | Basic |
|---------|---------------|-------------|-------|
| **Conversation Memory** | ✅ | ❌ | ❌ |
| **Follow-up Questions** | ✅ | ❌ | ❌ |
| **Multiple Questions** | ✅ | ✅ | ❌ (only 2) |
| **Custom Questions** | ✅ | ✅ | ❌ |
| **Conversation History** | ✅ | ❌ | ❌ |
| **Speed** | Medium | Fast | Fast |
| **Best For** | Conversations | Exploration | Testing |

---

## 💡 Which One Should I Use?

### Use **Conversational Mode** when:
- ✅ Asking follow-up questions
- ✅ Having a conversation about a topic
- ✅ Drilling down into details
- ✅ Want natural back-and-forth

### Use **Interactive Mode** when:
- ✅ Asking unrelated questions
- ✅ Want maximum speed
- ✅ Don't need context between questions

### Use **Basic Demo** when:
- ✅ Just testing if system works
- ✅ Learning how the code works

---

## 🔧 Common Usage Patterns

### Pattern 1: Topic Investigation (Use Conversational)
```bash
python scripts/conversational_demo.py

You: What products have warranty issues?
You: Tell me more about those issues
You: Which supplier is responsible?
You: Show me their quality ratings
You: What are our alternatives?
```

### Pattern 2: Quick Lookups (Use Interactive)
```bash
python scripts/interactive_demo.py

You: What OLED TVs are available?
You: What's in Warehouse-East?
You: Show me November sales
# Each question is independent
```

### Pattern 3: Single Question (Use Interactive with --query)
```bash
python scripts/interactive_demo.py --query "What products are low in stock?"
```

---

## 🎯 Example Sessions

### Conversational Session (Natural Flow)
```
./ask.sh

❓ What OLED TVs do we have?
💡 OLED sizes: 42", 48", 55", 65", 77", 83"

❓ Price range?
💡 From $899 (42") to $3,499 (83")

❓ Best seller?
💡 The 55" model with 400+ units sold in November

❓ Any quality issues?
💡 12 warranty claims, mostly dead pixels in Q4 batch

❓ history
📝 Shows all 4 Q&A pairs

❓ clear
🔄 Conversation reset

❓ What about LCD TVs?
💡 Fresh conversation about LCD...
```

### Interactive Session (Independent Questions)
```
python scripts/interactive_demo.py

❓ What OLED TVs are available?
💡 OLED sizes: 42", 48", 55"...

❓ Show shipping delays
💡 15 shipments have delays...

❓ Customer feedback on audio
💡 Soundbar ratings average 4.2/5...

# Each answer is independent
```

---

## ⚙️ Customization

### Change Models
Edit `config/config.yaml`:
```yaml
ollama:
  llm_model: "llama3.1:latest"        # Change LLM
  embedding_model: "nomic-embed-text" # Change embeddings
```

### Change Retrieval Settings
```yaml
retrieval:
  vector_search_k: 5    # More results = more context
  keyword_search_k: 5
  csv_weight: 0.4       # Adjust CSV vs text balance
  text_weight: 0.6
```

---

## 🐛 Troubleshooting

### "Connection refused to Ollama"
```bash
# Start Ollama
ollama serve

# Verify
curl http://localhost:11434
```

### "No module named 'hybrid_rag'"
```bash
source .venv/bin/activate
pip install -e .
```

### Conversation getting confused
```
# In conversational mode:
type: clear
# Starts fresh
```

### Slow responses
```bash
# Use interactive mode instead (no history overhead)
./ask.sh --simple
```

---

## 📚 Learn More

- **CONVERSATION_MEMORY.md** - Deep dive into how memory works
- **QUICK_START.md** - Complete usage guide
- **ARCHITECTURE.md** - Technical details
- **USAGE_COMPARISON.md** - Detailed comparison

---

## 🎓 Learning Path

### Day 1: Get Started
```bash
./ask.sh
# Ask questions, explore your data
```

### Day 2: Understand Memory
```bash
# Compare both modes
python scripts/conversational_demo.py
python scripts/interactive_demo.py --simple
```

### Day 3: Customize
```bash
# Edit config/config.yaml
# Tune retrieval parameters
# Run boundary tests
```

---

## ⚡ Quick Commands

```bash
# Easiest - conversational with memory
./ask.sh

# Simple mode - no memory
./ask.sh --simple

# Single question
python scripts/interactive_demo.py --query "Your question"

# Test system
python scripts/run_demo.py

# Performance test
python scripts/boundary_testing.py
```

---

**Bottom Line:**

New users → **`./ask.sh`** (conversational mode)

Power users → Choose based on task:
- Conversation = `conversational_demo.py`
- Quick lookups = `interactive_demo.py`
- Testing = `run_demo.py`
