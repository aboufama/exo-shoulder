"""Family V2 - two shoulder pivots + a ring-free VIRTUAL AXIAL JOINT on the mid upper arm.

  J1 scapula pivot (axis b) -L1- J2 (axis c) -L2- virtual joint about the humerus axis h, built as a remote-centre
  linkage (belt-synchronised parallelogram, pivots and tendons only) whose base sits on L2 at the mid upper arm and
  whose output is the cuff. L2 lives in the arm-pointing frame (it does not turn with humeral axial rotation).
Checks (BodyParts3D skin, extended grids): L1 routed in the shoulder shell; L2 routed from J2 down a corridor along
the arm to the joint base; the joint's whole operating band (all azimuths it can occupy, +-BAND deg around its base,
at the cuff, 10-35 mm off the arm skin) must clear the body in every kept pose. Kinematics: singularity margins,
one branch, virtual-joint travel +-TRAVEL.

    TRAVEL=110 WORKERS=4 python3 family_V2.py [RMAX] [GENS]
"""
import json, math, os, sys, random
import concurrent.futures as cf
import numpy as np
import design_search as D
import design_search_families as F
import design_search_anat as A
import family_X as X

TRAVEL = float(os.environ.get("TRAVEL", 110)); BAND = float(os.environ.get("BAND", 130))


def arm_radius_profile():
    """upper-arm skin radius about the humerus axis, every 10 mm along it (arm grid, rest pose)"""
    prof = {}
    for s in range(150, 351, 10):
        r_out = 0
        for k in range(16):
            a = 2 * math.pi * k / 16; d = np.array([math.sin(a), 0, math.cos(a)])
            for q in range(30, 160, 2):
                if X.look(X.ARM, (d * q + np.array([0, -s, 0]))[None])[0] > 0: r_out = max(r_out, q); break
        prof[s] = r_out
    return prof


PROF = None


def evaluate(d, full=False):
    global PROF
    if PROF is None: PROF = arm_radius_profile()
    hf, h = A.HF_ALL[X.SUB], A.HG_ALL[X.SUB]
    b = np.broadcast_to(np.asarray(d["b"], float), h.shape); a1, a2 = d["a1"] * D.D2R, d["a2"] * D.D2R
    c, ok = F.circ_int(b, a1, h, a2, d["branch"])
    ok &= F.triangle_ok(b, h, a1, a2) & (np.abs((b * h).sum(-1)) <= math.cos(A.SING))
    xa = hf @ np.array([1.0, 0, 0]); phi = A.about(c, xa, h); best = (-1, 0)
    for cc in range(-180, 180, 10):
        k = (ok & (np.abs((phi - cc + 180) % 360 - 180) <= TRAVEL)).sum()
        if k > best[0]: best = (k, cc)
    alive = ok & (np.abs((phi - best[1] + 180) % 360 - 180) <= TRAVEL); kin = alive.mean()
    if full is None or kin < 0.6: return dict(d, cov=0.0, kin=float(kin))
    cp = c - (c * h).sum(-1, keepdims=True) * h; cp /= np.linalg.norm(cp, axis=1, keepdims=True) + 1e-12; e3 = np.cross(h, cp)
    s_j = d["s_joint"]; rj = PROF[int(round(s_j / 10) * 10)] + 22.0             # joint base: at the cuff, ~22 mm off the skin
    g = d["gam"] * D.D2R
    def at(az, s_, rr):                                                          # point beside the arm (scapula frame, per pose)
        return s_ * h + rr * (math.cos(az) * cp + math.sin(az) * e3)
    q = at(g, s_j, rj); qn = q / np.linalg.norm(q, axis=1, keepdims=True)
    i0 = int(np.argmax(alive)); R1, R2 = X.frame(b, c), X.frame(qn, c)
    X1, e1r, e1c = X.domain(); X2, e2r, e2c = X.domain(axis=R2[i0].T @ h[i0])
    B1 = X.blocked(X1, R1); B2t, B2a = X.blocked(X2, R2, split=True)
    q2 = R2[i0].T @ q[i0]; near = np.linalg.norm(X2 - q2, axis=1) < 26.0            # the joint base meets the cuff region
    B2 = B2t | (B2a & ~near[None])
    rr = np.arange(X.RMIN + X.STEP, X.RMAX - 2, X.STEP)
    b1, c1, c2 = R1[i0].T @ b[i0], R1[i0].T @ c[i0], R2[i0].T @ c[i0]
    rb = rr[int(np.argmin([B1[:, X.nearest(X1, b1 * r)][alive].sum() for r in rr]))]
    rc = rr[int(np.argmin([(B1[:, X.nearest(X1, c1 * r)] | B2[:, X.nearest(X2, c2 * r)])[alive].sum() for r in rr]))]
    # the joint's operating band: every azimuth it may occupy, at two stations along the cuff, must clear the trunk
    hf_, rs, eb = A.HF_ALL[X.SUB], A.RS_ALL[X.SUB], A.EBIN_ALL[X.SUB]
    for daz in np.linspace(-BAND, BAND, 13) * D.D2R:
        for ds in (-25.0, 25.0):
            s2 = min(350, max(150, s_j + ds)); P = at(g + daz, s2, PROF[int(round(s2 / 10) * 10)] + 22.0)
            Pt = np.einsum("nij,nj->ni", rs, P); dt = np.empty(len(P))
            for bb in np.unique(eb): sel = eb == bb; dt[sel] = X.look(X.TRUNK[bb], Pt[sel])
            alive &= dt >= X.CLEAR
    links = [(X1, e1r, e1c, B1, X.nearest(X1, b1 * rb), X.nearest(X1, c1 * rc)), (X2, e2r, e2c, B2, X.nearest(X2, c2 * rc), X.nearest(X2, q2))]
    paths = [None, None]
    for _ in range(6):
        changed = False
        for k, (Xk, er, ec, Bs, va, vb) in enumerate(links):
            alive &= ~(Bs[:, va] | Bs[:, vb])
            path, blk = X.route(Xk, er, ec, Bs, va, vb, alive)
            if path is None: return dict(d, cov=0.0, kin=float(kin))
            paths[k] = path
            if blk.any(): alive &= ~blk; changed = True
        if not changed: break
    out = dict(d, cov=float(alive.mean()), kin=float(kin), axial_centre=best[1], r_pins=[float(rb), float(rc)], joint=[float(s_j), float(rj)])
    if full:
        out["paths"] = [links[k][0][paths[k]].tolist() for k in range(2)]; out["frames0"] = [R1[i0].tolist(), R2[i0].tolist()]; out["alive"] = alive.tolist()
    return out


def design(g):
    az, el, a1, a2, br, gam, sj = g
    return dict(b=X.bvec(az, el), az=round(az, 1), el=round(el, 1), a1=round(a1, 1), a2=round(a2, 1), branch=int(br), gam=round(gam, 1), s_joint=round(sj, 0))
def feasible(g):
    az, el, a1, a2, br, gam, sj = g
    return -20 <= el <= 90 and 30 <= a1 <= 140 and 30 <= a2 <= 140 and 170 <= sj <= 320 and D.base_ok(np.array(X.bvec(az, el)))
def init(k): X.SUB = slice(None, None, k)
def score(g):
    try: return evaluate(design(g))["cov"]
    except Exception as e: return 0.0
def kinscore(g):
    try: return evaluate(design(g), None)["kin"]
    except Exception: return 0.0
def mutate(g, s):
    for _ in range(60):
        az, el, a1, a2, br, gam, sj = g
        n = [(az + random.gauss(0, 25 * s)) % 360, el + random.gauss(0, 12 * s), a1 + random.gauss(0, 12 * s), a2 + random.gauss(0, 12 * s),
             br if random.random() > 0.1 else -br, (gam + random.gauss(0, 40 * s)) % 360, sj + random.gauss(0, 30 * s)]
        if feasible(n): return n
    return g


if __name__ == "__main__":
    X.RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
    GENS = int(sys.argv[2]) if len(sys.argv) > 2 else 10; W = int(os.environ.get("WORKERS", 4)); random.seed(5)
    seeds = []
    for r in json.load(open("family_V_kin.json"))[:40]:
        for gam in (0, 90, 180, 270):
            seeds.append([r["az"], r["el"], r["a1"], r["a2"], r["branch"], gam, 230])
    seeds = [s for s in seeds if feasible(s)][:32]
    log = open(f"family_V2_{int(X.RMAX)}.log", "w")
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(8,)) as ex:
        sc = list(ex.map(score, seeds, chunksize=1))
        pop = sorted(zip(sc, seeds), key=lambda t: -t[0])[:6]; sig = 1.0
        print("gen 0", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
        for gen in range(1, GENS + 1):
            kids = [mutate(random.choice(pop)[1], sig) for _ in range(12)]
            ks2 = list(ex.map(score, kids, chunksize=1)); prev = pop[0][0]
            pop = sorted(pop + list(zip(ks2, kids)), key=lambda t: -t[0])[:6]
            sig = max(0.3, sig * (0.85 if pop[0][0] <= prev else 1.0))
            print(f"gen {gen}", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
    json.dump([dict(design(g), screen=s) for s, g in pop], open(f"family_V2_{int(X.RMAX)}_pop.json", "w"))
