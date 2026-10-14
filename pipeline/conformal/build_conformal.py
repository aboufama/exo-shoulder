"""Conformal D4 shoulder (average body): links shaped to the skin, joints as low as the skin allows.

Input: envelope.json (avg/conformal.py export_envelope): design, per-link skin-side envelope over its footprint, joint
heights, rest spare angle. Every joint axis passes through the GH centre; each joint stack sits at its own height:
  lower member: flat G2 plate, skin-side face at z_J, 5.0 thick, integral Ø10 pin (DIN 509 relief, M4 tap)
  washer A GTM-1018-010 | upper member: flat G2 plate 5.5 thick, Ø12 bore + GSM-1012-05 sleeve | washer B
  cap: one curvature-continuous dome (no flat land) clamped by an M4 ULP screw
Links: plate (hub disc + stub) -> lofted ribbon whose underside follows the envelope along the arc and tilts with the
skin across its width (G2 rounded-rectangle section) -> plate. J4's lower member is the user's BOTTOM (built in
build_full_conformal.py, flat + one machinable jog); the base is a flat plate with a mounting tab.
Frame: canonical pose-0 thorax frame (mm, origin GH); written as STEP + the D4 part list for the full assembly.

    python3 build_conformal.py envelope.json OUTDIR
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
from scipy.interpolate import UnivariateSpline
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "shoulder-d4"))
import g2cad as G
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Fuse
from OCP.TopTools import TopTools_ListOfShape

ENV = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "envelope.json")))
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else HERE); os.makedirs(OUT, exist_ok=True)
D_ = ENV["design"]; order = tuple(D_.get("order", (1, 1, 0)))
P = {k: np.array(v) for k, v in ENV["rest_pins"].items()}                 # rest pose pins (scapula = thorax frame)
for k in P: P[k] = P[k] / np.linalg.norm(P[k])
T_LO, T_UP, T_W, T_CAP = 5.0, 5.5, 1.0, 3.0
HUB_R, HW, E_LO, E_UP = 17.0, 7.0, 1.5, 1.2
PIN_D, SLV_OD, SLV_L, WASH_ID, WASH_OD = 10.0, 12.0, 5.0, 10.0, 18.0
SCR_HEAD_D, SCR_HEAD_H = 7.1, 2.0
ZJ4 = ENV["z_j4"]; T_BOT = 6.5                                            # BOTTOM's hub (lower member at J4)

def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def V(p): return cq.Vector(*map(float, p))
def fuzzy_fuse(a, b, tol=0.1):
    args = TopTools_ListOfShape(); args.Append(a.wrapped); tools = TopTools_ListOfShape(); tools.Append(b.wrapped)
    f = BRepAlgoAPI_Fuse(); f.SetArguments(args); f.SetTools(tools); f.SetFuzzyValue(tol); f.Build(); return cq.Shape.cast(f.Shape())
def frame_of(axis):
    n = unit(axis); x = unit(np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])); return n, x, np.cross(n, x)

# ---------------------------------------------------------------- joint heights (lower face z_J) and roles
links = [("b", "c2"), ("c2", "c3"), ("c3", "u4")]
envs = [np.array(e) for e in ENV["env"]]; fps = ENV["fp"]           # lowest feasible envelope (ramp-limited by the evaluator)
CAPS = [np.array(e) for e in ENV["caps"]]
def hub_env(k, end): kind = np.array(fps[k]["kind"]); return float(CAPS[k][kind == 1 + end].max())   # joint faces as scored (caps)
# lower-member flag per (link, end); J1: base|l1, J2: l1|l2, J3: l2|l3, J4: BOTTOM|l3
lower = {(0, 0): order[0] == 0, (0, 1): order[1] == 1, (1, 0): order[1] == 0, (1, 1): order[2] == 1, (2, 0): order[2] == 0, (2, 1): False}
ZJ = {}
ZJ[1] = hub_env(0, 0); ZJ[2] = max(hub_env(0, 1), hub_env(1, 0)); ZJ[3] = max(hub_env(1, 1), hub_env(2, 0)); ZJ[4] = ZJ4
# J1 is fixed to the scapula and its stack is axisymmetric: lift it until the whole flat disc (lower face + edge round)
# clears the rest skin band by 0.5 mm (>= 3.5 mm off the skin) in every trunk bin. The evaluator samples hub rims at
# R_REF = 100 mm, i.e. inside the true rim of a disc ~65 mm out, so its J1 face can sit a little low.
sys.path.insert(0, os.path.join(HERE, "..", "avg")); _c = os.getcwd(); os.chdir(os.path.join(HERE, "..", "avg"))
import conformal as CFm, design_search as DSm; os.chdir(_c)
def disc_lift(axis, z0, margin=0.5):
    n, x, y = frame_of(axis); ph = np.radians(np.arange(0, 360, 3)); r_flat = HUB_R - E_LO; need = 0.0
    for r_ in np.r_[np.linspace(0, r_flat, 9), r_flat + np.linspace(0, E_LO, 5)[1:]]:
        rise = E_LO - math.sqrt(max(E_LO ** 2 - max(0.0, r_ - r_flat) ** 2, 0.0))     # circular edge round
        Pp = r_ * (np.cos(ph)[:, None] * x + np.sin(ph)[:, None] * y)
        for eb_ in range(CFm.T_R1C.shape[0]):
            Rs_ = DSm.scapula(float(CFm.ELEVS[eb_])); lo_map = CFm.T_R1C[eb_].ravel()
            for dz in np.arange(need, 20.0, 0.1):
                X = Pp + (z0 + rise + dz) * n; r = np.linalg.norm(X, axis=1)
                if (r >= lo_map[CFm.pix((X / r[:, None]) @ Rs_.T)] + margin).all(): need = dz; break
    return float(need)
J1_LIFT = disc_lift(P["b"], ZJ[1]); ZJ[1] += J1_LIFT
print(f"J1 disc lift {J1_LIFT:.1f} mm -> face {ZJ[1]:.1f}", flush=True)
AX = {1: P["b"], 2: P["c2"], 3: P["c3"], 4: P["u4"]}
def face_of(k, end):
    J = k + 1 + end
    if J == 4: return ZJ4 + T_BOT + T_W                                    # l3 sits on washer A over BOTTOM's hub
    return ZJ[J] if lower[(k, end)] else ZJ[J] + T_LO + T_W
def thick_of(k, end): return T_LO if (lower[(k, end)] and k + 1 + end != 4) else T_UP

# ---------------------------------------------------------------- link builder
def section_outline(width, t, e, n=160):
    """G2 rounded rectangle (centred), corners of size e; returns (n,2) closed outline (x = across, y = up)"""
    hw, ht = width / 2, t / 2; segs = []
    corners = [((hw, -ht + e), (0, 1.0), (hw - e, ht), (-1.0, 0)), ((-hw + e, ht), (-1.0, 0), (-hw, ht - e), (0, -1.0)),
               ((-hw, -ht + e), (0, -1.0), (-hw + e, -ht), (1.0, 0)), ((hw - e, -ht), (1.0, 0), (hw, -ht + e), (0, 1.0))]
    # walk: right wall up, top-right corner, top, top-left corner, left wall down, bottom-left, bottom, bottom-right
    pts = []
    def line(a, b, m): return [np.array(a) + (np.array(b) - np.array(a)) * t_ for t_ in np.linspace(0, 1, m, endpoint=False)]
    def corner(a, ta, b, tb, m):
        cp = G.g2_blend(np.r_[a, 0], np.r_[ta, 0], 0.0, np.r_[tb, 0], np.r_[b, 0], np.r_[tb, 0], 0.0, -np.r_[ta, 0], frac=0.3)
        cp = np.array(cp)[:, :2]; from math import comb
        ts = np.linspace(0, 1, m, endpoint=False); return [sum(comb(5, i) * (1 - u) ** (5 - i) * u ** i * cp[i] for i in range(6)) for u in ts]
    pts += line((hw, -ht + e), (hw, ht - e), 8); pts += corner((hw, ht - e), (0, 1), (hw - e, ht), (-1, 0), 14)
    pts += line((hw - e, ht), (-hw + e, ht), 20); pts += corner((-hw + e, ht), (-1, 0), (-hw, ht - e), (0, -1), 14)
    pts += line((-hw, ht - e), (-hw, -ht + e), 8); pts += corner((-hw, -ht + e), (0, -1), (-hw + e, -ht), (1, 0), 14)
    pts += line((-hw + e, -ht), (hw - e, -ht), 20); pts += corner((hw - e, -ht), (1, 0), (hw, -ht + e), (0, 1), 14)
    pts = np.array(pts); seg = np.linalg.norm(np.diff(np.r_[pts, pts[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    tt = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(tt, sl, np.r_[pts[:, k], pts[0, k]]) for k in range(2)]).T

def chain_loop(edges, n, ref_u, ref_v):
    segs = [np.array([e.positionAt(t).toTuple() for t in np.linspace(0, 1, 30)]) for e in edges]; loop = segs.pop(0)
    while segs:
        end = loop[-1]; k = min(range(len(segs)), key=lambda i: min(np.linalg.norm(segs[i][0] - end), np.linalg.norm(segs[i][-1] - end)))
        s = segs.pop(k); s = s[::-1] if np.linalg.norm(s[-1] - end) < np.linalg.norm(s[0] - end) else s; loop = np.r_[loop, s[1:]]
    if np.linalg.norm(loop[-1] - loop[0]) < 1e-3: loop = loop[:-1]
    c = loop.mean(0); x2, y2 = (loop - c) @ ref_u, (loop - c) @ ref_v
    if 0.5 * np.sum(x2 * np.roll(y2, -1) - np.roll(x2, -1) * y2) < 0: loop = loop[::-1]
    seg = np.linalg.norm(np.diff(np.r_[loop, loop[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    tt = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(tt, sl, np.r_[loop[:, k], loop[0, k]]) for k in range(3)]).T

def hub_plate(axis, toward, z0, t, e, lateral, stub=HUB_R + 7.0, cut_at=HUB_R + 6.0, extra=None):
    """flat G2 plate (planes z0..z0+t along axis): hub disc + stub toward `toward` (cut flat at cut_at mm).
    The section loop is returned counter-clockwise in (lateral, axis) so every loft section shares one handedness."""
    n = unit(axis); d = unit(toward - (toward @ n) * n); e2 = np.cross(n, d)
    def sdf2(x, y):
        d1 = np.hypot(x, y) - HUB_R; d2 = np.maximum(np.abs(y) - HW, np.maximum(x - stub - 6, -x)); k = 8.0
        h = np.maximum(k - np.abs(d1 - d2), 0) / k; s = np.minimum(d1, d2) - h ** 3 * k / 6
        if extra is not None: s = np.minimum(s, extra(x, y))
        return s
    ext = (-HUB_R - 6, stub + 10, -HUB_R - 6, HUB_R + 6) if extra is None else (-HUB_R - 6, 90, -60, 60)
    plate = G.flat_plate(sdf2, [0, 0, 0], d, e2, z0, z0 + t, e, ext)
    if cut_at is not None:
        cutp = cq.Workplane(cq.Plane(origin=tuple(n * z0 + cut_at * d), xDir=tuple(e2), normal=tuple(d))).rect(400, 400).extrude(200).val()
        plate = plate.cut(cutp)
        sec = cq.Shape.cast(BRepAlgoAPI_Section(plate.wrapped, cq.Face.makePlane(400, 400, basePnt=V(n * z0 + cut_at * d), dir=V(d)).wrapped).Shape())
        lat = unit(lateral - (lateral @ d) * d - (lateral @ n) * n)
        loop = chain_loop(sec.Edges(), 160, lat, n)
        return plate, loop, (n, d, lat)
    return plate, None, (n, d, e2)

def upper_spline(s, y, smooth=2.0):
    """smooth curve through y(s) that is never below the data"""
    sp = UnivariateSpline(s, y, k=3, s=smooth * len(s))
    f = sp(s); lift = max(0.0, float((y - f).max())); return lambda q: sp(q) + lift + 0.4

DEBUG = {}
def planform_halfwidth(x, stub_len=60.0, k=8.0):
    """half-width of the hub planform (disc HUB_R + strip HW, cubic smooth-min waist) at distance x from the pin"""
    def sdf2(xx, yy):
        d1 = np.hypot(xx, yy) - HUB_R; d2 = np.maximum(np.abs(yy) - HW, np.maximum(xx - stub_len, -xx))
        h = np.maximum(k - np.abs(d1 - d2), 0) / k; return np.minimum(d1, d2) - h ** 3 * k / 6
    lo, hi = 0.0, HUB_R + 6
    if sdf2(x, 0.0) >= 0: return 0.0
    for _ in range(40):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if sdf2(x, m) < 0 else (lo, m)
    return lo

def build_link(k):
    """one continuous loft, tip to tip: across plate A (flat, widths from the disc + G2 waist), along the ribbon
    (skin-following height, gentle ramps off the plates), across plate B"""
    A_, B_ = links[k]; a, b = P[A_], P[B_]
    ya = unit(b - (b @ a) * a); Fm = np.c_[a, ya, np.cross(a, ya)]; LAT = Fm[:, 2]
    th = math.acos(np.clip(a @ b, -1, 1)); fp = fps[k]; kind = np.array(fp["kind"]); s_ = np.array(fp["s"]); w_ = np.array(fp["w"]); e = envs[k]
    m0 = kind == 0; rows = {}
    for w in (-HW, 0.0, HW):
        m = m0 & (np.abs(w_ - w) < 1e-6); o = np.argsort(s_[m]); rows[w] = (s_[m][o], e[m][o])
    fC = upper_spline(*rows[0.0]); fL = upper_spline(*rows[-HW]); fR = upper_spline(*rows[HW])
    def h_at(s, w):
        c, l, r_ = fC(s), fL(s), fR(s); base = max(c, (l + r_) / 2); tilt = (r_ - l) / 2
        return base + tilt * w / HW + max(0.0, max(l - (base - tilt), r_ - (base + tilt)))
    lowA, lowB = lower[(k, 0)], lower[(k, 1)]; zA, zB = face_of(k, 0), face_of(k, 1); tA, tB = thick_of(k, 0), thick_of(k, 1)
    t = 5.0 if k == 1 else 5.5
    nA, nB = unit(a), unit(b)
    dA = unit(b - (b @ nA) * nA); dB = unit(a - (a @ nB) * nB)            # in-plate directions toward the other end
    xj = HUB_R + 7.0                                                       # plate -> ribbon hand-over (mm from the pin)
    sA = xj / (zA + tA / 2) / th; sB = 1 - xj / (zB + tB / 2) / th
    uA = zA + (tA - t) / 2; uB = zB + (tB - t) / 2; R_m = 0.5 * (zA + zB); slope = math.tan(math.radians(32)); kk = 2.5
    def H(s, w=0.0):
        env = h_at(s, w); rA = uA - slope * max(0.0, (s - sA) * th * R_m); rB = uB - slope * max(0.0, (sB - s) * th * R_m)
        v = np.array([env, rA, rB]); m = v.max(); return float(m + kk * math.log(np.exp((v - m) / kk).sum()))
    def dir_at(s): ang = s * th; return unit(Fm @ np.array([math.cos(ang), math.sin(ang), 0.0]))
    secs = []                                                             # (centre, across, up, width, thickness)
    def plate_sections(n, d, z0, tp, reverse):
        u = np.linspace(0, 1, 19); xs = np.r_[-HUB_R + 0.04 + (2 * HUB_R - 0.04) * (0.5 - 0.5 * np.cos(np.pi * u)), np.linspace(HUB_R + 1.2, xj, 5)]
        out = []
        for x in xs:
            hw_ = planform_halfwidth(x); c = n * (z0 + tp / 2) + x * d
            out.append((c, LAT - (LAT @ n) * n, n, 2 * max(hw_, 0.6), tp))
        return out[::-1] if reverse else out
    secs += plate_sections(nA, dA, zA, tA, False)
    ss = np.linspace(sA, sB, 22)[1:-1]
    for s in ss:
        w0 = dir_at(s); C = w0 * (H(s) + t / 2); Ct = dir_at(s + 1e-3) * (H(s + 1e-3) + t / 2); T = unit(Ct - C)
        up = unit(w0 - (w0 @ T) * T); acr = np.cross(T, up); acr = acr if acr @ LAT > 0 else -acr
        tilt = math.atan2(H(s, HW) - H(s, -HW), 2 * HW); up2 = math.cos(tilt) * up - math.sin(tilt) * acr; acr2 = np.cross(T, up2)
        acr2 = acr2 if acr2 @ LAT > 0 else -acr2
        secs.append((C, acr2, up2, 2 * HW, t))
    secs += plate_sections(nB, dB, zB, tB, True)
    ths = BRepOffsetAPI_ThruSections(True, False, 1e-6); ths.CheckCompatibility(False)
    for (c, acr, up, wd, tp) in secs:
        acr = unit(acr - (acr @ up) * up)
        ec = min(1.3 if True else 1.0, wd / 2 - 0.1, tp / 2 - 0.1)
        prof = section_outline(wd, tp, max(0.2, ec), n=96)
        pts = c + np.outer(prof[:, 0], acr) + np.outer(prof[:, 1], up)
        q = pts - c; i0 = int(np.argmax(q @ acr + 0.3 * (q @ up))); pts = np.roll(pts, -i0, 0)
        ths.AddWire(G.wire([BRepBuilderAPI_MakeEdge(G._periodic_curve(pts, G._shift())).Edge()]))
    ths.Build(); body = cq.Shape.cast(ths.Shape())
    if hasattr(body, "Solids") and body.Solids(): body = body.Solids()[0]
    DEBUG[f"l{k+1}_body"] = body
    return body, dict(zA=zA, zB=zB, tA=tA, tB=tB, lowA=lowA, lowB=lowB)

if __name__ == "__main__":
    print("joint lower faces (mm from GH):", {k: round(v, 1) for k, v in ZJ.items()}, "order", order)
    for k in range(3):
        body, info = build_link(k)
        print(f"link {k+1}: valid {body.isValid()} solids {len(body.Solids())} {info}")
        cq.exporters.export(cq.Workplane().add(body), os.path.join(OUT, f"link{k+1}_raw.step"))
    import trimesh
    sc = trimesh.Scene(); cols = {"body": [170, 175, 182, 255]}
    for nm, s in DEBUG.items():
        vs, tr = s.tessellate(0.05, 0.1)
        if not len(tr): print("empty", nm); continue
        m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]) * 0.001, tr, process=False); _ = m.vertex_normals
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=cols[nm.split("_")[1]], metallicFactor=0.5, roughnessFactor=0.45))
        sc.add_geometry(m, node_name=nm); print(nm, "valid", s.isValid(), "bbox", [round(x, 1) for x in (s.BoundingBox().xlen, s.BoundingBox().ylen, s.BoundingBox().zlen)])
    sc.export(os.path.join(HERE, "..", "shoulder-d4", "test_links.glb"))
