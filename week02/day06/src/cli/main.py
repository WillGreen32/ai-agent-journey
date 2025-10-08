import os
from src.core.manager import TaskManager

DATA_PATH = "data/tasks.json"

def main():
    os.makedirs("data", exist_ok=True)
    m = TaskManager(data_path=DATA_PATH)
    m.load()

    while True:
        print(f"\n=== Task Manager (tasks: {len(m.tasks)}) ===")
        print("[1] Add  [2] View  [3] Edit  [4] Delete  [5] Complete  [s] Save  [q] Quit")
        choice = input("Choose: ").strip().lower()

        try:
            if choice == "1":
                title = input("Title: ").strip()
                desc = input("Description (optional): ")
                if title:
                    tid = m.add(title, desc)
                    print(f"✅ Added id={tid}")
                else:
                    print("⚠️  Title required.")
            elif choice == "2":
                if not m.tasks:
                    print("No tasks yet.")
                else:
                    for i, (tid, t) in enumerate(m.tasks.items(), start=1):
                        mark = "✓" if t.completed else "•"
                        print(f"{i}. {mark} {t.title}  ({tid})")
            elif choice == "3":
                tid = input("Task id to edit: ").strip()
                new_title = input("New title (blank=skip): ")
                new_desc = input("New desc (blank=skip): ")
                kwargs = {}
                if new_title != "": kwargs["title"] = new_title
                if new_desc != "": kwargs["description"] = new_desc
                m.edit(tid, **kwargs)
                print("✏️  Updated.")
            elif choice == "4":
                tid = input("Task id to delete: ").strip()
                m.delete(tid)
                print("🗑️  Deleted.")
            elif choice == "5":
                tid = input("Task id to complete: ").strip()
                m.complete(tid)
                print("✅ Completed.")
            elif choice == "s":
                m.save()
                print("💾 Saved.")
            elif choice == "q":
                m.save()
                print("💾 Saved. Bye 👋")
                break
            else:
                print("Invalid option.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
