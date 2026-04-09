"""OCR Code"""

from typing import Any
import boto3
import pytesseract
from PIL import Image
from io import BytesIO
import gc

def run_ocr(file_system: Any, bucket: str, image_key: str, text_key: str) -> None:
    """OCR method for extracting data from Images"""

    try:
        print(f"Opening: {image_key}")
        resp = file_system.read_png(Bucket=bucket, Key=image_key)

        img = Image.open(BytesIO(resp['Body'].read()))

        # Tesseract OCR
        extracted_text = pytesseract.image_to_string(img)
        relative_path = image_key.replace('interim/', '')
        filename_txt = relative_path.replace('.png', '.txt')
        text_key = f"app/output/ocr-output/{filename_txt}"
        
        # Saving result
        file_system.write_text(bucket, text_key, extracted_text)

        # Cleanup
        del img
        gc.collect()
    except Exception as e:
        print(f"Error: {e}")

    return extracted_text
