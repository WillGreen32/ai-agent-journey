import csv, time, subprocess, sys, pytest
from pathlib import Path
PY = sys.executable

@pytest.mark.slow
@pytest.mark.parametrize("rows,chunksize,limit_s", [
    (50_000, 10_000, 15.0),      # baseline budget
])
def test_large_csv_under_budget(tmp_path: Path, rows, chunksize, limit_s):
    # Arrange: synth dataset
    in_csv = tmp_path / "big.csv"
    with in_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["first_name","last_name","email","state","signup_date"])
        for i in range(rows):
            w.writerow(["Ana","Smith","ana@example.com","VIC","2024-01-10"])

    report = tmp_path / "reports" / "quality_dashboard.csv"
    report.parent.mkdir(parents=True, exist_ok=True)

    # Act: time the CLI
    t0 = time.time()
    r = subprocess.run([PY, "-m", "src.cli.main", "report",
                        "--in", str(in_csv), "--out", str(report), "--chunksize", str(chunksize)],
                        capture_output=True, text=True)
    elapsed = time.time() - t0

    # Assert
    assert r.returncode == 0, r.stderr
    assert elapsed < limit_s, f"Too slow: {elapsed:.2f}s (limit {limit_s:.2f}s)"
