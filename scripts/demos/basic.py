#!/usr/bin/env python3
"""
Hybrid RAG System - Demo Script
Main script demonstrating hybrid search with RAG using configuration file and document loader.
"""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import yaml
from typing import Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers import EnsembleRetriever
from src.hybrid_rag import (
    DocumentLoaderUtility,
    configure_logging,
    create_document_type_aware_retriever
)


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    """Main function to run the hybrid RAG system."""

    # Configure logging to suppress warnings
    configure_logging()

    # Load configuration
    config = load_config()
    print("✅ Configuration loaded from config/config.yaml")

    # --- 1. Load Documents from Data Directory ---
    data_dir = config['data']['directory']
    data_path = Path(__file__).parent.parent.parent / data_dir
    loader = DocumentLoaderUtility(str(data_path), config=config)
    documents = loader.load_documents()

    if not documents:
        print("\n⚠️  No documents found in the data directory.")
        print(f"⚠️  Please add files to '{data_path}' directory.")
        print(f"⚠️  Supported formats: {', '.join(loader.get_supported_formats())}")
        return

    # --- 2. Initialize Models & Embeddings (Connecting to Ollama) ---
    try:
        ollama_url = config['ollama']['base_url']
        embedding_model = config['ollama']['embedding_model']
        llm_model = config['ollama']['llm_model']

        embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        llm = OllamaLLM(model=llm_model, base_url=ollama_url)
        print(f"✅ Connected to Ollama at {ollama_url}")
        print(f"✅ Using embedding model: {embedding_model}")
        print(f"✅ Using LLM model: {llm_model}")
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Please ensure Ollama is running and the specified models are downloaded.")
        return

    # --- 3. Create the Vector Store (Dense Search) ---
    persist_dir = Path(__file__).parent.parent.parent / config['vector_store']['persist_directory']
    vectorstore = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=str(persist_dir)
    )
    vector_k = config['retrieval']['vector_search_k']
    print(f"✅ Vector Store Created with k={vector_k}.")

    # --- 4. Create Hybrid Retriever (CSV vs Text Aware) ---
    use_separate = config.get('document_processing', {}).get('use_separate_retrievers', False)

    if use_separate:
        print("🔧 Using document-type-aware retriever (CSV vs Text separation)")
        hybrid_retriever = create_document_type_aware_retriever(
            documents=documents,
            vectorstore=vectorstore,
            config=config
        )
    else:
        print("🔧 Using traditional ensemble retriever")
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": vector_k})

        keyword_retriever = BM25Retriever.from_documents(documents)
        keyword_k = config['retrieval']['keyword_search_k']
        keyword_retriever.k = keyword_k

        hybrid_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever]
        )

    print("✅ Hybrid Retriever Created.")

    # --- 6. Define the Prompt (The Template Node) ---
    prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Answer the user's question based ONLY on the provided context.
If the context does not contain the answer, state clearly that the information is not available in the documents.

<context>
{context}
</context>

Question: {input}
""")

    # --- 7. Construct the RAG Chain ---
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(hybrid_retriever, document_chain)
    print("✅ RAG Chain Constructed.")

    # --- 8. Execute Sample Queries ---
    sample_queries = [
        "What information is available in these documents?",
        "Summarize the main topics covered."
    ]

    for query in sample_queries:
        print("\n" + "="*70)
        print(f"🔥 Executing Hybrid Query: '{query}'")
        print("="*70)

        try:
            response = rag_chain.invoke({"input": query})

            # --- 9. Output the Result ---
            print("\n--- Retrieved Context (Hybrid Results) ---")
            for i, doc in enumerate(response['context']):
                source = doc.metadata.get('source_file', 'unknown')
                content_preview = doc.page_content[:150].replace('\n', ' ')
                print(f"[{i+1}] Source: {source}")
                print(f"    {content_preview}...")

            print("\n--- Final LLM Answer ---")
            print(response['answer'])
            print("="*70)
        except Exception as e:
            print(f"❌ Error processing query: {e}")

    print("\n✅ Hybrid RAG demonstration complete!")


if __name__ == "__main__":
    main()
