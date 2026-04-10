"""Databases Table Creating"""

import dotenv
import os
from dotenv import load_dotenv
from pathlib import Path
import psycopg2



script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
env_path = root_dir / 'settings.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Successfully loaded settings from: {env_path}")
else:
    print(f"ERROR: Could not find settings.env at {env_path}")

# Step 1: Connect to default postgres database and drop/create invoice-db
conn = psycopg2.connect(database='postgres', user='postgres',
                        password=os.environ.get('PASSWORD'),
                        host=os.environ.get('HOST'),  port=os.environ.get('PORT'), sslmode='require')

conn.autocommit = True
cur = conn.cursor()

# Terminate all connections to the database first
cur.execute("""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = 'invoice-db'
    AND pid <> pg_backend_pid();
""")

# Drop database if exists
cur.execute('DROP DATABASE IF EXISTS "invoice-db";')
print("Dropped old database (if existed)")

# Create fresh database
cur.execute('CREATE DATABASE "invoice-db";')
print("Created new database 'invoice-db'")

cur.close()
conn.close()

# Step 2: Connect to invoice-db and create tables
conn = psycopg2.connect(database="invoice-db", user='postgres',
                        password=os.environ.get('PASSWORD'),
                        host=os.environ.get('HOST'),  port=os.environ.get('PORT'), sslmode='require')


cur = conn.cursor()

# Create invoices table
cur.execute("""
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    invoice_date DATE,
    due_date DATE,
    vendor_name VARCHAR(255),
    vendor_address TEXT,
    customer_name VARCHAR(255),
    customer_address TEXT,
    subtotal DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    shipping DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    bank_name VARCHAR(255),
    iban VARCHAR(100),
    swift_code VARCHAR(50),
    s3_json_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
print("Created 'invoices' table")

# Create invoice_items table
cur.execute("""
CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
    item_id VARCHAR(50),
    description TEXT,
    quantity DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    total DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
print("Created 'invoice_items' table")
conn.commit()

# Step 3: Verify tables
print("Step 3: Verifying tables...")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

tables = cur.fetchall()
print("  Tables in database:")
for table in tables:
    print(f" - {table[0]}")

cur.close()
conn.close()

print("ALL DONE! Fresh database and tables created.")
