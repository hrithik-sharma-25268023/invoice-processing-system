"""Dynamo DB Utils"""

import boto3
from datetime import datetime
import uuid
from decimal import Decimal
from typing import Any

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("invoice_logs")


def convert_floats_to_decimal(obj: Any) -> Any:
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    else:
        return obj


def save_metadata_to_dynamodb(pdf_filename, bucket_name, s3_key_pdf, s3_key_image,
                              s3_key_text, s3_json_key, pdf_bytes, img_bytes, json_data):

    metadata = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),

        "pdf_file_name": pdf_filename,
        "bucket_name": bucket_name,

        "s3_pdf_path": s3_key_pdf,
        "s3_image_path": s3_key_image,
        "s3_text_path": s3_key_text,
        "s3_json_path": s3_json_key,

        "pdf_size_kb": round(len(pdf_bytes) / 1024, 2),
        "image_size_kb": round(len(img_bytes) / 1024, 2),

        "invoice_number": json_data.get("invoice_number"),
        "invoice_date": str(json_data.get("invoice_date")),

        "vendor_name": json_data.get("vendor", {}).get("name"),
        "customer_name": json_data.get("customer", {}).get("name"),

        "total_amount": json_data.get("total_amount"),
        "num_items": len(json_data.get("items", [])),

        "processing_status": "completed",
        "ocr_status": "success",
        "llm_status": "success",

        "source": "streamlit_app",
        "file_type": "pdf"
    }

    metadata = convert_floats_to_decimal(metadata)

    table.put_item(Item=metadata)

    return metadata