
from pathlib import Path
import subprocess,sys,os
root=Path(__file__).resolve().parent
env=dict(os.environ); env["PYTHONPATH"]=str(root); env["PYTHONDONTWRITEBYTECODE"]="1"
tests=["tests/test_core.py","tests/test_treatment.py","tests/test_v2_extensions.py","tests/test_integration.py","tests/test_management_costs.py","tests/test_populated_case.py","tests/test_live_workbook.py","tests/test_cost_model.py","tests/test_header_detection.py","tests/test_app_workflow.py","tests/test_bilingual.py","tests/test_bilingual_workflow.py"]
failed=[]
for test in tests:
    print(f"\n=== {test} ===")
    p=subprocess.run([sys.executable,"-B",test],cwd=root,env=env)
    if p.returncode: failed.append(test)
if failed:
    print("\nFAILED:",", ".join(failed)); raise SystemExit(1)
print("\nALL V2.2 AND BILINGUAL TESTS PASSED / TODOS OS TESTES V2.2 E BILINGUES PASSARAM")
