
from core.network import calculate_cpm
from core.simulation import simulate

def run():
    serial = [
        {"id":"A","predecessors":[],"duration_model":"Fixed","duration_params":{"fixed":2},"base_cost":10},
        {"id":"B","predecessors":["A"],"duration_model":"Fixed","duration_params":{"fixed":3},"base_cost":20},
        {"id":"C","predecessors":["B"],"duration_model":"Fixed","duration_params":{"fixed":4},"base_cost":30},
    ]
    assert calculate_cpm(serial,{"A":2,"B":3,"C":4})["project_duration"] == 9

    branch = [
        {"id":"A","predecessors":[],"duration_model":"Fixed","duration_params":{"fixed":2},"base_cost":0},
        {"id":"B","predecessors":["A"],"duration_model":"Fixed","duration_params":{"fixed":5},"base_cost":0},
        {"id":"C","predecessors":["A"],"duration_model":"Fixed","duration_params":{"fixed":3},"base_cost":0},
        {"id":"D","predecessors":["B","C"],"duration_model":"Fixed","duration_params":{"fixed":1},"base_cost":0},
    ]
    c = calculate_cpm(branch,{"A":2,"B":5,"C":3,"D":1})
    assert c["project_duration"] == 8
    assert set(c["critical_activities"]) == {"A","B","D"}

    risk=[{"id":"R1","type":"Threat","probability":1.0,"active":True}]
    mapping=[{"risk_id":"R1","activity_id":"B","impact_type":"Duration","distribution":"Fixed","params":{"fixed":4}}]
    r=simulate(serial,risk,mapping,20,7)
    assert (r["project"]["Duration"]==13).all()
    assert (r["activities"].query("Activity_ID=='B'")["Risk_Duration_Impact"]==4).all()

    stochastic=[{"id":"A","predecessors":[],"duration_model":"Triangular",
                 "duration_params":{"min":1,"most_likely":2,"max":4},"base_cost":0}]
    x=simulate(stochastic,[],[],50,42)["project"]["Duration"]
    y=simulate(stochastic,[],[],50,42)["project"]["Duration"]
    assert x.equals(y)

    # Common random numbers: base activity draws remain identical across risk scenarios.
    rr=[{"id":"R1","type":"Threat","probability":0.5,"active":True}]
    mm=[{"risk_id":"R1","activity_id":"A","impact_type":"Duration","distribution":"Fixed","params":{"fixed":2}}]
    b=simulate(stochastic,rr,mm,50,99,active_risks=set())
    w=simulate(stochastic,rr,mm,50,99,active_risks={"R1"})
    assert b["activities"]["Base_Duration"].reset_index(drop=True).equals(
        w["activities"]["Base_Duration"].reset_index(drop=True))
    print("test_core: PASS")
if __name__=="__main__": run()
