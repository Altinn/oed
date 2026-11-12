"""Generate the supporting draw.io diagrams in docs/ (same visual language as oed.drawio).

Usage: python docs/tools/gen_more.py docs
Overwrites the .drawio files it generates; see docs/tools/render.sh.
"""
import os
import sys
from xml.sax.saxutils import quoteattr

OUT = sys.argv[1]
FONT = "fontFamily=Helvetica;"
INK = "light-dark(#1e293b,#d1d9e0)"

CONTAINER = (
    "swimlane;html=1;startSize=50;rounded=1;absoluteArcSize=1;arcSize=18;swimlaneLine=0;"
    "fillColor=light-dark(#e2e8f0,#21262d);swimlaneFillColor=light-dark(#f8fafc,#161b22);"
    "strokeColor=light-dark(#cbd5e1,#30363d);fontColor=light-dark(#0f172a,#e6edf3);"
    "fontStyle=1;fontSize=18;container=1;collapsible=0;align=left;spacingLeft=24;" + FONT
)
OURS = (
    "rounded=1;whiteSpace=wrap;html=1;absoluteArcSize=1;arcSize=14;strokeWidth=1.5;"
    "fillColor=light-dark(#dbeafe,#0c2d48);strokeColor=light-dark(#3b82f6,#4c9be8);"
    "fontColor=light-dark(#0b3a6e,#cfe6ff);fontSize=15;" + FONT
)
THEIRS = (
    "rounded=1;whiteSpace=wrap;html=1;absoluteArcSize=1;arcSize=14;strokeWidth=1.5;"
    "fillColor=light-dark(#ffffff,#2d333b);strokeColor=light-dark(#94a3b8,#6e7681);"
    "fontColor=light-dark(#334155,#d1d9e0);fontSize=15;" + FONT
)
USER = (
    "shape=mxgraph.office.users.user;html=1;pointerEvents=1;strokeColor=none;aspect=fixed;"
    "fillColor=light-dark(#2072B8,#58a6ff);labelPosition=center;verticalLabelPosition=bottom;"
    "verticalAlign=top;align=center;fontSize=15;fontStyle=1;fontColor=light-dark(#0f172a,#e6edf3);" + FONT
)
STATE = (
    "rounded=1;whiteSpace=wrap;html=1;absoluteArcSize=1;arcSize=28;strokeWidth=1.5;"
    "fillColor=light-dark(#f1f5f9,#21262d);strokeColor=light-dark(#64748b,#8b949e);"
    f"fontColor={INK};fontSize=16;fontStyle=1;" + FONT
)
STATE_OK = STATE.replace("fillColor=light-dark(#f1f5f9,#21262d);strokeColor=light-dark(#64748b,#8b949e);",
                         "fillColor=light-dark(#dcfce7,#0f2e1a);strokeColor=light-dark(#22c55e,#3fb950);")
STATE_BAD = STATE.replace("fillColor=light-dark(#f1f5f9,#21262d);strokeColor=light-dark(#64748b,#8b949e);",
                          "fillColor=light-dark(#fee2e2,#3b1219);strokeColor=light-dark(#ef4444,#f85149);")
START = "ellipse;html=1;strokeColor=none;fillColor=light-dark(#334155,#c9d1d9);"
END = ("ellipse;shape=doubleEllipse;html=1;strokeWidth=2;fillColor=light-dark(#334155,#c9d1d9);"
       "strokeColor=light-dark(#334155,#c9d1d9);")
EDGE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jumpStyle=arc;jumpSize=12;"
    "endArrow=blockThin;endFill=1;endSize=8;strokeWidth=1.5;"
    "strokeColor=light-dark(#64748b,#8b949e);fontSize=13;fontColor=light-dark(#334155,#c9d1d9);"
    "labelBackgroundColor=light-dark(#ffffff,#0d1117);exitPerimeter=0;entryPerimeter=0;" + FONT
)
MSG = (
    "html=1;endArrow=blockThin;endFill=1;endSize=8;strokeWidth=1.5;rounded=0;"
    "strokeColor=light-dark(#475569,#8b949e);fontSize=13;"
    f"fontColor={INK};verticalAlign=bottom;spacingBottom=2;labelBackgroundColor=none;" + FONT
)
REPLY = MSG + "dashed=1;endArrow=open;endFill=0;"
LIFELINE = "html=1;endArrow=none;dashed=1;dashPattern=4 4;strokeWidth=1;strokeColor=light-dark(#94a3b8,#6e7681);"
TEXT = f"text;html=1;align=left;verticalAlign=middle;whiteSpace=nowrap;fontSize=13;fontColor={INK};" + FONT
PHASE = "rounded=1;absoluteArcSize=1;arcSize=14;html=1;strokeColor=none;fillColor=light-dark(#eff6ff,#0f1b2a);"
PHASE_TITLE = ("text;html=1;align=left;verticalAlign=top;fontSize=14;fontStyle=1;"
               "fontColor=light-dark(#1d4ed8,#79c0ff);" + FONT)
FRAME = "rounded=0;html=1;fillColor=none;strokeWidth=1;strokeColor=light-dark(#64748b,#8b949e);"
FRAME_TAB = (f"text;html=1;align=left;verticalAlign=middle;fontSize=13;fontColor={INK};"
             "fillColor=light-dark(#e2e8f0,#30363d);spacingLeft=8;" + FONT)
FRAME_SPLIT = "html=1;endArrow=none;dashed=1;strokeWidth=1;strokeColor=light-dark(#64748b,#8b949e);"
NOTE = ("rounded=0;whiteSpace=wrap;html=1;fillColor=light-dark(#fefce8,#2b2a1a);"
        f"strokeColor=light-dark(#e5d97a,#5c5a3a);fontColor={INK};fontSize=13;" + FONT)


def label(name, kind=None):
    return name if kind is None else f'{name}<br><span style="font-size:12px;">{kind}</span>'


class Diagram:
    def __init__(self):
        self.cells = []
        self.geo = {}
        self.seq = 0

    def _id(self, prefix="c"):
        self.seq += 1
        return f"{prefix}{self.seq}"

    def vertex(self, value, style, x, y, w, h, id=None, parent="1"):
        id = id or self._id("v")
        px, py = self.geo[parent][:2] if parent in self.geo else (0, 0)
        self.geo[id] = (x, y, w, h)
        self.cells.append(
            f'<mxCell id={quoteattr(id)} value={quoteattr(value)} style={quoteattr(style)} vertex="1" '
            f'parent={quoteattr(parent)}><mxGeometry x="{x - px}" y="{y - py}" width="{w}" height="{h}" '
            f'as="geometry"/></mxCell>')
        return id

    def at(self, id, fx, fy):
        x, y, w, h = self.geo[id]
        return x + fx * w, y + fy * h

    def edge(self, src, tgt, value="", exit=None, entry=None, points=(), style=EDGE, label_pos=None):
        s = style
        if exit:
            s += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            s += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        pts = "".join(f'<mxPoint x="{round(x, 2)}" y="{round(y, 2)}"/>' for x, y in points)
        gx = f' x="{label_pos}"' if label_pos is not None else ""
        self.cells.append(
            f'<mxCell id="{self._id("e")}" value={quoteattr(value)} style={quoteattr(s)} edge="1" parent="1" '
            f'source={quoteattr(src)} target={quoteattr(tgt)}><mxGeometry relative="1"{gx} as="geometry">'
            f'<Array as="points">{pts}</Array></mxGeometry></mxCell>')

    def free(self, p1, p2, value="", style=MSG, points=()):
        pts = "".join(f'<mxPoint x="{round(x, 2)}" y="{round(y, 2)}"/>' for x, y in points)
        self.cells.append(
            f'<mxCell id="{self._id("e")}" value={quoteattr(value)} style={quoteattr(style)} edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry"><mxPoint x="{p1[0]}" y="{p1[1]}" as="sourcePoint"/>'
            f'<mxPoint x="{p2[0]}" y="{p2[1]}" as="targetPoint"/><Array as="points">{pts}</Array>'
            f'</mxGeometry></mxCell>')

    def save(self, name, diagram_id):
        xml = (
            '<mxfile host="app.diagrams.net">\n'
            f'  <diagram name="Page-1" id="{diagram_id}">\n'
            '    <mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            'page="0" pageScale="1" math="0" shadow="0">\n'
            '      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
            + "".join(f"        {c}\n" for c in self.cells)
            + "      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n")
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(xml)


class Sequence(Diagram):
    """Sequence diagram: participants across the top, numbered messages top to bottom."""
    COL, BW, BH = 210, 176, 58

    def __init__(self, parts):
        super().__init__()
        self.back, self.mid, self.front = [], [], []
        self.x = {}
        self.parts = parts
        for i, (key, _, _) in enumerate(parts):
            self.x[key] = 20 + self.BW / 2 + i * self.COL
        self.y = self.BH + 56
        self.n = 0
        self.frames = []

    def _into(self, layer, fn, *a, **k):
        saved = self.cells
        self.cells = layer
        fn(*a, **k)
        self.cells = saved

    def msg(self, a, b, text, reply=False):
        self.n += 1
        lines = text.count("<br>")
        self.y += 15 * lines
        self._into(self.front, self.free, (self.x[a], self.y), (self.x[b], self.y),
                   f"{self.n}. {text}", REPLY if reply else MSG)
        self.y += 46

    def self_msg(self, a, text):
        self.n += 1
        x, y = self.x[a], self.y - 8
        self._into(self.front, self.free, (x, y), (x + 4, y + 22), "", MSG,
                   points=[(x + 34, y), (x + 34, y + 22)])
        lines = text.count("<br>") + 1
        self._into(self.front, self.vertex, f"{self.n}. {text}", TEXT, x + 42, y - 4, 420, 16 * lines + 14)
        self.y += 54 + 16 * (lines - 1)

    def note(self, a, b, text):
        lines = text.count("<br>") + 1
        h = 18 * lines + 12
        x1, x2 = self.x[a] - self.BW / 2, self.x[b] + self.BW / 2
        self._into(self.front, self.vertex, text, NOTE, x1, self.y - 18, x2 - x1, h)
        self.y += h + 24

    def phase(self, title):
        self._phase = (title, self.y)
        self.y += 30

    def end_phase(self):
        title, y0 = self._phase
        x1 = 20 - 12
        x2 = self.x[self.parts[-1][0]] + self.BW / 2 + 12
        self._into(self.back, self.vertex, "", PHASE, x1, y0 - 26, x2 - x1, self.y - y0 + 6)
        self._into(self.back, self.vertex, title, PHASE_TITLE, x1 + 14, y0 - 22, 600, 24)
        self.y += 24

    def frame(self, a, b, kind, cond):
        self.frames.append([a, b, kind, cond, self.y, []])
        self.y += 34

    def split(self, cond):
        self.frames[-1][5].append((self.y, cond))
        self.y += 34

    def end_frame(self):
        a, b, kind, cond, y0, splits = self.frames.pop()
        x1, x2 = self.x[a] - self.BW / 2 + 6, self.x[b] + self.BW / 2 - 6
        y1 = self.y - 18
        self._into(self.mid, self.vertex, "", FRAME, x1, y0 - 22, x2 - x1, y1 - y0 + 22)
        self._into(self.mid, self.vertex, f"<b>{kind}</b>&nbsp; [{cond}]", FRAME_TAB, x1, y0 - 22, 360, 24)
        for sy, sc in splits:
            self._into(self.mid, self.free, (x1, sy - 14), (x2, sy - 14), "", FRAME_SPLIT)
            self._into(self.mid, self.vertex, f"[{sc}]", TEXT, x1 + 8, sy - 12, 400, 22)
        self.y += 10

    def finish(self):
        end_y = self.y + 4
        for key, text, kind in self.parts:
            cx = self.x[key]
            if kind == "actor":
                self.vertex(text, USER, cx - 20, 0, 40, 43)
                top = self.BH + 4
            else:
                self.vertex(text, OURS if kind == "ours" else THEIRS, cx - self.BW / 2, 0, self.BW, self.BH)
                top = self.BH
            self.free((cx, top), (cx, end_y), "", LIFELINE)
        self.cells = self.back + self.mid + self.cells + self.front


# --------------------------------------------------------------------------------------------
# 1. Estate lifecycle
s = Sequence([
    ("DA", "Domstoladministrasjonen<br>(DA)", "theirs"),
    ("FP", label("Feedpoller og proxy", "Azure Function"), "ours"),
    ("EV", label("OED Events", "Altinn Studio app"), "ours"),
    ("AE", "Altinn Events", "theirs"),
    ("OED", label("<b>Digitalt Dødsbo (OED)</b>", "Altinn Studio app"), "ours"),
    ("AZ", label("Authz", "Web-API"), "ours"),
    ("TQ", label("TaskQueue", "i OED"), "ours"),
    ("KORR", "Altinn Korrespondanse", "theirs"),
    ("ARV", "Arving", "actor"),
    ("PP", label("Privat skifteerklæring", "Altinn Studio app"), "ours"),
])
s.phase("Hent saksendringer fra DA")
s.msg("FP", "EV", "POST da-events/api/v1/process<br>hvert 5. min (sjeldnere om natten)")
s.msg("EV", "FP", "GET hendelsesliste")
s.msg("FP", "DA", "videresender (proxy)")
s.msg("DA", "FP", "hendelser", reply=True)
s.msg("FP", "EV", "hendelser", reply=True)
s.msg("EV", "FP", "GET objects/{caseId} per sak, videresendes til DA")
s.self_msg("EV", "filtrer bort saker med adressesperre (Folkeregisteret via DAN)")
s.msg("EV", "AE", "case-status-update-validated")
s.end_phase()
s.phase("Opprett eller oppdater dødsboet")
s.msg("AE", "OED", "POST api/cloudevents")
s.msg("AE", "AZ", "POST api/v1/eventhandler")
s.self_msg("AZ", "oppdater roller fra domstolen")
s.self_msg("OED", "opprett dødsbo-instans, oppdater arvinger og fullmakter")
s.msg("OED", "TQ", "EstateIsReadyCorrespondenceTaskV2 per arving<br>med fullmakt, planlagt til tilgangsdato")
s.end_phase()
s.phase("Varsle arvingene")
s.msg("TQ", "KORR", "«Dødsboet er klart»<br>(etter sjekk i Folkeregisteret)")
s.msg("KORR", "ARV", "melding i Altinn-innboksen", reply=True)
s.end_phase()
s.phase("Arvingen velger skifteform og sender inn")
s.msg("ARV", "OED", "velg skifteform (POST subapps/invoke)")
s.frame("AE", "PP", "alt", "privat skifte")
s.msg("OED", "PP", "opprett instans med forhåndsutfylte data")
s.msg("OED", "ARV", "videresend til skifteerklæringen", reply=True)
s.msg("ARV", "PP", "fyll ut, signer og send inn")
s.msg("PP", "AE", "app.instance.process.completed")
s.msg("AE", "OED", "POST api/cloudevents")
s.msg("OED", "TQ", "CollectPdfTask, PublishSubmittedEventTask,<br>kvittering (CorrespondenceTaskV2)")
s.self_msg("TQ", "kopier PDF-en fra underappen til dødsboet (Altinn Storage)")
s.msg("TQ", "AE", "v2.declaration-submitted")
s.split("offentlig skifte, uskifte eller lite dødsbo")
s.self_msg("OED", "lagre valget (ingen underapp)")
s.end_frame()
s.end_phase()
s.phase("DA henter erklæringen")
s.msg("AE", "DA", "POST fetcher/notify")
s.msg("DA", "OED", "GET …/subapps/{app}/{partyId}/{guid}/declaration")
s.msg("OED", "PP", "GET …/probatedeclaration")
s.msg("PP", "OED", "erklæring", reply=True)
s.msg("OED", "DA", "erklæring", reply=True)
s.end_phase()
s.y += 10
s.note("DA", "PP", "Senere endringer i saken (skifteattest utstedt, arving lagt til eller fjernet, feilført) "
                   "kommer samme vei (steg 1–13)<br>og gir nye meldinger, nye roller og eventuelt sletting av "
                   "underapp-instanser.")
s.finish()
s.save("livslop.drawio", "livslop")

# --------------------------------------------------------------------------------------------
# 2. TaskQueue: triggers, tasks, targets
d = Diagram()
NH, ROW0, STEP = 60, 86, 100
r = lambda i: ROW0 + i * STEP
TRIG_X, TASK_X, TGT_X = 0, 440, 1060
TRIG_W, TASK_W, TGT_W = 300, 360, 280
H_ALL = r(6.5) + NH + 30
c_trig = d.vertex("Utløsere i OED", CONTAINER, TRIG_X, 0, TRIG_W, H_ALL)
c_task = d.vertex("Oppgaver (oed.task_queue)", CONTAINER, TASK_X, 0, TASK_W, H_ALL)
c_tgt = d.vertex("Eksterne mål", CONTAINER, TGT_X, 0, TGT_W, H_ALL)
tn = lambda text, i: d.vertex(text, OURS, TRIG_X + 30, r(i), TRIG_W - 60, NH, parent=c_trig)
kn = lambda text, i: d.vertex(text, OURS, TASK_X + 30, r(i), TASK_W - 60, NH, parent=c_task)
gn = lambda text, i: d.vertex(text, THEIRS, TGT_X + 30, r(i), TGT_W - 60, NH, parent=c_tgt)

DA_ = tn(label("DA-sakshendelse", "DaCaseUpdateValidatedEventHandler"), 0)
DECL = tn(label("Skifteerklæring sendt inn", "POST cloudevents/declaration"), 1.5)
UNS = tn(label("Erklæring usignert", "DeclarationUnsignedEventHandler"), 2.5)
PROXY = tn(label("Fullmektig lagt til / fjernet", "ProbateProxyController"), 3.5)
SUB = tn(label("Underapp fullført", "AppInstanceProcessCompletedHandler"), 4.5)
STRT = tn("Oppstart av consumer", 6.5)

READY = kn(label("EstateIsReadyCorrespondenceTaskV2", "én per arving med fullmakt"), 0)
ARCH = kn("ArchiveTask", 1)
DEL = kn("DeleteInstanceTask", 2)
CORR = kn("CorrespondenceTaskV2", 3)
PDF = kn("CollectPdfTask", 4.5)
PUB = kn("PublishSubmittedEventTask", 5.5)
CLEAN = kn(label("TaskQueueCleanupTask", "planlegger seg selv på nytt"), 6.5)

FREG = gn("Folkeregisteret", 0)
ACOS = gn("Arkiv (ACOS)", 1)
KORR = gn(label("Altinn Korrespondanse", "via oed-messaging"), 3)
STOR = gn("Altinn Storage", 4.5)
EVTS = gn("Altinn Events", 5.5)

X_CORRBUS, X_SUBBUS, X_DABUS = TRIG_X + TRIG_W + 30, TRIG_X + TRIG_W + 60, TRIG_X + TRIG_W + 100
X_DELBUS, X_READYBUS = TASK_X + TASK_W + 60, TASK_X + TASK_W + 100
cy = lambda n, f=0.5: d.at(n, 0, f)[1]

d.edge(DA_, READY, exit=(1, 0.5), entry=(0, 0.5))
for tgt, f in ((ARCH, 0.5), (DEL, 0.5), (CORR, 0.3)):
    d.edge(DA_, tgt, exit=(1, 0.5), entry=(0, f), points=[(X_DABUS, cy(DA_)), (X_DABUS, cy(tgt, f))])
for src in (DECL, UNS, PROXY, SUB):
    d.edge(src, CORR, exit=(1, 0.5), entry=(0, 0.7), points=[(X_CORRBUS, cy(src)), (X_CORRBUS, cy(CORR, 0.7))])
d.edge(SUB, PDF, exit=(1, 0.5), entry=(0, 0.5))
d.edge(SUB, PUB, exit=(1, 0.5), entry=(0, 0.5), points=[(X_SUBBUS, cy(SUB)), (X_SUBBUS, cy(PUB))])
d.edge(STRT, CLEAN, exit=(1, 0.5), entry=(0, 0.5))

d.edge(READY, FREG, "lever avdøde fortsatt?", exit=(1, 0.3), entry=(0, 0.3))
d.edge(READY, ARCH, "legger inn", exit=(0.5, 1), entry=(0.5, 0), style=EDGE + "dashed=1;")
d.edge(READY, KORR, exit=(1, 0.8), entry=(0, 0.25),
       points=[(X_READYBUS, cy(READY, 0.8)), (X_READYBUS, cy(KORR, 0.25))])
d.edge(ARCH, ACOS, exit=(1, 0.5), entry=(0, 0.5))
_seg = [X_DELBUS - d.at(DEL, 1, 0.5)[0], cy(STOR, 0.25) - cy(DEL), d.at(STOR, 0, 0)[0] - X_DELBUS]
del_label_pos = round((_seg[0] + _seg[1] + _seg[2] / 2) / (sum(_seg) / 2) - 1, 3)  # middle of last segment
d.edge(DEL, STOR, "sletter underapp-instans", exit=(1, 0.5), entry=(0, 0.25),
       points=[(X_DELBUS, cy(DEL)), (X_DELBUS, cy(STOR, 0.25))], label_pos=del_label_pos)
d.edge(CORR, KORR, exit=(1, 0.6), entry=(0, 0.6))
d.edge(PDF, STOR, "henter PDF fra underapp,<br>lagrer på dødsboet", exit=(1, 0.75), entry=(0, 0.75), label_pos=0.42)
d.edge(PUB, EVTS, "DeclarationSubmittedV2", exit=(1, 0.5), entry=(0, 0.5))
d.save("taskqueue-oppgaver.drawio", "taskqueue-oppgaver")

# --------------------------------------------------------------------------------------------
# 3. TaskQueue: life of a row
d = Diagram()
Y, SW, SH = 200, 180, 56
start = d.vertex("", START, 0, Y + SH / 2 - 11, 22, 22)
plan = d.vertex("Planlagt", STATE, 130, Y, SW, SH)
run = d.vertex("Kjører", STATE, 500, Y, SW, SH)
wait = d.vertex("Venter", STATE, 500, 20, SW, SH)
dlq = d.vertex("DLQ", STATE_BAD, 500, 400, SW, SH)
done = d.vertex("Utført", STATE_OK, 900, Y, SW, SH)
end = d.vertex("", END, 1260, Y + SH / 2 - 13, 26, 26)
END_X = 1273
PLAN_X = 130 + SW / 2

d.edge(start, plan, "Schedule()", exit=(1, 0.5), entry=(0, 0.5))
d.edge(plan, run, "scheduled ≤ nå<br>FOR UPDATE SKIP LOCKED", exit=(1, 0.5), entry=(0, 0.5))
d.edge(run, done, "OK<br>executed = nå", exit=(1, 0.5), entry=(0, 0.5))
d.edge(done, end, "TaskQueueCleanupTask<br>etter 90 dager", exit=(1, 0.5), entry=(0, 0.5))
d.edge(run, wait, "feil<br>attempts + 1, last_error", exit=(0.25, 0), entry=(0.25, 1))
d.edge(wait, run, "etter 60 s", exit=(0.75, 1), entry=(0.75, 0))
d.edge(run, dlq, "10. forsøk feiler<br>scheduled = null", exit=(0.5, 1), entry=(0.5, 0))
d.edge(dlq, plan, "oed-admin PATCH<br>scheduled = ny tid, attempts = 0", exit=(0, 0.5), entry=(0.5, 1),
       points=[(PLAN_X, 400 + SH / 2)])
d.edge(dlq, end, "oed-admin DELETE", exit=(1, 0.5), entry=(0.5, 1), points=[(END_X, 400 + SH / 2)])
d.edge(plan, end, "Cancel() / oed-admin DELETE (raden slettes)", exit=(0.5, 0), entry=(0.5, 0),
       points=[(PLAN_X, -40), (END_X, -40)])
d.save("taskqueue-livslop.drawio", "taskqueue-livslop")

# --------------------------------------------------------------------------------------------
# 4. Auth: OED as service owner
s = Sequence([
    ("OED", label("<b>Digitalt Dødsbo (OED)</b>", "Altinn Studio app"), "ours"),
    ("MP", "Maskinporten", "theirs"),
    ("PLAT", "Altinn plattform<br>(token-veksling)", "theirs"),
    ("ST", "Altinn Storage /<br>Profile", "theirs"),
    ("AE", "Altinn Events", "theirs"),
    ("KORR", "Altinn Korrespondanse", "theirs"),
    ("AZ", label("Authz", "Web-API"), "ours"),
    ("DAN", "DAN / Skatteetaten", "theirs"),
])
s.msg("OED", "MP", "hent token (JWT-grant)")
s.msg("MP", "OED", "Maskinporten-token", reply=True)
s.y += 20
s.phase("Vekslet til Altinn-token (tjenesteeier)")
s.msg("OED", "PLAT", "veksle Maskinporten-token")
s.msg("PLAT", "OED", "Altinn-token", reply=True)
s.msg("OED", "ST", "instanser og data<br>[altinn:serviceowner/instances.read/write]")
s.msg("OED", "AE", "publiser og abonner<br>[altinn:events.publish, altinn:events.subscribe]")
s.msg("OED", "KORR", "send melding<br>[altinn:correspondence.write]")
s.end_phase()
s.phase("Maskinporten-token direkte")
s.msg("OED", "AZ", "roller og fullmektiger<br>[altinn:dd:authlookup, altinn:dd:internal]")
s.msg("OED", "DAN", "registeroppslag<br>[altinn:dataaltinnno/oed, folkeregister, skatteetaten]")
s.end_phase()
s.note("OED", "DAN", "Alle kall OED gjør mot Storage, går som tjenesteeier, også når en arving har startet handlingen.")
s.finish()
s.save("autentisering-tjenesteeier.drawio", "autentisering-tjenesteeier")

# --------------------------------------------------------------------------------------------
# 5. Auth: events and DA integration
s = Sequence([
    ("DA", "Domstoladministrasjonen<br>(DA)", "theirs"),
    ("FP", label("Feedpoller og proxy", "Azure Function"), "ours"),
    ("EV", label("OED Events", "Altinn Studio app"), "ours"),
    ("AE", "Altinn Events", "theirs"),
    ("OED", label("<b>Digitalt Dødsbo (OED)</b>", "Altinn Studio app"), "ours"),
    ("AZ", label("Authz", "Web-API"), "ours"),
])
s.phase("Saksendringer fra DA")
s.msg("FP", "EV", "POST da-events/api/v1/process<br>[Maskinporten, altinn:dd:internalevents]")
s.msg("EV", "FP", "GET hendelsesliste, objects/{caseId}<br>[funksjonsnøkkel]")
s.msg("FP", "DA", "videresender (proxy)<br>[Maskinporten, domstol:*]")
s.msg("EV", "AE", "publiser hendelse<br>[Altinn-token, vekslet]")
s.end_phase()
s.phase("Levering av hendelser")
s.msg("AE", "OED", "POST api/cloudevents?code=…<br>[hemmelighet i URL, ikke token]")
s.msg("AE", "AZ", "POST api/v1/eventhandler?auth=…<br>[hemmelighet i URL, ikke token]")
s.msg("AE", "DA", "POST fetcher/notify (declaration-submitted)")
s.end_phase()
s.phase("DA henter erklæringen")
s.msg("DA", "OED", "GET …/declaration<br>[Maskinporten, digdir:dd:probatedeclarations]")
s.end_phase()
s.note("DA", "AZ", "Abonnementene i Altinn Events opprettes av OED ved oppstart (Subscriptions/subscriptions.{miljø}.json).")
s.finish()
s.save("autentisering-hendelser.drawio", "autentisering-hendelser")
