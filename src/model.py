from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


SCENARIOS = (
    "Verified freeze or rollback",
    "Opaque threshold rebuilding",
    "Accelerated weaponization decision",
    "Sustained capability decline",
)

SCENARIO_PRIORS = {
    12: np.array([0.20, 0.45, 0.25, 0.10]),
    24: np.array([0.22, 0.42, 0.27, 0.09]),
    36: np.array([0.25, 0.39, 0.28, 0.08]),
}


@dataclass(frozen=True)
class ForecastResult:
    index_summary: pd.DataFrame
    scenario_summary: pd.DataFrame
    regional_summary: pd.DataFrame
    sensitivity: pd.DataFrame
    economic_exposure: pd.DataFrame
    simulation_draws: pd.DataFrame


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - values.max(axis=1, keepdims=True)
    exp_values = np.exp(shifted)
    return exp_values / exp_values.sum(axis=1, keepdims=True)


def _weighted_index(draws: pd.DataFrame, indicators: pd.DataFrame, dimension: str) -> np.ndarray:
    subset = indicators.loc[indicators["dimension"] == dimension]
    weights = subset["weight"].to_numpy(dtype=float)
    weights = weights / weights.sum()
    return draws[subset["indicator"].tolist()].to_numpy() @ weights


def sample_indicators(
    indicators: pd.DataFrame, simulations: int, rng: np.random.Generator
) -> pd.DataFrame:
    sampled: dict[str, np.ndarray] = {}
    for row in indicators.itertuples(index=False):
        sampled[row.indicator] = np.clip(
            rng.normal(float(row.mean), float(row.sd), simulations), 0.0, 100.0
        )
    return pd.DataFrame(sampled)


def calculate_indices(draws: pd.DataFrame, indicators: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=draws.index)
    for dimension in indicators["dimension"].drop_duplicates():
        result[dimension] = _weighted_index(draws, indicators, dimension)
    return result


def scenario_probabilities(indices: pd.DataFrame, horizon: int) -> pd.DataFrame:
    if horizon not in SCENARIO_PRIORS:
        raise ValueError(f"Unsupported horizon: {horizon}")

    # Standardized deviations from the current evidence baseline. Coefficients
    # encode directional logic, while priors anchor preliminary calibration.
    centered = pd.DataFrame(
        {
            "incentive": (indices["strategic_incentive"] - 82.0) / 15.0,
            "capability": (indices["capability_continuity"] - 57.0) / 18.0,
            "observability": (indices["verification_observability"] - 14.0) / 18.0,
            "diplomacy": (indices["diplomatic_opening"] - 22.0) / 18.0,
            "constraint": (indices["economic_constraint"] - 72.0) / 18.0,
            "cascade": (indices["regional_cascade"] - 52.0) / 18.0,
        }
    )

    coefficients = np.array(
        [
            [-0.9, -0.2, 0.8, 1.2, 0.5, -0.2],
            [0.6, 0.6, -0.9, -0.5, -0.2, 0.4],
            [1.1, 0.8, -0.7, -1.0, -0.6, 0.7],
            [-0.4, -1.3, 0.2, 0.3, 1.0, -0.2],
        ]
    )
    logits = np.log(SCENARIO_PRIORS[horizon])[None, :] + centered.to_numpy() @ coefficients.T
    probabilities = _softmax(logits)
    return pd.DataFrame(probabilities, columns=SCENARIOS)


def summarize_indices(indices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    display = {
        "strategic_incentive": "Strategic incentive",
        "capability_continuity": "Capability continuity",
        "verification_observability": "Verification observability",
        "diplomatic_opening": "Diplomatic opening",
        "economic_constraint": "Economic constraint",
        "regional_cascade": "Regional cascade pressure",
    }
    for column, label in display.items():
        values = indices[column]
        rows.append(
            {
                "index": label,
                "mean": values.mean(),
                "p05": values.quantile(0.05),
                "p50": values.quantile(0.50),
                "p95": values.quantile(0.95),
            }
        )
    return pd.DataFrame(rows)


def summarize_scenarios(probability_frames: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for horizon, frame in probability_frames.items():
        for scenario in SCENARIOS:
            values = frame[scenario] * 100.0
            rows.append(
                {
                    "horizon_months": horizon,
                    "scenario": scenario,
                    "mean_probability_pct": values.mean(),
                    "p05_pct": values.quantile(0.05),
                    "p50_pct": values.quantile(0.50),
                    "p95_pct": values.quantile(0.95),
                }
            )
        push = (frame[SCENARIOS[1]] + frame[SCENARIOS[2]]) * 100.0
        rows.append(
            {
                "horizon_months": horizon,
                "scenario": "Combined push toward latency or weaponization",
                "mean_probability_pct": push.mean(),
                "p05_pct": push.quantile(0.05),
                "p50_pct": push.quantile(0.50),
                "p95_pct": push.quantile(0.95),
            }
        )
    return pd.DataFrame(rows)


def _classification(score: float) -> str:
    if score >= 70:
        return "High"
    if score >= 50:
        return "Elevated"
    if score >= 30:
        return "Guarded"
    return "Low"


def regional_actor_forecast(
    actor_inputs: pd.DataFrame, simulations: int, rng: np.random.Generator
) -> pd.DataFrame:
    rows = []
    for actor in actor_inputs.itertuples(index=False):
        columns = [
            "threat_exposure",
            "guarantee_gap",
            "nuclear_asymmetry",
            "domestic_signal",
            "civil_nuclear_base",
            "technical_depth",
            "fiscal_capacity",
            "safeguards_strength",
            "economic_constraint",
        ]
        means = np.array([getattr(actor, name) for name in columns], dtype=float)
        samples = np.clip(rng.normal(means, 7.0, size=(simulations, len(columns))), 0, 100)
        incentive = samples[:, :4] @ np.array([0.34, 0.22, 0.28, 0.16])
        capability = samples[:, 4:7] @ np.array([0.38, 0.36, 0.26])
        restraint = samples[:, 7] * 0.62 + samples[:, 8] * 0.38
        # Strong safeguards and binding economic constraints materially reduce
        # the translation of strategic anxiety into weapons-development pressure.
        pressure = np.clip(0.56 * incentive + 0.31 * capability - 0.40 * restraint + 18.0, 0, 100)
        rows.append(
            {
                "actor": actor.actor,
                "mean_pressure": pressure.mean(),
                "p05": np.quantile(pressure, 0.05),
                "p50": np.quantile(pressure, 0.50),
                "p95": np.quantile(pressure, 0.95),
                "classification": _classification(float(pressure.mean())),
                "analytic_role": actor.analytic_role,
            }
        )
    return pd.DataFrame(rows).sort_values("mean_pressure", ascending=False).reset_index(drop=True)


def sensitivity_analysis(
    base_indicators: pd.DataFrame,
    simulations: int,
    seed: int,
    shock_size: float = 10.0,
) -> pd.DataFrame:
    candidates = [
        "direct_attack_exposure",
        "diplomatic_breakdown",
        "fissile_material_continuity",
        "facility_survivability",
        "iaea_access",
        "economic_pressure",
        "regional_security_anxiety",
    ]

    def run_once(frame: pd.DataFrame, local_seed: int) -> float:
        local_rng = np.random.default_rng(local_seed)
        draws = sample_indicators(frame, simulations, local_rng)
        idx = calculate_indices(draws, frame)
        probs = scenario_probabilities(idx, 12)
        return float((probs[SCENARIOS[1]] + probs[SCENARIOS[2]]).mean() * 100.0)

    baseline = run_once(base_indicators, seed)
    rows = []
    for offset, indicator in enumerate(candidates, start=1):
        for shock in (-shock_size, shock_size):
            changed = base_indicators.copy()
            mask = changed["indicator"] == indicator
            changed.loc[mask, "mean"] = np.clip(changed.loc[mask, "mean"] + shock, 0, 100)
            value = run_once(changed, seed + offset)
            rows.append(
                {
                    "indicator": indicator,
                    "shock_points": shock,
                    "push_probability_pct": value,
                    "change_from_baseline_pct_points": value - baseline,
                }
            )
    return pd.DataFrame(rows).sort_values("change_from_baseline_pct_points")


def economic_exposure_forecast(
    economic_map: pd.DataFrame, probability_frames: dict[int, pd.DataFrame]
) -> pd.DataFrame:
    rows = []
    metric_columns = [
        "energy_market_risk",
        "shipping_disruption_risk",
        "defense_spending_pressure",
        "sovereign_risk_pressure",
        "civil_nuclear_capex_pressure",
    ]
    mapping = economic_map.set_index("scenario")
    for horizon, probabilities in probability_frames.items():
        mean_probs = probabilities.mean()
        for metric in metric_columns:
            weighted = sum(float(mean_probs[scenario]) * float(mapping.loc[scenario, metric]) for scenario in SCENARIOS)
            rows.append(
                {
                    "horizon_months": horizon,
                    "metric": metric,
                    "probability_weighted_exposure_index": weighted,
                }
            )
    return pd.DataFrame(rows)


def run_forecast(
    indicators: pd.DataFrame,
    actor_inputs: pd.DataFrame,
    economic_map: pd.DataFrame,
    simulations: int,
    seed: int,
    horizons: Iterable[int] = (12, 24, 36),
) -> ForecastResult:
    if simulations < 1_000:
        raise ValueError("Use at least 1,000 simulations for stable uncertainty summaries.")
    if not np.isclose(indicators.groupby("dimension")["weight"].sum(), 1.0).all():
        raise ValueError("Indicator weights must sum to 1 within each dimension.")

    rng = np.random.default_rng(seed)
    draws = sample_indicators(indicators, simulations, rng)
    indices = calculate_indices(draws, indicators)
    frames = {horizon: scenario_probabilities(indices, horizon) for horizon in horizons}
    regional = regional_actor_forecast(actor_inputs, simulations, rng)
    sensitivity = sensitivity_analysis(indicators, min(simulations, 5_000), seed + 10_000)
    economic = economic_exposure_forecast(economic_map, frames)

    draw_output = indices.copy()
    draw_output.insert(0, "simulation_id", np.arange(1, simulations + 1))
    for horizon, frame in frames.items():
        for scenario in SCENARIOS:
            key = scenario.lower().replace(" ", "_").replace("-", "_")
            draw_output[f"p_{horizon}m_{key}"] = frame[scenario].to_numpy()

    return ForecastResult(
        index_summary=summarize_indices(indices),
        scenario_summary=summarize_scenarios(frames),
        regional_summary=regional,
        sensitivity=sensitivity,
        economic_exposure=economic,
        simulation_draws=draw_output,
    )
