import cv2


CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


def display_hands(image, current_hands, hand_gestures):
    for label, points in current_hands.items():
        pixel_points = [(int(x), int(y)) for x, y in points]

        for start, end in CONNECTIONS:
            cv2.line(
                image,
                pixel_points[start],
                pixel_points[end],
                (0, 255, 0),
                2
            )

        for index, (x, y) in enumerate(pixel_points):
            color = (
                (255, 180, 0)
                if index in (4, 8, 12, 16, 20)
                else (0, 200, 255)
            )
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


def should_quit():
    return cv2.waitKey(1) & 0xFF == ord("q")


def close_display():
    cv2.destroyAllWindows()