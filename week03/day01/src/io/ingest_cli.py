# src/io/ingest_cli.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
from src.paths import RAW, PROCESSED
from src.io.ingest_normalize_write import run_pipeline

def parse_args():
    p = argparse.ArgumentParser(description="Ingest -> Normalize -> Write JSON")
    p.add_argument("--input", type=Path, default=RAW / "customers_ingest.csv")
    p.add_argument("--output", type=Path, default=PROCESSED / "customers.cleaned.json")
    return p.parse_args()

def main():
    args = parse_args()
    schema = ["name", "email", "city"]
    synonyms = {"e-mail": "email", "email address": "email"}
    run_pipeline(args.input, args.output, fieldnames=schema, header_map=synonyms)

if __name__ == "__main__":
    main()
