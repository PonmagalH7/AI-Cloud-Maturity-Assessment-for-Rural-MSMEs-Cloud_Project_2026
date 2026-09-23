import json
import os
import boto3

from boto3.dynamodb.conditions import Key

from generate_report import generate_report


TABLE_NAME = "Assessments"
REPORT_BUCKET = os.environ["REPORT_BUCKET"]

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table(TABLE_NAME)

s3 = boto3.client("s3", region_name="ap-south-1")


def handler(event, context):
    try:
        print("GenerateReport event:", json.dumps(event))

        # Support API Gateway path parameter
        assessment_id = (
            event.get("pathParameters", {}).get("assessmentId")
            if event.get("pathParameters")
            else None
        )

        # Also support direct Lambda testing
        if not assessment_id:
            assessment_id = event.get("assessmentId")

        if not assessment_id and event.get("body"):
            body = event["body"]

            if isinstance(body, str):
                body = json.loads(body)

            assessment_id = body.get("assessmentId")

        if not assessment_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "assessmentId is required"
                })
            }

        # Get assessment from DynamoDB
        result = table.get_item(
            Key={
                "assessmentId": assessment_id
            }
        )

        assessment = result.get("Item")

        if not assessment:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "success": False,
                    "message": "Assessment not found"
                })
            }

        # Build scoring result expected by generate_report()
        scoring_result = {
            "categoryScores": assessment.get(
                "categoryScores", {}
            ),
            "overallScore": assessment.get(
                "overallScore", 0
            ),
            "maturityLevel": assessment.get(
                "maturityLevel", ""
            ),
            "gaps": assessment.get(
                "gaps", []
            )
        }

        recommendation_result = assessment.get(
            "recommendation"
        )

        if not recommendation_result:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "Recommendation result not found"
                })
            }

        business_name = assessment.get(
            "businessName",
            "Rural MSME"
        )

        business_type = assessment.get(
            "business_type",
            "Micro"
        )

        # Generate HTML using Person 1's existing code
        report_result = generate_report(
            assessment_id=assessment_id,
            business_name=business_name,
            business_type=business_type,
            scoring_result=scoring_result,
            recommendation_result=recommendation_result
        )

        html = report_result["html"]
        filename = report_result["filename"]

        # Upload HTML report to S3
        s3.put_object(
            Bucket=REPORT_BUCKET,
            Key=filename,
            Body=html.encode("utf-8"),
            ContentType="text/html"
        )

        report_url = (
            f"https://{REPORT_BUCKET}.s3.ap-south-1.amazonaws.com/"
            f"{filename}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "assessmentId": assessment_id,
                "filename": filename,
                "reportUrl": report_url
            })
        }

    except Exception as error:
        print("Generate report error:", str(error))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": "Report generation failed",
                "error": str(error)
            })
        }