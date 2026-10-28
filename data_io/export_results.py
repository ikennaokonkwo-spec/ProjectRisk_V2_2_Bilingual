
from __future__ import annotations
from io import BytesIO
import zipfile

def results_zip(project,activities,risks,ranking,activity_diagnostics,reference_cpm=None,
                schedule_summary=None,critical_paths=None,portrait=None,treatment=None,register=None,treatment_assumptions=None,cost_inputs=None):
    payload={"project_iterations.csv":project,"activity_iterations.csv":activities,"risk_iterations.csv":risks,
             "risk_importance.csv":ranking,"activity_diagnostics.csv":activity_diagnostics}
    if reference_cpm is not None: payload["reference_cpm.csv"]=reference_cpm
    if schedule_summary is not None: payload["risk_adjusted_schedule.csv"]=schedule_summary
    if critical_paths is not None: payload["critical_path_frequency.csv"]=critical_paths
    if portrait is not None: payload["risk_portrait_summary.csv"]=portrait
    if treatment is not None: payload["treatment_comparison.csv"]=treatment
    if register is not None: payload["risk_register_review_v2_2.csv"]=register
    if treatment_assumptions is not None: payload["treatment_assumptions.csv"]=treatment_assumptions
    if cost_inputs is not None: payload["activity_cost_inputs.csv"]=cost_inputs
    b=BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
        for name,df in payload.items(): z.writestr(name,df.to_csv(index=False))
    return b.getvalue()
