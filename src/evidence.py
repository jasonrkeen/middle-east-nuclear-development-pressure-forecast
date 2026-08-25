from __future__ import annotations

from pathlib import Path

import pandas as pd


CONFIDENCE_MULTIPLIERS = {"high": 1.0, "medium": 0.65, "low": 0.35}
REQUIRED_UPDATE_COLUMNS = {
    "evidence_id",
    "evidence_date",
    "indicator",
    "raw_delta_points",
    "confidence",
    "source_id",
    "status",
    "rationale",
}


def load_evidence_updates(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=sorted(REQUIRED_UPDATE_COLUMNS))
    updates = pd.read_csv(path)
    missing = REQUIRED_UPDATE_COLUMNS - set(updates.columns)
    if missing:
        raise ValueError(f"Evidence update file is missing columns: {sorted(missing)}")
    return updates


def apply_evidence_updates(
    indicators: pd.DataFrame,
    updates: pd.DataFrame,
    as_of: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    adjusted = indicators.copy()
    audit_rows: list[dict] = []
    if updates.empty:
        return adjusted, pd.DataFrame(
            columns=[
                "evidence_id",
                "indicator",
                "status",
                "raw_delta_points",
                "applied_delta_points",
                "previous_mean",
                "updated_mean",
                "source_id",
                "rationale",
            ]
        )

    cutoff = pd.Timestamp(as_of)
    known_indicators = set(adjusted["indicator"])
    for row in updates.sort_values(["evidence_date", "evidence_id"]).itertuples(index=False):
        evidence_date = pd.Timestamp(row.evidence_date)
        status = str(row.status).strip().lower()
        confidence = str(row.confidence).strip().lower()
        applied = status == "accepted" and evidence_date <= cutoff

        if row.indicator not in known_indicators:
            raise ValueError(f"Unknown indicator in evidence update {row.evidence_id}: {row.indicator}")
        if confidence not in CONFIDENCE_MULTIPLIERS:
            raise ValueError(f"Unsupported confidence level in {row.evidence_id}: {row.confidence}")

        mask = adjusted["indicator"] == row.indicator
        previous = float(adjusted.loc[mask, "mean"].iloc[0])
        applied_delta = float(row.raw_delta_points) * CONFIDENCE_MULTIPLIERS[confidence] if applied else 0.0
        updated = float(max(0.0, min(100.0, previous + applied_delta)))
        if applied:
            adjusted.loc[mask, "mean"] = updated

        audit_rows.append(
            {
                "evidence_id": row.evidence_id,
                "indicator": row.indicator,
                "status": "applied" if applied else "not_applied",
                "raw_delta_points": float(row.raw_delta_points),
                "applied_delta_points": applied_delta,
                "previous_mean": previous,
                "updated_mean": updated,
                "source_id": row.source_id,
                "rationale": row.rationale,
            }
        )
    return adjusted, pd.DataFrame(audit_rows)

