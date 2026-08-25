from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import __version__  # noqa: E402
from src.governance import run_structural_validation  # noqa: E402


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, check_id: str, condition: bool, detail: str) -> None:
        self.rows.append(
            {
                "check_id": check_id,
                "status": "pass" if condition else "fail",
                "detail": detail,
            }
        )

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows, columns=["check_id", "status", "detail"])


def _required_columns(audit: Audit, filename: str, frame: pd.DataFrame, columns: set[str]) -> None:
    missing = columns - set(frame.columns)
    audit.check(f"schema:{filename}", not missing, "complete" if not missing else f"missing {sorted(missing)}")


def run_audit() -> pd.DataFrame:
    audit = Audit()
    required_files = [
        "README.md",
        "MODEL_CARD.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CITATION.cff",
        "LICENSE",
        "docs/methodology.md",
        "docs/validation.md",
        "docs/github_publication.md",
        "outputs/reports/middle_east_nuclear_development_pressure_executive_brief.pdf",
    ]
    missing_files = [name for name in required_files if not (ROOT / name).exists()]
    audit.check("required_files", not missing_files, "complete" if not missing_files else f"missing {missing_files}")

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
    project_version = match.group(1) if match else "missing"
    audit.check("version_alignment", project_version == __version__, f"package={__version__}; pyproject={project_version}")

    raw = ROOT / "data" / "raw"
    indicators = pd.read_csv(raw / "current_indicators.csv")
    registry = pd.read_csv(raw / "forecast_registry.csv")
    cases = pd.read_csv(raw / "structural_validation_cases.csv")
    updates = pd.read_csv(raw / "evidence_updates.csv")
    sources = pd.read_csv(ROOT / "data" / "source_register.csv")

    _required_columns(
        audit,
        "current_indicators.csv",
        indicators,
        {"dimension", "indicator", "mean", "sd", "weight", "evidence_note"},
    )
    _required_columns(
        audit,
        "forecast_registry.csv",
        registry,
        {
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
        },
    )
    _required_columns(
        audit,
        "evidence_updates.csv",
        updates,
        {"evidence_id", "evidence_date", "indicator", "raw_delta_points", "confidence", "source_id", "status", "rationale"},
    )

    bounded = indicators["mean"].between(0, 100).all() and indicators["sd"].ge(0).all()
    audit.check("indicator_bounds", bool(bounded), "means within 0-100 and standard deviations non-negative")
    weights = indicators.groupby("dimension")["weight"].sum().to_numpy()
    audit.check("indicator_weights", bool(np.allclose(weights, 1.0)), "weights sum to one within each dimension")
    audit.check("indicator_ids", bool(indicators["indicator"].is_unique), "indicator names are unique")

    probability_columns = ["p_freeze", "p_threshold", "p_weaponization", "p_decline"]
    probability_sums = registry[probability_columns].sum(axis=1)
    probability_valid = registry[probability_columns].apply(lambda column: column.between(0, 1)).all().all()
    audit.check("registry_probabilities", bool(probability_valid and np.allclose(probability_sums, 1.0)), "probabilities are bounded and sum to one")
    audit.check("registry_ids", bool(registry["forecast_id"].is_unique), "forecast IDs are unique")
    dates_valid = (pd.to_datetime(registry["target_date"]) > pd.to_datetime(registry["issued_at"])).all()
    audit.check("registry_dates", bool(dates_valid), "target dates follow issuance dates")

    registry_path = raw / "forecast_registry.csv"
    expected_hash = (raw / "forecast_registry.sha256").read_text(encoding="utf-8").split()[0]
    actual_hash = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    audit.check("registry_fingerprint", actual_hash == expected_hash, f"sha256={actual_hash}")

    audit.check("source_ids", bool(sources["source_id"].is_unique), "source IDs are unique")
    audit.check("source_urls", bool(sources["url"].astype(str).str.startswith("https://").all()), "all sources use HTTPS")
    audit.check("source_freshness_limits", bool(sources["freshness_limit_days"].ge(0).all()), "freshness limits are non-negative")

    if updates.empty:
        updates_valid = True
        update_detail = "no pending evidence rows"
    else:
        accepted_states = {"accepted", "rejected", "pending"}
        confidence_states = {"high", "medium", "low"}
        updates_valid = set(updates["status"].str.lower()) <= accepted_states and set(updates["confidence"].str.lower()) <= confidence_states
        update_detail = "evidence statuses and confidence labels are valid"
    audit.check("evidence_update_values", bool(updates_valid), update_detail)

    structural = run_structural_validation(cases)
    audit.check("structural_validation", bool(structural["passed"].all()), f"{int(structural['passed'].sum())}/{len(structural)} cases passed")
    return audit.frame()


def main() -> int:
    result = run_audit()
    output = ROOT / "outputs" / "tables" / "release_readiness.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    failures = result[result["status"] == "fail"]
    print(result.to_string(index=False))
    print(f"\nRelease readiness: {len(result) - len(failures)}/{len(result)} checks passed")
    return 1 if not failures.empty else 0


if __name__ == "__main__":
    raise SystemExit(main())
