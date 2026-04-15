from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dictionaries."""
    import csv
    songs = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numerical fields
            row['id'] = int(row['id'])
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}.")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a song based on user preferences and returns score with reasons."""
    score = 0.0
    reasons = []
    
    # Genre match: +1.0 (halved)
    if song['genre'] == user_prefs.get('genre'):
        score += 1.0
        reasons.append("genre match (+1.0)")
    
    # Mood match: +1.0
    if song['mood'] == user_prefs.get('mood'):
        score += 1.0
        reasons.append("mood match (+1.0)")
    
    # Energy similarity: doubled importance
    if 'energy' in user_prefs:
        user_energy = user_prefs['energy']
        song_energy = song['energy']
        energy_similarity = 1 - abs(user_energy - song_energy)  # max diff is 1
        score += 2 * energy_similarity  # doubled
        reasons.append(f"energy similarity ({2 * energy_similarity:.2f})")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Recommends top k songs based on user preferences."""
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    return scored_songs[:k]
