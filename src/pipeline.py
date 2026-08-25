from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import __version__
from .charts import make_charts
from .evidence import apply_evidence_updates, load_evidence_updates
from .governance import (
    assess_source_freshness,
    compare_to_registry,
    run_structural_validation,
    score_forecast_registry,
)
from .model import run_forecast
from .report import build_report


@dataclass(frozen=True)
class PipelineResult:
    report_path: Path
    console_summary: str


def run_pipeline(
    project_root: Path,
    simulations: int,
    seed: int,
    save_draws: bool,
    as_of: str = "2026-08-21",
    evidence_updates_path: Path | None = None,
) -> PipelineResult:
    data_dir = project_root / "data" / "raw"
    table_dir = project_root / "outputs" / "tables"
    chart_dir = project_root / "outputs" / "charts"
    report_dir = project_root / "outputs" / "reports"
    for directory in (table_dir, chart_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)

    base_indicators = pd.read_csv(data_dir / "current_indicators.csv")
    actor_inputs = pd.read_csv(data_dir / "regional_actor_inputs.csv")
    economic_map = pd.read_csv(data_dir / "economic_scenario_map.csv")
    source_register = pd.read_csv(project_root / "data" / "source_register.csv")
    forecast_registry = pd.read_csv(data_dir / "forecast_registry.csv")
    structural_cases = pd.read_csv(data_dir / "structural_validation_cases.csv")

    update_path = evidence_updates_path or data_dir / "evidence_updates.csv"
    updates = load_evidence_updates(update_path)
    if not updates.empty:
        unknown_sources = set(updates.loc[updates["status"].str.lower() == "accepted", "source_id"]) - set(
            source_register["source_id"]
        )
        if unknown_sources:
            raise ValueError(f"Accepted evidence updates reference unknown sources: {sorted(unknown_sources)}")
    indicators, evidence_audit = apply_evidence_updates(base_indicators, updates, as_of)

    result = run_forecast(indicators, actor_inputs, economic_map, simulations, seed)
    source_freshness = assess_source_freshness(source_register, as_of)
    structural_validation = run_structural_validation(structural_cases)
    calibration_status = score_forecast_registry(forecast_registry, as_of)
    baseline_comparison = compare_to_registry(result.scenario_summary, forecast_registry)

    result.index_summary.to_csv(table_dir / "index_summary.csv", index=False)
    result.scenario_summary.to_csv(table_dir / "scenario_probabilities.csv", index=False)
    result.regional_summary.to_csv(table_dir / "regional_actor_scores.csv", index=False)
    result.sensitivity.to_csv(table_dir / "trigger_sensitivity.csv", index=False)
    result.economic_exposure.to_csv(table_dir / "economic_exposure.csv", index=False)
    evidence_audit.to_csv(table_dir / "evidence_update_audit.csv", index=False)
    source_freshness.to_csv(table_dir / "source_freshness.csv", index=False)
    structural_validation.to_csv(table_dir / "structural_validation_results.csv", index=False)
    calibration_status.to_csv(table_dir / "calibration_status.csv", index=False)
    baseline_comparison.to_csv(table_dir / "baseline_comparison.csv", index=False)
    if save_draws:
        result.simulation_draws.to_csv(table_dir / "monte_carlo_draws.csv", index=False)

    make_charts(
        result.index_summary,
        result.scenario_summary,
        result.regional_summary,
        result.economic_exposure,
        chart_dir,
    )
    report_path = report_dir / "middle_east_nuclear_development_pressure_executive_brief.pdf"
    build_report(
        output_path=report_path,
        index_summary=result.index_summary,
        scenario_summary=result.scenario_summary,
        regional_summary=result.regional_summary,
        sensitivity=result.sensitivity,
        economic_exposure=result.economic_exposure,
        chart_dir=chart_dir,
        simulations=simulations,
        seed=seed,
        as_of=f"{pd.Timestamp(as_of).day} {pd.Timestamp(as_of).strftime('%B %Y')}",
        source_freshness=source_freshness,
        calibration_status=calibration_status,
        structural_validation=structural_validation,
        evidence_audit=evidence_audit,
        baseline_comparison=baseline_comparison,
    )

    twelve = result.scenario_summary[
        (result.scenario_summary["horizon_months"] == 12)
        & (result.scenario_summary["scenario"] == "Combined push toward latency or weaponization")
    ].iloc[0]
    lead = (
        result.scenario_summary[
            (result.scenario_summary["horizon_months"] == 12)
            & (result.scenario_summary["scenario"] != "Combined push toward latency or weaponization")
        ]
        .sort_values("mean_probability_pct", ascending=False)
        .iloc[0]
    )
    summary = (
        f"Pipeline complete (v{__version__})\n"
        f"Simulations: {simulations:,} | Seed: {seed}\n"
        f"12-month push probability: {twelve.mean_probability_pct:.2f}% "
        f"(P05 {twelve.p05_pct:.2f}% / P95 {twelve.p95_pct:.2f}%)\n"
        f"Leading pathway: {lead.scenario} ({lead.mean_probability_pct:.2f}%)\n"
        f"Structural validation: {int(structural_validation['passed'].sum())}/{len(structural_validation)} passed\n"
        f"Source freshness: {(source_freshness['freshness_status'] == 'overdue').sum()} overdue\n"
        f"Calibration: {(calibration_status['score_status'] == 'scored').sum()} matured forecasts scored; "
        f"{(calibration_status['score_status'] == 'open_not_matured').sum()} open\n"
        f"Executive brief: {report_path}"
    )
    return PipelineResult(report_path=report_path, console_summary=summary)
