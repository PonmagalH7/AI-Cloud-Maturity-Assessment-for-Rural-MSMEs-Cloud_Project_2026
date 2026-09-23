const { body } = require("express-validator");

const assessmentValidation = [
    body("businessName")
        .trim()
        .notEmpty()
        .withMessage("Business name is required"),

    body("location")
        .trim()
        .notEmpty()
        .withMessage("Location is required"),

    body("industry")
        .trim()
        .notEmpty()
        .withMessage("Industry is required"),

    body("cloudUsage")
        .trim()
        .notEmpty()
        .withMessage("Cloud usage is required")
];

module.exports = {
    assessmentValidation
};