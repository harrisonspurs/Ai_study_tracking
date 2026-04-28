# OpenCV - for camera capture and drawing UI elements
# from: https://opencv.org/
import cv2
import time

# NumPy - for creating blank canvas for the widget
# from: https://numpy.org/
import numpy as np

# internal modules
from src.detection import FocusDetector
from src.utils import format_time
from src.session import save_session
from src.focus_manager import FocusManager
from src.ui import draw_widget, draw_detection_overlay

# widget window shows your focus status
WINDOW_NAME = "Focus Tracker"
WINDOW_W = 280
WINDOW_H = 90

# debug window for seeing what the AI sees
DEBUG_WINDOW_NAME = "Camera Detection (Dev Mode)"

# How long before we alert you
DISTRACTION_THRESHOLD = 10  # seconds
ALERT_SHOW_TIME = 3.0  # how long alert stays on screen
FOCUS_RESET = 3  # seconds of distraction to reset your streak


def main():
    print("Starting Focus Tracker...")
    print("Window hides behind your apps - only shows when distracted\n")
    detector = FocusDetector()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return 1

    # Create small window in corner
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_W, WINDOW_H)
    cv2.moveWindow(WINDOW_NAME, 20, 20)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 0)

    print("Press ESC to quit")
    print("Press 'c' to toggle developer mode (camera detection)\n")

    # timing stuff
    session_start = time.time()
    last_frame_time = session_start
    focus_manager = FocusManager(DISTRACTION_THRESHOLD)

    # Developer mode
    dev_mode = False
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            result = detector.process_frame(frame)

            # calculate time since last frame
            current_time = time.time()
            delta = current_time - last_frame_time
            last_frame_time = current_time

            # get what the AI detected
            status = result["status"]
            gaze = result.get("gaze_direction", "")
            on_phone = result.get("on_phone", False)

            # update tracking based on detection results
            state = focus_manager.update(status, gaze, on_phone, delta)
            status = state["status"]
            alert_message = state["alert_message"]
            focus_streak = state["focus_streak"]
            best_streak = state["best_streak"]
            distraction_streak = state["distraction_streak"]

            # make sure window shows up when there's an alert
            if state["show_topmost"]:
                cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
            else:
                cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 0)

            # check for keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC to quit
                break
            elif key == ord('c'):  # 'c' to toggle dev mode
                dev_mode = not dev_mode
                if dev_mode:
                    cv2.namedWindow(DEBUG_WINDOW_NAME, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(DEBUG_WINDOW_NAME, 960, 720)
                    print("Developer mode ON - showing camera detection")
                else:
                    cv2.destroyWindow(DEBUG_WINDOW_NAME)
                    print("Developer mode OFF")

            # show dev visualization if enabled
            if dev_mode:
                display_frame = draw_detection_overlay(frame.copy(), result)
                cv2.imshow(DEBUG_WINDOW_NAME, display_frame)

            # draw and show the main widget
            canvas = np.zeros((WINDOW_H, WINDOW_W, 3), dtype=np.uint8)
            draw_widget(canvas, status, focus_streak, best_streak, alert_message, distraction_streak)
            cv2.imshow(WINDOW_NAME, canvas)
                
    finally:
        # print out the results
        final_elapsed = time.time() - session_start
        summary = focus_manager.get_summary()
        final_score = (summary["focused_seconds"] / final_elapsed * 100) if final_elapsed > 0 else 0

        save_session(final_elapsed, summary["focused_seconds"], final_score)

        print("\n" + "=" * 40)
        print("SESSION DONE")
        print("=" * 40)
        print(f"Total Time:   {format_time(int(final_elapsed))}")
        print(f"Focused:      {format_time(int(summary['focused_seconds']))}")
        print(f"Best Streak:  {format_time(int(summary['best_streak']))}")
        print(f"Score:        {final_score:.1f}%")

        # feedback based on how well you did
        if final_score >= 80:
            print("\nStatus: Amazing focus!")
        elif final_score >= 60:
            print("\nStatus: Good Job!")
        elif final_score >= 40:
            print("\nStatus: Not bad keep trying")
        else:
            print("\nStatus: Got to focus more next time")

        print("=" * 40 + "\n")

        detector.cleanup()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    exit(main())