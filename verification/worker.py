"""Execute one isolated engine; called by verify_preservation.py."""
import sys,pickle
from pathlib import Path
module_root,workbook,iterations,seed,output=sys.argv[1:]
sys.path.insert(0,module_root)
from data_io.input_reader import read_v1_workbook,project_settings
from data_io.model_adapter import to_model_objects
from core.validation import validate_all
from core.simulation import simulate
from core.risk_analysis import project_statistics,risk_importance,activity_diagnostics,activity_schedule_summary,critical_path_frequency
from core.reference_analysis import reference_cpm
from core.cost_model import cost_input_summary
from core.register import register_view,treatment_specs
from core.risk_portrait import build_risk_portrait
from core.treatment import apply_treatments
n=int(iterations);seed=int(seed)
data=read_v1_workbook(workbook);issues=validate_all(data)
assert not issues,issues
objects=to_model_objects(data);acts,risks,maps=objects
settings=project_settings(data['Project']);td=settings.get('Target_Duration');tc=settings.get('Target_Cost')
main=simulate(*objects,iterations=n,seed=seed)
ranking=risk_importance(main['project'],main['risks'])
reference,cpm=reference_cpm(acts)
small=simulate(*objects,iterations=100,seed=seed)
portrait,scenarios=build_risk_portrait(*objects,ranking,iterations=100,seed=seed,target_duration=td,target_cost=tc,baseline_result=small)
treatments={}
specs=treatment_specs(data)
for name,selected in [('single',specs[:1]),('multiple',specs[:3])]:
    tr,tm=apply_treatments(risks,maps,selected)
    treatments[name]=simulate(acts,tr,tm,iterations=100,seed=seed)
result={'objects':objects,'issues':issues,'main':main,'statistics':project_statistics(main['project'],td,tc),'ranking':ranking,'activity_diagnostics':activity_diagnostics(main['activities'],main['project']),'schedule':activity_schedule_summary(main['activities']),'path_frequency':critical_path_frequency(main['project']),'reference':reference,'cpm':cpm,'cost_inputs':cost_input_summary(acts),'register':register_view(data,ranking),'portrait':portrait,'scenarios':scenarios,'treatments':treatments}
with open(output,'wb') as f:pickle.dump(result,f)
print(f'{Path(workbook).name}: {n} iterations + complete 100-iteration portrait + single/multiple treatments',flush=True)
