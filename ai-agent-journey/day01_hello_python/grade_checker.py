"""
Grade Checker Script
--------------------
Asks user for score (0-100) and returns grade A-F.
Refactored to separate pure grading logic from input/validation.
"""

def determine_grade(score: int) -> str:
    """Return A–F for a valid score 0–100. Assumes score already validated."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    elif score >= 50:
        return "E"
    else:
        return "F"


def grade_checker():
    """
    Get score from user, validate it, print grade.
    Keeps I/O separate from grading logic.
    """
    try:
        score = int(input("Enter your score (0-100): "))
    except ValueError:
        print("Please enter a whole number, like 72.")
        return

    if not (0 <= score <= 100):
        print("Invalid score. Please enter a number from 0 to 100.")
        return

    grade = determine_grade(score)
    print(f"Your grade is: {grade}")


if __name__ == "__main__":
    grade_checker()



