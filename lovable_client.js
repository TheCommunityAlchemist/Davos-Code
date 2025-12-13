/**
 * DAVOS 2026 API Client for Lovable Integration
 * ==============================================
 * 
 * Copy this code into your Lovable project to connect to the Davos chatbot API.
 * 
 * Usage:
 *   const davos = new DavosClient('https://your-api-url.com');
 *   const recommendations = await davos.getRecommendations('linkedin.com/in/yourname');
 *   const chatResponse = await davos.chat('I am interested in blockchain and climate');
 */

class DavosClient {
  constructor(apiUrl) {
    this.apiUrl = apiUrl.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Get personalized recommendations based on profile
   * @param {string} profile - LinkedIn URL or profile description
   * @param {number} topK - Number of recommendations (default 5)
   * @returns {Promise<Object>} Recommendations with match percentages
   */
  async getRecommendations(profile, topK = 5) {
    const response = await fetch(`${this.apiUrl}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, top_k: topK })
    });
    return response.json();
  }

  /**
   * Chat with the Davos AI assistant
   * @param {string} message - User message (LinkedIn URL, search query, or profile)
   * @returns {Promise<Object>} Chat response with recommendations or search results
   */
  async chat(message) {
    const response = await fetch(`${this.apiUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  }

  /**
   * Get all events
   * @returns {Promise<Object>} All events with coordinates for map
   */
  async getAllEvents() {
    const response = await fetch(`${this.apiUrl}/api/events`);
    return response.json();
  }

  /**
   * Get a single event by ID
   * @param {string} eventId - Event ID (e.g., "WEF2026-001")
   * @returns {Promise<Object>} Event details
   */
  async getEvent(eventId) {
    const response = await fetch(`${this.apiUrl}/api/events/${eventId}`);
    return response.json();
  }

  /**
   * Search events by query
   * @param {string} query - Search query
   * @param {number} limit - Max results (default 10)
   * @returns {Promise<Object>} Search results with scores
   */
  async search(query, limit = 10) {
    const response = await fetch(`${this.apiUrl}/api/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    return response.json();
  }

  /**
   * Get all tracks with event counts
   * @returns {Promise<Object>} List of tracks
   */
  async getTracks() {
    const response = await fetch(`${this.apiUrl}/api/tracks`);
    return response.json();
  }

  /**
   * Get all venues with coordinates
   * @returns {Promise<Object>} List of venues with lat/lon for map markers
   */
  async getVenues() {
    const response = await fetch(`${this.apiUrl}/api/venues`);
    return response.json();
  }

  /**
   * Check if input is a LinkedIn URL
   * @param {string} text - Input text
   * @returns {boolean} True if LinkedIn URL
   */
  isLinkedInUrl(text) {
    return /linkedin\.com\/in\/[\w-]+/i.test(text);
  }
}

// ============================================
// EXAMPLE USAGE IN LOVABLE
// ============================================

/*
// 1. Initialize the client with your API URL
const davos = new DavosClient('http://localhost:5000');

// 2. Simple chat interaction
async function handleUserInput(userMessage) {
  const response = await davos.chat(userMessage);
  
  if (response.success) {
    // Display the AI message
    console.log(response.message);
    
    // Handle recommendations
    if (response.recommendations) {
      response.recommendations.forEach(rec => {
        console.log(`${rec.title} - ${rec.match_percentage}% match`);
        console.log(`📍 ${rec.venue} (${rec.address})`);
        console.log(`🌐 ${rec.website}`);
        
        // Add marker to your map
        addMapMarker(rec.lat, rec.lon, rec.title, rec.venue);
      });
    }
  }
}

// 3. Load all events for map
async function loadMapEvents() {
  const response = await davos.getAllEvents();
  
  if (response.success) {
    response.events.forEach(event => {
      addMapMarker(event.lat, event.lon, event.title, event.venue);
    });
  }
}

// 4. LinkedIn URL handling
async function handleLinkedInInput(linkedinUrl) {
  if (davos.isLinkedInUrl(linkedinUrl)) {
    const response = await davos.getRecommendations(linkedinUrl);
    
    if (response.success) {
      console.log(`Welcome, ${response.profile_parsed.name}!`);
      console.log(`Skills detected: ${response.profile_parsed.skills.join(', ')}`);
      
      // Highlight recommended events on map
      response.recommendations.forEach(rec => {
        highlightMarker(rec.id, rec.lat, rec.lon);
      });
    }
  }
}
*/

// Export for use in Lovable
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DavosClient;
}

