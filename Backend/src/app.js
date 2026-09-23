require("dotenv").config();

const express = require("express");
const cors = require("cors");

const assessmentRoutes =
    require("./routes/assessmentRoutes");

const healthRoutes =
    require("./routes/healthRoutes");

const errorMiddleware =
    require("./middleware/errorMiddleware");

const app = express();

app.use(cors());

app.use(express.json());


// Health
app.get("/", (req, res) => {

    res.json({

        message:
            "AI Cloud Maturity Assessment API",

        status:
            "Backend is running"

    });

});


// Assessment API
app.use(
    "/api/assessments",
    assessmentRoutes
);
app.use(
    "/api/health",
    healthRoutes
);

// Error handler
app.use(errorMiddleware);


module.exports = app;