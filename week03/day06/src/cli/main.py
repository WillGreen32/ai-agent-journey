# src/cli/main.py
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd

from src.pipeline.utils import (
    set_global_determinism,
    configure_logging,
    get_logger,
    timed,
)
from src.pipeline.cleaners import clean_emails, normalize_names, add_signup_month
from src.pipeline.validator import flag_invalid_emails

log = get_logger("cli")

def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

@timed("validate")
def cmd_validate(inp: Path, out_dir: Path) -> None:
    """
    Read CSV -> clean emails -> flag invalids -> write validated.csv into out_dir.
    """
    df = pd.read_csv(inp)
    df = clean_emails(df)
    df = flag_invalid_emails(df)
    out_file = out_dir / "validated.csv"
    _ensure_parent(out_file)
    df.to_csv(out_file, index=False)
    log.info(f"validate: rows={len(df):,} -> {out_file}")

@timed("transform")
def cmd_transform(inp: Path, out_path: Path) -> None:
    """
    Read CSV -> normalize names + add signup_month -> write to out_path file.
    """
    df = pd.read_csv(inp)
    df = normalize_names(df)
    df = add_signup_month(df)
    _ensure_parent(out_path)
    df.to_csv(out_path, index=False)
    log.info(f"transform: rows={len(df):,} -> {out_path}")

@timed("report")
def cmd_report(inp: Path, out_path: Path, chunksize: int | None = None) -> None:
    """
    Produce a deterministic state count report with columns:
    state,total_customers
    Sorted by total_customers desc, then state asc.
    """
    if chunksize:
        counts: dict[str, int] = {}
        chunk_i = 0
        for chunk in pd.read_csv(inp, chunksize=chunksize):
            chunk_i += 1
            if "state" in chunk:
                vc = chunk["state"].value_counts()
                for k, v in vc.items():
                    counts[k] = counts.get(k, 0) + int(v)
            log.info(f"report: processed chunk {chunk_i} (rows={len(chunk):,})")
        rep = pd.DataFrame({"state": list(counts.keys()), "total_customers": list(counts.values())})
    else:
        df = pd.read_csv(inp)
        if "state" in df:
            rep = df.groupby("state", as_index=False).agg(total_customers=("state", "size"))
        else:
            rep = pd.DataFrame({"state": [], "total_customers": []})

    rep = (
        rep.astype({"total_customers": "int64"})
           .sort_values(by=["total_customers", "state"], ascending=[False, True])
           .reset_index(drop=True)
    )

    _ensure_parent(out_path)
    rep.to_csv(out_path, index=False)
    log.info(f"report: groups={len(rep):,} -> {out_path}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dataproc", description="Data pipeline CLI")
    p.add_argument("--log-level", default="INFO", help="DEBUG|INFO|WARNING|ERROR")
    p.add_argument("--log-file", default=None, help="Optional path to write logs")
    sub = p.add_subparsers(dest="command")

    v = sub.add_parser("validate", help="Validate raw data")
    v.add_argument("--in", dest="inp", required=True)
    v.add_argument("--out", dest="out", required=True)

    t = sub.add_parser("transform", help="Transform data")
    t.add_argument("--in", dest="inp", required=True)
    t.add_argument("--out", dest="out", required=True)

    r = sub.add_parser("report", help="Generate report")
    r.add_argument("--in", dest="inp", required=True)
    r.add_argument("--out", dest="out", required=True)
    r.add_argument("--chunksize", dest="chunksize", type=int, default=None)

    return p

def main() -> None:
    # parse args first so we can configure logging level/file
    parser = build_parser()
    args = parser.parse_args()

    # reproducibility + logging
    set_global_determinism(42)
    configure_logging(args.log_level, args.log_file)

    try:
        if args.command == "validate":
            cmd_validate(Path(args.inp), Path(args.out))
        elif args.command == "transform":
            cmd_transform(Path(args.inp), Path(args.out))
        elif args.command == "report":
            cmd_report(Path(args.inp), Path(args.out), args.chunksize)
        else:
            parser.print_help()
            sys.exit(1)
        log.info("✅ Completed.")
        sys.exit(0)
    except Exception as e:
        # Make sure failures set non-zero exit code so tests can assert correctly
        log.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
