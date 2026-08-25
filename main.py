from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Middle East Nuclear Development Pressure Forecast."
    )
    parser.add_argument("--simulations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument(
        "--as-of",
        default="2026-08-21",
        help="Evidence cutoff in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--evidence-updates",
        type=Path,
        help="Optional CSV of governed evidence adjustments; defaults to data/raw/evidence_updates.csv.",
    )
    parser.add_argument(
        "--save-draws",
        action="store_true",
        help="Save simulation-level draws in addition to summary outputs.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    result = run_pipeline(
        project_root=project_root,
        simulations=args.simulations,
        seed=args.seed,
        save_draws=args.save_draws,
        as_of=args.as_of,
        evidence_updates_path=args.evidence_updates,
    )
    print(result.console_summary)
