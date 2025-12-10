#!/usr/bin/env python3
"""
Interactive Hybrid RAG Demo
Easy-to-use command-line interface for querying your documents.
NO MCP SERVER REQUIRED - just run this script!
"""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import yaml
from typing import Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from src.hybrid_rag import (
    DocumentLoaderUtility,
    configure_logging,
    create_document_type_aware_retriever
)


class InteractiveRAG:
    """Interactive RAG system with easy command-line interface."""

    def __init__(self):
        """Initialize the RAG system."""
        print("=" * 70)
        print("🚀 HYBRID RAG SYSTEM - INTERACTIVE DEMO")
        print("=" * 70)
        print("\nInitializing system...\n")

        # Configure logging
        configure_logging()

        # Load configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        print("✅ Configuration loaded")

        # Initialize components
        self._load_documents()
        self._initialize_ollama()
        self._create_vector_store()
        self._create_retriever()
        self._create_qa_chain()

        print("\n" + "=" * 70)
        print("✅ SYSTEM READY - You can now ask questions!")
        print("=" * 70)

    def _load_documents(self):
        """Load documents from data directory."""
        data_dir = self.config['data']['directory']
        data_path = Path(__file__).parent.parent.parent / data_dir

        print(f"📂 Loading documents from: {data_path}")

        loader = DocumentLoaderUtility(str(data_path), config=self.config)
        self.documents = loader.load_documents()

        if not self.documents:
            print(f"\n⚠️  No documents found in '{data_path}'")
            print(f"⚠️  Supported formats: {', '.join(loader.get_supported_formats())}")
            sys.exit(1)

        # Count file types
        sources = [doc.metadata.get('source', '') for doc in self.documents]
        unique_files = set([Path(s).name for s in sources if s])

        print(f"✅ Loaded {len(self.documents)} chunks from {len(unique_files)} files")

    def _initialize_ollama(self):
        """Connect to Ollama and initialize models."""
        try:
            ollama_url = self.config['ollama']['base_url']
            self.embedding_model = self.config['ollama']['embedding_model']
            self.llm_model = self.config['ollama']['llm_model']

            self.embeddings = OllamaEmbeddings(
                model=self.embedding_model,
                base_url=ollama_url
            )
            self.llm = OllamaLLM(
                model=self.llm_model,
                base_url=ollama_url
            )

            print(f"✅ Connected to Ollama at {ollama_url}")
            print(f"   • Embedding model: {self.embedding_model}")
            print(f"   • LLM model: {self.llm_model}")

        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            print("\n💡 Make sure Ollama is running:")
            print("   1. Start Ollama: ollama serve")
            print("   2. Pull models:")
            print(f"      ollama pull {self.embedding_model}")
            print(f"      ollama pull {self.llm_model}")
            sys.exit(1)

    def _create_vector_store(self):
        """Create or load vector store."""
        persist_dir = Path(__file__).parent.parent / self.config['vector_store']['persist_directory']

        print(f"🔧 Creating vector store (this may take a few minutes)...")

        self.vectorstore = Chroma.from_documents(
            self.documents,
            self.embeddings,
            persist_directory=str(persist_dir)
        )

        print(f"✅ Vector store created with {len(self.documents)} embeddings")

    def _create_retriever(self):
        """Create hybrid retriever."""
        print("🔧 Creating hybrid retriever...")

        self.retriever = create_document_type_aware_retriever(
            documents=self.documents,
            vectorstore=self.vectorstore,
            config=self.config
        )

        print("✅ Hybrid retriever ready (semantic + keyword search)")

    def _create_qa_chain(self):
        """Create QA chain."""
        prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Answer the user's question based on the provided context.
If the context doesn't contain enough information, say so clearly.
Keep your answer concise and relevant.

<context>
{context}
</context>

Question: {input}

Answer:""")

        document_chain = create_stuff_documents_chain(self.llm, prompt)
        self.qa_chain = create_retrieval_chain(self.retriever, document_chain)

        print("✅ QA chain constructed")

    def query(self, question: str, show_sources: bool = True):
        """
        Ask a question and get an answer.

        Args:
            question: The question to ask
            show_sources: Whether to show source documents

        Returns:
            Dictionary with 'answer' and 'context'
        """
        try:
            response = self.qa_chain.invoke({"input": question})

            if show_sources:
                print("\n📚 Sources:")
                sources_seen = set()
                for i, doc in enumerate(response.get('context', [])[:5], 1):
                    source = doc.metadata.get('source', 'unknown')
                    source_file = Path(source).name if source != 'unknown' else 'unknown'

                    if source_file not in sources_seen:
                        sources_seen.add(source_file)
                        print(f"   [{i}] {source_file}")

            return response

        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            return None

    def interactive_mode(self):
        """Run interactive question-answering loop."""
        print("\n💬 INTERACTIVE MODE")
        print("   • Type your questions and press Enter")
        print("   • Type 'exit' or 'quit' to stop")
        print("   • Type 'help' for example questions")
        print("   • Type 'stats' for system statistics")
        print()

        while True:
            try:
                # Get user input
                question = input("❓ Your question: ").strip()

                if not question:
                    continue

                # Handle commands
                if question.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                elif question.lower() == 'help':
                    self._show_help()
                    continue

                elif question.lower() == 'stats':
                    self._show_stats()
                    continue

                # Process question
                print("\n🤔 Thinking...")
                response = self.query(question, show_sources=True)

                if response:
                    print(f"\n💡 Answer:\n{response['answer']}\n")
                    print("-" * 70)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break

            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    def _show_help(self):
        """Show example questions."""
        print("\n📖 EXAMPLE QUESTIONS:")
        print()
        print("General:")
        print("  • What information is available in these documents?")
        print("  • Summarize the main topics covered")
        print()
        print("Specific (adjust based on your data):")
        print("  • What OLED TVs are available?")
        print("  • Which products are low in stock?")
        print("  • Show me the largest orders in November")
        print("  • What are common warranty claim types?")
        print("  • Which supplier has the best ratings?")
        print("  • What customer feedback mentions delivery?")
        print()

    def _show_stats(self):
        """Show system statistics."""
        print("\n📊 SYSTEM STATISTICS:")
        print()

        # Document statistics
        sources = [doc.metadata.get('source', '') for doc in self.documents]
        unique_files = set([Path(s).name for s in sources if s])

        file_types = {}
        for source in sources:
            if source:
                ext = Path(source).suffix
                file_types[ext] = file_types.get(ext, 0) + 1

        print(f"Documents:")
        print(f"  • Total chunks: {len(self.documents)}")
        print(f"  • Unique files: {len(unique_files)}")
        print(f"  • File types:")
        for ext, count in sorted(file_types.items()):
            print(f"    - {ext}: {count} chunks")

        print()
        print(f"Models:")
        print(f"  • Embedding: {self.embedding_model}")
        print(f"  • LLM: {self.llm_model}")
        print()
        print(f"Configuration:")
        print(f"  • Vector search k: {self.config['retrieval']['vector_search_k']}")
        print(f"  • Keyword search k: {self.config['retrieval']['keyword_search_k']}")
        print(f"  • CSV weight: {self.config['retrieval']['csv_weight']}")
        print(f"  • Text weight: {self.config['retrieval']['text_weight']}")
        print()


def main():
    """Main entry point."""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Hybrid RAG Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python interactive_demo.py

  # Ask a single question
  python interactive_demo.py --query "What OLED TVs are available?"

  # Ask without showing sources
  python interactive_demo.py --query "Show me products" --no-sources
        """
    )

    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Ask a single question (non-interactive mode)'
    )

    parser.add_argument(
        '--no-sources',
        action='store_true',
        help='Hide source documents in output'
    )

    args = parser.parse_args()

    # Initialize system
    try:
        rag = InteractiveRAG()
    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}")
        sys.exit(1)

    # Single query mode
    if args.query:
        print(f"\n❓ Question: {args.query}")
        response = rag.query(args.query, show_sources=not args.no_sources)

        if response:
            print(f"\n💡 Answer:\n{response['answer']}")
        sys.exit(0)

    # Interactive mode
    rag.interactive_mode()


if __name__ == "__main__":
    main()
