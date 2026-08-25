# Contributing

Contributions that improve evidence quality, reproducibility, validation, or communication are welcome.

## Evidence proposals

Use the evidence-update issue form before editing model inputs. A proposal should identify:

- the public source and publication date;
- the exact model indicator affected;
- whether the source reports something confirmed, not detected, or outside available coverage;
- the proposed direction and magnitude of change;
- confidence and contradictory evidence; and
- why the change belongs before the stated evidence cutoff.

Missing inspection access or reporting coverage must not be described as proof of weaponization. Qualitative assessments must remain labeled as qualitative.

## Code or methodology changes

1. Create a focused branch.
2. Preserve all previously issued forecast rows.
3. Add or update tests for altered logic.
4. Run:

   ```bash
   python scripts/release_check.py
   python -m unittest discover -s tests -v
   MPLBACKEND=Agg python main.py --simulations 10000 --seed 20260821 --as-of 2026-08-21
   ```

5. Explain whether the change is a software release, evidence update, model revision, or new forecast issuance.

## Forecast issuance rule

Never overwrite an issued probability. Append new registry rows with a new issuance date, version, target date, and forecast ID. Update the registry fingerprint only after reviewing the exact diff and documenting the issuance in the changelog.

## Scope and safety

Do not submit weapon design, engineering, targeting, procurement, or operational assistance. This repository is for aggregate strategic decision support using public evidence.
