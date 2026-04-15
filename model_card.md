# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeFinder 1.0  

---

## 2. Goal / Task  

VibeFinder suggests the top 5 songs from a small music catalog that best match a user's preferences for genre, mood, and energy level. It predicts which songs a person might enjoy based on these simple traits, like recommending upbeat pop for someone who wants happy, high-energy music.  

---

## 3. Intended Use and Non-Intended Use  

This system is designed for classroom exploration of basic recommendation algorithms, helping students understand how simple rules can create personalized suggestions. It's for learning about AI biases and evaluation, not for real-world music apps. Don't use it for commercial recommendations, medical mood therapy, or any serious decision-making—it ignores many song features and has limited data.  

---

## 4. Data Used  

The dataset has 20 songs with features like genre, mood, energy level (0-1 scale), tempo, valence, danceability, and acousticness. Genres include pop, lofi, rock, jazz, and others, but some are underrepresented (only 1-2 songs each). Limits: Small size means limited variety, and it misses features like lyrics or artist popularity.  

---

## 5. Algorithm Summary  

VibeFinder scores songs by checking if the genre matches (+1 point), mood matches (+1 point), and how close the energy levels are (up to 2 points for perfect match). It ranks songs by total score and picks the top 5. I changed the weights from the starter code to double energy importance and halve genre to test sensitivity.  

---

## 6. Observed Behavior / Biases  

The system works well for users with clear, matching preferences, like high-energy pop fans getting upbeat songs. But it has biases: low-energy users get fewer good options since only 3 songs are mellow, and genre matches can override mood or energy conflicts, leading to mismatched vibes.  

---

## 7. Evaluation Process  

I tested 8 profiles—3 normal ones (High-Energy Pop, Chill Lofi, Deep Intense Rock) and 5 adversarial ones to find weaknesses. I ran experiments like changing weights and compared results to my intuition. Surprises included how energy doubling made lists more diverse but less genre-focused.  

---

## 8. Ideas for Improvement  

Add more song features like danceability or tempo to the scoring. Include user feedback loops to learn from past recommendations. Expand the dataset to 100+ songs for better variety and reduce biases.  

---

## 9. Personal Reflection  

My biggest learning moment was realizing how simple rules can create "smart" recommendations but also hide big biases, like favoring high-energy songs. AI tools helped generate adversarial profiles and analyze code quickly, but I double-checked their suggestions against the data to ensure accuracy. I was surprised that even basic matching feels like real personalization—it's why music apps work despite being imperfect. Next, I'd add collaborative filtering to consider what similar users like, or build a web interface for easier testing.  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
