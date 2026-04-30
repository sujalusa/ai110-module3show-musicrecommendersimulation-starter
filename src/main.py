"""
Music Recommender - AI-Powered Agentic System

This file demonstrates the enhanced AI recommender system with:
- Natural language processing via Claude/OpenAI
- Retrieval-Augmented Generation (RAG) for intelligent song search
- Agentic reasoning with validation steps
- Comprehensive logging and transparency

Usage:
    python -m src.main

Environment Setup:
    1. Copy .env.example to .env
    2. Add your OPENAI_API_KEY to .env
    3. pip install -r requirements.txt
    4. Run this script
"""

import sys
import logging
from .recommender import load_songs, recommend_songs
from .ai_agent import AIRecommenderAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_traditional_mode() -> None:
    """Run the traditional rule-based recommendation mode."""
    print("\n" + "="*70)
    print("TRADITIONAL MODE: Rule-Based Recommendations")
    print("="*70)
    
    songs = load_songs("data/songs.csv")
    
    profiles = [
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.9}),
        ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.2}),
        ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.8}),
    ]

    for profile_name, user_prefs in profiles:
        print(f"\n📋 Profile: {profile_name}")
        print(f"   Preferences: {user_prefs}")
        
        recommendations = recommend_songs(user_prefs, songs, k=3)

        print("   Top recommendations:")
        for i, rec in enumerate(recommendations, 1):
            song, score, explanation = rec
            print(f"   {i}. 🎵 {song['title']} by {song['artist']}")
            print(f"      Score: {score:.2f} | Reasons: {explanation}")
        print()


def run_ai_mode() -> None:
    """Run the AI-powered agentic recommendation mode."""
    print("\n" + "="*70)
    print("AI MODE: Agentic Workflow with RAG and Natural Language Processing")
    print("="*70)
    
    songs = load_songs("data/songs.csv")
    agent = AIRecommenderAgent(songs)
    
    # Natural language queries to test
    queries = [
        "I want something upbeat and energetic to workout to",
        "Give me chill lofi beats for studying and focusing",
        "I'm in the mood for some sad, emotional music",
        "Show me something intense and aggressive for running",
        "I need relaxing jazz music for a coffee shop vibe",
    ]
    
    for query in queries:
        print(f"\n👤 User Query: \"{query}\"")
        print("-" * 70)
        
        try:
            recommendations = agent.recommend(query, k=3)
            
            print("\n🤖 AI Agent Reasoning Process:")
            for thought in agent.get_thought_process():
                print(f"   Step {thought['step']}: {thought['action']}")
                print(f"      → {thought['reasoning'][:80]}")
            
            print("\n🎵 AI Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n   {i}. {rec.song['title']} by {rec.song['artist']}")
                print(f"      Genre: {rec.song['genre']} | Mood: {rec.song['mood']} | Energy: {rec.song['energy']}")
                print(f"      Match Score: {rec.score:.3f}")
                print(f"      Why: {rec.ai_explanation}")
                print(f"      Technical reasons: {', '.join(rec.match_reasons)}")
                
        except Exception as e:
            logger.error(f"Error during recommendation: {e}")
            print(f"   ❌ Error: {e}")
        
        print("\n" + "-" * 70)


def main() -> None:
    """Main entry point."""
    print("\n╔══════════════════════════════════════════════════════════════════════╗")
    print("║        AI-POWERED MUSIC RECOMMENDER SYSTEM                          ║")
    print("║                                                                      ║")
    print("║  Features:                                                          ║")
    print("║  • Agentic Workflow: Multi-step reasoning with validation           ║")
    print("║  • RAG (Retrieval-Augmented Generation): Semantic song search       ║")
    print("║  • Natural Language Understanding: Conversational preference input  ║")
    print("║  • Comprehensive Logging: Track all decisions and reasoning        ║")
    print("║  • Error Handling & Guardrails: Robust fallback mechanisms         ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    try:
        # Run both modes
        run_traditional_mode()
        run_ai_mode()
        
        print("\n" + "="*70)
        print("✅ Recommendation system executed successfully!")
        print("📊 Full session logs available in: recommender_agent.log")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
