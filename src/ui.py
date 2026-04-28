# OpenCV - for drawing on frames
# from: https://opencv.org/
import cv2

# internal modules
from src.utils import format_time


def draw_detection_overlay(frame, result):
    # debug visualization showing what the AI sees
    h, w = frame.shape[:2]

    # draw face bounding box if we detected a face
    if result.get("face_detected") and result.get("bbox"):
        bbox = result["bbox"]
        x, y, bw, bh = bbox["x"], bbox["y"], bbox["width"], bbox["height"]

        cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        # show status (green if focused, orange if distracted)
        status = result.get("status", "Unknown")
        status_color = (0, 255, 0) if status == "Focused" else (0, 165, 255)
        cv2.putText(frame, f"Status: {status}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        # show where they're looking
        gaze = result.get("gaze_direction", "")
        cv2.putText(frame, f"Gaze: {gaze}", (x, y + bh + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # phone detection status
    on_phone = result.get("on_phone", False)
    phone_color = (0, 0, 255) if on_phone else (0, 255, 0)
    phone_text = "PHONE DETECTED!" if on_phone else "No phone"
    cv2.putText(frame, phone_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, phone_color, 2)

    # face detection status
    face_text = "Face: YES" if result.get("face_detected") else "Face: NO"
    face_color = (0, 255, 0) if result.get("face_detected") else (0, 165, 255)
    cv2.putText(frame, face_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, face_color, 1)

    return frame


def draw_widget(canvas, status, streak, best, alert, distraction_time):
    # draw the small focus tracker bar in the corner
    h, w = canvas.shape[:2]

    if alert:
        # show alert in orange
        canvas[:] = (0, 100, 255)
        size = cv2.getTextSize(alert, cv2.FONT_HERSHEY_DUPLEX, 0.5, 2)[0]
        x = (w - size[0]) // 2
        y = h // 2 + 8
        cv2.putText(canvas, alert, (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2)

    elif status == "Focused":
        # showing you're focused - dark background, green text
        canvas[:] = (35, 35, 35)
        streak_text = format_time(int(streak))
        size = cv2.getTextSize(streak_text, cv2.FONT_HERSHEY_DUPLEX, 1.3, 2)[0]
        x = (w - size[0]) // 2
        cv2.putText(canvas, streak_text, (x, 55), cv2.FONT_HERSHEY_DUPLEX, 1.3, (50, 230, 80), 2)

        # show best streak so far
        best_text = f"best {format_time(int(best))}"
        best_size = cv2.getTextSize(best_text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
        cv2.putText(canvas, best_text, ((w - best_size[0]) // 2, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

    else:
        # distracted - change background color based on how long
        if distraction_time > 5:
            canvas[:] = (40, 50, 60)  # darker when more distracted
        else:
            canvas[:] = (35, 35, 35)

        if distraction_time > 3:
            # show countdown timer
            text = f"! {int(distraction_time)}s"
            size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1.1, 2)[0]
            cv2.putText(canvas, text, ((w - size[0]) // 2, 55), cv2.FONT_HERSHEY_DUPLEX, 1.1, (60, 150, 220), 2)
        else:
            # show previous streak fading out
            streak_text = format_time(int(streak))
            size = cv2.getTextSize(streak_text, cv2.FONT_HERSHEY_DUPLEX, 1.3, 2)[0]
            cv2.putText(canvas, streak_text, ((w - size[0]) // 2, 55), cv2.FONT_HERSHEY_DUPLEX, 1.3, (100, 100, 100), 2)
