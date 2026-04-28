# tests for the study tracker modules

import json
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np

from src.detection import FocusDetector
from src.session import save_session
from src.utils import format_time


class TestUtils(unittest.TestCase):
    def test_format_time_values(self):
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(65), "01:05")
        self.assertEqual(format_time(3600), "60:00")


class TestSession(unittest.TestCase):
    def setUp(self):
        self.created_files = []

    def tearDown(self):
        for file_path in self.created_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    @patch("src.session.datetime")
    def test_save_session_creates_json(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2099, 1, 2, 3, 4, 5)

        filepath = save_session(
            elapsed_seconds=125.9,
            focused_seconds=75.2,
            focus_score=59.949,
        )
        self.created_files.append(filepath)

        self.assertTrue(filepath.startswith(os.path.join("data", "sessions")))
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, "r") as f:
            payload = json.load(f)

        expected_keys = {"date", "time", "duration_seconds", "focused_seconds",
                         "focus_score", "duration_formatted", "focused_formatted"}
        self.assertEqual(set(payload.keys()), expected_keys)
        self.assertEqual(payload["focus_score"], 59.9)


class TestFocusDetector(unittest.TestCase):
    @patch("src.detection.vision.FaceLandmarker.create_from_options")
    @patch("src.detection.vision.FaceLandmarkerOptions")
    @patch("src.detection.python.BaseOptions")
    @patch("src.detection.download_model")
    def test_initializes_ok(self, _mock_download, _mock_base, _mock_opts, mock_create):
        mock_create.return_value = MagicMock()
        detector = FocusDetector()
        self.assertIsNotNone(detector)

    @patch("src.detection.mp.Image")
    @patch("src.detection.cv2.cvtColor")
    @patch("src.detection.vision.FaceLandmarker.create_from_options")
    @patch("src.detection.vision.FaceLandmarkerOptions")
    @patch("src.detection.python.BaseOptions")
    @patch("src.detection.download_model")
    def test_process_frame_no_face_returns_away(self, _mock_download, _mock_base,
                                                 _mock_opts, mock_create,
                                                 mock_cvt, mock_mp_image):
        fake_landmarker = MagicMock()
        fake_landmarker.detect.return_value = MagicMock(face_landmarks=[])
        mock_create.return_value = fake_landmarker

        mock_cvt.return_value = "rgb_frame"
        mock_mp_image.return_value = "mp_image"

        detector = FocusDetector()
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        result = detector.process_frame(frame)

        self.assertIsInstance(result, dict)
        self.assertIn("face_detected", result)
        self.assertIn("bbox", result)
        self.assertIn("status", result)
        self.assertIn("gaze_direction", result)
        self.assertEqual(result["status"], "Away")
        self.assertFalse(result["face_detected"])
        self.assertIsNone(result["bbox"])


if __name__ == "__main__":
    unittest.main()
