"""
Query Preprocessor for Product ID Translation

This module handles translation between different product ID formats
to enable cross-document correlation.
"""
import csv
from pathlib import Path
from typing import Dict, Optional, List


class ProductIDMapper:
    """Handles product ID mapping between different formats."""

    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize the product ID mapper.

        Args:
            mapping_file: Path to product_id_mapping.csv. If None, uses default location.
        """
        if mapping_file is None:
            # Default to data/product_id_mapping.csv
            mapping_file = Path(__file__).parent.parent.parent / "data" / "product_id_mapping.csv"

        self.mapping_file = Path(mapping_file)
        self.mappings: Dict[str, Dict[str, str]] = {}
        self.reverse_mappings: Dict[str, str] = {}

        if self.mapping_file.exists():
            self._load_mappings()

    def _load_mappings(self):
        """Load product ID mappings from CSV file."""
        with open(self.mapping_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                standard_id = row['Standard_Product_ID']
                internal_id = row['Internal_Product_ID']

                # Store full mapping data
                self.mappings[standard_id] = {
                    'internal_id': internal_id,
                    'product_name': row['Product_Name'],
                    'category': row['Category'],
                    'notes': row.get('Notes', '')
                }

                # Store reverse mapping (internal → standard)
                self.reverse_mappings[internal_id] = standard_id

    def get_internal_id(self, standard_id: str) -> Optional[str]:
        """
        Get internal product ID from standard ID.

        Args:
            standard_id: Standard product ID (e.g., "TV-OLED-55-001")

        Returns:
            Internal product ID (e.g., "PROD-4304") or None if not found
        """
        mapping = self.mappings.get(standard_id)
        return mapping['internal_id'] if mapping else None

    def get_standard_id(self, internal_id: str) -> Optional[str]:
        """
        Get standard product ID from internal ID.

        Args:
            internal_id: Internal product ID (e.g., "PROD-4304")

        Returns:
            Standard product ID (e.g., "TV-OLED-55-001") or None if not found
        """
        return self.reverse_mappings.get(internal_id)

    def get_product_name(self, standard_id: str) -> Optional[str]:
        """Get product name from standard ID."""
        mapping = self.mappings.get(standard_id)
        return mapping['product_name'] if mapping else None

    def get_all_ids(self, standard_id: str) -> List[str]:
        """
        Get all ID variations for a product.

        Args:
            standard_id: Standard product ID

        Returns:
            List of all IDs: [standard_id, internal_id, product_name]
        """
        mapping = self.mappings.get(standard_id)
        if not mapping:
            return [standard_id]

        return [
            standard_id,
            mapping['internal_id'],
            mapping['product_name']
        ]


class QueryPreprocessor:
    """Preprocesses queries to expand product IDs."""

    def __init__(self, mapping_file: Optional[str] = None):
        """Initialize with product ID mapper."""
        self.id_mapper = ProductIDMapper(mapping_file)

    def expand_query(self, query: str) -> str:
        """
        Expand query with alternative product IDs.

        Example:
            Input:  "Show me warranty claims for product TV-OLED-55-001"
            Output: "Show me warranty claims for product TV-OLED-55-001 PROD-4304 OLED 55\" TV Premium"

        Args:
            query: Original query string

        Returns:
            Expanded query with alternative IDs
        """
        # Find potential product IDs in query
        import re
        potential_ids = re.findall(r'\b[A-Z]+-[A-Z0-9]+-[\d-]+\b', query)

        expanded_query = query
        for product_id in potential_ids:
            # Get all ID variations
            all_ids = self.id_mapper.get_all_ids(product_id)

            if len(all_ids) > 1:
                # Add internal ID and product name to query
                internal_id = all_ids[1]
                product_name = all_ids[2]

                # Append to query
                expanded_query += f" {internal_id} {product_name}"

        return expanded_query

    def translate_product_ids(self, query: str, to_internal: bool = True) -> str:
        """
        Translate product IDs in query between standard and internal formats.

        Args:
            query: Query string
            to_internal: If True, convert standard→internal. If False, convert internal→standard.

        Returns:
            Query with translated product IDs
        """
        import re

        if to_internal:
            # Find standard IDs (e.g., TV-OLED-55-001) and replace with internal
            pattern = r'\b([A-Z]+-[A-Z0-9]+-[\d-]+)\b'

            def replace_with_internal(match):
                standard_id = match.group(1)
                internal_id = self.id_mapper.get_internal_id(standard_id)
                return internal_id if internal_id else standard_id

            return re.sub(pattern, replace_with_internal, query)

        else:
            # Find internal IDs (e.g., PROD-4304) and replace with standard
            pattern = r'\bPROD-\d+\b'

            def replace_with_standard(match):
                internal_id = match.group(0)
                standard_id = self.id_mapper.get_standard_id(internal_id)
                return standard_id if standard_id else internal_id

            return re.sub(pattern, replace_with_standard, query)


# Example usage
if __name__ == "__main__":
    # Test the mapper
    mapper = ProductIDMapper()

    print("=== Product ID Mapper Test ===\n")

    # Test standard → internal
    standard_id = "TV-OLED-55-001"
    internal_id = mapper.get_internal_id(standard_id)
    product_name = mapper.get_product_name(standard_id)

    print(f"Standard ID: {standard_id}")
    print(f"  → Internal ID: {internal_id}")
    print(f"  → Product Name: {product_name}")

    # Test internal → standard
    if internal_id:
        reverse = mapper.get_standard_id(internal_id)
        print(f"\nInternal ID: {internal_id}")
        print(f"  → Standard ID: {reverse}")

    # Test query preprocessing
    print("\n=== Query Preprocessor Test ===\n")

    preprocessor = QueryPreprocessor()

    original_query = "Show me warranty claims for product TV-OLED-55-001"
    expanded_query = preprocessor.expand_query(original_query)

    print(f"Original Query:")
    print(f"  {original_query}")
    print(f"\nExpanded Query:")
    print(f"  {expanded_query}")

    # Test translation
    print(f"\nTranslated to Internal IDs:")
    print(f"  {preprocessor.translate_product_ids(original_query, to_internal=True)}")
