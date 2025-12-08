"""
Hybrid RAG System

A generalized Retrieval-Augmented Generation (RAG) system with hybrid search capabilities.
Combines semantic (dense vector) search and keyword (sparse BM25) search for optimal document retrieval.
"""

__version__ = "2.1.0"
__author__ = "Christopher Gwyer"

from .document_loader import DocumentLoaderUtility
from .structured_query import StructuredQueryEngine
from .utils import configure_logging
from .hybrid_retriever import DocumentTypeAwareRetriever, create_document_type_aware_retriever

__all__ = [
    "DocumentLoaderUtility",
    "StructuredQueryEngine",
    "configure_logging",
    "DocumentTypeAwareRetriever",
    "create_document_type_aware_retriever",
]
