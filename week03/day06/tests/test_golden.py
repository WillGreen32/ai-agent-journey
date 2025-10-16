from pathlib import Path
import subprocess, sys
from src.pipeline.utils import file_hash_csv
PY = sys.executable

def test_report_matches_golden(tmp_path: Path):
    # Arrange: input with known counts VIC=2, NSW=1
    inp = tmp_path / "customers.csv"
    inp.write_text(
        "first_name,last_name,email,state,signup_date\n"
        "Ana,Smith,ana@example.com,VIC,2024-01-10\n"
        "Bob,Jones,bob@example.com,NSW,2024-02-02\n"
        "Z,Lee,z@example.com,VIC,2024-01-31\n"
    )
    out = tmp_path / "reports" / "quality_dashboard.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    # Act
    r = subprocess.run([PY, "-m", "src.cli.main", "report", "--in", str(inp), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    # Assert: canonical hashes match
    golden = Path("tests/golden/quality_dashboard.csv")
    assert file_hash_csv(out) == file_hash_csv(golden), (
        "Output drift detected! If change is intentional, regenerate golden after review."
    )
