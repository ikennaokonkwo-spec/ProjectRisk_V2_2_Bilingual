"""Distribution mathematics, input boundaries, worksheet rules and full-model checks."""
from pathlib import Path
import copy,io,json,math,sys,types,unittest,zipfile
import numpy as np
import pandas as pd
import openpyxl
from core.distributions import sample_distribution,expected_value,positive_moments
from core.validation import validate_all
from core.simulation import simulate
from core.risk_analysis import risk_importance,project_statistics
from core.risk_portrait import build_risk_portrait
from core.treatment import apply_treatments
from data_io.input_reader import read_v1_workbook
from data_io.model_adapter import to_model_objects,_params
from localization import set_language,PT
from localization.schema import CONTROLLED
ROOT=Path(__file__).resolve().parents[1]
NEW=['Exponential','Lognormal','Gamma']
ALL=['Fixed','Triangular','Beta-PERT','Uniform','Normal']+NEW
REQUIRED={'Fixed':{0},'Triangular':{1,2,3},'Beta-PERT':{1,2,3},'Uniform':{1,3},'Normal':{4,5},'Exponential':{4},'Lognormal':{4,5},'Gamma':{4,5}}
class DistributionTests(unittest.TestCase):
 def tearDown(self):set_language('en')
 def test_old_sampler_and_expected_values_are_exact(self):
  old=types.ModuleType('original_distributions')
  with zipfile.ZipFile(ROOT/'baseline/ProjectRisk_V2_2_original.zip') as z:exec(z.read('ProjectRisk_V2_2/core/distributions.py'),old.__dict__)
  params={'Fixed':{'fixed':5},'Triangular':{'min':2,'most_likely':4,'max':8},'Beta-PERT':{'min':2,'most_likely':4,'max':8},'Uniform':{'min':2,'max':8},'Normal':{'mean':5,'sd':1.25}}
  for model,p in params.items():
   a=np.random.default_rng(123);b=np.random.default_rng(123)
   self.assertEqual(expected_value(model,p),old.expected_value(model,p))
   np.testing.assert_array_equal([sample_distribution(model,p,a) for _ in range(2000)],[old.sample_distribution(model,p,b) for _ in range(2000)])
 def test_parameter_conversions_and_means(self):
  for model in NEW:
   p=positive_moments(model,{'mean':5,'sd':1.25});self.assertEqual(expected_value(model,p),5)
   if model=='Gamma':self.assertEqual(p['shape'],16);self.assertEqual(p['scale'],.3125)
   if model=='Lognormal':
    self.assertAlmostEqual(math.exp(p['log_mean']+p['log_sd']**2/2),5)
    self.assertAlmostEqual(math.sqrt((math.exp(p['log_sd']**2)-1)*math.exp(2*p['log_mean']+p['log_sd']**2)),1.25)
 def test_new_seeded_draws_match_numpy(self):
  for model in NEW:
   p=positive_moments(model,{'mean':5,'sd':1.25});a=np.random.default_rng(42);b=np.random.default_rng(42)
   expected=(b.exponential(5,100) if model=='Exponential' else b.lognormal(p['log_mean'],p['log_sd'],100) if model=='Lognormal' else b.gamma(p['shape'],p['scale'],100))
   np.testing.assert_array_equal([sample_distribution(model,p,a) for _ in range(100)],expected)
 def test_monte_carlo_moments_and_positive_support(self):
  for model in NEW:
   p=positive_moments(model,{'mean':5,'sd':1.25});rng=np.random.default_rng(12345)
   x=np.array([sample_distribution(model,p,rng) for _ in range(50000)])
   target_sd=5 if model=='Exponential' else 1.25
   self.assertTrue(np.all(np.isfinite(x)) and np.all(x>=0))
   self.assertAlmostEqual(x.mean(),5,delta=6*target_sd/math.sqrt(len(x)))
   self.assertAlmostEqual(x.std(),target_sd,delta=.05*target_sd)
 def test_invalid_moments_rejected_in_all_input_locations(self):
  base=read_v1_workbook(ROOT/'project_risk_template_v2_2.xlsx')
  for model in NEW:
   for column,sheet,prefix in [('Duration_Model','Activities','Duration'),('Cost_Model','Activities','Cost'),('Distribution','Risk_Activity_Map','Impact')]:
    for mean,sd in [(0,1),(-1,1),(float('nan'),1),(float('inf'),1),(None,1)]+([] if model=='Exponential' else [(1,0),(1,-1),(1,float('nan')),(1,float('inf')),(1,None)]):
     data=copy.deepcopy(base);df=data[sheet];df[column]=df[column].astype(object);df.loc[0,column]=model;df.loc[0,prefix+'_Mean']=mean
     df.loc[0,prefix+'_SD']=sd
     self.assertTrue(any(i.severity=='Error' and 'invalid parameters' in i.message for i in validate_all(data)),(model,sheet,mean,sd))
  with self.assertRaises(ValueError):positive_moments('Gamma',{'mean':1e308,'sd':1e-308})
 def test_unused_parameters_are_not_repurposed(self):
  row={'Duration_Mean':5,'Duration_SD':0,'Duration_Min':999,'Duration_Max':1000,'Duration_Fixed':222}
  p=_params(row,'Duration','Exponential');self.assertEqual(p,{'mean':5})
  for m in ['Lognormal','Gamma']:
   row['Duration_SD']=1.25;p=_params(row,'Duration',m);self.assertEqual(expected_value(m,p),5)
 def test_probability_models_are_unchanged(self):
  self.assertEqual(CONTROLLED['Probability_Model'],{'Fixed','Uniform'})
  data=read_v1_workbook(ROOT/'project_risk_template_v2_2.xlsx');data['Risk_Register'].loc[0,'Probability_Model']='Exponential'
  self.assertTrue(any('Probability_Model must be Fixed or Uniform' in i.message for i in validate_all(data)))
 def test_bilingual_workbook_lists_and_highlighting(self):
  for lang,filename in [('en','project_risk_template_v2_2.xlsx'),('pt_BR','project_risk_template_v2_2_pt_BR.xlsx')]:
   w=openpyxl.load_workbook(ROOT/filename)
   translate=lambda s:PT.get(s,s) if lang=='pt_BR' else s
   sheet=lambda s:translate(s)
   for sn,selector,first,end in [('Activities','D',5,99),('Activities','N',15,99),('Risk_Activity_Map','D',5,299)]:
    s=w[sheet(sn)]
    dropdown=next(dv for dv in s.data_validations.dataValidation if dv.type=='list' and dv.sqref==f'{selector}3:{selector}{end}')
    self.assertEqual(dropdown.formula1.strip('"').split(','),[translate(m) for m in ALL])
    for model in ALL:
     active=set()
     for cellrange in s.conditional_formatting:
      for rule in s.conditional_formatting[cellrange]:
       if not rule.formula:continue
       expr=rule.formula[0]
       if '$'+selector+'3=' not in expr or '"'+translate(model)+'"' not in expr:continue
       for area in cellrange.sqref.ranges:
        if area.min_col>=first and area.max_col<=first+5:
         active.update(range(area.min_col-first,area.max_col-first+1))
     self.assertEqual(active,REQUIRED[model],(lang,sn,selector,model,active))
   # Original mapped values and all unrelated fields are retained in the new templates.
   self.assertIsNone(w[sheet('Activities')]['N3'].value)
 def test_reference_formulas_recalculate_all_eight_models(self):
  means=[5,14/3,26/6,5,5,5,5,5]
  for lang in ['en','pt_BR']:
   w=openpyxl.load_workbook(ROOT/f'tests/fixtures/all_distributions_{lang}.xlsx',data_only=True)
   title='Case_Assumptions' if lang=='en' else PT['Case_Assumptions']
   for i,expected in enumerate(means,3):self.assertAlmostEqual(w[title][f'C{i}'].value,expected,places=10)
   data=read_v1_workbook(ROOT/f'tests/fixtures/all_distributions_{lang}.xlsx');self.assertEqual(validate_all(data),[])
 def test_full_model_bilingual_portrait_treatment_and_export(self):
  from localization.exports import results_zip
  from core.risk_analysis import activity_diagnostics
  inputs=[read_v1_workbook(ROOT/f'tests/fixtures/all_distributions_{lang}.xlsx') for lang in ['en','pt_BR']]
  for data in inputs:self.assertEqual(validate_all(data),[])
  objects=[to_model_objects(data) for data in inputs]
  results=[simulate(*o,iterations=100,seed=42) for o in objects]
  for key in results[0]:pd.testing.assert_frame_equal(results[0][key],results[1][key],check_exact=True)
  a,r,m=objects[0];result=results[0];ranking=risk_importance(result['project'],result['risks'])
  portrait,scenarios=build_risk_portrait(a,r,m,ranking,iterations=100,seed=42,baseline_result=result)
  self.assertIs(scenarios['ST'],result)
  self.assertTrue(np.isfinite(portrait['Mean_Duration']).all())
  ids=list(dict.fromkeys(x['risk_id'] for x in m if x['distribution'] in NEW))
  tr,tm=apply_treatments(r,m,[{'risk_id':rid,'new_probability':1,'duration_multiplier':.5,'cost_multiplier':.75} for rid in ids])
  after=simulate(a,tr,tm,iterations=100,seed=42);self.assertTrue(np.isfinite(after['project']['Cost']).all())
  set_language('pt_BR')
  archive=results_zip(result['project'],result['activities'],result['risks'],ranking,activity_diagnostics(result['activities'],result['project']),portrait=portrait)
  with zipfile.ZipFile(io.BytesIO(archive)) as z:self.assertIn('pt_BR/risk_portrait_summary.csv',z.namelist())

if __name__=='__main__':unittest.main(verbosity=2)
