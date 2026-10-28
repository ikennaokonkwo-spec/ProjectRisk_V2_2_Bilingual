"""Management documentation stays separate from simulation assumptions."""
import math
import pandas as pd
from data_io.model_adapter import _blank, _bool, _num

def treatment_specs(data):
    specs=[]
    for _, row in data.get('Risk_Treatments', pd.DataFrame()).iterrows():
        if _blank(row.get('Risk_ID')): continue
        specs.append({'risk_id': str(row['Risk_ID']).strip(),
                      'new_probability': _num(row.get('Treated_Probability')),
                      'duration_multiplier': _num(row.get('Duration_Impact_Multiplier'),1),
                      'cost_multiplier': _num(row.get('Cost_Impact_Multiplier'),1)})
    return specs

def register_view(data, ranking):
    register=data['Risk_Register'].copy()
    register['Risk_ID']=register['Risk_ID'].astype(str).str.strip()
    view=register.merge(ranking,on='Risk_ID',how='left')
    for dimension in ('Schedule','Cost'):
        field=f'Qualitative_{dimension}_Impact'
        if field in view:
            view[f'{dimension}_Screening_Score']=pd.to_numeric(view['Probability'],errors='coerce')*pd.to_numeric(view[field],errors='coerce')
    return view

def validate_management(data):
    from .validation import ValidationIssue
    issues=[]
    register=data['Risk_Register']
    ids=set(register['Risk_ID'].dropna().astype(str).str.strip())
    active={str(r['Risk_ID']).strip() for _,r in register.iterrows() if not _blank(r.get('Risk_ID')) and _bool(r.get('Active'))}
    for _,row in register.iterrows():
        rid=row.get('Risk_ID')
        if _blank(rid): continue
        for field in ('Qualitative_Schedule_Impact','Qualitative_Cost_Impact','Residual_Schedule_Impact','Residual_Cost_Impact'):
            if not _blank(row.get(field)):
                try:
                    v=float(row[field])
                    if not math.isfinite(v) or v not in (1,2,3,4,5): raise ValueError
                except (TypeError,ValueError):
                    issues.append(ValidationIssue('Error','Register',f'{rid}: {field} must be an integer from 1 to 5.'))
        if not _blank(row.get('Residual_Probability')):
            try:
                if not 0<=float(row['Residual_Probability'])<=1: raise ValueError
            except (TypeError,ValueError):
                issues.append(ValidationIssue('Error','Register',f'{rid}: Residual_Probability must be between 0 and 1.'))
        if row.get('Residual_Acceptance') == 'Accepted':
            required=['Residual_Probability','Residual_Schedule_Impact','Residual_Cost_Impact','Residual_Rationale']
            missing=[k for k in required if _blank(row.get(k))]
            if missing:
                issues.append(ValidationIssue('Warning','Register',f'{rid}: acceptance documentation incomplete: '+', '.join(missing)))
        action=str(row.get('Response_Action','')).strip()
        if action in {'Mitigate','Avoid','Transfer','Accept','Exploit','Enhance','Share'}:
            issues.append(ValidationIssue('Warning','Register',f'{rid}: replace Response_Action strategy label with a concrete action.'))
    seen=set()
    for spec in treatment_specs_safe(data,issues):
        rid=spec['risk_id']
        if rid not in ids or rid in seen or rid not in active:
            issues.append(ValidationIssue('Error','Treatment',f'{rid}: treatment requires one unique, known, active risk.'))
        seen.add(rid)
        p=spec['new_probability']
        if p is not None and (not math.isfinite(p) or not 0<=p<=1):
            issues.append(ValidationIssue('Error','Treatment',f'{rid}: treated probability must be between 0 and 1.'))
        if any(not math.isfinite(spec[k]) or spec[k]<0 for k in ('duration_multiplier','cost_multiplier')):
            issues.append(ValidationIssue('Error','Treatment',f'{rid}: multipliers must be finite and non-negative.'))
    return issues

def treatment_specs_safe(data,issues):
    from .validation import ValidationIssue
    try: return treatment_specs(data)
    except (ValueError,TypeError):
        issues.append(ValidationIssue('Error','Treatment','Treatment probability and multipliers must be numeric.'))
        return []
