import cv2
import mediapipe as mp
from pathlib import Path
from math import hypot

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

previous_hands = {}

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
    print("Unable to open the webcam.")
    raise SystemExit

print("EyesOnMe is running! Press Q to quit.")

with HandLandmarker.create_from_options(options) as detector:
    while True:
        success, image = camera.read()

        if not success:
            print("Unable to read the webcam image.")
            break

        image = cv2.flip(image, 1)
        height, width, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_image
        )

        timestamp_ms = int(
            cv2.getTickCount() * 1000 / cv2.getTickFrequency()
        )
        results = detector.detect_for_video(mp_image, timestamp_ms)

        current_hands = {}
        hand_gestures = {}

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

                finger_tips = [8, 12, 16, 20]
                extended_fingers = sum(
                    points[tip][1] < points[tip - 2][1]
                    for tip in finger_tips
                )

                if extended_fingers >= 3:
                    hand_gestures[label] = "Open Hand"
                else:
                    hand_gestures[label] = "Closed Hand"

        previous_hands = current_hands

        for label, points in current_hands.items():
            pixel_points = [(int(x), int(y)) for x, y in points]

            for start, end in connections:
                cv2.line(
                    image,
                    pixel_points[start],
                    pixel_points[end],
                    (0, 255, 0),
                    2
                )

            for index, (x, y) in enumerate(pixel_points):
                color = (255, 180, 0) if index in (4, 8, 12, 16, 20) else (0, 200, 255)
                cv2.circle(image, (x, y), 5, color, -1)

            cv2.putText(
                image,
                label,
                (pixel_points[0][0], pixel_points[0][1] + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        for label, gesture in hand_gestures.items():
            cv2.putText(
                image,
                f"{label}: {gesture}",
                (20, 40 if label == "Left" else 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

        cv2.imshow("EyesOnMe - Hand Tracking", image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()