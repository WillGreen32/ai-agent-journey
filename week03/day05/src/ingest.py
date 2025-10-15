import pandas as pd
from pathlib import Path

def ingest_data(input_path: str, output_dir: str = "data/processed") -> str:
    input_path = Path(input_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    out_path = output / "customers.json"
    df.to_json(out_path, orient="records", lines=True)
    print(f"✅ Ingested {len(df)} rows -> {out_path}")
    return str(out_path)
