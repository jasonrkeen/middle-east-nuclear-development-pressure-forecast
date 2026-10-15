> This file mirrors `.github/copilot-instructions.md` and `CLAUDE.md`; keep all three in sync when any changes.

# AGENTS.md — middle-east-nuclear-development-pressure-forecast

## Purpose
A reproducible OSINT scenario model assessing whether the Iran-Israel-Gulf conflict is more likely to push nuclear development forward or contribute to a verified freeze, rollback, or sustained capability decline.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `numpy`, `pandas`, `matplotlib`, `reportlab`

## Folder structure
- `.github/` (6 files)
- `data/` (8 files)
- `docs/` (3 files)
- `outputs/` (16 files)
- `scripts/` (1 files)
- `src/` (7 files)
- `tests/` (2 files)
- `CHANGELOG.md`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `MODEL_CARD.md`
- `README.md`
- `RELEASE_NOTES.md`
- `SECURITY.md`
- `main.py`
- `pyproject.toml`
- `requirements.txt`

## Setup, run, test
Commands documented in README.md (referenced files exist):
```bash
python -m venv .venv
python -m pip install -r requirements.txt
python main.py --simulations 10000 --seed 20260821 --as-of 2026-08-25
python -m unittest discover -s tests -v
python scripts/release_check.py
```
- Tests: 2 Python test file(s) under `tests/`; framework appears to be unittest. Add/update tests with any logic change.
- CI workflows exist in `.github/workflows/`; keep them passing.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Uses `dataclasses` for structured config/results.
- Config lives in: `pyproject.toml`; avoid hardcoding parameters elsewhere.
- Random seeds are set for reproducibility (Monte Carlo/simulation); keep seeded, deterministic runs.
- Public data sources referenced: SIPRI, IAEA.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- Generated outputs go to: `outputs/charts/`, `outputs/reports/`, `outputs/tables/`
- A PDF report is produced with `reportlab`; keep it in sync with model changes.
- Charts are generated with matplotlib.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Synthetic data must stay synthetic; never introduce real personal or sensitive records.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
