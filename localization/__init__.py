"""Language boundaries only. No simulation or model state is translated in place."""
from __future__ import annotations
import copy
import json
import numbers
from contextvars import ContextVar
from pathlib import Path
import re
import pandas as pd
import numpy as np

_ROOT = Path(__file__).parent
PT = json.loads((_ROOT/'pt_BR.json').read_text(encoding='utf-8'))
FIELDS = json.loads((_ROOT/'fields.json').read_text(encoding='utf-8'))
DEMO = json.loads((_ROOT/'demo_texts_pt_BR.json').read_text(encoding='utf-8'))
DEMO_REVERSE = {v:k for k,v in DEMO.items()}
TEMPLATES = json.loads((_ROOT/'templates_pt_BR.json').read_text(encoding='utf-8'))
REVERSE = {v:k for k,v in PT.items() if v!=k}
_language = ContextVar('project_risk_language', default='en')

def set_language(language):
    if language not in ('en','pt_BR'):
        raise ValueError('Unsupported language / Idioma não suportado')
    _language.set(language)

def language(): return _language.get()

def _pattern(template):
    parts = re.split(r'(\{\d+\})',template)
    return re.compile('^'+''.join('(.*?)' if re.fullmatch(r'\{\d+\}',p) else re.escape(p) for p in parts)+'$',re.DOTALL)

_PATTERNS = [(_pattern(a),b,a) for a,b in sorted(TEMPLATES.items(),key=lambda p:len(re.sub(r'\{\d+\}','',p[0])),reverse=True) if not a.endswith(': ')]

def t(text, _depth=0):
    if not isinstance(text,str): return text
    if language() == 'en': return REVERSE.get(text,text)
    if text in PT: return PT[text]
    if re.fullmatch(r'(?:[ARS]\d+|ST)',text): return text
    if _depth<3:
        for pattern,target,source in _PATTERNS:
            match=pattern.fullmatch(text)
            if match:
                indices=set()
                if source.startswith(('Time unit:', 'Worksheet ', 'Missing required worksheet', 'Workbook could not be read')):indices=set(range(len(match.groups())))
                elif source=='{0} — {1}' or 'acceptance documentation incomplete' in source or 'cannot reconcile live cost inputs' in source or '{1} must be' in source:indices={1}
                elif 'invalid parameters for' in source:indices={len(match.groups())-1}
                elif source=='{0} must be non-negative if supplied.':indices={0}
                return target.format(*(t(v,_depth+1) if i in indices else v for i,v in enumerate(match.groups())))
        for prefix in ('**Critical path(s):** ',):
            if text.startswith(prefix): return PT[prefix]+text[len(prefix):]
        # Lists embedded in diagnostics contain canonical field identifiers.
        if ', ' in text:
            return ', '.join(t(part,_depth+1) for part in text.split(', '))
    return text

def number(value,spec=',.2f'):
    """Explicit formatting: never changes process locale or the stored number."""
    rendered=format(value,spec)
    return rendered.translate(str.maketrans({',':'.','.':','})) if language()=='pt_BR' else rendered

# IDs and path strings are data, even when an ID happens to be an English word.
IDENTITY_COLUMNS={'Activity_ID','Risk_ID','Predecessors','Parent_Risk','Child_Risk','Critical_Path','Critical_Paths','Scenario','risk_id'}

def cell_value(value,column):
    if not isinstance(value,str):return value
    if column in IDENTITY_COLUMNS:return value
    from .schema import CONTROLLED
    if column in CONTROLLED or column in {'severity','area','message','Metric','Active_Risks','Field'}:
        return t(value)
    return DEMO.get(value,value) if language()=='pt_BR' else DEMO_REVERSE.get(value,value)

def display_value(value):
    if isinstance(value,(bool,np.bool_)): return t('true' if value else 'false')
    if isinstance(value,numbers.Integral): return number(value,',d')
    if isinstance(value,numbers.Real): return number(value,',.10g')
    return t(value)

def localized_frame(df):
    """A fresh export/presentation frame; original data and numeric dtypes survive."""
    out=df.copy(deep=True)
    for col in out:
        if language()=='pt_BR' and pd.api.types.is_bool_dtype(out[col]):
            out[col]=out[col].map(lambda v:t('true' if v else 'false'))
        elif pd.api.types.is_object_dtype(out[col]) or pd.api.types.is_string_dtype(out[col]):
            out[col]=out[col].map(lambda v:cell_value(v,col))
    labels={c:t(c) for c in out.columns}
    if 'Duration_Association' in out and 'Cost_Association' in out:
        labels['Cost_Association']='Associacao_com_o_Custo' if language()=='pt_BR' else 'Cost_Association'
    out=out.rename(columns=labels)
    if len(set(out.columns))!=len(out.columns):
        raise ValueError('Duplicate translated output headers / Cabeçalhos traduzidos duplicados')
    return out

def table_view(value):
    from pandas.io.formats.style import Styler
    if isinstance(value,Styler):
        # Preserve gradient subsets and existing canonical data; translate only display functions.
        out=copy.deepcopy(value)
        out.format({c:(lambda v,c=c:display_value(cell_value(v,c)) if not isinstance(v,str) else cell_value(v,c)) for c in out.data.columns}).format_index(lambda c:'Associacao_com_o_Custo' if language()=='pt_BR' and c=='Cost_Association' and 'Duration_Association' in out.data else t(c),axis=1)
        return out
    return value.style.format({c:(lambda v,c=c:display_value(v) if not isinstance(v,str) else cell_value(v,c)) for c in value.columns}).format_index(lambda c:'Associacao_com_o_Custo' if language()=='pt_BR' and c=='Cost_Association' and 'Duration_Association' in value else t(c),axis=1) if isinstance(value,pd.DataFrame) else value

def figure_view(fig):
    from matplotlib.ticker import FuncFormatter
    for ax in fig.axes:
        ax.set_title(t(ax.get_title()))
        ax.set_xlabel(t(ax.get_xlabel()))
        ax.set_ylabel(t(ax.get_ylabel()))
        for txt in ax.texts: txt.set_text(t(txt.get_text()))
        legend=ax.get_legend()
        if legend:
            for txt in legend.get_texts(): txt.set_text(t(txt.get_text()))
        if language()=='pt_BR':
            # Preserve custom money formatter (and units), localize its output only.
            from matplotlib.ticker import ScalarFormatter
            for axis in (ax.xaxis,ax.yaxis):
                old=axis.get_major_formatter()
                if isinstance(old,ScalarFormatter):
                    axis.set_major_formatter(FuncFormatter(lambda x,p:number(x,',.6g')))
                elif isinstance(old,FuncFormatter):
                    axis.set_major_formatter(FuncFormatter(lambda x,p,old=old:old(x,p).translate(str.maketrans({',':'.','.':','}))))
    return fig

def network_view(svg):
    if language()=='en': return svg
    # Restrict substitutions to SVG text nodes. Coordinates and path geometry stay untouched.
    def replace(m):
        s=m.group(1)
        for a,b in [('Slack ','Folga '),('Dur ','Dur '),('ES ','IC '),('EF ','TC '),('LS ','IT '),('LF ','TT ')]:
            s=s.replace(a,b)
        s=re.sub(r'(?<=\d)\.(?=\d)',',',s)
        return '>'+s+'</text>'
    return re.sub(r'>([^<>]*)</text>',replace,svg)

def localized_csv(df):
    """UTF-8 BOM for Excel; numeric conversion belongs to CSV serialization only."""
    return localized_frame(df).to_csv(index=False,sep=';' if language()=='pt_BR' else ',',decimal=',' if language()=='pt_BR' else '.').encode('utf-8-sig')


def translate_in_language(text,lang):
    token=_language.set(lang)
    try: return t(text)
    finally: _language.reset(token)
