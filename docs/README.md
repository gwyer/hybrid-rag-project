# Hybrid RAG Documentation

Welcome to the Hybrid RAG project documentation! This guide will help you find the information you need.

---

## 📖 Documentation Structure

### 🚀 Getting Started
Start here if you're new to the project:

- **[Quick Start Guide](getting-started/quick-start.md)** - Get up and running in 5 minutes
- **[Conversation Memory](getting-started/conversation-memory.md)** - Understanding context across questions
- **[Demo Cheat Sheet](getting-started/demo-cheat-sheet.md)** - Quick reference for all demo scripts

### 🏗️ Architecture & Technical
Deep dives into how the system works:

- **[System Design](architecture/system-design.md)** - Comprehensive architecture documentation
- **[Testing Results](architecture/testing-results.md)** - Performance benchmarks (41K+ records)
- **[Boundary Testing](architecture/boundary-testing.md)** - Stress testing suggestions

### 📚 Guides & How-Tos
Practical guides for specific tasks:

- **[Usage Comparison](guides/usage-comparison.md)** - Compare interactive vs conversational vs MCP modes
- **[GitHub Setup](guides/github-setup.md)** - Publishing to GitHub
- **[Restructure Options](guides/restructure-options.md)** - Project organization analysis

---

## 🎯 Quick Navigation

### I want to...

**...start using the system**
→ [Quick Start Guide](getting-started/quick-start.md)

**...understand how it works**
→ [System Design](architecture/system-design.md)

**...ask follow-up questions**
→ [Conversation Memory](getting-started/conversation-memory.md)

**...see performance at scale**
→ [Testing Results](architecture/testing-results.md)

**...compare different modes**
→ [Usage Comparison](guides/usage-comparison.md)

**...push to GitHub**
→ [GitHub Setup](guides/github-setup.md)

**...run boundary tests**
→ [Boundary Testing](architecture/boundary-testing.md)

---

## 📂 Project Overview

### What is Hybrid RAG?

This is a **Retrieval-Augmented Generation (RAG)** system that combines:
- **Semantic search** (vector embeddings) - understands meaning
- **Lexical search** (BM25 keywords) - exact matching
- **Hybrid fusion** (RRF) - best of both worlds

### Key Features
- ✅ Multi-format support (CSV, MD, TXT, PDF, DOCX)
- ✅ Document-type-aware retrieval
- ✅ Conversation memory
- ✅ Local LLM via Ollama
- ✅ Claude Desktop integration (MCP)
- ✅ Tested at scale (41,000+ records)

---

## 🛠️ Available Demo Scripts

Located in `scripts/demos/`:

1. **conversational.py** - WITH conversation memory (recommended)
2. **interactive.py** - Simple mode, no memory
3. **basic.py** - Predefined queries for testing

**Quick launch:** `./scripts/bin/ask.sh`

---

## 📊 Documentation by Audience

### For End Users
1. [Quick Start](getting-started/quick-start.md)
2. [Demo Cheat Sheet](getting-started/demo-cheat-sheet.md)
3. [Conversation Memory](getting-started/conversation-memory.md)

### For Developers
1. [System Design](architecture/system-design.md)
2. [Testing Results](architecture/testing-results.md)
3. [Boundary Testing](architecture/boundary-testing.md)

### For Contributors
1. [CONTRIBUTING.md](../CONTRIBUTING.md) (in root)
2. [Usage Comparison](guides/usage-comparison.md)
3. [GitHub Setup](guides/github-setup.md)

---

## 🔗 External Resources

- **Main README:** [../README.md](../README.md)
- **Changelog:** [../CHANGELOG.md](../CHANGELOG.md)
- **License:** [../LICENSE](../LICENSE)
- **Source Code:** [../src/hybrid_rag/](../src/hybrid_rag/)
- **Configuration:** [../config/config.yaml](../config/config.yaml)

---

## 💡 Need Help?

1. **Quick questions?** → Check the [Demo Cheat Sheet](getting-started/demo-cheat-sheet.md)
2. **Setup issues?** → See [Quick Start Guide](getting-started/quick-start.md)
3. **Architecture questions?** → Read [System Design](architecture/system-design.md)
4. **Performance questions?** → Review [Testing Results](architecture/testing-results.md)

---

## 📈 Documentation Stats

- **Total Documents:** 10 files
- **Lines of Documentation:** ~5,000+
- **Code Examples:** 100+
- **Architecture Diagrams:** Multiple
- **Test Results:** 41,000+ records tested

---

Happy learning! 🚀
