try:
    age = int(input("Enter your age: "))
    if age >= 18:
        print("Adult")
    else:
        print("Minor")
except ValueError:
    print("Please enter a whole number (e.g., 17).")

