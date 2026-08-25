## Change type

- [ ] Software or documentation only
- [ ] Evidence update
- [ ] Model methodology change
- [ ] New forecast issuance

## Summary

Describe the change and whether any issued probability is affected.

## Validation

- [ ] `python scripts/release_check.py`
- [ ] `python -m unittest discover -s tests -v`
- [ ] Pipeline smoke test
- [ ] Generated tables reviewed
- [ ] Executive brief proofread if regenerated

## Forecast-governance checks

- [ ] Earlier registry rows and probabilities remain unchanged.
- [ ] Evidence changes identify a public source, date, confidence, and rationale.
- [ ] Confirmed, not detected, and no coverage remain distinct.
- [ ] No weapon design or operational assistance is included.
