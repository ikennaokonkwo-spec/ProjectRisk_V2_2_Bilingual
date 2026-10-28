
from __future__ import annotations
import numpy as np
import pandas as pd
from .simulation import simulate
from .risk_analysis import project_statistics

def build_risk_portrait(activities, risks, mappings, ranking, iterations=5000, seed=42,
                        target_duration=None, target_cost=None, baseline_result=None):
    active_ids = [r["id"] for r in risks if r.get("active", True)]
    ordered = [rid for rid in ranking["Risk_ID"].tolist() if rid in set(active_ids)]
    scenarios = [("S0", "Baseline", set())]

    # Add cumulative ranked risks, reserving the final all-risk state for ST.
    cumulative = []
    for k, rid in enumerate(ordered[:-1], start=1):
        cumulative.append(rid)
        scenarios.append((f"S{k}", " + ".join(cumulative), set(cumulative)))
    scenarios.append(("ST", "Total Project Risk: " + " + ".join(ordered), set(ordered)))

    scenario_results, rows = {}, []
    previous = None
    for sid, label, active in scenarios:
        result = baseline_result if sid == "ST" and baseline_result is not None else simulate(activities, risks, mappings, iterations=iterations, seed=seed, active_risks=active)
        stats = project_statistics(result["project"], target_duration, target_cost)
        rows.append({
            "Scenario": sid, "Active_Risks": label, **stats,
            "Delta_Mean_Duration": 0.0 if previous is None else stats["Mean_Duration"]-previous["Mean_Duration"],
            "Delta_P50_Duration": 0.0 if previous is None else stats["P50_Duration"]-previous["P50_Duration"],
            "Delta_P90_Duration": 0.0 if previous is None else stats["P90_Duration"]-previous["P90_Duration"],
            "Delta_Mean_Cost": 0.0 if previous is None else stats["Mean_Cost"]-previous["Mean_Cost"],
            "Delta_P90_Cost": 0.0 if previous is None else stats["P90_Cost"]-previous["P90_Cost"],
        })
        scenario_results[sid] = result
        previous = stats
    return pd.DataFrame(rows), scenario_results

def empirical_cdf(values):
    x = np.sort(np.asarray(values, dtype=float))
    y = np.arange(1, len(x)+1) / len(x)
    return x, y
