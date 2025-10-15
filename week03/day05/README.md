# Day 5 — Pipeline Orchestration + CLI (End-to-End)

## Install
pip install -r requirements.txt

## Run
python -m src.cli.main validate --in data/raw/customers.csv --out reports/
python -m src.cli.main transform --in data/processed/customers.json --out data/final/customers_clean.csv
python -m src.cli.main report --in data/final/customers_clean.csv --out reports/quality_dashboard.csv

## One-shot
python -m src.cli.main run-all --src data/raw/customers.csv --final data/final/customers_clean.csv --report reports/quality_dashboard.csv
