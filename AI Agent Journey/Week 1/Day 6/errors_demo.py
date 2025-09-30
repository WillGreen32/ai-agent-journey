while True:
    raw = input("Enter a number (or 'q' to quit): ")
    if raw.lower() == "q":
        print("Goodbye!")
        break
    try:
        x = int(raw)
        result = 100 / x
    except ValueError:
        print("Numbers only, please.\n")
        continue
    except ZeroDivisionError:
        print("You can’t divide by zero.\n")
        continue
    else:
        print("Result:", result)
        break



