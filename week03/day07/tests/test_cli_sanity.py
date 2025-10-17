import subprocess, sys

PY = sys.executable


def test_cli_help_runs():
    r = subprocess.run([PY, "-m", "src.cli.main", "-h"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "usage:" in r.stdout.lower()
