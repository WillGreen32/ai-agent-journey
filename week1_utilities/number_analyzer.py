# --- Basic True/False checks ---

print(5 > 3)       # Is 5 greater than 3?  → True
print(10 == 2*5)   # Is 10 equal to 2*5?  → True
print(7 <= 6)      # Is 7 less than or equal to 6? → False

# --- Combine conditions with AND, OR, NOT ---

print((5 > 3) and (2 > 1))   # True and True → True
print((5 < 3) or (2 > 1))    # False or True → True
print(not (5 > 3))           # not True → False
raining = 0   # zero = False
if raining:
    print("Umbrella")
else:
    print("Sunglasses")
hungry = True

if hungry:
    print("Time to eat!")
else:
    print("Not hungry right now.")

