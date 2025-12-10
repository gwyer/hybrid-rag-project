# Testing Quick Start Guide

## TL;DR - Run This First

```bash
# Get your system's reliability score (takes ~5 minutes)
python tests/test_reliability_score.py
```

This will output:
- **Overall reliability percentage** (target: ≥90%)
- Specific failures with recommendations
- Detailed report: `RELIABILITY_TEST_REPORT.md`

## What Am I Testing?

Your RAG system can fail in subtle ways:

❌ **Hallucination**: Making up information
❌ **Wrong answers**: Retrieving incorrect context
❌ **Out-of-scope**: Using general knowledge instead of your documents
❌ **Number errors**: Approximating instead of being exact

The tests catch these failures **before** they happen in production.

## Quick Testing Workflow

### Step 1: Baseline Score (5 minutes)

```bash
python tests/test_reliability_score.py
```

**Example Output:**
```
Overall Reliability: 78.5%
Tests Passed: 11/14

Category Breakdown:
  Hallucination Resistance: 75.0% (3/4)
  Numerical Accuracy: 100.0% (2/2)
  Source Accuracy: 100.0% (3/3)
  Context Adherence: 66.7% (2/3)
  Basic Functionality: 100.0% (3/3)
```

### Step 2: Understand Failures

Open the generated report:
```bash
cat RELIABILITY_TEST_REPORT.md
```

Look for ❌ FAIL entries - these show exactly what went wrong.

### Step 3: Fix and Re-test

Common fixes:

**If Hallucination Resistance fails:**
```python
# Edit your demo script's prompt
# Add more explicit instructions:
prompt = ChatPromptTemplate.from_template("""
CRITICAL: If the context doesn't contain the answer,
respond EXACTLY with: "I don't have this information in the documents."
NEVER make up or infer information.

<context>
{context}
</context>

Question: {input}
""")
```

**If Context Adherence fails:**
```yaml
# Edit config/config.yaml
# Increase retrieval to get more context
retrieval:
  vector_search_k: 8  # Up from 5
  keyword_search_k: 8  # Up from 5
```

**Then re-run:**
```bash
python tests/test_reliability_score.py
```

### Step 4: Deep Dive Testing (Optional)

Once you're above 85%, run comprehensive tests:

```bash
# This takes ~15-20 minutes, runs 21 tests
python tests/test_rag_boundaries.py
```

This tests edge cases like:
- Empty queries
- Very long queries
- Negation ("products WITHOUT warranty claims")
- Multi-document reasoning
- Special characters

## Understanding Test Results

### Reliability Score Meanings

| Score | Meaning | Action |
|-------|---------|--------|
| **≥95%** | 🟢 Production Ready | Deploy with confidence |
| **85-94%** | 🟡 Nearly There | Fix remaining issues |
| **75-84%** | 🟠 Needs Work | Address failures before production |
| **<75%** | 🔴 Not Ready | Significant improvements needed |

### What Each Category Tests

**1. Hallucination Resistance** (Critical)
- Asks about information NOT in documents
- Should respond: "I don't have this information"
- Failure = System is making up answers ⚠️

**2. Numerical Accuracy** (Critical)
- Tests if exact numbers are preserved
- Should say "600 entries" not "~600 entries"
- Failure = Data integrity issues ⚠️

**3. Source Accuracy** (Important)
- Tests if correct documents are retrieved
- Should find product catalog when asked about products
- Failure = Retrieval issues

**4. Context Adherence** (Critical)
- Tests if system uses ONLY your documents
- Should NOT answer "What is machine learning?" from general knowledge
- Failure = Using training data instead of your docs ⚠️

**5. Basic Functionality** (Critical)
- Tests if system can answer in-domain questions
- Should successfully answer questions about your data
- Failure = Core system broken ⚠️

## Common Issues & Quick Fixes

### Issue 1: "Low Hallucination Resistance Score"

**Problem:** System invents information

**Quick Fix:**
```python
# In your demo script, strengthen the prompt:
prompt = ChatPromptTemplate.from_template("""
You MUST answer ONLY from the context below.
If the answer is not in the context, say: "I don't have this information in the documents."
DO NOT use any other knowledge.

<context>
{context}
</context>

Question: {input}
""")
```

### Issue 2: "Low Numerical Accuracy"

**Problem:** Numbers are rounded or lost

**Quick Fix:**
```yaml
# config/config.yaml
document_processing:
  text_chunk_size: 1500  # Increase from 1000
  text_chunk_overlap: 300  # Increase from 200
```

Larger chunks preserve more numerical context.

### Issue 3: "Low Source Accuracy"

**Problem:** Not finding the right documents

**Quick Fix:**
```yaml
# config/config.yaml
retrieval:
  vector_search_k: 10  # Increase from 5
  keyword_search_k: 10  # Increase from 5
```

More retrieved documents = better chance of finding the right one.

### Issue 4: "Low Context Adherence"

**Problem:** Using general knowledge instead of documents

**Quick Fix:**
```python
# Make prompt more restrictive:
prompt = ChatPromptTemplate.from_template("""
You are a document search assistant. Your ONLY knowledge is in the context below.
You have NO other knowledge. If the context is empty or doesn't answer the question,
say: "I don't have this information in the documents."

<context>
{context}
</context>

Question: {input}
""")
```

## Advanced: Custom Tests

Add your own critical tests:

```python
# tests/test_custom.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_reliability_score import ReliabilityTester

class MyCustomTests(ReliabilityTester):
    def test_my_critical_query(self):
        """Test the most important query for my use case."""
        answer = self.query("What OLED TVs cost under $1000?")

        # Check answer contains expected information
        assert "TV-OLED" in answer, "Should mention OLED TV products"
        assert "$" in answer, "Should include price information"

        print(f"✅ Critical query test passed")
        print(f"   Answer: {answer[:100]}...")

if __name__ == '__main__':
    tester = MyCustomTests()
    tester.test_my_critical_query()
```

Run:
```bash
python tests/test_custom.py
```

## Interpreting the Reports

### RELIABILITY_TEST_REPORT.md

This file contains:
- Overall score and breakdown
- Every test that was run
- For failures: What went wrong and why
- Specific answer that failed

**Look for:**
- ❌ FAIL entries - these are your problems
- The "Issue" field - explains what went wrong
- The "Expected" field - shows what should happen

### Example Failure Entry

```markdown
### ❌ FAIL - Hallucination Resistance

**Query:** What is the CEO's name?

**Answer:** The CEO is John Smith based on the organizational structure...

**Issue:** May be hallucinating - did not indicate lack of information

**Expected:** Should contain "don't have" or "not available"
```

**What this means:** The system made up a CEO name. This is critical - fix immediately.

**How to fix:** Strengthen prompt to explicitly refuse when information is missing.

## Test Often

### During Development
```bash
# Quick check after making changes
python tests/test_reliability_score.py
```

### Before Deployment
```bash
# Full validation
python tests/test_reliability_score.py
python tests/test_rag_boundaries.py
```

### In Production
```bash
# Weekly validation to catch degradation
python tests/test_reliability_score.py > weekly_report.txt
```

## Success Checklist

Before considering your system "production ready":

- [ ] Reliability score ≥90%
- [ ] All Hallucination Resistance tests pass
- [ ] All Context Adherence tests pass
- [ ] All Numerical Accuracy tests pass
- [ ] All Basic Functionality tests pass
- [ ] Source Accuracy ≥90%
- [ ] Boundary tests run without crashes
- [ ] Custom tests for your use case pass

## Next Steps

1. **Run baseline test** - `python tests/test_reliability_score.py`
2. **Review failures** - Check `RELIABILITY_TEST_REPORT.md`
3. **Fix top issues** - Start with Hallucination and Context Adherence
4. **Re-test** - Iterate until ≥90%
5. **Deep dive** - Run `python tests/test_rag_boundaries.py`
6. **Add custom tests** - For your specific use cases
7. **Monitor** - Run tests regularly

## Getting Help

If stuck on a failure:

1. Check `docs/guides/testing-strategy.md` for detailed solutions
2. Review the "Recommendations" section in test output
3. Look at `tests/test_data_adversarial.json` for similar cases
4. Test with different prompts and configurations

## Remember

⚠️ **A RAG system with <90% reliability will produce wrong answers ~1 in 10 queries.**
✅ **Testing is how you get to 95%+ reliability and trust your system.**

Start testing now:
```bash
python tests/test_reliability_score.py
```
