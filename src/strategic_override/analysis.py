from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

REQUIRED_TRIAL_FIELDS={"participant","ai_correct","initial_correct","final_correct","accept_ai","override","opportunity_wrong_ai","opportunity_correct_ai","appropriate_reliance"}


def validate_trials(df):
    missing=REQUIRED_TRIAL_FIELDS-set(df.columns)
    if missing:
        raise ValueError(f"Missing trial columns: {sorted(missing)}")
    for c in REQUIRED_TRIAL_FIELDS-{"participant"}:
        bad=set(pd.Series(df[c]).dropna().unique())-{0,1}
        if bad:
            raise ValueError(f"{c} must be binary; found {sorted(bad)}")


def osi(df):
    validate_trials(df)
    h=df.loc[df.opportunity_wrong_ai.eq(1),'override']
    a=df.loc[df.opportunity_correct_ai.eq(1),'override']
    return float(h.mean()-a.mean()) if len(h) and len(a) else float('nan')


def participant_bootstrap_osi(df,draws=2000,seed=2026):
    validate_trials(df)
    rng=np.random.default_rng(seed)
    rows=[]
    for _,x in df.groupby('participant',sort=False):
        rows.append([
            x.loc[x.opportunity_wrong_ai.eq(1),'override'].sum(),
            x.opportunity_wrong_ai.sum(),
            x.loc[x.opportunity_correct_ai.eq(1),'override'].sum(),
            x.opportunity_correct_ai.sum()
        ])
    g=np.asarray(rows,float)
    n=len(g)
    vals=np.full(draws,np.nan)
    for b in range(draws):
        z=g[rng.integers(0,n,n)].sum(axis=0)
        if z[1]>0 and z[3]>0:
            vals[b]=z[0]/z[1]-z[2]/z[3]
    return tuple(map(float,np.nanpercentile(vals,[2.5,97.5])))


def summarize_trials(label,df):
    validate_trials(df)
    h=df[df.opportunity_wrong_ai.eq(1)]
    a=df[df.opportunity_correct_ai.eq(1)]
    lo,hi=participant_bootstrap_osi(df)
    return {
        'dataset':label,
        'n_trials':int(len(df)),
        'participants':int(df.participant.nunique()),
        'final_accuracy':float(df.final_correct.mean()),
        'appropriate_reliance':float(df.appropriate_reliance.mean()),
        'overall_override_rate':float(df.override.mean()),
        'human_advantage_conflicts':int(len(h)),
        'override_when_human_advantage':float(h.override.mean()),
        'ai_advantage_conflicts':int(len(a)),
        'override_when_ai_advantage':float(a.override.mean()),
        'osi':osi(df),
        'osi_ci_low':lo,
        'osi_ci_high':hi,
        'human_advantage_final_accuracy':float(h.final_correct.mean()),
        'ai_advantage_final_accuracy':float(a.final_correct.mean())
    }


def classify_outcome_state(ai_correct:int, accept_ai:int, override:int, final_correct:int)->str:
    """Classify one human-AI trial into an exhaustive five-state outcome system.

    The fifth state, non-rescue override, occurs when AI is wrong, the human rejects
    the AI recommendation, but the final human choice is also criterion-incorrect.
    """
    vals=(ai_correct,accept_ai,override,final_correct)
    if any(v not in (0,1) for v in vals):
        raise ValueError('Outcome-state inputs must be binary.')
    if accept_ai+override != 1:
        raise ValueError('accept_ai and override must be complementary for outcome-state classification.')
    if ai_correct==1 and accept_ai==1:
        return 'appropriate_reliance'
    if ai_correct==0 and override==1 and final_correct==1:
        return 'justified_override'
    if ai_correct==0 and accept_ai==1:
        return 'automation_failure'
    if ai_correct==1 and override==1:
        return 'unjustified_override'
    if ai_correct==0 and override==1 and final_correct==0:
        return 'non_rescue_override'
    raise ValueError('Trial does not map to the declared five-state partition.')


def five_states(label,df):
    validate_trials(df)
    counts={
        'appropriate_reliance':0,
        'justified_override':0,
        'automation_failure':0,
        'unjustified_override':0,
        'non_rescue_override':0,
    }
    for r in df[['ai_correct','accept_ai','override','final_correct']].itertuples(index=False):
        counts[classify_outcome_state(int(r.ai_correct),int(r.accept_ai),int(r.override),int(r.final_correct))]+=1
    if sum(counts.values()) != len(df):
        raise AssertionError('Five-state outcomes do not exhaust all trials.')
    shares={k:v/len(df) for k,v in counts.items()}
    if not math.isclose(sum(shares.values()),1.0,rel_tol=0,abs_tol=1e-12):
        raise AssertionError('Five-state outcome shares do not sum to 1.')
    return {'dataset':label,**shares,'partition_sum':sum(shares.values())}


def fit_cluster_logit(df,outcome,controls=()):
    x=df[df.opportunity_wrong_ai.eq(1)|df.opportunity_correct_ai.eq(1)].copy()
    x['human_advantage']=x.opportunity_wrong_ai.astype(int)
    X=x[['human_advantage']].astype(float).copy()
    for c in controls:
        X[c]=(x.trial.astype(float)-x.trial.astype(float).mean())/x.trial.astype(float).std(ddof=0) if c=='trial_scaled' else x[c].astype(float)
    X=sm.add_constant(X,has_constant='add')
    fit=sm.GLM(x[outcome].astype(float),X,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':x.participant.astype(str)})
    ci=fit.conf_int()
    out=[]
    for term in fit.params.index:
        b=float(fit.params[term])
        out.append({'outcome':outcome,'term':term,'B':b,'SE':float(fit.bse[term]),'OR':math.exp(b),'p':float(fit.pvalues[term]),'CI_low':math.exp(float(ci.loc[term,0])),'CI_high':math.exp(float(ci.loc[term,1]))})
    return pd.DataFrame(out)


def validate_msod(msod_root: Path):
    d=msod_root/'data'
    cases=pd.read_csv(d/'msod_case_master.csv')
    cond=pd.read_csv(d/'condition_matrix.csv')
    stim=pd.read_csv(d/'msod_stimulus_bank_80.csv')
    if (len(cases),len(cond),len(stim))!=(10,8,80):
        raise ValueError('MSOD expected 10 cases, 8 conditions, and 80 stimuli.')
    if stim.stimulus_id.duplicated().any():
        raise ValueError('Duplicate MSOD stimulus IDs.')
    mismatches=0
    for _,r in stim.iterrows():
        expected=r.criterion_correct_final_decision if r.ai_correctness_condition=='correct' else ('approve' if r.criterion_correct_final_decision=='reject' else 'reject')
        mismatches += int(r.stage2_ai_recommendation != expected)
    if mismatches:
        raise ValueError(f'MSOD has {mismatches} AI/criterion mismatches.')
    return {'cases':10,'conditions':8,'stimuli':80,'domains':int(cases.strategic_domain.nunique()),'ai_assignment_mismatches':0,'contains_human_responses':False}


def analyze_msod_responses(df: pd.DataFrame):
    """Analyze genuine collected MSOD responses; never simulates missing responses."""
    required={'participant_id','representation_condition','human_only_information_condition','ai_correctness_condition','initial_decision','ai_recommendation','final_decision','criterion_correct_final_decision'}
    missing=required-set(df.columns)
    if missing:
        raise ValueError(f"Missing MSOD response columns: {sorted(missing)}")
    x=df.copy()
    x['override']=(x.final_decision.astype(str)!=x.ai_recommendation.astype(str)).astype(int)
    x['decision_accuracy']=(x.final_decision.astype(str)==x.criterion_correct_final_decision.astype(str)).astype(int)
    x['justified_override']=x.override*x.decision_accuracy
    x['unjustified_override']=x.override*(1-x.decision_accuracy)
    x['decision_revision']=(x.final_decision.astype(str)!=x.initial_decision.astype(str)).astype(int)
    wrong=x.ai_correctness_condition.astype(str).eq('incorrect')
    correct=x.ai_correctness_condition.astype(str).eq('correct')
    osi_value=float(x.loc[wrong,'override'].mean()-x.loc[correct,'override'].mean()) if wrong.any() and correct.any() else float('nan')
    summary=pd.DataFrame([{'participants':x.participant_id.nunique(),'trials':len(x),'final_accuracy':x.decision_accuracy.mean(),'override_rate':x.override.mean(),'override_when_ai_incorrect':x.loc[wrong,'override'].mean(),'override_when_ai_correct':x.loc[correct,'override'].mean(),'msod_override_selectivity':osi_value}])
    cells=x.groupby(['representation_condition','human_only_information_condition','ai_correctness_condition'],as_index=False).agg(n=('override','size'),override_rate=('override','mean'),accuracy=('decision_accuracy','mean'),justified_override_rate=('justified_override','mean'),unjustified_override_rate=('unjustified_override','mean'))
    return x,summary,cells
