"""
Add Special Product IDs from Specifications to Mapping

This script adds the TV-OLED-XX-XXX format products that appear
at the end of product_specifications.txt to the mapping file.
"""

import csv
import random
from pathlib import Path

# Special products from product_specifications.txt
SPECIAL_PRODUCTS = [
    {
        'standard_id': 'TV-OLED-55-001',
        'name': 'OLED 55" TV Premium',
        'category': 'OLED TV',
        'price': '1299.99'
    },
    {
        'standard_id': 'TV-OLED-48-001',
        'name': 'OLED 48" TV Premium',
        'category': 'OLED TV',
        'price': '999.99'
    },
    {
        'standard_id': 'TV-OLED-65-001',
        'name': 'OLED 65" TV Premium',
        'category': 'OLED TV',
        'price': '1799.99'
    },
    {
        'standard_id': 'TV-OLED-77-001',
        'name': 'OLED 77" TV Flagship',
        'category': 'OLED TV',
        'price': '2999.99'
    },
    {
        'standard_id': 'TV-OLED-83-001',
        'name': 'OLED 83" TV Flagship',
        'category': 'OLED TV',
        'price': '4999.99'
    },
    {
        'standard_id': 'SPEAKER-WIRELESS-001',
        'name': 'Wireless Speaker System',
        'category': 'Audio',
        'price': '299.99'
    },
    {
        'standard_id': 'HDMI-CABLE-001',
        'name': 'HDMI 2.1 Cable',
        'category': 'Accessory',
        'price': '29.99'
    },
    {
        'standard_id': 'SOUNDBAR-001',
        'name': 'Premium Soundbar',
        'category': 'Audio',
        'price': '599.99'
    },
    {
        'standard_id': 'PROJECTOR-001',
        'name': '4K Projector',
        'category': 'Projector',
        'price': '1499.99'
    },
    {
        'standard_id': 'MONITOR-001',
        'name': 'Professional Monitor 32"',
        'category': 'Monitor',
        'price': '799.99'
    },
    {
        'standard_id': 'LAPTOP-STAND-001',
        'name': 'Adjustable Laptop Stand',
        'category': 'Accessory',
        'price': '49.99'
    }
]


def load_existing_mapping(mapping_file):
    """Load existing mapping data."""
    existing = []
    existing_standards = set()
    existing_internals = set()

    with open(mapping_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.append(row)
            existing_standards.add(row['Standard_Product_ID'])
            existing_internals.add(row['Internal_Product_ID'])

    return existing, existing_standards, existing_internals


def get_unused_internal_ids(existing_internals, warranty_file, inventory_file, count=11):
    """Get internal IDs that exist in data files but aren't mapped yet."""
    all_internal_ids = set()

    # Read from warranty claims
    with open(warranty_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Product_ID' in row:
                all_internal_ids.add(row['Product_ID'])

    # Read from inventory
    with open(inventory_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Product_ID' in row:
                all_internal_ids.add(row['Product_ID'])

    # Get unused IDs
    unused = list(all_internal_ids - existing_internals)

    # Return random sample
    random.seed(42)  # For reproducibility
    return random.sample(unused, min(count, len(unused)))


def main():
    base_path = Path(__file__).parent.parent.parent
    mapping_file = base_path / 'data' / 'product_id_mapping.csv'
    warranty_file = base_path / 'data' / 'warranty_claims_q4.csv'
    inventory_file = base_path / 'data' / 'inventory_levels.csv'

    print("🔍 Adding special products to mapping...")

    # Load existing mapping
    existing, existing_standards, existing_internals = load_existing_mapping(mapping_file)

    print(f"   Current mappings: {len(existing)}")
    print(f"   Mapped standard IDs: {len(existing_standards)}")
    print(f"   Mapped internal IDs: {len(existing_internals)}")

    # Get unused internal IDs
    unused_internal_ids = get_unused_internal_ids(
        existing_internals,
        warranty_file,
        inventory_file,
        count=len(SPECIAL_PRODUCTS)
    )

    print(f"\n📋 Found {len(unused_internal_ids)} unused internal IDs")

    # Create new mappings for special products
    new_mappings = []
    for i, product in enumerate(SPECIAL_PRODUCTS):
        if product['standard_id'] in existing_standards:
            print(f"   ⏭️  {product['standard_id']} already mapped, skipping")
            continue

        if i >= len(unused_internal_ids):
            print(f"   ⚠️  No more internal IDs available for {product['standard_id']}")
            break

        mapping = {
            'Standard_Product_ID': product['standard_id'],
            'Internal_Product_ID': unused_internal_ids[i],
            'Product_Name': product['name'],
            'Category': product['category'],
            'Price_USD': product['price'],
            'Notes': 'Premium product from specifications'
        }
        new_mappings.append(mapping)
        print(f"   ✅ Mapping {product['standard_id']} → {unused_internal_ids[i]}")

    # Combine existing and new mappings
    all_mappings = existing + new_mappings

    # Write back to file
    with open(mapping_file, 'w', newline='') as f:
        fieldnames = ['Standard_Product_ID', 'Internal_Product_ID', 'Product_Name',
                     'Category', 'Price_USD', 'Notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_mappings)

    print(f"\n✅ Mapping file updated!")
    print(f"   Total mappings: {len(all_mappings)}")
    print(f"   New mappings added: {len(new_mappings)}")

    # Show specific mapping for TV-OLED-55-001
    print(f"\n🎯 Special Product Mappings:")
    for mapping in new_mappings:
        if 'TV-OLED' in mapping['Standard_Product_ID']:
            print(f"   {mapping['Standard_Product_ID']} → {mapping['Internal_Product_ID']} ({mapping['Product_Name']})")


if __name__ == '__main__':
    main()
