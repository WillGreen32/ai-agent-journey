# day5_slicing_drill.py
# Mini-Drill: Slicing
# Goal: practice grabbing parts (slices) of a list safely

# 1) Setup
fruits = ["apple", "banana", "cherry", "orange", "mango"]
print("fruits:", fruits)  # sanity check

# 2) Drill slices
first_two = fruits[:2]       # from start up to (not including) index 2
middle = fruits[1:4]         # indexes 1,2,3
evens = fruits[::2]          # every 2nd item (step = 2)
reversed_fruits = fruits[::-1]  # reverse order (negative step)

# 3) Show results
print("first_two:", first_two)               # expect ['apple', 'banana']
print("middle:", middle)                     # expect ['banana', 'cherry', 'orange']
print("evens (every 2nd):", evens)          # expect ['apple', 'cherry', 'mango']
print("reversed_fruits:", reversed_fruits)  # expect ['mango', 'orange', 'cherry', 'banana', 'apple']

# 4) Safety checks: slicing doesn't IndexError even if you go "too far"
print("safe big slice:", fruits[0:99])       # expect whole list
print("safe negative start:", fruits[-99:2]) # expect ['apple', 'banana']

# 5) Optional: quick self-check assertions (comment out if you don’t want them)
assert first_two == ["apple", "banana"]
assert middle == ["banana", "cherry", "orange"]
assert evens == ["apple", "cherry", "mango"]
assert reversed_fruits == ["mango", "orange", "cherry", "banana", "apple"]

print("✅ All slicing checks passed!")
