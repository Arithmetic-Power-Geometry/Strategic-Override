# Experiment Protocol

## Before data collection

1. Obtain the required institutional ethics/IRB approval or documented exemption.
2. Pre-register hypotheses, exclusion rules, primary estimands, power analysis, and analysis code.
3. Pretest the representation manipulation using `data/qc_pretest_instrument.csv`.
4. Freeze the final instrument version and random seed before confirmatory recruitment.

## Participant eligibility

Target working adults with genuine managerial responsibility. Record management level, years of management experience, industry, and country using non-identifying categories.

## Trial sequence

### Stage 1 — Common evidence
Present one case in the assigned representation condition. Ask:
- Approve or reject?
- Confidence 0–100.

### Stage 2 — AI recommendation
Display the recommendation and fixed case-specific AI confidence. Do not reveal whether the AI is correct.

### Stage 3 — Additional evidence
Present either the human-only evidence or the no-additional-information text.

### Stage 4 — Final judgment
Ask:
- Final approve/reject decision.
- Confidence 0–100.
- Short reason.

## Randomisation

Use `code/generate_randomization.py`. Each participant sees each of the ten cases once. Conditions rotate across participant × case combinations and case order is randomized. Researchers may use another randomisation scheme if preregistered.

## Quality control

Pre-register attention checks, minimum completion standards, implausibly fast response rules, duplicate-participant rules, and treatment of missing trials. Never decide exclusions after looking at treatment effects.

## Analysis

Use trial-level models with repeated decisions nested in participants and crossed with cases. At minimum, account for participant dependence; preferably model both participant and case heterogeneity when the estimator permits.

## Reporting

Report:
- participant count and trial count separately;
- exclusions and missingness;
- condition balance;
- manipulation-check results;
- primary treatment effects;
- uncertainty intervals;
- robustness to reasonable alternative specifications;
- deviations from preregistration.
