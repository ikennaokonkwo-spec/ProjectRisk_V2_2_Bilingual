
from core.simulation import simulate
from core.treatment import apply_treatments

def run():
    # 1) Intrinsic cost uncertainty is reproducible and active.
    a=[{"id":"A","name":"A","predecessors":[],"duration_model":"Fixed","duration_params":{"fixed":10},
        "cost_model":"Uniform","cost_params":{"min":100,"max":200}}]
    x=simulate(a,[],[],100,123)
    y=simulate(a,[],[],100,123)
    assert x["project"]["Cost"].equals(y["project"]["Cost"])
    assert x["project"]["Cost"].nunique()>1

    # 2) Relative duration impact: 10% of base duration 10 = +1.
    r=[{"id":"R1","name":"R1","type":"Threat","probability_model":"Fixed",
        "probability_params":{"fixed":1.0},"probability":1.0,"active":True}]
    m=[{"risk_id":"R1","activity_id":"A","impact_type":"Duration","impact_mode":"Relative",
        "distribution":"Fixed","params":{"fixed":0.10}}]
    z=simulate(a,r,m,10,1)
    assert (z["project"]["Duration"]==11).all()

    # 3) Uniform probability range is sampled and bounded.
    ru=[{"id":"R1","name":"R1","type":"Threat","probability_model":"Uniform",
         "probability_params":{"min":0.2,"max":0.4},"probability":0.3,"active":True}]
    u=simulate(a,ru,m,200,9)
    assert u["risks"]["Probability_Used"].between(.2,.4).all()
    assert u["risks"]["Probability_Used"].nunique()>1

    # 4) Combined treatment modifies multiple risks without mutating originals.
    rr=[
      {"id":"R1","type":"Threat","probability_model":"Fixed","probability_params":{"fixed":1.0},"probability":1.0,"active":True},
      {"id":"R2","type":"Threat","probability_model":"Fixed","probability_params":{"fixed":1.0},"probability":1.0,"active":True}]
    mm=[
      {"risk_id":"R1","activity_id":"A","impact_type":"Duration","impact_mode":"Absolute","distribution":"Fixed","params":{"fixed":2}},
      {"risk_id":"R2","activity_id":"A","impact_type":"Duration","impact_mode":"Absolute","distribution":"Fixed","params":{"fixed":3}}]
    tr,tm=apply_treatments(rr,mm,[
      {"risk_id":"R1","new_probability":0.0,"impact_multiplier":1.0},
      {"risk_id":"R2","new_probability":1.0,"impact_multiplier":0.5}])
    assert rr[0]["probability"]==1.0 and mm[1]["params"]["fixed"]==3
    out=simulate(a,tr,tm,10,4)
    assert (out["project"]["Duration"]==11.5).all()
    print("test_v2_extensions: PASS")
if __name__=="__main__": run()
