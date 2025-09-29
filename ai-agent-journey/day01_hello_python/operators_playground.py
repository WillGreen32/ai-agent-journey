print("Addition:", 5 + 2)      # 7
print("Subtraction:", 5 - 2)   # 3
print("Multiplication:", 5 * 2) # 10
print("Division:", 5 / 2)      # 2.5 (float)
print("Floor Division:", 5 // 2) # 2 (whole number only)
print("Modulus:", 5 % 2)       # 1 (remainder)
print("Exponent:", 5 ** 2)     # 25 (5 squared)
print("3 > 2:", 3 > 2)     # True
print("3 < 2:", 3 < 2)     # False
print("3 == 3:", 3 == 3)   # True
print("3 != 4:", 3 != 4)   # True
print("7 >= 7:", 7 >= 7)   # True
print("8 <= 6:", 8 <= 6)   # False
print("(3 > 2) and (2 < 5):", (3 > 2) and (2 < 5))  # True
print("(3 > 2) or (2 > 5):", (3 > 2) or (2 > 5))    # True
print("not (3 > 2):", not (3 > 2))                  # False
print("10 // 3:", 10 // 3)     # ?
print("10 % 3:", 10 % 3)       # ?
print("(7 > 3) and (2 > 5):", (7 > 3) and (2 > 5))  # ?
print("not (8 <= 10):", not (8 <= 10))              # ?
print("(2 + 3) * 4 == 20:", (2 + 3) * 4 == 20)      # ?
print("2 + 3 * 4 =", 2 + 3 * 4)          # 14, because 3*4 runs first
print("(2 + 3) * 4 =", (2 + 3) * 4)      # 20, because parentheses first
print("2 ** 3 ** 2 =", 2 ** 3 ** 2)      # 512, because 3**2 first (exponentiation is right-to-left)
x = 10
y = 3
print("Is x divisible by y?", x % y == 0)   # False
print("Is x bigger than 2*y?", x > 2 * y)   # True
age = 20
has_ticket = True

print("Can enter cinema?",
      (age >= 18) and has_ticket)   # True only if both are True
n = 5
print(1 < n < 10)     # True, means "1 < n and n < 10"
print(1 < n < 4)      # False
