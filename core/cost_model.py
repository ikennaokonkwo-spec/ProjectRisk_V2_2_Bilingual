"""Cost input reconciliation and reporting for fixed-price and time-based work."""
import math
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
from .distributions import expected_value

def effective_cost_rate(activity):
    if activity.get('cost_association') == 'Fixed only':
        return 0.0
    return float(activity.get('cost_rate', 0))

def cost_input_summary(activities):
    rows=[]
    for a in activities:
        duration=expected_value(a['duration_model'],a['duration_params'])
        fixed=expected_value(a.get('cost_model','Fixed'),a.get('cost_params',{'fixed':0}))
        rate=effective_cost_rate(a)
        rows.append({'Activity_ID':a['id'],'Activity_Name':a.get('name',''),
                     'Cost_Association':a.get('cost_association') or ('Fixed only' if rate==0 else 'Fixed + time'),
                     'Reference_Duration':duration,'Reference_Fixed_Cost':fixed,'Cost_Rate':rate,
                     'Reference_Time_Cost':rate*duration,'Reference_Total_Cost':fixed+rate*duration})
    return pd.DataFrame(rows)

def validate_live_cost_links(data):
    """Block missing/stale caches by reconciling saved outputs to current inputs."""
    from .validation import ValidationIssue, _blank, _text
    from data_io.model_adapter import _params
    issues=[]
    if 'Case_Assumptions' not in data: return issues
    basis=data['Case_Assumptions']
    if 'Activity_ID' not in basis:
        return [ValidationIssue('Error','Cost','Case_Assumptions requires Activity_ID.')]
    basis=basis[basis['Activity_ID'].notna()].copy()
    basis['Activity_ID']=basis['Activity_ID'].astype(str).str.strip()
    duplicates=set(basis.loc[basis['Activity_ID'].duplicated(),'Activity_ID'])
    for aid in duplicates:
        issues.append(ValidationIssue('Error','Cost',f'{aid}: duplicate Case_Assumptions entry.'))
    lookup={row['Activity_ID']:row for _,row in basis.iterrows()}
    for _,row in data['Activities'].iterrows():
        aid=_text(row.get('Activity_ID'));association=_text(row.get('Cost_Association'))
        if not aid or not association or aid in duplicates: continue
        if aid not in lookup:
            issues.append(ValidationIssue('Error','Cost',f'{aid}: missing Case_Assumptions entry.'));continue
        try:
            b=lookup[aid];budget=float(b.get('Original_Base_Cost'));share=float(b.get('Time_Dependent_Share'))
            if not math.isfinite(budget) or budget<0 or not math.isfinite(share) or not 0<=share<=1:
                raise ValueError('budget must be finite/non-negative and time share between 0 and 1')
            model=_text(row.get('Duration_Model'))
            duration=float(expected_value(model,_params(row,'Duration',model)))
            if not math.isfinite(duration) or duration<0: raise ValueError('invalid reference duration')
            if association=='Fixed only' or share==0: rate=0.0
            else:
                if duration<=0: raise ValueError('positive time share requires positive reference duration')
                rate=float((Decimal(str(budget))*Decimal(str(share))/Decimal(str(duration))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
            fixed=float((Decimal(str(budget))-Decimal(str(rate))*Decimal(str(duration))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
            saved_fixed=float(row.get('Fixed_Cost'));saved_rate=float(row.get('Cost_Rate'))
            if not math.isfinite(saved_fixed) or not math.isfinite(saved_rate) or abs(saved_fixed-fixed)>.011 or abs(saved_rate-rate)>.011:
                issues.append(ValidationIssue('Error','Cost',f'{aid}: saved cost formulas do not match the current budget/share/duration/association. Recalculate and save the workbook in Excel.'))
        except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc:
            issues.append(ValidationIssue('Error','Cost',f'{aid}: cannot reconcile live cost inputs ({exc}). Recalculate and save the workbook.'))
    return issues
