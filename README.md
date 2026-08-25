# Middle East Nuclear Development Pressure Forecast

**Version 0.2.1** is the publication-ready release. It adds automated release checks and public contribution, citation, evidence-review, and security guidance while preserving the 21 August 2026 forecast issued by v0.1.0.

A reproducible OSINT scenario model assessing whether the Iran-Israel-Gulf conflict is more likely to push nuclear development forward or contribute to a verified freeze, rollback, or sustained capability decline.

## Current baseline

Context reviewed through: **25 August 2026**. The quantitative forecast baseline was issued and frozen on **21 August 2026**. The preliminary baseline separates three propositions that are often incorrectly collapsed:

- strategic motivation may rise;
- technical capability may be damaged or constrained; and
- observability may deteriorate.

The model therefore treats low inspection access as an uncertainty amplifier rather than proof of weaponization.

## Outputs

Running the pipeline generates:

- 12-, 24-, and 36-month scenario probabilities;
- a combined push probability for threshold rebuilding or weaponization;
- Iran incentive, capability, verification, diplomacy, economic, and cascade indices;
- regional pressure scores for Iran, Saudi Arabia, Turkey, Egypt, the UAE, and Israel;
- trigger sensitivity analysis;
- probability-weighted economic exposure indices;
- four charts; and
- a PDF executive brief;
- an audit trail for accepted or rejected evidence changes;
- source-freshness and structural-validation reports; and
- calibration status plus comparison with the frozen v0.1.0 forecast.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py --simulations 10000 --seed 20260821 --as-of 2026-08-25
python -m unittest discover -s tests -v
python scripts/release_check.py
```

Use `--save-draws` to retain simulation-level results. To evaluate a governed update file elsewhere, add `--evidence-updates path/to/updates.csv`. Only rows marked `accepted` with an evidence date on or before the cutoff are applied.

## Project structure

```text
data/raw/              Editable evidence and scenario inputs
data/source_register.csv
docs/methodology.md
docs/validation.md
MODEL_CARD.md
src/model.py           Monte Carlo and scenario logic
src/evidence.py        Confidence-weighted update audit
src/governance.py      Freshness, structural tests, and scoring
src/charts.py          Visual outputs
src/report.py          Executive brief generator
src/pipeline.py        End-to-end orchestration
tests/                 Model and governance tests
.github/workflows/     GitHub Actions CI
scripts/release_check.py
outputs/charts/
outputs/reports/
outputs/tables/
```

## Scenario definitions

| Scenario | Meaning |
|---|---|
| Verified freeze or rollback | A monitored agreement materially limits or reverses sensitive activity |
| Opaque threshold rebuilding | Iran preserves or reconstructs latency while verification remains weak |
| Accelerated weaponization decision | Leadership decides to pursue an operational deterrent |
| Sustained capability decline | Damage, resource constraints, interdiction, or instability prevent meaningful recovery |

## Governance

- **Classification:** open-source analytical model.
- **Calibration:** preliminary. Forecasts issued on 21 August 2026 are frozen; Brier score and log loss begin only after target dates pass and outcomes are adjudicated.
- **Safety:** no weapons design, engineering, targeting, or operational assistance is included.
- **Interpretation:** regional pressure scores are not acquisition probabilities.
- **Update rule:** revise inputs only through dated, confidence-labeled evidence rows traceable to the source register; preserve the prior snapshot for comparison.
- **Freshness rule:** a source can be verified yet overdue for its assigned analytic role; the pipeline reports both states.

## GitHub-ready checks

The included workflow installs dependencies, runs the release audit and full unit-test suite, and executes a 2,000-draw pipeline smoke test. Before publishing a new forecast version, retain the old registry rows, add the new issued probabilities as new rows, and commit the generated summary tables and report.

Version 0.2.1 is a software and documentation release, not a newly issued forecast. See [CHANGELOG.md](CHANGELOG.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [docs/github_publication.md](docs/github_publication.md).

See [docs/methodology.md](docs/methodology.md) for full details and [data/source_register.csv](data/source_register.csv) for evidence anchors.
