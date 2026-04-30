"""
AI-Powered Music Recommender Agent

This module implements an agentic workflow with RAG (Retrieval-Augmented Generation)
to provide intelligent music recommendations based on natural language input.

Features:
- Natural language preference extraction
- Semantic similarity-based song retrieval (RAG)
- Multi-step reasoning with validation
- Comprehensive logging and error handling
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recommender_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AgentThought:
    """Represents a step in the agent's reasoning process."""
    step: int
    action: str
    reasoning: str
    result: str


@dataclass
class RecommendationDecision:
    """Represents a final recommendation with reasoning."""
    song: Dict
    score: float
    match_reasons: List[str]
    ai_explanation: str


class AIRecommenderAgent:
    """
    An AI agent that uses natural language understanding and RAG
    to provide personalized music recommendations.
    """
    
    def __init__(self, songs: List[Dict], api_key: Optional[str] = None):
        """
        Initialize the AI recommender agent.
        
        Args:
            songs: List of song dictionaries
            api_key: OpenAI API key (uses environment variable if not provided)
        """
        self.songs = songs
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.thought_process: List[AgentThought] = []
        self.step_counter = 0
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Using fallback recommendation mode.")
        else:
            openai.api_key = self.api_key
        
        # Build song corpus for RAG
        self.song_corpus = self._build_song_corpus()
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.song_vectors = self.vectorizer.fit_transform(self.song_corpus)
        
        logger.info(f"Initialized AI agent with {len(songs)} songs")
    
    def _build_song_corpus(self) -> List[str]:
        """Build text corpus from songs for semantic search."""
        corpus = []
        for song in self.songs:
            # Create a rich text representation of each song
            text = (
                f"{song.get('title', '')} {song.get('artist', '')} "
                f"{song.get('genre', '')} {song.get('mood', '')} "
                f"{song.get('artist', '')} music"
            )
            corpus.append(text)
        return corpus
    
    def _log_thought(self, action: str, reasoning: str, result: str) -> None:
        """Log a step in the agent's reasoning process."""
        self.step_counter += 1
        thought = AgentThought(
            step=self.step_counter,
            action=action,
            reasoning=reasoning,
            result=result
        )
        self.thought_process.append(thought)
        logger.info(f"[Step {self.step_counter}] {action}: {reasoning[:100]}...")
    
    def _extract_preferences_with_ai(self, user_query: str) -> Dict:
        """
        Use OpenAI to extract structured preferences from natural language.
        
        Args:
            user_query: Natural language description of music preferences
            
        Returns:
            Dictionary with extracted preferences
        """
        if not self.api_key:
            return self._fallback_preference_extraction(user_query)
        
        try:
            prompt = f"""
            Extract music preferences from this user query: "{user_query}"
            
            Return a JSON object with these fields:
            - genres: list of preferred genres (e.g., ["pop", "rock"])
            - moods: list of preferred moods (e.g., ["happy", "energetic"])
            - energy_level: average energy preference (0-1 scale, or null)
            - keywords: list of descriptive keywords
            
            Example: {{"genres": ["pop"], "moods": ["happy"], "energy_level": 0.8, "keywords": ["upbeat", "danceable"]}}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            prefs_text = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                prefs = json.loads(prefs_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                prefs = self._fallback_preference_extraction(user_query)
            
            self._log_thought(
                action="Preference Extraction",
                reasoning=f"Analyzed query: {user_query}",
                result=f"Extracted preferences: {prefs}"
            )
            return prefs
            
        except Exception as e:
            logger.error(f"Error in preference extraction: {e}")
            return self._fallback_preference_extraction(user_query)
    
    def _fallback_preference_extraction(self, user_query: str) -> Dict:
        """Fallback keyword-based preference extraction when API unavailable."""
        query_lower = user_query.lower()
        
        # Simple keyword matching
        prefs = {
            "genres": [],
            "moods": [],
            "energy_level": None,
            "keywords": user_query.split()[:5]
        }
        
        # Genre detection
        genre_keywords = {
            "pop": ["pop", "upbeat", "catchy"],
            "rock": ["rock", "guitar", "loud"],
            "lofi": ["lofi", "chill", "lo-fi", "beats"],
            "jazz": ["jazz", "smooth", "sophisticated"],
            "ambient": ["ambient", "atmospheric", "calm"],
            "metal": ["metal", "heavy", "intense", "aggressive"],
        }
        
        for genre, keywords in genre_keywords.items():
            if any(kw in query_lower for kw in keywords):
                prefs["genres"].append(genre)
        
        # Mood detection
        mood_keywords = {
            "happy": ["happy", "upbeat", "cheerful", "positive"],
            "chill": ["chill", "relaxed", "calm", "mellow"],
            "intense": ["intense", "energetic", "powerful", "aggressive"],
            "sad": ["sad", "melancholy", "emotional", "depressing"],
            "focused": ["focus", "work", "study", "concentration"],
        }
        
        for mood, keywords in mood_keywords.items():
            if any(kw in query_lower for kw in keywords):
                prefs["moods"].append(mood)
        
        # Energy level detection
        if any(word in query_lower for word in ["high", "energetic", "intense", "pump"]):
            prefs["energy_level"] = 0.8
        elif any(word in query_lower for word in ["chill", "relax", "calm", "sleep"]):
            prefs["energy_level"] = 0.3
        
        return prefs
    
    def _retrieve_songs_rag(self, preferences: Dict, top_k: int = 20) -> List[Tuple[Dict, float]]:
        """
        Retrieve songs using semantic similarity (RAG component).
        
        Args:
            preferences: Extracted user preferences
            top_k: Number of candidates to retrieve
            
        Returns:
            List of (song, similarity_score) tuples
        """
        # Build query from preferences
        query_parts = []
        query_parts.extend(preferences.get("genres", []))
        query_parts.extend(preferences.get("moods", []))
        query_parts.extend(preferences.get("keywords", []))
        
        query_text = " ".join(query_parts)
        
        if not query_text:
            query_text = "music"
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query_text])
        
        # Calculate similarity scores
        similarities = cosine_similarity(query_vector, self.song_vectors)[0]
        
        # Get top-k candidates
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        retrieved_songs = [
            (self.songs[idx], float(similarities[idx]))
            for idx in top_indices
            if similarities[idx] > 0.0
        ]
        
        self._log_thought(
            action="RAG Retrieval",
            reasoning=f"Query: {query_text}",
            result=f"Retrieved {len(retrieved_songs)} candidate songs"
        )
        
        return retrieved_songs
    
    def _validate_and_score(
        self,
        preferences: Dict,
        retrieved_songs: List[Tuple[Dict, float]]
    ) -> List[Tuple[Dict, float, List[str]]]:
        """
        Validate and score retrieved songs with detailed reasoning.
        
        Args:
            preferences: User preferences
            retrieved_songs: Retrieved song candidates
            
        Returns:
            List of (song, score, reasons) tuples
        """
        scored_songs = []
        
        for song, rag_score in retrieved_songs:
            score = rag_score
            reasons = [f"semantic match ({rag_score:.2f})"]
            
            # Genre match bonus
            if song.get('genre') in preferences.get('genres', []):
                score += 0.3
                reasons.append(f"genre match: {song['genre']}")
            
            # Mood match bonus
            if song.get('mood') in preferences.get('moods', []):
                score += 0.3
                reasons.append(f"mood match: {song['mood']}")
            
            # Energy level bonus (if specified)
            if preferences.get('energy_level') is not None:
                target_energy = preferences['energy_level']
                song_energy = float(song.get('energy', 0.5))
                energy_match = 1 - abs(target_energy - song_energy)
                energy_bonus = energy_match * 0.2
                score += energy_bonus
                reasons.append(f"energy alignment ({energy_bonus:.2f})")
            
            scored_songs.append((song, score, reasons))
        
        # Sort by score
        scored_songs.sort(key=lambda x: x[1], reverse=True)
        
        self._log_thought(
            action="Validation & Scoring",
            reasoning=f"Validated {len(retrieved_songs)} candidates",
            result=f"Top scores: {[f'{s[1]:.2f}' for s in scored_songs[:3]]}"
        )
        
        return scored_songs
    
    def _generate_ai_explanations(self, recommendations: List[Tuple[Dict, float, List[str]]]) -> List[RecommendationDecision]:
        """
        Use AI to generate natural language explanations for recommendations.
        
        Args:
            recommendations: List of (song, score, reasons) tuples
            
        Returns:
            List of RecommendationDecision objects
        """
        decisions = []
        
        for song, score, reasons in recommendations:
            explanation = self._generate_single_explanation(song, reasons)
            
            decision = RecommendationDecision(
                song=song,
                score=score,
                match_reasons=reasons,
                ai_explanation=explanation
            )
            decisions.append(decision)
        
        return decisions
    
    def _generate_single_explanation(self, song: Dict, reasons: List[str]) -> str:
        """Generate a natural language explanation for a single recommendation."""
        if not self.api_key:
            return self._fallback_explanation(song, reasons)
        
        try:
            prompt = f"""
            Generate a brief (1-2 sentences) natural explanation for why this song
            matches a user's music preferences.
            
            Song: {song['title']} by {song['artist']}
            Genre: {song['genre']}, Mood: {song['mood']}, Energy: {song['energy']}
            Match reasons: {', '.join(reasons)}
            
            Explanation:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._fallback_explanation(song, reasons)
    
    def _fallback_explanation(self, song: Dict, reasons: List[str]) -> str:
        """Fallback explanation generation."""
        reasons_str = ", ".join(reasons)
        return (
            f"We recommend '{song['title']}' because it matches your preferences "
            f"({reasons_str}). Give it a listen!"
        )
    
    def recommend(self, user_query: str, k: int = 5) -> List[RecommendationDecision]:
        """
        Main entry point: recommend songs based on natural language input.
        
        This method orchestrates the full agentic workflow:
        1. Extract preferences from natural language
        2. Retrieve relevant songs (RAG)
        3. Validate and score recommendations
        4. Generate AI explanations
        
        Args:
            user_query: Natural language description of music preferences
            k: Number of recommendations to return
            
        Returns:
            List of RecommendationDecision objects
        """
        logger.info(f"Processing recommendation request: {user_query}")
        self.thought_process = []
        self.step_counter = 0
        
        try:
            # Step 1: Extract preferences
            preferences = self._extract_preferences_with_ai(user_query)
            
            # Step 2: Retrieve candidates (RAG)
            retrieved = self._retrieve_songs_rag(preferences, top_k=max(k * 4, 20))
            
            if not retrieved:
                logger.warning("No songs retrieved, returning fallback recommendations")
                retrieved = [(song, 0.5) for song in self.songs[:k * 4]]
            
            # Step 3: Validate and score
            scored = self._validate_and_score(preferences, retrieved)
            
            if not scored:
                logger.error("No valid recommendations generated")
                return []
            
            # Step 4: Generate explanations
            final_recommendations = self._generate_ai_explanations(scored[:k])
            
            logger.info(f"Generated {len(final_recommendations)} recommendations")
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error in recommendation workflow: {e}", exc_info=True)
            raise
    
    def get_thought_process(self) -> List[Dict]:
        """Return the agent's reasoning steps for transparency."""
        return [asdict(thought) for thought in self.thought_process]
    
    def get_session_summary(self) -> Dict:
        """Generate a summary of the recommendation session."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_steps": self.step_counter,
            "thought_process": self.get_thought_process(),
            "songs_available": len(self.songs),
        }
