const express = require("express");
const { Pool } = require("pg");
const bodyParser = require("body-parser");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");

const app = express();
const port = 5001;

const apiRouter = express.Router();

const path = require("path");
const dotenv = require("dotenv");

const envFile =
    process.env.NODE_ENV === "production"
        ? path.resolve(__dirname, ".env.production")
        : path.resolve(__dirname, ".env.development");

dotenv.config({ path: envFile });

const { execFile } = require("child_process");
const util = require("util");
const execFilePromise = util.promisify(execFile);

/*
async function analyzeBertSentiment(text) {
    try {
        const { stdout } = await execFilePromise("python3", [
            path.join(__dirname, "analysis/ternary_bert.py"),
            text,
        ]);
        return stdout.trim();
    } catch (error) {
        console.error("Sentiment analysis failed:", error);
        return "neutral";
    }
}*/

async function analyzeVaderSentiment(text) {
    try {
        const { stdout } = await execFilePromise("python3", [
            path.join(__dirname, "analysis/vader.py"),
            text,
        ]);
        return stdout.trim();
    } catch (error) {
        console.error("VADER analysis failed:", error);
        return "neutral";
    }
}

async function analyzeTextBlobSentiment(text) {
    try {
        const { stdout } = await execFilePromise("python3", [
            path.join(__dirname, "analysis/text_analysis/analyze_textblob.py"),
            text,
        ]);
        return stdout.trim(); // JSON string
    } catch (error) {
        console.error("TextBlob analysis failed:", error);
        return null;
    }
}

async function analyzeGoEmotionsSentiment(text) {
    try {
        const { stdout } = await execFilePromise("python3", [
            path.join(__dirname, "analysis/text_analysis/goemotions.py"),
            text,
        ]);
        return stdout.trim(); // just the top emotion
    } catch (error) {
        console.error("GoEmotions analysis failed:", error);
        return null;
    }
}

async function analyzeMask2FormerGVI(locationId, filename) {
    try {
        const { stdout } = await execFilePromise("python3", [
            path.join(__dirname, "analysis/image_analysis/mask2former/mask2former.py"),
            locationId,
            filename
        ]);
        console.log(`✅ Mask2Former GVI updated for location_id ${locationId}: ${stdout.trim()}`);
    } catch (error) {
        console.error(`❌ Failed to run Mask2Former GVI for location_id ${locationId}:`, error.message);
    }
}

const pool = new Pool({
    user: process.env.DATABASE_USER,
    host: process.env.DATABASE_HOST,
    database: process.env.DATABASE_NAME,
    password: process.env.DATABASE_PASSWORD,
    port: process.env.DATABASE_PORT,
});

app.use(
    cors({
        origin: process.env.CORS_ORIGIN,
        methods: ["GET", "POST"],
    })
);

app.use(bodyParser.json());

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, path.join(__dirname, "../frontend/public/uploads"));
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
        cb(null, "photo-" + uniqueSuffix + ext);
    },
});

const upload = multer({
    storage: storage,
    fileFilter: (req, file, cb) => {
        const allowedTypes = ["image/jpeg", "image/png", "image/gif"];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error("Only JPEG, PNG and GIF files are allowed."));
        }
    },
    limits: { fileSize: 5 * 1024 * 1024 },
});

app.use("/uploads", express.static(path.join(__dirname, "../frontend/public/uploads")));

apiRouter.get("/get-locations", async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT
                l.id,
                l.geom,
                l.x_coordinate,
                l.y_coordinate,
                l.image,
                l.email,
                l.agreed,
                l.date_time,
                l.age_group_id,
                l.gender,
                l.user_id,
                AVG(pr.likert_value) AS avg_likert
            FROM locations l
            LEFT JOIN parameter_responses pr ON l.id = pr.location_id
            GROUP BY 
                l.id, l.geom, l.x_coordinate, l.y_coordinate, l.image,
                l.email, l.agreed, l.date_time, l.age_group_id, l.gender, l.user_id
            ORDER BY l.id;
        `);
        res.status(200).json(result.rows);
    } catch (err) {
        console.error("Error fetching locations:", err);
        res.status(500).json({ error: "Failed to fetch locations" });
    }
});

apiRouter.post("/submit", upload.single("photo"), async (req, res) => {
    try {
        const {
            x_coord,
            y_coord,
            email,
            agreed,
            parameter_responses,
            free_text_responses,
            age_group_id,
            gender
        } = req.body;

        const user_id = req.body.user_id || null;

        if (!x_coord || !y_coord) {
            return res.status(400).json({ error: "Coordinates are required." });
        }

        let photoPath = null;
        if (req.file) {
            photoPath = `https://csgis.idi.ntnu.no/uploads/${req.file.filename}`;
        }

        let ageGroupIdInt = null;

        if (age_group_id && age_group_id.trim() !== "") {
            let parsedAgeGroup = (typeof age_group_id === "string" ? age_group_id : "").trim();

            if (parsedAgeGroup !== "") {
                const ageGroupQuery = await pool.query(
                    "SELECT id FROM age_groups WHERE age_group = $1",
                    [parsedAgeGroup]
                );

                if (ageGroupQuery.rows.length === 0) {
                    return res.status(400).json({ error: "Invalid age group." });
                }

                ageGroupIdInt = ageGroupQuery.rows[0].location_id;
            }
        }

        const genderValue = gender && gender.trim() !== '' ? gender : null;

        const locationResult = await pool.query(
            `INSERT INTO locations 
                (geom, x_coordinate, y_coordinate, image, email, agreed, date_time, age_group_id, gender, user_id)
            VALUES
                (ST_SetSRID(ST_MakePoint($1, $2), 4326), $1, $2, $3, $4, $5, NOW(), $6, $7, $8)
            RETURNING id`,
            [
                x_coord,
                y_coord,
                photoPath,
                email || null,
                agreed === "true",
                ageGroupIdInt,
                genderValue,
                user_id
            ]
        );        

        const locationId = locationResult.rows[0].id;

        console.log("before img analysis")

        if (req.file) {
            console.log("Uploaded filename:", req.file.filename); // 👈 Add this line
            const filename = req.file.filename;
            analyzeMask2FormerGVI(locationId, filename);
        }              

        if (parameter_responses) {
            const parsedParams = JSON.parse(parameter_responses);

            for (const param of parsedParams) {
                const { parameter_id, likert_value } = param;
                const paramQuery = await pool.query(
                    `SELECT id FROM parameters WHERE short_name = $1`,
                    [parameter_id]
                );

                if (paramQuery.rows.length === 0) {
                    console.error(`Skipping unknown parameter: '${parameter_id}'`);
                    continue;
                }

                const paramId = paramQuery.rows[0].id;
                await pool.query(
                    `INSERT INTO parameter_responses (location_id, parameter_id, likert_value)
                     VALUES ($1, $2, $3)`,
                    [locationId, paramId, likert_value]
                );
            }
        }

        if (free_text_responses) {
            const parsedFreeText = JSON.parse(free_text_responses);
            let combinedText = "";
            for (const responseObj of parsedFreeText) {
                const { question_id, response } = responseObj;
                const questionId = parseInt(question_id, 10);

                if (!questionId || !response) continue;

                const freeTextResult = await pool.query(
                    `INSERT INTO free_text_responses (location_id, question_id, free_text_response)
                    VALUES ($1, $2, $3)
                    RETURNING id`,
                    [locationId, questionId, response]
                );
            }
            // After processing all free_text_responses...
            try {
                const combinedResult = await pool.query(
                    `SELECT free_text_response 
                    FROM free_text_responses 
                    WHERE location_id = $1`,
                    [locationId]
                );

                const allowedQuestionIds = [1, 2];

                const filteredResult = await pool.query(
                    `SELECT question_id, free_text_response 
                     FROM free_text_responses 
                     WHERE location_id = $1 AND question_id = ANY($2::int[])`,
                    [locationId, allowedQuestionIds]
                );
                
                const responses = filteredResult.rows
                    .map(row => row.free_text_response.trim())
                    .filter(Boolean);
                
                // Join responses into one sentence (e.g. with period or semicolon)
                combinedText = responses.join(" ").trim();

                await pool.query(
                    `INSERT INTO combined_sentiment_analysis (location_id, combined_response)
                    VALUES ($1, $2)`,
                    [locationId, combinedText]
                );                

                /* Trigger sentiment analysis asynchronously
                analyzeBertSentiment(combinedText).then(async sentiment => {
                    try {
                        await pool.query(
                            `UPDATE combined_sentiment_analysis SET bert_sentiment = $1 WHERE location_id = $2`,
                            [sentiment, locationId]
                        );
                    } catch (err) {
                        console.error("Failed to update bert_sentiment for combined:", err.message);
                    }
                });*/
                
                analyzeVaderSentiment(combinedText).then(async sentiment => {
                    try {
                        await pool.query(
                            `UPDATE combined_sentiment_analysis SET vader_sentiment = $1 WHERE location_id = $2`,
                            [sentiment, locationId]
                        );
                    } catch (err) {
                        console.error("Failed to update vader_sentiment for combined:", err.message);
                    }
                });       
                
                
                // TextBlob sentiment
                analyzeTextBlobSentiment(combinedText).then(async sentimentJson => {
                    if (!sentimentJson) return;
                    try {
                        await pool.query(
                            `UPDATE combined_sentiment_analysis SET textblob_sentiment = $1 WHERE location_id = $2`,
                            [sentimentJson, locationId]
                        );
                        console.log(`✅ Updated textblob_sentiment for ${locationId}`);
                    } catch (err) {
                        console.error("Failed to update textblob_sentiment:", err.message);
                    }
                });
                
                            // GoEmotions sentiment
                analyzeGoEmotionsSentiment(combinedText).then(async emotion => {
                    if (!emotion) return;
                    try {
                        await pool.query(
                            `UPDATE combined_sentiment_analysis SET goemotions_sentiment = $1 WHERE location_id = $2`,
                            [emotion, locationId]
                        );
                        console.log(`✅ Updated goemotions_sentiment for ${locationId}`);
                    } catch (err) {
                        console.error("Failed to update goemotions_sentiment:", err.message);
                    }
                });

                console.log(`✅ Combined free text stored and sentiment analysis triggered for location_id ${locationId}`);
            } catch (err) {
                console.error("❌ Failed to process combined free text:", err.message);
            }
        }

        res.status(200).json({
            locationId,
            message: "Location, parameter, and free text responses added successfully."
        });

    } catch (err) {
        console.error("Error inserting data:", err.message);
        res.status(500).json({ error: "Failed to insert data." });
    }
});

app.use("/api", apiRouter);

app.listen(port, "0.0.0.0", () => {
    console.log(`Server running at http://0.0.0.0:${port}`);
});
