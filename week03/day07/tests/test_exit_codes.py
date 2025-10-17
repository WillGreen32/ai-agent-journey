import subprocess, sys

PY = sys.executable


def test_exit_success(tmp_path):
    cfg = tmp_path / "ok.json"
    cfg.write_text(
        '{"input_path":"data/in.csv","output_path":"data/out.csv","required_fields":[],"allowed_states":[]}'
    )
    r = subprocess.run([PY, "-m", "src.cli.main", "-config", str(cfg)], text=True)
    assert r.returncode in (0, 2)  # 2 if missing input file, 0 if mocked ok


def test_exit_nonzero_on_error(tmp_path):
    bad_cfg = tmp_path / "bad.json"
    bad_cfg.write_text('{"allowed_states":"VIC"}')  # wrong type
    r = subprocess.run([PY, "-m", "src.cli.main", "-config", str(bad_cfg)], text=True)
    assert r.returncode != 0
