# 🎵 AI-Powered Music Recommender System

An intelligent music recommendation engine featuring **Agentic Workflow** and **Retrieval-Augmented Generation (RAG)** to understand natural language preferences and deliver personalized recommendations.

---

## ✨ Advanced AI Features

### 1. **Agentic Workflow** 🤖
The system uses multi-step reasoning to make decisions:
- **Step 1**: Extract user preferences from natural language
- **Step 2**: Retrieve candidate songs using RAG
- **Step 3**: Validate and score recommendations
- **Step 4**: Generate AI explanations

Each step is logged and transparent for debugging.

### 2. **Retrieval-Augmented Generation (RAG)** 🔍
Songs are semantically indexed using TF-IDF vectors:
- User queries are converted to semantic vectors
- Cosine similarity identifies the most relevant songs
- Results are ranked by relevance before additional validation

### 3. **Natural Language Understanding** 💬
Input can be conversational:
- ❌ Old: `{"genre": "pop", "mood": "happy", "energy": 0.9}`
- ✅ New: `"I want something upbeat and energetic to workout to"`

### 4. **Reliability & Testing** ✅
- Comprehensive logging to `recommender_agent.log`
- Graceful fallbacks when API is unavailable
- Error handling with detailed error messages
- Session summaries with reasoning traces

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (optional—system works offline with fallback mode)

### Installation

```bash
# 1. Navigate to the project directory
cd ai110-module3show-musicrecommendersimulation-starter

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
# (Leave empty to run in offline fallback mode)

# 4. Run the system
python -m src.main
```

### Run in Fallback Mode (No API Key Required)
```bash
# Simply run without setting OPENAI_API_KEY
python -m src.main
```

The system will:
- Use keyword-based preference extraction
- Return semantic recommendations via RAG
- Provide rule-based explanations

---

## 📊 System Architecture

```
User Natural Language Query
    ↓
┌─────────────────────────────────┐
│ Preference Extraction (AI)       │ ← Uses Claude/GPT-3.5 or fallback
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ RAG Retrieval                   │ ← Semantic similarity search
│ (Cosine Similarity on TF-IDF)    │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Validation & Scoring            │ ← Multi-criteria ranking
│ (Genre, Mood, Energy Matching)  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ AI Explanation Generation       │ ← Natural language output
└─────────────────────────────────┘
    ↓
Final Recommendations (with reasoning)
```

---

## 💡 Usage Examples

### Example 1: Workout Music
```
User Query: "I want something upbeat and energetic to workout to"

AI Agent Steps:
1. Extracts: genres=[pop, hip-hop], moods=[energetic], energy=0.8
2. Retrieves: 20 candidate songs via semantic search
3. Scores: Prioritizes high-energy tracks
4. Explains: "Gym Hero is perfect for workouts—it's energetic pop with high energy (0.93)"
```

### Example 2: Study Music
```
User Query: "Give me chill lofi beats for studying and focusing"

AI Agent Steps:
1. Extracts: genres=[lofi], moods=[focused, chill], energy=0.3
2. Retrieves: Lofi songs semantically similar to "study focus"
3. Scores: Prioritizes acoustic, low-energy tracks
4. Explains: "Focus Flow is ideal for concentration—it's a lofi track with focused mood and low energy"
```

---

## 📝 Logging & Transparency

All decisions are logged to `recommender_agent.log`:

```
2025-04-29 10:15:23,456 - __main__ - INFO - Processing recommendation request: I want upbeat pop music
2025-04-29 10:15:24,123 - __main__ - INFO - [Step 1] Preference Extraction: Analyzed query...
2025-04-29 10:15:24,456 - __main__ - INFO - [Step 2] RAG Retrieval: Retrieved 20 candidate songs
2025-04-29 10:15:24,789 - __main__ - INFO - [Step 3] Validation & Scoring: Top scores: ['0.89', '0.87', '0.85']
2025-04-29 10:15:25,012 - __main__ - INFO - Generated 5 recommendations
```

You can also access reasoning within code:
```python
agent = AIRecommenderAgent(songs)
recommendations = agent.recommend("upbeat music")

# Get the reasoning steps
thought_process = agent.get_thought_process()
for step in thought_process:
    print(f"Step {step['step']}: {step['action']}")
    print(f"  Reasoning: {step['reasoning']}")
    print(f"  Result: {step['result']}")
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|---|
| `OPENAI_API_KEY` | No | Your OpenAI API key. Leave empty for offline mode. |

### Adjusting Recommendations

Modify `src/main.py` to change:
- **Number of recommendations**: Change `k=3` to desired value
- **Query examples**: Update the `queries` list
- **Scoring weights**: Adjust bonus multipliers in `_validate_and_score()`

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/test_recommender.py -v
```

Test the AI agent specifically:
```bash
# In Python REPL
from src.recommender import load_songs
from src.ai_agent import AIRecommenderAgent

songs = load_songs("data/songs.csv")
agent = AIRecommenderAgent(songs)

# Test with a query
recs = agent.recommend("I love jazz and relaxation")
for rec in recs:
    print(f"{rec.song['title']}: {rec.ai_explanation}")
```

---

## 🌐 Advanced Features

### 1. **Semantic Song Search (RAG)**
- Uses TF-IDF vectorization to understand song relationships
- Combines artist, genre, mood, and title in search space
- Cosine similarity finds contextually relevant matches

### 2. **Multi-Step Validation**
- Genre/mood exact matching (highest priority)
- Energy level similarity (±0.2 tolerance)
- Semantic relevance scores combined with rule-based scoring

### 3. **Graceful Degradation**
- If API unavailable: Uses keyword-based preference extraction
- If LLM explanation fails: Falls back to rule-based reasoning
- All errors logged for debugging

### 4. **Session Transparency**
```python
agent = AIRecommenderAgent(songs)
recommendations = agent.recommend("upbeat pop")

# Get full session summary
summary = agent.get_session_summary()
print(f"Steps taken: {summary['total_steps']}")
print(f"Reasoning trace: {summary['thought_process']}")
```

---

## 📊 Project Structure

```
ai110-module3show-musicrecommendersimulation-starter/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main entry point (both traditional & AI modes)
│   ├── recommender.py          # Original rule-based logic
│   └── ai_agent.py             # NEW: Agentic workflow + RAG
├── data/
│   └── songs.csv               # 19 sample songs with attributes
├── tests/
│   └── test_recommender.py     # Unit tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── README.md                   # THIS FILE
├── model_card.md               # Model documentation
└── reflection.md               # Implementation notes
```

---

## 🎯 How This Meets AI Requirements

### ✅ Agentic Workflow
- Multi-step reasoning pipeline
- Each step logged and traceable
- Validation and refinement at each stage
- Natural language preference extraction and task execution

### ✅ Retrieval-Augmented Generation (RAG)
- Semantic song search via TF-IDF + cosine similarity
- Songs ranked by relevance to query
- Retrieved data actively shapes final recommendations

### ✅ Natural Language Understanding
- Accepts conversational input instead of structured JSON
- Extracts preferences from free-form text
- Provides human-readable explanations

### ✅ Reliability & Testing
- Comprehensive logging (all decisions tracked)
- Error handling with graceful fallbacks
- Session summaries with reasoning transparency
- Unit tests in `tests/test_recommender.py`

### ✅ Reproducibility
- Clear setup instructions above
- Deterministic song data in `data/songs.csv`
- Fallback mode works without API key
- Logging enables debugging and verification

---

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found" warning
**Solution**: This is normal! The system works in offline mode with keyword-based extraction and RAG. To use AI explanations, add your API key to `.env`.

### No recommendations returned
**Solution**: Check the logs:
```bash
tail -f recommender_agent.log
```
Ensure `data/songs.csv` exists and has songs.

### Module not found errors
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📚 References

- **TF-IDF & Cosine Similarity**: Standard NLP techniques for semantic search
- **Agentic Workflows**: Multi-step reasoning systems from LLM research
- **RAG Pattern**: Augmenting LLMs with external data sources
- **OpenAI API**: https://platform.openai.com/docs/

---

## 📄 License

This project is part of the Applied AI System curriculum.

---

**Last Updated**: April 2025  
**Version**: 2.0 (AI-Enhanced)
