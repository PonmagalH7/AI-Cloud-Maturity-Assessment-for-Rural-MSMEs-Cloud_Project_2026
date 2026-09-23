const { validationResult } = require("express-validator");
const { assessmentValidation } = require("../utils/validation");
const express = require("express");
const { v4: uuidv4 } = require("uuid");
const authMiddleware = require("../middleware/authMiddleware");

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

router.post("/", assessmentValidation, async (req, res, next) => { 

    try {
        const errors = validationResult(req);

        if (!errors.isEmpty()) {
            return res.status(400).json({
                success: false,
                message:"Validation failed",
                 errors: errors.array()
            });
        }

        const assessment = {

            assessmentId: uuidv4(),

            ...req.body,

            createdAt: new Date().toISOString()

        };

        const result =
            await createAssessment(assessment);

        res.status(201).json({

            success: true,

            message:
                "Assessment created successfully",

            data: result

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