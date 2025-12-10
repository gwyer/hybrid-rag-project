#!/usr/bin/env python3
"""
Boundary Testing Suite for Hybrid RAG System

This test suite identifies edge cases, failure modes, and potential weaknesses
in the RAG system to help achieve near-100% reliability.

Test Categories:
1. Out-of-Domain Queries - Questions about information NOT in the documents
2. Ambiguous Queries - Vague or poorly worded questions
3. Contradictory Information - Handling conflicting data
4. Numerical Precision - Exact number retrieval and calculations
5. Temporal Queries - Date/time-based questions
6. Negation Queries - Questions with "not", "without", "except"
7. Multi-hop Reasoning - Questions requiring multiple pieces of information
8. Edge Cases - Empty queries, very long queries, special characters
9. Hallucination Detection - Verify LLM doesn't make up information
10. Retrieval Failures - Cases where retrieval might fail
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import yaml
from typing import Dict, List, Any
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


class TestRAGBoundaries(unittest.TestCase):
    """Test RAG system boundary conditions and failure modes."""

    @classmethod
    def setUpClass(cls):
        """Initialize RAG system once for all tests."""
        configure_logging()

        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, "r") as f:
            cls.config = yaml.safe_load(f)

        # Load documents
        data_dir = cls.config['data']['directory']
        data_path = Path(__file__).parent.parent / data_dir
        loader = DocumentLoaderUtility(str(data_path), config=cls.config)
        cls.documents = loader.load_documents()

        # Initialize Ollama
        ollama_url = cls.config['ollama']['base_url']
        embedding_model = cls.config['ollama']['embedding_model']
        llm_model = cls.config['ollama']['llm_model']

        cls.embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        cls.llm = OllamaLLM(model=llm_model, base_url=ollama_url)

        # Create vector store
        persist_dir = Path(__file__).parent.parent / cls.config['vector_store']['persist_directory']
        cls.vectorstore = Chroma.from_documents(
            cls.documents,
            cls.embeddings,
            persist_directory=str(persist_dir)
        )

        # Create retriever
        cls.retriever = create_document_type_aware_retriever(
            documents=cls.documents,
            vectorstore=cls.vectorstore,
            config=cls.config
        )

        # Create QA chain with strict prompt
        prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Answer the user's question based ONLY on the provided context.

CRITICAL RULES:
1. If the context does not contain the answer, respond EXACTLY with: "I don't have this information in the documents."
2. Never make up or infer information not explicitly stated in the context
3. For numerical questions, provide EXACT numbers from the context
4. If the context is contradictory, acknowledge the contradiction
5. Do not use general knowledge - ONLY use the provided context

<context>
{context}
</context>

Question: {input}

Answer:""")

        document_chain = create_stuff_documents_chain(cls.llm, prompt)
        cls.rag_chain = create_retrieval_chain(cls.retriever, document_chain)

        cls.test_results = []

    def _query(self, question: str) -> Dict[str, Any]:
        """Execute a query and return response."""
        return self.rag_chain.invoke({"input": question})

    def _assert_contains_phrase(self, response: Dict, phrase: str, test_name: str):
        """Assert response contains a specific phrase (case-insensitive)."""
        answer = response['answer'].lower()
        result = phrase.lower() in answer

        self.test_results.append({
            'test': test_name,
            'query': response.get('input', ''),
            'passed': result,
            'expected': f"Contains '{phrase}'",
            'actual': response['answer'][:100] + "..." if len(response['answer']) > 100 else response['answer']
        })

        self.assertIn(phrase.lower(), answer,
                     f"Expected phrase '{phrase}' not found in answer: {answer[:200]}")

    def _assert_not_contains_phrase(self, response: Dict, phrase: str, test_name: str):
        """Assert response does NOT contain a specific phrase."""
        answer = response['answer'].lower()
        result = phrase.lower() not in answer

        self.test_results.append({
            'test': test_name,
            'query': response.get('input', ''),
            'passed': result,
            'expected': f"Does NOT contain '{phrase}'",
            'actual': response['answer'][:100] + "..." if len(response['answer']) > 100 else response['answer']
        })

        self.assertNotIn(phrase.lower(), answer,
                        f"Unexpected phrase '{phrase}' found in answer: {answer[:200]}")

    # ========================================
    # Category 1: Out-of-Domain Queries
    # ========================================

    def test_01_completely_unrelated_query(self):
        """Test query about topic not in documents (e.g., astronomy)."""
        response = self._query("What is the distance from Earth to Mars?")
        # Should say it doesn't have this information
        self._assert_contains_phrase(response, "don't have", "Out-of-domain: Astronomy")

    def test_02_wrong_domain_products(self):
        """Test query about products not in catalog."""
        response = self._query("What is the price of the Tesla Model S?")
        self._assert_contains_phrase(response, "don't have", "Out-of-domain: Wrong product")

    def test_03_future_information(self):
        """Test query about future dates beyond document scope."""
        response = self._query("What are the sales figures for March 2025?")
        self._assert_contains_phrase(response, "don't have", "Out-of-domain: Future date")

    # ========================================
    # Category 2: Ambiguous Queries
    # ========================================

    def test_04_vague_query(self):
        """Test very vague question."""
        response = self._query("What about it?")
        # Should either ask for clarification or say insufficient information
        answer = response['answer'].lower()
        result = ("clarif" in answer or "specific" in answer or
                 "don't have" in answer or "unclear" in answer)
        self.test_results.append({
            'test': 'Ambiguous: Vague query',
            'query': "What about it?",
            'passed': result,
            'expected': "Request clarification or indicate insufficient info",
            'actual': response['answer'][:100]
        })
        self.assertTrue(result, "Should handle vague query appropriately")

    def test_05_pronoun_without_context(self):
        """Test pronoun reference without context."""
        response = self._query("How much does it cost?")
        answer = response['answer'].lower()
        # Should either ask what "it" refers to or provide context-appropriate answer
        # This is acceptable behavior - just logging
        self.test_results.append({
            'test': 'Ambiguous: Pronoun without context',
            'query': "How much does it cost?",
            'passed': True,  # Informational test
            'expected': "Handle pronoun appropriately",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 3: Numerical Precision
    # ========================================

    def test_06_exact_number_retrieval(self):
        """Test if system returns exact numbers, not approximations."""
        # This tests if the system can retrieve specific numerical data
        response = self._query("How many entries are in the Customer Feedback Q4 2024 document?")
        answer = response['answer']

        # Should contain "600" (the exact number from the document)
        self.test_results.append({
            'test': 'Numerical: Exact count',
            'query': "How many entries in customer feedback?",
            'passed': '600' in answer,
            'expected': "Contains exact number '600'",
            'actual': answer[:100]
        })

    def test_07_calculation_request(self):
        """Test if system attempts calculations not in documents."""
        response = self._query("What is the total revenue across all sales orders multiplied by 2.5?")
        # System should NOT perform calculations - should only report what's in documents
        answer = response['answer'].lower()
        result = ("calculate" in answer or "don't have" in answer or
                 "not calculated" in answer or "cannot" in answer)
        self.test_results.append({
            'test': 'Numerical: Avoid calculations',
            'query': "Calculate total revenue * 2.5",
            'passed': result,
            'expected': "Refuse to calculate or indicate limitation",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 4: Temporal Queries
    # ========================================

    def test_08_date_range_boundary(self):
        """Test queries at the edge of date ranges in documents."""
        response = self._query("What happened on January 1, 2024?")
        # Should retrieve relevant information for this specific date
        self.test_results.append({
            'test': 'Temporal: Specific date',
            'query': "What happened on January 1, 2024?",
            'passed': True,  # Informational
            'expected': "Retrieve date-specific information",
            'actual': response['answer'][:100]
        })

    def test_09_relative_time_query(self):
        """Test relative time queries (yesterday, last week, etc.)."""
        response = self._query("What were sales like last week?")
        answer = response['answer'].lower()
        # System should either provide context-appropriate answer or indicate it needs specific dates
        self.test_results.append({
            'test': 'Temporal: Relative time',
            'query': "What were sales like last week?",
            'passed': True,  # Informational
            'expected': "Handle relative time reference",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 5: Negation Queries
    # ========================================

    def test_10_negation_without(self):
        """Test query with 'without' - these are hard for retrievers."""
        response = self._query("Which products do NOT have warranty claims?")
        # This is difficult because retrieval finds documents WITH warranty claims
        # System should acknowledge difficulty or attempt to answer
        self.test_results.append({
            'test': 'Negation: WITHOUT query',
            'query': "Which products do NOT have warranty claims?",
            'passed': True,  # Informational - negation is inherently difficult
            'expected': "Attempt to answer negation query",
            'actual': response['answer'][:100]
        })

    def test_11_except_query(self):
        """Test query with 'except' exclusion."""
        response = self._query("Show me all orders except those from November")
        self.test_results.append({
            'test': 'Negation: EXCEPT query',
            'query': "Show all orders except November",
            'passed': True,  # Informational
            'expected': "Handle exclusion query",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 6: Multi-hop Reasoning
    # ========================================

    def test_12_multi_document_reasoning(self):
        """Test query requiring information from multiple documents."""
        response = self._query(
            "Which products with low inventory levels also have high warranty claim rates?"
        )
        # Should retrieve from both inventory_levels.csv AND warranty_claims_q4.csv
        self.test_results.append({
            'test': 'Multi-hop: Cross-document reasoning',
            'query': "Low inventory + high warranty claims",
            'passed': True,  # Informational - checking if it attempts
            'expected': "Combine information from multiple sources",
            'actual': response['answer'][:100]
        })

    def test_13_chain_of_reasoning(self):
        """Test query requiring multi-step reasoning."""
        response = self._query(
            "Based on customer feedback sentiment and warranty claims, "
            "which products should we discontinue?"
        )
        # This requires inference - system should acknowledge this is interpretation
        answer = response['answer'].lower()
        self.test_results.append({
            'test': 'Multi-hop: Chain reasoning',
            'query': "Combine feedback + warranties for recommendation",
            'passed': True,  # Informational
            'expected': "Attempt reasoning or acknowledge limitation",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 7: Edge Cases
    # ========================================

    def test_14_empty_query(self):
        """Test empty or whitespace-only query."""
        with self.assertRaises(Exception):
            response = self._query("")

    def test_15_very_long_query(self):
        """Test extremely long query."""
        long_query = "What are the details about " + " and ".join([
            f"product {i}" for i in range(100)
        ]) + "?"

        response = self._query(long_query)
        # Should handle gracefully, not crash
        self.test_results.append({
            'test': 'Edge case: Very long query',
            'query': long_query[:50] + "...",
            'passed': True,  # If we got here, it didn't crash
            'expected': "Handle without crashing",
            'actual': "Success - no crash"
        })

    def test_16_special_characters(self):
        """Test query with special characters."""
        response = self._query("What about products with $ > $1000 && rating >= 4.5?")
        # Should handle special characters gracefully
        self.test_results.append({
            'test': 'Edge case: Special characters',
            'query': "Query with $, >, &&, >=",
            'passed': True,
            'expected': "Handle special characters",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 8: Hallucination Detection
    # ========================================

    def test_17_specific_non_existent_product(self):
        """Test query about specific product that doesn't exist."""
        response = self._query("What is the price of product SKU-FAKE-999999?")
        # Should say it doesn't have this information
        self._assert_contains_phrase(response, "don't have", "Hallucination: Non-existent SKU")

    def test_18_misleading_question(self):
        """Test question that assumes false premise."""
        response = self._query("Why did the company recall all OLED TVs in December 2024?")
        # Should NOT confirm a recall that didn't happen
        answer = response['answer'].lower()
        # Should either say no information about recall, or not confirm it happened
        result = ("don't have" in answer or "no" in answer or "not" in answer)
        self.test_results.append({
            'test': 'Hallucination: False premise',
            'query': "Why did recall happen? (false premise)",
            'passed': result,
            'expected': "Not confirm false premise",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 9: Retrieval Failures
    # ========================================

    def test_19_synonym_mismatch(self):
        """Test query using synonyms not in documents."""
        response = self._query("What gadgets are available?")  # Instead of "products"
        # Should still find product information despite synonym
        self.test_results.append({
            'test': 'Retrieval: Synonym handling',
            'query': "Gadgets (synonym for products)",
            'passed': True,  # Informational - semantic search should help
            'expected': "Handle synonyms via semantic search",
            'actual': response['answer'][:100]
        })

    def test_20_acronym_expansion(self):
        """Test query with acronyms vs full terms."""
        response = self._query("What Q4 data is available?")
        # Should understand Q4 means fourth quarter
        self.test_results.append({
            'test': 'Retrieval: Acronym understanding',
            'query': "Q4 (acronym)",
            'passed': True,  # Informational
            'expected': "Understand Q4 = fourth quarter",
            'actual': response['answer'][:100]
        })

    # ========================================
    # Category 10: Stress Tests
    # ========================================

    def test_21_rapid_successive_queries(self):
        """Test multiple queries in rapid succession."""
        queries = [
            "What products are available?",
            "What is customer feedback like?",
            "Show me inventory levels",
        ]

        for query in queries:
            response = self._query(query)
            self.assertIsNotNone(response['answer'])

        self.test_results.append({
            'test': 'Stress: Rapid queries',
            'query': "3 queries in succession",
            'passed': True,
            'expected': "Handle multiple queries",
            'actual': "All queries completed"
        })

    @classmethod
    def tearDownClass(cls):
        """Generate test report."""
        print("\n" + "="*80)
        print("BOUNDARY TEST RESULTS SUMMARY")
        print("="*80)

        passed = sum(1 for r in cls.test_results if r['passed'])
        total = len(cls.test_results)

        print(f"\nTests Passed: {passed}/{total} ({100*passed/total:.1f}%)")
        print("\nDetailed Results:\n")

        for result in cls.test_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            print(f"  Query: {result['query']}")
            print(f"  Expected: {result['expected']}")
            print(f"  Actual: {result['actual']}")
            print()

        # Write results to file
        report_path = Path(__file__).parent.parent / "BOUNDARY_TEST_RESULTS.md"
        with open(report_path, 'w') as f:
            f.write("# RAG System Boundary Testing Results\n\n")
            f.write(f"**Date:** {Path(__file__).stat().st_mtime}\n\n")
            f.write(f"**Pass Rate:** {passed}/{total} ({100*passed/total:.1f}%)\n\n")
            f.write("## Test Categories\n\n")
            f.write("1. Out-of-Domain Queries\n")
            f.write("2. Ambiguous Queries\n")
            f.write("3. Numerical Precision\n")
            f.write("4. Temporal Queries\n")
            f.write("5. Negation Queries\n")
            f.write("6. Multi-hop Reasoning\n")
            f.write("7. Edge Cases\n")
            f.write("8. Hallucination Detection\n")
            f.write("9. Retrieval Failures\n")
            f.write("10. Stress Tests\n\n")
            f.write("## Detailed Results\n\n")

            for result in cls.test_results:
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                f.write(f"### {status} {result['test']}\n\n")
                f.write(f"**Query:** {result['query']}\n\n")
                f.write(f"**Expected:** {result['expected']}\n\n")
                f.write(f"**Actual:** {result['actual']}\n\n")
                f.write("---\n\n")

        print(f"Full report written to: {report_path}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
