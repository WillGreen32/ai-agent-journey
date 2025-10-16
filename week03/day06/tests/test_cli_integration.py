import subprocess, sys, csv
from pathlib import Path
import pandas as pd
import pytest

PY = sys.executable

# ---------- small helpers ----------
def run_cli(*args: str):
    """Run the CLI as a subprocess and return CompletedProcess."""
    return subprocess.run([PY, "-m", "src.cli.main", *args],
                          capture_output=True, text=True)

def assert_ok(proc):
    """Fail with useful stderr if a CLI step fails."""
    assert proc.returncode == 0, f"\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

def read_csv(path: Path):
    return pd.read_csv(path)

def canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Stable sort & column order so comparisons are deterministic."""
    if df.empty:
        return df
    cols = sorted(df.columns)
    return df[cols].sort_values(cols, kind="mergesort").reset_index(drop=True)

# ---------- tests ----------

def test_cli_end_to_end(tmp_path: Path):
    # Arrange
    in_csv = tmp_path / "customers.csv"
    in_csv.write_text(
        "first_name,last_name,email,state,signup_date\n"
        "Ana,Smith,ana@example.com,VIC,2024-01-10\n"
        "Bob,Jones,bob@example.com,NSW,2024-02-02\n"
        ",Lee,bademail,VIC,2024-01-31\n"
    )
    out_dir = tmp_path / "reports"
    out_dir.mkdir()

    # validate -> writes validated.csv inside out_dir
    r1 = run_cli("validate", "--in", str(in_csv), "--out", str(out_dir))
    assert_ok(r1)
    validated = out_dir / "validated.csv"
    assert validated.exists(), "validated.csv not created"

    # transform -> writes a single CSV file
    final_csv = tmp_path / "final.csv"
    r2 = run_cli("transform", "--in", str(in_csv), "--out", str(final_csv))
    assert_ok(r2)
    assert final_csv.exists(), "final.csv not created"

    # report -> writes report file
    report = out_dir / "quality_dashboard.csv"
    r3 = run_cli("report", "--in", str(final_csv), "--out", str(report))
    assert_ok(r3)
    assert report.exists(), "report not created"

    # Quick schema & header sanity
    with report.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["state", "total_customers"], "Unexpected report header"

    # Deterministic ordering: total_customers desc, then state asc
    df = read_csv(report)
    ordered = df.sort_values(["total_customers", "state"], ascending=[False, True]).reset_index(drop=True)
    pd.testing.assert_frame_equal(df, ordered)

@pytest.mark.parametrize("chunksize", [None, 10000])
def test_report_chunked_vs_inmemory_is_identical(tmp_path: Path, chunksize):
    # Arrange input with known counts: VIC=2, NSW=1
    inp = tmp_path / "customers.csv"
    inp.write_text(
        "first_name,last_name,email,state,signup_date\n"
        "Ana,Smith,ana@example.com,VIC,2024-01-10\n"
        "Bob,Jones,bob@example.com,NSW,2024-02-02\n"
        "Z,Lee,z@example.com,VIC,2024-01-31\n"
    )
    # Transform once so report input is consistent with real flow
    final_csv = tmp_path / "final.csv"
    assert_ok(run_cli("transform", "--in", str(inp), "--out", str(final_csv)))

    # Act: generate report
    report = tmp_path / f"report_{'chunk' if chunksize else 'mem'}.csv"
    args = ["report", "--in", str(final_csv), "--out", str(report)]
    if chunksize:
        args += ["--chunksize", str(chunksize)]
    assert_ok(run_cli(*args))
    assert report.exists()

    # Keep both so we can compare after loop finishes
    report_df = canonical(read_csv(report))

    # Store as attribute on the test function between parameter runs (hack-free)
    marker = f"_store_{'chunk' if chunksize else 'mem'}"
    setattr(test_report_chunked_vs_inmemory_is_identical, marker, report_df)

    # After second run, compare
    if hasattr(test_report_chunked_vs_inmemory_is_identical, "_store_chunk") and \
       hasattr(test_report_chunked_vs_inmemory_is_identical, "_store_mem"):
        a = getattr(test_report_chunked_vs_inmemory_is_identical, "_store_chunk")
        b = getattr(test_report_chunked_vs_inmemory_is_identical, "_store_mem")
        pd.testing.assert_frame_equal(a, b)

def test_cli_logs_time(tmp_path: Path):
    """Timer decorator should log '... ran in X.XXs'."""
    in_csv = tmp_path / "customers.csv"
    in_csv.write_text(
        "first_name,last_name,email,state,signup_date\n"
        "Ana,Smith,ana@example.com,VIC,2024-01-10\n"
    )
    out_dir = tmp_path / "reports"
    out_dir.mkdir()

    proc = run_cli("--log-level", "INFO", "validate", "--in", str(in_csv), "--out", str(out_dir))
    assert_ok(proc)
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "validate ran in" in combined, f"Timer log missing. Output was:\n{combined}"
