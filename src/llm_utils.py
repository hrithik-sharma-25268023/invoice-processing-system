"""LLM Utils"""

import os
import re
import json
import boto3

from src.storage import FileSystem

S3_CLIENT = boto3.client('s3')
BEDROCK_CLIENT = boto3.client("bedrock-runtime", 'eu-west-1')
FILE_SYSTEM = FileSystem(s3_client=S3_CLIENT)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, '..', 'utils', 'prompt.txt')

with open(PROMPT_PATH, 'r') as file:
    INVOICE_PROMPT = file.read()


def extract_invoice_with_llm(text):
    """Extract JSON"""

    prompt = INVOICE_PROMPT.replace("{invoice_text}", text)
    body = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 2000,
                       "temperature": 0, "messages": [{"role": "user", "content": prompt}]})

    response = BEDROCK_CLIENT.invoke_model(modelId="anthropic.claude-3-haiku-20240307-v1:0", body=body,
                                           contentType="application/json", accept="application/json")

    result = json.loads(response["body"].read())
    output_text = result["content"][0]["text"]
    json_str = output_text.strip()

    if json_str.startswith("```"):
        # Remove opening ```json or ```
        json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
        # Remove closing ```
        json_str = re.sub(r'\s*```$', '', json_str)
        json_str = json_str.strip()

    # If there's still non-JSON text
    if not json_str.startswith('{'):
        match = re.search(r'\{[\s\S]*\}', json_str)
        if match:
            json_str = match.group()
        else:
            return None
    try:
        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError as e:
        # Show context around error
        start = max(0, e.pos - 100)
        end = min(len(json_str), e.pos + 100)

        # Try to fix common issues
        try:
            # Remove trailing commas before closing brackets
            fixed = re.sub(r',(\s*[}\]])', r'\1', json_str)
            # Remove any control characters
            fixed = re.sub(r'[\x00-\x1f\x7f]', '', fixed)
            parsed_json = json.loads(fixed)
            return parsed_json
        except:
            return None
