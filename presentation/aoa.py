"""Precedence-equivalent activity-on-arrow conversion and reference SVG presentation."""
from __future__ import annotations
import html
import math
import networkx as nx
from core.network import build_network
from core.distributions import expected_value
from localization import translate_in_language

def network_label(code,lang='en'):
    return translate_in_language({'AON':'AON — Activities on nodes','AOA':'AOA — Activities on arrows'}[code],lang)

def build_aoa(activities,durations=None):
    """Unique real-activity finish events avoid parallel arrows and false dependencies.

    Singleton predecessor sets reuse their finish event. Multiple-predecessor sets
    receive a shared join event with zero-duration dummies. This is not a claim
    of minimum dummy count; it preserves exactly the supplied precedence closure.
    """
    dag=build_network(activities)
    if not activities:return {'graph':nx.DiGraph(),'activities':{},'events':{},'project_duration':0.0,'source':None,'sink':None}
    lookup={a['id']:a for a in activities}
    durations=durations if durations is not None else {a['id']:expected_value(a['duration_model'],a['duration_params']) for a in activities}
    if any(not math.isfinite(float(durations[k])) or float(durations[k])<0 for k in lookup):
        raise ValueError('AOA durations must be finite and non-negative.')
    graph=nx.DiGraph();ends={};starts={};joins={}
    def event():
        node=f'E{len(graph):02d}';graph.add_node(node);return node
    source=event()
    for aid in nx.topological_sort(dag):
        preds=frozenset(dag.predecessors(aid))
        if not preds:start=source
        elif len(preds)==1:start=ends[next(iter(preds))]
        else:
            if preds not in joins:
                join=event();joins[preds]=join
                for p in sorted(preds):graph.add_edge(ends[p],join,duration=0.0,activity_id=None,dummy=True)
            start=joins[preds]
        finish=event();starts[aid]=start;ends[aid]=finish
        graph.add_edge(start,finish,duration=float(durations[aid]),activity_id=aid,dummy=False)
    terminals=[ends[k] for k in dag if dag.out_degree(k)==0]
    if len(terminals)==1:sink=terminals[0]
    else:
        sink=event()
        for node in terminals:graph.add_edge(node,sink,duration=0.0,activity_id=None,dummy=True)
    order=list(nx.topological_sort(graph));early={}
    for node in order:early[node]=max((early[p]+graph[p][node]['duration'] for p in graph.predecessors(node)),default=0.0)
    duration=early[sink];late={}
    for node in reversed(order):late[node]=min((late[s]-graph[node][s]['duration'] for s in graph.successors(node)),default=duration)
    records={}
    for aid in lookup:
        start,finish=starts[aid],ends[aid];d=float(durations[aid]);slack=late[finish]-early[start]-d
        records[aid]={'start_event':start,'finish_event':finish,'ES':early[start],'EF':early[finish],'LS':late[finish]-d,'LF':late[finish],'Slack':slack,'Critical':abs(slack)<=1e-9,'duration':d}
    for u,v,edge in graph.edges(data=True):edge['critical']=abs(late[v]-early[u]-edge['duration'])<=1e-9
    return {'graph':graph,'activities':records,'events':{n:{'early':early[n],'late':late[n],'slack':late[n]-early[n]} for n in graph},'project_duration':duration,'source':source,'sink':sink}

def aoa_svg_html(activities,lang='en'):
    result=build_aoa(activities);graph=result['graph']
    if not graph:return '<div></div>'
    number=lambda x:format(x,'.2f').replace('.',',') if lang=='pt_BR' else format(x,'.2f')
    layers=list(nx.topological_generations(graph));max_layer=max(map(len,layers))
    width=max(1100,120+(len(layers)-1)*420);height=max(460,160+max_layer*200)
    positions={}
    for i,layer in enumerate(layers):
        for j,node in enumerate(layer):positions[node]=(60+i*420,height/2+(j-(len(layer)-1)/2)*200)
    escape=lambda v:html.escape(str(v),quote=True)
    p=[f'<div style="width:100%;overflow:auto;border:1px solid #E5E7EB;border-radius:8px;background:white;padding:8px"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AOA" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       '<defs><marker id="aoa-grey" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3z" fill="#6B7280"/></marker><marker id="aoa-red" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3z" fill="#D62728"/></marker></defs>']
    for u,v,edge in graph.edges(data=True):
        x1,y1=positions[u];x2,y2=positions[v];sx=x1+48;ex=x2-48;mid=(sx+ex)/2;ymid=(y1+y2)/2
        red=edge['critical'];color='#D62728' if red else '#6B7280';marker='aoa-red' if red else 'aoa-grey';dash=' stroke-dasharray="7 5"' if edge['dummy'] else ''
        p.append(f'<path data-dummy="{str(edge["dummy"]).lower()}" d="M {sx} {y1} C {mid} {y1}, {mid} {y2}, {ex} {y2}" stroke="{color}" stroke-width="{3.2 if red else 1.6}" fill="none" marker-end="url(#{marker})"{dash}/>')
        if edge['dummy']:
            p.append(f'<text x="{mid}" y="{ymid-8}" font-family="Arial" font-size="11" text-anchor="middle" fill="#374151">0</text>')
            continue
        aid=edge['activity_id'];r=result['activities'][aid]
        fill='#FFF7F7' if red else '#F8FAFC'
        p.append(f'<g data-activity="{escape(aid)}"><rect x="{mid-94}" y="{ymid-44}" width="188" height="88" rx="5" fill="{fill}" stroke="{color}"/>')
        lines=[(aid,-27,'700'),('Dur '+number(r['duration']),-10,'500'),('ES '+number(r['ES'])+'   EF '+number(r['EF']),7,'500'),('LS '+number(r['LS'])+'   LF '+number(r['LF']),24,'500'),(('Folga ' if lang=='pt_BR' else 'Slack ')+number(r['Slack']),40,'500')]
        for text,dy,weight in lines:p.append(f'<text x="{mid}" y="{ymid+dy}" font-family="Arial,sans-serif" font-size="12" font-weight="{weight}" fill="#111111" text-anchor="middle">{escape(text)}</text>')
        p.append('</g>')
    for node,(x,y) in positions.items():
        record=result['events'][node];critical=abs(record['slack'])<=1e-9;stroke='#D62728' if critical else '#64748B'
        p.append(f'<circle cx="{x}" cy="{y}" r="48" fill="{"#FFF7F7" if critical else "#F8FAFC"}" stroke="{stroke}" stroke-width="2"/>')
        for text,dy in [(node,-17),('tE '+number(record['early']),1),('tL '+number(record['late']),19)]:p.append(f'<text x="{x}" y="{y+dy}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#111111">{escape(text)}</text>')
    p.append('</svg></div>');return ''.join(p)
