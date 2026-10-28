
from __future__ import annotations
import numpy as np

def sample_distribution(model: str, params: dict, rng: np.random.Generator) -> float:
    if model == "Fixed": return float(params["fixed"])
    if model == "Triangular": return float(rng.triangular(params["min"], params["most_likely"], params["max"]))
    if model == "Uniform": return float(rng.uniform(params["min"], params["max"]))
    if model == "Normal": return max(0.0, float(rng.normal(params["mean"], params["sd"])))
    if model == "Beta-PERT":
        a,m,b=map(float,[params["min"],params["most_likely"],params["max"]])
        if b==a: return a
        alpha=1+4*(m-a)/(b-a); beta=1+4*(b-m)/(b-a)
        return float(a+rng.beta(alpha,beta)*(b-a))
    raise ValueError(f"Unknown distribution: {model}")

def expected_value(model: str, params: dict) -> float:
    if model=="Fixed": return float(params["fixed"])
    if model=="Triangular": return sum(float(params[k]) for k in ("min","most_likely","max"))/3
    if model=="Uniform": return (float(params["min"])+float(params["max"]))/2
    if model=="Normal": return max(0.0,float(params["mean"]))
    if model=="Beta-PERT": return (float(params["min"])+4*float(params["most_likely"])+float(params["max"]))/6
    raise ValueError(f"Unknown distribution: {model}")
