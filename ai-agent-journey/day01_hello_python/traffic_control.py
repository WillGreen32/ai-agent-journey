"""
Traffic Control — Nested Decisions with Validation
--------------------------------------------------
Supported lights: green, yellow, red, flashing
Rules:
- green:
    - if button pressed:
        - if crossing guard present -> "Wait for the guard's signal."
        - else -> "Wait for pedestrians, then proceed carefully."
    - else -> "Drive."
- yellow -> "Prepare to stop."
- red -> "Stop."
- flashing -> "Proceed with caution."
"""

from typing import Literal


def ask_light() -> Literal["green", "yellow", "red", "flashing"]:
    """Ask until user enters a valid traffic light color."""
    valid = ("green", "yellow", "red", "flashing")
    while True:
        val = input("Traffic light (green/yellow/red/flashing): ").strip().lower()
        if val in valid:
            return val  # type: ignore[return-value]
        print("Please enter: green, yellow, red, or flashing.")


def ask_yes_no(prompt: str) -> bool:
    """Ask a yes/no question until valid; return True for 'y', False for 'n'."""
    while True:
        val = input(f"{prompt} (y/n): ").strip().lower()
        if val == "y":
            return True
        if val == "n":
            return False
        print("Please type 'y' or 'n'.")


def decide_action(light: Literal["green", "yellow", "red", "flashing"]) -> str:
    """Return the correct action message for a given light."""
    if light == "green":
        button_pressed = ask_yes_no("Is the pedestrian button pressed?")
        if not button_pressed:
            return "Drive."
        guard_present = ask_yes_no("Is a crossing guard present?")
        if guard_present:
            return "Wait for the guard's signal."
        return "Wait for pedestrians, then proceed carefully."

    if light == "yellow":
        return "Prepare to stop."

    if light == "red":
        return "Stop."

    # flashing
    return "Proceed with caution."


def main() -> None:
    light = ask_light()
    action = decide_action(light)
    print(action)


if __name__ == "__main__":
    main()
