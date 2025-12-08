"""
Enhanced Hybrid Retriever with Document Type Weighting
Separates retrieval for structured (CSV) vs unstructured (text/markdown) documents.
"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever


class DocumentTypeAwareRetriever(BaseRetriever):
    """
    Retriever that separates documents by type (structured vs text) and applies
    different retrieval strategies to each, then merges results with weighting.
    """

    # Define fields for proper initialization
    text_retriever: BaseRetriever
    csv_retriever: BaseRetriever
    text_weight: float
    csv_weight: float

    def __init__(
        self,
        text_vector_retriever: BaseRetriever,
        text_bm25_retriever: BaseRetriever,
        csv_vector_retriever: BaseRetriever,
        csv_bm25_retriever: BaseRetriever,
        text_weight: float = 0.6,
        csv_weight: float = 0.4,
    ):
        """
        Initialize the document type aware retriever.

        Args:
            text_vector_retriever: Vector retriever for text documents
            text_bm25_retriever: BM25 retriever for text documents
            csv_vector_retriever: Vector retriever for CSV documents
            csv_bm25_retriever: BM25 retriever for CSV documents
            text_weight: Weight for text document results (0-1)
            csv_weight: Weight for CSV document results (0-1)
        """
        # Create ensemble retrievers for each document type
        text_retriever = EnsembleRetriever(
            retrievers=[text_vector_retriever, text_bm25_retriever],
            weights=[0.5, 0.5]
        )

        csv_retriever = EnsembleRetriever(
            retrievers=[csv_vector_retriever, csv_bm25_retriever],
            weights=[0.5, 0.5]
        )

        # Initialize parent with fields
        super().__init__(
            text_retriever=text_retriever,
            csv_retriever=csv_retriever,
            text_weight=text_weight,
            csv_weight=csv_weight
        )

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Retrieve documents from both text and CSV retrievers, then merge with weighting.

        Args:
            query: The query string
            run_manager: Callback manager

        Returns:
            Merged list of documents from both retrievers
        """
        # Get results from both retrievers
        text_docs = self.text_retriever.invoke(query)
        csv_docs = self.csv_retriever.invoke(query)

        # Apply weighting by adjusting relevance scores
        # Since we don't have explicit scores, we'll use position-based scoring
        weighted_docs = []

        # Add text documents with text weight
        for idx, doc in enumerate(text_docs):
            # Higher position = lower score
            position_score = 1.0 / (idx + 1)
            doc.metadata['retrieval_score'] = position_score * self.text_weight
            doc.metadata['retrieval_source'] = 'text_retriever'
            weighted_docs.append(doc)

        # Add CSV documents with CSV weight
        for idx, doc in enumerate(csv_docs):
            position_score = 1.0 / (idx + 1)
            doc.metadata['retrieval_score'] = position_score * self.csv_weight
            doc.metadata['retrieval_source'] = 'csv_retriever'
            weighted_docs.append(doc)

        # Sort by retrieval score (highest first)
        weighted_docs.sort(key=lambda x: x.metadata.get('retrieval_score', 0), reverse=True)

        # Return merged results (limit to reasonable number)
        return weighted_docs[:10]


def create_document_type_aware_retriever(
    documents: List[Document],
    vectorstore: Chroma,
    config: Dict[str, Any]
) -> BaseRetriever:
    """
    Create a document type aware retriever that separates text and CSV documents.

    Args:
        documents: All loaded documents
        vectorstore: The vector store containing all documents
        config: Configuration dictionary

    Returns:
        DocumentTypeAwareRetriever instance
    """
    # Separate documents by type
    text_docs = [doc for doc in documents if doc.metadata.get('doc_category') == 'text']
    csv_docs = [doc for doc in documents if doc.metadata.get('doc_category') == 'structured']

    # Get retrieval config
    vector_k = config.get('retrieval', {}).get('vector_search_k', 5)
    keyword_k = config.get('retrieval', {}).get('keyword_search_k', 5)

    # Get weighting config
    doc_config = config.get('document_processing', {})
    text_weight = doc_config.get('text_retriever_weight', 0.6)
    csv_weight = doc_config.get('csv_retriever_weight', 0.4)

    # Create vector retrievers (using metadata filtering)
    text_vector_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": vector_k,
            "filter": {"doc_category": "text"}
        }
    )

    csv_vector_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": vector_k,
            "filter": {"doc_category": "structured"}
        }
    )

    # Create BM25 retrievers for each document type
    if text_docs:
        text_bm25_retriever = BM25Retriever.from_documents(text_docs)
        text_bm25_retriever.k = keyword_k
    else:
        # Fallback if no text docs
        text_bm25_retriever = text_vector_retriever

    if csv_docs:
        csv_bm25_retriever = BM25Retriever.from_documents(csv_docs)
        csv_bm25_retriever.k = keyword_k
    else:
        # Fallback if no CSV docs
        csv_bm25_retriever = csv_vector_retriever

    # Create and return the document type aware retriever
    return DocumentTypeAwareRetriever(
        text_vector_retriever=text_vector_retriever,
        text_bm25_retriever=text_bm25_retriever,
        csv_vector_retriever=csv_vector_retriever,
        csv_bm25_retriever=csv_bm25_retriever,
        text_weight=text_weight,
        csv_weight=csv_weight
    )
