# Model Card

## Model

Middle East Nuclear Development Pressure Forecast, version 0.2.1. This release does not revise the forecast issued on 21 August 2026.

## Intended use

Open-source strategic decision support for assessing whether Iran-Israel-Gulf conflict dynamics increase pressure for nuclear latency or weaponization, support a verified freeze or rollback, or contribute to sustained capability decline.

## Prohibited interpretations

- The model does not determine that any government has made a weapons decision.
- Low verification access is not proof of prohibited activity.
- Regional pressure scores are not acquisition probabilities.
- Economic exposure indices are not asset-price forecasts or investment advice.
- The project contains no weapon design, engineering, targeting, or operational assistance.

## Inputs

Analyst-scored indicators traceable to `data/source_register.csv`, optional confidence-weighted evidence updates, regional actor inputs, and transparent economic scenario mappings.

## Outputs

Mutually exclusive 12-, 24-, and 36-month scenario probabilities; Monte Carlo uncertainty intervals; regional pressure scores; sensitivity diagnostics; source freshness; structural validation; forecast-performance readiness; and an executive brief.

## Calibration status

Preliminary. Structural validation tests model directionality and scenario dominance. Actual probabilistic calibration cannot be evaluated until frozen forecasts mature and outcomes are independently adjudicated. The registry preserves issued probabilities for future Brier-score and log-loss evaluation.

## Principal limitations

- Sparse and disrupted verification data.
- Wartime reporting contradictions and selection bias.
- Analyst judgment in indicator scores, uncertainty ranges, and priors.
- Possible structural breaks that make historical analogies weak.
- Scenario boundaries require documented outcome adjudication.

## Governance

Preserve each issued forecast. Apply corrections as new versions rather than rewriting prior probabilities. Accept evidence updates only when they identify a source-register entry, confidence level, rationale, and affected indicator.
