#!/usr/bin/env python
"""
Quick demo of the AI Music Recommender System.

This script showcases the key features without requiring the full main.py output.
Run with: python demo.py
"""

import sys
sys.path.insert(0, '.')

from src.recommender import load_songs
from src.ai_agent import AIRecommenderAgent


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_recommendation(rec, index: int) -> None:
    """Print a single recommendation."""
    print(f"\n  {index}. 🎵 {rec.song['title']} by {rec.song['artist']}")
    print(f"     Genre: {rec.song['genre']} | Mood: {rec.song['mood']} | Energy: {rec.song['energy']}")
    print(f"     Match Score: {rec.score:.3f}")
    print(f"     Why: {rec.ai_explanation}")


def demo():
    """Run the demonstration."""
    print("\n╔══════════════════════════════════════════════════════════════════════╗")
    print("║        🎵 AI-POWERED MUSIC RECOMMENDER SYSTEM DEMO 🎵               ║")
    print("║                                                                      ║")
    print("║  Features:                                                          ║")
    print("║  • Agentic Workflow: Multi-step reasoning                           ║")
    print("║  • RAG: Semantic song retrieval                                     ║")
    print("║  • Natural Language: Conversational preference input                ║")
    print("║  • Logging: Full transparency on decisions                         ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    # Load songs and initialize agent
    print_header("Step 1: Initializing System")
    print("  Loading songs...")
    songs = load_songs("data/songs.csv")
    print(f"  ✓ Loaded {len(songs)} songs")
    
    print("  Initializing AI Agent...")
    agent = AIRecommenderAgent(songs)
    print("  ✓ Agent ready")
    
    # Demo queries
    queries = [
        "I want something upbeat and energetic to workout to",
        "Give me chill lofi beats for studying",
        "Show me some intense rock music",
    ]
    
    for query_num, query in enumerate(queries, 1):
        print_header(f"Demo {query_num}: User Query")
        print(f"  \"{query}\"")
        
        print_header(f"Demo {query_num}: AI Processing")
        recommendations = agent.recommend(query, k=3)
        
        # Show reasoning
        thoughts = agent.get_thought_process()
        print("  AI Reasoning Steps:")
        for thought in thoughts:
            print(f"    Step {thought['step']}: {thought['action']}")
        
        # Show recommendations
        print_header(f"Demo {query_num}: Recommendations")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print_recommendation(rec, i)
        else:
            print("  No recommendations found")
    
    print_header("✅ Demo Complete")
    print("  💡 Logs available in: recommender_agent.log")
    print()


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
