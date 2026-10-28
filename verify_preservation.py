"""Exact numerical regression against the untouched supplied V2.2 archive.
Run: python verify_preservation.py --iterations 5000 --seed 42
"""
from pathlib import Path
import argparse,hashlib,json,pickle,subprocess,sys,tempfile,zipfile
import pandas as pd
ROOT=Path(__file__).resolve().parent

def compare(a,b,path='root'):
    if isinstance(a,pd.DataFrame):
        # Project narrative names/descriptions are intentionally translated. Every numeric,
        # boolean, scenario/path/ID, ranking and model field remains exact.
        text_columns=[c for c in a if a[c].dtype=='object' and c not in {'Activity_ID','Risk_ID','Scenario','Active_Risks','Critical_Path','Critical_Paths','Cost_Association'}]
        pd.testing.assert_frame_equal(a.drop(columns=text_columns),b.drop(columns=text_columns),check_exact=True,obj=path)
        return
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for key in a:
            if key=='name':continue
            compare(a[key],b[key],path+'.'+str(key))
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
    else:assert a==b,(path,a,b)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--iterations',type=int,default=5000);parser.add_argument('--seed',type=int,default=42);args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='projectrisk_verify_') as work:
        work=Path(work)
        with zipfile.ZipFile(ROOT/'baseline/ProjectRisk_V2_2_original.zip') as z:z.extractall(work/'baseline')
        baseline=work/'baseline/ProjectRisk_V2_2'
        original_core={str(f.relative_to(baseline)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (baseline/'core').glob('*.py')}
        for name,digest in original_core.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('Core changed',name)
        for name in ['data_io/export_results.py','data_io/model_adapter.py','project_risk_template_v2_2.xlsx']:
            assert (baseline/name).read_bytes()==(ROOT/name).read_bytes(),name
        results=[]
        for i,(module,book) in enumerate([(baseline,baseline/'project_risk_template_v2_2.xlsx'),(ROOT,ROOT/'project_risk_template_v2_2.xlsx'),(ROOT,ROOT/'project_risk_template_v2_2_pt_BR.xlsx')]):
            output=work/f'case_{i}.pickle'
            subprocess.run([sys.executable,'-B',str(ROOT/'verification/worker.py'),str(module),str(book),str(args.iterations),str(args.seed),str(output)],check=True,cwd=module)
            # Loading only our own just-generated local verification outputs.
            with open(output,'rb') as f:results.append(pickle.load(f))
        compare(results[0],results[1]);compare(results[0],results[2])
        summary={'result':'PASS','iterations_per_main_run':args.iterations,'seed':args.seed,'engines_compared':['original V2.2','bilingual English workbook','bilingual Portuguese workbook'],'main_iteration_frames':'exact equality for every project, activity and risk cell','portrait':'all cumulative scenarios at 100 iterations; exact equality of every scenario iteration frame and summary','treatments':'single and multiple risk scenarios at 100 iterations; exact equality','unchanged_core_files':original_core,'canonical_exporter_model_adapter_english_workbook':'byte-identical to supplied V2.2','translated_narrative_fields':'excluded from numerical comparison; source text is preserved in the original workbook and archive'}
        (ROOT/'verification/NUMERICAL_EQUIVALENCE.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
        print('PASS: original, English and Portuguese results are exactly equal. Core files are byte-identical.',flush=True)
if __name__=='__main__':main()
