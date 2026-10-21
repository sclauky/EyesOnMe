
import cv2
import mediapipe as mp
from pathlib import Path

model_path = Path(__file__).parent / "models" / "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(model_path)),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Impossible to open the webcam.")
    raise SystemExit

print("EyesOnMe is running! Press Q to quit.")

with HandLandmarker.create_from_options(options) as detector:
    while True:
        success, image = camera.read()

        if not success:
            print("Impossible to read your webcam image.")
            break

        image = cv2.flip(image, 1)
        height, width, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_image
        )

        timestamp_ms = int(cv2.getTickCount() * 1000 / cv2.getTickFrequency())
        results = detector.detect_for_video(mp_image, timestamp_ms)

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                points = []

                for landmark in hand_landmarks:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    points.append((x, y))

                for start, end in connections:
                    cv2.line(image, points[start], points[end], (0, 255, 0), 2)

                for x, y in points:
                    cv2.circle(image, (x, y), 5, (0, 200, 255), -1)

        cv2.imshow("EyesOnMe - Hands detection", image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()