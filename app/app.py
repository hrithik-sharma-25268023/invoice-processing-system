"""Streamlit UI"""

import warnings
import streamlit as st
import json
from pdf2image import convert_from_bytes
import sys
import os
from io import BytesIO

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.storage import FileSystem
import boto3
warnings.filterwarnings("ignore")

S3_CLIENT = boto3.client('s3')
FILE_SYSTEM = FileSystem(s3_client=S3_CLIENT)

st.set_page_config(layout="wide")

st.title("📄 Invoice Processing System")

# Upload PDF
uploaded_file = st.file_uploader("Upload Invoice PDF", type=["pdf"])

if uploaded_file is not None:

    # Two columns
    col1, col2 = st.columns(2)

    # Use the original filename for S3 key
    pdf_filename = uploaded_file.name
    base_name = os.path.splitext(pdf_filename)[0]
    
    s3_key_pdf = f"app/input/{pdf_filename}"
    
    # Upload PDF to S3
    pdf_bytes = uploaded_file.read()
    FILE_SYSTEM.write_pdf(bucket='document-processing-project', key=s3_key_pdf, pdf_bytes=pdf_bytes)
    
    # Convert PDF to image (single page)
    images = convert_from_bytes(pdf_bytes)
    img = images[0]  # Only first page
    
    # Convert PIL Image to bytes
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    # Save PNG to S3 interim folder
    image_filename = f"{base_name}.png"
    s3_key_image = f"app/interim/images/{image_filename}"
    
    FILE_SYSTEM.write_png(
        bucket='document-processing-project',
        key=s3_key_image,
        image_bytes=img_bytes
    )
    
    st.success(f"PDF and PNG uploaded to S3 successfully!")
    
    # LEFT: PDF Preview
    with col1:
        st.subheader("Invoice Preview")
        st.image(img, use_column_width=True)

    # RIGHT: Storage Info
    with col2:
        st.subheader("Storage Information")
        
        st.info("**Files uploaded to S3:**")
        st.write(f"**PDF:** `{s3_key_pdf}`")
        st.write(f"**PNG:** `{s3_key_image}`")
        
        st.divider()
        
        st.info("**File Details:**")
        st.write(f"**Filename:** {pdf_filename}")
        st.write(f"**Size:** {len(pdf_bytes) / 1024:.2f} KB")
        st.write(f"**Bucket:** document-processing-project")
