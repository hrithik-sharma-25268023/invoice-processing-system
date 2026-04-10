"""Streamlit UI"""

import streamlit as st
from pdf2image import convert_from_bytes
import sys
import os
from io import BytesIO
import boto3

from src.storage import FileSystem
from src.file_ocr import run_ocr
from src.llm_utils import extract_invoice_with_llm
from src.utilities import insert_invoice_into_db


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


# Constants
S3_CLIENT = boto3.client('s3')
FILE_SYSTEM = FileSystem(s3_client=S3_CLIENT)
BUCKET_NAME = 'document-processing-project'


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
    
    # S3 paths
    s3_key_pdf = f"app/input/{pdf_filename}"
    s3_key_image = f"app/interim/images/{base_name}.png"
    s3_key_text = f"app/interim/text/{base_name}.txt"
    s3_json_key = f"app/output/{base_name}.json"
    
    # Read PDF bytes
    pdf_bytes = uploaded_file.read()
    
    # Upload PDF to S3
    with st.spinner("Uploading PDF to S3..."):
        FILE_SYSTEM.write_pdf(
            bucket=BUCKET_NAME, 
            key=s3_key_pdf, 
            pdf_bytes=pdf_bytes
        )
    
    # Convert PDF to image (single page)
    with st.spinner("Converting PDF to PNG..."):
        images = convert_from_bytes(pdf_bytes)
        img = images[0]
        
        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
    
    # Upload PNG to S3
    with st.spinner("Uploading PNG to S3..."):
        FILE_SYSTEM.write_png(
            bucket=BUCKET_NAME,
            key=s3_key_image,
            image_bytes=img_bytes
        )
    
    st.success("PDF and PNG uploaded to S3 successfully!")
    
    # LEFT: PDF Preview
    with col1:
        st.subheader("📄 Invoice Preview")
        st.image(img, use_column_width=True)

    # RIGHT: Storage Info & Operations
    with col2:
        st.subheader("📄 JSON Preview")
        text = run_ocr(FILE_SYSTEM, BUCKET_NAME, s3_key_image, s3_key_text)
        json_data = extract_invoice_with_llm(text)
        st.json(json_data)

        with st.spinner("Uploading JSON to S3..."):
            FILE_SYSTEM.write_json(bucket=BUCKET_NAME, key=s3_json_key, data=json_data)
    st.success("JSON uploaded to S3 successfully!")

    # Saving JSON to Database into RDS (Relational Database Table)
    with st.spinner("Saving to database..."):
        insert_invoice_into_db(json_data=json_data, s3_uri=f"s3://{BUCKET_NAME}/"+s3_json_key)
        st.success("Data saved to RDS successfully!")

        # st.subheader("💾 Storage Information")
        
        # # Upload details
        # with st.container():
        #     st.markdown("**Files Uploaded:**")
        #     st.code(f"PDF: {s3_key_pdf}", language=None)
        #     st.code(f"PNG: {s3_key_image}", language=None)
        
        # st.divider()
        
        # # File details
        # with st.container():
        #     st.markdown("**File Details:**")
        #     col_a, col_b = st.columns(2)
        #     with col_a:
        #         st.metric("PDF Size", f"{len(pdf_bytes) / 1024:.2f} KB")
        #     with col_b:
        #         st.metric("PNG Size", f"{len(img_bytes) / 1024:.2f} KB")
            
        #     st.text(f"Filename: {pdf_filename}")
        #     st.text(f"Bucket: {BUCKET_NAME}")
        #     st.text(f"Upload Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # st.divider()
        
        # # Storage Operations
        # st.subheader("🔧 Storage Operations")
        
        # col_btn1, col_btn2 = st.columns(2)
        
        # with col_btn1:
        #     if st.button("📥 Read PDF", use_container_width=True):
        #         with st.spinner("Reading PDF from S3..."):
        #             try:
        #                 read_pdf_bytes = FILE_SYSTEM.read_pdf(
        #                     bucket=BUCKET_NAME, 
        #                     key=s3_key_pdf
        #                 )
        #                 st.success(f"✅ Read {len(read_pdf_bytes) / 1024:.2f} KB")
        #             except Exception as e:
        #                 st.error(f"❌ Error: {str(e)}")
        
        # with col_btn2:
        #     if st.button("Read PNG", use_container_width=True):
        #         with st.spinner("Reading PNG from S3..."):
        #             try:
        #                 read_img_bytes = FILE_SYSTEM.read_png(
        #                     bucket=BUCKET_NAME, 
        #                     key=s3_key_image
        #                 )
        #                 st.success(f"Read {len(read_img_bytes) / 1024:.2f} KB")
        #             except Exception as e:
        #                 st.error(f"Error: {str(e)}")
        
        # # Save metadata
        # if st.button("Save Metadata JSON", use_container_width=True):
        #     with st.spinner("Saving metadata to S3..."):
        #         try:
        #             metadata = {
        #                 "invoice_id": base_name,
        #                 "filename": pdf_filename,
        #                 "upload_timestamp": datetime.now().isoformat(),
        #                 "pdf_path": s3_key_pdf,
        #                 "image_path": s3_key_image,
        #                 "pdf_size_kb": round(len(pdf_bytes) / 1024, 2),
        #                 "png_size_kb": round(len(img_bytes) / 1024, 2),
        #                 "status": "uploaded"
        #             }
                    
        #             json_key = f"app/interim/json/{base_name}_metadata.json"
        #             FILE_SYSTEM.write_json(
        #                 bucket=BUCKET_NAME, 
        #                 key=json_key, 
        #                 data=metadata
        #             )
                    
        #             st.success(f"Metadata saved to: `{json_key}`")
        #             st.json(metadata)
                    
        #         except Exception as e:
        #             st.error(f"Error: {str(e)}")
