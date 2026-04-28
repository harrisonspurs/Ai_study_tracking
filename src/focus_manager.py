# manages all the focus tracking logic - timers, streaks, alert state
# keeps track of how long you've been focused and when to show alerts

from .alerts import get_alert


class FocusManager:
    def __init__(self, distraction_threshold=10):
        # timing stuff
        self.focused_seconds = 0.0
        self.last_frame_time = None

        # tracking focus streaks and distraction
        self.focus_streak = 0.0
        self.best_streak = 0.0
        self.distraction_streak = 0.0

        # alerts management
        self.alert_message = ""
        self.alert_timer = 0.0
        self.phone_alert_timer = 0.0
        self.PHONE_ALERT_TIME = 3.0
        self.ALERT_SHOW_TIME = 3.0
        self.FOCUS_RESET = 3  # seconds to wait before resetting streak
        self.distraction_threshold = distraction_threshold

    def update(self, status, gaze, on_phone, delta):
    # update the focus score based on the detection results

        # if phone detected show alert immediately
        if on_phone and self.phone_alert_timer <= 0:
            status = "Distracted"
            self.phone_alert_timer = self.PHONE_ALERT_TIME
            self.alert_message = "PHONE!"
            self.alert_timer = 0
            show_topmost = True
        else:
            show_topmost = False

        # keep distracted status while phone alert is showing
        if self.phone_alert_timer > 0:
            status = "Distracted"

        # update the focus/distraction time
        if status == "Focused":
            self.focused_seconds += delta
            self.focus_streak += delta
            if self.focus_streak > self.best_streak:
                self.best_streak = self.focus_streak
            self.distraction_streak = 0
        else:
            self.distraction_streak += delta
            if self.distraction_streak > self.FOCUS_RESET:
                self.focus_streak = 0

        # count down phone alert timer
        if self.phone_alert_timer > 0:
            self.phone_alert_timer -= delta
            if self.phone_alert_timer <= 0:
                self.alert_message = ""
                show_topmost = True

        # show distraction alert if no other alerts are showing
        if self.phone_alert_timer <= 0 and self.alert_timer <= 0 and not self.alert_message:
            self.alert_message = get_alert(status, gaze, self.distraction_streak, self.distraction_threshold)
            if self.alert_message:
                self.alert_timer = self.ALERT_SHOW_TIME
                show_topmost = True

        # count down regular alert timer
        if self.alert_timer > 0:
            self.alert_timer -= delta
            if self.alert_timer <= 0:
                self.alert_message = ""
                show_topmost = True

        return {
            "status": status,
            "focused_seconds": self.focused_seconds,
            "focus_streak": self.focus_streak,
            "best_streak": self.best_streak,
            "distraction_streak": self.distraction_streak,
            "alert_message": self.alert_message,
            "show_topmost": show_topmost
        }

    def get_summary(self):
        """get session summary data"""
        return {
            "focused_seconds": self.focused_seconds,
            "best_streak": self.best_streak
        }
