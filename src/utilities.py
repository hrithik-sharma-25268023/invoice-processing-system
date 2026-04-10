"""app utilities"""

import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
import pandas as pd


script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
env_path = root_dir / 'settings.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Successfully loaded settings from: {env_path}")
else:
    print(f"ERROR: Could not find settings.env at {env_path}")

DB_CONFIG = {
    "host": os.environ.get('HOST'),
    "database": "invoice-db",
    "user": "postgres",
    "password": os.environ.get('PASSWORD'),
    "port": os.environ.get('PORT'),
    "sslmode": "require"
}


def clean_amount(value: Any) -> Any:
    """convert currency strings to float"""

    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").replace("€", "").strip())
    except:
        return None


def clean_date(value: Any) -> Any:
    """cleans date"""

    if not value or str(value).strip() == "":
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        return None


def insert_invoice_into_db(json_data: Dict, s3_uri: str) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO invoices (
            invoice_number,
            invoice_date,
            due_date,
            vendor_name,
            vendor_address,
            customer_name,
            customer_address,
            subtotal,
            tax,
            shipping,
            total_amount,
            bank_name,
            iban,
            swift_code,
            s3_json_path
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (invoice_number) DO UPDATE SET
            total_amount = EXCLUDED.total_amount
        RETURNING id
        """, (
            json_data.get("invoice_number"),
            clean_date(json_data.get("invoice_date")),
            clean_date(json_data.get("due_date")),
            json_data.get("vendor", {}).get("name"),
            json_data.get("vendor", {}).get("address"),
            json_data.get("customer", {}).get("name"),
            json_data.get("customer", {}).get("address"),
            clean_amount(json_data.get("subtotal")),
            clean_amount(json_data.get("tax")),
            clean_amount(json_data.get("shipping")),
            clean_amount(json_data.get("total_amount")),
            json_data.get("payment_details", {}).get("bank_name"),
            json_data.get("payment_details", {}).get("iban"),
            json_data.get("payment_details", {}).get("swift_code"),
            s3_uri
        ))

        result = cur.fetchone()

        if result:
            invoice_id = result[0]
        else:
            cur.execute(
                "SELECT id FROM invoices WHERE invoice_number = %s",
                (json_data.get("invoice_number"),)
            )
            invoice_id = cur.fetchone()[0]

        cur.execute("DELETE FROM invoice_items WHERE invoice_id = %s", (invoice_id,))

        for item in json_data.get("items", []):
            cur.execute("""
            INSERT INTO invoice_items (
                invoice_id,
                item_id,
                description,
                quantity,
                unit_price,
                total,
                s3_json_path
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                invoice_id,
                item.get("id"),
                item.get("description"),
                clean_amount(item.get("quantity")),
                clean_amount(item.get("unit_price")),
                clean_amount(item.get("total")),
                s3_uri
            ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()


def fetch_tables_from_db() -> tuple:

    conn = psycopg2.connect(
        host=os.environ.get('HOST'),
        database="invoice-db",
        user="postgres",
        password=os.environ.get('PASSWORD'),
        port=os.environ.get('PORT'),
        sslmode="require"
    )

    try:
        invoices_df = pd.read_sql(
            "SELECT * FROM invoices ORDER BY created_at DESC",
            conn
        )

        items_df = pd.read_sql(
            "SELECT * FROM invoice_items ORDER BY created_at DESC",
            conn
        )

        return invoices_df, items_df

    finally:
        conn.close()
