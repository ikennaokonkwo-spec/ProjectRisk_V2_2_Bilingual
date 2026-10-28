
from __future__ import annotations
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from .distributions import expected_value
from .network import calculate_cpm

def _clean(v):
    v=float(v)
    return 0.0 if abs(v)<1e-9 else round(v,2)

def reference_cpm(activities):
    durations={a["id"]:expected_value(a["duration_model"],a["duration_params"]) for a in activities}
    cpm=calculate_cpm(activities,durations)
    rows=[]
    names={a["id"]:a.get("name","") for a in activities}
    for a in activities:
        aid=a["id"]
        rows.append({"Activity_ID":aid,"Activity_Name":names[aid],"Reference_Duration":_clean(durations[aid]),
            "ES":_clean(cpm["ES"][aid]),"EF":_clean(cpm["EF"][aid]),"LS":_clean(cpm["LS"][aid]),"LF":_clean(cpm["LF"][aid]),
            "Slack":_clean(cpm["Slack"][aid]),"Critical":aid in set(cpm["critical_activities"])})
    return pd.DataFrame(rows),cpm

def cpm_edges(reference_table,activities):
    lookup=reference_table.set_index("Activity_ID").to_dict("index")
    out=[]
    for a in activities:
        for p in a["predecessors"]:
            if lookup[p]["Critical"] and lookup[a["id"]]["Critical"] and abs(lookup[p]["EF"]-lookup[a["id"]]["ES"])<=1e-9:
                out.append((p,a["id"]))
    return out

def network_figure(activities,reference_table):
    g=nx.DiGraph()
    for a in activities:
        g.add_node(a["id"])
        for pred in a["predecessors"]: g.add_edge(pred,a["id"])

    layers=list(nx.topological_generations(g))
    pos={}
    for x,layer in enumerate(layers):
        n=len(layer)
        for j,node in enumerate(layer):
            pos[node]=(x*3.8,((n-1)/2-j)*2.8)

    lookup=reference_table.set_index("Activity_ID").to_dict("index")
    critical=[n for n in g.nodes if lookup[n]["Critical"]]
    normal=[n for n in g.nodes if n not in critical]
    crit_edges=cpm_edges(reference_table,activities)
    normal_edges=[e for e in g.edges if e not in crit_edges]

    fig_w=max(20,min(46,len(layers)*3.5))
    max_layer=max((len(layer) for layer in layers),default=1)
    fig_h=max(9,min(30,max_layer*3.0+3))
    fig,ax=plt.subplots(figsize=(fig_w,fig_h))

    nx.draw_networkx_edges(g,pos,edgelist=normal_edges,ax=ax,arrows=True,arrowsize=24,
        width=1.4,edge_color="#6B7280")
    nx.draw_networkx_edges(g,pos,edgelist=crit_edges,ax=ax,arrows=True,arrowsize=27,
        width=3.6,edge_color="#D62728")

    nx.draw_networkx_nodes(g,pos,nodelist=normal,node_size=7600,node_shape="s",
        node_color="#F8FAFC",edgecolors="#64748B",linewidths=1.4,ax=ax)
    nx.draw_networkx_nodes(g,pos,nodelist=critical,node_size=7800,node_shape="s",
        node_color="#FFF7F7",edgecolors="#D62728",linewidths=2.3,ax=ax)

    labels={}
    for n in g.nodes:
        r=lookup[n]
        labels[n]=(f"{n}\nDur {r['Reference_Duration']:.2f}\n"
                   f"ES {r['ES']:.2f}   EF {r['EF']:.2f}\n"
                   f"LS {r['LS']:.2f}   LF {r['LF']:.2f}\n"
                   f"Slack {r['Slack']:.2f}")
    nx.draw_networkx_labels(g,pos,labels=labels,font_size=10,font_color="#111111",
        font_weight="medium",ax=ax)
    ax.set_title("Activity-on-Node Project Network — Reference CPM",fontsize=16,pad=20)
    ax.margins(x=.04,y=.12)
    ax.axis("off")
    fig.tight_layout()
    return fig


def network_svg_html(activities, reference_table):
    """Scrollable vector network for the Streamlit UI; text remains legible at large project sizes."""
    import html
    g=nx.DiGraph()
    for a in activities:
        g.add_node(a["id"])
        for pred in a["predecessors"]:
            g.add_edge(pred,a["id"])
    layers=list(nx.topological_generations(g))
    lookup=reference_table.set_index("Activity_ID").to_dict("index")
    crit=set(cpm_edges(reference_table,activities))

    node_w,node_h=190,122
    x_gap,y_gap=285,175
    margin_x,margin_y=45,55
    max_layer=max((len(layer) for layer in layers),default=1)
    width=max(1100,margin_x*2+(len(layers)-1)*x_gap+node_w)
    height=max(420,margin_y*2+(max_layer-1)*y_gap+node_h)
    pos={}
    for xi,layer in enumerate(layers):
        total=(len(layer)-1)*y_gap
        y0=(height-total-node_h)/2
        for yi,node in enumerate(layer):
            pos[node]=(margin_x+xi*x_gap,y0+yi*y_gap)

    parts=[]
    parts.append(
        '<div style="width:100%; overflow-x:auto; overflow-y:auto; border:1px solid #E5E7EB; '
        'border-radius:8px; background:white; padding:8px;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<defs>'
        '<marker id="arrowGrey" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#6B7280"/></marker>'
        '<marker id="arrowRed" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#D62728"/></marker>'
        '</defs>'
    )
    for u,v in g.edges:
        x1,y1=pos[u]; x2,y2=pos[v]
        sx=x1+node_w; sy=y1+node_h/2; ex=x2; ey=y2+node_h/2
        iscrit=(u,v) in crit
        color="#D62728" if iscrit else "#6B7280"
        line_w=4 if iscrit else 1.6
        marker="arrowRed" if iscrit else "arrowGrey"
        parts.append(
            f'<path d="M {sx} {sy} C {(sx+ex)/2} {sy}, {(sx+ex)/2} {ey}, {ex} {ey}" '
            f'stroke="{color}" stroke-width="{line_w}" fill="none" marker-end="url(#{marker})"/>'
        )
    for node in g.nodes:
        x,y=pos[node]; r=lookup[node]; critical=bool(r["Critical"])
        fill="#FFF8F8" if critical else "#F8FAFC"
        stroke="#D62728" if critical else "#64748B"
        sw=2.5 if critical else 1.4
        parts.append(
            f'<rect x="{x}" y="{y}" width="{node_w}" height="{node_h}" rx="7" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        lines=[
            (node,y+22,15,"700"),
            (f"Dur {r['Reference_Duration']:.2f}",y+44,14,"500"),
            (f"ES {r['ES']:.2f}   EF {r['EF']:.2f}",y+67,14,"500"),
            (f"LS {r['LS']:.2f}   LF {r['LF']:.2f}",y+90,14,"500"),
            (f"Slack {r['Slack']:.2f}",y+113,14,"500"),
        ]
        for txt,yy,size,weight in lines:
            parts.append(
                f'<text x="{x+node_w/2}" y="{yy}" text-anchor="middle" '
                f'font-family="Arial, sans-serif" font-size="{size}px" font-weight="{weight}" '
                f'fill="#111111">{html.escape(str(txt))}</text>'
            )
    parts.append("</svg></div>")
    return "".join(parts)
