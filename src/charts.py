from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COLORS = {
    "navy": "#17324D",
    "blue": "#2E6F95",
    "teal": "#2A9D8F",
    "gold": "#E9C46A",
    "orange": "#F4A261",
    "red": "#D65A4A",
    "gray": "#657786",
}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.edgecolor": "#C7D0D9",
            "axes.labelcolor": COLORS["navy"],
            "xtick.color": "#455A64",
            "ytick.color": "#455A64",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def make_charts(
    index_summary: pd.DataFrame,
    scenario_summary: pd.DataFrame,
    regional_summary: pd.DataFrame,
    economic_exposure: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    _style()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    scenario_order = [
        "Verified freeze or rollback",
        "Opaque threshold rebuilding",
        "Accelerated weaponization decision",
        "Sustained capability decline",
    ]
    scenario = scenario_summary[scenario_summary["scenario"].isin(scenario_order)].copy()
    pivot = scenario.pivot(index="scenario", columns="horizon_months", values="mean_probability_pct").loc[scenario_order]
    ax = pivot.T.plot(
        kind="bar",
        figsize=(10.5, 5.6),
        color=[COLORS["teal"], COLORS["gold"], COLORS["red"], COLORS["gray"]],
        width=0.78,
    )
    ax.set_title("Scenario probability by forecast horizon", loc="left", fontsize=15)
    ax.set_xlabel("Forecast horizon")
    ax.set_ylabel("Mean probability (%)")
    ax.set_xticklabels([f"{int(x)} months" for x in pivot.columns], rotation=0)
    ax.set_ylim(0, max(55, pivot.to_numpy().max() + 8))
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    path = output_dir / "scenario_probabilities.png"
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    paths.append(path)

    ordered = index_summary.sort_values("mean")
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    error = np.vstack([ordered["mean"] - ordered["p05"], ordered["p95"] - ordered["mean"]])
    ax.barh(ordered["index"], ordered["mean"], color=COLORS["blue"], alpha=0.92)
    ax.errorbar(ordered["mean"], ordered["index"], xerr=error, fmt="none", ecolor=COLORS["navy"], capsize=3)
    ax.set_title("Current evidence indices", loc="left", fontsize=15)
    ax.set_xlabel("Index score (0-100); whiskers show P05-P95")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    path = output_dir / "evidence_indices.png"
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    paths.append(path)

    ordered = regional_summary.sort_values("mean_pressure")
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    colors = [COLORS["red"] if value >= 70 else COLORS["orange"] if value >= 50 else COLORS["gold"] if value >= 30 else COLORS["teal"] for value in ordered["mean_pressure"]]
    ax.barh(ordered["actor"], ordered["mean_pressure"], color=colors)
    ax.set_title("Regional nuclear-development pressure", loc="left", fontsize=15)
    ax.set_xlabel("Pressure score (0-100), not probability of acquisition")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    path = output_dir / "regional_pressure.png"
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    paths.append(path)

    econ = economic_exposure.copy()
    econ["metric"] = econ["metric"].str.replace("_", " ").str.title()
    pivot_econ = econ.pivot(index="metric", columns="horizon_months", values="probability_weighted_exposure_index")
    ax = pivot_econ.plot(kind="barh", figsize=(10, 5.8), color=[COLORS["teal"], COLORS["gold"], COLORS["red"]])
    ax.set_title("Probability-weighted economic exposure", loc="left", fontsize=15)
    ax.set_xlabel("Exposure index (0-100), conditional scenario scale")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.2)
    ax.legend([f"{int(x)} months" for x in pivot_econ.columns], title="Horizon", frameon=False)
    plt.tight_layout()
    path = output_dir / "economic_exposure.png"
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    paths.append(path)

    return paths

