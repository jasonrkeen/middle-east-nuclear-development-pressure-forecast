import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.model import SCENARIOS, calculate_indices, run_forecast, sample_indicators, scenario_probabilities


ROOT = Path(__file__).resolve().parents[1]


def load_inputs():
    raw = ROOT / "data" / "raw"
    return (
        pd.read_csv(raw / "current_indicators.csv"),
        pd.read_csv(raw / "regional_actor_inputs.csv"),
        pd.read_csv(raw / "economic_scenario_map.csv"),
    )


class ForecastTests(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        indicators, _, _ = load_inputs()
        draws = sample_indicators(indicators, 2_000, np.random.default_rng(11))
        indices = calculate_indices(draws, indicators)
        probabilities = scenario_probabilities(indices, 12)
        self.assertTrue(np.allclose(probabilities.sum(axis=1), 1.0))
        self.assertTrue((probabilities.to_numpy() >= 0).all())

    def test_fixed_seed_is_reproducible(self):
        indicators, actors, economic = load_inputs()
        first = run_forecast(indicators, actors, economic, 2_000, 42)
        second = run_forecast(indicators, actors, economic, 2_000, 42)
        pd.testing.assert_frame_equal(first.scenario_summary, second.scenario_summary)
        pd.testing.assert_frame_equal(first.regional_summary, second.regional_summary)

    def test_more_direct_attack_pressure_increases_push_probability(self):
        indicators, actors, economic = load_inputs()
        low = indicators.copy()
        high = indicators.copy()
        low.loc[low["indicator"] == "direct_attack_exposure", "mean"] = 35
        high.loc[high["indicator"] == "direct_attack_exposure", "mean"] = 95
        low_result = run_forecast(low, actors, economic, 3_000, 99)
        high_result = run_forecast(high, actors, economic, 3_000, 99)

        def select(frame):
            return frame.loc[
                (frame["horizon_months"] == 12)
                & (frame["scenario"] == "Combined push toward latency or weaponization"),
                "mean_probability_pct",
            ].iloc[0]

        self.assertGreater(select(high_result.scenario_summary), select(low_result.scenario_summary))

    def test_more_iaea_access_reduces_opaque_pathway(self):
        indicators, actors, economic = load_inputs()
        low = indicators.copy()
        high = indicators.copy()
        low.loc[low["indicator"] == "iaea_access", "mean"] = 5
        high.loc[high["indicator"] == "iaea_access", "mean"] = 90
        low_result = run_forecast(low, actors, economic, 3_000, 101)
        high_result = run_forecast(high, actors, economic, 3_000, 101)

        def select(frame):
            return frame.loc[
                (frame["horizon_months"] == 12)
                & (frame["scenario"] == SCENARIOS[1]),
                "mean_probability_pct",
            ].iloc[0]

        self.assertLess(select(high_result.scenario_summary), select(low_result.scenario_summary))

    def test_weights_sum_to_one_by_dimension(self):
        indicators, _, _ = load_inputs()
        sums = indicators.groupby("dimension")["weight"].sum()
        self.assertTrue(np.allclose(sums.to_numpy(), 1.0))


if __name__ == "__main__":
    unittest.main()
