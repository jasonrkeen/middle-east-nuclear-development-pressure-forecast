# GitHub Publication Guide

Version 0.2.1 is ready to publish as a software and documentation release. It does not issue a new forecast.

## Final local gate

```powershell
python scripts/release_check.py
python -m unittest discover -s tests -v
$env:MPLBACKEND = "Agg"
python main.py --simulations 10000 --seed 20260821 --as-of 2026-08-21
```

Confirm that the release audit reports no failures and that the executive brief displays `v0.2.1` in its footer.

## Create the repository

From the project directory:

```powershell
git init
git branch -M main
git add .
git commit -m "Publish Middle East nuclear pressure forecast v0.2.1"
gh repo create middle-east-nuclear-development-pressure-forecast --public --source=. --remote=origin --push
```

Review the repository URL before continuing. The intended account is `jasonrkeen`.

## Create the release

```powershell
git tag -a v0.2.1 -m "Publication-ready release; forecast unchanged"
git push origin v0.2.1
gh release create v0.2.1 --title "v0.2.1 — Publication-ready release" --notes-file RELEASE_NOTES.md
```

Attach the packaged ZIP and executive brief to the release if desired.

## Repository description

> Reproducible OSINT scenario forecast of Iran–Israel–Gulf nuclear-development pressure with Monte Carlo uncertainty, source governance, and calibration tracking.

Suggested topics: `osint`, `geopolitical-risk`, `scenario-analysis`, `monte-carlo`, `nuclear-safeguards`, `risk-intelligence`, `python`.

## Human review gate

Before publishing any future forecast:

- verify each current source date, jurisdiction, and definition;
- distinguish confirmed, not detected, and no coverage;
- preserve earlier registry rows and probabilities;
- document every quantitative input change;
- regenerate and proofread all outputs; and
- avoid deterministic language about government intent.
