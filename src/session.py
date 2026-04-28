# save study sessions to json files for later review

import json
import os
from datetime import datetime
from .utils import format_time


def save_session(elapsed_seconds, focused_seconds, focus_score):
    # save this session's data
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    session_data = {
        "date": date_str,
        "time": time_str,
        "duration_seconds": int(elapsed_seconds),
        "focused_seconds": int(focused_seconds),
        "focus_score": round(focus_score, 1),
        "duration_formatted": format_time(int(elapsed_seconds)),
        "focused_formatted": format_time(int(focused_seconds))
    }

    # create data if path it doesn't exist
    sessions_dir = os.path.join("data", "sessions")
    os.makedirs(sessions_dir, exist_ok=True)

    # save with date and time in filename
    filename = f"session_{date_str}_{now.strftime('%H-%M')}.json"
    filepath = os.path.join(sessions_dir, filename)

    with open(filepath, "w") as f:
        json.dump(session_data, f, indent=2)

    return filepath
