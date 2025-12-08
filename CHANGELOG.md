# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-12-07

### Added
- **Document-type-aware retriever** with separate pipelines for CSV vs text documents
- **Configurable weighting** between structured and unstructured data (default 40/60)
- **Text chunking** for markdown/text files (1000 chars with 200 char overlap)
- **Markdown support dependency** (`markdown>=3.4.0`) added to requirements
- **Metadata enrichment** with `doc_category`, `retrieval_score`, and `retrieval_source`
- **Comprehensive documentation** including RETRIEVAL_IMPROVEMENTS.md
- **GitHub-ready project structure** with LICENSE, CONTRIBUTING.md, and CHANGELOG

### Fixed
- **Critical**: Markdown files now load correctly (was failing due to missing `markdown` package)
- **Field initialization** bug in `DocumentTypeAwareRetriever` class (Pydantic compatibility)
- **Import paths** after restructuring to src layout

### Changed
- **Increased retrieval limits** from k=2 to k=5 for both vector and keyword search
- **Project structure** reorganized to follow Python best practices (src layout)
- **Version bumped** to 2.1.0 in `__init__.py`

### Performance
- Text/markdown retrieval improved from ~25% to ~90%+ success rate
- Maintained 100% success rate for CSV/structured data queries
- Overall system success rate improved from ~70% to ~95%

## [2.0.0] - 2024-11-25

### Added
- **Generalized document loading** from data directory
- **Multi-format support**: TXT, PDF, MD, DOCX, CSV
- **Configuration-driven architecture** via config.yaml
- **MCP server** for Claude Desktop integration
- **REST API server** with FastAPI
- **Structured query engine** for CSV data using Pandas
- **Async document ingestion** with progress tracking
- **Graceful shutdown handling** for all servers
- **Comprehensive documentation** suite
- **Automated setup script** (setup.sh)
- **Distribution packaging** (package.sh)

### Changed
- Restructured from sample project to production-ready system
- Moved from hardcoded values to configuration file
- Renamed main script from `SampleData.py` to `hybrid_rag.py` (later `run_demo.py`)

### Features
- Document-type-aware metadata tagging
- Progress callbacks for ingestion monitoring
- Multiple retrieval modes (semantic, keyword, hybrid)
- Persistent vector store with ChromaDB
- Local LLM integration via Ollama

## [1.0.0] - Initial Release

### Added
- Basic hybrid RAG implementation
- Vector-based semantic search using Chroma
- BM25 keyword search
- Reciprocal Rank Fusion (RRF) for result merging
- Sample HR documents for testing
- Integration with Ollama for embeddings and LLM

### Features
- Ensemble retriever combining vector and keyword search
- Context-aware answer generation
- Document metadata tracking

---

## Version Numbering

- **Major version** (X.0.0): Breaking changes or major new features
- **Minor version** (0.X.0): New features, backwards compatible
- **Patch version** (0.0.X): Bug fixes, backwards compatible

## Links

- [GitHub Repository](https://github.com/yourusername/hybrid-rag-project)
- [Documentation](./docs/)
- [Issues](https://github.com/yourusername/hybrid-rag-project/issues)
