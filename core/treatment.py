
from __future__ import annotations
from copy import deepcopy
import math

def apply_treatment(risks,mappings,risk_id,new_probability=None,impact_multiplier=1.0):
    return apply_treatments(risks,mappings,[{"risk_id":risk_id,"new_probability":new_probability,"impact_multiplier":impact_multiplier}])

def apply_treatments(risks,mappings,treatments):
    rr=deepcopy(risks); mm=deepcopy(mappings)
    rlookup={r["id"]:r for r in rr}
    for spec in treatments:
        rid=spec["risk_id"]
        if rid not in rlookup: raise ValueError(f"Unknown risk: {rid}")
        mult=float(spec.get("impact_multiplier",1.0))
        if not math.isfinite(mult) or mult<0: raise ValueError("Impact multiplier cannot be negative.")
        p=spec.get("new_probability")
        if p is not None:
            p=float(p)
            if not 0<=p<=1: raise ValueError("Treated probability must be between 0 and 1.")
            rlookup[rid]["probability_model"]="Fixed"
            rlookup[rid]["probability_params"]={"fixed":p}
            rlookup[rid]["probability"]=p
        dm=float(spec.get("duration_multiplier",mult))
        cm=float(spec.get("cost_multiplier",mult))
        if any(not math.isfinite(v) or v<0 for v in (dm,cm)):
            raise ValueError("Impact multipliers must be finite and non-negative.")
        for m in mm:
            if m["risk_id"]!=rid: continue
            # Keep distribution draws stable; apply separate dimensional scaling.
            m["duration_multiplier"]=m.get("duration_multiplier",1.0)*dm
            m["cost_multiplier"]=m.get("cost_multiplier",1.0)*cm
    return rr,mm
