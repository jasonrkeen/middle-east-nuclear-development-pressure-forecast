# Methodology

## Analytical question

Does the current Iran-Israel-Gulf conflict increase or decrease pressure for nuclear-weapons development over 12, 24, and 36 months?

The model deliberately separates **motivation**, **capability**, and **observability**. Military attacks can damage infrastructure while simultaneously increasing the strategic incentive to seek a stronger deterrent. Missing inspections are treated as an uncertainty amplifier, not proof of weaponization.

## Indices

1. Strategic Incentive Index - direct attack exposure, regime survival pressure, deterrence gap, diplomatic breakdown, weak security guarantees, and regional nuclear asymmetry.
2. Capability Continuity Index - expertise, material continuity, facility survivability, reconstruction, procurement, and finance.
3. Verification Observability Index - IAEA access, inventory continuity, declarations, monitoring, and independent corroboration.
4. Diplomatic Opening Index - talks, mediator channels, and enforceable verification offers.
5. Economic Constraint Index - sanctions, export disruption, and reconstruction burden.
6. Regional Cascade Index - security anxiety, guarantee uncertainty, civil nuclear expansion, and regional restraint.

Each indicator is scored 0-100 and sampled from a bounded normal distribution. Indicator standard deviations encode evidentiary uncertainty.

## Governed evidence updates

The baseline input file remains unchanged. New evidence is recorded in `data/raw/evidence_updates.csv` with a date, source-register ID, affected indicator, raw point change, confidence, disposition, and rationale. Accepted rows dated on or before the run cutoff are applied sequentially and clipped to the 0-100 scale. High-, medium-, and low-confidence updates receive multipliers of 1.00, 0.65, and 0.35. The pipeline writes every decision to `outputs/tables/evidence_update_audit.csv`.

These multipliers are governance conventions, not empirically estimated likelihood ratios.

## Scenario engine

Four mutually exclusive pathways are evaluated:

- Verified freeze or rollback
- Opaque threshold rebuilding
- Accelerated weaponization decision
- Sustained capability decline

Priors are set for each horizon and then adjusted using standardized index deviations. A softmax transformation ensures that probabilities are non-negative and sum to one for every simulation.

The combined **push probability** is the sum of opaque threshold rebuilding and accelerated weaponization. This definition captures development pressure without claiming that a weapon has been built.

## Regional model

Iran, Saudi Arabia, Turkey, Egypt, the UAE, and Israel are scored separately. The regional pressure score combines strategic incentive and capability, then subtracts restraint from safeguards and economic constraints. For Israel, the score represents modernization and posture pressure because SIPRI already assesses Israel as nuclear armed.

## Economic layer

Scenario-specific 0-100 exposure indices connect the strategic forecast to:

- energy markets;
- shipping disruption;
- defense spending;
- sovereign risk; and
- civil nuclear investment.

These are conditional exposure scales for integration with separate quantitative market models. They are not commodity-price or asset-return forecasts.

## Validation and calibration

The project validates:

- probability accounting;
- deterministic reproducibility for a fixed seed;
- monotonic directional behavior for critical indicators;
- stable output schemas; and
- sensitivity to a controlled 10-point indicator shock.

Four synthetic edge cases test whether the intended scenario dominates under extreme combinations of incentive, capability, observability, diplomacy, constraint, and cascade pressure. These cases test structural behavior; they are not historical backtests.

The forecast registry freezes the v0.1.0 probabilities and target dates. Once a target date passes, a documented outcome-adjudication process must assign one mutually exclusive realized scenario before the pipeline calculates multiclass Brier score and log loss. Until then, forecast performance is correctly reported as not yet scoreable.

## Source freshness

Every source has a role-specific freshness limit. Current snapshots and conflict context expire faster than structural or foundational references. A source may remain verified but be flagged overdue, which prompts review without silently altering model inputs.

## Version preservation

Prior issued probabilities are append-only. New evidence creates a new model run and baseline comparison; it does not rewrite an earlier forecast. This protects the integrity of future calibration measurement.
