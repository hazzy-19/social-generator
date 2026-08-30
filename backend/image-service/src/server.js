// App instance and route mounting only. No pexelkit calls here directly —
// that logic lives in services/pexelSearch.js.
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import searchRouter from "./routes/search.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, "..", ".env") });

const app = express();
app.use(cors());
app.use(express.json());

app.use("/search", searchRouter);

app.get("/health", (req, res) => res.json({ status: "ok" }));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`image-service listening on :${PORT}`));
