const { generateRecommendation } = require("./src/services/recommendationService");

async function test() {
    const result = await generateRecommendation(
        "Micro",
        {
            infrastructure: 60,
            process: 70,
            people: 50,
            data: 65,
            security: 55
        },
        60.5,
        "Level 4 - Managed",
        []
    );

    console.log(JSON.stringify(result, null, 2));
}

test();