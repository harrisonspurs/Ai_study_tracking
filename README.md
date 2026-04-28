# AI Study Focus Tracker

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## How it Works
1. **Start the session** - The app will open with a small widget in the corner showing your focus status
2. **Stay focused** - The app tracks your gaze and detects if you're on your phone. You'll get alerts if you get distracted
3. **Finish your session** - Press ESC to stop. Your session data will be saved to `data/sessions/` as JSON
4. **Copy session data** - Find your session JSON file in `data/sessions/` and copy the output
5. **Log your data** - Paste the JSON data into the Study dashboard `<https://studentfocus.me/>` in the import tab to track your session
6. **Developer mode** - Press 'c' on the widget to toggle developer mode and see what the AI is detecting
