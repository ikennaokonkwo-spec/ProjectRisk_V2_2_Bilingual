
from __future__ import annotations
import numpy as np
import pandas as pd

def project_statistics(project_df,target_duration=None,target_cost=None):
    d=project_df["Duration"].astype(float); c=project_df["Cost"].astype(float)
    out={}
    for label,s in [("Duration",d),("Cost",c)]:
        out[f"Mean_{label}"]=s.mean(); out[f"SD_{label}"]=s.std(ddof=1)
        for q in [10,50,80,90,95]: out[f"P{q}_{label}"]=s.quantile(q/100)
        out[f"Min_{label}"]=s.min(); out[f"Max_{label}"]=s.max()
    out["P_Meet_Duration_Target"]=None if target_duration is None else float((d<=float(target_duration)).mean())
    out["P_Meet_Cost_Target"]=None if target_cost is None else float((c<=float(target_cost)).mean())
    return out

def activity_diagnostics(activity_df,project_df):
    merged=activity_df.merge(project_df[["Iteration","Duration"]],on="Iteration")
    rows=[]
    for aid,g in merged.groupby("Activity_ID"):
        x=g["Final_Duration"].astype(float)
        y=g["Duration"].astype(float)
        # Spearman without scipy: Pearson correlation of ranks.
        cruciality=x.rank(method="average").corr(y.rank(method="average")) if x.nunique()>1 and y.nunique()>1 else 0.0
        rows.append({"Activity_ID":aid,"Criticality_Index":float(g["Critical"].mean()),
                     "Cruciality_Spearman":0.0 if pd.isna(cruciality) else float(cruciality)})
    return pd.DataFrame(rows).sort_values(["Criticality_Index","Cruciality_Spearman"],ascending=False).reset_index(drop=True)

def activity_criticality(activity_df):
    return activity_df.groupby("Activity_ID",as_index=False)["Critical"].mean().rename(columns={"Critical":"Criticality_Index"}).sort_values("Criticality_Index",ascending=False)

def activity_schedule_summary(activity_df):
    rows=[]
    for aid,g in activity_df.groupby("Activity_ID"):
        row={"Activity_ID":aid}
        for field in ["Final_Duration","ES","EF"]:
            s=g[field].astype(float)
            row.update({f"{field}_P10":s.quantile(.10),f"{field}_P50":s.quantile(.50),f"{field}_P90":s.quantile(.90)})
        rows.append(row)
    return pd.DataFrame(rows)

def risk_importance(project_df,risk_df):
    merged=risk_df.merge(project_df[["Iteration","Duration","Cost"]],on="Iteration",how="left")
    rows=[]
    for rid,g in merged.groupby("Risk_ID"):
        x=g["Occurred"].astype(int); yd=g["Duration"].astype(float); yc=g["Cost"].astype(float)
        dc=x.corr(yd) if x.nunique()>1 and yd.nunique()>1 else 0.0
        cc=x.corr(yc) if x.nunique()>1 and yc.nunique()>1 else 0.0
        rows.append({"Risk_ID":rid,"Occurrence_Rate":float(x.mean()),"Mean_Probability":float(g["Probability_Used"].mean()),
            "Duration_Association":0.0 if pd.isna(dc) else float(dc),"Abs_Duration_Association":abs(0.0 if pd.isna(dc) else float(dc)),
            "Cost_Association":0.0 if pd.isna(cc) else float(cc),"Abs_Cost_Association":abs(0.0 if pd.isna(cc) else float(cc)),
            "Mean_Realized_Duration_Impact":float(g["Duration_Impact"].mean()),"Mean_Realized_Cost_Impact":float(g["Cost_Impact"].mean())})
    return pd.DataFrame(rows).sort_values(["Abs_Duration_Association","Abs_Cost_Association"],ascending=False).reset_index(drop=True)


def critical_path_frequency(project_df):
    counts={}
    for cell in project_df.get("Critical_Paths",[]):
        for path in str(cell).split(" || "):
            path=path.strip()
            if path: counts[path]=counts.get(path,0)+1
    n=len(project_df)
    return pd.DataFrame([{"Critical_Path":k,"Count":v,"Frequency":v/n if n else 0.0} for k,v in counts.items()]).sort_values("Frequency",ascending=False).reset_index(drop=True)
