"""Command-line interface for Task Manager v3.

This file handles user interaction, input validation, and navigation logic.
It calls the TaskManager (core logic) and never directly manipulates files.
"""
from __future__ import annotations

import os
from src.core.manager import TaskManager

# Path to our persistent task file
DATA_PATH = "data/tasks.json"

# ---------- Presentation Helpers ----------
def separator(width: int = 36) -> None:
    """Print a visual separator line."""
    print("─" * width)


def print_header() -> None:
    """Prints the CLI header for every loop."""
    print("\n✨ Task Manager v3 ✨")
    separator()


def print_menu(task_count: int) -> None:
    """Show menu options with task count."""
    print(f"({task_count} tasks)")
    print("[1] Add  [2] View  [3] Edit  [4] Delete  [Q] Quit")


# ---------- Input Safety Helpers ----------
def read_int(prompt: str) -> int | None:
    """Read an integer safely, returning None if input isn't valid."""
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("❌ Please enter a number, not text.")
        return None


def safe_index(prompt: str, upper_bound: int) -> int | None:
    """Return 0-based valid index within [0, upper_bound)."""
    n = read_int(prompt)
    if n is None:
        return None
    idx = n - 1  # convert 1-based → 0-based
    if idx < 0 or idx >= upper_bound:
        print("⚠️ That task number doesn’t exist.")
        return None
    return idx

def main() -> None:
    """Run the interactive CLI loop for Task Manager."""
    os.makedirs("data", exist_ok=True)
    manager = TaskManager()
    manager.load(DATA_PATH)

    print("\n✨ Welcome to Task Manager v3 ✨")
    separator()

    while True:
        print_header()
        print_menu(len(manager.tasks))
        choice = input("Choose an option: ").strip().lower()

        # --- Normalize common letters to numbers ---
        if choice in {"a"}:
            choice = "1"
        elif choice in {"v"}:
            choice = "2"
        elif choice in {"e"}:
            choice = "3"
        elif choice in {"d"}:
            choice = "4"
        elif choice in {"q", "quit", "exit"}:
            choice = "q"

        # --- Add ---
        if choice == "1":
            title = input("Task title: ").strip()
            if title:
                manager.add_task(title)
                print("✅ Task added successfully!")
            else:
                print("ℹ️ Nothing added (empty title).")

        # --- View ---
        elif choice == "2":
            manager.view_tasks()
            separator()

        # --- Edit ---
        elif choice == "3":
            if not manager.tasks:
                print("ℹ️ No tasks to edit yet.")
            else:
                manager.view_tasks()
                idx = safe_index("Task number to edit: ", len(manager.tasks))
                if idx is not None:
                    new_title = input("New title: ").strip()
                    if new_title:
                        try:
                            manager.edit_task(idx, new_title)
                            print("✏️  Task updated.")
                        except IndexError:
                            print("⚠️ That task number doesn’t exist.")
                    else:
                        print("ℹ️ Title unchanged.")

        # --- Delete ---
        elif choice == "4":
            if not manager.tasks:
                print("ℹ️ No tasks to delete yet.")
            else:
                manager.view_tasks()
                idx = safe_index("Task number to delete: ", len(manager.tasks))
                if idx is not None:
                    try:
                        manager.delete_task(idx)
                        print("🗑️  Task deleted.")
                    except IndexError:
                        print("⚠️ That task number doesn’t exist.")

        # --- Quit ---
        elif choice == "q":
            ans = input("Save changes before quitting? [Y/n]: ").strip().lower()
            if ans in {"", "y", "yes"}:
                manager.save(DATA_PATH)
                print("💾 All changes saved.")
            print("👋 Goodbye!")
            break

        # --- Invalid ---
        else:
            print("❓ Not a valid option. Try 1/2/3/4 or Q.")


if __name__ == "__main__":
    main()
