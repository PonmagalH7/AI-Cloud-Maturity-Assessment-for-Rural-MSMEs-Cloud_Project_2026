const { validationResult } = require("express-validator");
const { assessmentValidation } = require("../utils/validation");
const express = require("express");
const { v4: uuidv4 } = require("uuid");
const authMiddleware = require("../middleware/authMiddleware");
const { runFullAssessment } =
    require("../services/scoringService");

const { generateRecommendation } =
    require("../services/recommendationService");
const {
    createAssessment,
    getAllAssessments,
    getAssessmentById,
    updateAssessment,
    deleteAssessment
} = require("../services/assessmentService");

const router = express.Router();

router.use(authMiddleware);

// ===============================
// GET ALL ASSESSMENTS
// ===============================

router.get("/", async (req, res, next) => {

    try {

        const assessments = await getAllAssessments();

        res.status(200).json({
            success: true,
            count: assessments.length,
            data: assessments
        });

    } catch (error) {

        next(error);

    }

});


// ===============================
// CREATE ASSESSMENT
// ===============================


router.post("/", async (req, res, next) => {
  try {
    const {
      responses,
      business_type,
      businessName = "",
      location = "",
      industry = "",
      cloudUsage = "",
    } = req.body || {};

    const businessTypes = ["Micro", "Small", "Medium"];

    if (!businessTypes.includes(business_type)) {
      return res.status(400).json({
        success: false,
        message: "business_type must be Micro, Small, or Medium",
      });
    }

    const categories = [
      "infra",
      "process",
      "people",
      "data",
      "security",
    ];

    const requiredIds = categories.flatMap((category) =>
      Array.from(
        { length: 5 },
        (_, index) => `${category}_${index + 1}`
      )
    );

    if (!responses || typeof responses !== "object" ||
        Array.isArray(responses)) {
      return res.status(400).json({
        success: false,
        message: "A responses object is required",
      });
    }

    const missing = requiredIds.filter(
      (id) => !Object.prototype.hasOwnProperty.call(responses, id)
    );

    const invalid = requiredIds.filter(
      (id) =>
        !Number.isInteger(responses[id]) ||
        responses[id] < 0 ||
        responses[id] > 4
    );

    if (missing.length || invalid.length) {
      return res.status(400).json({
        success: false,
        message: "Submit all 25 answers as integers from 0 to 4",
        missing,
        invalid,
      });
    }

    // Calculate category scores, overall score, maturity level and gaps.
    const scores = runFullAssessment(responses);

    // Generate three practical recommendations.
    const recommendation = await generateRecommendation(
      business_type,
      scores.categoryScores,
      scores.overallScore,
      scores.maturityLevel,
      scores.gaps
    );

    const assessment = {
      assessmentId: require("crypto").randomUUID(),
      businessName,
      location,
      industry,
      cloudUsage,
      businessType: business_type,
      business_type,
      responses,
      ...scores,
      recommendation,
      createdAt: new Date().toISOString(),
    };

    // Persist the completed assessment in DynamoDB.
    await createAssessment(assessment);

    return res.status(201).json({
      success: true,
      message: "Assessment completed successfully",
      data: assessment,
    });
  } catch (error) {
    next(error);
  }
});


// ===============================
// GET ONE ASSESSMENT
// ===============================

router.get("/:assessmentId", async (req, res, next) => {

    try {

        const assessment =
            await getAssessmentById(
                req.params.assessmentId
            );

        if (!assessment) {

            return res.status(404).json({

                success: false,

                message:
                    "Assessment not found"

            });

        }

        res.status(200).json({

            success: true,

            data: assessment

        });

    } catch (error) {

        next(error);

    }

});


// ===============================
// UPDATE ASSESSMENT
// ===============================

router.put("/:assessmentId", assessmentValidation, async (req, res, next) => {

    try {
        const errors = validationResult(req);

        if (!errors.isEmpty()) {
            return res.status(400).json({
                success: false,
                message: "Validation failed",
                errors: errors.array()
            });
        }

        const existing =
            await getAssessmentById(
                req.params.assessmentId
            );

        if (!existing) {

            return res.status(404).json({

                success: false,

                message:
                    "Assessment not found"

            });

        }

        const updatedData = {

            ...req.body,

            updatedAt:
                new Date().toISOString()

        };

        const result =
            await updateAssessment(
                req.params.assessmentId,
                updatedData
            );

        res.status(200).json({

            success: true,

            message:
                "Assessment updated successfully",

            data: result

        });

    } catch (error) {

        next(error);

    }

});


// ===============================
// DELETE ASSESSMENT
// ===============================

router.delete("/:assessmentId", async (req, res, next) => {

    try {

        const existing =
            await getAssessmentById(
                req.params.assessmentId
            );

        if (!existing) {

            return res.status(404).json({

                success: false,

                message:
                    "Assessment not found"

            });

        }

        await deleteAssessment(
            req.params.assessmentId
        );

        res.status(200).json({

            success: true,

            message:
                "Assessment deleted successfully"

        });

    } catch (error) {

        next(error);

    }

});


module.exports = router;