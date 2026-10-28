
from __future__ import annotations
import networkx as nx

def build_network(activities):
    g=nx.DiGraph()
    for a in activities: g.add_node(a["id"])
    for a in activities:
        for pred in a.get("predecessors",[]): g.add_edge(pred,a["id"])
    if not nx.is_directed_acyclic_graph(g): raise ValueError("Project network contains a cycle.")
    return g

def calculate_cpm(activities,durations):
    g=build_network(activities); order=list(nx.topological_sort(g))
    es={}; ef={}
    for a in order:
        es[a]=max((ef[p] for p in g.predecessors(a)),default=0.0)
        ef[a]=es[a]+float(durations[a])
    pdur=max(ef.values(),default=0.0)
    lf={}; ls={}
    for a in reversed(order):
        succ=list(g.successors(a)); lf[a]=min((ls[s] for s in succ),default=pdur); ls[a]=lf[a]-float(durations[a])
    slack={a:ls[a]-es[a] for a in order}
    critical=[a for a in order if abs(slack[a])<=1e-9]
    cset=set(critical)
    cedges=[(u,v) for u,v in g.edges if u in cset and v in cset and abs(ef[u]-es[v])<=1e-9]
    cg=nx.DiGraph(); cg.add_nodes_from(critical); cg.add_edges_from(cedges)
    sources=[n for n in critical if cg.in_degree(n)==0 and abs(es[n])<=1e-9]
    sinks=[n for n in critical if cg.out_degree(n)==0 and abs(ef[n]-pdur)<=1e-9]
    paths=[]
    for s in sources:
        for t in sinks:
            if s==t: paths.append([s])
            elif nx.has_path(cg,s,t): paths.extend(list(nx.all_simple_paths(cg,s,t)))
    return {"project_duration":pdur,"ES":es,"EF":ef,"LS":ls,"LF":lf,"Slack":slack,"slack":slack,
            "critical_activities":critical,"critical_edges":cedges,"critical_paths":paths}
