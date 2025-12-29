# Sign Language Emotion & Gesture Password Demo

This repository contains a simple demo that detects hand gestures using MediaPipe, annotates emotion (movement-based), and speaks detected words using `pyttsx3`.

Files:
- `final_sign_project.py` — main demo (gesture detection, emotion, voice, password sequence)
- `hand_detection.py`, `camera_test.py`, `collect_data.py`, `simple_sign_demo.py` — helper/demo scripts
- `output.txt` — sample output / logs

Requirements:
- Python 3.8+
- See `requirements.txt` for packages.

Quick start:

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the demo:

```bash
python final_sign_project.py
```

Notes:
- The script uses the default webcam (index 0). If your camera index differs, update the code.
- `pyttsx3` speaks on the main thread by default and may block the UI; consider running speech in a separate thread for smoother video.

How to add this repo to GitHub (replace `<YOUR_GITHUB_URL>`):

```bash
git init
git add .
git commit -m "Initial commit: sign language demo"
git branch -M main
git remote add origin <YOUR_GITHUB_URL>
git push -u origin main
```
# sign-language-emotion-voice
Emotion-aware sign language to speech system
