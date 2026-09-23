const { v4: uuidv4 } = require("uuid");
const { runFullAssessment } = require("../src/services/scoringService");
const { createAssessment } = require("../src/services/assessmentService");
const { generateRecommendation } = require("../src/services/recommendationService");

exports.handler = async (event) => {
    try {
        console.log("Lambda received event:", JSON.stringify(event));

        const body =
            typeof event.body === "string"
                ? JSON.parse(event.body)
                : event.body || event;

        const { responses, business_type } = body;

        if (!responses || typeof responses !== "object") {
            return {
                statusCode: 400,
                body: JSON.stringify({
                    success: false,
                    message: "responses object is required"
                })
            };
        }

        if (!business_type) {
            return {
                statusCode: 400,
                body: JSON.stringify({
                    success: false,
                    message: "business_type is required"
                })
            };
        }

        const scoringResult = runFullAssessment(responses);

        const recommendationResult = await generateRecommendation(
            business_type,
            scoringResult.categoryScores,
            scoringResult.overallScore,
            scoringResult.maturityLevel,
            scoringResult.gaps
        );

        const assessment = {
            assessmentId: uuidv4(),

            responses,

            business_type,

            categoryScores: scoringResult.categoryScores,

            overallScore: scoringResult.overallScore,

            maturityLevel: scoringResult.maturityLevel,

            gaps: scoringResult.gaps,

            recommendation: recommendationResult,

            createdAt: new Date().toISOString()
        };

        const savedAssessment = await createAssessment(assessment);

        return {
            statusCode: 201,
            body: JSON.stringify({
                success: true,
                message: "Assessment submitted successfully",
                data: savedAssessment
            })
        };

    } catch (error) {

        console.error("Assessment Lambda error:", error);

        return {
            statusCode: 500,
            body: JSON.stringify({
                success: false,
                message: "Assessment submission failed",
                error: error.message
            })
        };
    }
};