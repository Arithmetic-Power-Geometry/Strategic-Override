#!/usr/bin/env python3
"""Create a balanced MSOD schedule. No participant response data are generated."""
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

def make_schedule(n_participants=600, seed=20260814, case_file="../data/msod_case_master.csv",
                  condition_file="../data/condition_matrix.csv", out="../data/randomization_schedule.csv"):
    rng = np.random.default_rng(seed)
    cases = pd.read_csv(Path(__file__).parent / case_file)
    cond = pd.read_csv(Path(__file__).parent / condition_file)
    rows = []
    # Balanced rotation: each participant sees every case once; condition assignment rotates
    # across participants and cases, then case order is independently randomized.
    for p in range(n_participants):
        pid = f"P{p+1:04d}"
        order = rng.permutation(len(cases))
        for pos, case_index in enumerate(order, start=1):
            case = cases.iloc[case_index]
            cond_index = (p + case_index) % len(cond)
            c = cond.iloc[cond_index]
            rows.append({
                "participant_id": pid,
                "presentation_order": pos,
                "case_id": case.case_id,
                "condition_id": c.condition_id,
                "stimulus_id": f"{case.case_id}_{c.condition_id}",
                "representation_condition": c.representation_condition,
                "human_only_information_condition": c.human_only_information_condition,
                "ai_correctness_condition": c.ai_correctness_condition
            })
    df = pd.DataFrame(rows)
    df.to_csv(Path(__file__).parent / out, index=False)
    return df

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--seed", type=int, default=20260814)
    ap.add_argument("--out", default="../data/randomization_schedule.csv")
    args = ap.parse_args()
    df = make_schedule(args.n, args.seed, out=args.out)
    print(f"Wrote {len(df)} trial assignments for {args.n} participants.")
