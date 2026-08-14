from pathlib import Path
import json,math
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
EXP=json.loads((ROOT/'reproducibility/expected_results.json').read_text())
S=pd.read_csv(ROOT/'results/study_summary.csv').set_index('dataset')
F=pd.read_csv(ROOT/'results/five_state_outcomes.csv').set_index('dataset')
M=pd.read_csv(ROOT/'results/msod_design_summary.csv').iloc[0]
B=pd.read_csv(ROOT/'results/fifar_benchmark_summary.csv').set_index('metric')['value']
assert round(float(S.loc['Loan decisions','osi']),3)==EXP['loan_osi_round3']
assert round(float(S.loc['Chess decisions','osi']),3)==EXP['chess_osi_round3']
assert int(S.loc['Loan decisions','n_trials'])==EXP['loan_trials']
assert int(S.loc['Chess decisions','n_trials'])==EXP['chess_trials']
assert int(S.loc['Loan decisions','participants'])==EXP['loan_participants']
assert int(S.loc['Chess decisions','participants'])==EXP['chess_participants']
assert round(float(F.loc['Loan','non_rescue_override']),6)==EXP['loan_non_rescue_override_round6']
assert round(float(F.loc['Chess','non_rescue_override']),6)==EXP['chess_non_rescue_override_round6']
assert round(float(F.loc['Chess','unjustified_override']),6)==EXP['chess_unjustified_override_round6']
assert round(float(F.loc['Loan','appropriate_reliance']),6)==EXP['loan_appropriate_reliance_round6']
assert round(float(F.loc['Loan','justified_override']),6)==EXP['loan_justified_override_round6']
assert round(float(F.loc['Loan','automation_failure']),6)==EXP['loan_automation_failure_round6']
assert round(float(F.loc['Loan','unjustified_override']),6)==EXP['loan_unjustified_override_round6']
assert round(float(F.loc['Chess','appropriate_reliance']),6)==EXP['chess_appropriate_reliance_round6']
assert round(float(F.loc['Chess','justified_override']),6)==EXP['chess_justified_override_round6']
assert round(float(F.loc['Chess','automation_failure']),6)==EXP['chess_automation_failure_round6']
assert all(math.isclose(float(v),1.0,abs_tol=1e-12) for v in F.partition_sum)
assert (int(M.cases),int(M.conditions),int(M.stimuli))==(EXP['msod_cases'],EXP['msod_conditions'],EXP['msod_stimuli'])
assert int(float(B.base_records))==EXP['fifar_base_records']
assert int(float(B.synthetic_experts))==EXP['fifar_synthetic_experts']
assert int(float(B.test_team_configurations))==EXP['fifar_test_team_configurations']
print('REPRODUCTION VERIFICATION PASSED')
