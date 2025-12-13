/**
 * DAVOS 2026 AI Event Navigator - Configuration
 */

export const CONFIG = {
  // Your Railway API URL (use localhost:8080 for local testing)
  API_URL: 'http://localhost:8080',
  
  // Your Mapbox Access Token
  MAPBOX_TOKEN: 'pk.eyJ1IjoiZmxvd2J5ZnJhbnMiLCJhIjoiY21qNGU1Mm1kMTl1ODNsc2Y2YXc3dDk2NyJ9.5b6Qxwv-34lhKczdCq6oUw',
  
  // Davos coordinates
  DAVOS_CENTER: [9.8360, 46.8027] as [number, number],
  DEFAULT_ZOOM: 14,
  DEFAULT_PITCH: 45,
  DEFAULT_BEARING: -10,
};

export const TRACK_COLORS: Record<string, string> = {
  'Technology & AI': '#06b6d4',
  'Blockchain & Web3': '#8b5cf6',
  'Climate & Sustainability': '#10b981',
  'Health & Science': '#f43f5e',
  'Health & Longevity': '#f43f5e',
  'Health & Technology': '#f43f5e',
  'Finance & Technology': '#f59e0b',
  'Finance & Innovation': '#f59e0b',
  'Economy & Society': '#3b82f6',
  'Geopolitics': '#ef4444',
  'Media & Finance': '#ec4899',
  'Media & Economics': '#ec4899',
  'Media & Investment': '#ec4899',
  'Innovation & Startups': '#84cc16',
  'Innovation & Sustainability': '#84cc16',
  'Technology & Innovation': '#06b6d4',
  'Technology & Security': '#6366f1',
  'Space & Technology': '#a855f7',
  'Diversity & Inclusion': '#f472b6',
  'Well-being & Culture': '#14b8a6',
  'Networking': '#22d3ee',
  'Exclusive Events': '#fbbf24',
  'Independent Events': '#9ca3af',
  'Leadership': '#f97316',
  'Business & Strategy': '#0ea5e9',
  'Science & Research': '#a3e635',
};

export function getTrackColor(track: string): string {
  return TRACK_COLORS[track] || '#6b7280';
}
