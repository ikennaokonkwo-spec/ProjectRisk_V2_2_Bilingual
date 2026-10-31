
from __future__ import annotations
import numpy as np
import math

NEW_DISTRIBUTIONS = {"Exponential", "Lognormal", "Gamma"}

def positive_moments(model: str, params: dict) -> dict:
    """Arithmetic input moments; derived sampler parameters are computed once at import."""
    mean = float(params["mean"])
    if not math.isfinite(mean) or mean <= 0:
        raise ValueError("Mean must be finite and greater than zero.")
    out = {"mean": mean}
    if model == "Exponential":
        return out
    sd = float(params["sd"])
    if not math.isfinite(sd) or sd <= 0:
        raise ValueError("Standard deviation must be finite and greater than zero.")
    out["sd"] = sd
    if model == "Lognormal":
        log_variance = float(np.logaddexp(0.0, 2 * (math.log(sd) - math.log(mean))))
        out.update(log_mean=math.log(mean)-log_variance/2, log_sd=math.sqrt(log_variance))
        if out["log_sd"] == 0:
            raise ValueError("Parameters exceed the supported numerical range.")
    elif model == "Gamma":
        try:
            shape = (mean/sd)**2
            scale = sd*(sd/mean)
        except OverflowError as exc:
            raise ValueError("Parameters exceed the supported numerical range.") from exc
        if not all(math.isfinite(x) and x > 0 for x in (shape,scale)):
            raise ValueError("Parameters exceed the supported numerical range.")
        out.update(shape=shape, scale=scale)
    else:
        raise ValueError(f"Unknown distribution: {model}")
    return out

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
    if model == "Exponential":
        mean = float(params["mean"])
        if not math.isfinite(mean) or mean <= 0: raise ValueError("Mean must be finite and greater than zero.")
        return float(rng.exponential(mean))
    if model == "Lognormal":
        p = params if "log_mean" in params and "log_sd" in params else positive_moments(model, params)
        return float(rng.lognormal(p["log_mean"], p["log_sd"]))
    if model == "Gamma":
        p = params if "shape" in params and "scale" in params else positive_moments(model, params)
        return float(rng.gamma(p["shape"], p["scale"]))
    raise ValueError(f"Unknown distribution: {model}")

def expected_value(model: str, params: dict) -> float:
    if model=="Fixed": return float(params["fixed"])
    if model=="Triangular": return sum(float(params[k]) for k in ("min","most_likely","max"))/3
    if model=="Uniform": return (float(params["min"])+float(params["max"]))/2
    if model=="Normal": return max(0.0,float(params["mean"]))
    if model=="Beta-PERT": return (float(params["min"])+4*float(params["most_likely"])+float(params["max"]))/6
    if model in NEW_DISTRIBUTIONS: return positive_moments(model, params)["mean"]
    raise ValueError(f"Unknown distribution: {model}")
