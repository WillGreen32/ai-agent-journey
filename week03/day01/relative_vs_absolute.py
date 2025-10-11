from pathlib import Path

relative_path = Path("data/raw/customers.csv")
print("Relative path object:", relative_path)
print("Is absolute?", relative_path.is_absolute())

# Convert to absolute
print("Absolute version:", relative_path.resolve())

# Check if it exists
print("Exists?", relative_path.exists())
absolute_path = Path(r"D:\AI Agent Journey\week03\day01\data\raw\customers.csv")
print("\nAbsolute path object:", absolute_path)
print("Is absolute?", absolute_path.is_absolute())
print("Exists?", absolute_path.exists())
