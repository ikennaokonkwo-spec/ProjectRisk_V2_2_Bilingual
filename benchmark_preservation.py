"""Interleaved simulation-only timings. Run when other intensive jobs are idle."""
from pathlib import Path
import json,statistics,subprocess,sys,tempfile,time,zipfile
ROOT=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=='--worker':
    module,book,n=sys.argv[2:];sys.path.insert(0,module)
    from data_io.input_reader import read_v1_workbook
    from data_io.model_adapter import to_model_objects
    from core.simulation import simulate
    objects=to_model_objects(read_v1_workbook(book))
    simulate(*objects,iterations=5,seed=42)
    start=time.perf_counter();result=simulate(*objects,iterations=int(n),seed=42);elapsed=time.perf_counter()-start
    print(json.dumps({'seconds':elapsed,'iterations':int(n)}))
else:
    with tempfile.TemporaryDirectory(prefix='projectrisk_benchmark_') as d:
        d=Path(d)
        with zipfile.ZipFile(ROOT/'baseline/ProjectRisk_V2_2_original.zip') as z:z.extractall(d)
        old=d/'ProjectRisk_V2_2';timings={'original':[],'extended_legacy_inputs':[]}
        for rep in range(3):
            order=['original','extended_legacy_inputs'] if rep%2==0 else ['extended_legacy_inputs','original']
            for name in order:
                module=old if name=='original' else ROOT
                book=module/'project_risk_template_v2_2.xlsx'
                p=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(module),str(book),'400'],capture_output=True,text=True,check=True,cwd=module)
                seconds=json.loads(p.stdout)['seconds'];timings[name].append(seconds)
                print(name,round(seconds,4),'s',flush=True)
        original=statistics.median(timings['original']);extended=statistics.median(timings['extended_legacy_inputs'])
        # New-distribution profile is measured separately; its inputs intentionally differ.
        p=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(ROOT),str(ROOT/'tests/fixtures/all_distributions_en.xlsx'),'400'],capture_output=True,text=True,check=True,cwd=ROOT)
        profile=json.loads(p.stdout)['seconds']
        report={'iterations':400,'seed':42,'repeats_per_legacy_variant':3,'timings_seconds':timings,'median_original_seconds':original,'median_extended_legacy_seconds':extended,'legacy_runtime_change_percent':100*(extended/original-1),'all_eight_distributions_profile_seconds':profile,'scope':'simulation only; excludes workbook import, validation, UI and export; no universal speed guarantee; host timings vary'}
        (ROOT/'verification/PERFORMANCE.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
