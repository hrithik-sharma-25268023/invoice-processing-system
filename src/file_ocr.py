"""OCR Code"""

from typing import Any
import pytesseract
from PIL import Image
from io import BytesIO
import gc

def run_ocr(file_system: Any, bucket: str, image_key: str, text_key: str) -> str:
    """OCR method for extracting data from Images"""
    extracted_text = "" 

    try:
        print(f"Opening: {image_key}")
        image_bytes = file_system.read_png(bucket=bucket, key=image_key)
        img = Image.open(BytesIO(image_bytes))

        # Tesseract OCR
        extracted_text = pytesseract.image_to_string(img)

        # Saving results
        file_system.write_text(bucket, text_key, extracted_text)

        # Cleanup
        del img
        gc.collect()
        
    except Exception as e:
        error_msg = f"OCR Error: {str(e)}"
        print(error_msg)
        return error_msg

    return extracted_text
