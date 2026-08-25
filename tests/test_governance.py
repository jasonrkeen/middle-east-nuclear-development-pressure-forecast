import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.evidence import apply_evidence_updates
from src.governance import assess_source_freshness, run_structural_validation, score_forecast_registry


ROOT = Path(__file__).resolve().parents[1]


class EvidenceUpdateTests(unittest.TestCase):
    def setUp(self):
        self.indicators = pd.DataFrame(
            [
                {
                    "dimension": "strategic_incentive",
                    "indicator": "test_indicator",
                    "mean": 50.0,
                    "sd": 5.0,
                    "weight": 1.0,
                    "evidence_note": "test",
                }
            ]
        )

    def test_confidence_discount_is_applied(self):
        updates = pd.DataFrame(
            [
                {
                    "evidence_id": "E1",
                    "evidence_date": "2026-08-20",
                    "indicator": "test_indicator",
                    "raw_delta_points": 10,
                    "confidence": "high",
                    "source_id": "S1",
                    "status": "accepted",
                    "rationale": "high",
                },
                {
                    "evidence_id": "E2",
                    "evidence_date": "2026-08-21",
                    "indicator": "test_indicator",
                    "raw_delta_points": 10,
                    "confidence": "low",
                    "source_id": "S1",
                    "status": "accepted",
                    "rationale": "low",
                },
            ]
        )
        adjusted, audit = apply_evidence_updates(self.indicators, updates, "2026-08-21")
        self.assertAlmostEqual(float(adjusted.loc[0, "mean"]), 63.5)
        self.assertEqual(audit["applied_delta_points"].tolist(), [10.0, 3.5])

    def test_future_evidence_is_not_applied(self):
        updates = pd.DataFrame(
            [
                {
                    "evidence_id": "E1",
                    "evidence_date": "2026-08-22",
                    "indicator": "test_indicator",
                    "raw_delta_points": 20,
                    "confidence": "high",
                    "source_id": "S1",
                    "status": "accepted",
                    "rationale": "future",
                }
            ]
        )
        adjusted, audit = apply_evidence_updates(self.indicators, updates, "2026-08-21")
        self.assertEqual(float(adjusted.loc[0, "mean"]), 50.0)
        self.assertEqual(audit.loc[0, "status"], "not_applied")


class GovernanceTests(unittest.TestCase):
    def test_source_freshness_detects_overdue(self):
        sources = pd.DataFrame(
            [
                {
                    "source_id": "S1",
                    "date": "2026-01-01",
                    "freshness_limit_days": 30,
                    "source_role": "current_context",
                    "status": "verified",
                }
            ]
        )
        result = assess_source_freshness(sources, "2026-08-21")
        self.assertEqual(result.loc[0, "freshness_status"], "overdue")

    def test_structural_cases_pass(self):
        cases = pd.read_csv(ROOT / "data" / "raw" / "structural_validation_cases.csv")
        result = run_structural_validation(cases)
        self.assertTrue(result["passed"].all(), result.to_string(index=False))

    def test_open_registry_is_not_scored(self):
        registry = pd.read_csv(ROOT / "data" / "raw" / "forecast_registry.csv")
        result = score_forecast_registry(registry, "2026-08-21")
        self.assertTrue((result["score_status"] == "open_not_matured").all())
        self.assertTrue(result["brier_score"].isna().all())

    def test_resolved_forecast_is_scored(self):
        registry = pd.read_csv(ROOT / "data" / "raw" / "forecast_registry.csv").head(1)
        registry.loc[:, "target_date"] = "2026-08-20"
        registry["realized_scenario"] = registry["realized_scenario"].astype("object")
        registry.loc[:, "realized_scenario"] = "Opaque threshold rebuilding"
        result = score_forecast_registry(registry, "2026-08-21")
        self.assertEqual(result.loc[0, "score_status"], "scored")
        self.assertTrue(np.isfinite(result.loc[0, "brier_score"]))
        self.assertTrue(np.isfinite(result.loc[0, "log_loss"]))


if __name__ == "__main__":
    unittest.main()
