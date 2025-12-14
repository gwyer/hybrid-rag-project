#!/usr/bin/env python3
"""
Demo Query Runner for BM25 and Semantic Search Demonstration

This script runs a series of queries that showcase:
1. BM25 strengths (exact matching, IDs, technical terms)
2. Vector search strengths (semantic understanding, synonyms)
3. Hybrid search benefits (combining both)

Outputs results in a markdown table format for reports.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import yaml
from typing import List, Dict, Tuple
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
from src.hybrid_rag.query_preprocessor import QueryPreprocessor


# Demo queries organized by capability
DEMO_QUERIES = {
    "BM25 Strengths - Exact Matching": [
        {
            "query": "TV-OLED-55-001",
            "category": "Exact Product ID",
            "expected": "BM25 finds exact product code match"
        },
        {
            "query": "What is the price of product TV-OLED-55-001?",
            "category": "Specific Product Query",
            "expected": "BM25 matches exact product ID in CSV"
        },
        {
            "query": "Show me order ORD-00100",
            "category": "Exact Order Number",
            "expected": "BM25 finds exact order ID"
        },
    ],
    "Vector Strengths - Semantic Understanding": [
        {
            "query": "What products are running low on inventory?",
            "category": "Concept Query (no exact match)",
            "expected": "Vector understands 'running low' = low stock"
        },
        {
            "query": "Which items have quality problems?",
            "category": "Synonym Query",
            "expected": "Vector finds 'issues', 'defects', 'problems'"
        },
        {
            "query": "What do customers complain about most?",
            "category": "Natural Language Question",
            "expected": "Vector understands question intent"
        },
    ],
    "Hybrid Benefits - Best of Both": [
        {
            "query": "What is the inventory status of OLED TVs?",
            "category": "Mixed Query (exact term + concept)",
            "expected": "BM25 finds 'OLED', vector understands 'status'"
        },
        {
            "query": "Show me warranty claims for product TV-OLED-55-001",
            "category": "Exact ID + Semantic Context",
            "expected": "BM25 finds product ID, vector finds related claims"
        },
        {
            "query": "Are there delivery issues with recent orders?",
            "category": "Concept + Context",
            "expected": "Hybrid finds shipping/delivery mentions"
        },
    ],
    "Structured Data (CSV) Queries": [
        {
            "query": "How many products are in the catalog?",
            "category": "Count Query",
            "expected": "Retrieves from product_catalog.csv"
        },
        {
            "query": "What is the most expensive product?",
            "category": "Comparison Query",
            "expected": "Finds max price in CSV data"
        },
        {
            "query": "Show me products priced under $500",
            "category": "Numerical Filtering",
            "expected": "Retrieves price-based results"
        },
    ],
    "Unstructured Data (Text/Markdown) Queries": [
        {
            "query": "What is the return policy?",
            "category": "Policy Question",
            "expected": "Retrieves from return_policy_procedures.md"
        },
        {
            "query": "What are common customer complaints?",
            "category": "Sentiment Analysis",
            "expected": "Retrieves from customer_feedback_q4_2024.md"
        },
        {
            "query": "What are the technical specifications for OLED displays?",
            "category": "Technical Query",
            "expected": "Retrieves from product_specifications.txt"
        },
    ],
    "Cross-Document Synthesis": [
        {
            "query": "Which products have both low inventory and warranty claims?",
            "category": "Multi-Document Join",
            "expected": "Correlates inventory_levels.csv + warranty_claims_q4.csv"
        },
        {
            "query": "What products are mentioned in both customer feedback and quality reports?",
            "category": "Cross-Reference",
            "expected": "Finds overlap between feedback + QC reports"
        },
    ],
}


class DemoQueryRunner:
    """Runs demonstration queries and formats results."""

    def __init__(self):
        """Initialize RAG system."""
        print("🔧 Initializing RAG system...")
        configure_logging()

        # Load configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize query preprocessor for product ID mapping
        print("🔧 Loading product ID mapping...")
        self.query_preprocessor = QueryPreprocessor()
        print("✅ Query preprocessor ready (product ID expansion enabled)")

        # Load documents
        data_dir = self.config['data']['directory']
        data_path = Path(__file__).parent.parent.parent / data_dir
        loader = DocumentLoaderUtility(str(data_path), config=self.config)
        self.documents = loader.load_documents()

        print(f"✅ Loaded {len(self.documents)} document chunks")

        # Initialize Ollama
        ollama_url = self.config['ollama']['base_url']
        embedding_model = self.config['ollama']['embedding_model']
        llm_model = self.config['ollama']['llm_model']

        self.embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        self.llm = OllamaLLM(model=llm_model, base_url=ollama_url)

        print(f"✅ Connected to Ollama ({llm_model})")

        # Create vector store
        persist_dir = Path(__file__).parent.parent.parent / self.config['vector_store']['persist_directory']
        self.vectorstore = Chroma.from_documents(
            self.documents,
            self.embeddings,
            persist_directory=str(persist_dir)
        )

        # Create retriever
        self.retriever = create_document_type_aware_retriever(
            documents=self.documents,
            vectorstore=self.vectorstore,
            config=self.config
        )

        print("✅ Hybrid retriever ready")

        # Create QA chain
        prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Answer the question based ONLY on the provided context.
Be concise but informative. If the context doesn't contain the answer, say so.

<context>
{context}
</context>

Question: {input}

Answer:""")

        document_chain = create_stuff_documents_chain(self.llm, prompt)
        self.qa_chain = create_retrieval_chain(self.retriever, document_chain)

        print("✅ System ready\n")

    def query(self, question: str) -> Tuple[str, List[str]]:
        """
        Execute a query and return answer with sources.

        Returns:
            Tuple of (answer, list of source files)
        """
        # Expand query with product ID mappings
        expanded_question = self.query_preprocessor.expand_query(question)

        # Use expanded query for retrieval
        response = self.qa_chain.invoke({"input": expanded_question})

        # Extract sources
        sources = []
        for doc in response.get('context', [])[:3]:  # Top 3 sources
            source = doc.metadata.get('source', '')
            if source:
                source_name = Path(source).name
                if source_name not in sources:
                    sources.append(source_name)

        return response['answer'], sources

    def run_all_queries(self) -> List[Dict]:
        """Run all demo queries and collect results."""
        results = []
        total_queries = sum(len(queries) for queries in DEMO_QUERIES.values())
        current = 0

        print("="*80)
        print("RUNNING DEMO QUERIES")
        print("="*80)
        print()

        for section, queries in DEMO_QUERIES.items():
            print(f"\n📊 {section}")
            print("-" * 80)

            for query_info in queries:
                current += 1
                query = query_info['query']
                category = query_info['category']

                print(f"\n[{current}/{total_queries}] Query: {query}")

                try:
                    answer, sources = self.query(query)

                    # Truncate answer for display
                    display_answer = answer[:150] + "..." if len(answer) > 150 else answer
                    print(f"✅ Answer: {display_answer}")
                    print(f"📄 Sources: {', '.join(sources)}")

                    results.append({
                        'section': section,
                        'category': category,
                        'query': query,
                        'answer': answer,
                        'sources': sources,
                        'expected': query_info['expected']
                    })

                except Exception as e:
                    print(f"❌ Error: {e}")
                    results.append({
                        'section': section,
                        'category': category,
                        'query': query,
                        'answer': f"ERROR: {str(e)}",
                        'sources': [],
                        'expected': query_info['expected']
                    })

        return results

    def format_as_markdown_table(self, results: List[Dict]) -> str:
        """Format results as a markdown table."""
        markdown = "# Hybrid RAG System Demonstration Results\n\n"
        markdown += f"**Date:** {Path(__file__).stat().st_mtime}\n\n"
        markdown += f"**Total Queries:** {len(results)}\n\n"
        markdown += f"**Dataset:** 43,835 document chunks (41,000 CSV rows + 2,835 text chunks)\n\n"
        markdown += "---\n\n"

        # Group by section
        current_section = None
        for result in results:
            if result['section'] != current_section:
                if current_section is not None:
                    markdown += "\n---\n\n"
                current_section = result['section']
                markdown += f"## {current_section}\n\n"
                markdown += "| Category | Query | Answer | Sources |\n"
                markdown += "|----------|-------|--------|----------|\n"

            # Format table row
            category = result['category']
            query = result['query'].replace('|', '\\|')  # Escape pipes
            answer = result['answer'][:200].replace('\n', ' ').replace('|', '\\|')  # Truncate & escape
            if len(result['answer']) > 200:
                answer += "..."
            sources = ', '.join(result['sources'][:2])  # Top 2 sources

            markdown += f"| {category} | {query} | {answer} | {sources} |\n"

        return markdown

    def format_as_csv(self, results: List[Dict]) -> str:
        """Format results as CSV."""
        csv = "Section,Category,Query,Answer,Sources\n"
        for result in results:
            section = result['section']
            category = result['category']
            query = result['query'].replace('"', '""')  # Escape quotes
            answer = result['answer'][:200].replace('"', '""').replace('\n', ' ')
            sources = '; '.join(result['sources'])

            csv += f'"{section}","{category}","{query}","{answer}","{sources}"\n'

        return csv

    def save_results(self, results: List[Dict]):
        """Save results to files."""
        output_dir = Path(__file__).parent.parent.parent

        # Save markdown
        md_path = output_dir / "DEMO_QUERY_RESULTS.md"
        with open(md_path, 'w') as f:
            f.write(self.format_as_markdown_table(results))
        print(f"\n📄 Markdown table saved to: {md_path}")

        # Save CSV
        csv_path = output_dir / "DEMO_QUERY_RESULTS.csv"
        with open(csv_path, 'w') as f:
            f.write(self.format_as_csv(results))
        print(f"📊 CSV saved to: {csv_path}")

        # Print markdown table to console
        print("\n" + "="*80)
        print("MARKDOWN TABLE (Copy for Report)")
        print("="*80)
        print(self.format_as_markdown_table(results))


def main():
    """Main entry point."""
    try:
        runner = DemoQueryRunner()
        results = runner.run_all_queries()
        runner.save_results(results)

        print("\n" + "="*80)
        print("✅ DEMO COMPLETE")
        print("="*80)
        print(f"\nTotal queries executed: {len(results)}")
        print("\nFiles generated:")
        print("  - DEMO_QUERY_RESULTS.md  (Markdown table)")
        print("  - DEMO_QUERY_RESULTS.csv (CSV format)")
        print("\nYou can copy either format into your report.")

    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
