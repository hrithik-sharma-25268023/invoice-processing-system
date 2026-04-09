"""Streamlit UI"""

import warnings
import streamlit as st
import json
import tempfile
from pdf2image import convert_from_bytes
import sys
import os

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
    s3_input_key = f"app/input/{uploaded_file.name}"
    
    # Upload PDF to S3
    pdf_bytes = uploaded_file.read()
    FILE_SYSTEM.write_pdf(bucket='document-processing-project', key=s3_input_key, pdf_bytes=pdf_bytes)
    
    st.success(f"PDF uploaded to S3: {s3_input_key}")
    
    # LEFT: PDF Preview
    with col1:
        st.subheader("Invoice Preview")

        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)

        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1}", use_column_width=True)

    # RIGHT: JSON Output
    with col2:
        st.subheader("Extracted JSON")

        if st.button("Process Invoice"):

            data = {
                "status": "processed",
                "message": "OCR Logic",
                "s3_location": {
                    "bucket": "document-processing-project",
                    "key": s3_input_key
                },
                "filename": uploaded_file.name
            }

            st.json(data)

            st.success("Invoice processed successfully!")
