# Data Dictionary

## Unit of observation

For future empirical data, one row represents one participant × one strategic case trial.

## Design variables

`case_id` identifies one of ten strategic problems. `condition_id` identifies one of eight 2 × 2 × 2 conditions. `stimulus_id` uniquely joins both.

`representation_condition` is deliberately labelled `high_qc_candidate` or `low_qc_candidate`, not `high_qc`/`low_qc`. The manipulation must be pretested before it is treated as a validated DPT-inspired representation manipulation.

`human_only_information_condition` indicates whether stage 3 supplies additional verified evidence unavailable to the AI recommendation.

`ai_correctness_condition` indicates whether the displayed AI recommendation matches the declared criterion for that condition.

## Response variables

Initial and final decisions use `approve` / `reject`. Confidence uses 0–100. `decision_reason` is optional short text. Before public release, free text must be reviewed for accidental personal or employer-identifying information.

## Derived variables

Derived variables are created after collection using `code/derive_variables.py`. They should not be typed manually into raw data.

See `data/codebook.csv` and `data/analysis_variable_spec.csv` for full definitions.
