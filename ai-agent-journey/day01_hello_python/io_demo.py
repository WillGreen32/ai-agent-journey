# --- Simple input/output ---
user = input("Your name: ")
print(f"Hi {user}! Nice to meet you.")

# --- Age example ---
age_str = input("Your age: ")
# input() returns string → must convert to int
try:
    age = int(age_str)   # safe conversion
    print(f"Cool, in 5 years you’ll be {age + 5}.")
except ValueError:
    print("That doesn’t look like a valid number.")
