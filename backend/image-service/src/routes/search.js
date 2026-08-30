// HTTP layer only — delegates to services/pexelSearch.js, no pexelkit
// imports here.
import { Router } from "express";
import { findBestImage } from "../services/pexelSearch.js";

const router = Router();

router.get("/", async (req, res) => {
  const { q } = req.query;

  if (!q || typeof q !== "string") {
    return res.status(400).json({ error: "Missing required query param: q" });
  }

  try {
    const result = await findBestImage(q);
    if (!result) {
      return res.status(404).json({ error: `No image found for query: ${q}` });
    }
    return res.json(result);
  } catch (err) {
    console.error("pexelkit search failed:", err);
    return res.status(502).json({ error: "Image search failed" });
  }
});

export default router;
