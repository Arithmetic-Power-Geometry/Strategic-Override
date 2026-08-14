from pathlib import Path
import math
import pandas as pd
from src.strategic_override.analysis import osi,validate_msod,five_states,classify_outcome_state
ROOT=Path(__file__).resolve().parents[1]


def test_known_osi():
    assert round(osi(pd.read_csv(ROOT/'data/loan_trials.csv')),3)==-0.095
    assert round(osi(pd.read_csv(ROOT/'data/chess_trials.csv')),3)==0.292


def test_counts():
    a=pd.read_csv(ROOT/'data/loan_trials.csv')
    b=pd.read_csv(ROOT/'data/chess_trials.csv')
    assert (len(a),a.participant.nunique(),len(b),b.participant.nunique())==(2810,281,3000,100)


def test_msod():
    s=validate_msod(ROOT/'data/msod')
    assert s['stimuli']==80 and s['ai_assignment_mismatches']==0 and not s['contains_human_responses']


def test_fifar():
    f=pd.read_csv(ROOT/'data/fifar/benchmark_summary.csv').set_index('metric')['value']
    assert int(float(f.base_records))==1000000 and int(float(f.synthetic_experts))==50 and int(float(f.test_team_configurations))==25


def test_msod_response_analyzer_schema():
    from src.strategic_override.analysis import analyze_msod_responses
    d=pd.DataFrame([
      {'participant_id':'T1','representation_condition':'low_qc_candidate','human_only_information_condition':'absent','ai_correctness_condition':'correct','initial_decision':'reject','ai_recommendation':'reject','final_decision':'reject','criterion_correct_final_decision':'reject'},
      {'participant_id':'T1','representation_condition':'high_qc_candidate','human_only_information_condition':'present','ai_correctness_condition':'incorrect','initial_decision':'reject','ai_recommendation':'reject','final_decision':'approve','criterion_correct_final_decision':'approve'}])
    scored,summary,cells=analyze_msod_responses(d)
    assert len(scored)==2 and summary.iloc[0].trials==2 and len(cells)==2


def test_five_state_partition_on_real_data():
    loan=five_states('Loan',pd.read_csv(ROOT/'data/loan_trials.csv'))
    chess=five_states('Chess',pd.read_csv(ROOT/'data/chess_trials.csv'))
    assert math.isclose(loan['partition_sum'],1.0,abs_tol=1e-12)
    assert math.isclose(chess['partition_sum'],1.0,abs_tol=1e-12)
    assert loan['non_rescue_override']==0.0
    assert round(chess['non_rescue_override'],6)==0.173333
    assert round(chess['unjustified_override'],6)==0.191667


def test_multiclass_non_rescue_rule():
    # Criterion=A, AI=B, human=C: AI is wrong, human rejects it, but does not reach the criterion-correct action.
    assert classify_outcome_state(ai_correct=0,accept_ai=0,override=1,final_correct=0)=='non_rescue_override'
