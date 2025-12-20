import streamlit as st
import cv2
from deepface import DeepFace
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
        "label": "POSITIVE",
        "expressions": ["( ^_^ )", "( 😆 )", "( 😎 )", "( 😌 )", "( 🥰 )"],
        "color": "#F4D03F",
        "song": "https://www.youtube.com/watch?v=jv-pYB0Qw9A", 
        "msg": "Vibe Check: Radiant. High energy detected.",
        "food": "Ice Cream or Iced Coffee.",
        "activities": {"1": "Play a game.", "2": "Drive/Walk.", "3": "Plan a trip.", "4": "Host dinner.", "5": "Gardening."},
        "movies": {"1": "Lego Movie", "2": "Ferris Bueller", "3": "La La Land", "4": "Mamma Mia", "5": "Singin' in Rain"}
    },
    "sad": {
        "label": "LOW ENERGY",
        "expressions": ["( u_u )", "( =_= )", "( ._. )", "( 😵‍💫 )"],
        "color": "#85929E",
        "song": "https://www.youtube.com/watch?v=D5147zORrGU", 
        "msg": "Vibe Check: Heavy. It is okay to slow down.",
        "food": "Hot Cocoa or Soup.",
        "activities": {"1": "Watch cartoons.", "2": "Journal.", "3": "Yin Yoga.", "4": "Nature walk.", "5": "Photo albums."},
        "movies": {"1": "Inside Out", "2": "Eternal Sunshine", "3": "Good Will Hunting", "4": "Shawshank", "5": "It's a Wonderful Life"}
    },
    "angry": {
        "label": "HIGH ENERGY/NEGATIVE",
        "expressions": ["( 😠 )", "( 😤 )", "( 😒 )", "( 😣 )", "( 😡 )", "( 🤬 )", "( 👿 )", "( 💢 )"],
        "color": "#C0392B",
        "song": "https://www.youtube.com/watch?v=WT2JOLqZBCM", 
        "msg": "Vibe Check: Volatile. Channel this heat.",
        "food": "Crunchy Snacks or Cold Water.",
        "activities": {"1": "Sprint outside.", "2": "Gym/Weights.", "3": "Clean house.", "4": "Power walk.", "5": "Breathing exercises."},
        "movies": {"1": "Kung Fu Panda", "2": "Fight Club", "3": "Mad Max", "4": "Gladiator", "5": "Rocky"}
    },
    "neutral": {
        "label": "BALANCED",
        "expressions": ["( 😌 )", "( 🤔 )", "( 👉👈 )"],
        "color": "#2E4053",
        "song": "https://www.youtube.com/watch?v=83ILtWq7HX0", 
        "msg": "Vibe Check: Steady. Ready to build.",
        "food": "Green Tea or Nuts.",
        "activities": {"1": "Build LEGOs.", "2": "Study.", "3": "Budgeting.", "4": "Read news.", "5": "Crossword."},
        "movies": {"1": "Wall-E", "2": "Social Network", "3": "Interstellar", "4": "Spotlight", "5": "12 Angry Men"}
    },
    "fear": {
        "label": "ANXIOUS",
        "expressions": ["( 😨 )", "( 😰 )", "( 😳 )"],
        "color": "#A2D9CE",
        "song": "https://www.youtube.com/watch?v=xuDhu7aNH4M", 
        "msg": "Vibe Check: Unstable. Deep breath in...",
        "food": "Chamomile Tea.",
        "activities": {"1": "Hug a pet.", "2": "Text a friend.", "3": "Box Breathing.", "4": "List worries.", "5": "Call family."},
        "movies": {"1": "Finding Nemo", "2": "Paddington 2", "3": "Walter Mitty", "4": "The Terminal", "5": "Sound of Music"}
    },
    "surprise": {
        "label": "SHOCK",
        "expressions": ["( 😯 )", "( 😲 )"],
        "color": "#E67E22",
        "song": "https://www.youtube.com/watch?v=kPNsevIaxWw", 
        "msg": "Vibe Check: Plot Twist.",
        "food": "Popcorn or Sweets.",
        "activities": {"1": "Tell a friend.", "2": "Research topic.", "3": "Brainstorm.", "4": "Walk it off.", "5": "Reflect."},
        "movies": {"1": "Zootopia", "2": "Knives Out", "3": "Parasite", "4": "Sixth Sense", "5": "Psycho"}
    },
    "disgust": {
        "label": "REJECTION",
        "expressions": ["( 🤢 )", "( 🤨 )"],
        "color": "#7DCEA0",
        "song": "https://www.youtube.com/watch?v=WZf9YXNOyZo", 
        "msg": "Vibe Check: Glitch detected.",
        "food": "Water with Lemon.",
        "activities": {"1": "Change room.", "2": "Drink water.", "3": "Clean up.", "4": "Fresh air.", "5": "Herbal tea."},
        "movies": {"1": "Ratatouille", "2": "Spirited Away", "3": "Amelie", "4": "Truman Show", "5": "Casablanca"}
    },
    "sleepy": {
        "label": "TIRED / DROWSY",
        "expressions": ["( 😴 )", "( 💤 )", "( -_- )zzZ"],
        "color": "#4A235A",
        "song": "https://www.youtube.com/watch?v=tphyy-5cCB4",
        "msg": "Vibe Check: Low Battery. Recharge required.",
        "food": "Warm Milk or Decaf Tea.",
        "activities": {"1": "Take a nap.", "2": "Listen to rain sounds.", "3": "Meditation.", "4": "Stretch gently.", "5": "Go to bed early."},
        "movies": {"1": "Fantasia", "2": "Midnight in Paris", "3": "Lost in Translation", "4": "The Big Blue", "5": "March of the Penguins"}
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
    try:
        r = requests.get("https://api.quotable.io/random?maxLength=100", timeout=2)
        if r.status_code == 200: 
            return f"\"{r.json()['content']}\" - {r.json()['author']}"
    except: pass
    return "Offline mode: Believe in yourself."

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
        
        if "error_message" in result: return None
        # Strict check: If faces list is empty, return None immediately
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
            return None # Correctly return None for objects/boxes
    except: return None

def analyze_image(image_file):
    temp_filename = "temp_face.jpg"
    with open(temp_filename, "wb") as f:
        f.write(image_file.getbuffer())

    enhance_image_quality(temp_filename)

    dom = analyze_with_faceplusplus(temp_filename)
    
    if not dom:
        st.warning("☁️ Cloud API unreachable or No Face. Switching to Local AI check...")
        try:
            # CHANGED: enforce_detection=True
            # This forces DeepFace to crash if it sees a box instead of a face.
            # We then catch that crash and return None.
            analysis = DeepFace.analyze(
                img_path=temp_filename, 
                actions=['emotion'], 
                enforce_detection=True, 
                detector_backend='opencv' 
            )
            if isinstance(analysis, list): 
                raw_emotions = analysis[0]['emotion']
            else: 
                raw_emotions = analysis['emotion']
            
            dom = determine_priority_mood(raw_emotions)

        except Exception as e:
            # If DeepFace crashes (because it saw a box), we return None.
            st.error(f"Analysis failed: No human face detected.")
            dom = None
    
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
        
        # If mood is None (e.g. Box, Bottle, Empty Room), show warning
        if mood is None:
            st.warning("⚠️ No face detected. Please try again.")
            st.caption("Tip: Ensure your face is clearly visible and not blocked by objects.")
        else:
            cfg = MOOD_MAP.get(mood, MOOD_MAP["neutral"])
            log_mood_to_file(mood, age_key)
            set_app_style(cfg['color'])

            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"<h1 style='text-align: center; color: {cfg['color']};'>{mood.upper()}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center;'>{random.choice(cfg['expressions'])}</h2>", unsafe_allow_html=True)
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

if __name__ == "__main__":
    main()