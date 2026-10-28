
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import math
import pandas as pd
import networkx as nx

DISTRIBUTIONS = {"Fixed", "Beta-PERT", "Triangular", "Uniform", "Normal"}
RISK_TYPES = {"Threat", "Opportunity"}
SCOPES = {"Local", "Global"}
IMPACT_TYPES = {"Duration", "Cost", "Both"}

@dataclass
class ValidationIssue:
    severity: str
    area: str
    message: str

def _blank(v: Any) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == ""

def _text(v: Any) -> str:
    return "" if _blank(v) else str(v).strip()

def validate_project(df: pd.DataFrame) -> list[ValidationIssue]:
    issues = []
    settings = dict(zip(df["Field"], df["Value"]))
    if _blank(settings.get("Project_ID")):
        issues.append(ValidationIssue("Error", "Project", "Project_ID is required."))
    if _blank(settings.get("Project_Name")):
        issues.append(ValidationIssue("Error", "Project", "Project_Name is required."))
    try:
        n = int(settings.get("Simulation_Iterations"))
        if n <= 0:
            raise ValueError
    except Exception:
        issues.append(ValidationIssue("Error", "Project", "Simulation_Iterations must be an integer > 0."))
    if not _blank(settings.get("Random_Seed")):
        try:
            int(settings.get("Random_Seed"))
        except Exception:
            issues.append(ValidationIssue("Error", "Project", "Random_Seed must be an integer if supplied."))
    for field in ("Target_Duration", "Target_Cost"):
        if not _blank(settings.get(field)):
            try:
                if float(settings[field]) < 0:
                    raise ValueError
            except Exception:
                issues.append(ValidationIssue("Error", "Project", f"{field} must be non-negative if supplied."))
    return issues

def validate_activities(df: pd.DataFrame) -> list[ValidationIssue]:
    issues = []
    if df.empty:
        return [ValidationIssue("Error", "Activities", "No activities were supplied.")]
    ids = [_text(v) for v in df["Activity_ID"] if not _blank(v)]
    duplicates = pd.Series(ids)[pd.Series(ids).duplicated()].unique().tolist() if ids else []
    for x in duplicates:
        issues.append(ValidationIssue("Error", "Activities", f"Duplicate Activity_ID: {x}"))
    known = set(ids)
    g = nx.DiGraph()
    g.add_nodes_from(known)

    for _, row in df.iterrows():
        aid = _text(row.get("Activity_ID"))
        if not aid:
            continue
        model = _text(row.get("Duration_Model"))
        if model not in DISTRIBUTIONS:
            issues.append(ValidationIssue("Error", "Duration", f"{aid}: unknown Duration_Model '{model}'."))
            continue
        raw_preds = row.get("Predecessors", "")
        preds = [] if _blank(raw_preds) else [_text(x) for x in str(raw_preds).split(",") if _text(x)]
        if aid in preds:
            issues.append(ValidationIssue("Error", "Network", f"{aid} cannot be its own predecessor."))
        for p in preds:
            if p not in known:
                issues.append(ValidationIssue("Error", "Network", f"{aid} references unknown predecessor {p}."))
            else:
                g.add_edge(p, aid)

        vals = {k: row.get(k) for k in [
            "Duration_Fixed","Duration_Min","Duration_MostLikely","Duration_Max","Duration_Mean","Duration_SD"
        ]}
        try:
            if model == "Fixed":
                if _blank(vals["Duration_Fixed"]) or float(vals["Duration_Fixed"]) < 0:
                    raise ValueError
            elif model in {"Beta-PERT", "Triangular"}:
                if any(_blank(vals[k]) for k in ["Duration_Min","Duration_MostLikely","Duration_Max"]):
                    raise ValueError
                a, m, b = map(float, [vals["Duration_Min"], vals["Duration_MostLikely"], vals["Duration_Max"]])
                if not (0 <= a <= m <= b):
                    raise ValueError
            elif model == "Uniform":
                if _blank(vals["Duration_Min"]) or _blank(vals["Duration_Max"]):
                    raise ValueError
                if not (0 <= float(vals["Duration_Min"]) <= float(vals["Duration_Max"])):
                    raise ValueError
            elif model == "Normal":
                if _blank(vals["Duration_Mean"]) or _blank(vals["Duration_SD"]):
                    raise ValueError
                if float(vals["Duration_Mean"]) < 0 or float(vals["Duration_SD"]) <= 0:
                    raise ValueError
        except Exception:
            issues.append(ValidationIssue("Error", "Duration", f"{aid}: invalid parameters for {model}."))
        if not _blank(row.get("Base_Cost")):
            try:
                if float(row.get("Base_Cost")) < 0:
                    raise ValueError
            except Exception:
                issues.append(ValidationIssue("Error", "Cost", f"{aid}: Base_Cost must be non-negative."))

    if known and not nx.is_directed_acyclic_graph(g):
        issues.append(ValidationIssue("Error", "Network", "Circular precedence relationship detected."))
    return issues

def validate_risks(df: pd.DataFrame) -> list[ValidationIssue]:
    issues = []
    ids = [_text(v) for v in df.get("Risk_ID", []) if not _blank(v)]
    if ids:
        dup = pd.Series(ids)[pd.Series(ids).duplicated()].unique().tolist()
        for x in dup:
            issues.append(ValidationIssue("Error", "Risk", f"Duplicate Risk_ID: {x}"))
    for _, row in df.iterrows():
        rid = _text(row.get("Risk_ID"))
        if not rid:
            continue
        try:
            p = float(row.get("Probability")) if not _blank(row.get("Probability")) else (0.0 if _text(row.get("Active")).lower() in {"false","0","no","n"} else float("nan"))
            if not math.isfinite(p) or not 0 <= p <= 1:
                raise ValueError
        except Exception:
            issues.append(ValidationIssue("Error", "Risk", f"{rid}: Probability must be between 0 and 1."))
        if _text(row.get("Risk_Type")) not in RISK_TYPES:
            issues.append(ValidationIssue("Error", "Risk", f"{rid}: Risk_Type must be Threat or Opportunity."))
        if _text(row.get("Scope")) not in SCOPES:
            issues.append(ValidationIssue("Error", "Risk", f"{rid}: Scope must be Local or Global."))
        if _text(row.get("Impact_Type")) not in IMPACT_TYPES:
            issues.append(ValidationIssue("Error", "Risk", f"{rid}: Impact_Type must be Duration, Cost or Both."))
    return issues

def validate_mapping(mapping: pd.DataFrame, activities: pd.DataFrame, risks: pd.DataFrame) -> list[ValidationIssue]:
    issues = []
    activity_ids = {_text(x) for x in activities["Activity_ID"] if not _blank(x)}
    risk_ids = {_text(x) for x in risks["Risk_ID"] if not _blank(x)}
    mapped_risks = set()

    for _, row in mapping.iterrows():
        rid, aid = _text(row.get("Risk_ID")), _text(row.get("Activity_ID"))
        if not rid and not aid:
            continue
        mapped_risks.add(rid)
        if rid not in risk_ids:
            issues.append(ValidationIssue("Error", "Mapping", f"Mapping references unknown risk {rid}."))
        if aid not in activity_ids:
            issues.append(ValidationIssue("Error", "Mapping", f"{rid or 'Risk'} maps to unknown activity {aid}."))
        if _text(row.get("Impact_Type")) not in IMPACT_TYPES:
            issues.append(ValidationIssue("Error", "Mapping", f"{rid}/{aid}: invalid Impact_Type."))
        dist = _text(row.get("Distribution"))
        if dist not in DISTRIBUTIONS:
            issues.append(ValidationIssue("Error", "Mapping", f"{rid}/{aid}: unknown Distribution '{dist}'."))
            continue
        fixed, mn, ml, mx, mean, sd = [row.get(k) for k in [
            "Impact_Fixed","Impact_Min","Impact_MostLikely","Impact_Max","Impact_Mean","Impact_SD"
        ]]
        try:
            if dist == "Fixed":
                if _blank(fixed) or float(fixed) < 0: raise ValueError
            elif dist in {"Beta-PERT","Triangular"}:
                if any(_blank(x) for x in [mn, ml, mx]): raise ValueError
                if not (0 <= float(mn) <= float(ml) <= float(mx)): raise ValueError
            elif dist == "Uniform":
                if _blank(mn) or _blank(mx) or not (0 <= float(mn) <= float(mx)): raise ValueError
            elif dist == "Normal":
                if _blank(mean) or _blank(sd) or float(mean) < 0 or float(sd) <= 0: raise ValueError
        except Exception:
            issues.append(ValidationIssue("Error", "Mapping", f"{rid}/{aid}: invalid parameters for {dist}."))

    for _, row in risks.iterrows():
        rid = _text(row.get("Risk_ID"))
        active = str(row.get("Active", True)).strip().lower() not in {"false","0","no","n"}
        if rid and active and rid not in mapped_risks:
            issues.append(ValidationIssue("Warning", "Mapping", f"{rid} is active but has no risk–activity mapping; it will have no modeled project consequence."))
    return issues

def _validate_v2_extensions(data):
    issues=[]
    activities=data["Activities"]; risks=data["Risk_Register"]; mapping=data["Risk_Activity_Map"]
    for _,row in activities.iterrows():
        aid=_text(row.get("Activity_ID"))
        if not aid: continue
        association=_text(row.get("Cost_Association"))
        if association:
            if association not in {"Fixed only","Fixed + time"}:
                issues.append(ValidationIssue("Error","Cost",f"{aid}: invalid Cost_Association."))
            if any(_blank(row.get(field)) for field in ("Fixed_Cost","Cost_Rate")):
                issues.append(ValidationIssue("Error","Cost",f"{aid}: linked costs have no saved result; recalculate and save the workbook in Excel before uploading."))
            if association=="Fixed only" and not _blank(row.get("Cost_Rate")):
                try:
                    if float(row['Cost_Rate'])!=0:
                        issues.append(ValidationIssue("Error","Cost",f"{aid}: Fixed only requires Cost_Rate=0; recalculate and save the workbook."))
                except (ValueError,TypeError): pass
        for field in ("Fixed_Cost", "Cost_Rate"):
            if not _blank(row.get(field)):
                try:
                    value=float(row[field])
                    if not math.isfinite(value) or value<0: raise ValueError
                except (TypeError,ValueError):
                    issues.append(ValidationIssue("Error","Cost",f"{aid}: {field} must be finite and non-negative."))
        cm=_text(row.get("Cost_Model")) or "Fixed"
        if cm not in DISTRIBUTIONS:
            issues.append(ValidationIssue("Error","Cost",f"{aid}: unknown Cost_Model '{cm}'."))
        try:
            if cm=="Fixed":
                v=row.get("Cost_Fixed")
                if _blank(v): v=row.get("Fixed_Cost")
                if _blank(v): v=row.get("Base_Cost")
                if not _blank(v) and float(v)<0: raise ValueError
            elif cm in {"Beta-PERT","Triangular"}:
                a,m,b=map(float,[row.get("Cost_Min"),row.get("Cost_MostLikely"),row.get("Cost_Max")])
                if not (0<=a<=m<=b): raise ValueError
            elif cm=="Uniform":
                a,b=map(float,[row.get("Cost_Min"),row.get("Cost_Max")])
                if not (0<=a<=b): raise ValueError
            elif cm=="Normal":
                if float(row.get("Cost_Mean"))<0 or float(row.get("Cost_SD"))<=0: raise ValueError
        except Exception:
            issues.append(ValidationIssue("Error","Cost",f"{aid}: invalid parameters for Cost_Model {cm}."))
    for _,row in risks.iterrows():
        rid=_text(row.get("Risk_ID"))
        if not rid: continue
        pm=_text(row.get("Probability_Model")) or "Fixed"
        if pm not in {"Fixed","Uniform"}:
            issues.append(ValidationIssue("Error","Risk",f"{rid}: Probability_Model must be Fixed or Uniform."))
        if pm=="Uniform":
            try:
                a,b=map(float,[row.get("Probability_Min"),row.get("Probability_Max")])
                if not (0<=a<=b<=1): raise ValueError
            except Exception:
                issues.append(ValidationIssue("Error","Risk",f"{rid}: probability range must satisfy 0 ≤ min ≤ max ≤ 1."))
    for _,row in mapping.iterrows():
        rid,aid=_text(row.get("Risk_ID")),_text(row.get("Activity_ID"))
        if not rid and not aid: continue
        mode=_text(row.get("Impact_Mode")) or "Absolute"
        if mode not in {"Absolute","Relative"}:
            issues.append(ValidationIssue("Error","Mapping",f"{rid}/{aid}: Impact_Mode must be Absolute or Relative."))
        if mode=="Relative":
            issues.append(ValidationIssue("Info","Mapping",f"{rid}/{aid}: Relative impacts use decimal rates (0.10 = 10%)."))
        if mode=="Absolute" and _text(row.get("Impact_Type"))=="Both":
            issues.append(ValidationIssue("Warning","Mapping",f"{rid}/{aid}: Absolute 'Both' uses one numeric consequence for duration and cost; use separate Duration and Cost rows when units/magnitudes differ."))
    return issues

def validate_all(data: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues = []
    issues += validate_project(data["Project"])
    issues += validate_activities(data["Activities"])
    issues += validate_risks(data["Risk_Register"])
    issues += validate_mapping(data["Risk_Activity_Map"], data["Activities"], data["Risk_Register"])
    issues += _validate_v2_extensions(data)
    from .register import validate_management
    issues += validate_management(data)
    from .cost_model import validate_live_cost_links
    issues += validate_live_cost_links(data)
    return issues
