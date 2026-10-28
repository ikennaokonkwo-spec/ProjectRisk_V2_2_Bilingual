"""Verify formulas, cached upload values, fixed-only packages and native controls."""
import openpyxl
from copy import deepcopy
from data_io.input_reader import read_v1_workbook
from data_io.model_adapter import to_model_objects
from core.validation import validate_all
from core.simulation import simulate
p='project_risk_template_v2_2.xlsx'
f=openpyxl.load_workbook(p,data_only=False);v=openpyxl.load_workbook(p,data_only=True)
assert sum(c.data_type=='f' for s in f for row in s for c in row)==210
assert len(f['Activities'].conditional_formatting)==3
assert len(f['Activities'].data_validations.dataValidation)==3
assert f['Activities'].freeze_panes is not None
d=read_v1_workbook(p)
assert not [x for x in validate_all(d) if x.severity=='Error']
a,r,m=to_model_objects(d)
fixed=[]
originals=dict(zip(d['Case_Assumptions']['Activity_ID'],d['Case_Assumptions']['Original_Base_Cost']))
for act in a:
    mode=act['cost_association']
    if mode=='Fixed only':
        fixed.append(act['id']);assert act['cost_rate']==0
        assert act['cost_params']['fixed']==originals[act['id']]
assert set(fixed)=={'A15','A22','A23','A24','A29','A30'}
# A duration-only event on a fixed-price activity cannot increase its time cost.
activity=next(x for x in a if x['id']=='A15');activity=deepcopy(activity);activity['predecessors']=[]
risk=[{'id':'R','type':'Threat','probability':1,'active':True}]
map_=[{'risk_id':'R','activity_id':'A15','impact_type':'Duration','distribution':'Fixed','params':{'fixed':5}}]
result=simulate([activity],risk,map_,4,42)
assert (result['project']['Cost']==45000).all()
# Missing cached formulas must be exposed rather than silently treated as zero.
bad=deepcopy(d);bad['Activities'].loc[0,'Fixed_Cost']=float('nan')
assert any('no saved result' in x.message for x in validate_all(bad))
print('test_live_workbook: PASS')
