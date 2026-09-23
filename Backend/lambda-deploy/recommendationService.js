const {
    BedrockRuntimeClient,
    ConverseCommand
} = require("@aws-sdk/client-bedrock-runtime");

const REGION = "ap-south-1";
const MODEL_ID =
    process.env.BEDROCK_MODEL_ID || "amazon.nova-micro-v1:0";

const bedrock = new BedrockRuntimeClient({
    region: REGION
});

const FALLBACK_TIPS = {
    infrastructure: [
        "Move critical business files to a free-tier cloud storage service with automatic backup",
        "Set up a basic scheduled maintenance check for business devices"
    ],
    process: [
        "Document your top 3 daily workflows in a simple shared document",
        "Start using one free digital tool (e.g. spreadsheet-based tracking) for inventory or billing"
    ],
    people: [
        "Run a short internal session to walk staff through the tools you already use",
        "Assign one staff member as the point of contact for basic tech issues"
    ],
    data: [
        "Set up automatic weekly backups for your most important business data",
        "Start using a shared spreadsheet or basic database instead of paper records"
    ],
    security: [
        "Turn on multi-factor authentication (MFA) for all business accounts",
        "Set a policy requiring strong, unique passwords across all business logins"
    ]
};

const TIER_UPGRADE_TIPS = {
    infrastructure:
        "Consider a paid cloud hosting/storage plan with stronger reliability guarantees",
    process:
        "Invest in a lightweight business management tool instead of fully manual tracking",
    people:
        "Bring in a part-time trainer for structured digital upskilling",
    data:
        "Move to a managed cloud database service instead of spreadsheet-based records",
    security:
        "Engage a professional to set up a formal cybersecurity policy"
};

const GENERIC_FREE_TIPS = [
    "Continue maintaining your current digital practices",
    "Review your setup periodically as your business grows",
    "Consider light staff refreshers to keep digital skills current"
];

function buildPrompt(
    businessType,
    categoryScores,
    overallScore,
    maturityLevel,
    gaps
) {
    return `You are a cloud advisor for a rural MSME (Micro, Small, or Medium
Enterprise) in India. You will be given a cloud maturity assessment result.
Do not invent or change any numbers - use only the scores given. Explain the
result in plain, non-technical language suitable for a small business owner,
and suggest exactly 3 practical next steps, prioritizing the weakest categories.

This business is classified as a ${businessType} enterprise under India's
MSME classification. Scale your suggestions to match: a Micro enterprise
typically has very limited budget and staff, so favor free or near-zero-cost
steps and avoid suggesting dedicated IT hires or paid enterprise tools. A
Small enterprise can typically afford small recurring costs (e.g. a paid
backup service, a part-time trainer). A Medium enterprise can typically
absorb moderate investment (e.g. a proper cloud migration project, hiring
part-time IT support). Do not mention the word "budget" or the classification
itself in your output - just make the suggestions naturally appropriate to a
business of this scale.

Overall score: ${overallScore}/100 (${maturityLevel})
Category scores: ${JSON.stringify(categoryScores)}
Weakest categories (gaps): ${JSON.stringify(gaps)}

Respond ONLY with valid JSON in this exact format, nothing else:
{
  "summary": "2-3 sentence plain-language explanation of the result",
  "priorities": ["step 1", "step 2", "step 3"]
}`;
}

function getFallbackRecommendation(
    overallScore,
    maturityLevel,
    gaps,
    businessType = "Micro"
) {
    const priorities = [];

    // First pass: one free/low-cost tip per gap.
    for (const gap of gaps.slice(0, 3)) {
        const tips = FALLBACK_TIPS[gap];

        if (tips && tips.length > 0) {
            priorities.push(tips[0]);
        }
    }

    // Second pass: second tip from gap categories.
    if (priorities.length < 3) {
        for (const gap of gaps.slice(0, 3)) {
            const tips = FALLBACK_TIPS[gap];

            if (tips && tips.length > 1) {
                priorities.push(tips[1]);
            }

            if (priorities.length >= 3) {
                break;
            }
        }
    }

    // Third pass: Small/Medium tier upgrades.
    if (
        priorities.length < 3 &&
        (businessType === "Small" ||
            businessType === "Medium")
    ) {
        for (const gap of gaps) {
            const tip = TIER_UPGRADE_TIPS[gap];

            if (
                tip &&
                !priorities.includes(tip)
            ) {
                priorities.push(tip);
            }

            if (priorities.length >= 3) {
                break;
            }
        }
    }

    // Final padding.
    let i = 0;

    while (priorities.length < 3) {
        priorities.push(
            GENERIC_FREE_TIPS[
                i % GENERIC_FREE_TIPS.length
            ]
        );
        i++;
    }

    return {
        summary:
            `Your business scored ${overallScore}/100, placing it at ${maturityLevel}. ` +
            `The areas needing the most attention are: ` +
            `${gaps.length ? gaps.join(", ") : "none - strong across the board"}.`,

        priorities: priorities.slice(0, 3),

        source: "fallback"
    };
}

async function generateRecommendation(
    businessType,
    categoryScores,
    overallScore,
    maturityLevel,
    gaps
) {
    try {
        const prompt = buildPrompt(
            businessType,
            categoryScores,
            overallScore,
            maturityLevel,
            gaps
        );

        const command = new ConverseCommand({
            modelId: MODEL_ID,

            messages: [
                {
                    role: "user",
                    content: [
                        {
                            text: prompt
                        }
                    ]
                }
            ],

            inferenceConfig: {
                maxTokens: 400,
                temperature: 0.3
            }
        });

        const response =
            await bedrock.send(command);

        let text =
            response?.output?.message?.content?.[0]?.text;

        if (!text) {
            throw new Error(
                "Bedrock response did not contain text"
            );
        }

        text = text.trim();

        if (text.startsWith("```")) {
            text = text.split("```")[1];

            if (text.startsWith("json")) {
                text = text.substring(4);
            }
        }

        text = text.trim();

        const result = JSON.parse(text);

        if (
            !result.summary ||
            !Array.isArray(result.priorities)
        ) {
            throw new Error(
                "Bedrock response missing expected fields"
            );
        }

        return {
            summary: result.summary,
            priorities: result.priorities,
            source: "bedrock"
        };

    } catch (error) {
        console.error(
            "Bedrock recommendation failed:",
            error.message
        );

        return getFallbackRecommendation(
            overallScore,
            maturityLevel,
            gaps,
            businessType
        );
    }
}

module.exports = {
    generateRecommendation
};