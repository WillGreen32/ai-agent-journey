# src/cli/main.py
import argparse, json, sys, os
from pathlib import Path
from typing import Any
from src.validate.config_schema import validate_config

DEFAULTS: dict[str, Any] = {
    "input_path": "data/input.csv",
    "output_path": "data/output_clean.csv",
    "required_fields": [],
    "allowed_states": []
}

def parse_args():
    p = argparse.ArgumentParser(description="Data Processor Tool")
    p.add_argument("-config", metavar="PATH", default=None)
    p.add_argument("-i", "--input", metavar="PATH", default=None)
    p.add_argument("-o", "--output", metavar="PATH", default=None)
    p.add_argument("--required-fields", default=None)
    p.add_argument("--allowed-states", default=None)
    return p.parse_args()

# src/cli/main.py (inside main())
from src.validate.collector import IssueCollector
from src.validate.reporting import print_summary, write_reports, exit_for_issues

collector = IssueCollector()

# Example: gather issues from your checks
# collector.extend(check_required(df, cfg["required_fields"]))
# collector.extend(check_state(df, cfg["allowed_states"]))
# ... add other checks

print_summary(collector, show_examples=10)
paths = write_reports(collector, Path("reports"))
if collector.issues:
    print(f"Tip: see {paths['csv']} for full details")
exit_for_issues(collector, success_code=0, error_code=1)


def load_json_or_exit(path: str | None) -> dict:
    if path is None:
        return {}
    p = Path(path)
    if not p.exists():
        print(f"❌ Config not found: {p}", file=sys.stderr); sys.exit(2)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            print("❌ Config root must be a JSON object { ... }", file=sys.stderr); sys.exit(2)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {p}:\n   {e}", file=sys.stderr); sys.exit(2)

def coerce_csv_list(val: str | None) -> list[str] | None:
    if val is None: return None
    return [x.strip() for x in val.split(",") if x.strip()]

def build_effective_config(args) -> dict:
    cfg = DEFAULTS.copy()
    file_cfg = load_json_or_exit(args.config)
    cfg |= file_cfg  # shallow merge
    if args.input:  cfg["input_path"]  = args.input
    if args.output: cfg["output_path"] = args.output
    req = coerce_csv_list(args.required_fields)
    if req is not None: cfg["required_fields"] = req
    allowed = coerce_csv_list(args.allowed_states)
    if allowed is not None: cfg["allowed_states"] = allowed
    return cfg

def validate_or_exit(cfg: dict):
    issues = validate_config(cfg)
    if issues:
        print(f"❌ Config validation failed ({len(issues)})")
        for i in issues: print("   -", i)
        sys.exit(2)

def ensure_paths(cfg: dict):
    inp = Path(cfg["input_path"]).expanduser()
    outp = Path(cfg["output_path"]).expanduser()
    if not inp.exists():
        print(f"❌ Input not found: {inp}")
        print("   Tip: use -i to override or fix 'input_path' in config.json"); sys.exit(2)
    outp.parent.mkdir(parents=True, exist_ok=True)

def main():
    args = parse_args()
    cfg = build_effective_config(args)
    validate_or_exit(cfg)
    print("🧩 Effective settings:", cfg)
    ensure_paths(cfg)
    # TODO: run pipeline with cfg
    # sys.exit(0)

if __name__ == "__main__":
    main()
