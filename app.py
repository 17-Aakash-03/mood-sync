import streamlit as st
import cv2
import json
import os
import random
import datetime
import requests
import numpy as np

API_KEY = st.secrets["api_key"]
API_SECRET = st.secrets["api_secret"]
API_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"

st.set_page_config(page_title="Mood Sync", page_icon="🎭", layout="centered")

MOOD_MAP = {
    "happy": {
        "label": "JOYFUL / ENERGETIC / LOVE",
        "expressions": [
            "Joyful", "Smiling", "Cheerful", "Delighted", "Blessed", "Positive vibes", "Feeling good", "Over the moon", 
            "Glowing", "Carefree", "Laughing", "Pumped", "Fired up", "Adrenaline rush", "Lit", "Ready to move", 
            "Butterflies", "Obsessed", "Attached", "Affectionate", "Caring", "Dreaming of you", "Heart full",
            "Weekend mode", "Let’s dance", "Wild night", "Cheers", "Vibing", "Club mood"
        ],
        "color": "#F4D03F",
        "song": "https://www.youtube.com/watch?v=jv-pYB0Qw9A",
        "playlist": [
            "Happy — Pharrell Williams", "Good Life — OneRepublic", "Best Day of My Life — American Authors",
            "Perfect — Ed Sheeran", "All of Me — John Legend", "Until I Found You — Stephen Sanchez",
            "I Gotta Feeling — Black Eyed Peas", "Uptown Funk — Bruno Mars", "Levitating — Dua Lipa",
            "Don’t Stop Me Now — Queen", "Titanium — David Guetta"
        ],
        "msg": "Vibe Check: Radiant energy detected! Whether it's love, party, or joy—soak it in.",
        "food": "Ice Cream, Pizza, or Iced Coffee.",
        "activities": {"1": "Play a game.", "2": "Go dancing.", "3": "Plan a date.", "4": "Host a party.", "5": "Gardening."},
        "movies": {"1": "Lego Movie", "2": "Ferris Bueller", "3": "La La Land", "4": "Mamma Mia", "5": "Singin' in Rain"}
    },
    "sad": {
        "label": "SAD / HEARTBROKEN / LONELY",
        "expressions": [
            "Broken", "Empty", "Hopeless", "Low", "Miserable", "Numb", "Crying inside", "Gloomy", "Heavy heart", "Worthless",
            "Abandoned", "Betrayed", "Cheated", "Left alone", "Shattered", "Missing you", "Regret", "Lost everything",
            "Alone", "Ignored", "Nobody cares", "Disconnected", "Empty room", "Silent nights", "Unwanted"
        ],
        "color": "#85929E",
        "song": "https://www.youtube.com/watch?v=hLQl3WQQoQ0",
        "playlist": [
            "Someone Like You — Adele", "Fix You — Coldplay", "Lovely — Billie Eilish",
            "Back to Black — Amy Winehouse", "Let Her Go — Passenger", "Happier — Ed Sheeran",
            "Dancing On My Own — Calum Scott", "Lonely — Justin Bieber", "How to Save a Life — The Fray"
        ],
        "msg": "Vibe Check: Heavy heart detected. It's okay to feel this way. Take your time.",
        "food": "Hot Cocoa, Soup, or Comfort Food.",
        "activities": {"1": "Watch cartoons.", "2": "Journal.", "3": "Cry it out.", "4": "Nature walk.", "5": "Photo albums."},
        "movies": {"1": "Inside Out", "2": "Eternal Sunshine", "3": "Good Will Hunting", "4": "Shawshank", "5": "It's a Wonderful Life"}
    },
    "angry": {
        "label": "ANGRY / FRUSTRATED",
        "expressions": [
            "Furious", "Mad", "Irritated", "Annoyed", "Boiling", "Fed up", "Raging", "Done with it", "Snapping", "Explosive"
        ],
        "color": "#C0392B",
        "song": "https://www.youtube.com/watch?v=7wtfhZwyrcc",
        "playlist": [
            "Believer — Imagine Dragons", "Killing In The Name — Rage Against The Machine", 
            "Look What You Made Me Do — Taylor Swift", "Before He Cheats — Carrie Underwood", "Monster — Skillet"
        ],
        "msg": "Vibe Check: High heat detected. Channel this energy into something powerful.",
        "food": "Crunchy Snacks, Spicy Food, or Cold Water.",
        "activities": {"1": "Sprint outside.", "2": "Gym/Weights.", "3": "Clean house.", "4": "Power walk.", "5": "Breathing exercises."},
        "movies": {"1": "Kung Fu Panda", "2": "Fight Club", "3": "Mad Max", "4": "Gladiator", "5": "Rocky"}
    },
    "neutral": {
        "label": "CALM / CONFIDENT / FOCUSED",
        "expressions": [
            "Peaceful", "Quiet", "Soothing", "Stress-free", "Laid back", "Mindful", "Balanced", "Steady", "Tranquil",
            "Unstoppable", "Fearless", "Self-belief", "Powerful", "Focused", "Boss mode", "Winner mindset", "Grinding"
        ],
        "color": "#2E4053",
        "song": "https://www.youtube.com/watch?v=_mEC54eTuGw",
        "playlist": [
            "Let It Be — The Beatles", "River — Leon Bridges", "Ocean Eyes — Billie Eilish",
            "Lose Yourself — Eminem", "Stronger — Kanye West", "Unstoppable — Sia", "Hall of Fame — The Script"
        ],
        "msg": "Vibe Check: Steady and Locked in. You are ready to build or relax.",
        "food": "Green Tea, Nuts, or a Smoothie.",
        "activities": {"1": "Build LEGOs.", "2": "Study/Work.", "3": "Meditation.", "4": "Read news.", "5": "Crossword."},
        "movies": {"1": "Wall-E", "2": "Social Network", "3": "Interstellar", "4": "Spotlight", "5": "12 Angry Men"}
    },
    "fear": {
        "label": "ANXIOUS / STRESSED",
        "expressions": [
            "Overthinking", "Nervous", "Panicking", "Restless", "Uneasy", "Pressure", "Headache", "Mentally tired", "Overwhelmed"
        ],
        "color": "#A2D9CE",
        "song": "https://www.youtube.com/watch?v=kXYiU_JCYtU",
        "playlist": [
            "Breathin — Ariana Grande", "Stressed Out — Twenty One Pilots", "Mad World — Gary Jules",
            "Demons — Imagine Dragons", "Anxiety — Julia Michaels"
        ],
        "msg": "Vibe Check: Unstable. Deep breath in... hold... and let go.",
        "food": "Chamomile Tea or Dark Chocolate.",
        "activities": {"1": "Hug a pet.", "2": "Text a friend.", "3": "Box Breathing.", "4": "List worries.", "5": "Call family."},
        "movies": {"1": "Finding Nemo", "2": "Paddington 2", "3": "Walter Mitty", "4": "The Terminal", "5": "Sound of Music"}
    },
    "sleepy": {
        "label": "TIRED / EXHAUSTED",
        "expressions": [
            "Exhausted", "Drained", "Worn out", "Yawning", "Low battery", "No energy", "Sleepy eyes", "Burnt out"
        ],
        "color": "#4A235A",
        "song": "https://www.youtube.com/watch?v=syFZfO_wfMQ",
        "playlist": [
            "Night Changes — One Direction", "The Scientist — Coldplay", "Breathe Me — Sia",
            "Gravity — John Mayer", "Location Unknown — HONNE"
        ],
        "msg": "Vibe Check: Low Battery. Recharge required immediately.",
        "food": "Warm Milk or Decaf Tea.",
        "activities": {"1": "Take a nap.", "2": "Listen to rain sounds.", "3": "Meditation.", "4": "Stretch gently.", "5": "Go to bed early."},
        "movies": {"1": "Fantasia", "2": "Midnight in Paris", "3": "Lost in Translation", "4": "The Big Blue", "5": "March of the Penguins"}
    },
    "surprise": {
        "label": "SHOCK / HYPED",
        "expressions": ["( 😯 )", "( 😲 )", "Plot Twist!", "Mind Blown", "Whoa!"],
        "color": "#E67E22",
        "song": "https://www.youtube.com/watch?v=kPNsevIaxWw", 
        "playlist": ["Turn Down for What — DJ Snake", "Power — Kanye West", "Thunder — Imagine Dragons"],
        "msg": "Vibe Check: Unexpected energy detected.",
        "food": "Popcorn or Sweets.",
        "activities": {"1": "Tell a friend.", "2": "Research topic.", "3": "Brainstorm.", "4": "Walk it off.", "5": "Reflect."},
        "movies": {"1": "Zootopia", "2": "Knives Out", "3": "Parasite", "4": "Sixth Sense", "5": "Psycho"}
    },
    "disgust": {
        "label": "REJECTION",
        "expressions": ["( 🤢 )", "( 🤨 )", "Eww", "Nope", "Glitch"],
        "color": "#7DCEA0",
        "song": "https://www.youtube.com/watch?v=WZf9YXNOyZo", 
        "playlist": ["Bad Guy — Billie Eilish", "Toxic — Britney Spears"],
        "msg": "Vibe Check: Glitch detected.",
        "food": "Water with Lemon.",
        "activities": {"1": "Change room.", "2": "Drink water.", "3": "Clean up.", "4": "Fresh air.", "5": "Herbal tea."},
        "movies": {"1": "Ratatouille", "2": "Spirited Away", "3": "Amelie", "4": "Truman Show", "5": "Casablanca"}
    }
}

def set_app_style(hex_code):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {hex_code}22;
            transition: background-color 0.5s ease;
        }}
        div[data-testid="stHeader"] {{
            background-color: {hex_code};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def log_mood_to_file(mood, age_group):
    try:
        with open("mood_history.txt", "a") as f:
            f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mood: {mood.upper()} | Age: {age_group}\n")
    except: pass

def get_quote_from_api():
    quotes = [
        "\"Believe you can and you're halfway there.\" - Theodore Roosevelt",
        "\"The only way to do great work is to love what you do.\" - Steve Jobs",
        "\"It always seems impossible until it is done.\" - Nelson Mandela",
        "\"Act as if what you do makes a difference. It does.\" - William James",
        "\"Success is not final, failure is not fatal: it is the courage to continue that counts.\" - Winston Churchill",
        "\"You are never too old to set another goal or to dream a new dream.\" - C.S. Lewis",
        "\"Keep your face always toward the sunshine—and shadows will fall behind you.\" - Walt Whitman",
        "\"Happiness is not something ready made. It comes from your own actions.\" - Dalai Lama",
        "\"Your time is limited, so don't waste it living someone else's life.\" - Steve Jobs",
        "\"The best way to predict the future is to create it.\" - Peter Drucker"
    ]
    return random.choice(quotes)

def enhance_image_quality(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None: return
        enhanced = cv2.convertScaleAbs(img, alpha=1.5, beta=30)
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        cv2.imwrite(image_path, sharpened)
    except Exception as e:
        print(f"Enhancement failed: {e}")

def determine_priority_mood(emotions_dict):
    print("----- RAW SCORES -----")
    for k, v in emotions_dict.items():
        print(f"{k}: {v:.2f}")
    print("----------------------")

    if emotions_dict.get('disgust', 0) > 2.0:
        return 'disgust'
    if emotions_dict.get('fear', 0) > 5.0:
        return 'fear'
    if emotions_dict.get('angry', 0) > 10.0:
        return 'angry'
    if emotions_dict.get('sad', 0) > 15.0:
        return 'sad'

    return max(emotions_dict, key=emotions_dict.get)

def analyze_with_faceplusplus(image_path):
    try:
        data = {
            "api_key": API_KEY, "api_secret": API_SECRET, "return_attributes": "emotion,eyestatus" 
        }
        files = {"image_file": open(image_path, "rb")}
        response = requests.post(API_URL, data=data, files=files, timeout=10)
        result = response.json()
        
        if "error_message" in result: 
            print(f"API Error: {result['error_message']}")
            return None
            
        if "faces" in result and len(result["faces"]) > 0:
            face = result["faces"][0]
            emotions = face["attributes"]["emotion"]
            eyestatus = face["attributes"]["eyestatus"]
            
            emotions["happy"] = emotions.pop("happiness")
            emotions["sad"] = emotions.pop("sadness")
            emotions["angry"] = emotions.pop("anger") 
            
            left_closed = eyestatus["left_eye_status"]["no_glass_eye_close"] + eyestatus["left_eye_status"]["normal_glass_eye_close"]
            right_closed = eyestatus["right_eye_status"]["no_glass_eye_close"] + eyestatus["right_eye_status"]["normal_glass_eye_close"]
            if ((left_closed + right_closed) / 2.0) > 50.0:
                return "sleepy"

            return determine_priority_mood(emotions)
        else:
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def analyze_image(image_file):
    temp_filename = "temp_face.jpg"
    with open(temp_filename, "wb") as f:
        f.write(image_file.getbuffer())
    enhance_image_quality(temp_filename)
    dom = analyze_with_faceplusplus(temp_filename)
    return dom

def main():
    st.title("Mood Sync 🎭")
    st.markdown("Scan your face to get personalized music, food, and movie recommendations.")

    st.sidebar.header("User Profile")
    age_map = {"Under 15": "1", "15 - 24": "2", "25 - 40": "3", "41 - 60": "4", "60+": "5"}
    age_selection = st.sidebar.radio("Select Age Group:", list(age_map.keys()), index=1)
    age_key = age_map[age_selection]

    img_file = st.camera_input("Take a photo")

    if img_file is not None:
        with st.spinner("Analyzing Priority Vibes..."):
            mood = analyze_image(img_file)
        
        if mood is None:
            st.warning("⚠️ No face detected. Please try again.")
            st.caption("Tip: Ensure your face is clearly visible and lighting is good.")
        else:
            cfg = MOOD_MAP.get(mood, MOOD_MAP["neutral"])
            log_mood_to_file(mood, age_key)
            set_app_style(cfg['color'])

            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"<h1 style='text-align: center; color: {cfg['color']};'>{mood.upper()}</h1>", unsafe_allow_html=True)
                random_exprs = random.sample(cfg['expressions'], min(3, len(cfg['expressions'])))
                st.markdown(f"<h3 style='text-align: center;'>{'  •  '.join(random_exprs)}</h3>", unsafe_allow_html=True)
                st.info(f"{cfg['msg']}")

            with col2:
                st.markdown("### 📜 Quote")
                st.success(f"*{get_quote_from_api()}*")
                st.markdown("### 🧩 Activity")
                st.write(cfg['activities'].get(age_key, 'Relax.'))
                st.markdown("### 🎬 Movie")
                st.write(cfg['movies'].get(age_key, 'Any Movie'))
                st.markdown(f"### 🍵 Craving: **{cfg.get('food', '')}**")

            st.divider()
            st.markdown("### 🎧 Mood Anthem")
            st.video(cfg['song'])
            
            st.markdown("### 🎼 Recommended Playlist")
            for track in cfg.get('playlist', []):
                st.text(f"🎵 {track}")

if __name__ == "__main__":
    main()