# 🏔️ DAVOS 2026 - Intelligent Event Navigator

A PhD-level semantic recommendation system for World Economic Forum events, featuring TF-IDF vectorization, cosine similarity matching, and an interactive open canvas map architecture.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

```bash
# Navigate to project directory
cd "WEF 2026"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the interactive CLI
python davos_agent.py
```

### Launch Interactive Map
Simply open `davos_map.html` in any modern browser:

```bash
open davos_map.html  # macOS
# or
xdg-open davos_map.html  # Linux
```

---

## 📁 Project Structure

```
WEF 2026/
├── davos_agent.py          # 🧠 Core recommendation engine (TF-IDF + CLI)
├── davos_events.csv        # 📊 Sample event data (20 WEF events)
├── davos_map.html          # 🗺️ Interactive map visualization
├── DAVOS_HACKATHON_PLAN.md # 📋 PhD-level technical specification
├── requirements.txt        # 📦 Python dependencies
└── README.md              # 📖 This file
```

---

## 🎯 Features

### 1. Semantic Recommendation Engine (`davos_agent.py`)
- **TF-IDF Vectorization** with bi-gram features
- **Cosine Similarity** for profile-event matching
- **Explainable AI** with matched topic explanations
- **Interactive CLI** for real-time recommendations

### 2. Interactive Map (`davos_map.html`)
- **Leaflet.js** map with Davos venue markers
- **Real-time filtering** by track, search, and date
- **Personalized recommendations** with visual highlighting
- **Smooth navigation** with fly-to animations
- **Navigation tracking** for analytics

### 3. Open Canvas Architecture
- Modular, extensible components
- Stateless core design
- JSON export for integrations
- Event-driven tracking

---

## 💡 Usage Examples

### CLI Recommendations
```
🎯 Enter your profile or command: I'm a climate scientist interested in blockchain for carbon tracking

🎯 Top 5 Recommended Events for You:

1. 🏆 Climate Finance Revolution
   Match: 72.3% | Track: Climate & Sustainability
   📍 Parsenn Hall (Congress Centre)
   💡 Highly relevant to your interests | Covers: Climate Change, Finance
```

### Available Commands
| Command | Description |
|---------|-------------|
| `<profile>` | Enter profile text for recommendations |
| `search <query>` | Search events by keyword |
| `tracks` | List all event tracks |
| `all` | Show all events |
| `export` | Export events to JSON |
| `history` | View navigation history |
| `quit` | Exit the application |

---

## 🧮 Algorithm Details

### TF-IDF Weighting
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{N}{|\{d \in D : t \in d\}|}\right)$$

### Cosine Similarity
$$\text{sim}(\vec{u}, \vec{e}) = \frac{\vec{u} \cdot \vec{e}}{||\vec{u}|| \times ||\vec{e}||}$$

See `DAVOS_HACKATHON_PLAN.md` for complete mathematical foundations.

---

## 🗺️ Map Features

- **Track Color Coding**: Each track has a unique color
- **Click Navigation**: Click markers or event cards to fly to locations
- **Profile Recommendations**: Enter your profile for personalized suggestions
- **Search & Filter**: Real-time filtering with visual feedback
- **Navigation Tracker**: All interactions logged for analytics

---

## 🔧 API Integration

```python
from davos_agent import DavosRecommendationAgent

agent = DavosRecommendationAgent("davos_events.csv")
recommendations = agent.recommend("AI governance and climate policy", top_k=5)

for rec in recommendations:
    print(f"{rec.event.title}: {rec.match_percentage}%")
```

---

## 📈 Performance

| Operation | Complexity |
|-----------|------------|
| TF-IDF Fit | O(n × m) |
| Transform | O(m × v) |
| Similarity | O(k × v) |

Where n=events, m=tokens, v=vocabulary, k=results.

---

## 🛣️ Roadmap

- [ ] Transformer embeddings (Sentence-BERT)
- [ ] Collaborative filtering
- [ ] Real-time schedule optimization
- [ ] Mobile app integration

---

## 📜 License

MIT License - WEF 2026 Hackathon Team

---

*Built with 🧠 TF-IDF + 🗺️ Leaflet.js for the World Economic Forum 2026*

