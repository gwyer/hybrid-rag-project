"""
Structured Query Module
Handles SQL-like queries on CSV and structured data files.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

from langchain_classic.evaluation import load_dataset

class StructuredQueryEngine:
    """Engine for querying structured data files (CSV, etc.)"""

    def __init__(self, data_directory: str):
        """
        Initialize the structured query engine.

        Args:
            data_directory: Path to the directory containing data files
        """
        self.data_directory = Path(data_directory)
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self._load_csv_files()

    def _load_csv_files(self):
        """Load all CSV files into pandas DataFrames."""
        if not self.data_directory.exists():
            return

        for csv_file in self.data_directory.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                self.dataframes[csv_file.stem] = df
                print(f"✅ Loaded CSV: {csv_file.name} ({len(df)} rows, {len(df.columns)} columns)")
            except Exception as e:
                print(f"❌ Error loading {csv_file.name}: {e}")

    def get_available_datasets(self) -> List[Dict[str, Any]]:
        """Get list of available datasets with metadata."""
        datasets = []
        for name, df in self.dataframes.items():
            datasets.append({
                "name": name,
                "rows": len(df),
                "columns": list(df.columns),
                "column_count": len(df.columns)
            })
        return datasets

    def count_by_field(self, dataset: str, field: str, value: str) -> Dict[str, Any]:
        """
        Count rows where a field matches a value.

        Args:
            dataset: Name of the dataset (CSV filename without extension)
            field: Column name to filter on
            value: Value to match

        Returns:
            Dict with count and sample results
        """
        if dataset not in self.dataframes:
            return {
                "success": False,
                "error": f"Dataset '{dataset}' not found. Available: {list(self.dataframes.keys())}"
            }

        df = self.dataframes[dataset]

        if field not in df.columns:
            return {
                "success": False,
                "error": f"Field '{field}' not found. Available: {list(df.columns)}"
            }

        # Filter rows
        matches = df[df[field].astype(str).str.contains(value, case=False, na=False)]

        return {
            "success": True,
            "count": len(matches),
            "total_rows": len(df),
            "field": field,
            "value": value,
            "sample": matches.head(5).to_dict('records') if len(matches) > 0 else []
        }

    def filter_by_field(self, dataset: str, field: str, value: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get all rows where a field matches a value.

        Args:
            dataset: Name of the dataset
            field: Column name to filter on
            value: Value to match
            limit: Maximum number of results to return

        Returns:
            Dict with matching rows
        """
        if dataset not in self.dataframes:
            return {
                "success": False,
                "error": f"Dataset '{dataset}' not found"
            }

        df = self.dataframes[dataset]

        if field not in df.columns:
            return {
                "success": False,
                "error": f"Field '{field}' not found"
            }

        # Filter rows
        matches = df[df[field].astype(str).str.contains(value, case=False, na=False)]

        return {
            "success": True,
            "count": len(matches),
            "results": matches.head(limit).to_dict('records'),
            "truncated": len(matches) > limit
        }

    def query_dataset(self, dataset: str, query: str) -> Dict[str, Any]:
        """
        Execute a pandas query on the dataset.

        Args:
            dataset: Name of the dataset
            query: Pandas query string (e.g., "`First Name` == 'Michael'")

        Returns:
            Dict with query results
        """
        if dataset not in self.dataframes:
            return {
                "success": False,
                "error": f"Dataset '{dataset}' not found"
            }

        try:
            df = self.dataframes[dataset]
            results = df.query(query)

            return {
                "success": True,
                "count": len(results),
                "results": results.head(100).to_dict('records'),
                "truncated": len(results) > 100
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Query error: {str(e)}"
            }

    def get_unique_values(self, dataset: str, field: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get unique values for a field.

        Args:
            dataset: Name of the dataset
            field: Column name
            limit: Maximum number of unique values to return

        Returns:
            Dict with unique values and counts
        """
        if dataset not in self.dataframes:
            return {
                "success": False,
                "error": f"Dataset '{dataset}' not found"
            }

        df = self.dataframes[dataset]

        if field not in df.columns:
            return {
                "success": False,
                "error": f"Field '{field}' not found"
            }

        value_counts = df[field].value_counts().head(limit)

        return {
            "success": True,
            "field": field,
            "unique_count": df[field].nunique(),
            "top_values": value_counts.to_dict()
        }

    def get_stats(self, dataset: str) -> Dict[str, Any]:
        """
        Get statistics about a dataset.

        Args:
            dataset: Name of the dataset

        Returns:
            Dict with dataset statistics
        """
        if dataset not in self.dataframes:
            return {
                "success": False,
                "error": f"Dataset '{dataset}' not found"
            }

        df = self.dataframes[dataset]

        return {
            "success": True,
            "dataset": dataset,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            "sample_row": df.head(1).to_dict('records')[0] if len(df) > 0 else {}
        }


def aggregate_by_field(dataset: str, field: str, aggregation_function: str, sort_by: str = "key"):
    """
    Aggregate dataset by applying a transformation to a field and counting occurrences
    """
    df = load_dataset(dataset)

    # Apply transformation
    if aggregation_function == "extract_year":
        df['_agg_key'] = df[field].apply(extract_year_from_date)
    elif aggregation_function == "extract_domain":
        df['_agg_key'] = df[field].apply(extract_domain)
    # ... other transformations

    # Count occurrences
    counts = df['_agg_key'].value_counts()

    # Sort
    if sort_by == "key":
        counts = counts.sort_index()
    elif sort_by == "count":
        counts = counts.sort_values(ascending=False)

    # Format response
    return {
        "aggregations": [
            {"key": str(key), "count": int(count)}
            for key, count in counts.items()
            if pd.notna(key)
        ],
        "total_records": len(df),
        "null_values": df['_agg_key'].isna().sum()
    }


def extract_year_from_date(date_str):
    """
    Extract 4-digit year from date string in format DD-MMM-YY

    Examples:
        "15-Apr-04" -> 2004
        "23-Dec-99" -> 1999
        "05-Jan-15" -> 2015
        "31-Mar-25" -> 2025
        "01-Jun-26" -> 1926
        None -> None
        "" -> None

    Args:
        date_str: Date string in format DD-MMM-YY

    Returns:
        int: 4-digit year, or None if parsing fails
    """
    import pandas as pd

    # Handle None, NaN, or empty strings
    if pd.isna(date_str) or not date_str or str(date_str).strip() == '':
        return None

    try:
        # Convert to string and strip whitespace
        date_str = str(date_str).strip()

        # Split by dash to get [day, month, year]
        parts = date_str.split('-')

        if len(parts) != 3:
            return None

        # Extract the year part (last element)
        year_str = parts[2]

        # Convert to integer
        year = int(year_str)

        # Convert 2-digit year to 4-digit year
        # Rule: 00-25 = 2000s, 26-99 = 1900s
        if year <= 25:
            return 2000 + year
        elif year <= 99:
            return 1900 + year
        else:
            # Already 4-digit year
            return year

    except (ValueError, IndexError, AttributeError):
        return None


# Alternative implementation using datetime parsing (more robust for various formats)
def extract_year_from_date_v2(date_str):
    """
    Alternative implementation using pandas datetime parsing
    More flexible for various date formats
    """
    import pandas as pd
    from datetime import datetime

    if pd.isna(date_str) or not date_str or str(date_str).strip() == '':
        return None

    try:
        # Try to parse the date using pandas (handles many formats automatically)
        parsed_date = pd.to_datetime(date_str, format='%d-%b-%y', errors='coerce')

        if pd.isna(parsed_date):
            return None

        return parsed_date.year

    except Exception:
        return None


def extract_domain(value):
    """
    Extract domain from email address or URL

    Examples:
        Email addresses:
            "user@example.com" -> "example.com"
            "john.doe@company.org" -> "company.org"

        URLs:
            "https://www.linkedin.com/in/username" -> "linkedin.com"
            "http://google.com" -> "google.com"
            "www.github.com" -> "github.com"

        Invalid:
            None -> None
            "" -> None
            "invalid" -> None

    Args:
        value: Email address or URL string

    Returns:
        str: Domain name, or None if extraction fails
    """
    import pandas as pd
    import re
    from urllib.parse import urlparse

    # Handle None, NaN, or empty strings
    if pd.isna(value) or not value or str(value).strip() == '':
        return None

    try:
        value = str(value).strip().lower()

        # Check if it's an email address (contains @ but not ://)
        if '@' in value and '://' not in value:
            # Email format: extract everything after @
            parts = value.split('@')
            if len(parts) == 2:
                domain = parts[1].strip()
                # Remove any trailing characters that aren't part of domain
                domain = re.match(r'^([a-z0-9.-]+)', domain)
                if domain:
                    return domain.group(1)

        # Check if it's a URL
        elif '://' in value or value.startswith('www.'):
            # Add scheme if missing
            if not value.startswith(('http://', 'https://')):
                value = 'http://' + value

            # Parse URL
            parsed = urlparse(value)
            domain = parsed.netloc or parsed.path.split('/')[0]

            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]

            # Remove port if present
            domain = domain.split(':')[0]

            return domain if domain else None

        # Check if it's just a domain name (no @ or ://)
        elif re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', value):
            # Remove www. prefix if present
            if value.startswith('www.'):
                value = value[4:]
            return value

        return None

    except Exception:
        return None


# Alternative simpler implementation (less robust but faster)
def extract_domain_simple(value):
    """
    Simplified domain extraction - faster but less comprehensive
    """
    import pandas as pd
    import re

    if pd.isna(value) or not value:
        return None

    value = str(value).strip().lower()

    # Email: get everything after @
    if '@' in value:
        match = re.search(r'@([a-z0-9.-]+)', value)
        return match.group(1) if match else None

    # URL: extract domain from URL pattern
    match = re.search(r'://(?:www\.)?([a-z0-9.-]+)', value)
    if match:
        return match.group(1).split(':')[0]  # Remove port if present

    # www.domain pattern
    match = re.search(r'www\.([a-z0-9.-]+)', value)
    if match:
        return match.group(1).split('/')[0]  # Remove path if present

    return None


def aggregate_by_field_v2(dataset: str, field: str, aggregation_function: str, sort_by: str = "key"):
    """
    Aggregate dataset by applying a transformation to a field
    """
    import pandas as pd

    # Load the dataset (assuming you have this function)
    df = load_dataset(dataset)

    # Apply the appropriate transformation function
    if aggregation_function == "extract_year":
        df['_agg_key'] = df[field].apply(extract_year_from_date)

    elif aggregation_function == "extract_domain":
        df['_agg_key'] = df[field].apply(extract_domain)

    elif aggregation_function == "extract_month":
        # Extract month name or number
        def extract_month(date_str):
            if pd.isna(date_str):
                return None
            try:
                parts = str(date_str).split('-')
                if len(parts) == 3:
                    return parts[1]  # Returns month abbreviation (e.g., "Apr")
            except:
                return None

        df['_agg_key'] = df[field].apply(extract_month)

    elif aggregation_function == "lowercase":
        df['_agg_key'] = df[field].str.lower()

    elif aggregation_function == "first_word":
        df['_agg_key'] = df[field].str.split().str[0]

    else:
        raise ValueError(f"Unknown aggregation function: {aggregation_function}")

    # Remove null values
    df_filtered = df[df['_agg_key'].notna()]

    # Count occurrences
    counts = df_filtered['_agg_key'].value_counts()

    # Sort
    if sort_by == "key":
        counts = counts.sort_index()
    elif sort_by == "count":
        counts = counts.sort_values(ascending=False)
    else:
        raise ValueError(f"Unknown sort_by: {sort_by}")

    # Format response
    return {
        "aggregations": [
            {"key": str(key), "count": int(count)}
            for key, count in counts.items()
        ],
        "total_records": len(df),
        "non_null_records": len(df_filtered),
        "null_values": df['_agg_key'].isna().sum()
    }


def extract_year_from_date_vectorized(series):
    """
    Vectorized version for pandas Series - much faster for large datasets
    """
    import pandas as pd

    # Use pandas string operations for vectorization
    year_str = series.str.split('-').str[2]
    year_int = pd.to_numeric(year_str, errors='coerce')

    # Vectorized year conversion
    return year_int.apply(lambda y: 2000 + y if pd.notna(y) and y <= 25
    else 1900 + y if pd.notna(y) and y <= 99
    else y)