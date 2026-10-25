#!/usr/bin/env python3
"""Convert a Graphviz .dot file into (1) a high-resolution PNG and (2) an editable diagrams.net (Draw.io) .drawio file.
Usage: dot2drawio.py <file.dot> [out_dir]     Requires: graphviz (dot).  Layout coordinates come from `dot -Tjson`."""
import json, subprocess, sys, pathlib, html
from xml.sax.saxutils import quoteattr

SC = 72.0  # points per inch

def build(dotfile: pathlib.Path, out: pathlib.Path):
    stem = dotfile.stem
    subprocess.run(["dot", "-Tpng", "-Gdpi=220", str(dotfile), "-o", str(out / f"{stem}.png")], check=True)
    g = json.loads(subprocess.run(["dot", "-Tjson", str(dotfile)], check=True, capture_output=True, text=True).stdout)
    x0, y0, x1, y1 = [float(v) for v in g["bb"].split(",")]
    H = y1 - y0
    cells, ids, nid = [], {}, 2
    def new():
        nonlocal nid; nid += 1; return str(nid)
    def geom(cx, cy, w, h):  # graphviz centre/size -> drawio top-left
        return (cx - w / 2 - x0 + 20, (H - cy) - h / 2 + 20, w, h)
    # clusters (subgraphs) first so they sit behind nodes
    for o in g.get("objects", []):
        if "bb" in o and o["name"].startswith("cluster"):
            a, b, c, d = [float(v) for v in o["bb"].split(",")]
            i = new(); ids[o["_gvid"]] = i
            label = html.unescape(o.get("label", "")).replace("\\n", "<br>")
            style = f"rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;align=left;spacingLeft=8;fillColor={o.get('bgcolor', o.get('fillcolor', '#F5F5F5'))};strokeColor={o.get('color', '#666666')};dashed=1;fontStyle=1;"
            gx, gy, gw, gh = a - x0 + 20, (H - d) + 20, c - a, d - b
            cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{style}" vertex="1" parent="1"><mxGeometry x="{gx:.0f}" y="{gy:.0f}" width="{gw:.0f}" height="{gh:.0f}" as="geometry"/></mxCell>')
    for o in g.get("objects", []):
        if "pos" in o and not o["name"].startswith("cluster"):
            cx, cy = [float(v) for v in o["pos"].split(",")]
            w, h = float(o["width"]) * SC, float(o["height"]) * SC
            x, y, w, h = geom(cx, cy, w, h)
            i = new(); ids[o["_gvid"]] = i
            label = html.unescape(o.get("label", o["name"])).replace("\\n", "<br>")
            shape = o.get("shape", "box")
            sh = "rhombus;" if shape == "diamond" else "shape=cylinder3;boundedLbl=1;" if shape == "cylinder" else "ellipse;" if shape in ("ellipse", "oval") else "rounded=1;arcSize=12;"
            fill = o.get("fillcolor", "#FFFFFF"); stroke = o.get("color", "#333333")
            dashed = "dashed=1;" if "dashed" in o.get("style", "") else ""
            style = f"{sh}whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};{dashed}fontSize=11;"
            cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{style}" vertex="1" parent="1"><mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
    for e in g.get("edges", []):
        s, t = ids.get(e["tail"]), ids.get(e["head"])
        if not s or not t: continue
        i = new(); lab = html.unescape(e.get("label", ""))
        dashed = "dashed=1;" if "dashed" in e.get("style", "") else ""
        col = e.get("color", "#333333")
        cells.append(f'<mxCell id="{i}" value={quoteattr(lab)} style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;{dashed}strokeColor={col};fontSize=10;" edge="1" parent="1" source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    xml = ('<mxfile host="app.diagrams.net"><diagram name="%s" id="%s"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" page="1" pageScale="1" pageWidth="%d" pageHeight="%d"><root><mxCell id="0"/><mxCell id="1" parent="0"/>%s</root></mxGraphModel></diagram></mxfile>'
           % (stem, stem, int(x1 - x0 + 80), int(H + 80), "".join(cells)))
    (out / f"{stem}.drawio").write_text(xml)
    print("built", stem)

if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent.parent
    build(src, out)
