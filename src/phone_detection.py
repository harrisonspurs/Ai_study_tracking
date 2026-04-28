# detecting phones using mediapipe's object detection model

# OpenCV - for image processing
# from: https://opencv.org/
import cv2
import os
import urllib.request

# MediaPipe - free object detection model
# from: https://mediapipe.dev/
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
OBJECT_DETECTOR_URL = "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite"
OBJECT_DETECTOR_PATH = "object_detector.tflite"


def download_object_detector_model():
    if not os.path.exists(OBJECT_DETECTOR_PATH):
        print(f"Downloading object detector model to {OBJECT_DETECTOR_PATH}...")
        urllib.request.urlretrieve(OBJECT_DETECTOR_URL, OBJECT_DETECTOR_PATH)
        print("Done!")


class PhoneDetector:
    def __init__(self):
        download_object_detector_model()

        base_options = python.BaseOptions(model_asset_path=OBJECT_DETECTOR_PATH)
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            max_results=5,  # don't need to detect any more than 5 objects
            score_threshold=0.5,  # only confident detections so theres less annoying errors
        )
        self.detector = vision.ObjectDetector.create_from_options(options)

    def is_phone_detected(self, frame):
        h, w = frame.shape[:2]

        # convert to RGB for mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # run detection
        detection_result = self.detector.detect(mp_image)

        # look for objects labeled as phone or mobile
        phone_keywords = ["phone", "mobile"]

        # check each detected object
        for detection in detection_result.detections:
            category = detection.categories[0]
            label = category.category_name.lower()

            # see if this is a phone
            found_phone = False
            for keyword in phone_keywords:
                if keyword in label:
                    found_phone = True
                    break

            if found_phone:
                return True

        return False

    def cleanup(self):
        if self.detector:
            self.detector = None
