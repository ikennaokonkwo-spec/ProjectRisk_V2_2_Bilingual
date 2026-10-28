
from __future__ import annotations
import tempfile
import hashlib
from core.register import register_view, treatment_specs
from core.cost_model import cost_input_summary
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

from data_io.input_reader import read_v1_workbook, project_settings
from data_io.model_adapter import to_model_objects
from data_io.export_results import results_zip
from core.validation import validate_all
from core.simulation import simulate
from core.risk_analysis import project_statistics, risk_importance, activity_diagnostics, activity_schedule_summary, critical_path_frequency
from core.risk_portrait import build_risk_portrait, empirical_cdf
from core.treatment import apply_treatments
from core.reference_analysis import reference_cpm, network_figure, network_svg_html

st.set_page_config(page_title="Project Risk Analysis V2.2",page_icon="📊",layout="wide")
st.title("Project Risk Analysis V2.2")
st.caption("Classroom-oriented project network and probabilistic risk analysis")
st.markdown("**Project → Network/CPM → Risk Register → Mapping → Validate → Simulate → Diagnose → Risk Portrait → Treat → Compare**")

TEMPLATE=Path(__file__).parent/"project_risk_template_v2_2.xlsx"
with open(TEMPLATE,"rb") as f:
    st.download_button("Download V2.2 input template",f.read(),"project_risk_template_v2_2.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

uploaded=st.file_uploader("Upload completed V2.2 workbook",type=["xlsx"])
if uploaded is None:
    st.info("Complete the template and upload it to begin."); st.stop()
with tempfile.NamedTemporaryFile(delete=False,suffix=".xlsx") as tmp:
    tmp.write(uploaded.getvalue()); path=tmp.name
try: data=read_v1_workbook(path)
except Exception as e:
    st.error(f"Workbook could not be read: {e}"); st.stop()

issues=validate_all(data); errors=[x for x in issues if x.severity=="Error"]; warnings=[x for x in issues if x.severity=="Warning"]
st.header("1. Validate")
if errors:
    st.error(f"{len(errors)} blocking validation error(s).")
    st.dataframe(pd.DataFrame([vars(x) for x in issues]),use_container_width=True); st.stop()
st.success("Input validation passed.")
if warnings:
    st.warning(f"{len(warnings)} non-blocking warning(s).")
    st.dataframe(pd.DataFrame([vars(x) for x in warnings]),use_container_width=True)

settings=project_settings(data["Project"]); activities,risks,mappings=to_model_objects(data)
cost_inputs=cost_input_summary(activities)
st.subheader("Activity cost associations")
fixed_count=int((cost_inputs["Cost_Association"]=="Fixed only").sum())
st.caption(f"{fixed_count} fixed-only activities; {len(cost_inputs)-fixed_count} fixed-plus-time activities. Fixed only enforces a zero duration cost rate. Explicit direct risk costs still apply when mapped. Reference totals exclude discrete risks.")
st.dataframe(cost_inputs,use_container_width=True)
st.caption("Edit Cost_Association in Activities and budget/time share in Case_Assumptions. Live Excel formulas feed the simulation; recalculate and save before uploading. Cost inputs are reconciled against the current assumptions to detect stale results.")
def opt_float(v):
    try:
        if pd.isna(v) or str(v).strip()=="": return None
        return float(v)
    except: return None
target_duration=opt_float(settings.get("Target_Duration")); target_cost=opt_float(settings.get("Target_Cost"))

with st.expander("Input data",expanded=False):
    tabs=st.tabs(["Activities","Risk Register","Risk–Activity Mapping","Risk Relationships"])
    with tabs[0]: st.dataframe(data["Activities"],use_container_width=True)
    with tabs[1]: st.dataframe(data["Risk_Register"],use_container_width=True)
    with tabs[2]: st.dataframe(data["Risk_Activity_Map"],use_container_width=True)
    with tabs[3]:
        if "Risk_Relationships" in data:
            st.dataframe(data["Risk_Relationships"],use_container_width=True)
            st.caption("Reserved for the later causal-risk layer; V2.2 does not propagate these relationships.")
        else: st.info("No optional risk-relationship sheet supplied.")

st.header("2. Project Network Analysis")
ref_table,ref_cpm=reference_cpm(activities)
c1,c2=st.columns(2)
c1.metric("Reference project duration",f"{ref_cpm['project_duration']:.2f}")
c2.metric("Critical activities",len(ref_cpm["critical_activities"]))
paths=ref_cpm.get("critical_paths",[])
st.write("**Critical path(s):** " + ("; ".join(" → ".join(p) for p in paths) if paths else "None identified"))
st.caption("Reference durations are distribution expected values; this is the pre-simulation CPM view.")
st.markdown("**Network legend:** red link = critical-path precedence · light red-bordered node = critical activity · grey link = non-critical precedence")
network_html=network_svg_html(activities,ref_table)
components.html(network_html,height=720,scrolling=True)
st.caption("The network is a scrollable vector diagram so node text remains legible even for large projects.")
st.dataframe(ref_table.style.format({"Reference_Duration":"{:.2f}","ES":"{:.2f}","EF":"{:.2f}","LS":"{:.2f}","LF":"{:.2f}","Slack":"{:.2f}"}),use_container_width=True)
st.caption("Critical path here is the reference CPM result. Probabilistic criticality below measures how often each activity is critical across simulations.")

st.header("3. Monte Carlo Simulation")
c1,c2=st.columns(2)
iterations=c1.number_input("Iterations",min_value=100,max_value=100000,value=int(settings.get("Simulation_Iterations",5000)),step=100)
seed=c2.number_input("Random seed",min_value=0,value=int(settings.get("Random_Seed",42)),step=1)
signature=(hashlib.sha256(uploaded.getvalue()).hexdigest(),int(iterations),int(seed))
if st.button("Run simulation",type="primary"):
    with st.spinner("Simulating complete project realizations..."):
        st.session_state["sig"]=signature
        st.session_state["result"]=simulate(activities,risks,mappings,int(iterations),int(seed))
        for k in ["portrait","treatment","treatment_specs"]: st.session_state.pop(k,None)
        for key in list(st.session_state):
            if key.startswith(("p_","dm_","cm_")): st.session_state.pop(key,None)
if st.session_state.get("sig")!=signature or "result" not in st.session_state: st.stop()

result=st.session_state["result"]
stats=project_statistics(result["project"],target_duration,target_cost)
ranking=risk_importance(result["project"],result["risks"])
adiag=activity_diagnostics(result["activities"],result["project"])
pathfreq=critical_path_frequency(result["project"])
schedule=activity_schedule_summary(result["activities"])

st.header("4. Project Risk Results")
st.caption(f"Time unit: {settings.get('Time_Unit','project time unit')} · Currency: {settings.get('Currency','project currency')}")
cols=st.columns(5)
for col,(lab,key,fmt) in zip(cols,[("Mean duration","Mean_Duration",".2f"),("P50 duration","P50_Duration",".2f"),
    ("P90 duration","P90_Duration",".2f"),("Mean cost","Mean_Cost",",.2f"),("P90 cost","P90_Cost",",.2f")]):
    col.metric(lab,format(stats[key],fmt))
if target_duration is not None or target_cost is not None:
    c1,c2=st.columns(2)
    if target_duration is not None: c1.metric("P(Duration ≤ target)",f"{stats['P_Meet_Duration_Target']:.1%}")
    if target_cost is not None: c2.metric("P(Cost ≤ target)",f"{stats['P_Meet_Cost_Target']:.1%}")

t1,t2=st.tabs(["Cumulative probability","Frequency"])
with t1:
    fig,axs=plt.subplots(1,2,figsize=(12,4.5))
    for ax,field,title in [(axs[0],"Duration","Project Duration CDF"),(axs[1],"Cost","Project Cost CDF")]:
        x,y=empirical_cdf(result["project"][field]); ax.plot(x,y); ax.set_title(title); ax.set_xlabel(field); ax.set_ylabel("Cumulative Probability"); ax.grid(alpha=.3)
    st.pyplot(fig); plt.close(fig)
with t2:
    fig,axs=plt.subplots(1,2,figsize=(12,4.5))
    axs[0].hist(result["project"]["Duration"],bins=30); axs[0].set_title("Project Duration Frequency"); axs[0].set_xlabel("Duration")
    axs[1].hist(result["project"]["Cost"],bins=30); axs[1].set_title("Project Cost Frequency"); axs[1].set_xlabel("Cost")
    def compact_money(x,pos):
        ax=abs(x)
        if ax>=1_000_000_000: return f"{x/1_000_000_000:.2f}B"
        if ax>=1_000_000: return f"{x/1_000_000:.3f}M"
        if ax>=1_000: return f"{x/1_000:.1f}K"
        return f"{x:,.0f}"
    axs[1].xaxis.set_major_formatter(FuncFormatter(compact_money))
    axs[1].xaxis.set_major_locator(MaxNLocator(nbins=6))
    axs[1].tick_params(axis="x",labelrotation=0,labelsize=9)
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)

st.header("5. Risk-Adjusted Schedule")
st.caption("Activity cost = fixed cost + cost rate × final activity duration + direct mapped risk costs (total floored at zero). Cost rates use the same time unit as activity durations. Separate direct costs must not repeat the same time-related expense.")
st.caption("P10–P90 activity start/finish ranges summarize schedule uncertainty across Monte Carlo realizations.")
merged=schedule.merge(ref_table[["Activity_ID","Activity_Name","ES","EF"]],on="Activity_ID",suffixes=("_Prob","_Reference"))
fig,ax=plt.subplots(figsize=(11,max(5,len(merged)*.35)))
for y,(_,r) in enumerate(merged.iterrows()):
    ax.hlines(y,r["ES_P10"],r["EF_P90"],linewidth=3,color="#A8B3BF")
    ax.plot([r["ES_P50"],r["EF_P50"]],[y,y],linewidth=6,color="#2F5D7E")
ax.set_yticks(range(len(merged))); ax.set_yticklabels(merged["Activity_ID"]); ax.set_xlabel("Project Time")
ax.set_title("Risk-Adjusted Activity Timing — P10/P50/P90 Envelope"); ax.grid(axis="x",alpha=.3)
st.pyplot(fig); plt.close(fig)
st.dataframe(merged,use_container_width=True)

selected_activity=st.selectbox("Inspect one activity",merged["Activity_ID"].tolist())
ag=result["activities"].query("Activity_ID == @selected_activity")
fig,axs=plt.subplots(1,3,figsize=(12,3.8))
for ax,field in zip(axs,["Final_Duration","ES","EF"]):
    ax.hist(ag[field],bins=25); ax.set_title(f"{selected_activity} — {field}")
st.pyplot(fig); plt.close(fig)

st.header("6. Diagnose")
st.subheader("Risk importance")
st.caption("Risk associations use Pearson correlation between binary risk occurrence and final project duration/cost. Negative values indicate association with shorter duration or lower cost, not an error. Absolute values determine ranking; associations are not causal-effect estimates. Mean_Probability is the input probability averaged across iterations; Occurrence_Rate is the observed frequency. Realized cost impacts report direct mapped costs; duration-related costs appear in activity results.")
st.subheader("Risk register and response planning")
management=register_view(data,ranking)
st.dataframe(management,use_container_width=True)
st.caption("Screening scores = occurrence probability × user-assessed impact (1–5), separately for schedule and cost. These are ordinal screening aids, not monetary expected values. No acceptance thresholds are imposed. Residual assessment and acceptance remain user decisions.")
st.dataframe(ranking.style.background_gradient(subset=["Abs_Duration_Association","Abs_Cost_Association"]),use_container_width=True)
st.subheader("Activity criticality and cruciality")
st.caption("Criticality_Index is the fraction of iterations where the activity is critical. Cruciality_Spearman correlates ranked activity duration with ranked final project duration. Undefined constant-variable associations are displayed as zero for compatibility, not evidence of no effect.")
st.dataframe(adiag.style.background_gradient(subset=["Criticality_Index","Cruciality_Spearman"]),use_container_width=True)
st.subheader("Critical path frequency")
st.caption("Restored from the baseline analytical concept: frequency shows how often each complete path becomes critical across simulations.")
st.dataframe(pathfreq,use_container_width=True)

st.header("7. Risk Portrait")
st.caption("The table retains the complete cumulative risk sequence. The chart intentionally focuses on the four highest-ranked risks so curve separation remains readable.")
if st.button("Build complete Risk Portrait"):
    with st.spinner("Building cumulative scenarios using common random numbers..."):
        st.session_state["portrait"]=build_risk_portrait(activities,risks,mappings,ranking,int(iterations),int(seed),target_duration,target_cost,baseline_result=result)
if "portrait" in st.session_state:
    portrait,scenarios=st.session_state["portrait"]
    cols=["Scenario","Active_Risks","Mean_Duration","P50_Duration","P90_Duration","Delta_Mean_Duration","Delta_P50_Duration","Delta_P90_Duration","Mean_Cost","P90_Cost"]
    st.dataframe(portrait[cols],use_container_width=True)
    # Focused graph: S0, cumulative top four risks, and optional all-active ST.
    focus=["S0"]+[f"S{i}" for i in range(1,5) if f"S{i}" in scenarios]
    show_total=st.checkbox("Show all-active-risks curve (ST)",value=True)
    if show_total and "ST" in scenarios and "ST" not in focus: focus.append("ST")
    # For four or fewer active risks, ST is needed to complete the focused sequence.

    fig,ax=plt.subplots(figsize=(10,5.5))
    for sid in focus:
        row=portrait.loc[portrait["Scenario"]==sid].iloc[0] if sid in set(portrait["Scenario"]) else portrait.iloc[-1]
        x,y=empirical_cdf(scenarios[sid]["project"]["Duration"])
        label="Total Project Risk" if sid=="ST" else f"{sid}: {row['Active_Risks']}"
        ax.plot(x,y,label=label)
    ax.set(xlabel="Project Duration",ylabel="Cumulative Probability",title="Focused Risk Portrait — Four Most Important Risks")
    ax.grid(alpha=.3); ax.legend(loc="best",fontsize=9); fig.tight_layout(); st.pyplot(fig); plt.close(fig)

st.header("8. Risk Treatment")
mode=st.radio("Treatment mode",["Single Risk","Multiple Risks"],horizontal=True)
active_ids={r["id"] for r in risks if r.get("active",True)}
ranked_ids=[rid for rid in ranking["Risk_ID"] if rid in active_ids]
file_specs={x["risk_id"]:x for x in treatment_specs(data)}
if not ranked_ids:
    st.info("No active risks to treat. Activate and map a registered risk to compare treatments.")
selected=([st.selectbox("Risk to treat",ranked_ids)] if mode=="Single Risk" else st.multiselect("Risks to treat",ranked_ids,default=ranked_ids[:min(2,len(ranked_ids))])) if ranked_ids else []
specs=[]
for rid in selected:
    r=next(x for x in risks if x["id"]==rid)
    saved=file_specs.get(rid,{})
    default_p=saved.get("new_probability")
    if default_p is None: default_p=float(r.get("probability",0))
    with st.expander(f"Treatment assumptions — {rid}",expanded=True):
        c1,c2,c3=st.columns(3)
        p=c1.slider(f"Treated probability — {rid}",0.0,1.0,default_p,0.01,key=f"p_{rid}")
        dm=c2.number_input(f"Duration impact multiplier — {rid}",min_value=0.0,value=float(saved.get("duration_multiplier",1)),step=0.05,key=f"dm_{rid}")
        cm=c3.number_input(f"Direct cost impact multiplier — {rid}",min_value=0.0,value=float(saved.get("cost_multiplier",1)),step=0.05,key=f"cm_{rid}")
        specs.append({"risk_id":rid,"new_probability":p,"duration_multiplier":dm,"cost_multiplier":cm})
        record=management.loc[management["Risk_ID"]==rid]
        if not record.empty:
            st.dataframe(record[[c for c in ["Risk_ID","Response_Strategy","Response_Action","Response_Owner","Response_Due_Date","Residual_Acceptance"] if c in record]],use_container_width=True)
if "treatment" in st.session_state and st.session_state.get("treatment_specs") != specs:
    st.session_state.pop("treatment",None)
if selected and st.button("Run treatment comparison"):
    tr,tm=apply_treatments(risks,mappings,specs)
    after=simulate(activities,tr,tm,int(iterations),int(seed))
    bs=project_statistics(result["project"],target_duration,target_cost); ats=project_statistics(after["project"],target_duration,target_cost)
    comp=pd.DataFrame([["Mean Duration",bs["Mean_Duration"],ats["Mean_Duration"]],["P50 Duration",bs["P50_Duration"],ats["P50_Duration"]],
        ["P90 Duration",bs["P90_Duration"],ats["P90_Duration"]],["Mean Cost",bs["Mean_Cost"],ats["Mean_Cost"]],["P90 Cost",bs["P90_Cost"],ats["P90_Cost"]]],
        columns=["Metric","Before","After"]); comp["Change"]=comp["After"]-comp["Before"]
    st.session_state["treatment"]=(after,comp,pd.DataFrame(specs))
    st.session_state["treatment_specs"]=specs
if "treatment" in st.session_state:
    after,comp,specdf=st.session_state["treatment"]
    st.subheader("Treatment assumptions"); st.dataframe(specdf,use_container_width=True)
    st.subheader("Before/after results"); st.dataframe(comp,use_container_width=True)
    fig,ax=plt.subplots(figsize=(9,5))
    for label,res in [("Before treatment",result),("After treatment",after)]:
        x,y=empirical_cdf(res["project"]["Duration"]); ax.plot(x,y,label=label)
    ax.set(xlabel="Project Duration",ylabel="Cumulative Probability",title="Treatment Comparison"); ax.grid(alpha=.3); ax.legend()
    st.pyplot(fig); plt.close(fig)
    st.info("Treatment settings are scenario assumptions for analysis, not optimized recommendations.")

st.header("9. Export")
st.download_button("Download risk register with simulation findings",management.to_csv(index=False).encode("utf-8-sig"),"risk_register_review_v2_2.csv","text/csv")
portrait_df=st.session_state.get("portrait",(None,None))[0]
treat_df=st.session_state.get("treatment",(None,None,None))[1]
bundle=results_zip(result["project"],result["activities"],result["risks"],ranking,adiag,ref_table,schedule,pathfreq,portrait_df,treat_df,management,st.session_state.get("treatment",(None,None,None))[2],cost_inputs)
st.download_button("Download complete analysis results",bundle,"project_risk_analysis_v2_2_results.zip","application/zip")
