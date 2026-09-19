import json
import boto3

REGION = "ap-south-1"
MODEL_ID = "amazon.nova-micro-v1:0"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def call_bedrock(prompt):
    """
    Sends the prompt to Amazon Nova Micro via the Bedrock Converse API and
    returns the parsed JSON response (a dict with "summary" and "priorities").

    The Converse API is used instead of invoke_model because it gives a
    consistent request/response shape across model families (Nova, Claude,
    etc.) - if you ever switch models later, this function barely changes.

    Raises an exception if the call fails or the response isn't valid JSON -
    the caller (generate_recommendation) is expected to catch this and fall
    back to the rules-based recommendations.
    """
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 400,
            "temperature": 0.3,  # low temperature - we want consistent, factual output, not creative
        },
    )

    # Converse API response shape (same across model families):
    # response["output"]["message"]["content"] is a list of content blocks
    text = response["output"]["message"]["content"][0]["text"]

    # Strip markdown code fences in case the model wraps its JSON in them
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    return json.loads(text)
