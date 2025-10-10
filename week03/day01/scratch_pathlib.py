from pathlib import Path

raw_dir = Path("data/raw")
customers_csv = raw_dir / "customers.csv"

print("raw_dir:", raw_dir.resolve())
print("customers_csv:", customers_csv.resolve())
print("exists?", customers_csv.exists())
print("Is absolute?", customers_csv.is_absolute())
print("Absolute version:", customers_csv.resolve())
