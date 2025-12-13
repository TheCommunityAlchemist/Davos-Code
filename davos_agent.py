#!/usr/bin/env python3
"""
DAVOS EVENT RECOMMENDATION AGENT
================================
A PhD-level semantic recommendation engine for World Economic Forum events.

Uses TF-IDF vectorization and cosine similarity for intelligent event matching.
Implements an open canvas architecture for extensibility and trackability.

Features:
- LinkedIn profile integration (paste or API)
- TF-IDF semantic matching
- Real-time recommendations

Author: WEF 2026 Hackathon Team
Version: 1.1.0
"""

import csv
import json
import logging
import re
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings

warnings.filterwarnings('ignore')

# Configure logging for trackability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Represents a single Davos event with full metadata."""
    id: str
    title: str
    description: str
    topics: List[str]
    location: str
    venue: str
    start_time: str
    end_time: str
    speakers: List[str] = field(default_factory=list)
    capacity: int = 100
    track: str = "General"
    lat: float = 46.8027
    lon: float = 9.8360
    address: str = ""
    website: str = ""
    
    def to_searchable_text(self) -> str:
        """Combine all text fields for vectorization."""
        topics_text = " ".join(self.topics)
        speakers_text = " ".join(self.speakers)
        return f"{self.title} {self.description} {topics_text} {speakers_text} {self.track}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "topics": self.topics,
            "location": self.location,
            "venue": self.venue,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "speakers": self.speakers,
            "capacity": self.capacity,
            "track": self.track,
            "lat": self.lat,
            "lon": self.lon,
            "address": self.address,
            "website": self.website
        }


@dataclass
class UserProfile:
    """Represents a user's professional profile and interests."""
    id: str
    name: str
    profession: str
    interests: List[str]
    bio: str
    attended_events: List[str] = field(default_factory=list)
    saved_events: List[str] = field(default_factory=list)
    
    def to_searchable_text(self) -> str:
        """Combine profile fields for vectorization."""
        interests_text = " ".join(self.interests)
        return f"{self.profession} {interests_text} {self.bio}"


@dataclass
class Recommendation:
    """Represents a single event recommendation with scoring details."""
    event: Event
    similarity_score: float
    match_percentage: float
    explanation: str
    matched_topics: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "event": self.event.to_dict(),
            "similarity_score": self.similarity_score,
            "match_percentage": self.match_percentage,
            "explanation": self.explanation,
            "matched_topics": self.matched_topics
        }


class LinkedInProfileParser:
    """
    LinkedIn Profile Integration
    ============================
    
    Provides multiple methods to extract professional profile data:
    
    1. PASTE MODE (Recommended): User pastes their LinkedIn "About" section
    2. API MODE: Uses official LinkedIn API (requires OAuth credentials)
    3. DEMO MODE: Simulates profile data for demonstration
    
    Note: Direct scraping of LinkedIn is against their ToS.
    This implementation uses compliant methods only.
    """
    
    # Common LinkedIn keywords to extract
    SKILL_KEYWORDS = [
        "AI", "artificial intelligence", "machine learning", "deep learning",
        "blockchain", "crypto", "DeFi", "web3",
        "climate", "sustainability", "ESG", "carbon", "renewable",
        "finance", "investment", "banking", "fintech",
        "healthcare", "biotech", "pharma", "health",
        "policy", "governance", "regulation", "compliance",
        "technology", "software", "engineering", "data",
        "leadership", "strategy", "consulting", "management",
        "energy", "oil", "gas", "solar", "wind",
        "cybersecurity", "security", "privacy", "quantum",
        "economics", "trade", "supply chain", "logistics"
    ]
    
    # Role-based interest mapping
    ROLE_MAPPINGS = {
        "ceo": ["leadership", "strategy", "governance", "stakeholder capitalism"],
        "cto": ["technology", "innovation", "AI", "digital transformation"],
        "cfo": ["finance", "investment", "risk management", "capital markets"],
        "scientist": ["research", "innovation", "data", "methodology"],
        "engineer": ["technology", "systems", "infrastructure", "innovation"],
        "policy": ["governance", "regulation", "international cooperation", "policy"],
        "investor": ["finance", "growth", "markets", "returns", "ESG"],
        "professor": ["research", "education", "academic", "thought leadership"],
        "doctor": ["healthcare", "medical", "patient outcomes", "health systems"],
        "founder": ["entrepreneurship", "innovation", "startups", "disruption"],
        "director": ["strategy", "leadership", "governance", "operations"],
        "analyst": ["data", "research", "insights", "trends"],
        "consultant": ["strategy", "advisory", "transformation", "solutions"]
    }
    
    @staticmethod
    def is_linkedin_url(text: str) -> bool:
        """Check if input is a LinkedIn URL."""
        linkedin_patterns = [
            r'linkedin\.com/in/[\w-]+',
            r'linkedin\.com/pub/[\w-]+',
            r'www\.linkedin\.com/in/[\w-]+'
        ]
        return any(re.search(pattern, text.lower()) for pattern in linkedin_patterns)
    
    @staticmethod
    def extract_username_from_url(url: str) -> Optional[str]:
        """Extract LinkedIn username from URL."""
        match = re.search(r'linkedin\.com/in/([\w-]+)', url)
        if match:
            return match.group(1)
        return None
    
    @classmethod
    def parse_pasted_profile(cls, text: str) -> Dict:
        """
        Parse a pasted LinkedIn profile text.
        
        Users can paste their:
        - About section
        - Headline
        - Experience descriptions
        - Skills list
        """
        profile = {
            "raw_text": text,
            "detected_skills": [],
            "detected_roles": [],
            "interests": [],
            "searchable_text": text
        }
        
        text_lower = text.lower()
        
        # Extract skills
        for skill in cls.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                profile["detected_skills"].append(skill)
        
        # Detect roles and map to interests
        for role, interests in cls.ROLE_MAPPINGS.items():
            if role in text_lower:
                profile["detected_roles"].append(role)
                profile["interests"].extend(interests)
        
        # Remove duplicates
        profile["interests"] = list(set(profile["interests"]))
        profile["detected_skills"] = list(set(profile["detected_skills"]))
        
        return profile
    
    @classmethod
    def generate_demo_profile(cls, linkedin_url: str) -> Dict:
        """
        Generate a demo profile based on LinkedIn URL patterns.
        
        This simulates what the API would return for demonstration.
        In production, replace with actual LinkedIn API call.
        """
        username = cls.extract_username_from_url(linkedin_url) or "demo-user"
        
        # Generate contextual demo based on username hints
        demo_profiles = {
            "default": {
                "name": username.replace("-", " ").title(),
                "headline": "Senior Professional | Innovation & Strategy",
                "about": """
                Experienced leader focused on driving innovation and sustainable growth.
                Passionate about technology, climate action, and global cooperation.
                Regular speaker at international forums on digital transformation.
                Expertise in AI, blockchain, and sustainable finance.
                """,
                "skills": ["Strategy", "Innovation", "Leadership", "AI", "Sustainability"],
                "interests": ["Technology", "Climate", "Finance", "Policy"]
            }
        }
        
        # Check for keywords in username
        profile = demo_profiles["default"].copy()
        
        if any(k in username.lower() for k in ["climate", "green", "sustain", "eco"]):
            profile["about"] += " Deep focus on climate tech and environmental sustainability."
            profile["skills"].extend(["Climate Finance", "ESG", "Carbon Markets"])
            profile["interests"].extend(["Climate Action", "Renewable Energy"])
        
        if any(k in username.lower() for k in ["tech", "ai", "data", "digital"]):
            profile["about"] += " Pioneer in AI and digital transformation initiatives."
            profile["skills"].extend(["Machine Learning", "Data Science", "Digital Strategy"])
            profile["interests"].extend(["AI Governance", "Digital Innovation"])
        
        if any(k in username.lower() for k in ["health", "med", "bio", "pharma"]):
            profile["about"] += " Committed to advancing global health and healthcare innovation."
            profile["skills"].extend(["Healthcare Innovation", "Biotech", "Health Policy"])
            profile["interests"].extend(["Global Health", "Medical AI"])
        
        if any(k in username.lower() for k in ["finance", "invest", "capital", "bank"]):
            profile["about"] += " Expert in global finance and investment strategies."
            profile["skills"].extend(["Investment", "Capital Markets", "Financial Strategy"])
            profile["interests"].extend(["Sustainable Finance", "DeFi"])
        
        profile["searchable_text"] = f"""
        {profile['headline']}
        {profile['about']}
        Skills: {', '.join(profile['skills'])}
        Interests: {', '.join(profile['interests'])}
        """
        
        return profile
    
    @classmethod
    def fetch_via_api(cls, linkedin_url: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch profile via LinkedIn API or third-party service.
        
        Supported services:
        - LinkedIn Marketing API (requires OAuth)
        - Proxycurl (paid service)
        - RocketReach (paid service)
        
        Set LINKEDIN_API_KEY environment variable or pass api_key.
        """
        import os
        
        api_key = api_key or os.environ.get("LINKEDIN_API_KEY")
        
        if not api_key:
            logger.warning("No LinkedIn API key configured. Using demo mode.")
            return None
        
        # Example: Proxycurl API integration
        # In production, uncomment and configure:
        #
        # try:
        #     headers = {"Authorization": f"Bearer {api_key}"}
        #     url = f"https://nubela.co/proxycurl/api/v2/linkedin?url={linkedin_url}"
        #     req = urllib.request.Request(url, headers=headers)
        #     with urllib.request.urlopen(req) as response:
        #         data = json.loads(response.read().decode())
        #         return {
        #             "name": data.get("full_name", ""),
        #             "headline": data.get("headline", ""),
        #             "about": data.get("summary", ""),
        #             "skills": [s["name"] for s in data.get("skills", [])],
        #             "searchable_text": f"{data.get('headline', '')} {data.get('summary', '')}"
        #         }
        # except Exception as e:
        #     logger.error(f"LinkedIn API error: {e}")
        #     return None
        
        logger.info("LinkedIn API integration placeholder - using demo mode")
        return None
    
    @classmethod
    def get_profile(cls, input_text: str, api_key: Optional[str] = None) -> Dict:
        """
        Main entry point - intelligently handles different input types.
        
        Args:
            input_text: LinkedIn URL, pasted profile text, or natural description
            api_key: Optional API key for LinkedIn services
            
        Returns:
            Parsed profile dictionary with searchable_text for recommendations
        """
        # Check if it's a LinkedIn URL
        if cls.is_linkedin_url(input_text):
            logger.info(f"Detected LinkedIn URL: {input_text}")
            
            # Try API first
            api_result = cls.fetch_via_api(input_text, api_key)
            if api_result:
                return api_result
            
            # Fall back to demo mode
            logger.info("Using demo mode for LinkedIn URL")
            return cls.generate_demo_profile(input_text)
        
        # Otherwise, treat as pasted profile or direct text
        parsed = cls.parse_pasted_profile(input_text)
        
        if parsed["detected_skills"] or parsed["detected_roles"]:
            logger.info(f"Parsed profile - Skills: {parsed['detected_skills']}, Roles: {parsed['detected_roles']}")
        
        return parsed


class DavosRecommendationAgent:
    """
    PhD-Level Semantic Recommendation Engine for Davos Events
    ==========================================================
    
    This agent implements a sophisticated information retrieval approach using:
    1. TF-IDF (Term Frequency-Inverse Document Frequency) vectorization
    2. Cosine similarity for semantic matching
    3. Topic overlap analysis for explainability
    4. Dynamic re-ranking based on user feedback
    
    Architecture follows Open Canvas principles:
    - Modular components for extensibility
    - Event-driven updates for real-time tracking
    - Stateless core with optional persistence layer
    
    Mathematical Foundation:
    ------------------------
    TF-IDF(t, d, D) = TF(t, d) × IDF(t, D)
    where:
        TF(t, d) = frequency of term t in document d
        IDF(t, D) = log(N / |{d ∈ D : t ∈ d}|)
    
    Cosine Similarity:
        sim(u, e) = (u · e) / (||u|| × ||e||)
    where u is user vector and e is event vector
    """
    
    def __init__(self, events_file: Optional[str] = None):
        """Initialize the recommendation agent."""
        self.events: List[Event] = []
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            max_features=5000,
            min_df=1,
            max_df=0.95,
            sublinear_tf=True  # Apply sublinear TF scaling
        )
        self.event_vectors = None
        self.is_fitted = False
        self.navigation_history: List[Dict] = []
        
        if events_file:
            self.load_events(events_file)
        
        logger.info("DavosRecommendationAgent initialized")
    
    def load_events(self, filepath: str) -> None:
        """Load events from CSV file."""
        logger.info(f"Loading events from {filepath}")
        self.events = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    event = Event(
                        id=row.get('id', ''),
                        title=row.get('title', ''),
                        description=row.get('description', ''),
                        topics=row.get('topics', '').split(';'),
                        location=row.get('location', 'Davos Congress Centre'),
                        venue=row.get('venue', 'Main Hall'),
                        start_time=row.get('start_time', ''),
                        end_time=row.get('end_time', ''),
                        speakers=row.get('speakers', '').split(';') if row.get('speakers') else [],
                        capacity=int(row.get('capacity', 100)),
                        track=row.get('track', 'General'),
                        lat=float(row.get('lat', 46.8027)),
                        lon=float(row.get('lon', 9.8360)),
                        address=row.get('address', ''),
                        website=row.get('website', '')
                    )
                    self.events.append(event)
            
            self._fit_vectorizer()
            logger.info(f"Loaded {len(self.events)} events successfully")
            
        except FileNotFoundError:
            logger.warning(f"Events file not found: {filepath}")
            self._load_sample_events()
    
    def _load_sample_events(self) -> None:
        """Load sample events for demonstration."""
        logger.info("Loading sample events for demonstration")
        sample_events = [
            Event(
                id="WEF2026-001",
                title="AI Governance for Global Good",
                description="Exploring frameworks for responsible AI development and deployment across borders. Discussion on international cooperation for AI safety standards.",
                topics=["Artificial Intelligence", "Governance", "Technology Policy", "Global Cooperation"],
                location="Congress Centre",
                venue="Jakobshorn Hall",
                start_time="2026-01-20 09:00",
                end_time="2026-01-20 10:30",
                speakers=["Dr. Fei-Fei Li", "Yoshua Bengio", "Margrethe Vestager"],
                capacity=300,
                track="Technology & Innovation",
                lat=46.8027,
                lon=9.8360
            ),
            Event(
                id="WEF2026-002",
                title="Climate Finance Revolution",
                description="Mobilizing trillions for climate action. Innovative financial instruments, carbon markets, and green bonds for sustainable development.",
                topics=["Climate Change", "Finance", "Sustainability", "Green Bonds", "Carbon Markets"],
                location="Congress Centre",
                venue="Parsenn Hall",
                start_time="2026-01-20 11:00",
                end_time="2026-01-20 12:30",
                speakers=["Mark Carney", "Christiana Figueres", "Larry Fink"],
                capacity=250,
                track="Climate & Sustainability",
                lat=46.8030,
                lon=9.8365
            ),
            Event(
                id="WEF2026-003",
                title="The Future of Work: Human-AI Collaboration",
                description="Reimagining the workforce in an age of automation. Skills development, education reform, and creating meaningful employment.",
                topics=["Future of Work", "Automation", "Education", "Skills Development", "Human Capital"],
                location="Congress Centre",
                venue="Flüela Hall",
                start_time="2026-01-20 14:00",
                end_time="2026-01-20 15:30",
                speakers=["Satya Nadella", "Ginni Rometty", "Andrew Ng"],
                capacity=400,
                track="Economy & Society",
                lat=46.8025,
                lon=9.8355
            ),
            Event(
                id="WEF2026-004",
                title="Blockchain and Decentralized Finance",
                description="The transformation of global financial systems through blockchain technology. CBDCs, DeFi protocols, and regulatory frameworks.",
                topics=["Blockchain", "DeFi", "Central Bank Digital Currency", "Financial Innovation", "Regulation"],
                location="Steigenberger Grandhotel Belvédère",
                venue="Bellevue Suite",
                start_time="2026-01-20 16:00",
                end_time="2026-01-20 17:30",
                speakers=["Vitalik Buterin", "Christine Lagarde", "Brian Armstrong"],
                capacity=150,
                track="Finance & Technology",
                lat=46.8089,
                lon=9.8376
            ),
            Event(
                id="WEF2026-005",
                title="Global Health Resilience",
                description="Building pandemic-proof healthcare systems. Lessons from COVID-19 for future health security and equitable vaccine distribution.",
                topics=["Global Health", "Pandemic Preparedness", "Healthcare Systems", "Vaccine Equity"],
                location="Congress Centre",
                venue="Sanada Hall",
                start_time="2026-01-21 09:00",
                end_time="2026-01-21 10:30",
                speakers=["Dr. Tedros Adhanom", "Bill Gates", "Dr. Anthony Fauci"],
                capacity=350,
                track="Health & Wellbeing",
                lat=46.8028,
                lon=9.8362
            ),
            Event(
                id="WEF2026-006",
                title="Geopolitics of Energy Transition",
                description="Navigating the shift from fossil fuels to renewables. Energy security, critical minerals, and international power dynamics.",
                topics=["Energy Transition", "Geopolitics", "Renewable Energy", "Critical Minerals", "Energy Security"],
                location="Congress Centre",
                venue="Wisshorn Hall",
                start_time="2026-01-21 11:00",
                end_time="2026-01-21 12:30",
                speakers=["Fatih Birol", "Jennifer Granholm", "Sultan Al Jaber"],
                capacity=280,
                track="Energy & Environment",
                lat=46.8026,
                lon=9.8358
            ),
            Event(
                id="WEF2026-007",
                title="Cybersecurity in the Quantum Age",
                description="Preparing for quantum computing threats to current encryption. Post-quantum cryptography and critical infrastructure protection.",
                topics=["Cybersecurity", "Quantum Computing", "Cryptography", "Critical Infrastructure"],
                location="Hotel & Spa & Waldhaus Davos",
                venue="Alpine Conference Room",
                start_time="2026-01-21 14:00",
                end_time="2026-01-21 15:30",
                speakers=["Sundar Pichai", "Jen Easterly", "Meredith Whittaker"],
                capacity=120,
                track="Technology & Security",
                lat=46.7942,
                lon=9.8156
            ),
            Event(
                id="WEF2026-008",
                title="Nature-Based Solutions for Climate",
                description="Harnessing ecosystems for carbon sequestration. Forest conservation, ocean restoration, and biodiversity credits.",
                topics=["Nature-Based Solutions", "Carbon Sequestration", "Biodiversity", "Conservation", "Ecosystem Restoration"],
                location="Congress Centre",
                venue="Dischma Hall",
                start_time="2026-01-21 16:00",
                end_time="2026-01-21 17:30",
                speakers=["Jane Goodall", "David Attenborough", "Hindou Ibrahim"],
                capacity=320,
                track="Climate & Sustainability",
                lat=46.8029,
                lon=9.8363
            ),
            Event(
                id="WEF2026-009",
                title="The Metaverse Economy",
                description="Virtual worlds and their economic implications. Digital assets, virtual real estate, and the future of digital commerce.",
                topics=["Metaverse", "Virtual Reality", "Digital Economy", "NFTs", "Digital Commerce"],
                location="Steigenberger Grandhotel Belvédère",
                venue="Crystal Ballroom",
                start_time="2026-01-22 09:00",
                end_time="2026-01-22 10:30",
                speakers=["Tim Sweeney", "Mark Zuckerberg", "Jensen Huang"],
                capacity=200,
                track="Technology & Innovation",
                lat=46.8091,
                lon=9.8378
            ),
            Event(
                id="WEF2026-010",
                title="Inclusive Growth and Inequality",
                description="Addressing wealth disparity in a changing economy. Social mobility, universal basic income, and stakeholder capitalism.",
                topics=["Inequality", "Inclusive Growth", "Social Policy", "Stakeholder Capitalism", "UBI"],
                location="Congress Centre",
                venue="Promenade Hall",
                start_time="2026-01-22 11:00",
                end_time="2026-01-22 12:30",
                speakers=["Esther Duflo", "Ray Dalio", "Klaus Schwab"],
                capacity=380,
                track="Economy & Society",
                lat=46.8024,
                lon=9.8352
            ),
            Event(
                id="WEF2026-011",
                title="Space Economy Frontiers",
                description="Commercial space exploration and its economic potential. Satellite infrastructure, lunar mining, and space tourism.",
                topics=["Space Economy", "Commercial Space", "Satellite Technology", "Space Tourism"],
                location="Congress Centre",
                venue="Schwarzhorn Hall",
                start_time="2026-01-22 14:00",
                end_time="2026-01-22 15:30",
                speakers=["Elon Musk", "Peter Beck", "Gwynne Shotwell"],
                capacity=450,
                track="Technology & Innovation",
                lat=46.8031,
                lon=9.8367
            ),
            Event(
                id="WEF2026-012",
                title="Food Systems Transformation",
                description="Feeding 10 billion sustainably. Agricultural innovation, alternative proteins, and reducing food waste.",
                topics=["Food Security", "Sustainable Agriculture", "Alternative Proteins", "Food Waste", "AgriTech"],
                location="Hotel & Spa & Waldhaus Davos",
                venue="Garden Terrace",
                start_time="2026-01-22 16:00",
                end_time="2026-01-22 17:30",
                speakers=["Pat Brown", "David Kenny", "Ertharin Cousin"],
                capacity=180,
                track="Climate & Sustainability",
                lat=46.7944,
                lon=9.8158
            )
        ]
        
        self.events = sample_events
        self._fit_vectorizer()
        logger.info(f"Loaded {len(self.events)} sample events")
    
    def _fit_vectorizer(self) -> None:
        """Fit the TF-IDF vectorizer on all events."""
        if not self.events:
            logger.warning("No events to vectorize")
            return
        
        event_texts = [event.to_searchable_text() for event in self.events]
        self.event_vectors = self.vectorizer.fit_transform(event_texts)
        self.is_fitted = True
        logger.info(f"Vectorizer fitted with vocabulary size: {len(self.vectorizer.vocabulary_)}")
    
    def recommend(
        self,
        user_profile: str,
        top_k: int = 3,
        exclude_ids: Optional[List[str]] = None,
        use_linkedin: bool = True
    ) -> List[Recommendation]:
        """
        Generate event recommendations based on user profile.
        
        Parameters:
        -----------
        user_profile : str
            Natural language description, LinkedIn URL, or pasted LinkedIn profile
        top_k : int
            Number of recommendations to return
        exclude_ids : List[str], optional
            Event IDs to exclude from recommendations
        use_linkedin : bool
            Whether to parse LinkedIn URLs/profiles (default True)
            
        Returns:
        --------
        List[Recommendation]
            Ordered list of recommendations with scores and explanations
        """
        if not self.is_fitted:
            self._load_sample_events()
        
        # Parse LinkedIn profile if applicable
        searchable_text = user_profile
        linkedin_data = None
        
        if use_linkedin:
            linkedin_data = LinkedInProfileParser.get_profile(user_profile)
            searchable_text = linkedin_data.get("searchable_text", user_profile)
            
            if LinkedInProfileParser.is_linkedin_url(user_profile):
                logger.info(f"Processed LinkedIn URL - using enriched profile data")
        
        logger.info(f"Generating recommendations for profile: {searchable_text[:50]}...")
        
        # Vectorize user profile
        user_vector = self.vectorizer.transform([searchable_text])
        
        # Compute cosine similarity with all events
        similarities = cosine_similarity(user_vector, self.event_vectors).flatten()
        
        # Create recommendations with explanations
        recommendations = []
        exclude_ids = exclude_ids or []
        
        # Get indices sorted by similarity (descending)
        sorted_indices = np.argsort(similarities)[::-1]
        
        for idx in sorted_indices:
            event = self.events[idx]
            
            if event.id in exclude_ids:
                continue
            
            similarity = similarities[idx]
            
            if similarity <= 0:
                continue
            
            # Find matched topics
            user_terms = set(user_profile.lower().split())
            matched_topics = [
                topic for topic in event.topics
                if any(term in topic.lower() for term in user_terms)
            ]
            
            # Generate explanation
            explanation = self._generate_explanation(
                event, similarity, matched_topics, user_profile
            )
            
            recommendation = Recommendation(
                event=event,
                similarity_score=float(similarity),
                match_percentage=round(float(similarity) * 100, 1),
                explanation=explanation,
                matched_topics=matched_topics
            )
            recommendations.append(recommendation)
            
            if len(recommendations) >= top_k:
                break
        
        # Track navigation
        self._track_navigation("recommend", {
            "profile": user_profile[:100],
            "num_recommendations": len(recommendations)
        })
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _generate_explanation(
        self,
        event: Event,
        similarity: float,
        matched_topics: List[str],
        user_profile: str
    ) -> str:
        """Generate human-readable explanation for recommendation."""
        explanations = []
        
        # Similarity-based explanation
        if similarity > 0.5:
            explanations.append(f"Highly relevant to your interests")
        elif similarity > 0.3:
            explanations.append(f"Strong alignment with your profile")
        elif similarity > 0.1:
            explanations.append(f"Moderate connection to your interests")
        else:
            explanations.append(f"Some overlap with your interests")
        
        # Topic-based explanation
        if matched_topics:
            topics_str = ", ".join(matched_topics[:3])
            explanations.append(f"Covers: {topics_str}")
        
        # Speaker highlight
        if event.speakers:
            explanations.append(f"Featuring: {event.speakers[0]}")
        
        return " | ".join(explanations)
    
    def search_events(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[Event, float]]:
        """
        Search events by keyword/semantic query.
        
        Returns list of (event, score) tuples.
        """
        if not self.is_fitted:
            self._load_sample_events()
        
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.event_vectors).flatten()
        
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [
            (self.events[idx], float(similarities[idx]))
            for idx in sorted_indices
            if similarities[idx] > 0
        ]
        
        self._track_navigation("search", {"query": query, "results": len(results)})
        
        return results
    
    def get_events_by_track(self, track: str) -> List[Event]:
        """Get all events in a specific track."""
        return [e for e in self.events if e.track.lower() == track.lower()]
    
    def get_events_by_location(self, location: str) -> List[Event]:
        """Get all events at a specific location."""
        return [e for e in self.events if location.lower() in e.location.lower()]
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get a specific event by ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def _track_navigation(self, action: str, details: Dict) -> None:
        """Track user navigation for analytics."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.navigation_history.append(entry)
        logger.debug(f"Navigation tracked: {action}")
    
    def get_navigation_history(self) -> List[Dict]:
        """Return navigation history for analytics."""
        return self.navigation_history.copy()
    
    def export_recommendations_json(
        self,
        recommendations: List[Recommendation]
    ) -> str:
        """Export recommendations as JSON for frontend consumption."""
        return json.dumps(
            [rec.to_dict() for rec in recommendations],
            indent=2,
            default=str
        )
    
    def get_all_events_json(self) -> str:
        """Export all events as JSON for map visualization."""
        return json.dumps(
            [event.to_dict() for event in self.events],
            indent=2,
            default=str
        )
    
    def get_tracks(self) -> List[str]:
        """Get list of unique tracks."""
        return list(set(e.track for e in self.events))
    
    def get_venues(self) -> List[str]:
        """Get list of unique venues."""
        return list(set(e.venue for e in self.events))


def interactive_cli():
    """
    Interactive CLI for the Davos Recommendation Agent.
    Provides real-time recommendations based on user input.
    Supports LinkedIn URL integration.
    """
    print("\n" + "="*70)
    print("   🏔️  DAVOS 2026 - INTELLIGENT EVENT RECOMMENDATION SYSTEM  🏔️")
    print("="*70)
    print("\nWelcome to the World Economic Forum Event Navigator!")
    print("Powered by TF-IDF semantic matching & cosine similarity\n")
    
    # Initialize agent
    agent = DavosRecommendationAgent()
    
    print("=" * 70)
    print("Available Commands:")
    print("  - Enter your profile description for personalized recommendations")
    print("  - Paste your LinkedIn URL (e.g., linkedin.com/in/yourname)")
    print("  - Paste your LinkedIn 'About' section for best results")
    print("  - Type 'search <query>' to search for specific topics")
    print("  - Type 'tracks' to see all event tracks")
    print("  - Type 'all' to list all events")
    print("  - Type 'export' to export events as JSON")
    print("  - Type 'history' to see your navigation history")
    print("  - Type 'quit' to exit")
    print("=" * 70)
    print("\n💡 TIP: For best results, paste your LinkedIn URL or About section!")
    
    while True:
        try:
            user_input = input("\n🎯 Enter your profile or command: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\n✨ Thank you for using the Davos Event Navigator! See you in Davos! ✨\n")
                break
            
            if user_input.lower() == 'tracks':
                tracks = agent.get_tracks()
                print("\n📋 Available Tracks:")
                for track in sorted(tracks):
                    count = len(agent.get_events_by_track(track))
                    print(f"   • {track} ({count} events)")
                continue
            
            if user_input.lower() == 'all':
                print("\n📅 All Events:")
                for event in agent.events:
                    print(f"   [{event.id}] {event.title}")
                    print(f"       📍 {event.venue} | 🕐 {event.start_time}")
                continue
            
            if user_input.lower() == 'export':
                json_data = agent.get_all_events_json()
                with open('events_export.json', 'w') as f:
                    f.write(json_data)
                print("\n✅ Events exported to events_export.json")
                continue
            
            if user_input.lower() == 'history':
                history = agent.get_navigation_history()
                print(f"\n📊 Navigation History ({len(history)} entries):")
                for entry in history[-5:]:
                    print(f"   {entry['timestamp']}: {entry['action']}")
                continue
            
            if user_input.lower().startswith('search '):
                query = user_input[7:]
                results = agent.search_events(query, top_k=5)
                print(f"\n🔍 Search Results for '{query}':")
                for event, score in results:
                    print(f"\n   📌 {event.title}")
                    print(f"      Score: {score:.1%} | Track: {event.track}")
                    print(f"      📍 {event.venue}")
                continue
            
            # Check if LinkedIn URL was provided
            is_linkedin = LinkedInProfileParser.is_linkedin_url(user_input)
            
            if is_linkedin:
                print("\n🔗 LinkedIn URL detected! Analyzing your professional profile...")
                profile_data = LinkedInProfileParser.get_profile(user_input)
                
                if profile_data.get("name"):
                    print(f"   👤 Profile: {profile_data.get('name', 'Unknown')}")
                if profile_data.get("headline"):
                    print(f"   💼 {profile_data.get('headline', '')}")
                if profile_data.get("skills"):
                    print(f"   🎯 Skills: {', '.join(profile_data.get('skills', [])[:5])}")
                if profile_data.get("detected_skills"):
                    print(f"   🔍 Detected: {', '.join(profile_data.get('detected_skills', [])[:5])}")
                print()
            
            # Generate recommendations
            recommendations = agent.recommend(user_input, top_k=5)
            
            if not recommendations:
                print("\n❌ No matching events found. Try a different description.")
                continue
            
            source = "LinkedIn Profile" if is_linkedin else "Your Profile"
            print(f"\n🎯 Top {len(recommendations)} Recommended Events (based on {source}):\n")
            print("-" * 70)
            
            for i, rec in enumerate(recommendations, 1):
                event = rec.event
                print(f"\n{i}. 🏆 {event.title}")
                print(f"   Match: {rec.match_percentage}% | Track: {event.track}")
                print(f"   📍 {event.venue} ({event.location})")
                print(f"   🕐 {event.start_time} - {event.end_time}")
                print(f"   💡 {rec.explanation}")
                if event.speakers:
                    print(f"   🎤 Speakers: {', '.join(event.speakers[:3])}")
                print(f"   📝 {event.description[:150]}...")
                print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\n✨ Goodbye! See you in Davos! ✨\n")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n⚠️ An error occurred: {e}")


if __name__ == "__main__":
    interactive_cli()

