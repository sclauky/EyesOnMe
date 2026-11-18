def initialize_gesture_state():
    return {
        "previous_gestures": {},
        "gesture_candidates": {},
        "gesture_counts": {}
    }


def detect_gestures(current_hands, state):
    hand_gestures = {}

    for label, points in current_hands.items():
        finger_tips = [8, 12, 16, 20]

        extended_fingers = [
            points[tip][1] < points[tip - 2][1]
            for tip in finger_tips
        ]

        if (
            extended_fingers[0]
            and extended_fingers[1]
            and not extended_fingers[2]
            and not extended_fingers[3]
        ):
            detected_gesture = "Peace Sign"
        elif sum(extended_fingers) >= 3:
            detected_gesture = "Open Hand"
        else:
            detected_gesture = "Closed Hand"

        if state["gesture_candidates"].get(label) == detected_gesture:
            state["gesture_counts"][label] = (
                state["gesture_counts"].get(label, 0) + 1
            )
        else:
            state["gesture_candidates"][label] = detected_gesture
            state["gesture_counts"][label] = 1

        if state["gesture_counts"][label] >= 5:
            state["previous_gestures"][label] = detected_gesture

        hand_gestures[label] = state["previous_gestures"].get(
            label,
            detected_gesture
        )

    return hand_gestures