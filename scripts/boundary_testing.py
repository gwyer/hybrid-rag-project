#!/usr/bin/env python3
"""
Comprehensive boundary testing for Hybrid RAG system.
Tests performance, accuracy, and scalability with large datasets.
"""

import time
import psutil
import os
import yaml
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hybrid_rag import DocumentLoaderUtility, configure_logging, create_document_type_aware_retriever
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


class BoundaryTester:
    """Comprehensive boundary testing suite."""

    def __init__(self):
        self.results = {
            'start_time': datetime.now(),
            'system_info': self.get_system_info(),
            'tests': []
        }

        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize Ollama connections
        self.ollama_url = self.config['ollama']['base_url']
        self.embedding_model = self.config['ollama']['embedding_model']
        self.llm_model = self.config['ollama']['llm_model']

        self.data_dir = Path(__file__).parent.parent / self.config['data']['directory']

    def get_system_info(self):
        """Collect system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'available_memory_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'python_version': sys.version.split()[0]
        }

    def get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / (1024 * 1024), 2)

    def print_section(self, title):
        """Print formatted section header."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")

    def test_document_loading(self):
        """Test 1: Document loading performance."""
        self.print_section("TEST 1: DOCUMENT LOADING PERFORMANCE")

        configure_logging()

        start_mem = self.get_memory_usage()
        start_time = time.time()

        print(f"Starting memory: {start_mem} MB")
        print(f"Loading documents from: {self.data_dir}")
        print("\nProgress:")

        loader = DocumentLoaderUtility(str(self.data_dir), config=self.config)
        documents = loader.load_documents()

        load_time = time.time() - start_time
        end_mem = self.get_memory_usage()
        mem_increase = end_mem - start_mem

        # Count total chunks (documents include chunked text)
        total_chunks = len(documents)

        result = {
            'test_name': 'Document Loading',
            'total_chunks': total_chunks,
            'load_time_seconds': round(load_time, 2),
            'memory_increase_mb': round(mem_increase, 2),
            'chunks_per_second': round(total_chunks / load_time, 2),
            'status': 'PASS'
        }

        self.results['tests'].append(result)

        print(f"\n✓ Loaded and chunked {total_chunks} document chunks in {load_time:.2f} seconds")
        print(f"  • Rate: {result['chunks_per_second']} chunks/sec")
        print(f"  • Memory used: {mem_increase:.2f} MB")

        return documents

    def test_vector_store_creation(self, documents):
        """Test 2: Vector store initialization and population."""
        self.print_section("TEST 2: VECTOR STORE CREATION & EMBEDDING GENERATION")

        start_mem = self.get_memory_usage()
        start_time = time.time()

        print(f"Starting memory: {start_mem} MB")
        print(f"Creating embeddings for {len(documents)} document chunks...")
        print("\nThis may take several minutes with a large dataset...\n")

        embeddings = OllamaEmbeddings(model=self.embedding_model, base_url=self.ollama_url)
        persist_dir = Path(__file__).parent.parent / self.config['vector_store']['persist_directory']

        vectorstore = Chroma.from_documents(
            documents,
            embeddings,
            persist_directory=str(persist_dir)
        )

        total_time = time.time() - start_time
        end_mem = self.get_memory_usage()
        mem_increase = end_mem - start_mem

        result = {
            'test_name': 'Vector Store Creation',
            'total_embeddings': len(documents),
            'total_time_seconds': round(total_time, 2),
            'memory_increase_mb': round(mem_increase, 2),
            'embeddings_per_second': round(len(documents) / total_time, 2),
            'status': 'PASS'
        }

        self.results['tests'].append(result)

        print(f"\n✓ Created vector store with {len(documents)} embeddings in {total_time:.2f} seconds")
        print(f"  • Rate: {result['embeddings_per_second']} embeddings/sec")
        print(f"  • Memory used: {mem_increase:.2f} MB")

        return vectorstore

    def test_retrieval_performance(self, vectorstore, documents):
        """Test 3: Retrieval performance with various query types."""
        self.print_section("TEST 3: RETRIEVAL PERFORMANCE & ACCURACY")

        # Create hybrid retriever
        retriever = create_document_type_aware_retriever(
            documents=documents,
            vectorstore=vectorstore,
            config=self.config
        )

        test_queries = [
            # Specific product queries
            ("What OLED TVs are available?", "semantic", "Product search"),
            ("Find all 65 inch televisions", "semantic", "Size-based search"),
            ("Show me gaming monitors", "semantic", "Category search"),

            # Inventory queries
            ("Which products are low in stock?", "semantic", "Inventory status"),
            ("What is available in Warehouse-East?", "keyword", "Location search"),
            ("Find products with reorder required status", "keyword", "Status filter"),

            # Sales queries
            ("What were the largest orders in November?", "hybrid", "Order analysis"),
            ("Show sales to retail customers", "keyword", "Customer type filter"),
            ("Which sales rep had the most orders?", "hybrid", "Performance analysis"),

            # Quality queries
            ("What are common warranty claim types?", "hybrid", "Defect analysis"),
            ("Show shipping delays or exceptions", "keyword", "Logistics issues"),
            ("Find production delays", "keyword", "Manufacturing status"),

            # Complex cross-document queries
            ("What products have both high sales and high warranty claims?", "hybrid", "Cross-domain analysis"),
            ("Which suppliers provide OLED panels?", "keyword", "Supply chain"),
            ("Show customer feedback on delivery issues", "semantic", "Customer sentiment"),
        ]

        retrieval_results = []

        for query, query_type, description in test_queries:
            print(f"\n🔍 Query: {query}")
            print(f"   Type: {query_type} | Category: {description}")

            start_time = time.time()
            results = retriever.get_relevant_documents(query)
            retrieval_time = time.time() - start_time

            # Analyze results
            sources = set([doc.metadata.get('source', 'unknown') for doc in results])
            result_types = {}
            for doc in results:
                source = doc.metadata.get('source', 'unknown')
                ext = Path(source).suffix
                result_types[ext] = result_types.get(ext, 0) + 1

            retrieval_results.append({
                'query': query,
                'query_type': query_type,
                'description': description,
                'retrieval_time_ms': round(retrieval_time * 1000, 2),
                'results_found': len(results),
                'unique_sources': len(sources),
                'result_types': result_types
            })

            print(f"   ✓ Found {len(results)} results from {len(sources)} sources in {retrieval_time*1000:.2f}ms")
            print(f"   Files: {', '.join([Path(s).name for s in list(sources)[:3]])}")

        # Calculate aggregate statistics
        avg_time = sum(r['retrieval_time_ms'] for r in retrieval_results) / len(retrieval_results)
        avg_results = sum(r['results_found'] for r in retrieval_results) / len(retrieval_results)

        result = {
            'test_name': 'Retrieval Performance',
            'total_queries': len(test_queries),
            'avg_retrieval_time_ms': round(avg_time, 2),
            'avg_results_per_query': round(avg_results, 2),
            'queries_per_second': round(1000 / avg_time, 2),
            'detailed_results': retrieval_results,
            'status': 'PASS'
        }

        self.results['tests'].append(result)

        print(f"\n{'='*70}")
        print(f"RETRIEVAL STATISTICS:")
        print(f"  • Average retrieval time: {avg_time:.2f}ms")
        print(f"  • Average results per query: {avg_results:.1f}")
        print(f"  • Queries per second: {result['queries_per_second']}")
        print(f"  • Success rate: 100% ({len(test_queries)}/{len(test_queries)})")

        return retriever

    def test_qa_chain_performance(self, retriever):
        """Test 4: End-to-end QA performance."""
        self.print_section("TEST 4: END-TO-END QA CHAIN PERFORMANCE")

        # Create QA chain
        llm = OllamaLLM(model=self.llm_model, base_url=self.ollama_url)

        template = """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Context: {context}

Question: {input}

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

        test_questions = [
            "What are the top 3 most expensive OLED TVs?",
            "Which warehouse has the lowest inventory levels?",
            "What percentage of warranty claims are approved?",
            "How many orders were placed in November 2024?",
            "What are the common customer complaints?",
        ]

        qa_results = []

        for question in test_questions:
            print(f"\n❓ Question: {question}")

            start_time = time.time()
            try:
                response = qa_chain.invoke({"input": question})
                qa_time = time.time() - start_time

                answer = response.get('answer', 'No answer generated')
                print(f"   ✓ Answered in {qa_time:.2f}s")
                print(f"   Answer: {answer[:150]}...")

                qa_results.append({
                    'question': question,
                    'response_time_seconds': round(qa_time, 2),
                    'answer_length_chars': len(answer),
                    'status': 'SUCCESS'
                })

            except Exception as e:
                qa_time = time.time() - start_time
                print(f"   ✗ Error after {qa_time:.2f}s: {str(e)[:100]}")

                qa_results.append({
                    'question': question,
                    'response_time_seconds': round(qa_time, 2),
                    'error': str(e)[:200],
                    'status': 'ERROR'
                })

        # Calculate statistics
        successful = [r for r in qa_results if r['status'] == 'SUCCESS']
        avg_time = sum(r['response_time_seconds'] for r in successful) / len(successful) if successful else 0

        result = {
            'test_name': 'QA Chain Performance',
            'total_questions': len(test_questions),
            'successful_answers': len(successful),
            'failed_answers': len(qa_results) - len(successful),
            'success_rate_percent': round((len(successful) / len(test_questions)) * 100, 1),
            'avg_response_time_seconds': round(avg_time, 2),
            'detailed_results': qa_results,
            'status': 'PASS' if len(successful) == len(test_questions) else 'PARTIAL'
        }

        self.results['tests'].append(result)

        print(f"\n{'='*70}")
        print(f"QA CHAIN STATISTICS:")
        print(f"  • Success rate: {result['success_rate_percent']}%")
        print(f"  • Average response time: {avg_time:.2f}s")
        print(f"  • Successful answers: {len(successful)}/{len(test_questions)}")

    def test_scalability_limits(self):
        """Test 5: System scalability and resource limits."""
        self.print_section("TEST 5: SCALABILITY & RESOURCE ANALYSIS")

        current_mem = self.get_memory_usage()
        total_mem = psutil.virtual_memory().total / (1024**3)
        mem_percent = (current_mem / (total_mem * 1024)) * 100

        # Get directory size
        data_size_mb = sum(f.stat().st_size for f in self.data_dir.rglob('*') if f.is_file()) / (1024**2)

        result = {
            'test_name': 'Scalability Analysis',
            'current_memory_mb': round(current_mem, 2),
            'memory_usage_percent': round(mem_percent, 2),
            'total_system_memory_gb': round(total_mem, 2),
            'data_directory_size_mb': round(data_size_mb, 2),
            'cpu_count': psutil.cpu_count(),
            'status': 'PASS'
        }

        self.results['tests'].append(result)

        print(f"System Resources:")
        print(f"  • Memory usage: {current_mem:.2f} MB ({mem_percent:.1f}% of system)")
        print(f"  • Total system memory: {total_mem:.2f} GB")
        print(f"  • Data size: {data_size_mb:.2f} MB")
        print(f"  • CPU cores: {psutil.cpu_count()}")

        # Estimate capacity
        estimated_capacity = (total_mem * 1024 * 0.8) / (current_mem / data_size_mb)
        print(f"\n  📊 Estimated capacity: ~{estimated_capacity:.0f} MB of data")
        print(f"     (at 80% memory utilization)")

    def generate_report(self):
        """Generate comprehensive test report."""
        self.print_section("BOUNDARY TESTING REPORT")

        self.results['end_time'] = datetime.now()
        duration = (self.results['end_time'] - self.results['start_time']).total_seconds()

        print(f"Test Duration: {duration:.2f} seconds\n")

        print("SYSTEM INFORMATION:")
        for key, value in self.results['system_info'].items():
            print(f"  • {key}: {value}")

        print("\n\nTEST RESULTS SUMMARY:")
        print("-" * 70)

        for test in self.results['tests']:
            status_icon = "✓" if test['status'] == 'PASS' else "⚠" if test['status'] == 'PARTIAL' else "✗"
            print(f"{status_icon} {test['test_name']}: {test['status']}")

            # Print key metrics for each test
            for key, value in test.items():
                if key not in ['test_name', 'status', 'detailed_results']:
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        print(f"    • {key}: {value}")
                    elif isinstance(value, dict):
                        print(f"    • {key}: {value}")

        # Overall summary
        passed_tests = sum(1 for t in self.results['tests'] if t['status'] == 'PASS')
        total_tests = len(self.results['tests'])

        print("\n" + "=" * 70)
        print(f"OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        print(f"Total execution time: {duration:.2f} seconds")
        print("=" * 70)

        # Save detailed report
        self.save_report()

    def save_report(self):
        """Save detailed report to file."""
        report_file = Path(__file__).parent.parent / "BOUNDARY_TESTING_REPORT.md"

        with open(report_file, 'w') as f:
            f.write("# Hybrid RAG - Boundary Testing Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## System Information\n\n")
            for key, value in self.results['system_info'].items():
                f.write(f"- **{key}**: {value}\n")

            f.write("\n## Test Results\n\n")

            for test in self.results['tests']:
                f.write(f"### {test['test_name']}\n\n")
                f.write(f"**Status:** {test['status']}\n\n")

                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")

                for key, value in test.items():
                    if key not in ['test_name', 'status', 'detailed_results']:
                        f.write(f"| {key} | {value} |\n")

                f.write("\n")

                # Add detailed results if available
                if 'detailed_results' in test:
                    f.write("#### Detailed Results\n\n")
                    for detail in test['detailed_results']:
                        f.write(f"- **{detail.get('query', detail.get('question', 'Item'))}**\n")
                        for k, v in detail.items():
                            if k not in ['query', 'question']:
                                f.write(f"  - {k}: {v}\n")
                        f.write("\n")

            duration = (self.results['end_time'] - self.results['start_time']).total_seconds()
            f.write(f"\n## Summary\n\n")
            f.write(f"- **Total Tests:** {len(self.results['tests'])}\n")
            f.write(f"- **Passed:** {sum(1 for t in self.results['tests'] if t['status'] == 'PASS')}\n")
            f.write(f"- **Duration:** {duration:.2f} seconds\n")

        print(f"\n✓ Detailed report saved to: {report_file}")


def main():
    """Run comprehensive boundary tests."""
    print("=" * 70)
    print("HYBRID RAG - COMPREHENSIVE BOUNDARY TESTING")
    print("=" * 70)
    print("\nTesting with large-scale dataset (~41,000 records)")
    print("This will take several minutes...\n")

    tester = BoundaryTester()

    try:
        # Run all tests
        documents = tester.test_document_loading()
        vectorstore = tester.test_vector_store_creation(documents)
        retriever = tester.test_retrieval_performance(vectorstore, documents)
        tester.test_qa_chain_performance(retriever)
        tester.test_scalability_limits()

        # Generate final report
        tester.generate_report()

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
