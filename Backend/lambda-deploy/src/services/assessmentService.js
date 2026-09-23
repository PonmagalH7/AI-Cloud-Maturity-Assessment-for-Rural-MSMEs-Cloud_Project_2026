const dynamoDB = require("../../config/dynamodb");

const {
    PutCommand,
    GetCommand,
    ScanCommand,
    UpdateCommand,
    DeleteCommand
} = require("@aws-sdk/lib-dynamodb");

const TABLE_NAME = "Assessments";

// CREATE
async function createAssessment(assessment) {
    await dynamoDB.send(
        new PutCommand({
            TableName: TABLE_NAME,
            Item: assessment
        })
    );

    return assessment;
}

// GET ALL
async function getAllAssessments() {
    const result = await dynamoDB.send(
        new ScanCommand({
            TableName: TABLE_NAME
        })
    );

    return result.Items || [];
}

// GET ONE
async function getAssessmentById(assessmentId) {
    const result = await dynamoDB.send(
        new GetCommand({
            TableName: TABLE_NAME,
            Key: {
                assessmentId
            }
        })
    );

    return result.Item;
}

// UPDATE
async function updateAssessment(assessmentId, data) {

    const updateExpressions = [];
    const expressionAttributeNames = {};
    const expressionAttributeValues = {};

    Object.entries(data).forEach(([key, value], index) => {

        const nameKey = `#key${index}`;
        const valueKey = `:value${index}`;

        updateExpressions.push(
            `${nameKey} = ${valueKey}`
        );

        expressionAttributeNames[nameKey] = key;
        expressionAttributeValues[valueKey] = value;
    });

    const result = await dynamoDB.send(
        new UpdateCommand({
            TableName: TABLE_NAME,

            Key: {
                assessmentId
            },

            UpdateExpression:
                `SET ${updateExpressions.join(", ")}`,

            ExpressionAttributeNames:
                expressionAttributeNames,

            ExpressionAttributeValues:
                expressionAttributeValues,

            ReturnValues: "ALL_NEW"
        })
    );

    return result.Attributes;
}

// DELETE
async function deleteAssessment(assessmentId) {

    await dynamoDB.send(
        new DeleteCommand({
            TableName: TABLE_NAME,

            Key: {
                assessmentId
            }
        })
    );
}

module.exports = {
    createAssessment,
    getAllAssessments,
    getAssessmentById,
    updateAssessment,
    deleteAssessment
};