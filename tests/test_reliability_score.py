#!/usr/bin/env python3
"""
RAG System Reliability Scoring Test

This script provides a simple, quantifiable reliability score for the RAG system.
It tests critical failure modes and calculates an overall confidence score.

Run: python tests/test_reliability_score.py

Outputs:
- Overall reliability percentage
- Per-category scores
- Specific failures with recommendations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import yaml
from datetime import datetime
from typing import Dict, List, Tuple
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


class ReliabilityTester:
    """Tests RAG system reliability and calculates confidence score."""

    def __init__(self):
        """Initialize the RAG system for testing."""
        print("🔧 Initializing RAG system for reliability testing...")
        configure_logging()

        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Load documents
        data_dir = self.config['data']['directory']
        data_path = Path(__file__).parent.parent / data_dir
        loader = DocumentLoaderUtility(str(data_path), config=self.config)
        self.documents = loader.load_documents()

        # Initialize Ollama
        ollama_url = self.config['ollama']['base_url']
        embedding_model = self.config['ollama']['embedding_model']
        llm_model = self.config['ollama']['llm_model']

        self.embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        self.llm = OllamaLLM(model=llm_model, base_url=ollama_url)

        # Create vector store
        persist_dir = Path(__file__).parent.parent / self.config['vector_store']['persist_directory']
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

        # Create QA chain with strict prompt
        prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Answer the user's question based ONLY on the provided context.

CRITICAL RULES:
1. If the context does not contain the answer, respond with: "I don't have this information in the documents."
2. NEVER make up or infer information not explicitly in the context
3. For numbers, provide EXACT values from context
4. If context is contradictory, acknowledge it
5. Do not use general knowledge - ONLY the context

<context>
{context}
</context>

Question: {input}

Answer:""")

        document_chain = create_stuff_documents_chain(self.llm, prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, document_chain)

        self.results = []
        print("✅ System initialized\n")

    def query(self, question: str) -> str:
        """Execute a query and return answer."""
        response = self.rag_chain.invoke({"input": question})
        return response['answer']

    def test_hallucination_resistance(self) -> Tuple[int, int]:
        """Test if system resists making up information."""
        print("📊 Testing hallucination resistance...")
        tests = [
            ("What is the CEO's name?", ["don't have", "not available", "no information"]),
            ("How many employees work at the company?", ["don't have", "not available", "no information"]),
            ("What was the stock price yesterday?", ["don't have", "not available", "no information"]),
            ("What is the company's mission statement?", ["don't have", "not available", "no information"]),
        ]

        passed = 0
        total = len(tests)

        for query, acceptable_phrases in tests:
            answer = self.query(query).lower()
            # Check if answer contains any acceptable phrase
            if any(phrase in answer for phrase in acceptable_phrases):
                passed += 1
                self.results.append({
                    'category': 'Hallucination Resistance',
                    'query': query,
                    'passed': True,
                    'answer': answer[:80]
                })
            else:
                self.results.append({
                    'category': 'Hallucination Resistance',
                    'query': query,
                    'passed': False,
                    'answer': answer[:80],
                    'issue': 'May be hallucinating - did not indicate lack of information'
                })

        print(f"  Result: {passed}/{total} passed\n")
        return passed, total

    def test_numerical_accuracy(self) -> Tuple[int, int]:
        """Test if system provides exact numerical values."""
        print("📊 Testing numerical accuracy...")
        tests = [
            # These tests check if exact numbers are maintained
            ("How many entries are in the Customer Feedback Q4 2024 document?", "600"),
            ("How many customer feedback entries are documented?", "600"),
        ]

        passed = 0
        total = len(tests)

        for query, expected_number in tests:
            answer = self.query(query)
            if expected_number in answer:
                passed += 1
                self.results.append({
                    'category': 'Numerical Accuracy',
                    'query': query,
                    'passed': True,
                    'answer': answer[:80]
                })
            else:
                self.results.append({
                    'category': 'Numerical Accuracy',
                    'query': query,
                    'passed': False,
                    'answer': answer[:80],
                    'expected': f"Should contain '{expected_number}'",
                    'issue': 'Exact number not found in answer'
                })

        print(f"  Result: {passed}/{total} passed\n")
        return passed, total

    def test_source_accuracy(self) -> Tuple[int, int]:
        """Test if system retrieves from correct sources."""
        print("📊 Testing source accuracy...")
        tests = [
            ("What products are in the catalog?", ["product", "catalog"]),
            ("What is the customer feedback like?", ["feedback", "customer"]),
            ("What are the inventory levels?", ["inventory", "stock"]),
        ]

        passed = 0
        total = len(tests)

        for query, expected_terms in tests:
            answer = self.query(query).lower()
            # Check if answer contains relevant terms (indicates correct retrieval)
            if any(term in answer for term in expected_terms):
                passed += 1
                self.results.append({
                    'category': 'Source Accuracy',
                    'query': query,
                    'passed': True,
                    'answer': answer[:80]
                })
            else:
                self.results.append({
                    'category': 'Source Accuracy',
                    'query': query,
                    'passed': False,
                    'answer': answer[:80],
                    'issue': 'May not have retrieved correct source'
                })

        print(f"  Result: {passed}/{total} passed\n")
        return passed, total

    def test_context_adherence(self) -> Tuple[int, int]:
        """Test if system stays within context boundaries."""
        print("📊 Testing context adherence...")
        tests = [
            # Questions where system should NOT provide general knowledge
            ("What is machine learning?", ["don't have", "not in", "documents don't"]),
            ("How does a TV work?", ["don't have", "not in", "documents don't"]),
            ("What is the capital of France?", ["don't have", "not in", "documents don't"]),
        ]

        passed = 0
        total = len(tests)

        for query, rejection_phrases in tests:
            answer = self.query(query).lower()
            # System should refuse to answer from general knowledge
            if any(phrase in answer for phrase in rejection_phrases):
                passed += 1
                self.results.append({
                    'category': 'Context Adherence',
                    'query': query,
                    'passed': True,
                    'answer': answer[:80]
                })
            else:
                self.results.append({
                    'category': 'Context Adherence',
                    'query': query,
                    'passed': False,
                    'answer': answer[:80],
                    'issue': 'May be using general knowledge instead of documents'
                })

        print(f"  Result: {passed}/{total} passed\n")
        return passed, total

    def test_basic_functionality(self) -> Tuple[int, int]:
        """Test if system can answer basic in-domain questions."""
        print("📊 Testing basic functionality...")
        tests = [
            # Questions that SHOULD be answerable
            "What files are in the data directory?",
            "What types of documents are available?",
            "What is Q4 2024?",
        ]

        passed = 0
        total = len(tests)

        for query in tests:
            answer = self.query(query).lower()
            # Check that we got SOME answer (not just "don't have")
            if "don't have" not in answer or len(answer) > 50:
                passed += 1
                self.results.append({
                    'category': 'Basic Functionality',
                    'query': query,
                    'passed': True,
                    'answer': answer[:80]
                })
            else:
                self.results.append({
                    'category': 'Basic Functionality',
                    'query': query,
                    'passed': False,
                    'answer': answer[:80],
                    'issue': 'Failed to answer in-domain question'
                })

        print(f"  Result: {passed}/{total} passed\n")
        return passed, total

    def run_all_tests(self) -> Dict:
        """Run all tests and return results."""
        print("="*70)
        print("RAG SYSTEM RELIABILITY TEST")
        print("="*70)
        print()

        category_results = {}

        # Run each test category
        category_results['Hallucination Resistance'] = self.test_hallucination_resistance()
        category_results['Numerical Accuracy'] = self.test_numerical_accuracy()
        category_results['Source Accuracy'] = self.test_source_accuracy()
        category_results['Context Adherence'] = self.test_context_adherence()
        category_results['Basic Functionality'] = self.test_basic_functionality()

        # Calculate overall score
        total_passed = sum(passed for passed, _ in category_results.values())
        total_tests = sum(total for _, total in category_results.values())
        overall_score = (total_passed / total_tests * 100) if total_tests > 0 else 0

        return {
            'overall_score': overall_score,
            'total_passed': total_passed,
            'total_tests': total_tests,
            'category_results': category_results,
            'detailed_results': self.results
        }

    def generate_report(self, results: Dict):
        """Generate and save detailed report."""
        print("="*70)
        print("RELIABILITY SCORE SUMMARY")
        print("="*70)
        print()
        print(f"Overall Reliability: {results['overall_score']:.1f}%")
        print(f"Tests Passed: {results['total_passed']}/{results['total_tests']}")
        print()
        print("Category Breakdown:")
        for category, (passed, total) in results['category_results'].items():
            score = (passed/total*100) if total > 0 else 0
            print(f"  {category}: {score:.1f}% ({passed}/{total})")
        print()

        # Show failures
        failures = [r for r in results['detailed_results'] if not r['passed']]
        if failures:
            print("⚠️  FAILURES DETECTED:")
            print()
            for failure in failures:
                print(f"Category: {failure['category']}")
                print(f"Query: {failure['query']}")
                print(f"Answer: {failure['answer']}")
                if 'issue' in failure:
                    print(f"Issue: {failure['issue']}")
                if 'expected' in failure:
                    print(f"Expected: {failure['expected']}")
                print()

        # Recommendations
        print("="*70)
        print("RECOMMENDATIONS FOR IMPROVEMENT")
        print("="*70)
        print()

        if results['overall_score'] >= 90:
            print("✅ System is highly reliable (≥90%)")
            print("   Minor refinements may still improve edge cases")
        elif results['overall_score'] >= 75:
            print("⚠️  System is moderately reliable (75-90%)")
            print("   Focus on failures above to improve")
        else:
            print("❌ System needs significant improvement (<75%)")
            print("   Address critical failures before production use")

        print()
        print("Specific Recommendations:")

        # Check which categories failed most
        for category, (passed, total) in results['category_results'].items():
            score = (passed/total*100) if total > 0 else 0
            if score < 80:
                print(f"\n🔧 {category} needs improvement ({score:.1f}%):")
                if category == "Hallucination Resistance":
                    print("   - Strengthen prompt with more explicit 'no information' instructions")
                    print("   - Add confidence scoring to answers")
                    print("   - Implement source verification")
                elif category == "Numerical Accuracy":
                    print("   - Ensure chunks preserve complete numerical data")
                    print("   - Test chunk size adjustments")
                    print("   - Add post-processing for number extraction")
                elif category == "Source Accuracy":
                    print("   - Adjust retrieval weights (csv_weight vs text_weight)")
                    print("   - Increase k value for retrievers")
                    print("   - Improve query preprocessing")
                elif category == "Context Adherence":
                    print("   - Make prompt more restrictive about general knowledge")
                    print("   - Add input validation for out-of-domain queries")
                elif category == "Basic Functionality":
                    print("   - Check document loading and chunking")
                    print("   - Verify embeddings are being created correctly")
                    print("   - Test retriever configuration")

        # Save detailed report
        report_path = Path(__file__).parent.parent / "RELIABILITY_TEST_REPORT.md"
        with open(report_path, 'w') as f:
            f.write("# RAG System Reliability Test Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Overall Score: {results['overall_score']:.1f}%\n\n")
            f.write(f"**Tests Passed:** {results['total_passed']}/{results['total_tests']}\n\n")

            f.write("## Category Scores\n\n")
            for category, (passed, total) in results['category_results'].items():
                score = (passed/total*100) if total > 0 else 0
                f.write(f"- **{category}:** {score:.1f}% ({passed}/{total})\n")

            f.write("\n## Detailed Results\n\n")
            for result in results['detailed_results']:
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                f.write(f"### {status} - {result['category']}\n\n")
                f.write(f"**Query:** {result['query']}\n\n")
                f.write(f"**Answer:** {result['answer']}\n\n")
                if not result['passed']:
                    if 'issue' in result:
                        f.write(f"**Issue:** {result['issue']}\n\n")
                    if 'expected' in result:
                        f.write(f"**Expected:** {result['expected']}\n\n")
                f.write("---\n\n")

            f.write("\n## Improvement Recommendations\n\n")
            f.write("See console output for detailed recommendations.\n")

        print(f"\n📄 Detailed report saved to: {report_path}")
        print()


def main():
    """Run reliability tests."""
    try:
        tester = ReliabilityTester()
        results = tester.run_all_tests()
        tester.generate_report(results)

    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
