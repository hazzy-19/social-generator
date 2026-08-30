// The ONLY file in this service that imports pexelkit directly.
import { searchPhotos, scoreAndRank } from "pexelkit";

/**
 * @param {string} query - natural-language description, e.g. "minimalist desk deep work focus"
 * @returns {Promise<{url: string, photographer?: string, source: string} | null>}
 */
export async function findBestImage(query) {
  const candidates = await searchPhotos({ query, perPage: 20 });
  if (!candidates.length) return null;

  const [best] = scoreAndRank(candidates);

  return {
    url: best.urls.large,
    photographer: best.photographer ?? null,
    source: "pexels",
  };
}
