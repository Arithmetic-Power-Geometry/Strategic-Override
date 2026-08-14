#!/usr/bin/env python3
"""Reproduce all design-level MSOD v1.0 results.

This script analyzes the experimental instrument and randomization design only.
It never generates or imputes human participant responses.
"""
from pathlib import Path
import json
import hashlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)

cases = pd.read_csv(DATA / "msod_case_master.csv")
cond = pd.read_csv(DATA / "condition_matrix.csv")
stim = pd.read_csv(DATA / "msod_stimulus_bank_80.csv")
pretest = pd.read_csv(DATA / "qc_pretest_instrument.csv")

# Integrity checks
assert len(cases) == 10
assert len(cond) == 8
assert len(stim) == 80
assert stim.stimulus_id.is_unique
assert set(cond.representation_condition) == {"low_qc_candidate", "high_qc_candidate"}
assert set(cond.human_only_information_condition) == {"absent", "present"}
assert set(cond.ai_correctness_condition) == {"correct", "incorrect"}

mismatch = []
for _, r in stim.iterrows():
    expected = r.criterion_correct_final_decision if r.ai_correctness_condition == "correct" else ("approve" if r.criterion_correct_final_decision == "reject" else "reject")
    if r.stage2_ai_recommendation != expected:
        mismatch.append(r.stimulus_id)
assert not mismatch

# Condition balance in the 80-stimulus bank
balance = (stim.groupby(["representation_condition", "human_only_information_condition", "ai_correctness_condition"])
           .size().rename("n_stimuli").reset_index())
balance.to_csv(RESULTS / "table_condition_balance.csv", index=False)

# Case-domain manifest
manifest = stim.groupby(["case_id", "strategic_domain", "case_title"]).agg(
    stimuli=("stimulus_id", "size"),
    ai_confidence=("stage2_ai_confidence", "first")
).reset_index()
manifest.to_csv(RESULTS / "table_case_manifest.csv", index=False)

# Criterion and recommendation balance
crit = pd.crosstab(stim.human_only_information_condition, stim.criterion_correct_final_decision, margins=True)
crit.to_csv(RESULTS / "table_criterion_balance.csv")
ai = pd.crosstab(stim.ai_correctness_condition, stim.stage2_ai_recommendation, margins=True)
ai.to_csv(RESULTS / "table_ai_recommendation_balance.csv")

# Generate deterministic 600-participant planning schedule (not response data)
rng = np.random.default_rng(20260814)
rows = []
for p in range(600):
    order = rng.permutation(len(cases))
    for pos, case_index in enumerate(order, start=1):
        co = cond.iloc[(p + case_index) % len(cond)]
        case_id = cases.iloc[case_index].case_id
        rows.append({
            "participant_id": f"PLAN{p+1:04d}",
            "presentation_order": pos,
            "case_id": case_id,
            "condition_id": co.condition_id,
            "stimulus_id": f"{case_id}_{co.condition_id}",
            "representation_condition": co.representation_condition,
            "human_only_information_condition": co.human_only_information_condition,
            "ai_correctness_condition": co.ai_correctness_condition,
        })
schedule = pd.DataFrame(rows)
schedule.to_csv(RESULTS / "planning_randomization_600x10.csv", index=False)

sched_balance = (schedule.groupby(["representation_condition", "human_only_information_condition", "ai_correctness_condition"])
                 .size().rename("n_assignments").reset_index())
sched_balance["share"] = sched_balance.n_assignments / len(schedule)
sched_balance.to_csv(RESULTS / "table_planning_assignment_balance.csv", index=False)

case_cond = pd.crosstab(schedule.case_id, schedule.condition_id)
case_cond.to_csv(RESULTS / "table_case_by_condition_planning_balance.csv")

# Design-level summary only
summary = {
    "release": "MSOD v1.0",
    "analysis_scope": "experimental instrument and randomization design; no human participant responses",
    "master_cases": int(len(cases)),
    "factorial_conditions": int(len(cond)),
    "unique_stimuli": int(len(stim)),
    "strategic_domains": int(cases.strategic_domain.nunique()),
    "candidate_representation_levels": int(stim.representation_condition.nunique()),
    "human_information_levels": int(stim.human_only_information_condition.nunique()),
    "ai_correctness_levels": int(stim.ai_correctness_condition.nunique()),
    "pretest_rows": int(len(pretest)),
    "ai_assignment_mismatches": int(len(mismatch)),
    "planning_participants": 600,
    "planning_trials_per_participant": 10,
    "planning_trial_assignments": int(len(schedule)),
    "min_condition_assignments": int(sched_balance.n_assignments.min()),
    "max_condition_assignments": int(sched_balance.n_assignments.max()),
    "contains_empirical_human_responses": False,
    "empirical_OSI_available": False,
    "empirical_DA_available": False
}
(RESULTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

# Figure 1: stimulus balance
fig, ax = plt.subplots(figsize=(8, 4.8))
labels = [f"{r.representation_condition.replace('_candidate','')}\n{r.human_only_information_condition}\nAI {r.ai_correctness_condition}" for _, r in balance.iterrows()]
ax.bar(range(len(balance)), balance.n_stimuli)
ax.set_xticks(range(len(balance)), labels, rotation=35, ha="right")
ax.set_ylabel("Number of stimuli")
ax.set_title("MSOD v1.0: balanced 2 × 2 × 2 stimulus design")
fig.tight_layout()
fig.savefig(RESULTS / "figure_stimulus_balance.png", dpi=220)
plt.close(fig)

# Figure 2: planning assignment balance
fig, ax = plt.subplots(figsize=(8, 4.8))
labels2 = [f"{r.representation_condition.replace('_candidate','')}\n{r.human_only_information_condition}\nAI {r.ai_correctness_condition}" for _, r in sched_balance.iterrows()]
ax.bar(range(len(sched_balance)), sched_balance.n_assignments)
ax.set_xticks(range(len(sched_balance)), labels2, rotation=35, ha="right")
ax.set_ylabel("Planned trial assignments")
ax.set_title("Planning schedule balance: 600 managers × 10 cases")
fig.tight_layout()
fig.savefig(RESULTS / "figure_planning_balance.png", dpi=220)
plt.close(fig)

# Human-readable report
report = f"""# MSOD v1.0 Complete Reproduction Report

## Status

This run validates and summarizes the **experimental instrument and planned randomization**. It contains **no collected human-participant responses**, so it does not estimate empirical treatment effects, OSI, Decision Answerability, or manager performance.

## Reproduced design results

- Master strategic cases: **{len(cases)}**
- Factorial conditions: **{len(cond)}**
- Unique experimental stimuli: **{len(stim)}**
- Design: **2 × 2 × 2**
- AI assignment mismatches: **{len(mismatch)}**
- Candidate QC-pretest rows: **{len(pretest)}**
- Planning schedule: **600 synthetic planning IDs × 10 cases = {len(schedule):,} assignments**
- Assignments per factorial condition: **{sched_balance.n_assignments.min()}–{sched_balance.n_assignments.max()}**

## What can be concluded now

MSOD v1.0 is internally consistent as a reusable experimental stimulus bank. The 80 stimuli instantiate all eight factorial combinations across ten strategic cases, and the deterministic planning schedule provides near-balanced allocation for a 600-participant planning target.

## What cannot be concluded now

No empirical claim about managers is produced by this workflow. In particular, there is currently no observed OSI, treatment effect, confidence effect, DPT manipulation effect, or Decision Answerability estimate. Those outputs become available only after genuine participant responses are collected and merged with the stimulus identifiers.

## Output files

The `results/` directory contains machine-readable tables, the 6,000-row planning schedule, two figures, and `summary.json`.
"""
(RESULTS / "REPORT.md").write_text(report, encoding="utf-8")

# Result checksums
checks=[]
for f in sorted(RESULTS.glob("*")):
    if f.is_file() and f.name != "SHA256SUMS_RESULTS.txt":
        checks.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}")
(RESULTS / "SHA256SUMS_RESULTS.txt").write_text("\n".join(checks)+"\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
print(f"Wrote complete outputs to {RESULTS}")
