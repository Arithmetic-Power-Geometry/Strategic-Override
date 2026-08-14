from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from src.strategic_override.analysis import summarize_trials,five_states,fit_cluster_logit,validate_msod
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
RESULTS=ROOT/'results'
RESULTS.mkdir(exist_ok=True)


def figures(summary,states,balance):
    fig,ax=plt.subplots(figsize=(6.8,4.1))
    x=np.arange(len(summary)); y=summary.osi.to_numpy(float)
    lo=y-summary.osi_ci_low.to_numpy(float); hi=summary.osi_ci_high.to_numpy(float)-y
    ax.errorbar(x,y,yerr=np.vstack([lo,hi]),fmt='o',capsize=5,linewidth=1.7)
    ax.axhline(0,linewidth=1)
    ax.set_xticks(x,['Loan','Chess'])
    ax.set_ylabel('Override Selectivity Index (OSI)')
    ax.set_title('Selective disagreement with AI differs by task')
    fig.tight_layout(); fig.savefig(RESULTS/'figure_osi.png',dpi=220,bbox_inches='tight'); plt.close(fig)

    cols=['appropriate_reliance','justified_override','automation_failure','unjustified_override','non_rescue_override']
    labs=['Appropriate reliance','Justified override / rescue','Automation failure','Unjustified override','Non-rescue override']
    fig,ax=plt.subplots(figsize=(9.0,4.8)); x=np.arange(len(states)); w=.15
    for i,(c,l) in enumerate(zip(cols,labs)):
        ax.bar(x+(i-2)*w,states[c],w,label=l)
    ax.set_xticks(x,states.dataset)
    ax.set_ylabel('Share of all trials')
    ax.set_title('Five mutually exclusive human-AI decision outcomes')
    ax.legend(fontsize=8,frameon=False,ncol=2)
    fig.tight_layout(); fig.savefig(RESULTS/'figure_five_states.png',dpi=220,bbox_inches='tight'); plt.close(fig)

    fig,ax=plt.subplots(figsize=(8,4.3))
    ax.bar(balance.condition_id,balance.stimuli)
    ax.set_ylabel('Stimuli'); ax.set_title('MSOD v1.0: balanced factorial cells')
    fig.tight_layout(); fig.savefig(RESULTS/'figure_msod_balance.png',dpi=220,bbox_inches='tight'); plt.close(fig)


def main():
    for old in ('figure_four_states.png','four_state_outcomes.csv'):
        p=RESULTS/old
        if p.exists(): p.unlink()
    loan=pd.read_csv(DATA/'loan_trials.csv')
    chess=pd.read_csv(DATA/'chess_trials.csv')
    summary=pd.DataFrame([summarize_trials('Loan decisions',loan),summarize_trials('Chess decisions',chess)])
    summary.to_csv(RESULTS/'study_summary.csv',index=False)

    states=pd.DataFrame([five_states('Loan',loan),five_states('Chess',chess)])
    if not np.allclose(states.partition_sum.to_numpy(float),1.0,rtol=0,atol=1e-12):
        raise AssertionError('Five-state partition failed.')
    states.to_csv(RESULTS/'five_state_outcomes.csv',index=False)

    mods=[]
    for label,df,controls in [('Loan',loan,()),('Chess',chess,('selfconf','aiconf','trial_scaled'))]:
        for outcome in ('final_correct','override'):
            m=fit_cluster_logit(df,outcome,controls); m.insert(0,'dataset',label); mods.append(m)
    pd.concat(mods,ignore_index=True).to_csv(RESULTS/'clustered_logit_models.csv',index=False)

    ms=validate_msod(DATA/'msod')
    pd.DataFrame([ms]).to_csv(RESULTS/'msod_design_summary.csv',index=False)
    stim=pd.read_csv(DATA/'msod/data/msod_stimulus_bank_80.csv')
    balance=stim.groupby(['condition_id','representation_condition','human_only_information_condition','ai_correctness_condition'],as_index=False).size().rename(columns={'size':'stimuli'})
    balance.to_csv(RESULTS/'msod_condition_balance.csv',index=False)
    stim.groupby(['case_id','strategic_domain','case_title'],as_index=False).size().rename(columns={'size':'stimuli'}).to_csv(RESULTS/'msod_case_manifest.csv',index=False)

    fifar=pd.read_csv(DATA/'fifar/benchmark_summary.csv')
    fifar.to_csv(RESULTS/'fifar_benchmark_summary.csv',index=False)
    figures(summary,states,balance)

    resources=pd.DataFrame([
        {'resource':'Loan human-AI experiment','status':'empirical human behavior','records':len(loan),'units':loan.participant.nunique()},
        {'resource':'Chess human-AI experiment','status':'empirical human behavior','records':len(chess),'units':chess.participant.nunique()},
        {'resource':'FiFAR','status':'synthetic-expert benchmark','records':1000000,'units':50},
        {'resource':'MSOD v1.0','status':'experimental instrument; no responses','records':80,'units':10}
    ])
    resources.to_csv(RESULTS/'resource_integration.csv',index=False)

    s={
        'real_human_trials':int(len(loan)+len(chess)),
        'real_human_participants':int(loan.participant.nunique()+chess.participant.nunique()),
        'loan_osi':float(summary.iloc[0].osi),
        'chess_osi':float(summary.iloc[1].osi),
        'loan_non_rescue_override':float(states.loc[states.dataset.eq('Loan'),'non_rescue_override'].iloc[0]),
        'chess_non_rescue_override':float(states.loc[states.dataset.eq('Chess'),'non_rescue_override'].iloc[0]),
        'five_state_partition_verified':bool(np.allclose(states.partition_sum.to_numpy(float),1.0,rtol=0,atol=1e-12)),
        'msod':ms,
        'fifar_base_records':1000000,
        'fifar_synthetic_experts':50
    }
    (RESULTS/'summary.json').write_text(json.dumps(s,indent=2))
    (RESULTS/'REPORT.md').write_text(
        f"# Complete reproducibility report\n\n"
        f"- Real human-AI behavioral trials: **{s['real_human_trials']:,}** from **{s['real_human_participants']}** participants.\n"
        f"- Loan OSI: **{s['loan_osi']:.3f}**.\n"
        f"- Chess OSI: **{s['chess_osi']:.3f}**.\n"
        f"- Five-state outcome partition: **verified for both datasets**.\n"
        f"- Loan non-rescue override: **{100*s['loan_non_rescue_override']:.1f}%**.\n"
        f"- Chess non-rescue override: **{100*s['chess_non_rescue_override']:.1f}%**.\n\n"
        f"## Five-state outcome shares\n\n"
        f"| Dataset | Appropriate reliance | Justified override | Automation failure | Unjustified override | Non-rescue override |\n"
        f"|---|---:|---:|---:|---:|---:|\n"
        f"| Loan | {100*states.loc[states.dataset.eq('Loan'),'appropriate_reliance'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Loan'),'justified_override'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Loan'),'automation_failure'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Loan'),'unjustified_override'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Loan'),'non_rescue_override'].iloc[0]:.1f}% |\n"
        f"| Chess | {100*states.loc[states.dataset.eq('Chess'),'appropriate_reliance'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Chess'),'justified_override'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Chess'),'automation_failure'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Chess'),'unjustified_override'].iloc[0]:.1f}% | {100*states.loc[states.dataset.eq('Chess'),'non_rescue_override'].iloc[0]:.1f}% |\n\n"
        f"- MSOD: **10 cases x 8 conditions = 80 stimuli**, 0 AI-assignment mismatches, no human responses in v1.0.\n"
        f"- FiFAR: **1,000,000 base records**, **50 synthetic experts**, **25 test-team configurations**.\n\n"
        f"Behavioral claims use only the loan and chess human-participant data.\n"
    )
    lines=[]
    for f in sorted(RESULTS.iterdir()):
        if f.is_file() and f.name!='SHA256SUMS.txt':
            lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}")
    (RESULTS/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
    print(summary.to_string(index=False))
    print('\nFive-state outcomes')
    print(states.to_string(index=False))
    print('\nMSOD',ms)

if __name__=='__main__':
    main()
