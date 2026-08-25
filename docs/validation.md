# Validation and Calibration Roadmap

## Validation layers

### 1. Mechanical validation - active

- probabilities sum to one;
- values remain bounded;
- indicator weights sum to one by dimension;
- fixed seeds reproduce identical outputs; and
- output schemas remain stable.

### 2. Directional validation - active

Controlled shocks confirm that increased direct-attack pressure increases the combined push pathway and increased IAEA access reduces the opaque threshold pathway.

### 3. Structural scenario validation - active

Four synthetic edge cases test whether the dominant pathway matches model logic. These are face-validity checks, not historical backtests.

### 4. Probabilistic calibration - pending maturation

The frozen registry contains 12-, 24-, and 36-month forecasts issued on 21 August 2026. When a target date passes, an outcome must be adjudicated from documented public evidence before Brier score and log loss are calculated.

## Outcome adjudication protocol

1. Use only evidence available on or before the target date.
2. Preserve confirmed, not detected, and no coverage as distinct evidence states.
3. Do not treat absence of evidence as evidence of absence.
4. Record the selected scenario, source references, dissenting evidence, and confidence.
5. Do not edit the issued forecast probabilities.
6. Score only after the adjudication record is complete.

## Evidence update protocol

New evidence enters through `data/raw/evidence_updates.csv` with a source ID, indicator, raw point change, confidence, status, and rationale. Accepted updates are discounted by confidence:

- high: 100 percent of the raw adjustment;
- medium: 65 percent; and
- low: 35 percent.

This is a governance control, not an empirical likelihood ratio. Future versions may replace these multipliers after enough forecast outcomes accumulate.

