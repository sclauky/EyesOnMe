import cv2

from core.camera import initialize_camera
from core.hand_tracking import initialize_hand_tracker, detect_hands
from core.gesture_detection import initialize_gesture_state, detect_gestures
from core.mouse_control import initialize_mouse_state, update_mouse_control, move_mouse
from core.display import display_hands, should_quit, close_display


def main():
    camera = initialize_camera()
    gesture_state = initialize_gesture_state()
    mouse_state = initialize_mouse_state()
    previous_hands = {}

    print("EyesOnMe is running! Press Q to quit.")

    try:
        with initialize_hand_tracker() as detector:
            while True:
                success, image = camera.read()

                if not success:
                    print("Unable to read the webcam image.")
                    break

                image = cv2.flip(image, 1)
                height, width, _ = image.shape

                timestamp_ms = int(
                    cv2.getTickCount() * 1000 / cv2.getTickFrequency()
                )

                current_hands = detect_hands(
                    detector,
                    image,
                    previous_hands,
                    timestamp_ms
                )

                hand_gestures = detect_gestures(
                    current_hands,
                    gesture_state
                )

                update_mouse_control(hand_gestures, mouse_state)

                display_hands(image, current_hands, hand_gestures)

                move_mouse(current_hands, mouse_state, width, height)

                previous_hands = current_hands

                if should_quit():
                    break

    finally:
        camera.release()
        close_display()


if __name__ == "__main__":
    main()