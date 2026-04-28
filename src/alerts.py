# alert messages that pop up when your distracted for more than 10 seconds

ALERTS = {
    "looking down": [
        "Phone check? Back to work!",
        "Eyes up!",
        "Put it down.",
    ],
    "looking left": [
        "Eyes on screen.",
        "Focus left!",
        "Looking away?",
    ],
    "looking right": [
        "Back to center.",
        "Stay focused.",
        "Eyes left!",
    ],
    "looking up": [
        "Looking up?",
        "Ceiling won't help.",
        "Re-focus.",
    ],
    "away": [
        "You were on a roll!",
        "Come back to study.",
        "Stay with me.",
    ],
    "default": [
        "Stay focused.",
        "Keep going!",
        "You got this.",
    ]
}


def get_alert(status, gaze_direction, distraction_streak, threshold=10):
    # different allert based on how you are distracted

    if distraction_streak > threshold and status == "Distracted":
        # matching the alert to where your looking
        if gaze_direction == "looking down":
            alerts = ALERTS["looking down"]
        elif gaze_direction == "looking left":
            alerts = ALERTS["looking left"]
        elif gaze_direction == "looking right":
            alerts = ALERTS["looking right"]
        elif gaze_direction == "looking up":
            alerts = ALERTS["looking up"]
        else:
            alerts = ALERTS["default"]

        # goes through messages so you don't get the same one twice
        idx = int(distraction_streak) % len(alerts)
        return alerts[idx]

    if status == "Away" and distraction_streak > threshold:
        alerts = ALERTS["away"]
        idx = int(distraction_streak) % len(alerts)
        return alerts[idx]

    return ""
