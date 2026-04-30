"""
Test suite for the AI Music Recommender Agent.

Tests cover:
- Preference extraction (both AI and fallback modes)
- RAG retrieval and similarity search
- Scoring and validation logic
- End-to-end recommendation workflow
"""

import pytest
import json
from src.ai_agent import AIRecommenderAgent, AgentThought, RecommendationDecision
from src.recommender import load_songs


class TestAIAgent:
    """Test suite for the AI Recommender Agent."""
    
    @pytest.fixture
    def songs(self):
        """Load test songs."""
        return load_songs("data/songs.csv")
    
    @pytest.fixture
    def agent(self, songs):
        """Create an agent instance without API key (fallback mode)."""
        import os
        # Ensure no API key is set for testing
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        return AIRecommenderAgent(songs)
    
    def test_agent_initialization(self, agent, songs):
        """Test agent initializes correctly."""
        assert agent is not None
        assert len(agent.songs) == len(songs)
        assert len(agent.song_corpus) == len(songs)
        assert agent.song_vectors is not None
    
    def test_preference_extraction_fallback(self, agent):
        """Test fallback preference extraction without API."""
        prefs = agent._extract_preferences_with_ai("I want chill lofi beats")
        
        assert "genres" in prefs
        assert "moods" in prefs
        assert "keywords" in prefs
        
        # Should detect lofi and chill
        assert "lofi" in prefs["genres"]
        assert "chill" in prefs["moods"]
    
    def test_preference_extraction_energy_high(self, agent):
        """Test energy level detection for high energy."""
        prefs = agent._extract_preferences_with_ai("I need high energy intense music")
        
        assert prefs.get("energy_level") is not None
        assert prefs["energy_level"] > 0.7  # High energy
    
    def test_preference_extraction_energy_low(self, agent):
        """Test energy level detection for low energy."""
        prefs = agent._extract_preferences_with_ai("Give me calm relaxing music")
        
        assert prefs.get("energy_level") is not None
        assert prefs["energy_level"] < 0.4  # Low energy
    
    def test_rag_retrieval(self, agent):
        """Test RAG retrieval mechanism."""
        preferences = {
            "genres": ["pop"],
            "moods": ["happy"],
            "keywords": ["upbeat", "catchy"],
            "energy_level": 0.8
        }
        
        retrieved = agent._retrieve_songs_rag(preferences, top_k=5)
        
        assert len(retrieved) > 0
        assert len(retrieved) <= 5
        
        # Check structure
        for song, score in retrieved:
            assert isinstance(song, dict)
            assert isinstance(score, float)
            assert 0 <= score <= 1
    
    def test_retrieval_returns_multiple_results(self, agent):
        """Test that retrieval returns reasonable number of results."""
        preferences = {
            "genres": ["rock"],
            "moods": ["intense"],
            "keywords": ["powerful"],
            "energy_level": 0.9
        }
        
        retrieved = agent._retrieve_songs_rag(preferences, top_k=10)
        
        assert len(retrieved) > 0
        # Should return songs, not just empty list
        assert all("title" in song[0] for song in retrieved)
    
    def test_scoring_and_validation(self, agent):
        """Test scoring and validation logic."""
        preferences = {
            "genres": ["pop"],
            "moods": ["happy"],
            "keywords": [],
            "energy_level": 0.8
        }
        
        retrieved = agent._retrieve_songs_rag(preferences, top_k=10)
        scored = agent._validate_and_score(preferences, retrieved)
        
        assert len(scored) > 0
        
        # Check structure
        for song, score, reasons in scored:
            assert isinstance(song, dict)
            assert isinstance(score, float)
            assert isinstance(reasons, list)
            assert len(reasons) > 0
        
        # Scores should be sorted descending
        scores = [s[1] for s in scored]
        assert scores == sorted(scores, reverse=True)
    
    def test_explanation_generation_fallback(self, agent):
        """Test explanation generation in fallback mode."""
        song = {
            "title": "Test Song",
            "artist": "Test Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8
        }
        reasons = ["genre match: pop", "mood match: happy"]
        
        explanation = agent._generate_single_explanation(song, reasons)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert song["title"] in explanation or "Test Song" in explanation
    
    def test_recommendation_workflow(self, agent):
        """Test full recommendation workflow."""
        query = "I want upbeat pop music for working out"
        recommendations = agent.recommend(query, k=3)
        
        assert len(recommendations) <= 3
        assert len(recommendations) > 0
        
        # Check structure
        for rec in recommendations:
            assert isinstance(rec, RecommendationDecision)
            assert isinstance(rec.song, dict)
            assert isinstance(rec.score, float)
            assert isinstance(rec.match_reasons, list)
            assert isinstance(rec.ai_explanation, str)
            
            # Validate song has required fields
            assert "title" in rec.song
            assert "artist" in rec.song
            assert "genre" in rec.song
    
    def test_thought_process_logging(self, agent):
        """Test that reasoning steps are logged."""
        query = "Give me chill music"
        agent.recommend(query, k=2)
        
        thought_process = agent.get_thought_process()
        
        assert len(thought_process) > 0
        
        # Check that key steps are logged
        actions = [t["action"] for t in thought_process]
        # In fallback mode, we at least get RAG Retrieval and Validation & Scoring
        assert any("RAG" in action or "Retrieval" in action for action in actions)
        assert any("Validation" in action or "Scoring" in action for action in actions)
    
    def test_session_summary(self, agent):
        """Test session summary generation."""
        query = "Rock music"
        agent.recommend(query, k=2)
        
        summary = agent.get_session_summary()
        
        assert "timestamp" in summary
        assert "total_steps" in summary
        assert "thought_process" in summary
        assert summary["total_steps"] > 0
        assert summary["songs_available"] > 0
    
    def test_different_query_variations(self, agent):
        """Test robustness with different query styles."""
        queries = [
            "I want upbeat pop",
            "chill lofi vibes",
            "aggressive metal music",
            "sad emotional tracks",
            "happy music",
        ]
        
        for query in queries:
            recommendations = agent.recommend(query, k=2)
            
            assert len(recommendations) > 0, f"No recommendations for: {query}"
            assert all(isinstance(r, RecommendationDecision) for r in recommendations)
    
    def test_error_handling_empty_query(self, agent):
        """Test error handling with empty query."""
        try:
            recommendations = agent.recommend("", k=2)
            # Should either return empty or fallback gracefully
            assert isinstance(recommendations, list)
        except Exception as e:
            pytest.fail(f"Should handle empty query gracefully: {e}")
    
    def test_reproducibility(self, agent):
        """Test that results are reproducible (deterministic)."""
        query = "upbeat pop music"
        
        recs1 = agent.recommend(query, k=3)
        recs2 = agent.recommend(query, k=3)
        
        # Should get same songs (order might vary if scores are tied)
        songs1 = [r.song["id"] for r in recs1]
        songs2 = [r.song["id"] for r in recs2]
        
        assert songs1 == songs2, "Results should be deterministic"


class TestIntegration:
    """Integration tests for the full system."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from loading to recommendations."""
        # Load songs
        songs = load_songs("data/songs.csv")
        assert len(songs) > 0
        
        # Create agent
        agent = AIRecommenderAgent(songs)
        assert agent is not None
        
        # Get recommendations
        query = "I'm in the mood for some energetic music"
        recommendations = agent.recommend(query, k=5)
        
        # Validate results
        assert len(recommendations) > 0
        assert all(isinstance(r, RecommendationDecision) for r in recommendations)
        
        # Validate scores are descending
        scores = [r.score for r in recommendations]
        assert scores == sorted(scores, reverse=True)


if __name__ == "__main__":
    # Run tests with: pytest tests/test_ai_agent.py -v
    pytest.main([__file__, "-v"])
