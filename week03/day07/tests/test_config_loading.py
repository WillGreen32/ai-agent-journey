import json, subprocess, sys
from pathlib import Path

PY = sys.executable


def test_config_ok(tmp_path: Path):
    # Arrange: valid config + tiny input file
    in_csv = tmp_path / "in.csv"
    in_csv.write_text("id,name,email\n1,Ana,ana@example.com\n", encoding="utf-8")

    cfg = {
        "input_path": str(in_csv),
        "output_path": str(tmp_path / "out.csv"),
        "required_fields": ["id"],
        "allowed_states": ["VIC"],
    }
    cfile = tmp_path / "cfg.json"
    cfile.write_text(json.dumps(cfg), encoding="utf-8")

    # Act
    r = subprocess.run(
        [PY, "-m", "src.cli.main", "-config", str(cfile)],
        capture_output=True,
        text=True,
    )

    # Assert: Until full pipeline is wired, allow 0 or 2 (2 if ensure_paths triggers)
    assert r.returncode in (0, 2)
    assert "Effective settings" in (r.stdout + r.stderr)


def test_config_bad_type(tmp_path: Path):
    # Arrange: wrong type for required_fields (string instead of list)
    in_csv = tmp_path / "in.csv"
    in_csv.write_text("id\n1\n", encoding="utf-8")

    cfg = {
        "input_path": str(in_csv),
        "output_path": str(tmp_path / "out.csv"),
        "required_fields": "id",  # WRONG TYPE
        "allowed_states": ["VIC"],
    }
    cfile = tmp_path / "bad.json"
    cfile.write_text(json.dumps(cfg), encoding="utf-8")

    # Act
    r = subprocess.run(
        [PY, "-m", "src.cli.main", "-config", str(cfile)],
        capture_output=True,
        text=True,
    )

    # Assert
    assert r.returncode != 0
    assert "Config validation failed" in (r.stdout + r.stderr)
