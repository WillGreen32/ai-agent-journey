from typing import Any

from src.validate.config_schema import validate_config

def validate_or_exit(cfg: dict):
    issues = validate_config(cfg)
    if issues:
        print(f"❌ Config validation failed ({len(issues)} issue(s)):")
        for i in issues:
            print("   -", i)
        import sys; sys.exit(2)


# What a *valid* config must contain
REQUIRED_KEYS = ["input_path", "output_path", "required_fields", "allowed_states"]

# Expected Python types for each key
TYPES: dict[str, type] = {
    "input_path": str,
    "output_path": str,
    "required_fields": list,
    "allowed_states": list,
}


def validate_config(cfg: dict[str, Any]) -> list[str]:
    """
    Return a list of human-friendly error messages.
    Empty list => config is valid.
    """
    errors: list[str] = []

    # 1) Required keys exist
    for k in REQUIRED_KEYS:
        if k not in cfg:
            errors.append(f"Missing required key: '{k}'")

    # 2) Types are correct
    for k, t in TYPES.items():
        if k in cfg and not isinstance(cfg[k], t):
            errors.append(
                f"Key '{k}' must be {t.__name__}, got {type(cfg[k]).__name__}"
            )

    # 3) List item types (strings only)
    if "required_fields" in cfg and isinstance(cfg.get("required_fields"), list):
        if not all(isinstance(x, str) for x in cfg["required_fields"]):
            errors.append("All 'required_fields' must be strings")
    if "allowed_states" in cfg and isinstance(cfg.get("allowed_states"), list):
        if not all(isinstance(x, str) for x in cfg["allowed_states"]):
            errors.append("All 'allowed_states' must be strings")

    return errors
