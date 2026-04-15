"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Define user preference profiles
    profiles = [
        # Distinct profiles
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.9}),
        ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.2}),
        ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.8}),
        
        # Adversarial profiles
        ("Oxymoronic Mood-Energy Conflict", {"genre": "lofi", "mood": "intense", "energy": 0.15}),
        ("Extreme Energy Boundary (Zero)", {"genre": "pop", "mood": "happy", "energy": 0.0}),
        ("Non-Existent Genre-Mood Pair", {"genre": "reggae", "mood": "aggressive", "energy": 0.5}),
        ("High Energy + Relaxed Mood Contradiction", {"genre": "jazz", "mood": "relaxed", "energy": 0.92}),
        ("Neutral Energy with No Matching Preferences", {"genre": "metal", "mood": "happy", "energy": 0.5}),
    ]

    for profile_name, user_prefs in profiles:
        print(f"\n=== Profile: {profile_name} ===")
        print(f"Preferences: {user_prefs}")
        
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\nTop recommendations:\n")
        for rec in recommendations:
            song, score, explanation = rec
            print(f"🎵 {song['title']} by {song['artist']}")
            print(f"   Score: {score:.2f}")
            print(f"   Reasons: {explanation}")
            print()


if __name__ == "__main__":
    main()
