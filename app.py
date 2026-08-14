from pathlib import Path
import pandas as pd,gradio as gr,tempfile
from src.strategic_override.analysis import summarize_trials,five_states,validate_msod,analyze_msod_responses
BASE=Path(__file__).resolve().parent
def behavioral(choice,uploaded):
    df=pd.read_csv(uploaded) if uploaded else pd.read_csv(BASE/'data'/('loan_trials.csv' if choice=='Loan decisions' else 'chess_trials.csv'))
    label=Path(uploaded).name if uploaded else choice
    s=summarize_trials(label,df)
    f=five_states(label,df)
    state_table=pd.DataFrame([{'Outcome':k.replace('_',' ').title(),'Share':v} for k,v in f.items() if k not in {'dataset','partition_sum'}])
    note=(f"**OSI = {s['osi']:.3f}**; participant-bootstrap 95% CI [{s['osi_ci_low']:.3f}, {s['osi_ci_high']:.3f}]. "
          f"Five-state partition sum = **{f['partition_sum']:.3f}**. Non-rescue override = **{100*f['non_rescue_override']:.1f}%**.")
    return pd.DataFrame(s.items(),columns=['Metric','Value']),state_table,note
def msod():
    s=validate_msod(BASE/'data/msod'); m=pd.read_csv(BASE/'data/msod/data/msod_stimulus_bank_80.csv'); return pd.DataFrame(s.items(),columns=['Metric','Value']),m[['stimulus_id','case_id','strategic_domain','representation_condition','human_only_information_condition','ai_correctness_condition']]
def msod_responses(uploaded):
    if not uploaded: raise gr.Error('Upload a genuine collected MSOD response CSV. The software will not create participant responses.')
    scored,summary,cells=analyze_msod_responses(pd.read_csv(uploaded)); out=Path(tempfile.gettempdir())/'msod_scored_responses.csv'; scored.to_csv(out,index=False); return summary,cells,str(out)
def fifar(): return pd.read_csv(BASE/'data/fifar/benchmark_summary.csv')
with gr.Blocks(title='Strategic Override Research Studio') as demo:
    gr.Markdown('# Strategic Override Research Studio\nOne interface for two human behavioral datasets, FiFAR, and MSOD v1.0. **No behavioral conclusion is generated from synthetic FiFAR experts or uncollected MSOD responses.**')
    with gr.Tab('Behavioral OSI'):
        c=gr.Radio(['Loan decisions','Chess decisions'],value='Loan decisions')
        u=gr.File(file_types=['.csv'],type='filepath')
        b=gr.Button('Run analysis',variant='primary')
        o=gr.Dataframe(label='Behavioral summary')
        st=gr.Dataframe(label='Five-state outcome decomposition')
        t=gr.Markdown()
        b.click(behavioral,[c,u],[o,st,t])
    with gr.Tab('MSOD instrument'):
        gr.Markdown('Validates 10 strategic cases × 8 conditions = 80 stimuli. MSOD v1.0 contains no manager responses.'); b=gr.Button('Validate MSOD'); s=gr.Dataframe(); m=gr.Dataframe(); b.click(msod,outputs=[s,m])
    with gr.Tab('MSOD collected responses'):
        gr.Markdown('Upload **genuine collected MSOD responses** using the supplied response schema. The software derives override, accuracy, justified/unjustified override, factorial-cell summaries, and an AI-correctness selective-override contrast.'); ur=gr.File(file_types=['.csv'],type='filepath'); br=gr.Button('Analyze collected responses'); sr=gr.Dataframe(); cr=gr.Dataframe(); dr=gr.File(); br.click(msod_responses,ur,[sr,cr,dr])
    with gr.Tab('FiFAR'):
        gr.Markdown('Structural audit of the attached FiFAR benchmark. The 50 experts are synthetic.'); b=gr.Button('Show audit'); f=gr.Dataframe(); b.click(fifar,outputs=f)
    with gr.Tab('Reproduce'):
        gr.Markdown('Run `python reproduce.py` locally or **Actions → Reproduce Complete Strategic Override Study → Run workflow** on GitHub. The workflow runs 7 tests, regenerates outputs, and independently verifies expected primary results from `reproducibility/`.')
if __name__=='__main__': demo.launch()
