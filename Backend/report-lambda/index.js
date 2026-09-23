const { GetCommand } = require("@aws-sdk/lib-dynamodb");
const dynamoDB = require("./config/dynamodb");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const TABLE_NAME = "Assessments";
const S3_BUCKET = process.env.REPORT_BUCKET;

async function getAssessment(assessmentId) {
    const result = await dynamoDB.send(
        new GetCommand({
            TableName: TABLE_NAME,
            Key: { assessmentId }
        })
    );

    return result.Item;
}

exports.handler = async (event) => {
    try {
        console.log("GenerateReport event:", JSON.stringify(event));

        const assessmentId =
            event.pathParameters?.assessmentId ||
            event.assessmentId ||
            event.body?.assessmentId;

        if (!assessmentId) {
            return {
                statusCode: 400,
                body: JSON.stringify({
                    success: false,
                    message: "assessmentId is required"
                })
            };
        }

        const assessment = await getAssessment(assessmentId);

        if (!assessment) {
            return {
                statusCode: 404,
                body: JSON.stringify({
                    success: false,
                    message: "Assessment not found"
                })
            };
        }

        const scoringResult = {
            categoryScores: assessment.categoryScores,
            overallScore: assessment.overallScore,
            maturityLevel: assessment.maturityLevel,
            gaps: assessment.gaps
        };

        const recommendationResult = assessment.recommendation;

        if (!recommendationResult) {
            return {
                statusCode: 400,
                body: JSON.stringify({
                    success: false,
                    message: "Recommendation result not found for assessment"
                })
            };
        }

        const pythonScript = path.join(
            __dirname,
            "generate_report.py"
        );

        const input = JSON.stringify({
            assessment_id: assessment.assessmentId,
            business_name: assessment.businessName || "Rural MSME",
            business_type: assessment.business_type,
            scoring_result: scoringResult,
            recommendation_result: recommendationResult
        });

        const output = execFileSync(
            "python",
            [pythonScript, input],
            {
                encoding: "utf8"
            }
        );

        const reportResult = JSON.parse(output);

        return {
            statusCode: 200,
            body: JSON.stringify({
                success: true,
                assessmentId,
                filename: reportResult.filename,
                html: reportResult.html
            })
        };

    } catch (error) {
        console.error("Generate report error:", error);

        return {
            statusCode: 500,
            body: JSON.stringify({
                success: false,
                message: "Report generation failed",
                error: error.message
            })
        };
    }
};