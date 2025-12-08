# Contributing to Hybrid RAG Project

Thank you for your interest in contributing to the Hybrid RAG Project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a Code of Conduct that all contributors are expected to adhere to:

- **Be respectful** and inclusive
- **Be collaborative** and helpful
- **Focus on what is best** for the community
- **Show empathy** towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hybrid-rag-project.git
   cd hybrid-rag-project
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/hybrid-rag-project.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Ollama installed and running
- Git

### Setup Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies** (if any):
   ```bash
   pip install pytest black flake8 mypy
   ```

4. **Set up Ollama models**:
   ```bash
   ollama pull llama3.1:latest
   ollama pull nomic-embed-text
   ```

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, Ollama version)
- **Relevant logs** or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- **Check existing issues** to avoid duplicates
- **Provide a clear use case** for the enhancement
- **Explain the expected behavior** and benefits
- **Consider backwards compatibility**

### Code Contributions

1. **Create a new branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Test your changes** thoroughly

4. **Commit your changes** with clear messages:
   ```bash
   git commit -m "Add feature: description of feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Code Style

This project follows Python best practices:

### General Guidelines

- **PEP 8** compliance for Python code
- **Type hints** for function signatures
- **Docstrings** for all public functions and classes
- **Meaningful variable names** that describe purpose
- **Comments** for complex logic

### Example

```python
def load_documents(
    self,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[Document]:
    """
    Load all supported documents from the data directory.

    Args:
        progress_callback: Optional callback function(current, total, filename)
                          for progress updates

    Returns:
        List of Document objects

    Raises:
        ValueError: If data directory doesn't exist
    """
    # Implementation
```

### Formatting

Run formatters before committing:

```bash
# Format with black
black src/ scripts/

# Check with flake8
flake8 src/ scripts/

# Type check with mypy (optional)
mypy src/ scripts/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_document_loader.py
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names
- Include docstrings explaining what is being tested

Example:

```python
def test_document_loader_loads_markdown():
    """Test that DocumentLoaderUtility correctly loads markdown files."""
    loader = DocumentLoaderUtility("test_data/")
    documents = loader.load_documents()

    md_docs = [d for d in documents if d.metadata['file_type'] == '.md']
    assert len(md_docs) > 0
```

## Pull Request Process

1. **Update documentation** if you change functionality
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Reference related issues** in PR description
6. **Request review** from maintainers

### PR Title Format

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:
- `feat: add support for EPUB documents`
- `fix: resolve markdown loading issue`
- `docs: update installation instructions`

## Project Structure

```
hybrid-rag-project/
├── src/hybrid_rag/          # Core library code
│   ├── __init__.py
│   ├── document_loader.py
│   ├── structured_query.py
│   ├── hybrid_retriever.py
│   └── utils.py
├── scripts/                  # Executable scripts
│   ├── run_demo.py
│   ├── mcp_server.py
│   └── mcp_server_claude.py
├── config/                   # Configuration files
│   ├── config.yaml
│   └── claude_desktop_config.json
├── docs/                     # Documentation
├── tests/                    # Test files
├── data/                     # User data (not in git)
└── README.md
```

## Areas for Contribution

### High Priority

- [ ] Additional document format support (EPUB, HTML, etc.)
- [ ] More comprehensive test coverage
- [ ] Performance optimizations for large documents
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

### Documentation

- [ ] More usage examples
- [ ] Video tutorials
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Troubleshooting guides

### Features

- [ ] Support for more embedding models
- [ ] Query caching
- [ ] Document version tracking
- [ ] Multi-language support
- [ ] Advanced filtering options

## Questions?

If you have questions about contributing:

1. Check existing **Issues** and **Discussions**
2. Create a new **Discussion** for general questions
3. Create an **Issue** for bug reports or feature requests

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you to all contributors who help make this project better!

---

**Happy Contributing!** 🎉
