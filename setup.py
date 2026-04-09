"""setup file"""

from setuptools import setup, find_packages

setup(
    name="invoice-processing-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "boto3",
        "pdf2image",
    ],
)