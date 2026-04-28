# detecting face landmarks using mediapipe
# also runs phone object detection to check if user is on their phone

# OpenCV - for image processing
# from: https://opencv.org/
import cv2
import os
import urllib.request

# MediaPipe - free face detection and landmark tracking
# from: https://mediapipe.dev/
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# internal modules
from .phone_detection import PhoneDetector

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = "face_landmarker.task"

# landmark points from mediapipe's face mesh
# representing different parts of the face nose, eyes, temple, etc.
NOSE_TIP = 1
CHIN = 152
LEFT_TEMPLE = 234
RIGHT_TEMPLE = 454
FOREHEAD = 10
LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133
RIGHT_EYE_OUTER = 362
RIGHT_EYE_INNER = 263
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473


def download_model():
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading model to {MODEL_PATH}...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Done!")


class FocusDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        download_model()

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=min_detection_confidence,
            min_face_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

        # Initialize phone detector
        self.phone_detector = PhoneDetector()

    def get_head_direction(self, landmarks):
        nose = landmarks[NOSE_TIP]
        left_temple = landmarks[LEFT_TEMPLE]
        right_temple = landmarks[RIGHT_TEMPLE]
        forehead = landmarks[FOREHEAD]
        chin = landmarks[CHIN]

        # how far left/right the nose is between the temples
        temple_span = max(0.000001, right_temple.x - left_temple.x)
        h_ratio = (nose.x - left_temple.x) / temple_span

        # how far up/down is the nose between forehead and chin
        v_span = max(0.000001, chin.y - forehead.y)
        v_ratio = (nose.y - forehead.y) / v_span

        looking_left = h_ratio < 0.35
        looking_right = h_ratio > 0.65
        looking_down = v_ratio > 0.75
        looking_up = v_ratio < 0.25

        return looking_left, looking_right, looking_down, looking_up

    def get_eye_direction(self, landmarks):
        # where is the iris in each eye?
        left_outer = landmarks[LEFT_EYE_OUTER]
        left_inner = landmarks[LEFT_EYE_INNER]
        left_iris = landmarks[LEFT_IRIS_CENTER]

        right_outer = landmarks[RIGHT_EYE_OUTER]
        right_inner = landmarks[RIGHT_EYE_INNER]
        right_iris = landmarks[RIGHT_IRIS_CENTER]

        # calculate how far left to right each iris is
        left_span = max(0.000001, left_inner.x - left_outer.x)
        left_ratio = (left_iris.x - left_outer.x) / left_span

        if left_ratio < 0:
            left_ratio = 0
        if left_ratio > 1:
            left_ratio = 1

        right_span = max(0.000001, right_inner.x - right_outer.x)
        right_ratio = (right_iris.x - right_outer.x) / right_span

        if right_ratio < 0:
            right_ratio = 0
        if right_ratio > 1:
            right_ratio = 1

        avg_ratio = (left_ratio + right_ratio) / 2

        eyes_left = avg_ratio < 0.35
        eyes_right = avg_ratio > 0.65

        return eyes_left, eyes_right

    def get_gaze_label(self, head_left, head_right, head_down, head_up, eyes_left, eyes_right):
        if head_down:
            return "looking down"
        if head_up:
            return "looking up"
        if head_left or eyes_left:
            return "looking left"
        if head_right or eyes_right:
            return "looking right"
        return "forward"

    def get_face_bbox(self, landmarks, w, h):
        # find the min/max positions of all face points
        xs = []
        ys = []
        for lm in landmarks:
            xs.append(int(lm.x * w))
            ys.append(int(lm.y * h))

        x_min = max(0, min(xs))
        y_min = max(0, min(ys))
        x_max = min(w - 1, max(xs))
        y_max = min(h - 1, max(ys))

        return {"x": x_min, "y": y_min, "width": x_max - x_min, "height": y_max - y_min}

    def draw_mesh(self, frame, landmarks, w, h):
        for lm in landmarks:
            x = int(lm.x * w)
            y = int(lm.y * h)
            cv2.circle(frame, (x, y), 1, (180, 180, 180), 1)

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.landmarker.detect(mp_image)

        # check if phone is in the frame
        on_phone = self.phone_detector.is_phone_detected(frame)

        # no face detected
        if not result.face_landmarks:
            return {
                "face_detected": False,
                "status": "Away",
                "bbox": None,
                "gaze_direction": "no face",
                "on_phone": on_phone,
            }

        landmarks = result.face_landmarks[0]
        self.draw_mesh(frame, landmarks, w, h)

        # calculate where the head and eyes are pointing
        head_left, head_right, head_down, head_up = self.get_head_direction(landmarks)
        eyes_left, eyes_right = self.get_eye_direction(landmarks)

        gaze = self.get_gaze_label(head_left, head_right, head_down, head_up, eyes_left, eyes_right)

        head_turned = head_left or head_right
        head_tilted = head_down or head_up
        eyes_away = eyes_left or eyes_right

        # if looking straight at screen, you're focused
        if not head_turned and not head_tilted and not eyes_away:
            status = "Focused"
        else:
            status = "Distracted"

        return {
            "face_detected": True,
            "status": status,
            "bbox": self.get_face_bbox(landmarks, w, h),
            "gaze_direction": gaze,
            "on_phone": on_phone,
        }

    def cleanup(self):
        if self.landmarker:
            self.landmarker.close()
        if self.phone_detector:
            self.phone_detector.cleanup()
