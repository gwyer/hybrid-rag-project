"""
Document Loader Utility
Loads documents from various file formats in the data directory.
"""
import os
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
    CSVLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentLoaderUtility:
    """Utility class to load documents from various file formats."""

    def __init__(self, data_directory: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the document loader.

        Args:
            data_directory: Path to the directory containing documents
            config: Optional configuration dictionary for chunking parameters
        """
        self.data_directory = Path(data_directory)
        self.config = config or {}

        # Get chunking config
        doc_config = self.config.get('document_processing', {})
        self.text_chunk_size = doc_config.get('text_chunk_size', 1000)
        self.text_chunk_overlap = doc_config.get('text_chunk_overlap', 200)
        self.csv_chunk_size = doc_config.get('csv_chunk_size', 10)

        self.supported_loaders = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader,
            '.md': UnstructuredMarkdownLoader,
            '.docx': Docx2txtLoader,
            '.csv': CSVLoader,
        }

        # Text splitter for markdown/text files
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.text_chunk_size,
            chunk_overlap=self.text_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def count_files(self) -> int:
        """
        Count the number of supported files in the data directory.

        Returns:
            Number of supported files
        """
        if not self.data_directory.exists():
            return 0

        count = 0
        for file_path in self.data_directory.rglob('*'):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                if file_extension in self.supported_loaders:
                    count += 1
        return count

    def load_documents(self, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[Document]:
        """
        Load all supported documents from the data directory.

        Args:
            progress_callback: Optional callback function(current, total, filename) for progress updates

        Returns:
            List of Document objects
        """
        if not self.data_directory.exists():
            print(f"Warning: Data directory '{self.data_directory}' does not exist.")
            return []

        # First, collect all supported files
        supported_files = []
        for file_path in self.data_directory.rglob('*'):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                if file_extension in self.supported_loaders:
                    supported_files.append(file_path)

        total_files = len(supported_files)
        documents = []
        files_loaded = 0

        for idx, file_path in enumerate(supported_files, 1):
            file_extension = file_path.suffix.lower()

            try:
                # Report progress
                if progress_callback:
                    progress_callback(idx, total_files, file_path.name)

                loader_class = self.supported_loaders[file_extension]
                loader = loader_class(str(file_path))
                loaded_docs = loader.load()

                # Apply chunking for text-based documents (not CSV)
                if file_extension in ['.txt', '.md', '.pdf', '.docx']:
                    # Split text documents into smaller chunks
                    chunked_docs = self.text_splitter.split_documents(loaded_docs)

                    # Add metadata about the source file and document type
                    for doc in chunked_docs:
                        doc.metadata['source_file'] = file_path.name
                        doc.metadata['file_type'] = file_extension
                        doc.metadata['doc_category'] = 'text'  # Mark as text document

                    documents.extend(chunked_docs)
                else:
                    # CSV files - keep as-is but mark as structured
                    for doc in loaded_docs:
                        doc.metadata['source_file'] = file_path.name
                        doc.metadata['file_type'] = file_extension
                        doc.metadata['doc_category'] = 'structured'  # Mark as structured data

                    documents.extend(loaded_docs)
                files_loaded += 1
                print(f"✅ Loaded: {file_path.name} ({idx}/{total_files})")
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")

        print(f"\n📚 Total files loaded: {files_loaded}")
        print(f"📄 Total documents created: {len(documents)}")

        return documents

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.

        Returns:
            List of supported file extensions
        """
        return list(self.supported_loaders.keys())
