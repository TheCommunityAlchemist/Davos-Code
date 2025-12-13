#!/usr/bin/env python3
"""
DAVOS 2026 RECOMMENDATION API
=============================
Clean REST API for integration with external frontends (Lovable, React, etc.)

Endpoints:
- POST /api/recommend - Get personalized recommendations
- GET /api/events - Get all events
- GET /api/events/<id> - Get single event
- GET /api/search?q=<query> - Search events
- GET /api/tracks - Get all tracks

Author: WEF 2026 Hackathon Team
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from davos_agent import DavosRecommendationAgent, LinkedInProfileParser
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Lovable integration

# Initialize the recommendation agent
agent = DavosRecommendationAgent('davos_events.csv')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "events_loaded": len(agent.events),
        "version": "1.1.0"
    })


@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """
    Get personalized event recommendations.
    
    Request Body:
    {
        "profile": "Your LinkedIn URL or profile description",
        "top_k": 5  // optional, default 5
    }
    
    Response:
    {
        "success": true,
        "profile_parsed": {...},
        "recommendations": [...]
    }
    """
    data = request.get_json()
    
    if not data or 'profile' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'profile' in request body"
        }), 400
    
    profile = data['profile']
    top_k = data.get('top_k', 5)
    
    # Parse LinkedIn profile if applicable
    is_linkedin = LinkedInProfileParser.is_linkedin_url(profile)
    profile_data = LinkedInProfileParser.get_profile(profile)
    
    # Get recommendations
    recommendations = agent.recommend(profile, top_k=top_k)
    
    return jsonify({
        "success": True,
        "is_linkedin": is_linkedin,
        "profile_parsed": {
            "name": profile_data.get("name"),
            "headline": profile_data.get("headline"),
            "skills": profile_data.get("skills", profile_data.get("detected_skills", [])),
            "interests": profile_data.get("interests", [])
        },
        "recommendations": [
            {
                "id": rec.event.id,
                "title": rec.event.title,
                "description": rec.event.description,
                "venue": rec.event.venue,
                "address": rec.event.address,
                "location": rec.event.location,
                "track": rec.event.track,
                "topics": rec.event.topics,
                "start_time": rec.event.start_time,
                "end_time": rec.event.end_time,
                "capacity": rec.event.capacity,
                "website": rec.event.website,
                "lat": rec.event.lat,
                "lon": rec.event.lon,
                "match_percentage": rec.match_percentage,
                "explanation": rec.explanation,
                "matched_topics": rec.matched_topics
            }
            for rec in recommendations
        ]
    })


@app.route('/api/events', methods=['GET'])
def get_all_events():
    """Get all events."""
    return jsonify({
        "success": True,
        "count": len(agent.events),
        "events": [event.to_dict() for event in agent.events]
    })


@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get a single event by ID."""
    event = agent.get_event_by_id(event_id)
    
    if not event:
        return jsonify({
            "success": False,
            "error": f"Event {event_id} not found"
        }), 404
    
    return jsonify({
        "success": True,
        "event": event.to_dict()
    })


@app.route('/api/search', methods=['GET'])
def search_events():
    """
    Search events by query.
    
    Query params:
    - q: Search query (required)
    - limit: Max results (optional, default 10)
    """
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Missing 'q' query parameter"
        }), 400
    
    results = agent.search_events(query, top_k=limit)
    
    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": [
            {
                **event.to_dict(),
                "score": round(score * 100, 1)
            }
            for event, score in results
        ]
    })


@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    """Get all unique tracks with event counts."""
    tracks = {}
    for event in agent.events:
        tracks[event.track] = tracks.get(event.track, 0) + 1
    
    return jsonify({
        "success": True,
        "tracks": [
            {"name": name, "count": count}
            for name, count in sorted(tracks.items(), key=lambda x: -x[1])
        ]
    })


@app.route('/api/venues', methods=['GET'])
def get_venues():
    """Get all unique venues with their locations."""
    venues = {}
    for event in agent.events:
        if event.venue not in venues:
            venues[event.venue] = {
                "name": event.venue,
                "address": event.address,
                "lat": event.lat,
                "lon": event.lon,
                "events": []
            }
        venues[event.venue]["events"].append(event.id)
    
    return jsonify({
        "success": True,
        "count": len(venues),
        "venues": list(venues.values())
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Simple chat endpoint for conversational interface.
    
    Request Body:
    {
        "message": "User's message"
    }
    
    Handles:
    - LinkedIn URLs
    - Profile descriptions
    - Search queries
    - General questions
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'message' in request body"
        }), 400
    
    message = data['message'].strip()
    
    # Check if it's a LinkedIn URL
    if LinkedInProfileParser.is_linkedin_url(message):
        profile_data = LinkedInProfileParser.get_profile(message)
        recommendations = agent.recommend(message, top_k=5)
        
        return jsonify({
            "success": True,
            "type": "linkedin_recommendations",
            "message": f"Found your LinkedIn profile! Based on your background in {', '.join(profile_data.get('skills', [])[:3])}, here are your top recommendations:",
            "profile": {
                "name": profile_data.get("name"),
                "skills": profile_data.get("skills", []),
                "interests": profile_data.get("interests", [])
            },
            "recommendations": [
                {
                    "id": rec.event.id,
                    "title": rec.event.title,
                    "venue": rec.event.venue,
                    "address": rec.event.address,
                    "match_percentage": rec.match_percentage,
                    "explanation": rec.explanation,
                    "website": rec.event.website,
                    "lat": rec.event.lat,
                    "lon": rec.event.lon
                }
                for rec in recommendations
            ]
        })
    
    # Check for search intent
    search_keywords = ['find', 'search', 'looking for', 'where', 'show me', 'events about']
    is_search = any(kw in message.lower() for kw in search_keywords)
    
    if is_search:
        # Extract search query
        query = message.lower()
        for kw in search_keywords:
            query = query.replace(kw, '')
        query = query.strip()
        
        results = agent.search_events(query, top_k=5)
        
        return jsonify({
            "success": True,
            "type": "search_results",
            "message": f"Found {len(results)} events matching '{query}':",
            "results": [
                {
                    "id": event.id,
                    "title": event.title,
                    "venue": event.venue,
                    "address": event.address,
                    "track": event.track,
                    "score": round(score * 100, 1),
                    "website": event.website,
                    "lat": event.lat,
                    "lon": event.lon
                }
                for event, score in results
            ]
        })
    
    # Treat as profile description for recommendations
    recommendations = agent.recommend(message, top_k=5)
    profile_data = LinkedInProfileParser.get_profile(message)
    
    detected_skills = profile_data.get('detected_skills', []) or profile_data.get('skills', [])
    
    intro_message = "Based on your interests"
    if detected_skills:
        intro_message = f"Based on your interest in {', '.join(detected_skills[:3])}"
    
    return jsonify({
        "success": True,
        "type": "recommendations",
        "message": f"{intro_message}, here are your personalized recommendations:",
        "detected_interests": detected_skills,
        "recommendations": [
            {
                "id": rec.event.id,
                "title": rec.event.title,
                "venue": rec.event.venue,
                "address": rec.event.address,
                "track": rec.event.track,
                "match_percentage": rec.match_percentage,
                "explanation": rec.explanation,
                "website": rec.event.website,
                "lat": rec.event.lat,
                "lon": rec.event.lon
            }
            for rec in recommendations
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║           🏔️  DAVOS 2026 RECOMMENDATION API  🏔️                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Server running at: http://localhost:{port}                       ║
║                                                                  ║
║  Endpoints:                                                      ║
║    POST /api/recommend  - Get personalized recommendations       ║
║    POST /api/chat       - Conversational chat interface          ║
║    GET  /api/events     - Get all events                         ║
║    GET  /api/search?q=  - Search events                          ║
║    GET  /api/tracks     - Get all tracks                         ║
║    GET  /api/venues     - Get all venues with coordinates        ║
║                                                                  ║
║  Events loaded: {len(agent.events):3}                                         ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)

