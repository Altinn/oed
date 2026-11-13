"""Generate docs/oed.drawio for Altinn/oed with an orthogonal, crossing-minimised layout.

Every node, edge and label from the previous diagram is kept, with the same cell ids.
Coordinates are derived from the layout constants below, so spacing can be tuned in one place.

Usage: python docs/tools/gen.py docs/oed.drawio
Overwrites docs/oed.drawio; see docs/tools/render.sh.
"""
import sys
from xml.sax.saxutils import quoteattr

FONT = "fontFamily=Helvetica;"

CONTAINER = (
    "swimlane;html=1;startSize=56;rounded=1;absoluteArcSize=1;arcSize=20;swimlaneLine=0;"
    "fillColor=light-dark(#e2e8f0,#21262d);swimlaneFillColor=light-dark(#f8fafc,#161b22);"
    "strokeColor=light-dark(#cbd5e1,#30363d);fontColor=light-dark(#0f172a,#e6edf3);"
    "fontStyle=1;fontSize=20;container=1;collapsible=0;align=left;" + FONT
)
OURS = (
    "rounded=1;whiteSpace=wrap;html=1;absoluteArcSize=1;arcSize=16;strokeWidth=1.5;"
    "fillColor=light-dark(#dbeafe,#0c2d48);strokeColor=light-dark(#3b82f6,#4c9be8);"
    "fontColor=light-dark(#0b3a6e,#cfe6ff);fontSize=16;" + FONT
)
OURS_HUB = OURS.replace("strokeWidth=1.5;", "strokeWidth=3;") + "fontSize=18;"
OURS_DB = (
    "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;strokeWidth=1.5;"
    "fillColor=light-dark(#dbeafe,#0c2d48);strokeColor=light-dark(#3b82f6,#4c9be8);"
    "fontColor=light-dark(#0b3a6e,#cfe6ff);fontSize=16;" + FONT
)
THEIRS = (
    "rounded=1;whiteSpace=wrap;html=1;absoluteArcSize=1;arcSize=16;strokeWidth=1.5;"
    "fillColor=light-dark(#ffffff,#2d333b);strokeColor=light-dark(#94a3b8,#6e7681);"
    "fontColor=light-dark(#334155,#d1d9e0);fontSize=16;" + FONT
)
USER = (
    "shape=mxgraph.office.users.user;html=1;pointerEvents=1;strokeColor=none;aspect=fixed;"
    "fillColor=light-dark(#2072B8,#58a6ff);labelPosition=center;verticalLabelPosition=bottom;"
    "verticalAlign=top;align=center;fontSize=17;fontStyle=1;fontColor=light-dark(#0f172a,#e6edf3);" + FONT
)
EDGE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jumpStyle=arc;jumpSize=14;"
    "endArrow=blockThin;endFill=1;endSize=9;strokeWidth=1.5;"
    "strokeColor=light-dark(#64748b,#8b949e);fontSize=14;fontColor=light-dark(#334155,#c9d1d9);"
    "labelBackgroundColor=light-dark(#ffffff,#0d1117);exitPerimeter=0;entryPerimeter=0;" + FONT
)
LEGEND_TEXT = (
    "text;html=1;align=left;verticalAlign=middle;fontSize=15;"
    "fontColor=light-dark(#334155,#c9d1d9);" + FONT
)

# ---- layout ----
W, H = 230, 76            # node size
HUB_H = 96                # OED
PAD, HEADER = 40, 56      # container inner padding / title band
ROW_STEP = 160
TOP = 170                 # top of DD / Altinn 3 containers

DD_X = 0
DD_L = DD_X + PAD
DD_R = DD_L + W + 80
DD_W = DD_R + W + PAD - DD_X

ALT_X = DD_X + DD_W + 260  # channel between the two containers (room for edge labels right of the channels)
COL_A = ALT_X + PAD
COL_B = COL_A + W + 150
COL_C = COL_B + W + 110
ALT_W = COL_C + W + PAD - ALT_X

ROW = {i: TOP + HEADER + PAD + (i - 1) * ROW_STEP for i in range(1, 6)}
HUB_Y = ROW[2] - (HUB_H - H) // 2

ALT_H = ROW[4] + H + 44 - TOP
DD_H = ROW[5] + H + 44 - TOP

DOM_Y = TOP + ALT_H + 64
DOM_ROW = DOM_Y + HEADER + PAD
DOM_H = DOM_ROW + H + 40 - DOM_Y

DAN_Y = max(DOM_Y + DOM_H, TOP + DD_H) + 80
DAN_X, DAN_W = DD_X, ALT_X + ALT_W - DD_X
DAN_ROW = DAN_Y + HEADER + PAD
DAN_NW = 290
DAN_GAP = (DAN_W - 2 * PAD - 5 * DAN_NW) / 4

# channel x positions between DD and Altinn 3
CH_META, CH_DAN, CH_TQ = DD_X + DD_W + 35, DD_X + DD_W + 70, DD_X + DD_W + 105
CH_AZ = DD_X + DD_W + 140  # Altinn Events -> Authz

cells = []
geo = {}


def label(name, kind=None):
    return name if kind is None else f'{name}<br><span style="font-size:13px;">{kind}</span>'


def vertex(id, value, style, x, y, w=W, h=H, parent="1"):
    px, py = geo[parent][:2] if parent in geo else (0, 0)
    geo[id] = (x, y, w, h)
    cells.append(
        f'<mxCell id={quoteattr(id)} value={quoteattr(value)} style={quoteattr(style)} '
        f'vertex="1" parent={quoteattr(parent)}>'
        f'<mxGeometry x="{x - px}" y="{y - py}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    )


def at(id, fx, fy):
    x, y, w, h = geo[id]
    return x + fx * w, y + fy * h


def edge(id, src, tgt, value="", exit=None, entry=None, points=(), both=False, label_pos=None):
    style = EDGE
    if both:
        style += "startArrow=blockThin;startFill=1;startSize=9;"
    if exit:
        style += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
    if entry:
        style += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
    pts = "".join(f'<mxPoint x="{round(x, 2)}" y="{round(y, 2)}"/>' for x, y in points)
    geo_x = f' x="{label_pos}"' if label_pos is not None else ""
    cells.append(
        f'<mxCell id={quoteattr(id)} value={quoteattr(value)} style={quoteattr(style)} edge="1" '
        f'parent="1" source={quoteattr(src)} target={quoteattr(tgt)}>'
        f'<mxGeometry relative="1"{geo_x} as="geometry"><Array as="points">{pts}</Array></mxGeometry></mxCell>'
    )


def title(spacing_left):
    return CONTAINER + f"spacingLeft={spacing_left};"


# ---- ids from the previous diagram ----
DD, ALTINN, DOMSTOL, DAN = (f"mRQTRkCE-5xtZGmJmvK6-{n}" for n in (20, 37, 53, 6))
n = lambda k: f"mRQTRkCE-5xtZGmJmvK6-{k}"
BRUKER, PRIVAT = "b7xdcVu81Tnr1B8ahJKg-2", "privat-skifte-1"
KORR, AUT, INNBOKS, OED, MELDING = n(5), n(38), n(40), n(42), n(41)
LEGACY, OED_EVENTS, EVENTS = n(44), n(43), n(39)
TQ, AUTHZ, META, FEED, ADMIN = n(27), n(26), n(25), n(28), n(29)
HENDELSER, DA = n(54), n(55)

APP3 = "Altinn Studio app"

# ---- legend ----
vertex("legend-ours", "", OURS, DD_X, 8, 38, 24)
vertex("legend-ours-text", "Digitalt Dødsbo-teamet er ansvarlig", LEGEND_TEXT, DD_X + 52, 5, 320, 30)
vertex("legend-theirs", "", THEIRS, DD_X, 52, 38, 24)
vertex("legend-theirs-text", "Annen eier", LEGEND_TEXT, DD_X + 52, 49, 320, 30)

# ---- Digitalt Dødsbo ----
vertex(DD, "Digitalt Dødsbo", title(28), DD_X, TOP, DD_W, DD_H)
vertex(n(23), label("Infrastructure", "Terraform"), OURS, DD_L, ROW[1], parent=DD)
vertex(n(22), label("E2E tester", "Playwright"), OURS, DD_L, ROW[2], parent=DD)
vertex(ADMIN, label("Admin", "Web-app"), OURS, DD_L, ROW[3], parent=DD)
vertex(n(21), label("Testdata", "Web-app"), OURS, DD_L, ROW[4], parent=DD)
vertex(n(24), label("Korrespondanse bibliotek", "NuGet-pakke"), OURS, DD_L, ROW[5], parent=DD)
vertex(TQ, label("TaskQueue", "PostgreSQL"), OURS_DB, DD_R, ROW[1], parent=DD)
vertex(AUTHZ, label("Authz", "Web-API"), OURS, DD_R, ROW[2], parent=DD)
vertex(META, label("Metadata database", "PostgreSQL"), OURS_DB, DD_R, ROW[3], parent=DD)
vertex(FEED, label("Feedpoller og proxy", "Azure Function"), OURS, DD_R, ROW[4], parent=DD)

# ---- Altinn 3 ----
vertex(ALTINN, "Altinn 3", title(28), ALT_X, TOP, ALT_W, ALT_H)
vertex(KORR, "Altinn Korrespondanse", THEIRS, COL_A, ROW[1], parent=ALTINN)
vertex(AUT, "Altinn Autorisasjon", THEIRS, COL_B, ROW[1], parent=ALTINN)
vertex(INNBOKS, "Innboks", THEIRS, COL_C, ROW[1], parent=ALTINN)
vertex(OED, label("<b>Digitalt Dødsbo (OED)</b>", APP3), OURS_HUB, COL_B, HUB_Y, h=HUB_H, parent=ALTINN)
vertex(MELDING, "Altinn Melding", THEIRS, COL_C, ROW[2], parent=ALTINN)
vertex(PRIVAT, label("Privat skifteerklæring", APP3), OURS, COL_A, ROW[3], parent=ALTINN)
vertex(LEGACY, label("Skifteerklæring (legacy)", APP3), OURS, COL_C, ROW[3], parent=ALTINN)
vertex(OED_EVENTS, label("OED Events", APP3), OURS, COL_A, ROW[4], parent=ALTINN)
vertex(EVENTS, "Altinn Events", THEIRS, COL_B, ROW[4], parent=ALTINN)

# ---- user, centred between Korrespondanse and Autorisasjon ----
BW, BH = 60, 65
bx = (at(KORR, 0.5, 0)[0] + at(AUT, 0.5, 0)[0]) / 2 - BW / 2
vertex(BRUKER, "Bruker", USER, bx, 18, BW, BH)

# ---- Domstoladministrasjonen (title centred between the two incoming edges) ----
dom_title_left = (COL_A + W / 2 + COL_B + W / 2) / 2 - 130 - ALT_X
vertex(DOMSTOL, "Domstoladministrasjonen", title(dom_title_left), ALT_X, DOM_Y, ALT_W, DOM_H)
vertex(HENDELSER, "Hendelsesliste", THEIRS, COL_A, DOM_ROW, parent=DOMSTOL)
vertex(DA, "DA fagsystem", THEIRS, COL_B, DOM_ROW, parent=DOMSTOL)

# ---- DAN ----
vertex(DAN, "DAN (data.altinn.no)", title(28), DAN_X, DAN_Y, DAN_W, DAN_ROW + 2 * H + 44 + PAD - DAN_Y)
dan = [
    (n(7), "Bits - Kundeforhold"), (n(9), "Bits - Kontotransaksjoner"), (n(8), "Bits - Kontodetaljer"),
    (n(15), "Enhetsregisteret - Virksomhetsinformasjon"), (n(13), "Løsøreregisteret - Ektepakt"),
    (n(14), "Folkeregisteret - FregPerson"), (n(11), "Kartverket - Grunnbok"),
    (n(12), "Norsk pensjon - NorskPensjon"), (n(10), "SVV - Kjøretoy"),
]
for i, (id, text) in enumerate(dan):
    row, col = divmod(i, 5)
    step = DAN_NW + DAN_GAP
    x = DAN_X + PAD + col * step + (step / 2 if row else 0)
    vertex(id, text, THEIRS, x, DAN_ROW + row * (H + 44), DAN_NW, H, parent=DAN)

# ---- edges ----
user_y = 18 + BH / 2
gap_r1_hub = (ROW[1] + H + HUB_Y) / 2           # between row 1 and the OED box
gap_hub_r3 = (HUB_Y + HUB_H + ROW[3]) / 2       # between the OED box and row 3

# user journey
edge(n(68), KORR, BRUKER, exit=(0.5, 0), entry=(0, 0.5), points=[(at(KORR, 0.5, 0)[0], user_y)])
edge(n(58), BRUKER, AUT, "Logger inn", exit=(1, 0.5), entry=(0.5, 0), points=[(at(AUT, 0.5, 0)[0], user_y)])
edge(n(45), AUT, INNBOKS, exit=(1, 0.5), entry=(0, 0.5))
edge(n(46), INNBOKS, MELDING, exit=(0.5, 1), entry=(0.5, 0))
edge(n(47), MELDING, OED, exit=(0, 0.5), entry=(1, 0.5))
edge(n(48), OED, AUT, "Autoriserer bruker", exit=(0.5, 0), entry=(0.5, 1))
edge(n(60), AUT, AUTHZ, "Henter roller", exit=(0.15, 1), entry=(0.5, 0),
     points=[(at(AUT, 0.15, 1)[0], gap_r1_hub), (at(AUTHZ, 0.5, 0)[0], gap_r1_hub)])

# OED -> Digitalt Dødsbo components
edge(n(59), OED, TQ, exit=(0, 0.25), entry=(1, 0.75),
     points=[(CH_TQ, at(OED, 0, 0.25)[1]), (CH_TQ, at(TQ, 1, 0.75)[1])])
edge(n(61), OED, AUTHZ, exit=(0, 0.5), entry=(1, 0.5))
edge(n(66), OED, META, exit=(0, 0.75), entry=(1, 0.5),
     points=[(CH_META, at(OED, 0, 0.75)[1]), (CH_META, at(META, 1, 0.5)[1])])
edge(n(36), ADMIN, META, exit=(1, 0.5), entry=(0, 0.5))
edge(n(67), TQ, KORR, "Send korrespondanse", exit=(1, 0.25), entry=(0, 0.25))

# OED -> DAN
edge("XrT4xMYESNk_eO4uSYzE-4", OED, DAN, exit=(0, 0.92), entry=(round((CH_DAN - DAN_X) / DAN_W, 4), 0),
     points=[(CH_DAN, at(OED, 0, 0.92)[1]), (CH_DAN, DAN_Y)])

# declarations and events
edge("ZwzPzqGa1WCbiXD-ek_v-1", OED, PRIVAT, exit=(0.15, 1), entry=(0.5, 0),
     points=[(at(OED, 0.15, 1)[0], gap_hub_r3), (at(PRIVAT, 0.5, 0)[0], gap_hub_r3)])
edge("ZwzPzqGa1WCbiXD-ek_v-2", PRIVAT, EVENTS, exit=(1, 0.5), entry=(0.25, 0),
     points=[(at(EVENTS, 0.25, 0)[0], at(PRIVAT, 1, 0.5)[1])])
edge(n(50), OED, LEGACY, exit=(0.85, 1), entry=(0.5, 0),
     points=[(at(OED, 0.85, 1)[0], gap_hub_r3), (at(LEGACY, 0.5, 0)[0], gap_hub_r3)])
edge(n(51), LEGACY, EVENTS, "Publiser app-event", exit=(0.5, 1), entry=(1, 0.25),
     points=[(at(LEGACY, 0.5, 1)[0], at(EVENTS, 1, 0.25)[1])])
edge(n(52), EVENTS, OED, both=True, exit=(0.5, 0), entry=(0.5, 1))
# Authz subscribes to the same events and sets the heirs' roles from them; OED only sets proxy roles
gap_r3_r4 = (ROW[3] + H + ROW[4]) / 2
gap_az_meta = (ROW[2] + H + ROW[3]) / 2
edge("events-authz", EVENTS, AUTHZ, exit=(0.1, 0), entry=(0.5, 1),
     points=[(at(EVENTS, 0.1, 0)[0], gap_r3_r4), (CH_AZ, gap_r3_r4),
             (CH_AZ, gap_az_meta), (at(AUTHZ, 0.5, 1)[0], gap_az_meta)])
def right_of_channels(x_start, x_end):
    """Relative label position that centres a straight edge's label between the channels and Altinn 3."""
    want = (CH_TQ + 10 + COL_A) / 2
    return round((want - (x_start + x_end) / 2) / ((x_end - x_start) / 2), 3)


feed_r, ev_l = at(FEED, 1, 0.5)[0], at(OED_EVENTS, 0, 0.5)[0]
edge(n(64), FEED, OED_EVENTS, "Trigger hvert 5. minutt", exit=(1, 0.25), entry=(0, 0.25),
     label_pos=right_of_channels(feed_r, ev_l))
edge(n(49), OED_EVENTS, EVENTS, "Publiser CloudEvents", exit=(1, 0.5), entry=(0, 0.5))

# Domstoladministrasjonen
# OED Events reads the DA feed through the proxy function in oed-feedpoller
edge(n(65), OED_EVENTS, FEED, "Henter hendelsesliste", exit=(0, 0.75), entry=(1, 0.75),
     label_pos=right_of_channels(ev_l, feed_r))
fx, fy = at(FEED, 0.5, 1)
hx, hy = at(HENDELSER, 0, 0.5)
seg_v, seg_h = hy - fy, hx - fx
edge("feedpoller-proxy-da", FEED, HENDELSER, "Videresender (proxy)", exit=(0.5, 1), entry=(0, 0.5),
     points=[(fx, hy)], label_pos=round((seg_v + (CH_TQ - fx) + (hx - CH_TQ) / 2) / ((seg_v + seg_h) / 2) - 1, 3))
edge(n(63), EVENTS, DA, exit=(0.5, 1), entry=(0.5, 0))

ch_right = ALT_X + ALT_W - 20
da_y = at(DA, 1, 0.5)[1]
hub_entry_y = HUB_Y + HUB_H + 16
da_pts = [(ch_right, da_y), (ch_right, hub_entry_y), (at(OED, 0.95, 1)[0], hub_entry_y)]
seg = [ch_right - at(DA, 1, 0.5)[0], da_y - hub_entry_y, ch_right - at(OED, 0.95, 1)[0], 16]
half = sum(seg) / 2
edge(n(62), DA, OED, "Henter skifteerklæring", exit=(1, 0.5), entry=(0.95, 1),
     points=da_pts, label_pos=round(seg[0] / 2 / half - 1, 3))

xml = (
    '<mxfile host="app.diagrams.net">\n'
    '  <diagram name="Page-1" id="jPhfbrwJ7afIqJezLMGa">\n'
    '    <mxGraphModel dx="1800" dy="1600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
    'arrows="1" fold="1" page="0" pageScale="1" pageWidth="1800" pageHeight="1600" math="0" shadow="0">\n'
    '      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
    + "".join(f"        {c}\n" for c in cells)
    + "      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n"
)
with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
    f.write(xml)
