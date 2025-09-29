# --- Basic concatenation ---
first = "Ada"
last = "Lovelace"

# combine strings with +
print("Full name (concat): " + first + " " + last)

# --- f-strings (modern, clean) ---
full = f"{first} {last}"
print("Full name (f-string):", full)

# math inside f-strings
msg = f"{first} is {2025 - 1815} years after her birth"
print(msg)

# --- Formatting numbers ---
pi = 22/7
pi_fmt = f"pi ≈ {pi:.2f}"        # 2 decimal places
print(pi_fmt)

number_fmt = f"{1234567:,}"      # adds commas
print("Formatted number:", number_fmt)

# --- Other tricks ---
name = "ada"
print("Title case:", name.title())   # Ada
print("Upper:", name.upper())        # ADA
print("Lower:", name.lower())        # ada

# --- Multi-line strings ---
quote = """This is a 
multi-line
string."""
print(quote)
