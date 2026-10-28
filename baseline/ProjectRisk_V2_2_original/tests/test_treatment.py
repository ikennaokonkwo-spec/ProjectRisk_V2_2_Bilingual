
from core.treatment import apply_treatment
from core.simulation import simulate

def run():
    a=[{"id":"A","predecessors":[],"duration_model":"Fixed","duration_params":{"fixed":5},"base_cost":100}]
    r=[{"id":"R1","type":"Threat","probability":1.0,"active":True}]
    m=[{"risk_id":"R1","activity_id":"A","impact_type":"Duration","distribution":"Fixed","params":{"fixed":10}}]
    tr,tm=apply_treatment(r,m,"R1",1.0,0.5)
    assert r[0]["probability"]==1.0 and m[0]["params"]["fixed"]==10
    assert (simulate(a,r,m,10,10)["project"]["Duration"]==15).all()
    assert (simulate(a,tr,tm,10,10)["project"]["Duration"]==10).all()
    zr,zm=apply_treatment(r,m,"R1",0.0,1.0)
    assert (simulate(a,zr,zm,10,10)["project"]["Duration"]==5).all()
    print("test_treatment: PASS")
if __name__=="__main__": run()
