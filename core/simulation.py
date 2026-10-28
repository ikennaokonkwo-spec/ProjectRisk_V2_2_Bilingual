
from __future__ import annotations
import hashlib
import numpy as np
import pandas as pd
from .distributions import sample_distribution
from .network import calculate_cpm
from .cost_model import effective_cost_rate

def _stable_rng(seed,iteration,namespace,entity):
    digest=hashlib.sha256(f"{seed}|{iteration}|{namespace}|{entity}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:8],"little"))

def _risk_probability(r,i,seed):
    model=r.get("probability_model","Fixed")
    if model=="Uniform":
        rng=_stable_rng(seed,i,"risk_probability",r["id"])
        return float(rng.uniform(r["probability_params"]["min"],r["probability_params"]["max"]))
    return float(r.get("probability_params",{}).get("fixed",r.get("probability",0)))

def simulate(activities,risks,mappings,iterations=5000,seed=42,active_risks=None):
    if active_risks is None:
        active_risks={r["id"] for r in risks if r.get("active",True)}
    maps={}
    for m in mappings: maps.setdefault(m["risk_id"],[]).append(m)
    project_rows=[]; activity_rows=[]; risk_rows=[]

    for i in range(1,iterations+1):
        base_d={}; base_c={}
        for a in activities:
            base_d[a["id"]]=sample_distribution(a["duration_model"],a["duration_params"],_stable_rng(seed,i,"activity_duration",a["id"]))
            base_c[a["id"]]=sample_distribution(a.get("cost_model","Fixed"),a.get("cost_params",{"fixed":0}),_stable_rng(seed,i,"activity_cost",a["id"]))
        final_d=dict(base_d); final_c=dict(base_c)
        direct_impacts={aid:0.0 for aid in base_c}
        states={}; realized={r["id"]:{"duration":0.0,"cost":0.0} for r in risks}

        for r in risks:
            rid=r["id"]; p=_risk_probability(r,i,seed)
            underlying=_stable_rng(seed,i,"risk_occurrence",rid).random()<p
            occurred=bool(rid in active_risks and underlying); states[rid]=occurred
            if not occurred: continue
            sign=1.0 if r["type"]=="Threat" else -1.0
            for idx,m in enumerate(maps.get(rid,[])):
                aid=m["activity_id"]
                mag=sample_distribution(m["distribution"],m["params"],_stable_rng(seed,i,"risk_impact",f"{rid}|{aid}|{idx}"))
                mode=m.get("impact_mode","Absolute")
                duration_mult=m.get("duration_multiplier",1.0)
                cost_mult=m.get("cost_multiplier",1.0)
                if m["impact_type"] in {"Duration","Both"}:
                    raw=mag if mode=="Absolute" else base_d[aid]*mag
                    val=sign*raw*duration_mult; final_d[aid]=max(0.0,final_d[aid]+val); realized[rid]["duration"]+=val
                if m["impact_type"] in {"Cost","Both"}:
                    raw=mag if mode=="Absolute" else (base_c[aid]+next(effective_cost_rate(a) for a in activities if a["id"]==aid)*base_d[aid])*mag
                    val=sign*raw*cost_mult; direct_impacts[aid]+=val; realized[rid]["cost"]+=val

        # Time costs use each activity's final duration, not project elapsed time.
        direct_cost = direct_impacts
        time_cost = {a["id"]: effective_cost_rate(a)*final_d[a["id"]] for a in activities}
        for aid in final_c:
            final_c[aid] = max(0.0,base_c[aid]+time_cost[aid]+direct_cost[aid])
        cpm=calculate_cpm(activities,final_d)
        path_labels=[" → ".join(p) for p in cpm.get("critical_paths",[])]
        project_rows.append({"Iteration":i,"Duration":cpm["project_duration"],"Cost":float(sum(final_c.values())),
                             "Critical_Paths":" || ".join(path_labels)})
        critical=set(cpm["critical_activities"])
        for a in activities:
            aid=a["id"]
            activity_rows.append({"Iteration":i,"Activity_ID":aid,"Base_Duration":base_d[aid],"Final_Duration":final_d[aid],
                "Risk_Duration_Impact":final_d[aid]-base_d[aid],"Base_Cost":base_c[aid]+effective_cost_rate(a)*base_d[aid],"Final_Cost":final_c[aid],
                "Fixed_Cost":base_c[aid],"Time_Dependent_Cost":time_cost[aid],
                "Direct_Risk_Cost":direct_cost[aid],
                "Duration_Related_Cost_Change":effective_cost_rate(a)*(final_d[aid]-base_d[aid]),
                "ES":cpm["ES"][aid],"EF":cpm["EF"][aid],"LS":cpm["LS"][aid],"LF":cpm["LF"][aid],"Slack":cpm["Slack"][aid],
                "Critical":aid in critical})
        for r in risks:
            rid=r["id"]
            risk_rows.append({"Iteration":i,"Risk_ID":rid,"Active_in_Scenario":rid in active_risks,
                "Probability_Used":_risk_probability(r,i,seed),"Occurred":states[rid],
                "Duration_Impact":realized[rid]["duration"],"Cost_Impact":realized[rid]["cost"]})
    return {"project":pd.DataFrame(project_rows),"activities":pd.DataFrame(activity_rows),"risks":pd.DataFrame(risk_rows)}
