import argparse, logging, sys
from pathlib import Path

from src.ingest import ingest_data
from src.validate import validate_data
from src.transform import transform_data
from src.export import export_data

# ---------- Logging setup ----------
def setup_logging(level: str = "INFO") -> None:
    level_map = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    logging.basicConfig(
        level=level_map.get(level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.debug("Logging configured at %s", level.upper())

# ---------- CLI ----------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataproc",
        description="Data pipeline CLI (ingest → validate → transform → report)"
    )
    parser.add_argument("--log-level", default="INFO",
                        help="CRITICAL|ERROR|WARNING|INFO|DEBUG (default: INFO)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Plan only; print what would run without writing files")

    subparsers = parser.add_subparsers(dest="command")

    # validate
    val = subparsers.add_parser("validate", help="Validate raw or processed data")
    val.add_argument("--in", dest="input", required=True, help="Input CSV or JSONL")
    val.add_argument("--out", dest="output", required=True, help="Report directory")

    # transform
    trans = subparsers.add_parser("transform", help="Transform data")
    trans.add_argument("--in", dest="input", required=True, help="Input CSV or JSONL")
    trans.add_argument("--out", dest="output", required=True, help="Output CSV path")

    # report
    rep = subparsers.add_parser("report", help="Generate report")
    rep.add_argument("--in", dest="input", required=True, help="Final CSV path")
    rep.add_argument("--out", dest="output", required=True, help="Report CSV path")

    # run-all (bonus)
    runall = subparsers.add_parser("run-all", help="Ingest → Validate → Transform → Report")
    runall.add_argument("--src", required=True, help="Raw CSV path")
    runall.add_argument("--final", default="data/final/customers_clean.csv",
                        help="Output CSV path (default: data/final/customers_clean.csv)")
    runall.add_argument("--report", default="reports/quality_dashboard.csv",
                        help="Report CSV path (default: reports/quality_dashboard.csv)")

    return parser

# ---------- Dispatch helpers ----------
def ensure_exists(path: str) -> None:
    if not Path(path).exists():
        raise FileNotFoundError(f"Path not found: {path}")

def main():
    parser = build_parser()
    args = parser.parse_args()

    # logging
    setup_logging(args.log_level)
    logging.info("Command: %s", args.command)

    # safety: no command → show help and exit(1)
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # --- VALIDATE ---
        if args.command == "validate":
            ensure_exists(args.input)
            logging.info("Validate → in=%s out=%s dry=%s", args.input, args.output, args.dry_run)
            if args.dry_run:
                logging.info("DRY-RUN: would run validate_data('%s','%s')", args.input, args.output)
            else:
                validate_data(args.input, args.output)

        # --- TRANSFORM ---
        elif args.command == "transform":
            ensure_exists(args.input)
            logging.info("Transform → in=%s out=%s dry=%s", args.input, args.output, args.dry_run)
            if args.dry_run:
                logging.info("DRY-RUN: would run transform_data('%s','%s')", args.input, args.output)
            else:
                transform_data(args.input, args.output)

        # --- REPORT ---
        elif args.command == "report":
            ensure_exists(args.input)
            logging.info("Report → in=%s out=%s dry=%s", args.input, args.output, args.dry_run)
            if args.dry_run:
                logging.info("DRY-RUN: would run export_data('%s','%s')", args.input, args.output)
            else:
                export_data(args.input, args.output)

        # --- RUN-ALL ---
        elif args.command == "run-all":
            ensure_exists(args.src)
            logging.info("Run-all → src=%s final=%s report=%s dry=%s",
                         args.src, args.final, args.report, args.dry_run)

            if args.dry_run:
                logging.info("DRY-RUN: would ingest → validate → transform → report")
            else:
                json_path = ingest_data(args.src, "data/processed")
                validate_data(json_path, "reports")
                transform_data(json_path, args.final)
                export_data(args.final, args.report)

        else:
            parser.print_help()
            sys.exit(1)

        logging.info("✅ Command completed successfully.")
        sys.exit(0)

    except FileNotFoundError as e:
        logging.error("Path error: %s", e)
        sys.exit(1)
    except Exception as e:
        logging.error("❌ Pipeline failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
