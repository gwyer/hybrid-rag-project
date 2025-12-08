"""Setup script for Hybrid RAG Project"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name="hybrid-rag",
    version="2.1.0",
    author="Christopher Gwyer",
    author_email="your.email@example.com",  # Update with your email
    description="Hybrid RAG system with semantic and keyword search, supporting multiple document formats and Claude Desktop integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hybrid-rag-project",  # Update with your GitHub username
    project_urls={
        "Bug Reports": "https://github.com/yourusername/hybrid-rag-project/issues",
        "Documentation": "https://github.com/yourusername/hybrid-rag-project/tree/main/docs",
        "Source": "https://github.com/yourusername/hybrid-rag-project",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="rag retrieval langchain ollama embeddings semantic-search hybrid-search mcp claude",
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hybrid-rag-demo=scripts.run_demo:main",
            "hybrid-rag-server=scripts.mcp_server:main",
        ],
    },
)
