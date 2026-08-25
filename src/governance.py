from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .model import SCENARIOS, scenario_probabilities


REGISTRY_COLUMNS = {
    "forecast_id",
    "model_version",
    "issued_at",
    "horizon_months",
    "target_date",
    "p_freeze",
    "p_threshold",
    "p_weaponization",
    "p_decline",
    "outcome_status",
    "realized_scenario",
}

PROBABILITY_COLUMNS = {
    SCENARIOS[0]: "p_freeze",
    SCENARIOS[1]: "p_threshold",
    SCENARIOS[2]: "p_weaponization",
    SCENARIOS[3]: "p_decline",
}


def assess_source_freshness(source_register: pd.DataFrame, as_of: str) -> pd.DataFrame:
    required = {"source_id", "date", "freshness_limit_days", "source_role", "status"}
    missing = required - set(source_register.columns)
    if missing:
        raise ValueError(f"Source register is missing columns: {sorted(missing)}")

    cutoff = pd.Timestamp(as_of)
    output = source_register.copy()
    parsed = pd.to_datetime(output["date"], errors="coerce")
    output["age_days"] = (cutoff - parsed).dt.days

    def classify(row) -> str:
        if str(row.status).lower() != "verified":
            return "unverified"
        if pd.isna(row.age_days) or row.source_role == "foundational":
            return "foundational"
        if row.age_days < 0:
            return "future_dated"
        if row.age_days <= int(row.freshness_limit_days):
            return "current"
        return "overdue"

    output["freshness_status"] = output.apply(classify, axis=1)
    return output


def run_structural_validation(cases: pd.DataFrame) -> pd.DataFrame:
    required = {
        "case_id",
        "description",
        "horizon_months",
        "expected_scenario",
        "strategic_incentive",
        "capability_continuity",
        "verification_observability",
        "diplomatic_opening",
        "economic_constraint",
        "regional_cascade",
    }
    missing = required - set(cases.columns)
    if missing:
        raise ValueError(f"Structural validation file is missing columns: {sorted(missing)}")

    rows = []
    index_columns = [
        "strategic_incentive",
        "capability_continuity",
        "verification_observability",
        "diplomatic_opening",
        "economic_constraint",
        "regional_cascade",
    ]
    for case in cases.itertuples(index=False):
        indices = pd.DataFrame([{name: getattr(case, name) for name in index_columns}])
        probabilities = scenario_probabilities(indices, int(case.horizon_months)).iloc[0]
        dominant = str(probabilities.idxmax())
        row = {
            "case_id": case.case_id,
            "description": case.description,
            "expected_scenario": case.expected_scenario,
            "dominant_scenario": dominant,
            "passed": dominant == case.expected_scenario,
        }
        for scenario, value in probabilities.items():
            row[PROBABILITY_COLUMNS[scenario]] = float(value)
        rows.append(row)
    return pd.DataFrame(rows)


def score_forecast_registry(registry: pd.DataFrame, as_of: str) -> pd.DataFrame:
    missing = REGISTRY_COLUMNS - set(registry.columns)
    if missing:
        raise ValueError(f"Forecast registry is missing columns: {sorted(missing)}")

    cutoff = pd.Timestamp(as_of)
    rows = []
    for row in registry.itertuples(index=False):
        target = pd.Timestamp(row.target_date)
        probabilities = np.array(
            [row.p_freeze, row.p_threshold, row.p_weaponization, row.p_decline],
            dtype=float,
        )
        if not np.isclose(probabilities.sum(), 1.0, atol=1e-6):
            raise ValueError(f"Registry probabilities do not sum to one: {row.forecast_id}")

        realized = str(row.realized_scenario).strip()
        if realized in {"", "nan", "None"}:
            realized = ""

        if target > cutoff:
            score_status = "open_not_matured"
            brier = np.nan
            log_loss = np.nan
        elif not realized:
            score_status = "matured_awaiting_adjudication"
            brier = np.nan
            log_loss = np.nan
        elif realized not in SCENARIOS:
            raise ValueError(f"Unknown realized scenario in {row.forecast_id}: {realized}")
        else:
            outcome = np.array([1.0 if scenario == realized else 0.0 for scenario in SCENARIOS])
            brier = float(np.mean((probabilities - outcome) ** 2))
            log_loss = float(-math.log(max(probabilities[SCENARIOS.index(realized)], 1e-12)))
            score_status = "scored"

        rows.append(
            {
                "forecast_id": row.forecast_id,
                "model_version": row.model_version,
                "horizon_months": int(row.horizon_months),
                "target_date": row.target_date,
                "score_status": score_status,
                "realized_scenario": realized,
                "brier_score": brier,
                "log_loss": log_loss,
            }
        )
    return pd.DataFrame(rows)


def compare_to_registry(
    scenario_summary: pd.DataFrame,
    registry: pd.DataFrame,
    baseline_version: str = "0.1.0",
) -> pd.DataFrame:
    baseline = registry[registry["model_version"].astype(str) == baseline_version].copy()
    rows = []
    for registry_row in baseline.itertuples(index=False):
        current = scenario_summary[
            (scenario_summary["horizon_months"] == int(registry_row.horizon_months))
            & (scenario_summary["scenario"].isin(SCENARIOS))
        ].set_index("scenario")
        for scenario, probability_column in PROBABILITY_COLUMNS.items():
            current_probability = float(current.loc[scenario, "mean_probability_pct"]) / 100.0
            baseline_probability = float(getattr(registry_row, probability_column))
            rows.append(
                {
                    "horizon_months": int(registry_row.horizon_months),
                    "scenario": scenario,
                    "baseline_version": baseline_version,
                    "baseline_probability_pct": baseline_probability * 100.0,
                    "current_probability_pct": current_probability * 100.0,
                    "change_pct_points": (current_probability - baseline_probability) * 100.0,
                }
            )
    return pd.DataFrame(rows)

