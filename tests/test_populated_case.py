import openpyxl
from data_io.input_reader import read_v1_workbook
from core.validation import validate_all
from core.register import treatment_specs
from data_io.model_adapter import to_model_objects
from core.distributions import expected_value
w=openpyxl.load_workbook('project_risk_template_v2_2.xlsx',data_only=True)
d=read_v1_workbook('project_risk_template_v2_2.xlsx')
assert not [x for x in validate_all(d) if x.severity=='Error']
a,r,m=to_model_objects(d)
assert len(a)==30 and len(r)==24 and len(treatment_specs(d))==24
originals=dict(zip(d['Case_Assumptions']['Activity_ID'],d['Case_Assumptions']['Original_Base_Cost']))
for act in a:
    original=originals[act['id']]
    reference=act['cost_params']['fixed']+act['cost_rate']*expected_value(act['duration_model'],act['duration_params'])
    assert abs(original-reference)<.011,(act['id'],original,reference)
for _,row in d['Risk_Register'].iterrows():
    assert row.iloc[16:26].notna().all()
    assert row['Residual_Acceptance']=='Pending'
for risk,spec in zip(r,treatment_specs(d)):
    if risk['type']=='Opportunity':assert spec['new_probability']>=risk['probability']
    else:assert spec['new_probability']<=risk['probability']
assert d['Activities'].iloc[0]['Duration_Model']=='Fixed'
assert len(w['Activities'].conditional_formatting)==3
print('test_populated_case: PASS')
