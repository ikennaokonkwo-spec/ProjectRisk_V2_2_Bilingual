
from __future__ import annotations
import math

def _blank(v):
    return v is None or (isinstance(v,float) and math.isnan(v)) or str(v).strip()==""
def _num(v,default=None): return default if _blank(v) else float(v)
def _bool(v,default=True):
    if _blank(v): return default
    if isinstance(v,bool): return v
    return str(v).strip().lower() in {"true","1","yes","y","sim"}

def _params(row,prefix,model):
    if model=="Fixed": return {"fixed":_num(row.get(f"{prefix}_Fixed"),0.0)}
    if model in {"Triangular","Beta-PERT"}:
        return {"min":_num(row.get(f"{prefix}_Min")),"most_likely":_num(row.get(f"{prefix}_MostLikely")),"max":_num(row.get(f"{prefix}_Max"))}
    if model=="Uniform": return {"min":_num(row.get(f"{prefix}_Min")),"max":_num(row.get(f"{prefix}_Max"))}
    if model=="Normal": return {"mean":_num(row.get(f"{prefix}_Mean")),"sd":_num(row.get(f"{prefix}_SD"))}
    if model in {"Exponential", "Lognormal", "Gamma"}:
        from core.distributions import positive_moments
        params={"mean":_num(row.get(f"{prefix}_Mean"))}
        if model!="Exponential": params["sd"]=_num(row.get(f"{prefix}_SD"))
        return positive_moments(model,params)
    raise ValueError(model)

def to_model_objects(data):
    activities=[]
    for _,row in data["Activities"].iterrows():
        if _blank(row.get("Activity_ID")): continue
        preds=[] if _blank(row.get("Predecessors")) else [x.strip() for x in str(row["Predecessors"]).split(",") if x.strip()]
        dm=str(row["Duration_Model"]).strip()
        cm="Fixed" if _blank(row.get("Cost_Model")) else str(row["Cost_Model"]).strip()
        cp={"fixed":_num(row.get("Fixed_Cost"),_num(row.get("Base_Cost"),0.0))} if cm=="Fixed" and _blank(row.get("Cost_Fixed")) else _params(row,"Cost",cm)
        activities.append({"id":str(row["Activity_ID"]).strip(),"name":str(row.get("Activity_Name","")).strip(),
            "predecessors":preds,"duration_model":dm,"duration_params":_params(row,"Duration",dm),
            "cost_model":cm,"cost_params":cp,"cost_rate":_num(row.get("Cost_Rate"),0.0),
            "cost_association":"" if _blank(row.get("Cost_Association")) else str(row["Cost_Association"]).strip()})
    risks=[]
    for _,row in data["Risk_Register"].iterrows():
        if _blank(row.get("Risk_ID")): continue
        pm="Fixed" if _blank(row.get("Probability_Model")) else str(row.get("Probability_Model")).strip()
        pp={"min":_num(row.get("Probability_Min")),"max":_num(row.get("Probability_Max"))} if pm=="Uniform" else {"fixed":_num(row.get("Probability"),0.0)}
        risks.append({"id":str(row["Risk_ID"]).strip(),"name":str(row.get("Risk_Name","")).strip(),
            "type":str(row["Risk_Type"]).strip(),"probability_model":pm,"probability_params":pp,
            "probability":_num(row.get("Probability"),0.0),"scope":str(row["Scope"]).strip(),
            "impact_type":str(row["Impact_Type"]).strip(),"active":_bool(row.get("Active"),True)})
    mappings=[]
    for _,row in data["Risk_Activity_Map"].iterrows():
        if _blank(row.get("Risk_ID")) and _blank(row.get("Activity_ID")): continue
        model=str(row["Distribution"]).strip()
        mappings.append({"risk_id":str(row["Risk_ID"]).strip(),"activity_id":str(row["Activity_ID"]).strip(),
            "impact_type":str(row["Impact_Type"]).strip(),
            "impact_mode":"Absolute" if _blank(row.get("Impact_Mode")) else str(row.get("Impact_Mode")).strip(),
            "distribution":model,"params":_params(row,"Impact",model)})
    return activities,risks,mappings
