require('dotenv').config({ path: '../../backend/.env' }); // Read from backend .env
const express = require('express');
const cors = require('cors');
const { searchPhotos } = require('pexelkit');

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

app.get('/search', async (req, res) => {
  const query = req.query.q;
  if (!query) {
    return res.status(400).json({ error: 'Missing query parameter q' });
  }

  try {
    // pexelkit's searchPhotos returns an array of photos
    const photos = await searchPhotos({ query, perPage: 1 });
    if (photos && photos.length > 0) {
      // pexelkit standardizes the photo object, typically returning src or similar.
      // pexels API returns photos[0].src.large or similar, let's just grab the best URL
      const photo = photos[0];
      const url = photo.urls?.large || photo.urls?.original || photo.sourceUrl;
      res.json({ url });
    } else {
      res.status(404).json({ error: 'No images found' });
    }
  } catch (error) {
    console.error('Error fetching from pexels:', error);
    res.status(500).json({ error: 'Failed to fetch image' });
  }
});

app.listen(PORT, () => {
  console.log(`Image service listening on port ${PORT}`);
});
