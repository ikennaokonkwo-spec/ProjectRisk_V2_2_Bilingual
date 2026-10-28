"""Normalize bilingual workbook structures before any original validation runs."""
import re
import unicodedata
import pandas as pd
from . import FIELDS, PT

SHEETS={k:FIELDS[k] for k in ['Project','Activities','Risk_Register','Risk_Activity_Map','Risk_Relationships','Risk_Treatments','Risk_Categories','Case_Assumptions']}

def token(value):
    if pd.isna(value): return ''
    return ''.join(c for c in unicodedata.normalize('NFKD',str(value).replace('\ufeff','').strip()) if not unicodedata.combining(c)).casefold()

_HEADERS={token(v):k for k,v in FIELDS.items() if k not in SHEETS and k[0].isupper()}
_HEADERS.update({token(k):k for k in FIELDS if k not in SHEETS and k[0].isupper()})

def canonical_header(value):
    return _HEADERS.get(token(value),str(value).replace('\ufeff','').strip()) if not pd.isna(value) else ''

def resolve_sheets(names):
    aliases={token(alias):key for key,val in SHEETS.items() for alias in (key,val)}
    out={}
    for name in names:
        canonical=aliases.get(token(name))
        if canonical:
            if canonical in out:
                raise ValueError(f"Duplicate bilingual worksheets / Planilhas bilíngues duplicadas: {out[canonical]}, {name}")
            out[canonical]=name
    return out

CONTROLLED={
 'Duration_Model':{'Fixed','Triangular','Beta-PERT','Normal','Uniform'},
 'Cost_Model':{'Fixed','Triangular','Beta-PERT','Normal','Uniform'},
 'Distribution':{'Fixed','Triangular','Beta-PERT','Normal','Uniform'},
 'Impact_Distribution_Default':{'Fixed','Triangular','Beta-PERT','Normal','Uniform'},
 'Probability_Model':{'Fixed','Uniform'},'Risk_Type':{'Threat','Opportunity'},
 'Scope':{'Local','Global'},'Impact_Type':{'Duration','Cost','Both'},
 'Impact_Mode':{'Absolute','Relative'},'Cost_Association':{'Fixed only','Fixed + time'},
 'Response_Action':{'Avoid','Mitigate','Transfer','Accept','Exploit','Enhance','Share'},
 'Response_Strategy':{'Avoid','Mitigate','Transfer','Accept','Exploit','Enhance','Share'},
 'Status':{'Open','Monitoring','Closed'},
 'Residual_Acceptance':{'Pending','Accepted','Further treatment required'},
 'Relationship_Type':{'Causes/Increases','Causes','Increases Probability','Decreases Probability','Conditional','Reduces'},
 'Category':{'Commercial','Contractor','Coordination','Design','Environmental','Equipment','Financial','Geotechnical','HSE','Innovation','Operational','Quality','Regulatory','Resource','Security','Stakeholder','Supply','Technical'},
}
# Text-encoded numbers only. Real Excel numeric cells pass through unchanged.
NUMERIC=set('Duration_Fixed Duration_Min Duration_MostLikely Duration_Max Duration_Mean Duration_SD Cost_Fixed Cost_Min Cost_MostLikely Cost_Max Cost_Mean Cost_SD Fixed_Cost Cost_Rate Base_Cost Original_Base_Cost Reference_Duration Time_Dependent_Share Reference_Total Probability Probability_Min Probability_Max Qualitative_Schedule_Impact Qualitative_Cost_Impact Residual_Probability Residual_Schedule_Impact Residual_Cost_Impact Impact_Fixed Impact_Min Impact_MostLikely Impact_Max Impact_Mean Impact_SD Influence_Parameter Treated_Probability Duration_Impact_Multiplier Cost_Impact_Multiplier'.split())

def numeric(value,pt):
    if not isinstance(value,str) or not value.strip(): return value
    s=value.strip()
    # Never guess foreign separators. Invalid/ambiguous formats fail explicitly.
    pattern=r'[+-]?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d+)?(?:[eE][+-]?\d+)?' if pt else r'[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?(?:[eE][+-]?\d+)?'
    if not re.fullmatch(pattern,s):
        raise ValueError(f"Invalid numeric text / Texto numérico inválido: {value!r}. Use numeric Excel cells / Use células numéricas do Excel.")
    return float(s.replace('.','').replace(',','.')) if pt else float(s.replace(',',''))

def normalize_table(df,sheet,pt=False):
    out=df.copy()
    if sheet=='Project':
        out['Field']=out['Field'].map(canonical_header)
        for i,row in out.iterrows():
            if row['Field'] in {'Simulation_Iterations','Random_Seed','Target_Duration','Target_Cost'}:
                out.at[i,'Value']=numeric(row['Value'],pt)
            elif row['Field']=='Time_Unit':
                choices=['days','project time units']
                rev={token(PT.get(v,v)):v for v in choices}
                out.at[i,'Value']=rev.get(token(row['Value']),row['Value'])
        return out
    for col in out:
        if col in CONTROLLED:
            choices=CONTROLLED[col]
            aliases={token(a):v for v in choices for a in (v,PT.get(v,v))}
            out[col]=out[col].map(lambda v:aliases.get(token(v),v))
        elif col=='Active':
            bools={'true':True,'verdadeiro':True,'sim':True,'yes':True,'y':True,'1':True,'false':False,'falso':False,'nao':False,'no':False,'n':False,'0':False}
            out[col]=out[col].map(lambda v:bools.get(token(v),v))
        elif col in NUMERIC:
            out[col]=out[col].map(lambda v:numeric(v,pt))
        elif col=='Predecessors':
            out[col]=out[col].map(lambda v:v.replace(';',',') if isinstance(v,str) else v)
    return out
