const errorMiddleware = (err, req, res, next) => {

    console.error("ERROR:", err);

    res.status(500).json({

        success: false,

        message:
            "Internal server error",

        error:
            process.env.NODE_ENV === "development"
                ? err.message
                : undefined

    });

};

module.exports = errorMiddleware;