import json
import re

REGION = "ap-south-1"
# NOTE: confirm this model ID is enabled for your account in this region. Some
# regions require a cross-region inference-profile ID (e.g. "apac.amazon.nova-micro-v1:0").
MODEL_ID = "amazon.nova-micro-v1:0"

_client = None


def _get_client():
    """Create the Bedrock client lazily so importing this module never needs AWS."""
    global _client
    if _client is None:
        import boto3
        from botocore.config import Config

        _client = boto3.client(
            "bedrock-runtime",
            region_name=REGION,
            config=Config(
                connect_timeout=3,
                read_timeout=15,
                retries={"max_attempts": 2, "mode": "standard"},
            ),
        )
    return _client


def extract_json(text):
    """Pull the first JSON object out of a model reply, ignoring fences and chatter."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object found in model response")
    return json.loads(text[start : end + 1])


def call_bedrock(prompt):
    """
    Sends the prompt to Amazon Nova Micro via the Bedrock Converse API and
    returns the parsed JSON (a dict with "summary" and "priorities").
    Raises on any failure - the caller falls back to rules-based advice.
    """
    response = _get_client().converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={
            "maxTokens": 500,  # a little more room for Tamil/Hindi, which use more tokens
            "temperature": 0.3,
        },
    )
    text = response["output"]["message"]["content"][0]["text"]
    return extract_json(text)
