"""Joint cross-sections: v3 low-profile pivot (shoulder-d4/shoulder_d4.step) next to the conformal shoulder
(out_*/full_exo.step), cut by a plane through each joint axis. Parts are told apart by their order in the STEP.

    python3 section_joints.py [conformal out dir=../out_test] [png=joint_sections.png]
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import stepnames
OUTD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "out_test"))
PNG = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "joint_sections.png")
HW = ["washer A  GTM-1018-010", "sleeve  GSM-1012-05", "washer B  GTM-1018-010", "cap", "M4 ULP screw"]

def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)

def v3_parts():
    P = stepnames.load(os.path.join(HERE, "..", "..", "shoulder-d4", "shoulder_d4.step"))
    names = ["base", "link 1", "link 2", "link 3", "arm stub"] + [f"J{j} {h}" for j in range(1, 5) for h in HW]
    pins = json.load(open(os.path.join(HERE, "..", "..", "shoulder-d4", "display_pose.json")))["pins"]
    # v3 roles: links alternate shells; inner members carry the pin. J1 base|l1, J2 l1|l2, J3 l2|l3, J4 l3|stub
    members = {1: ("base", "link 1"), 2: ("link 2", "link 1"), 3: ("link 2", "link 3"), 4: ("arm stub", "link 3")}
    return dict(zip(names, [s for _, s in P])), pins, members

def conf_parts():
    P = stepnames.load(os.path.join(OUTD, "full_exo.step"))
    names = ["link 1", "link 2", "link 3", "base"] + [f"J{j} {h}" for j in range(1, 5) for h in HW] + ["BOTTOM"]
    shapes = dict(zip(names, [s for _, s in P[:len(names)]]))
    disp = json.load(open(os.path.join(OUTD, "shoulder", "display_pose.json")))
    order = disp["DES"]["order"]
    # J4 hardware + BOTTOM are stored in the arm's rest frame: back to the canonical frame (x -> HR^T x)
    HR = np.array(json.load(open(os.path.join(HERE, "..", "..", "avg", "body_mesh.json")))["landmarks"]["rest_humerus"])
    U_, _, Vt_ = np.linalg.svd(HR); HR = U_ @ Vt_                                       # exact rotation
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    R_ = HR.T; T_ = gp_Trsf(); T_.SetValues(*[float(x) for row in np.c_[R_, np.zeros(3)] for x in row])
    for k in [k for k in shapes if k.startswith("J4") or k == "BOTTOM"]: shapes[k] = cq.Shape.cast(BRepBuilderAPI_Transform(shapes[k].wrapped, T_, True).Shape())
    lo = {1: "base" if order[0] == 1 else "link 1", 2: "link 1" if order[1] == 1 else "link 2", 3: "link 2" if order[2] == 1 else "link 3", 4: "BOTTOM"}
    up = {1: "link 1" if order[0] == 1 else "base", 2: "link 2" if order[1] == 1 else "link 1", 3: "link 3" if order[2] == 1 else "link 2", 4: "link 3"}
    return shapes, disp["pins"], {J: (lo[J], up[J]) for J in lo}

def section(shape, c, n, t):
    """faces of shape cut by the plane through c spanned by t (in-plane) and n (axis) -> list of (outer, holes) in (u, v)"""
    nrm = np.cross(t, n)
    pl = cq.Face.makePlane(400, 400, cq.Vector(*c), cq.Vector(*nrm))
    try: cut = shape.intersect(pl)
    except Exception: return []
    out = []
    for f in cut.Faces():
        loops = []
        for w in [f.outerWire()] + f.innerWires():
            L = w.Length(); m = max(40, int(L / 0.05))
            pts = np.array([[p.x, p.y, p.z] for p in w.positions(np.linspace(0, 1, m).tolist())])
            loops.append(np.c_[(pts - c) @ t, (pts - c) @ n])
        out.append(loops)
    return out

COL = {"Ti": "#c9ccd1", "igus": "#e8a33d", "cap": "#9fb3c8", "screw": "#6b7280", "Al": "#b8c4b0"}
def mat(name):
    if "washer" in name or "sleeve" in name: return "igus"
    if "cap" in name: return "cap"
    if "screw" in name: return "screw"
    if name == "BOTTOM": return "Al"
    return "Ti"

def draw(ax, shapes, pins, members, J, title, floor=None):
    lo, up = members[J]; names = [lo, up] + [f"J{J} {h}" for h in HW]
    # joint axis from washer A's circular edges, pointing from the lower member to the cap
    wa = shapes[f"J{J} {HW[0]}"]
    circ = [e for e in wa.Edges() if e.geomType() == "CIRCLE"]
    ax_ = circ[0]._geomAdaptor().Circle().Axis(); n = np.array([ax_.Direction().X(), ax_.Direction().Y(), ax_.Direction().Z()])
    cen = np.mean([[e.Center().x, e.Center().y, e.Center().z] for e in circ], axis=0)
    cb = shapes[f"J{J} cap"].BoundingBox(); capc = np.array([cb.center.x, cb.center.y, cb.center.z])
    if (capc - cen) @ n < 0: n = -n
    ub = shapes[up].BoundingBox(); o = np.array([ub.center.x, ub.center.y, ub.center.z]) - cen; t = unit(o - (o @ n) * n)
    zc = 0.0; c = cen
    ext = {}
    for nm in names:
        secs = section(shapes[nm], c, n, t)
        for loops in secs:
            verts, codes = [], []
            for k, L in enumerate(loops):
                L = L.copy(); L[:, 1] -= zc
                area = 0.5 * np.sum(L[:-1, 0] * L[1:, 1] - L[1:, 0] * L[:-1, 1])
                if (k == 0) != (area > 0): L = L[::-1]
                verts += L.tolist(); codes += [Path.MOVETO] + [Path.LINETO] * (len(L) - 2) + [Path.CLOSEPOLY]
            m_ = mat(nm)
            ax.add_patch(PathPatch(Path(verts, codes), facecolor=COL[m_], edgecolor="#1f2328", lw=0.5,
                                   hatch="////" if m_ in ("Ti", "Al") else None, zorder=2))
            A = np.concatenate(loops); A[:, 1] -= zc; near = np.abs(A[:, 0]) < 9.6
            if near.any(): e = ext.setdefault(nm, [1e9, -1e9]); e[0] = min(e[0], A[near, 1].min()); e[1] = max(e[1], A[near, 1].max())
    # stack: skin-side face of the lower member at the axis .. top of the cap
    z_skin = ext[lo][0] if floor is None else max(ext[lo][0], floor); z_top = max(ext[f"J{J} cap"][1], ext[f"J{J} M4 ULP screw"][1])
    ax.set_xlim(-24, 30); ax.set_ylim(z_skin - 3, z_top + 3); ax.set_aspect("equal"); ax.axvline(0, color="#8a8f98", lw=0.5, ls=(0, (6, 3, 1, 3)), zorder=1)
    # dimension ladder on the right
    lv = [("skin-side face", z_skin)]
    for nm, lab in ((f"J{J} {HW[0]}", "washer A"), (up, "outer member"), (f"J{J} {HW[2]}", "washer B"), (f"J{J} cap", "cap")):
        if nm in ext: lv.append((lab, ext[nm][0]))
    lv.append(("top", z_top))
    x0 = 23
    for (la, za), (lb, zb) in zip(lv[:-1], lv[1:]):
        ax.annotate("", (x0, za), (x0, zb), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#1f2328", shrinkA=0, shrinkB=0))
        if zb - za > 0.15: ax.text(x0 + 0.8, (za + zb) / 2, f"{zb - za:.2f}", va="center", fontsize=6.5)
        ax.plot([18, x0 + 0.4], [za, za], lw=0.3, color="#8a8f98")
    ax.plot([18, x0 + 0.4], [z_top, z_top], lw=0.3, color="#8a8f98")
    ax.text(x0 + 0.5, z_top + 1.2, f"stack {z_top - z_skin:.2f} mm", fontsize=7.5, weight="bold")
    ax.set_title(title, fontsize=9, loc="left"); ax.tick_params(labelsize=6)
    return z_top - z_skin, ext

if __name__ == "__main__":
    S3, P3, M3 = v3_parts(); SC, PC, MC = conf_parts()
    fig, axs = plt.subplots(4, 2, figsize=(11, 15.5))
    rep = []
    for i, J in enumerate((1, 2, 3, 4)):
        h3, e3 = draw(axs[i, 0], S3, P3, M3, J, f"v3 low-profile pivot · J{J}  ({M3[J][0]} inner, {M3[J][1]} outer)", floor=-5.51 if J == 1 else None)   # v3 base: turned column below the hub
        hc, ec = draw(axs[i, 1], SC, PC, MC, J, f"conformal shoulder · J{J}  ({MC[J][0]} lower, {MC[J][1]} upper)")
        rep.append((J, h3, hc, e3, ec))
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor=COL["Ti"], hatch="////", edgecolor="#1f2328", label="Ti-6Al-4V"), Patch(facecolor=COL["Al"], hatch="////", edgecolor="#1f2328", label="BOTTOM (Al)"),
                        Patch(facecolor=COL["igus"], edgecolor="#1f2328", label="iglidur G washers / sleeve"), Patch(facecolor=COL["cap"], edgecolor="#1f2328", label="retaining cap"),
                        Patch(facecolor=COL["screw"], edgecolor="#1f2328", label="M4 ULP screw (stainless)")], loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.suptitle("Joint cross-sections through the axis (mm, axis vertical)", fontsize=11, x=0.06, ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, 0.98)); fig.savefig(PNG, dpi=220)
    for J, h3, hc, e3, ec in rep:
        print(f"J{J}: v3 stack {h3:.2f}  conformal {hc:.2f}")
        for nm in sorted(set(e3) | set(ec)):
            a = e3.get(nm); b = ec.get(nm)
            print(f"   {nm:28s} v3 {'' if a is None else f'{a[0]:6.2f}..{a[1]:6.2f}'}   conf {'' if b is None else f'{b[0]:6.2f}..{b[1]:6.2f}'}")
    print("saved", PNG)
