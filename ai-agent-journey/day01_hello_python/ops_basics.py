print("=== Arithmetic ===")
print("5 + 2  =", 5 + 2)     # addition
print("5 - 2  =", 5 - 2)     # subtraction
print("5 * 2  =", 5 * 2)     # multiplication
print("5 / 2  =", 5 / 2)     # true division -> float
print("5 // 2 =", 5 // 2)    # floor division -> whole pages/batches
print("5 % 2  =", 5 % 2)     # remainder -> use for 'every N items'
print("5 ** 2 =", 5 ** 2)    # exponent -> 25

print("\n=== Comparisons (return booleans) ===")
print("3 > 2      ->", 3 > 2)
print("2 < 5      ->", 2 < 5)
print("3 == 3     ->", 3 == 3)   # equality
print("1 == 2     ->", 1 == 2)
print("3 != 2     ->", 3 != 2)   # not equal

print("\n=== Logic (combine booleans) ===")
print("(3 > 2) and (2 < 5) ->", (3 > 2) and (2 < 5))
print("(3 == 3) or (1 == 2) ->", (3 == 3) or (1 == 2))
print("not False ->", not False)

# extras you’ll use a lot:
print("\n=== Practical extras ===")
items = 23
page_size = 5
pages = (items + page_size - 1) // page_size  # ceiling division for pages
print("Items:", items, "Page size:", page_size, "Pages needed:", pages)

i = 12
print("Log every 5th:", "LOG!" if i % 5 == 0 else "skip")
