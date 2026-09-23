const CATEGORIES = {
    infrastructure: {
        weight: 0.25,
        questions: [
            "infra_1",
            "infra_2",
            "infra_3",
            "infra_4",
            "infra_5"
        ]
    },

    process: {
        weight: 0.20,
        questions: [
            "process_1",
            "process_2",
            "process_3",
            "process_4",
            "process_5"
        ]
    },

    people: {
        weight: 0.15,
        questions: [
            "people_1",
            "people_2",
            "people_3",
            "people_4",
            "people_5"
        ]
    },

    data: {
        weight: 0.20,
        questions: [
            "data_1",
            "data_2",
            "data_3",
            "data_4",
            "data_5"
        ]
    },

    security: {
        weight: 0.20,
        questions: [
            "security_1",
            "security_2",
            "security_3",
            "security_4",
            "security_5"
        ]
    }
};

const MAX_ANSWER_VALUE = 4;

const MATURITY_LEVELS = [
    [20, "Level 1 - Initial"],
    [40, "Level 2 - Developing"],
    [60, "Level 3 - Defined"],
    [80, "Level 4 - Managed"],
    [100, "Level 5 - Optimized"]
];

function calculateCategoryScore(responses, categoryName) {
    const questionIds = CATEGORIES[categoryName].questions;

    const total = questionIds.reduce(
        (sum, questionId) =>
            sum + (responses[questionId] ?? 0),
        0
    );

    const maxPossible =
        questionIds.length * MAX_ANSWER_VALUE;

    return Number(((total / maxPossible) * 100).toFixed(2));
}

function calculateAllCategoryScores(responses) {
    const categoryScores = {};

    for (const category of Object.keys(CATEGORIES)) {
        categoryScores[category] =
            calculateCategoryScore(responses, category);
    }

    return categoryScores;
}

function calculateOverallScore(categoryScores) {
    let total = 0;

    for (const [category, details] of Object.entries(CATEGORIES)) {
        total +=
            (categoryScores[category] ?? 0) *
            details.weight;
    }

    return Number(total.toFixed(2));
}

function getMaturityLevel(overallScore) {
    for (const [threshold, label] of MATURITY_LEVELS) {
        if (overallScore <= threshold) {
            return label;
        }
    }

    return MATURITY_LEVELS[MATURITY_LEVELS.length - 1][1];
}

function identifyGaps(categoryScores, threshold = 50) {
    const gaps = Object.entries(categoryScores)
        .filter(([, score]) => score < threshold)
        .map(([category]) => category);

    gaps.sort(
        (a, b) =>
            categoryScores[a] - categoryScores[b]
    );

    return gaps;
}

function runFullAssessment(responses) {
    const categoryScores =
        calculateAllCategoryScores(responses);

    const overallScore =
        calculateOverallScore(categoryScores);

    const maturityLevel =
        getMaturityLevel(overallScore);

    const gaps =
        identifyGaps(categoryScores);

    return {
        categoryScores,
        overallScore,
        maturityLevel,
        gaps
    };
}

module.exports = {
    runFullAssessment
};