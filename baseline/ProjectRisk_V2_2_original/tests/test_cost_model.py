import unittest
from copy import deepcopy
from io import BytesIO
from zipfile import ZipFile
from core.cost_model import cost_input_summary
from core.simulation import simulate
from core.validation import validate_all
from data_io.input_reader import read_v1_workbook
from data_io.model_adapter import to_model_objects
from data_io.export_results import results_zip

class CostModelTests(unittest.TestCase):
    def setUp(self):
        self.data=read_v1_workbook('project_risk_template_v2_2.xlsx')
    def test_fixed_only_enforced_in_core(self):
        a=[{'id':'A','predecessors':[],'duration_model':'Fixed','duration_params':{'fixed':10},'cost_model':'Fixed','cost_params':{'fixed':100},'cost_rate':99,'cost_association':'Fixed only'}]
        r=[{'id':'R','type':'Threat','probability':1,'active':True}]
        m=[{'risk_id':'R','activity_id':'A','impact_type':'Duration','distribution':'Fixed','params':{'fixed':5}}]
        out=simulate(a,r,m,4,1)
        self.assertTrue((out['project']['Cost']==100).all())
        self.assertTrue((out['project']['Duration']==15).all())
        m.append({'risk_id':'R','activity_id':'A','impact_type':'Cost','distribution':'Fixed','params':{'fixed':20}})
        self.assertTrue((simulate(a,r,m,4,1)['project']['Cost']==120).all())
    def test_current_and_stale_workbook(self):
        self.assertFalse([x for x in validate_all(self.data) if x.severity=='Error'])
        for column,value in [('Original_Base_Cost',24000),('Time_Dependent_Share',.5)]:
            d=deepcopy(self.data);d['Case_Assumptions'].loc[0,column]=value
            self.assertTrue(any('saved cost formulas' in x.message for x in validate_all(d)))
        d=deepcopy(self.data);d['Activities'].loc[0,'Duration_Fixed']=6
        self.assertTrue(any('saved cost formulas' in x.message for x in validate_all(d)))
        d=deepcopy(self.data);d['Case_Assumptions']=d['Case_Assumptions'].iloc[::-1]
        self.assertFalse([x for x in validate_all(d) if x.severity=='Error'])
    def test_summary_and_export(self):
        a,r,m=to_model_objects(self.data);summary=cost_input_summary(a)
        self.assertEqual((summary['Cost_Association']=='Fixed only').sum(),6)
        self.assertAlmostEqual(summary['Reference_Total_Cost'].sum(),1057000,delta=.31)
        out=simulate(a,r,m,4,1)
        payload=results_zip(out['project'],out['activities'],out['risks'],summary,summary,cost_inputs=summary)
        with ZipFile(BytesIO(payload)) as z:self.assertIn('activity_cost_inputs.csv',z.namelist())
if __name__=='__main__':unittest.main()
