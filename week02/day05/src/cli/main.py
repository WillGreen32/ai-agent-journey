# src/cli/main.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from src.managers.task_manager import TaskManager

# Single source of truth for where we persist
DATA_PATH = "data/tasks.json"


# ---------- CLI helpers (UI concerns only) ----------

def clear() -> None:
    # Small nicety; if you don't want screen clearing, remove this.
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def print_header(manager: TaskManager) -> None:
    print(f"\n=== Task Manager v2 ({manager.count()} tasks) ===")


def print_menu() -> None:
    print("[1] Add")
    print("[2] View")
    print("[3] Edit")
    print("[4] Delete")
    print("[s] Save now")
    print("[q] Quit")


def prompt_int(prompt: str) -> Optional[int]:
    """Return int typed by user or None if invalid (no crash)."""
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("⚠️  Please enter a number.")
        return None


def show_list(manager: TaskManager) -> None:
    lines = manager.list_tasks()
    print("\n".join(lines) if lines else "No tasks yet.")


# ---------- Flows for each action ----------

def add_flow(manager: TaskManager) -> None:
    title = input("Task title: ").strip()
    if not title:
        print("⚠️  Title cannot be empty.")
        return
    try:
        manager.add_task(title)
        print("✅ Added!")
    except ValueError as e:
        print(f"⚠️  {e}")


def view_flow(manager: TaskManager) -> None:
    show_list(manager)


def edit_flow(manager: TaskManager) -> None:
    show_list(manager)
    if manager.count() == 0:
        return
    n = prompt_int("Task # to edit: ")
    if n is None:
        return
    idx = n - 1  # UI is 1-based; manager is 0-based
    new_title = input("New title: ")
    ok = manager.edit_task(idx, new_title)
    print("✏️  Updated!" if ok else "⚠️  Invalid task # or title.")


def delete_flow(manager: TaskManager) -> None:
    show_list(manager)
    if manager.count() == 0:
        return
    n = prompt_int("Task # to delete: ")
    if n is None:
        return
    idx = n - 1
    ok = manager.delete_task(idx)
    print("🗑️  Deleted!" if ok else "⚠️  Invalid task #.")


def save_now_flow(manager: TaskManager, path: str = DATA_PATH) -> None:
    print("💾 Saved." if manager.save_to_json(path) else "⚠️  Save failed.")


# ---------- Entrypoint ----------

def main() -> None:
    # Ensure data folder exists even if user saves immediately
    Path(DATA_PATH).parent.mkdir(parents=True, exist_ok=True)

    m = TaskManager()
    # Autoload on start
    m.load_from_json(DATA_PATH)

    while True:
        print_header(m)
        print_menu()
        choice = input("Choose: ").strip().lower()

        if choice == "1":
            add_flow(m)
        elif choice == "2":
            view_flow(m)
        elif choice == "3":
            edit_flow(m)
        elif choice == "4":
            delete_flow(m)
        elif choice == "s":
            save_now_flow(m)
        elif choice == "q":
            # Autosave on quit
            m.save_to_json(DATA_PATH)
            print("💾 Saved. Bye 👋")
            break
        else:
            print("Invalid option.")
        # optional: small visual separator
        # input("\n(Press Enter to continue)")
        # clear()


if __name__ == "__main__":
    main()
