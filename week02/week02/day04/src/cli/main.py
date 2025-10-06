# week02/day04/src/cli/main.py
from typing import List
from src.models.task import Task

def print_menu(count: int) -> None:
    print(f"\n=== Task Manager v1 ({count} tasks) ===")
    print("[1] Add task")
    print("[2] View tasks")
    print("[q] Quit")


def handle_add(tasks: List[Task]) -> None:
    title = input("Task title: ").strip()
    if not title:
        print("⚠️  Title cannot be empty.")
        # one gentle retry
        title = input("Task title: ").strip()
        if not title:
            print("❌ Cancelled add.")
            return

    tasks.append(Task(title=title))
    print("✅ Task added!")



from typing import List
from src.models.task import Task

def handle_view(tasks: List[Task]) -> None:
    if not tasks:
        print("No tasks yet.")
        return

    print("\nYour tasks:")
    width = len(str(len(tasks)))  # dynamic width: 1..9 aligns with 10..99 etc.
    for i, t in enumerate(tasks, start=1):
        print(f"{str(i).rjust(width)}. {t.to_display()}")



def main() -> None:
    tasks: List[Task] = []
    while True:
        print_menu(len(tasks))
        choice = input("Choose: ").strip().lower()
        if choice == "1":
            handle_add(tasks)
        elif choice == "2":
            handle_view(tasks)
        elif choice == "q":
            print("Bye 👋")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
