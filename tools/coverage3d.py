"""Where can the arm go with the exo on? One row per (design, judged R16 workspace pose), for the dashboard's 3-D reach
view: the dot sits where the upper arm points from the shoulder centre (GH), green if the BUILT design reaches that
pose (judge/workspace.py, R16: the chain closes, no shoulder part enters the body, no two moving parts collide), red
with the reason if not.

Sources, per design dir that has judge/workspace.json: the judge's per_pose list (pass / fail and depths) and the
design's workspace.json poses (plane, elev, axial, flex, pron; the judge takes poses[::step], same order - checked).
Directions come from the body rig's own segment maths (pipeline/avg/body_pose.py segs(): Ry(plane) Rx(-elev)
Ry(axial) on the rest humerus), so they match the poses the judge posed the skin at.

Frame (the rig's thorax frame, body_pose.py): x anterior (forward), y up, z right (lateral for this RIGHT shoulder),
origin the right GH centre; right-handed. Plane 0 = raise to the side (+z), 90 = forward (+x), -90 = backward,
150 = across the body; elev 0 = arm hanging (-y). Axial > 0 turns the forearm inward (internal rotation).

Columns: design, label, level (Full CAD | Keep-out CAD), k (pose index in the judge's list), plane_deg, elev_deg, axial_deg, flex_deg (elbow), x, y, z (unit upper-arm direction GH -> elbow),
fx, fy, fz (unit forearm direction elbow -> wrist), pass (bool, the judge's own criterion), reason ('' when it passes,
else 'chain does not close' | 'body contact' | 'part interference' | 'body contact + part interference'),
body_mm (deepest shoulder part into the skin), body_part, parts_mm (deepest overlap of two moving parts, static fits
left to R6 excluded as the judge does), parts_pair. Rounded to 3 decimals (directions), 2 (mm). Designs in the order
they were judged (judge file time), the newest last.

    python3 tools/coverage3d.py [-o cov3d.json] [design id ...]      (default: every judged design; stdout)"""
import argparse, glob, json, os, re, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DES = os.path.join(REPO, "pipeline", "full-exo", "designs")
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import body_pose as BP                                       # lazy: only segs() is used, the skin rig never loads

ap = argparse.ArgumentParser(); ap.add_argument("designs", nargs="*"); ap.add_argument("-o", "--out", default="-")
a = ap.parse_args()

RIG = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json"))); L, S = RIG["landmarks"], RIG["scale"]
ELB, WRI = np.array(L["elbow"]), (np.array(L["ulnar_head"]) + np.array(L["radial_head"])) / 2
unit = lambda v: v / np.linalg.norm(v)


def arm(plane, elev, axial, flex, pron):
    sg, _ = BP.segs(L, S, dict(plane=plane, elev=elev, axial=axial, flex=flex, pron=pron))
    E = sg[2][0] @ ELB + sg[2][1]; Wr = sg[3][0] @ WRI + sg[3][1]
    return unit(E), unit(Wr - E)                             # GH is the origin


def short(n):                                                # 'D4-03 link 2 (Ti-6Al-4V)' -> 'link 2'
    if not n: return ""
    n = n.split("|", 1)[-1]; n = re.sub(r"\s*\(.*$", "", n).strip(); n = re.sub(r"^D4(-0\d)?\s+(member\s+)?", "", n)
    return {"l1": "link 1", "l2": "link 2", "l3": "link 3"}.get(n, n)


def label(des):                                              # designs/index.json label, else one made from the id
    try: lab = {r["id"]: r.get("label") for r in json.load(open(os.path.join(DES, "index.json")))}.get(des)
    except (OSError, ValueError): lab = None
    if not lab:
        m = re.match(r"^(cad|band|l1)_r(\d+)_(?:n(\d)|(\d)r)_s(\d+)_(\d+)(?:_(.+))?$", des)
        if not m: return des
        k, r, n1, n2, s, i, suf = m.groups()
        lab = f"r{r}, {n1 or n2} joints, {'CAD' if k == 'cad' else 'keep-out'} (s{s} #{i})" + (f", {suf}" if suf else "")
    return lab if len(lab) <= 56 else lab[:56].rsplit(" ", 1)[0].rstrip(",:;") + "…"


jt = lambda d: os.path.getmtime(os.path.join(DES, d, "judge", "workspace.json"))
ids = a.designs or sorted((os.path.basename(os.path.dirname(os.path.dirname(f))) for f in glob.glob(os.path.join(DES, "*", "judge", "workspace.json"))), key=jt)
rows = []
for des in ids:
    jf = os.path.join(DES, des, "judge", "workspace.json"); J = json.load(open(jf)); W = json.load(open(os.path.join(DES, des, "workspace.json")))
    poses = W["poses"][::J["step"]]; per = J["per_pose"]
    if len(poses) != len(per) or any([float(v) for v in fr["p"][:3]] != [float(v) for v in r["p"]] for fr, r in zip(poses, per)):
        sys.exit(f"{des}: judge per_pose does not match workspace.json poses[::{J['step']}]")
    tb, tp, static = J["tol_body_mm"], J["tol_parts_mm"], set(J.get("static_fits_left_to_R6") or [])
    lab, level = label(des), ("Full CAD" if des.startswith("cad_") or des == "final" else "Keep-out CAD")
    n_ok = 0
    for fr, r in zip(poses, per):
        plane, elev, axial, flex, pron = [float(v) for v in fr["p"][:5]]
        e, f = arm(plane, elev, axial, flex, pron)
        moving = {k: v for k, v in (r.get("pairs") or {}).items() if k not in static}
        pm = r.get("parts_motion_mm", max(moving.values(), default=0.0)) if r["closes"] else None
        pair = max(moving, key=moving.get) if moving and r["closes"] and pm > tp else ""
        why = [] if r["closes"] else ["chain does not close"]
        if r["closes"] and r["body_mm"] > tb: why.append("body contact")
        if r["closes"] and pm > tp: why.append("part interference")
        ok = not why; n_ok += ok
        rows.append(dict(design=des, label=lab, level=level, k=r["k"], plane_deg=round(plane), elev_deg=round(elev), axial_deg=round(axial),
                         flex_deg=round(flex), x=round(float(e[0]), 3), y=round(float(e[1]), 3), z=round(float(e[2]), 3),
                         fx=round(float(f[0]), 3), fy=round(float(f[1]), 3), fz=round(float(f[2]), 3), **{"pass": ok}, reason=" + ".join(why),
                         body_mm=r["body_mm"] if r["closes"] else None, body_part=short(r["body_part"]) if r["closes"] and r["body_mm"] > tb else "",
                         parts_mm=round(pm, 2) if pm is not None else None, parts_pair=" into ".join(short(s) for s in pair.split(" IN ")) if pair else ""))
    share = n_ok / max(1, len(per))
    if abs(share - J["share_passing"]) > 6e-4: sys.exit(f"{des}: {share:.4f} passing here, the judge says {J['share_passing']}")
    print(f"{des}: {len(per)} poses, {100 * share:.1f} % reached (judge: {100 * J['share_passing']:.1f} %)", file=sys.stderr)
txt = json.dumps(rows, separators=(",", ":"), ensure_ascii=False)
if a.out == "-": sys.stdout.write(txt + "\n")
else:
    open(a.out, "w").write(txt + "\n"); print(f"{len(rows)} rows, {len(txt) / 1024:.0f} KB -> {a.out}", file=sys.stderr)
