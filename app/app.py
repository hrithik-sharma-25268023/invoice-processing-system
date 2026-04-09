"""Streamlit UI"""

import warnings
import streamlit as st
import json
import tempfile
from pdf2image import convert_from_bytes

warnings.filterwarnings("ignore")


st.set_page_config(layout="wide")

st.title("📄 Invoice Processing System")

# Upload PDF
uploaded_file = st.file_uploader("Upload Invoice PDF", type=["pdf"])

if uploaded_file is not None:

    # Two columns
    col1, col2 = st.columns(2)


    # LEFT: PDF Preview
    with col1:
        st.subheader("Invoice Preview")

        # Convert PDF to images
        images = convert_from_bytes(uploaded_file.read())

        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1}", use_column_width=True)

    # RIGHT: JSON Output
    with col2:
        st.subheader("Extracted JSON")

        if st.button("Process Invoice"):

            data = {
                "status": "processed",
                "message": "OCR Logic"
            }

            st.json(data)

            st.success("Invoice processed successfully!")