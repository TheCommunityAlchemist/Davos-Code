# DAVOS 2026 AI Event Navigator - React Frontend

A modern React + TypeScript frontend for the Davos 2026 AI Event Navigator, built with Tailwind CSS and shadcn/ui components. Designed to work seamlessly with [Lovable](https://lovable.dev).

## 🚀 Quick Start

### For Lovable

1. Import this project into Lovable
2. The components are ready to use - just update the `API_URL` in `src/lib/constants.ts` to point to your backend

### For Local Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at `http://localhost:8080`

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui components (Button, Input, etc.)
│   ├── Header.tsx       # Top navigation with stats
│   ├── ChatPanel.tsx    # Side panel with AI chat interface
│   ├── DavosMap.tsx     # Mapbox GL map with markers
│   ├── FilterChips.tsx  # Track filter buttons
│   ├── LoadingOverlay.tsx
│   └── RecommendationCard.tsx
├── hooks/
│   ├── useEvents.ts     # Fetch and manage events
│   ├── useRecommendations.ts  # AI chat functionality
│   └── use-toast.ts     # Toast notifications
├── lib/
│   ├── constants.ts     # API config, track colors
│   └── utils.ts         # Utility functions (cn)
├── pages/
│   ├── Index.tsx        # Main page
│   └── NotFound.tsx     # 404 page
├── types/
│   └── events.ts        # TypeScript interfaces
├── App.tsx              # Root component with routing
├── main.tsx             # Entry point
└── index.css            # Tailwind + custom styles
```

## 🎨 Features

- **AI-Powered Recommendations**: Enter your LinkedIn URL or describe your interests to get personalized event suggestions
- **Interactive 3D Map**: Mapbox GL with custom markers, popups, and smooth fly-to animations
- **Track Filtering**: Quick filter chips to browse events by category
- **Responsive Design**: Works on desktop and mobile
- **Beautiful Dark Theme**: Alpine-inspired color palette

## 🔧 Configuration

Update `src/lib/constants.ts` to configure:

```typescript
export const CONFIG = {
  API_URL: 'http://localhost:8080',  // Your backend URL
  MAPBOX_TOKEN: 'your-mapbox-token', // Get one at mapbox.com
  DAVOS_CENTER: [9.8360, 46.8027],
  DEFAULT_ZOOM: 14,
};
```

## 🎯 Components Overview

### Header
Displays the logo, title, and live stats (event count, venue count).

### ChatPanel
- LinkedIn URL input with badge
- Freeform profile description textarea
- AI response display
- Scrollable recommendation cards

### DavosMap
- Full Mapbox GL integration
- Custom styled markers with track colors
- Popup cards with event details
- 3D/2D toggle and reset view controls

### RecommendationCard
Clickable cards that show:
- Event title
- Match percentage badge
- Venue location
- AI explanation for the match

### FilterChips
Horizontal scrolling filter buttons for each event track.

## 🔌 API Integration

The frontend expects these endpoints from your backend:

### GET /api/events
Returns all events:
```json
{
  "success": true,
  "events": [
    {
      "id": "1",
      "title": "AI Summit",
      "venue": "Congress Center",
      "track": "Technology & AI",
      "lat": 46.8027,
      "lon": 9.8360
    }
  ]
}
```

### POST /api/chat
Send user profile for recommendations:
```json
// Request
{ "message": "linkedin.com/in/username" }

// Response
{
  "success": true,
  "message": "Based on your profile...",
  "recommendations": [
    {
      "id": "1",
      "title": "AI Summit",
      "match_percentage": 95,
      "explanation": "Perfect match for your AI background"
    }
  ]
}
```

## 📦 Dependencies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Mapbox GL** - Interactive maps
- **React Query** - Data fetching
- **React Router** - Navigation

## 🎨 Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Alpine Dark | `#0a1628` | Background |
| Glacier Blue | `#1a4a6e` | Accents |
| Aurora Cyan | `#06b6d4` | Primary |
| Aurora Green | `#10b981` | Success |
| Frost | `#94a3b8` | Muted text |

## License

MIT
