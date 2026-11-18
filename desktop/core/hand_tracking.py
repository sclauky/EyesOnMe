import cv2
import mediapipe as mp
from pathlib import Path
from math import hypot


MODEL_PATH = Path(__file__).parent.parent / "models" / "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def initialize_hand_tracker():
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6
    )

    return HandLandmarker.create_from_options(options)


def detect_hands(detector, image, previous_hands, timestamp_ms):
    height, width, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image
    )

    results = detector.detect_for_video(mp_image, timestamp_ms)
    current_hands = {}

    if results.hand_landmarks:
        for hand_index, hand_landmarks in enumerate(results.hand_landmarks):
            label = results.handedness[hand_index][0].category_name
            label = "Right" if label == "Left" else "Left"

            points = [
                [landmark.x * width, landmark.y * height]
                for landmark in hand_landmarks
            ]

            if label in previous_hands:
                old_points = previous_hands[label]

                movement = sum(
                    hypot(
                        point[0] - old_point[0],
                        point[1] - old_point[1]
                    )
                    for point, old_point in zip(points, old_points)
                ) / len(points)

                if movement < 2:
                    alpha = 0.15
                elif movement < 8:
                    alpha = 0.35
                else:
                    alpha = 0.75

                points = [
                    [
                        alpha * point[0] + (1 - alpha) * old_point[0],
                        alpha * point[1] + (1 - alpha) * old_point[1]
                    ]
                    for point, old_point in zip(points, old_points)
                ]

            current_hands[label] = points

    return current_hands