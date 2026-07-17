import os
import csv
import json
import random
import logging
from datetime import datetime, timedelta
import requests
from faker import Faker

# Configure base directory relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure local logging for generator script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

def fetch_api_data():
    """Fetch external API data using Requests library with offline fallback."""
    url = "https://jsonplaceholder.typicode.com/users"
    logger.info(f"Attempting to fetch API data from {url}...")
    dest_path = os.path.join(DATASETS_DIR, "api_users.json")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        with open(dest_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully fetched API data and saved to {dest_path}")
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch API data (network error or offline): {e}")
        logger.info("Generating mock API data locally as fallback...")
        fallback_data = []
        for i in range(1, 11):
            fallback_data.append({
                "id": i,
                "name": fake.name(),
                "username": fake.user_name(),
                "email": fake.email(),
                "address": {
                    "street": fake.street_name(),
                    "suite": fake.secondary_address(),
                    "city": fake.city(),
                    "zipcode": fake.zipcode()
                },
                "phone": fake.phone_number(),
                "website": fake.domain_name()
            })
        with open(dest_path, "w") as f:
            json.dump(fallback_data, f, indent=2)
        logger.info(f"Saved fallback API data to {dest_path}")

def generate_customers(num_records=100):
    """Generate customer profiles CSV with intentional dirtiness for validation testing."""
    logger.info("Generating synthetic customer dataset...")
    
    # 1. Generate clean list of customers
    customers = []
    for i in range(1, num_records + 1):
        customers.append({
            "customer_id": f"CUST{i:04d}",
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "city": fake.city()
        })
    
    # 2. Inject anomalies
    
    # 5 Duplicate customer IDs
    for i in range(5):
        dup_index = random.randint(0, len(customers) - 1)
        target_index = random.randint(0, len(customers) - 1)
        customers[target_index]["customer_id"] = customers[dup_index]["customer_id"]
        logger.info(f"Injected duplicate customer_id: {customers[dup_index]['customer_id']}")
        
    # 5 Missing (null) values in name, email, or phone
    for _ in range(5):
        target_index = random.randint(0, len(customers) - 1)
        field = random.choice(["name", "email", "phone"])
        customers[target_index][field] = ""
        logger.info(f"Injected null/empty value at index {target_index} for field: {field}")
        
    # 5 Malformed emails
    malformed_examples = ["testemail.com", "john.doe@", "alex @domain.com", "user@domain..com", "invalid-email-format"]
    for i in range(5):
        target_index = random.randint(0, len(customers) - 1)
        customers[target_index]["email"] = malformed_examples[i]
        logger.info(f"Injected malformed email at index {target_index}: {malformed_examples[i]}")
        
    # Write to CSV
    csv_file = os.path.join(DATASETS_DIR, "customers.csv")
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id", "name", "email", "phone", "city"])
        writer.writeheader()
        writer.writerows(customers)
    
    logger.info(f"Saved synthetic customer data to {csv_file}")
    return customers

def generate_transactions(customers, num_records=150):
    """Generate transactional JSON logs with nested items and intentional anomalies."""
    logger.info("Generating synthetic transactional dataset...")
    
    transactions = []
    start_date = datetime.now() - timedelta(days=30)
    customer_ids = [c["customer_id"] for c in customers if c["customer_id"]]
    
    for i in range(1, num_records + 1):
        # Generate nested item list
        items = []
        num_items = random.randint(1, 4)
        total_amount = 0.0
        for _ in range(num_items):
            price = round(random.uniform(5.0, 150.0), 2)
            qty = random.randint(1, 3)
            items.append({
                "item_name": fake.word().capitalize(),
                "qty": qty,
                "price": price
            })
            total_amount += price * qty
            
        trans_date = start_date + timedelta(
            seconds=random.randint(0, int((datetime.now() - start_date).total_seconds()))
        )
        
        transactions.append({
            "transaction_id": f"TXN{i:05d}",
            "customer_id": random.choice(customer_ids) if customer_ids else "CUST0001",
            "amount": round(total_amount, 2),
            "date": trans_date.strftime("%Y-%m-%d %H:%M:%S"),
            "items": items
        })
        
    # Inject anomalies
    
    # 5 Transaction logs missing transaction_id or customer_id
    for _ in range(5):
        target_index = random.randint(0, len(transactions) - 1)
        field = random.choice(["transaction_id", "customer_id"])
        transactions[target_index][field] = ""
        logger.info(f"Injected null key value in transaction at index {target_index} for field: {field}")
        
    # 5 Records with negative or non-numeric amount
    for i in range(5):
        target_index = random.randint(0, len(transactions) - 1)
        if i % 2 == 0:
            transactions[target_index]["amount"] = -100.50
        else:
            transactions[target_index]["amount"] = "INVALID_NUMERIC"
        logger.info(f"Injected malformed amount in transaction at index {target_index}: {transactions[target_index]['amount']}")
        
    # Write to JSON
    json_file = os.path.join(DATASETS_DIR, "transactions.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2)
        
    logger.info(f"Saved synthetic transaction data to {json_file}")

def generate_config():
    """Generate a mock configuration file."""
    config_content = """# Data Engineering Ingestion Configurations
ingest_batch_size = 100
quarantine_enabled = true
sqlite_db_name = ecommerce.db
validation_level = STRICT
api_timeout_sec = 5
max_retry_attempts = 3
"""
    dest_path = os.path.join(DATASETS_DIR, "config.txt")
    with open(dest_path, "w") as f:
        f.write(config_content)
    logger.info(f"Saved unstructured configuration to {dest_path}")

if __name__ == "__main__":
    logger.info("=== Starting Data Generation Engine ===")
    fetch_api_data()
    customer_list = generate_customers()
    generate_transactions(customer_list)
    generate_config()
    logger.info("=== Data Generation Completed Successfully ===")
