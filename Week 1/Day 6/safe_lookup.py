# safe_lookup.py
prices = {"apple": 2.5, "banana": 1.8}

try:
    key = input("Enter a fruit name: ").strip().lower()
    # risky dictionary access
    print("Price:", prices[key])
except KeyError as e:
    print("Key not found:", e)

