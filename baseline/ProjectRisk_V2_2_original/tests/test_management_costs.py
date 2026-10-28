import unittest
from copy import deepcopy
import pandas as pd
from core.simulation import simulate
from core.treatment import apply_treatments
from core.validation import validate_all
from data_io.input_reader import read_v1_workbook
from data_io.model_adapter import to_model_objects
from core.risk_analysis import risk_importance
from core.register import register_view, treatment_specs
from core.risk_portrait import build_risk_portrait

class ManagementCosts(unittest.TestCase):
    def setUp(self):
        self.a=[{'id':'A','predecessors':[],'duration_model':'Fixed','duration_params':{'fixed':10},'cost_model':'Fixed','cost_params':{'fixed':100},'cost_rate':5}]
        self.r=[{'id':'R','type':'Threat','probability':1.,'active':True}]
        self.m=[{'risk_id':'R','activity_id':'A','impact_type':'Duration','distribution':'Fixed','params':{'fixed':2}}, {'risk_id':'R','activity_id':'A','impact_type':'Cost','distribution':'Fixed','params':{'fixed':30}}]
    def test_cost_decomposition_and_independent_treatment(self):
        before=simulate(self.a,self.r,self.m,4,42)
        self.assertEqual(before['project'].iloc[0]['Cost'],190)
        rr,mm=apply_treatments(self.r,self.m,[{'risk_id':'R','duration_multiplier':.5,'cost_multiplier':0}])
        after=simulate(self.a,rr,mm,4,42)
        self.assertEqual(after['project'].iloc[0]['Duration'],11)
        self.assertEqual(after['project'].iloc[0]['Cost'],155)
        self.assertEqual(self.m[0]['params']['fixed'],2)
        self.assertEqual(before['activities'].iloc[0]['Duration_Related_Cost_Change'],10)
    def test_shared_occurrence_and_inactive_risk(self):
        self.a.append(dict(self.a[0],id='B',predecessors=['A']))
        self.m.append(dict(self.m[0],activity_id='B'))
        self.r[0]['probability']=.5
        out=simulate(self.a,self.r,self.m,50,9)
        durations=out['activities'].pivot(index='Iteration',columns='Activity_ID',values='Final_Duration')
        self.assertTrue(durations['A'].equals(durations['B']))
        self.r[0]['active']=False
        out=simulate(self.a,self.r,self.m,4,9)
        self.assertFalse(out['risks']['Occurred'].any())
        self.assertTrue((out['project']['Cost']==300).all())
    def test_opportunity_cost_floor(self):
        self.r[0]['type']='Opportunity';self.m[1]['params']['fixed']=1000
        out=simulate(self.a,self.r,self.m,4,1)
        self.assertTrue((out['project']['Cost']==0).all())
        self.assertTrue((out['project']['Duration']==8).all())
    def test_workbook_and_legacy_compatibility(self):
        data=read_v1_workbook('project_risk_template_v2_2.xlsx')
        self.assertFalse([x for x in validate_all(data) if x.severity=='Error'])
        a,r,m=to_model_objects(data)
        out=simulate(a,r,m,4,1)
        zero_rate=deepcopy(data);zero_rate['Activities']['Cost_Rate']=0.0
        za,zr,zm=to_model_objects(zero_rate)
        legacy_reference=simulate(za,zr,zm,4,1)
        old=deepcopy(zero_rate);old['Activities']=old['Activities'].rename(columns={'Fixed_Cost':'Base_Cost'}).drop(columns='Cost_Rate')
        aa,rr,mm=to_model_objects(old)
        pd.testing.assert_frame_equal(legacy_reference['project'],simulate(aa,rr,mm,4,1)['project'])
        ranking=risk_importance(out['project'],out['risks'])
        self.assertEqual(len(register_view(data,ranking)),len(data['Risk_Register']))
        portrait,scenarios=build_risk_portrait(a,r,m,ranking,4,1,baseline_result=out)
        self.assertIs(scenarios['ST'],out)
        bad=deepcopy(data);bad['Activities']['Cost_Rate']=bad['Activities']['Cost_Rate'].astype(float);bad['Activities'].loc[0,'Cost_Rate']=float('inf')
        self.assertTrue([x for x in validate_all(bad) if x.severity=='Error'])
        inactive=deepcopy(data);inactive['Risk_Register'].loc[0,'Active']=False;inactive['Risk_Register'].loc[0,'Probability']=float('nan');inactive['Risk_Treatments']=inactive['Risk_Treatments'].query("Risk_ID != 'R01'")
        self.assertFalse([x for x in validate_all(inactive) if x.severity=='Error'])
    def test_both_mapping_separate_multipliers(self):
        m=[dict(self.m[0],impact_type='Both')]
        rr,mm=apply_treatments(self.r,m,[{'risk_id':'R','duration_multiplier':0,'cost_multiplier':3}])
        out=simulate(self.a,rr,mm,4,1)
        self.assertEqual(out['project'].iloc[0]['Duration'],10)
        self.assertEqual(out['project'].iloc[0]['Cost'],156)

if __name__=='__main__':unittest.main()
