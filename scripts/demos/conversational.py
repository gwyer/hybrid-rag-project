#!/usr/bin/env python3
"""
Conversational Hybrid RAG Demo
Interactive CLI with conversation history and context memory.
Maintains context across follow-up questions!
"""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import yaml
from typing import Dict, Any, List
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from src.hybrid_rag import (
    DocumentLoaderUtility,
    configure_logging,
    create_document_type_aware_retriever
)
from src.hybrid_rag.query_preprocessor import QueryPreprocessor


class ConversationalRAG:
    """Conversational RAG system with memory."""

    def __init__(self):
        """Initialize the RAG system."""
        print("=" * 70)
        print("🚀 CONVERSATIONAL HYBRID RAG SYSTEM")
        print("=" * 70)
        print("\n💡 This version maintains conversation history!")
        print("   Follow-up questions will reference previous answers.\n")
        print("Initializing system...\n")

        # Configure logging
        configure_logging()

        # Load configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        print("✅ Configuration loaded")

        # Initialize conversation history
        self.chat_history = ChatMessageHistory()
        self.conversation_count = 0

        # Initialize query preprocessor for product ID mapping
        print("🔧 Loading product ID mapping...")
        self.query_preprocessor = QueryPreprocessor()
        print("✅ Query preprocessor ready (product ID expansion enabled)")

        # Initialize components
        self._load_documents()
        self._initialize_ollama()
        self._create_vector_store()
        self._create_retriever()
        self._create_conversational_chain()

        print("\n" + "=" * 70)
        print("✅ SYSTEM READY - You can now have conversations!")
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

    def _create_conversational_chain(self):
        """Create conversational QA chain with memory."""
        # Conversational prompt with history
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert assistant with access to document context.
Answer questions based on the provided context and conversation history.

When answering follow-up questions:
- Reference previous answers when relevant
- Use pronouns like "it", "them", "that product" naturally
- Maintain context across the conversation
- If the user asks about "more details" or "tell me more", expand on the previous topic

If you don't have enough information, say so clearly.
Keep answers concise but informative."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Context: {context}"),
            ("human", "{input}")
        ])

        # Create document chain
        document_chain = create_stuff_documents_chain(self.llm, prompt)

        # Create retrieval chain
        self.qa_chain = create_retrieval_chain(self.retriever, document_chain)

        print("✅ Conversational chain constructed with memory")

    def query(self, question: str, show_sources: bool = True):
        """
        Ask a question with conversation context.

        Args:
            question: The question to ask
            show_sources: Whether to show source documents

        Returns:
            Dictionary with 'answer' and 'context'
        """
        try:
            # Expand query with product ID mappings
            expanded_question = self.query_preprocessor.expand_query(question)

            # Show expansion if it happened
            if expanded_question != question:
                print(f"🔍 Expanded query with product IDs: {expanded_question[:100]}...")

            # Convert chat history to proper format
            history_messages = []
            for msg in self.chat_history.messages:
                history_messages.append(msg)

            # Invoke chain with history (using expanded query)
            response = self.qa_chain.invoke({
                "input": expanded_question,
                "chat_history": history_messages
            })

            # Add to conversation history
            self.chat_history.add_user_message(question)
            self.chat_history.add_ai_message(response['answer'])
            self.conversation_count += 1

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
            import traceback
            traceback.print_exc()
            return None

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history.clear()
        self.conversation_count = 0
        print("\n🔄 Conversation history cleared!\n")

    def show_history(self):
        """Show conversation history."""
        if not self.chat_history.messages:
            print("\n📝 No conversation history yet.\n")
            return

        print("\n📝 CONVERSATION HISTORY:")
        print("-" * 70)

        for i, msg in enumerate(self.chat_history.messages):
            if isinstance(msg, HumanMessage):
                print(f"\n[{i//2 + 1}] 👤 You: {msg.content}")
            elif isinstance(msg, AIMessage):
                # Truncate long responses
                content = msg.content
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"    🤖 Assistant: {content}")

        print("\n" + "-" * 70 + "\n")

    def interactive_mode(self):
        """Run interactive question-answering loop."""
        print("\n💬 CONVERSATIONAL MODE")
        print("   • Ask follow-up questions - I'll remember the context!")
        print("   • Type 'exit' or 'quit' to stop")
        print("   • Type 'help' for example questions")
        print("   • Type 'history' to see conversation history")
        print("   • Type 'clear' to start a new conversation")
        print("   • Type 'stats' for system statistics")
        print()

        while True:
            try:
                # Show conversation count
                if self.conversation_count > 0:
                    print(f"[Turn {self.conversation_count + 1}]")

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

                elif question.lower() == 'history':
                    self.show_history()
                    continue

                elif question.lower() == 'clear':
                    self.clear_history()
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
        """Show example questions with conversational examples."""
        print("\n📖 EXAMPLE CONVERSATIONS:")
        print()
        print("Single Questions:")
        print("  • What OLED TVs are available?")
        print("  • Which products are low in stock?")
        print("  • Show me the largest orders in November")
        print()
        print("Follow-up Questions (using context):")
        print("  You: What OLED TVs are available?")
        print("  AI: We have OLED TVs in sizes 42\", 48\", 55\"...")
        print("  You: Which one is the most popular?")
        print("  AI: Based on sales data, the 55\" model is most popular...")
        print("  You: How much does it cost?")
        print("  AI: The OLED 55\" TV Premium is priced at $1,299.99")
        print()
        print("  You: What products have warranty claims?")
        print("  AI: The TV-OLED-55-001 has 12 claims, mostly for dead pixels...")
        print("  You: Tell me more about those claims")
        print("  AI: The dead pixel claims were primarily from the Q4 2024 batch...")
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
        print(f"Conversation:")
        print(f"  • Messages exchanged: {len(self.chat_history.messages)}")
        print(f"  • Questions asked: {self.conversation_count}")

        print()
        print(f"Models:")
        print(f"  • Embedding: {self.embedding_model}")
        print(f"  • LLM: {self.llm_model}")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Conversational Hybrid RAG Demo with Memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive conversational mode (default)
  python conversational_demo.py

  # The system maintains context across questions!
  # You can ask follow-ups like:
  #   "What OLED TVs are available?"
  #   "Which one is cheapest?"
  #   "How many are in stock?"
        """
    )

    args = parser.parse_args()

    # Initialize system
    try:
        rag = ConversationalRAG()
    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Interactive mode
    rag.interactive_mode()


if __name__ == "__main__":
    main()
