# DAVOS 2026 Frontend

Interactive Mapbox map with AI-powered event recommendations.

## Setup

1. **Get a Mapbox Token**: https://mapbox.com/
2. **Update `app.js`**:
   ```javascript
   const CONFIG = {
       API_URL: 'https://YOUR-RAILWAY-URL.up.railway.app',
       MAPBOX_TOKEN: 'YOUR_MAPBOX_TOKEN',
   };
   ```

## Deploy to Vercel

```bash
cd frontend
npx vercel --prod
```

## Features

- 🗺️ Mapbox GL JS map with 42 Davos venues
- 🔗 LinkedIn URL integration
- 🤖 AI-powered recommendations
- ✨ Animated fly-to on recommendations
- 🎨 Track-based color coding
- 📱 Responsive design

