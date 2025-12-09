#!/usr/bin/env python3
"""
Generate large-scale test data for boundary testing the Hybrid RAG system.
This script augments existing data files with thousands of realistic entries.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def generate_product_catalog(output_file: Path, num_records: int = 5000):
    """Generate extensive product catalog with diverse products."""
    print(f"Generating {num_records} product catalog entries...")

    categories = ["LCD TV", "OLED TV", "QLED TV", "Computer Monitor", "Commercial Display",
                  "Projector", "Accessories", "Audio"]
    screen_sizes = [24, 27, 32, 40, 43, 45, 48, 50, 55, 60, 65, 70, 75, 77, 80, 83, 85, 98]
    resolutions = ["720p", "1080p", "1440p", "4K UHD", "8K UHD"]
    panel_types = ["IPS", "VA", "OLED", "QLED", "LCD", "DLP", "Laser", "N/A"]
    refresh_rates = ["60Hz", "75Hz", "120Hz", "144Hz", "165Hz", "240Hz", "N/A"]
    stock_statuses = ["In Stock", "In Stock", "In Stock", "In Stock", "Limited", "Pre-order"]

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Product_ID', 'Product_Name', 'Category', 'Screen_Size', 'Resolution',
            'Panel_Type', 'Price_USD', 'MSRP_USD', 'Cost_USD', 'Margin_Percent',
            'Weight_LBS', 'Dimensions', 'HDR_Support', 'Smart_TV', 'Refresh_Rate',
            'Release_Year', 'Warranty_Years', 'Energy_Rating', 'Stock_Status'
        ])

        for i in range(num_records):
            category = random.choice(categories)
            screen_size = random.choice(screen_sizes) if category != "Accessories" else 0
            resolution = random.choice(resolutions)
            panel_type = random.choice(panel_types)

            # Realistic pricing based on category and size
            if category == "OLED TV":
                base_price = 800 + screen_size * 20
            elif category == "QLED TV":
                base_price = 500 + screen_size * 15
            elif category == "LCD TV":
                base_price = 200 + screen_size * 8
            elif category == "Computer Monitor":
                base_price = 150 + screen_size * 10
            elif category == "Commercial Display":
                base_price = 600 + screen_size * 12
            elif category == "Projector":
                base_price = random.randint(300, 2000)
            else:  # Accessories
                base_price = random.randint(10, 300)

            price = round(base_price + random.uniform(-50, 100), 2)
            msrp = round(price * random.uniform(1.1, 1.3), 2)
            cost = round(price * random.uniform(0.5, 0.7), 2)
            margin = round(((price - cost) / price) * 100, 0)

            weight = round(screen_size * 0.8 + random.uniform(5, 15), 1) if screen_size > 0 else round(random.uniform(0.5, 10), 1)

            product_id = f"{category.replace(' ', '-').upper()}-{screen_size}-{i:05d}"
            product_name = f"{category} {screen_size}\" - Model {i:05d}" if screen_size > 0 else f"{category} - SKU {i:05d}"

            hdr_support = random.choice(["Yes", "No", "N/A"])
            smart_tv = random.choice(["Yes", "No", "N/A"])
            refresh_rate = random.choice(refresh_rates)
            release_year = random.choice([2023, 2024, 2024, 2024])
            warranty_years = random.choice([1, 2, 2, 3, 3, 5])
            energy_rating = random.choice(["A+", "A++", "A+++", "B+", "N/A"])
            stock_status = random.choice(stock_statuses)

            dimensions = f"{screen_size*0.89:.1f}x{screen_size*0.51:.1f}x{random.uniform(2, 5):.1f}" if screen_size > 0 else "N/A"

            writer.writerow([
                product_id, product_name, category, screen_size, resolution, panel_type,
                price, msrp, cost, margin, weight, dimensions, hdr_support, smart_tv,
                refresh_rate, release_year, warranty_years, energy_rating, stock_status
            ])

    print(f"✓ Generated {num_records} products in {output_file}")


def generate_inventory_levels(output_file: Path, num_records: int = 10000):
    """Generate inventory tracking data across multiple warehouses."""
    print(f"Generating {num_records} inventory records...")

    warehouses = ["Warehouse-East", "Warehouse-West", "Warehouse-Central",
                  "Warehouse-North", "Warehouse-South", "Warehouse-Midwest"]
    statuses = ["Normal", "Normal", "Normal", "Low Stock", "Reorder Required", "Overstocked"]

    base_date = datetime(2024, 12, 1)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Date', 'Product_ID', 'Product_Name', 'Warehouse', 'Quantity_On_Hand',
            'Quantity_Reserved', 'Quantity_Available', 'Reorder_Point', 'Reorder_Quantity',
            'Unit_Cost', 'Total_Value', 'Last_Received', 'Next_Expected', 'Status'
        ])

        for i in range(num_records):
            product_id = f"PROD-{random.randint(1000, 99999):05d}"
            product_name = f"Product {random.randint(1000, 9999)}"
            warehouse = random.choice(warehouses)

            qty_on_hand = random.randint(10, 1000)
            qty_reserved = random.randint(0, min(50, qty_on_hand))
            qty_available = qty_on_hand - qty_reserved
            reorder_point = random.randint(20, 100)
            reorder_qty = random.randint(50, 200)

            unit_cost = round(random.uniform(10, 2000), 2)
            total_value = round(qty_on_hand * unit_cost, 2)

            last_received = base_date - timedelta(days=random.randint(1, 30))
            next_expected = base_date + timedelta(days=random.randint(1, 45))

            status = "Low Stock" if qty_available < reorder_point else random.choice(statuses)

            writer.writerow([
                base_date.strftime("%Y-%m-%d"), product_id, product_name, warehouse,
                qty_on_hand, qty_reserved, qty_available, reorder_point, reorder_qty,
                unit_cost, total_value, last_received.strftime("%Y-%m-%d"),
                next_expected.strftime("%Y-%m-%d"), status
            ])

    print(f"✓ Generated {num_records} inventory records in {output_file}")


def generate_sales_orders(output_file: Path, num_records: int = 8000):
    """Generate sales order history."""
    print(f"Generating {num_records} sales orders...")

    customer_types = ["Retailer", "E-commerce", "Hospitality", "Enterprise",
                      "Commercial", "Education", "Government", "Healthcare", "Consumer"]
    ship_methods = ["Ground", "Freight", "Air", "White Glove", "Express"]
    statuses = ["Delivered", "Delivered", "Delivered", "In Transit", "Processing", "Cancelled"]
    regions = ["East", "West", "Central", "North", "South", "National"]
    sales_reps = ["John Smith", "Sarah Johnson", "Mike Wilson", "Emily Davis",
                  "Robert Brown", "Lisa Anderson", "David Martinez", "Jennifer Lee"]

    base_date = datetime(2024, 11, 1)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Order_ID', 'Order_Date', 'Customer_ID', 'Customer_Name', 'Customer_Type',
            'Product_ID', 'Product_Name', 'Quantity', 'Unit_Price', 'Total_Amount',
            'Discount_Percent', 'Net_Amount', 'Ship_Date', 'Ship_Method', 'Status',
            'Region', 'Sales_Rep'
        ])

        for i in range(num_records):
            order_id = f"ORD-2024-{50000 + i}"
            order_date = base_date + timedelta(days=random.randint(0, 60))
            customer_id = f"CUST-{random.randint(10000, 99999)}"
            customer_name = f"Customer {random.randint(1000, 9999)}"
            customer_type = random.choice(customer_types)

            product_id = f"PROD-{random.randint(1000, 9999):04d}"
            product_name = f"Product {random.randint(100, 999)}"

            # Quantity varies by customer type
            if customer_type in ["Retailer", "E-commerce"]:
                quantity = random.randint(50, 1000)
            elif customer_type in ["Enterprise", "Government"]:
                quantity = random.randint(20, 500)
            else:
                quantity = random.randint(1, 100)

            unit_price = round(random.uniform(50, 2500), 2)
            total_amount = round(quantity * unit_price, 2)

            # Discount varies by customer type and quantity
            if customer_type in ["Retailer", "E-commerce"]:
                discount = random.randint(15, 25)
            elif quantity > 100:
                discount = random.randint(10, 20)
            else:
                discount = random.randint(0, 10)

            net_amount = round(total_amount * (1 - discount / 100), 2)

            ship_date = order_date + timedelta(days=random.randint(1, 14))
            ship_method = random.choice(ship_methods)
            status = random.choice(statuses)
            region = random.choice(regions)
            sales_rep = random.choice(sales_reps)

            writer.writerow([
                order_id, order_date.strftime("%Y-%m-%d"), customer_id, customer_name,
                customer_type, product_id, product_name, quantity, unit_price,
                total_amount, discount, net_amount, ship_date.strftime("%Y-%m-%d"),
                ship_method, status, region, sales_rep
            ])

    print(f"✓ Generated {num_records} sales orders in {output_file}")


def generate_warranty_claims(output_file: Path, num_records: int = 3000):
    """Generate warranty claim records."""
    print(f"Generating {num_records} warranty claims...")

    claim_types = ["Defect", "Damage", "Performance", "Dead Pixel", "Power Issue",
                   "Connectivity", "Audio", "Screen Defect", "Shipping Damage"]
    statuses = ["Approved", "Approved", "Pending", "Denied", "Under Review"]
    resolutions = ["Replacement", "Repair", "Refund", "Parts Sent", "Pending"]

    base_date = datetime(2024, 10, 1)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Claim_ID', 'Claim_Date', 'Product_ID', 'Product_Name', 'Serial_Number',
            'Purchase_Date', 'Claim_Type', 'Description', 'Status', 'Resolution',
            'Resolution_Date', 'Cost', 'Customer_ID', 'Customer_Name'
        ])

        for i in range(num_records):
            claim_id = f"WRN-2024-Q4-{10000 + i}"
            claim_date = base_date + timedelta(days=random.randint(0, 90))

            product_id = f"PROD-{random.randint(1000, 9999):04d}"
            product_name = f"Product Model {random.randint(100, 999)}"
            serial_number = f"SN{random.randint(100000, 999999)}"

            purchase_date = claim_date - timedelta(days=random.randint(30, 730))
            claim_type = random.choice(claim_types)

            descriptions = {
                "Defect": "Manufacturing defect reported by customer",
                "Damage": "Physical damage during shipping or handling",
                "Performance": "Unit not performing to specifications",
                "Dead Pixel": "Dead or stuck pixels reported on display",
                "Power Issue": "Device fails to power on or powers off randomly",
                "Connectivity": "HDMI or connectivity issues reported",
                "Audio": "Audio output problems or distortion",
                "Screen Defect": "Display showing artifacts or discoloration",
                "Shipping Damage": "Damage occurred during delivery"
            }
            description = descriptions.get(claim_type, "Customer reported issue")

            status = random.choice(statuses)
            resolution = random.choice(resolutions) if status == "Approved" else "Pending"

            resolution_date = claim_date + timedelta(days=random.randint(1, 30)) if status == "Approved" else None
            cost = round(random.uniform(50, 1500), 2) if status == "Approved" else 0.0

            customer_id = f"CUST-{random.randint(10000, 99999)}"
            customer_name = f"Customer {random.randint(1000, 9999)}"

            writer.writerow([
                claim_id, claim_date.strftime("%Y-%m-%d"), product_id, product_name,
                serial_number, purchase_date.strftime("%Y-%m-%d"), claim_type,
                description, status, resolution,
                resolution_date.strftime("%Y-%m-%d") if resolution_date else "N/A",
                cost, customer_id, customer_name
            ])

    print(f"✓ Generated {num_records} warranty claims in {output_file}")


def generate_production_schedule(output_file: Path, num_records: int = 4000):
    """Generate production schedule data."""
    print(f"Generating {num_records} production schedule entries...")

    facilities = ["Plant-Shanghai", "Plant-Vietnam", "Plant-Mexico", "Plant-Poland", "Plant-India"]
    statuses = ["Scheduled", "In Progress", "Completed", "Delayed", "On Hold"]
    shifts = ["Day Shift", "Night Shift", "Weekend Shift"]

    base_date = datetime(2024, 12, 1)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Schedule_ID', 'Production_Date', 'Product_ID', 'Product_Name',
            'Facility', 'Planned_Quantity', 'Actual_Quantity', 'Shift',
            'Start_Time', 'End_Time', 'Status', 'Yield_Percent', 'Defect_Count'
        ])

        for i in range(num_records):
            schedule_id = f"PROD-SCH-{base_date.year}-{10000 + i}"
            production_date = base_date + timedelta(days=random.randint(0, 60))

            product_id = f"PROD-{random.randint(1000, 9999):04d}"
            product_name = f"Product Line {random.randint(100, 999)}"
            facility = random.choice(facilities)

            planned_qty = random.randint(50, 1000)
            status = random.choice(statuses)

            if status == "Completed":
                actual_qty = int(planned_qty * random.uniform(0.85, 1.0))
                yield_percent = round((actual_qty / planned_qty) * 100, 1)
                defect_count = int(actual_qty * random.uniform(0.01, 0.05))
            elif status == "In Progress":
                actual_qty = int(planned_qty * random.uniform(0.3, 0.7))
                yield_percent = round((actual_qty / planned_qty) * 100, 1)
                defect_count = int(actual_qty * random.uniform(0.01, 0.05))
            else:
                actual_qty = 0
                yield_percent = 0.0
                defect_count = 0

            shift = random.choice(shifts)
            start_time = f"{random.randint(6, 22):02d}:00"
            end_time = f"{(random.randint(6, 22) + 8) % 24:02d}:00"

            writer.writerow([
                schedule_id, production_date.strftime("%Y-%m-%d"), product_id,
                product_name, facility, planned_qty, actual_qty, shift,
                start_time, end_time, status, yield_percent, defect_count
            ])

    print(f"✓ Generated {num_records} production schedule entries in {output_file}")


def generate_supplier_pricing(output_file: Path, num_records: int = 6000):
    """Generate supplier pricing data."""
    print(f"Generating {num_records} supplier pricing records...")

    suppliers = ["Samsung Display", "LG Display", "BOE Technology", "Sharp Corporation",
                 "AU Optronics", "Innolux", "Tianma", "JDI", "Visionox", "TCL CSOT"]
    components = ["LCD Panel", "OLED Panel", "QLED Panel", "LED Backlight", "T-Con Board",
                  "Power Supply", "Main Board", "Remote Control", "Stand", "Bezel"]
    currencies = ["USD", "USD", "USD", "EUR", "CNY"]

    base_date = datetime(2024, 12, 1)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Supplier_ID', 'Supplier_Name', 'Component_ID', 'Component_Name',
            'Unit_Price', 'Currency', 'MOQ', 'Lead_Time_Days', 'Quote_Date',
            'Valid_Until', 'Payment_Terms', 'Quality_Rating', 'On_Time_Delivery'
        ])

        for i in range(num_records):
            supplier_id = f"SUP-{random.randint(1000, 9999):04d}"
            supplier_name = random.choice(suppliers)

            component_id = f"COMP-{random.randint(10000, 99999)}"
            component_name = random.choice(components)

            # Realistic pricing based on component
            price_ranges = {
                "LCD Panel": (50, 300),
                "OLED Panel": (200, 800),
                "QLED Panel": (100, 500),
                "LED Backlight": (10, 50),
                "T-Con Board": (15, 60),
                "Power Supply": (20, 80),
                "Main Board": (30, 120),
                "Remote Control": (3, 15),
                "Stand": (8, 40),
                "Bezel": (5, 25)
            }

            price_range = price_ranges.get(component_name, (10, 100))
            unit_price = round(random.uniform(*price_range), 2)
            currency = random.choice(currencies)

            moq = random.choice([100, 200, 500, 1000, 2000])
            lead_time = random.randint(30, 120)

            quote_date = base_date - timedelta(days=random.randint(0, 30))
            valid_until = quote_date + timedelta(days=random.randint(60, 180))

            payment_terms = random.choice(["Net 30", "Net 60", "Net 90", "30% Deposit", "LC at Sight"])
            quality_rating = round(random.uniform(85, 100), 1)
            on_time_delivery = round(random.uniform(80, 100), 1)

            writer.writerow([
                supplier_id, supplier_name, component_id, component_name,
                unit_price, currency, moq, lead_time,
                quote_date.strftime("%Y-%m-%d"), valid_until.strftime("%Y-%m-%d"),
                payment_terms, quality_rating, on_time_delivery
            ])

    print(f"✓ Generated {num_records} supplier pricing records in {output_file}")


def generate_shipping_manifests(output_file: Path, num_records: int = 5000):
    """Generate shipping manifest data."""
    print(f"Generating {num_records} shipping manifests...")

    carriers = ["FedEx", "UPS", "DHL", "USPS", "XPO Logistics", "J.B. Hunt"]
    ship_methods = ["Ground", "Express", "Freight", "Air", "Ocean"]
    statuses = ["Delivered", "Delivered", "In Transit", "At Terminal", "Out for Delivery", "Exception"]

    base_date = datetime(2024, 11, 1)

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Manifest_ID', 'Ship_Date', 'Carrier', 'Tracking_Number', 'Ship_Method',
            'Origin', 'Destination', 'Package_Count', 'Total_Weight_LBS',
            'Declared_Value', 'Freight_Cost', 'Status', 'Delivery_Date', 'Signature_Required'
        ])

        for i in range(num_records):
            manifest_id = f"SHIP-{base_date.year}-{20000 + i}"
            ship_date = base_date + timedelta(days=random.randint(0, 60))

            carrier = random.choice(carriers)
            tracking_number = f"{carrier[:3].upper()}{random.randint(100000000, 999999999)}"
            ship_method = random.choice(ship_methods)

            cities = ["New York NY", "Los Angeles CA", "Chicago IL", "Houston TX",
                     "Phoenix AZ", "Philadelphia PA", "San Antonio TX", "San Diego CA",
                     "Dallas TX", "San Jose CA", "Austin TX", "Jacksonville FL"]
            origin = random.choice(cities)
            destination = random.choice([c for c in cities if c != origin])

            package_count = random.randint(1, 20)
            total_weight = round(random.uniform(50, 2000), 1)
            declared_value = round(random.uniform(500, 50000), 2)
            freight_cost = round(total_weight * random.uniform(0.5, 2.0), 2)

            status = random.choice(statuses)

            if status == "Delivered":
                delivery_date = ship_date + timedelta(days=random.randint(1, 7))
            else:
                delivery_date = None

            signature_required = random.choice(["Yes", "Yes", "No"])

            writer.writerow([
                manifest_id, ship_date.strftime("%Y-%m-%d"), carrier, tracking_number,
                ship_method, origin, destination, package_count, total_weight,
                declared_value, freight_cost, status,
                delivery_date.strftime("%Y-%m-%d") if delivery_date else "N/A",
                signature_required
            ])

    print(f"✓ Generated {num_records} shipping manifests in {output_file}")


def generate_markdown_content(output_file: Path, title: str, sections: int = 500):
    """Generate large markdown file with extensive content."""
    print(f"Generating {sections} sections for {output_file.name}...")

    with open(output_file, 'w') as f:
        f.write(f"# {title}\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(f"This document contains {sections} detailed entries for comprehensive testing.\n\n")
        f.write("---\n\n")

        for i in range(sections):
            f.write(f"## Entry {i + 1}: {title} - Item {i + 1:04d}\n\n")
            f.write(f"**Date:** {(datetime(2024, 1, 1) + timedelta(days=i % 365)).strftime('%Y-%m-%d')}\n\n")
            f.write(f"**Reference ID:** REF-{i + 1:06d}\n\n")

            # Random content
            sentiments = ["very positive", "positive", "neutral", "negative", "mixed"]
            priorities = ["Low", "Medium", "High", "Critical"]
            ratings = [1, 2, 3, 4, 5]

            f.write(f"**Rating:** {random.choice(ratings)}/5\n\n")
            f.write(f"**Priority:** {random.choice(priorities)}\n\n")
            f.write(f"**Sentiment:** {random.choice(sentiments)}\n\n")

            f.write("### Description\n\n")
            f.write(f"This is entry number {i + 1} in the {title} document. ")
            f.write(f"It contains important information about item {i + 1:04d} which requires ")
            f.write(f"careful attention and proper indexing. The entry was created on ")
            f.write(f"{(datetime(2024, 1, 1) + timedelta(days=i % 365)).strftime('%B %d, %Y')}. ")
            f.write("\n\n")

            f.write("### Key Points\n\n")
            for j in range(random.randint(3, 6)):
                f.write(f"- Point {j + 1}: Important detail about {title.lower()} entry {i + 1}\n")
            f.write("\n")

            f.write("### Metrics\n\n")
            f.write(f"- **Response Time:** {random.randint(1, 120)} minutes\n")
            f.write(f"- **Satisfaction Score:** {random.uniform(1, 5):.2f}/5.00\n")
            f.write(f"- **Follow-up Required:** {random.choice(['Yes', 'No'])}\n")
            f.write("\n---\n\n")

    print(f"✓ Generated {sections} sections in {output_file}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("HYBRID RAG - LARGE DATASET GENERATOR")
    print("=" * 70)
    print("\nThis script will generate thousands of records for boundary testing.\n")

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("CSV FILES - Generating structured data...\n")

    generate_product_catalog(data_dir / "product_catalog.csv", 5000)
    generate_inventory_levels(data_dir / "inventory_levels.csv", 10000)
    generate_sales_orders(data_dir / "sales_orders_november.csv", 8000)
    generate_warranty_claims(data_dir / "warranty_claims_q4.csv", 3000)
    generate_production_schedule(data_dir / "production_schedule_dec2024.csv", 4000)
    generate_supplier_pricing(data_dir / "supplier_pricing.csv", 6000)
    generate_shipping_manifests(data_dir / "shipping_manifests.csv", 5000)

    print("\nMARKDOWN FILES - Generating unstructured content...\n")

    generate_markdown_content(
        data_dir / "customer_feedback_q4_2024.md",
        "Customer Feedback Q4 2024",
        600
    )
    generate_markdown_content(
        data_dir / "market_analysis_2024.md",
        "Market Analysis 2024",
        400
    )
    generate_markdown_content(
        data_dir / "quality_control_report_nov2024.md",
        "Quality Control Report November 2024",
        500
    )
    generate_markdown_content(
        data_dir / "return_policy_procedures.md",
        "Return Policy and Procedures",
        300
    )
    generate_markdown_content(
        data_dir / "support_tickets_summary.md",
        "Support Tickets Summary",
        700
    )

    print("\nTEXT FILE - Generating detailed specifications...\n")

    spec_file = data_dir / "product_specifications.txt"
    with open(spec_file, 'w') as f:
        f.write("COMPREHENSIVE PRODUCT SPECIFICATIONS DATABASE\n")
        f.write("=" * 70 + "\n\n")
        for i in range(1000):
            f.write(f"\nPRODUCT SPECIFICATION #{i + 1:04d}\n")
            f.write("-" * 70 + "\n")
            f.write(f"Product ID: SPEC-{i + 1:06d}\n")
            f.write(f"Category: {random.choice(['Display', 'Audio', 'Accessory', 'Commercial'])}\n")
            f.write(f"Model Year: {random.choice([2023, 2024])}\n")
            f.write(f"Certification: {random.choice(['UL', 'CE', 'FCC', 'RoHS', 'Energy Star'])}\n")
            f.write(f"Specification Details: This product meets all regulatory requirements ")
            f.write(f"and has been tested for safety, performance, and environmental compliance.\n")

    print(f"✓ Generated 1000 specifications in {spec_file}")

    print("\n" + "=" * 70)
    print("DATASET GENERATION COMPLETE!")
    print("=" * 70)

    print("\nFinal Statistics:")
    print(f"  • Product Catalog: 5,000 products")
    print(f"  • Inventory Levels: 10,000 records")
    print(f"  • Sales Orders: 8,000 orders")
    print(f"  • Warranty Claims: 3,000 claims")
    print(f"  • Production Schedule: 4,000 entries")
    print(f"  • Supplier Pricing: 6,000 quotes")
    print(f"  • Shipping Manifests: 5,000 shipments")
    print(f"  • Customer Feedback: 600 entries")
    print(f"  • Market Analysis: 400 entries")
    print(f"  • Quality Control: 500 reports")
    print(f"  • Return Policies: 300 procedures")
    print(f"  • Support Tickets: 700 tickets")
    print(f"  • Product Specs: 1,000 specifications")
    print(f"\n  TOTAL: 41,000+ records across 13 files")
    print("\nYou can now run boundary tests with this large-scale dataset!")


if __name__ == "__main__":
    main()
