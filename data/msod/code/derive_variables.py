#!/usr/bin/env python3
"""Derive preregistered trial-level MSOD variables from collected responses."""
from pathlib import Path
import argparse
import pandas as pd

def derive(df):
    required = ["final_decision","ai_recommendation","criterion_correct_final_decision","initial_decision"]
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError(f"Missing columns: {missing}")
    out=df.copy()
    out["override"]=(out.final_decision!=out.ai_recommendation).astype(int)
    out["decision_accuracy"]=(out.final_decision==out.criterion_correct_final_decision).astype(int)
    out["justified_override"]=out["override"]*out["decision_accuracy"]
    out["unjustified_override"]=out["override"]*(1-out["decision_accuracy"])
    out["decision_revision"]=(out.final_decision!=out.initial_decision).astype(int)
    return out

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("input_csv")
    ap.add_argument("--out",default="msod_analysis_ready.csv")
    args=ap.parse_args()
    d=pd.read_csv(args.input_csv)
    derive(d).to_csv(args.out,index=False)
    print(f"Wrote {args.out}")
