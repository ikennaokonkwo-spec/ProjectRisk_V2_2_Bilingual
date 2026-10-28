"""Keep every original CSV byte-for-byte; add localized copies and a field glossary."""
from io import BytesIO
import json
import zipfile
import pandas as pd
from data_io.export_results import results_zip as canonical_results_zip
from . import language, localized_csv, t, FIELDS

def results_zip(*args,**kwargs):
    original=canonical_results_zip(*args,**kwargs)
    out=BytesIO()
    with zipfile.ZipFile(BytesIO(original)) as source, zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as dest:
        for name in source.namelist():
            raw=source.read(name)
            dest.writestr(name,raw)
            # Read-back is for presentation only. Original canonical CSV bytes stay untouched.
            # Derive frames directly to retain text IDs and values without CSV type inference.
        names=['project_iterations.csv','activity_iterations.csv','risk_iterations.csv','risk_importance.csv','activity_diagnostics.csv','reference_cpm.csv','risk_adjusted_schedule.csv','critical_path_frequency.csv','risk_portrait_summary.csv','treatment_comparison.csv','risk_register_review_v2_2.csv','treatment_assumptions.csv','activity_cost_inputs.csv']
        params=['project','activities','risks','ranking','activity_diagnostics','reference_cpm','schedule_summary','critical_paths','portrait','treatment','register','treatment_assumptions','cost_inputs']
        values=dict(zip(params,args)); values.update(kwargs)
        for param,name in zip(params,names):
            frame=values.get(param)
            if frame is not None: dest.writestr(language()+'/'+name,localized_csv(frame))
        glossary=pd.DataFrame([{'Canonical_Field':k,'English':k,'Português':v} for k,v in FIELDS.items()])
        dest.writestr('field_glossary_en_pt_BR.csv',glossary.to_csv(index=False).encode('utf-8-sig'))
        dest.writestr('LANGUAGE_README.txt',(
            'Original root CSVs retain V2.2 names, values, delimiters and encoding.\n'
            'Selected-language copies are in '+language()+'/ and use UTF-8 BOM.\n'
            'Portuguese copies use semicolon delimiter and decimal comma.\n'
            'User-authored free text is retained; known demonstration-case text has reviewed translations.\n'
            'Os CSVs originais na raiz mantêm nomes, valores, separadores e codificação V2.2.\n'
            'Cópias no idioma selecionado estão em '+language()+'/ e usam UTF-8 BOM.\n'
            'Cópias em português usam ponto e vírgula como separador e vírgula decimal.\n'
            'Textos livres do usuário são preservados; textos conhecidos do caso demonstrativo têm traduções revisadas.\n'
        ).encode('utf-8-sig'))
    return out.getvalue()
