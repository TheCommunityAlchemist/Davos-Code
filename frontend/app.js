/**
 * DAVOS 2026 AI Event Navigator
 * ==============================
 * Mapbox + AI Agent Integration
 */

// =============================================
// CONFIGURATION
// =============================================

// TODO: Replace with your actual values
const CONFIG = {
    // Your Railway API URL (use localhost:8080 for local testing)
    API_URL: 'http://localhost:8080',
    
    // Your Mapbox Access Token - Get one free at https://mapbox.com
    MAPBOX_TOKEN: 'pk.eyJ1IjoiZmxvd2J5ZnJhbnMiLCJhIjoiY21qNGU1Mm1kMTl1ODNsc2Y2YXc3dDk2NyJ9.5b6Qxwv-34lhKczdCq6oUw',
    
    // Davos coordinates
    DAVOS_CENTER: [9.8360, 46.8027],
    DEFAULT_ZOOM: 14
};

// =============================================
// STATE
// =============================================

let map = null;
let markers = {};
let allEvents = [];
let currentRecommendations = [];

// =============================================
// TRACK COLORS
// =============================================

const TRACK_COLORS = {
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
    'Science & Research': '#a3e635'
};

function getTrackColor(track) {
    return TRACK_COLORS[track] || '#6b7280';
}

// =============================================
// INITIALIZATION
// =============================================

document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Initialize Mapbox
    mapboxgl.accessToken = CONFIG.MAPBOX_TOKEN;
    
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v11',
        center: CONFIG.DAVOS_CENTER,
        zoom: CONFIG.DEFAULT_ZOOM,
        pitch: 45,
        bearing: -10
    });

    // Add navigation controls
    map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');

    // Wait for map to load
    map.on('load', async () => {
        // Load all events
        await loadAllEvents();
        
        // Initialize filters
        initFilters();
    });

    // Setup event listeners
    setupEventListeners();
}

// =============================================
// API CALLS
// =============================================

async function loadAllEvents() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/api/events`);
        const data = await response.json();
        
        if (data.success) {
            allEvents = data.events;
            updateStats(data.events.length);
            
            // Add markers for all events
            data.events.forEach(event => {
                addMarker(event);
            });
            
            // Count unique venues
            const venues = new Set(data.events.map(e => e.venue));
            document.getElementById('venue-count').textContent = venues.size;
        }
    } catch (error) {
        console.error('Error loading events:', error);
        showMessage('⚠️ Could not connect to API. Make sure your Railway backend is running.');
    }
}

async function getRecommendations(input) {
    showLoading(true);
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display AI message
            showMessage(data.message);
            
            // Store and display recommendations
            currentRecommendations = data.recommendations || [];
            displayRecommendations(currentRecommendations);
            
            // Update markers
            highlightRecommendations(currentRecommendations);
            
            // Fly to first recommendation
            if (currentRecommendations.length > 0) {
                const first = currentRecommendations[0];
                map.flyTo({
                    center: [first.lon, first.lat],
                    zoom: 16,
                    pitch: 60,
                    duration: 2000
                });
            }
        } else {
            showMessage('❌ ' + (data.error || 'Something went wrong'));
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
        showMessage('⚠️ Could not connect to the AI agent. Please check if your API is running.');
    }
    
    showLoading(false);
}

// =============================================
// MAP FUNCTIONS
// =============================================

function addMarker(event, highlighted = false) {
    // Create marker element
    const el = document.createElement('div');
    el.className = 'marker';
    el.style.width = highlighted ? '20px' : '14px';
    el.style.height = highlighted ? '20px' : '14px';
    el.style.backgroundColor = getTrackColor(event.track);
    el.style.borderRadius = '50%';
    el.style.border = '2px solid white';
    el.style.cursor = 'pointer';
    el.style.boxShadow = highlighted 
        ? `0 0 20px ${getTrackColor(event.track)}` 
        : '0 2px 6px rgba(0,0,0,0.3)';
    el.style.transition = 'all 0.3s ease';

    // Create popup
    const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div class="popup-title">${event.title}</div>
        <div class="popup-venue">📍 ${event.venue}</div>
        <div class="popup-address">${event.address || event.location}</div>
        <span class="popup-track">${event.track}</span>
        ${event.website ? `<a href="${event.website}" target="_blank" class="popup-link">🔗 Visit Website</a>` : ''}
    `);

    // Create and add marker
    const marker = new mapboxgl.Marker(el)
        .setLngLat([event.lon, event.lat])
        .setPopup(popup)
        .addTo(map);

    markers[event.id] = { marker, element: el, event };
}

function highlightRecommendations(recommendations) {
    // Dim all markers
    Object.values(markers).forEach(({ element }) => {
        element.style.opacity = '0.3';
        element.style.transform = 'scale(0.8)';
    });

    // Highlight recommended markers
    recommendations.forEach((rec, index) => {
        const markerData = markers[rec.id];
        if (markerData) {
            const { element } = markerData;
            element.style.opacity = '1';
            element.style.transform = 'scale(1.3)';
            element.style.width = '20px';
            element.style.height = '20px';
            element.style.boxShadow = `0 0 20px ${getTrackColor(rec.track)}`;
            element.style.zIndex = 100 - index;
        }
    });
}

function resetMarkers() {
    Object.values(markers).forEach(({ element, event }) => {
        element.style.opacity = '1';
        element.style.transform = 'scale(1)';
        element.style.width = '14px';
        element.style.height = '14px';
        element.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
    });
}

function flyToEvent(eventId) {
    const markerData = markers[eventId];
    if (markerData) {
        const { marker, event } = markerData;
        map.flyTo({
            center: [event.lon, event.lat],
            zoom: 17,
            pitch: 60,
            duration: 1500
        });
        marker.togglePopup();
    }
}

// =============================================
// UI FUNCTIONS
// =============================================

function setupEventListeners() {
    // Recommend button
    document.getElementById('recommend-btn').addEventListener('click', () => {
        const linkedinInput = document.getElementById('linkedin-input').value.trim();
        const profileInput = document.getElementById('profile-input').value.trim();
        
        const input = linkedinInput || profileInput;
        
        if (input) {
            getRecommendations(input);
        } else {
            showMessage('⚠️ Please enter your LinkedIn URL or describe your interests.');
        }
    });

    // Enter key support
    document.getElementById('linkedin-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('recommend-btn').click();
        }
    });

    // Reset view button
    document.getElementById('reset-view').addEventListener('click', () => {
        map.flyTo({
            center: CONFIG.DAVOS_CENTER,
            zoom: CONFIG.DEFAULT_ZOOM,
            pitch: 45,
            bearing: -10,
            duration: 1500
        });
        resetMarkers();
    });

    // Toggle 3D button
    document.getElementById('toggle-3d').addEventListener('click', () => {
        const currentPitch = map.getPitch();
        map.easeTo({
            pitch: currentPitch > 0 ? 0 : 60,
            duration: 1000
        });
    });
}

function showMessage(message) {
    const messageEl = document.getElementById('ai-message');
    messageEl.innerHTML = `<p>${message}</p>`;
}

function displayRecommendations(recommendations) {
    const listEl = document.getElementById('recommendations-list');
    listEl.innerHTML = '';

    recommendations.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.style.animationDelay = `${index * 0.1}s`;
        card.onclick = () => flyToEvent(rec.id);

        card.innerHTML = `
            <div class="rec-card-header">
                <span class="rec-card-title">${rec.title}</span>
                <span class="rec-card-score">${rec.match_percentage}%</span>
            </div>
            <div class="rec-card-venue">📍 ${rec.venue}</div>
            <div class="rec-card-explanation">💡 ${rec.explanation}</div>
        `;

        listEl.appendChild(card);
    });
}

function initFilters() {
    const chipsContainer = document.getElementById('filter-chips');
    
    // FIX: Clear the container first (removes hardcoded "All Events" button)
    chipsContainer.innerHTML = '';
    
    // Add "All Events" button first
    const allChip = document.createElement('button');
    allChip.className = 'chip active';
    allChip.dataset.filter = 'all';
    allChip.textContent = 'All Events';
    allChip.onclick = () => {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        allChip.classList.add('active');
        resetMarkers();
    };
    chipsContainer.appendChild(allChip);
    
    // Get unique tracks and add chips
    const tracks = [...new Set(allEvents.map(e => e.track))].sort();
    
    tracks.forEach(track => {
        const chip = document.createElement('button');
        chip.className = 'chip';
        chip.dataset.filter = track;
        chip.textContent = track.split(' ')[0]; // Short name
        chip.onclick = () => filterByTrack(track, chip);
        chipsContainer.appendChild(chip);
    });
}

function filterByTrack(track, chipEl) {
    // Update active chip
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chipEl.classList.add('active');

    if (track === 'all') {
        resetMarkers();
        return;
    }

    // Filter markers
    Object.values(markers).forEach(({ element, event }) => {
        if (event.track === track) {
            element.style.opacity = '1';
            element.style.transform = 'scale(1.2)';
        } else {
            element.style.opacity = '0.2';
            element.style.transform = 'scale(0.7)';
        }
    });
}

function updateStats(eventCount) {
    document.getElementById('event-count').textContent = eventCount;
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.toggle('active', show);
    document.getElementById('recommend-btn').disabled = show;
}
