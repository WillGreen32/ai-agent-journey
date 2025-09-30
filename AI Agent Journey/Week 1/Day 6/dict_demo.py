prices = {"apple": 2.5, "banana": 1.8}

# Direct indexing (can raise KeyError)
print("Direct indexing:")
print("apple ->", prices["apple"])    # works
print("orange ->", prices["orange"])  # will raise KeyError

# Safe get (no KeyError)
print("\nSafe .get():")
print("apple ->", prices.get("apple", "Not sold"))
print("orange ->", prices.get("orange", "Not sold"))
