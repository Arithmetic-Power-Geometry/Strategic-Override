#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import sys

base = Path(__file__).resolve().parents[1]
stim = pd.read_csv(base/"data"/"msod_stimulus_bank_80.csv")
cond = pd.read_csv(base/"data"/"condition_matrix.csv")
case = pd.read_csv(base/"data"/"msod_case_master.csv")

errors=[]
if len(case)!=10: errors.append(f"Expected 10 master cases; found {len(case)}")
if len(cond)!=8: errors.append(f"Expected 8 factorial conditions; found {len(cond)}")
if len(stim)!=80: errors.append(f"Expected 80 stimuli; found {len(stim)}")
if stim.stimulus_id.duplicated().any(): errors.append("Duplicate stimulus_id detected")
if set(stim.ai_correctness_condition) != {"correct","incorrect"}: errors.append("AI correctness levels invalid")
if set(stim.human_only_information_condition) != {"present","absent"}: errors.append("Human-info levels invalid")
if set(stim.representation_condition) != {"high_qc_candidate","low_qc_candidate"}: errors.append("Representation levels invalid")

for _,r in stim.iterrows():
    expected = r.criterion_correct_final_decision if r.ai_correctness_condition=="correct" else ("approve" if r.criterion_correct_final_decision=="reject" else "reject")
    if r.stage2_ai_recommendation != expected:
        errors.append(f"AI correctness mismatch: {r.stimulus_id}")

if errors:
    print("VALIDATION FAILED")
    for e in errors: print("-",e)
    sys.exit(1)
print("VALIDATION PASSED")
print("10 cases × 8 conditions = 80 unique stimuli")
print("No fabricated participant responses are included.")
