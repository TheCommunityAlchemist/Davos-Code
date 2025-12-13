# DAVOS 2026 - PhD-Level Event Recommendation System
## Technical Specification & Implementation Guide

---

## 📋 Executive Summary

This document provides a comprehensive PhD-level technical specification for the **Davos Intelligent Event Navigation System (DIENS)** — a semantic recommendation engine designed for the World Economic Forum Annual Meeting 2026. The system leverages advanced Natural Language Processing (NLP) techniques to match attendee profiles with relevant events through an open canvas architecture.

---

## 🎯 Project Objectives

1. **Intelligent Matching**: Deploy TF-IDF vectorization with cosine similarity for semantic event-user matching
2. **Real-time Navigation**: Provide smooth, trackable navigation through the event landscape
3. **Open Canvas Architecture**: Enable extensibility, modularity, and integration with external systems
4. **Explainable Recommendations**: Deliver transparent, interpretable recommendation explanations

---

## 🧮 Mathematical Foundation

### 1. TF-IDF (Term Frequency-Inverse Document Frequency)

The TF-IDF weighting scheme combines term frequency with inverse document frequency to produce a composite weight:

$$
\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)
$$

Where:
- **Term Frequency (TF)**: Measures how frequently a term occurs in a document
  $$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$
  
- **Inverse Document Frequency (IDF)**: Measures how important a term is across the corpus
  $$\text{IDF}(t, D) = \log\left(\frac{N}{|\{d \in D : t \in d\}|}\right)$$

Our implementation uses **sublinear TF scaling**:
$$\text{TF}_{sub}(t, d) = 1 + \log(f_{t,d}) \text{ if } f_{t,d} > 0$$

### 2. Cosine Similarity

For computing similarity between user profile vector $\vec{u}$ and event vector $\vec{e}$:

$$
\text{sim}(\vec{u}, \vec{e}) = \frac{\vec{u} \cdot \vec{e}}{||\vec{u}|| \times ||\vec{e}||} = \frac{\sum_{i=1}^{n} u_i \times e_i}{\sqrt{\sum_{i=1}^{n} u_i^2} \times \sqrt{\sum_{i=1}^{n} e_i^2}}
$$

Properties:
- Range: [-1, 1] for general vectors, [0, 1] for TF-IDF vectors
- Scale-invariant: Focuses on orientation, not magnitude
- Computational complexity: O(n) where n = vocabulary size

### 3. N-gram Feature Engineering

We employ **bi-gram features** (n=1,2) to capture phrase-level semantics:

```
"climate change policy" → ["climate", "change", "policy", "climate_change", "change_policy"]
```

This enables matching on:
- Single concepts: "blockchain", "sustainability"
- Compound concepts: "climate_finance", "AI_governance"

---

## 🏗️ System Architecture

### Open Canvas Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Interactive  │  │   REST API   │  │  Real-time WebSocket    │  │
│  │     CLI      │  │   /api/v1    │  │      Connections        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              DavosRecommendationAgent                       │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │    │
│  │  │ Vectorizer  │ │ Recommender │ │  Navigation Tracker   │ │    │
│  │  │  (TF-IDF)   │ │   Engine    │ │                       │ │    │
│  │  └─────────────┘ └─────────────┘ └───────────────────────┘ │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │    Events    │  │    Users     │  │    Navigation History   │  │
│  │  (CSV/JSON)  │  │   Profiles   │  │        (In-memory)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Specifications

#### 1. Vectorizer Module
- **Library**: scikit-learn TfidfVectorizer
- **Parameters**:
  - `ngram_range`: (1, 2) — unigrams and bigrams
  - `max_features`: 5000 — vocabulary cap
  - `min_df`: 1 — minimum document frequency
  - `max_df`: 0.95 — maximum document frequency (filter common words)
  - `sublinear_tf`: True — logarithmic TF scaling
  - `stop_words`: 'english' — remove common words

#### 2. Recommender Engine
- **Input**: User profile text (natural language)
- **Output**: Ranked list of (Event, Score, Explanation)
- **Algorithm**:
  1. Transform user profile to TF-IDF vector
  2. Compute cosine similarity with all event vectors
  3. Rank by similarity score (descending)
  4. Generate explanation for top-k results
  5. Return recommendations with metadata

#### 3. Navigation Tracker
- **Purpose**: Track user interactions for analytics and personalization
- **Data Structure**:
  ```python
  {
      "timestamp": ISO8601,
      "action": "recommend|search|view|save",
      "details": {...}
  }
  ```

---

## 📊 Data Model

### Event Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique event identifier (WEF2026-XXX) |
| `title` | string | Event title (max 100 chars) |
| `description` | string | Full event description |
| `topics` | string[] | Semicolon-separated topic tags |
| `location` | string | Venue name |
| `venue` | string | Specific room/hall |
| `start_time` | datetime | ISO8601 start timestamp |
| `end_time` | datetime | ISO8601 end timestamp |
| `speakers` | string[] | Semicolon-separated speaker names |
| `capacity` | int | Maximum attendees |
| `track` | string | Event track/category |
| `lat` | float | Venue latitude (for map) |
| `lon` | float | Venue longitude (for map) |

### User Profile Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique user identifier |
| `name` | string | Display name |
| `profession` | string | Job title/role |
| `interests` | string[] | Topics of interest |
| `bio` | string | Professional bio |
| `attended_events` | string[] | List of event IDs attended |
| `saved_events` | string[] | List of saved event IDs |

### Recommendation Schema

| Field | Type | Description |
|-------|------|-------------|
| `event` | Event | Full event object |
| `similarity_score` | float | Raw cosine similarity [0,1] |
| `match_percentage` | float | Score as percentage |
| `explanation` | string | Human-readable reason |
| `matched_topics` | string[] | Topics matching user profile |

---

## 🚀 Implementation Guide

### Quick Start

```bash
# 1. Clone or navigate to project
cd "WEF 2026"

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the interactive CLI
python davos_agent.py
```

### Example Usage

```python
from davos_agent import DavosRecommendationAgent

# Initialize agent with event data
agent = DavosRecommendationAgent("davos_events.csv")

# Get personalized recommendations
profile = """
I'm a climate scientist interested in blockchain applications 
for carbon tracking. I work on policy frameworks for 
international cooperation on environmental issues.
"""

recommendations = agent.recommend(profile, top_k=5)

for rec in recommendations:
    print(f"{rec.event.title}: {rec.match_percentage}%")
    print(f"  → {rec.explanation}")
```

### API Endpoints (for Flask deployment)

```python
# GET /api/v1/recommendations
# Query params: profile (string), top_k (int)
# Returns: JSON array of recommendations

# GET /api/v1/events
# Returns: JSON array of all events

# GET /api/v1/events/<id>
# Returns: Single event by ID

# GET /api/v1/search
# Query params: q (string), limit (int)
# Returns: Search results with scores

# GET /api/v1/tracks
# Returns: List of unique tracks

# GET /api/v1/analytics/navigation
# Returns: Navigation history for tracking
```

---

## 🗺️ Map Visualization

The system includes an interactive map (`davos_map.html`) with:

### Features
- **Leaflet.js** map with Davos venue markers
- **Real-time filtering** by track, date, and search
- **Event clustering** for dense areas
- **Click-through details** with full event information
- **Responsive design** for mobile and desktop

### Venue Coordinates (Davos, Switzerland)

| Venue | Latitude | Longitude |
|-------|----------|-----------|
| Congress Centre | 46.8027 | 9.8360 |
| Steigenberger Grandhotel | 46.8089 | 9.8376 |
| Hotel Waldhaus | 46.7942 | 9.8156 |

---

## 📈 Performance Considerations

### Computational Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| TF-IDF Fit | O(n × m) | O(n × v) |
| Transform | O(m × v) | O(v) |
| Cosine Similarity | O(k × v) | O(k) |
| Top-k Selection | O(k log k) | O(k) |

Where:
- n = number of events
- m = average tokens per event
- v = vocabulary size
- k = number of recommendations

### Scalability

For large-scale deployment (10,000+ events):

1. **Approximate Nearest Neighbors**: Replace cosine similarity with FAISS or Annoy
2. **Caching**: Pre-compute common profile patterns
3. **Batch Processing**: Vectorize new events in batches
4. **Horizontal Scaling**: Stateless design enables load balancing

---

## 🔮 Future Enhancements

### Phase 2: Transformer Embeddings

```python
from sentence_transformers import SentenceTransformer

# Replace TF-IDF with BERT embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
event_embeddings = model.encode([e.to_searchable_text() for e in events])
```

### Phase 3: Collaborative Filtering

Incorporate user-user and item-item similarity:

$$
\hat{r}_{ui} = \frac{\sum_{j \in N_i^k} \text{sim}(i, j) \times r_{uj}}{\sum_{j \in N_i^k} |\text{sim}(i, j)|}
$$

### Phase 4: Real-time Learning

- Online learning with SGD updates
- Click-through rate optimization
- A/B testing framework
- Multi-armed bandit for exploration/exploitation

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_vectorizer_initialization():
    agent = DavosRecommendationAgent()
    assert agent.is_fitted == True
    assert len(agent.events) > 0

def test_recommendation_count():
    agent = DavosRecommendationAgent()
    recs = agent.recommend("climate finance", top_k=3)
    assert len(recs) <= 3
    assert all(r.similarity_score >= 0 for r in recs)

def test_similarity_range():
    agent = DavosRecommendationAgent()
    recs = agent.recommend("AI governance policy")
    for rec in recs:
        assert 0 <= rec.similarity_score <= 1
```

### Integration Tests

```python
def test_full_workflow():
    # Load events
    agent = DavosRecommendationAgent("davos_events.csv")
    
    # Generate recommendations
    profile = "Healthcare innovation and AI"
    recs = agent.recommend(profile)
    
    # Verify recommendations are relevant
    health_related = any("Health" in r.event.track for r in recs)
    assert health_related
```

---

## 📝 Deployment Checklist

- [ ] Environment variables configured
- [ ] Event data loaded and validated
- [ ] TF-IDF model fitted
- [ ] API endpoints tested
- [ ] Map visualization connected
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Rate limiting enabled
- [ ] CORS configured
- [ ] SSL certificate installed

---

## 📚 References

1. Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513-523.

2. Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press.

3. Ramos, J. (2003). Using TF-IDF to determine word relevance in document queries. *Proceedings of the First Instructional Conference on Machine Learning*.

4. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *EMNLP 2019*.

---

## 👥 Contributors

- WEF 2026 Hackathon Team
- Open Canvas Architecture Group

---

*Document Version: 1.0.0 | Last Updated: January 2026*

