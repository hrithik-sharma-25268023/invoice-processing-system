"""Read and write files to S3"""

import boto3
import json
from typing import Any, Dict


class FileSystem:

    
    def __init__(self, s3_client: boto3.client) -> None:
        self.s3_client = s3_client


    def read_json(self, bucket: str, key: str) -> Dict[str, Any]:
        """Read JSON file from S3 and return as dictionary"""

        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)


    def write_json(self, bucket: str, key: str, data: Dict[str, Any]) -> None:
        """Write dictionary to S3 as JSON file"""

        json_content = json.dumps(data, indent=2)
        self.s3_client.put_object(Bucket=bucket, Key=key, Body=json_content.encode('utf-8'), ContentType='application/json')


    def read_text(self, bucket: str, key: str) -> str:
        """Read text file from S3 and return as string"""

        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')


    def write_text(self, bucket: str, key: str, text: str) -> None:
        """Write string to S3 as text file"""

        self.s3_client.put_object(Bucket=bucket, Key=key, Body=text.encode('utf-8'), ContentType='text/plain')


    def read_png(self, bucket: str, key: str) -> bytes:
        """Read PNG file from S3 and return as bytes"""

        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()


    def write_png(self, bucket: str, key: str, image_bytes: bytes) -> None:
        """Write bytes to S3 as PNG file"""

        self.s3_client.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType='image/png')


    def read_pdf(self, bucket: str, key: str) -> bytes:
        """Read PDF file from S3 and return as bytes"""

        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()


    def write_pdf(self, bucket: str, key: str, pdf_bytes: bytes) -> None:
        """Write bytes to S3 as PDF file"""

        self.s3_client.put_object(Bucket=bucket,Key=key, Body=pdf_bytes, ContentType='application/pdf')
