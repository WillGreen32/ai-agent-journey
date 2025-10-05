# src/cli/main.py
from datetime import timedelta, datetime
from src.task import Task, UrgentTask, RecurringTask, CompletedTask
from src.utils import slugify, parse_date

def demo():
    t1 = Task("Write README", due=datetime.utcnow() + timedelta(days=2), priority=2)
    t2 = UrgentTask("Fix failing tests", hours=6)
    t3 = RecurringTask("Weekly review", interval_days=7)
    t4 = CompletedTask("Set up repo")

    for t in (t1, t2, t3, t4):
        print(t, "| slug:", slugify(t.title))

    print("Parsed date:", parse_date("02/10/2025"))

if __name__ == "__main__":
    demo()
