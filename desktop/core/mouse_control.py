import pyautogui


pyautogui.PAUSE = 0

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


def initialize_mouse_state():
    return {
        "enabled": False,
        "previous_peace_sign": False
    }


def update_mouse_control(hand_gestures, state):
    peace_sign_detected = any(
        gesture == "Peace Sign"
        for gesture in hand_gestures.values()
    )

    if peace_sign_detected and not state["previous_peace_sign"]:
        state["enabled"] = not state["enabled"]

        print(
            "Mouse control enabled."
            if state["enabled"]
            else "Mouse control disabled."
        )

    state["previous_peace_sign"] = peace_sign_detected


def move_mouse(current_hands, state, width, height):
    if not state["enabled"] or not current_hands:
        return

    active_hand = next(iter(current_hands.values()))
    index_x, index_y = active_hand[8]

    zone_left = 0.15
    zone_right = 0.85
    zone_top = 0.15
    zone_bottom = 0.85

    normalized_x = index_x / width
    normalized_y = index_y / height

    normalized_x = max(zone_left, min(normalized_x, zone_right))
    normalized_y = max(zone_top, min(normalized_y, zone_bottom))

    mouse_x = int(
        (normalized_x - zone_left)
        / (zone_right - zone_left)
        * SCREEN_WIDTH
    )
    mouse_y = int(
        (normalized_y - zone_top)
        / (zone_bottom - zone_top)
        * SCREEN_HEIGHT
    )

    margin = 10

    mouse_x = max(margin, min(mouse_x, SCREEN_WIDTH - margin - 1))
    mouse_y = max(margin, min(mouse_y, SCREEN_HEIGHT - margin - 1))

    pyautogui.moveTo(mouse_x, mouse_y, duration=0)