
from data_io.input_reader import read_v1_workbook, project_settings
from data_io.model_adapter import to_model_objects
from core.validation import validate_all
from core.simulation import simulate
from core.risk_analysis import risk_importance, activity_diagnostics, activity_schedule_summary
from core.risk_portrait import build_risk_portrait
from core.reference_analysis import reference_cpm

def run():
    data=read_v1_workbook("project_risk_template_v2_2.xlsx")
    errors=[x for x in validate_all(data) if x.severity=="Error"]
    assert not errors, "\n".join(x.message for x in errors)
    settings=project_settings(data["Project"])
    a,r,m=to_model_objects(data)
    ref,cpm=reference_cpm(a)
    assert {"ES","EF","LS","LF","Slack","Critical"}.issubset(ref.columns)
    out=simulate(a,r,m,100,int(settings.get("Random_Seed",42)))
    assert len(out["project"])==100
    assert out["project"]["Cost"].nunique()>1  # V2 example includes intrinsic cost uncertainty.
    ranking=risk_importance(out["project"],out["risks"])
    diag=activity_diagnostics(out["activities"],out["project"])
    sched=activity_schedule_summary(out["activities"])
    assert {"Criticality_Index","Cruciality_Spearman"}.issubset(diag.columns)
    assert {"ES_P10","ES_P50","ES_P90","EF_P10","EF_P50","EF_P90"}.issubset(sched.columns)
    portrait,scenarios=build_risk_portrait(a,r,m,ranking,100,int(settings.get("Random_Seed",42)))
    assert portrait.iloc[0]["Scenario"]=="S0"
    assert portrait.iloc[-1]["Scenario"]=="ST"
    assert set(scenarios["ST"]["risks"].query("Active_in_Scenario")["Risk_ID"].unique())=={x["id"] for x in r if x.get("active",True)}
    print("test_integration: PASS")
if __name__=="__main__": run()
