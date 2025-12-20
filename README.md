# Mood Sync: AI-Powered Emotion & Media Recommendation System

**[View Live App](https://mood-sync-aakash.streamlit.app)**

## About the Project
**Mood Sync** is an intelligent, full-stack web application designed to bridge the gap between human emotion and digital experiences. Unlike static recommendation engines that rely on manual input or search history, Mood Sync uses **Computer Vision and Artificial Intelligence** to analyze your facial expressions in real-time.

By detecting your current emotional state (e.g., Happy, Sad, Fear, Angry, Disgust), the system acts as a personalized digital companion: it instantly curates a matching environment of music, movies, food, and activities to either amplify your joy or comfort your stress.

## Problems Solved
This project addresses three common gaps in personalized media consumption:

### 1. Emotional Disconnect
Standard algorithms (like Spotify or Netflix) recommend content based on *past* behavior, not *current* feelings. Mood Sync solves this by using real-time biometric data to match your **present** emotional needs.

### 2. Decision Paralysis
Users often spend more time scrolling for something to watch or listen to than actually enjoying it. This system removes the friction of choice by autonomously providing a curated "Vibe Check."

### 3. Detection Bias
Standard AI models often struggle to detect subtle negative emotions (like Disgust or Fear), labeling them as "Neutral." This project solves that with a custom **Priority Threshold Algorithm** that weighs subtle expressions higher than dominant neutral features.

## How It Works (The Logic)
The system operates on a **"Enhance → Scan → Analyze → Curate"** cycle:

### Enhance
Before analysis, the system applies **Adaptive Image Processing** using OpenCV. It increases contrast (alpha=1.5) and brightness (beta=30) and applies a sharpening kernel to ensure accurate detection even in low-quality webcam lighting.

### Scan
The application uses the user's webcam (via `streamlit-camera-input`) to capture a real-time image frame.

### Analyze (Dual-AI Engine)
1.  **Cloud Layer:** The image is sent to the **Face++ API** for high-precision emotion detection and eye-status analysis (to detect drowsiness).
2.  **Local Fallback:** If the cloud API is unreachable, the system automatically switches to **DeepFace (OpenCV)** running locally to ensure 100% uptime.
3.  **Priority Logic:** A custom Python function overrides the raw confidence scores. If a "hard-to-detect" emotion like *Disgust* or *Fear* crosses a specific threshold (e.g., >2%), it takes priority over *Neutral*, ensuring high sensitivity.

### Curate
Based on the final determined emotion and the user's selected age group, the system queries a dynamic `MOOD_MAP` database to retrieve tailored recommendations for music (YouTube), movies, food, and activities.

## Results
* **Accuracy:** Achieved high-fidelity emotion recognition. The **Priority Threshold** logic successfully distinguishes between subtle expressions like *Disgust* vs. *Neutral*, which standard models often miss.
* **Resilience:** The "Dual-Engine" architecture ensures the app never crashes, seamlessly failing over to local AI if the internet connection is unstable.
* **Latency:** Optimized image processing allows for analysis and recommendation delivery in under **3 seconds**.

## Tech Stack
* **Language:** Python 3.x
* **Frontend/Backend:** Streamlit Cloud
* **Computer Vision:** OpenCV (cv2), DeepFace
* **Cloud AI:** Face++ Cognitive Services API
* **Security:** Streamlit Secrets Management (for API Key protection)

## How to Run

### Prerequisites
* Python 3.x installed
* A webcam

### 1. Install Required Libraries
Open your terminal and run:
```bash
pip install streamlit opencv-python-headless deepface requests
