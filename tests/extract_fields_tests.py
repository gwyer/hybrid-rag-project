# Test cases
from src.hybrid_rag.structured_query import extract_domain, extract_year_from_date

if __name__ == "__main__":
    test_cases = [
        # Email addresses
        ("user@example.com", "example.com"),
        ("john.doe@company.org", "company.org"),
        ("katie.p.smith@outlook.com", "outlook.com"),

        # URLs
        ("https://www.linkedin.com/in/username", "linkedin.com"),
        ("http://google.com", "google.com"),
        ("www.github.com", "github.com"),
        ("https://api.anthropic.com/v1/messages", "api.anthropic.com"),

        # Plain domains
        ("example.com", "example.com"),
        ("www.example.com", "example.com"),

        # Invalid
        ("", None),
        (None, None),
        ("invalid", None),
        ("@invalid", None),
    ]

    print("\nTesting extract_domain:")
    for value_input, expected in test_cases:
        result = extract_domain(value_input)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {value_input!r:50} -> {result!r:20} (expected {expected!r})")


# Test cases
if __name__ == "__main__":
    test_cases = [
        ("15-Apr-04", 2004),
        ("23-Dec-99", 1999),
        ("05-Jan-15", 2015),
        ("31-Mar-25", 2025),
        ("01-Jun-26", 1926),
        ("8-Feb-11", 2011),
        ("29-Apr-07", 2007),
        ("", None),
        (None, None),
        ("invalid", None),
        ("2024-01-15", None),  # Wrong format
    ]

    print("Testing extract_year_from_date:")
    for date_input, expected in test_cases:
        result = extract_year_from_date(date_input)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {date_input!r:20} -> {result} (expected {expected})")