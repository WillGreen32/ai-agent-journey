# --- LISTS ---
skills = ["python", "apis"]
print("Initial skills:", skills)

# add to list
skills.append("agents")
print("After append:", skills)

# access by index
print("First skill:", skills[0])  # index starts at 0
print("Last skill:", skills[-1])  # negative index = from end

# iterate through list
for skill in skills:
    print("Skill:", skill)


# --- DICTIONARIES ---
prefs = {"theme": "dark", "autosave": True}
print("\nInitial prefs:", prefs)

# add new key-value
prefs["font"] = "Fira Code"
print("After adding font:", prefs)

# access keys safely
print("Theme:", prefs["theme"])
print("Language (default if missing):", prefs.get("lang", "en"))

# iterate through dict
for key, value in prefs.items():
    print(f"{key} → {value}")
