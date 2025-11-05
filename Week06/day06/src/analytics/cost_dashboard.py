import json
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Config ----------
REQUIRED_COLUMNS = ["model_name", "total_tokens", "latency_s", "cost_usd", "success"]
RENAME_MAP = {"model": "model_name", "tokens": "total_tokens", "latency": "latency_s", "cost": "cost_usd"}

# ---------- Load ----------
def load_logs(path="logs/prompt_logs.jsonl") -> pd.DataFrame:
    fp = Path(path)
    if not fp.exists():
        raise FileNotFoundError(f"Log file not found: {fp}")

    records = []
    with fp.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    if not records:
        raise ValueError("Log file is empty.")

    df = pd.DataFrame(records)

    # Rename variant column names if present
    available_renames = {k: v for k, v in RENAME_MAP.items() if k in df.columns}
    if available_renames:
        df = df.rename(columns=available_renames)

    # Validate required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns in logs: {missing}")

    # Dtypes
    df["model_name"] = df["model_name"].astype(str)
    for num_col in ["total_tokens", "latency_s", "cost_usd"]:
        df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
    df["success"] = df["success"].astype(int)

    # Drop rows with NaNs in numeric fields
    df = df.dropna(subset=["total_tokens", "latency_s", "cost_usd"])

    return df

# ---------- Analyze ----------
def analyze(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.groupby("model_name").size().rename("requests")

    agg = df.groupby("model_name").agg(
        total_tokens=("total_tokens", "sum"),
        cost_usd=("cost_usd", "sum"),
        latency_s=("latency_s", "mean"),
        success=("success", "mean"),
        avg_tokens_per_request=("total_tokens", "mean"),
        avg_cost_per_request=("cost_usd", "mean"),
    )

    summary = agg.join(counts, how="left").reset_index()

    def _cps(row):
        return (row["cost_usd"] / row["success"]) if row["success"] > 0 else float("inf")

    summary["cost_per_success"] = summary.apply(_cps, axis=1)

    cols = [
        "model_name", "requests",
        "total_tokens", "avg_tokens_per_request",
        "cost_usd", "avg_cost_per_request",
        "latency_s", "success", "cost_per_success"
    ]
    summary = summary[cols]
    summary = summary.sort_values(by=["cost_per_success", "latency_s"], ascending=[True, True])

    return summary

# ---------- Visualize ----------
def plot_bar(df, x, y, title, ylabel):
    plt.figure()
    plt.bar(df[x], df[y])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Model")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()

# --- Add near the top if not already imported ---
import matplotlib.pyplot as plt

def _as_percent(series):
    """Convert success rate from 0..1 to 0..100 for display only."""
    return (series.astype(float) * 100.0)

def visualize(summary: pd.DataFrame):
    """
    Shows:
      - Avg Cost per Request (single bar chart)
      - Side-by-side: Avg Latency (s) and Success Rate (%)
    """
    # --- 1) Average Cost per Request (single chart) ---
    plt.figure()
    plt.bar(summary["model_name"], summary["avg_cost_per_request"])
    plt.title("Average Cost per Request by Model")
    plt.ylabel("USD")
    plt.xlabel("Model")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()

    # --- 2) Side-by-side Latency + Success (% of requests) ---
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: Avg Latency (seconds)
    axes[0].bar(summary["model_name"], summary["latency_s"])
    axes[0].set_title("Avg Latency (s)")
    axes[0].set_ylabel("Seconds")
    axes[0].set_xlabel("Model")
    axes[0].tick_params(axis="x", rotation=15)

    # Right: Success Rate (%)
    success_pct = _as_percent(summary["success"])
    axes[1].bar(summary["model_name"], success_pct)
    axes[1].set_title("Success Rate (%)")
    axes[1].set_ylabel("Percent")
    axes[1].set_xlabel("Model")
    axes[1].tick_params(axis="x", rotation=15)

    plt.tight_layout()
    plt.show()


def save_report(summary: pd.DataFrame, out_csv="reports/model_cost_report.csv"):
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Saved report → {out_path}")

# ---------- CLI ----------
def parse_args():
    p = argparse.ArgumentParser(description="Cost & Performance Analytics Dashboard")
    p.add_argument("--log", default="logs/prompt_logs.jsonl", help="Path to JSONL logs")
    p.add_argument("--out", default="reports/model_cost_report.csv", help="Output CSV path")
    p.add_argument("--no-plots", action="store_true", help="Skip plots (for CI/headless)")
    return p.parse_args()

def main():
    args = parse_args()
    df = load_logs(args.log)
    summary = analyze(df)
    print("\n=== Model Cost & Performance Summary ===")
    print(summary.to_string(index=False))
    save_report(summary, args.out)
    if not args.no_plots:
        visualize(summary)

if __name__ == "__main__":
    main()
