"""roller-longdyad-knuckle-3r (round 9, pick 1): the verified roller-flank knuckle (sidecar-roller-flank-knuckle-3r: J1
acromion top, link 1a with a milled flank boss, K slaved and never read, link 1b, J2, link 2, J3, pin knee + cuff; the
hub-2 rim lobe -> bell crank on an MR63ZZ pair on link 1b -> bent long arm -> MR63ZZ roller -> conjugate spherical flank on
link 1a) worn on the lead's LONGER K dyad (bk2 38-48) with a RE-CUT flank whose own range (dK_lim) is 56-64 deg instead
of the lead RSSR's 43 (rod vs hub 2) / 38.1 taken. 3 ACTIVE DOF (J1, J2, J3), 0 passive translations, no gears / pulleys /
cables / rods.

THE LEVER (judge, round 9): the lead's binding stretched wall is the drive stroke, th_wall = a1e(dK_lim) + a2 - 5
(109.5 on the lead), not stop B (120.1, never bound). A longer flank stroke raises it to 117.5-120.2 at bk2 44; the lobe
skirt (th 123.6) caps it.

WHAT THIS FILE CHANGES on the roller-flank model (everything else - the cam synthesis per 0.25 deg of K, both pressure
angles, lift-off, cusp, contact-on-lug, arm / roller / lug clearances, the drive-range truncation on every bench, the
per-pose metal, the pin knee, the O20 stacks, the kit fold rule - is that model's code, loaded unchanged):
  * chain 'free' always (the parent's 'lead' chain forced the frontload dyad bk1 30.05 / bk2 37.57);
  * component / search limits: bk1 26-32, bk2 38-48, a1max <= bk1 + bk2 - 5, g 1.8-3.0, beta -180..-150, r_c 14.5-19.5,
    lift 0-4, law 'lin' (cprog 0: the progressive law cusps at the pitch point, measured by the parent);
  * PA_MAX 43 (2 deg under the 45 gate: ~0.6 deg K slop + flank tolerance; judge's pass rule);
  * the roller's retaining stub head is sampled as metal: an O4.5 x 0.8 head under the MR63ZZ (the O3 stub is integral
    to the crank, the head is on the skin side of the roller), member 9 (crank), skin / in-band / near-touch / part pairs;
  * 'near2' objective (round-9 rule): the search gap is the 2 mm near-touch gap (metal < 2 mm counted as contact);
    'plain' and 'gap_near1' are reported next to it;
  * gate(params): the law-only kill gate - fit on Bench(60,160) fast, then the fitted design's own IK on every
    Bench(110,360) workspace pose: kinematic reach without and with the drive's own range dK_lim, the largest th taken,
    overhead, and the lost poses by wall.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/roller-longdyad-knuckle-3r.py [check] ['<json>']
    ... gate '<json>'
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("rollerflank_for_longdyad", os.path.join(HERE, "sidecar-roller-flank-knuckle-3r.py"))
RF = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RF)
SC, FL, PK, S = RF.SC, RF.FL, RF.PK, RF.S
unit = S.unit; D2R = math.pi / 180
ID = "roller-longdyad-knuckle-3r"
RF.PA_MAX = 43.0
HEAD_R, HEAD_T = 2.25, 0.8

# the verified lead's seats (rows/sidecar-longdyad-knuckle-3r.json best_params) + the proposer's re-cut flank (g 2.3,
# beta -168, r_c 17.5 at bk2 44 / a1max 68: dK_lim 64.0 measured by the proposer at pressure angles 37.4 / 43.1)
LEAD_SEATS = {"bk1": 28.9414, "bk2": 39.236, "a1max": 63.1774, "kK": 1.6232, "s_arm": 4.3872, "r_lobe": 7.7447, "smhi": 16.5464,
              "smlo": 5.0, "az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345,
              "ang_min": 26.8823, "lc": 25.6915, "phib": -60.7036}
SEED = dict(LEAD_SEATS, bk2=44.0, a1max=68.0, g=2.3, beta=-168.0, r_c=17.5, lift=1.4, hl=1.35, zr=3.0, cprog=0.0, law_mode="lin",
            chain="free", near2=1)
PARAMS = dict(RF.PARAMS, **SEED)


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    p["chain"] = "free"; p["law_mode"] = "lin"
    p["bk1"] = _c(p["bk1"], 26.0, 32.0); p["bk2"] = _c(p["bk2"], 38.0, 48.0)
    p["g"] = _c(p["g"], 1.8, 3.0); p["r_c"] = _c(p["r_c"], 14.5, 19.5); p["lift"] = _c(p.get("lift", 0.0), 0.0, 4.0)
    b = float(p["beta"]); b = b - 360.0 if b > 0 else b; p["beta"] = _c(b, -180.0, -150.0)
    p["cprog"] = 0.0
    return RF._clamp(p)


class RLModel(RF.RFModel):
    def _rod_metal(self):
        super()._rod_metal()
        C0 = np.asarray(self._viz_rod["roller"], float); cr = unit(C0); e, f = S.frame_of(cr); dd = S.disc(HEAD_R, 1.5)
        head = C0 - (1.25 + HEAD_T) * cr + dd[:, :1] * e + dd[:, 1:] * f          # stub head underside, skin side of the roller
        ring = SC._ring(C0 - (1.25 + HEAD_T) * cr, HEAD_R, cr)
        m, X = self.rigid["roller"]; self.rigid["roller"] = (m, np.concatenate([X, head]))
        self.contact.append((9, np.concatenate([head, ring])))
        mR, XR = self.strap["ROD"]; self.strap["ROD"] = (mR, np.concatenate([XR, ring]))
        self._sc_info["stub_head"] = [HEAD_R * 2, HEAD_T]


SC.SCModel = RLModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = RLModel; FL.FLModel_SC = RLModel


def ws_inband(B):
    """the unscored workspace in-band (round-9 rule, gaming pattern L2): in-band 2-14 / 2-10 over the metal of the TAKEN
    workspace poses, overall and at elevation 90-140, from the bench's own per-pose distances (B.res)"""
    out = {}
    for nm, lo, hi in (("all", -1, 999), ("e90_140", 90, 140), ("ovh140", 140, 999)):
        d = [B.res[j] for j, k in enumerate(B.kind) if k == "ws" and B.res[j] is not None and float(np.min(B.res[j])) >= 0
             and lo <= float(B.poses[j]["elev"]) < hi]
        d = np.concatenate(d) if d else np.zeros(0)
        out[nm] = [round(float(np.mean((d >= 2) & (d <= 14))), 4), round(float(np.mean((d >= 2) & (d <= 10))), 4)] if len(d) else None
    return out


def _report(B, params):
    p = dict(PARAMS, **params)
    r, M = RF._report(B, p)
    r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")} if "plain" not in r else r["plain"]
    r["ws_inband"] = ws_inband(B)
    if M.kin_ok.any() and p.get("near2"):
        a = PK.audit(M, B); r["gap_near2"] = a.get("gap_near2"); r["near2_poses"] = a.get("near2_poses")
        r["gap_near1"] = a.get("gap_near1", r.get("gap_near1"))
        if r["gap_near2"] is not None: r["gap"] = r["gap_near2"]
    info = getattr(M, "_sc_info", None) or {}
    r["cam"] = {k: info.get(k) for k in ("dK_lim", "why_lim", "pa_crank_max_taken", "pa_horn_max_taken", "phi_max_taken", "flank_rho_min",
                                         "clear_hubK_min", "clear_roll_hubK_min", "clear_lowarm_lug_min", "arm_len", "arc_deg", "law_dK_max")}
    if info and (info.get("pa_crank_max_taken", 0) > RF.PA_MAX + 1e-6 or info.get("pa_horn_max_taken", 0) > RF.PA_MAX + 1e-6):
        r["honest"] = False; r["pa_fail"] = True
    return r, M


def contact_split(M, B):
    """per-part split of the skin-contact poses after M.run(): for each pose whose why is contact / skin, the parts whose
    metal (rigid samples by name, contact-only samples by member) goes under the skin, and the member-level count"""
    mem_name = {}
    for nm, (m, X) in M.rigid.items(): mem_name.setdefault(m, []).append(nm)
    out = {}; n = 0
    for i in range(len(B.idx)):
        if M.why[i] not in ("contact", "skin"): continue
        n += 1; hit = set()
        for nm, (m, X) in M.rigid.items():
            if len(X) and float(B.dist(i, M.world(m, i, X)).min()) < 0: hit.add(nm)
        for m, X in M.contact:
            if len(X) and float(B.dist(i, M.world(m, i, X)).min()) < 0: hit.add("m%d:%s" % (m, "/".join(mem_name.get(m, ["?"]))))
        for h in hit: out[h] = out.get(h, 0) + 1
    return dict(n=n, by_part=dict(sorted(out.items(), key=lambda kv: -kv[1])))


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def gate(params, nc=110, nw=360):
    """law-only kill gate (drive metal does not decide it): fit on Bench(60,160) fast, then the fitted design's own IK
    (law + K + knee + |s_n| <= R_tol) on every Bench(nc, nw) workspace pose: kinematic reach with the law alone and with the
    drive's own range |dK| <= dK_lim, the largest th taken, overhead, and the lost poses by wall"""
    p = _clamp(dict(PARAMS, **params))
    B1 = CB.Bench(n_clip=60, n_ws=160); r1, M1 = _report(B1, p); D = M1.D
    Z = CB._poses_all(); B3 = CB.Bench(n_clip=nc, n_ws=nw)
    k = np.array(B3.kind); ws = k == "ws"; Q = Z["HG"][B3.idx].astype(float)
    q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s); dK = np.degrees(np.abs(np.asarray(D._dK, float)))
    kin = ok & Kn["ok"] & (np.abs(s[:, 2]) <= float(D.p["R_tol"]))
    lim = math.degrees(float(M1._scg["dK_lim"])); kinD = kin & (dK <= lim + 1e-6)
    th = np.degrees(np.arccos(np.clip((Q @ D.u[2]) @ D.u[0], -1, 1)))
    elev = np.array([B3.poses[i]["elev"] for i in range(len(B3.idx))]); ov = ws & (elev >= 140)
    a1A, a2 = D.a1, D.a2; amax = float(D.p["a1max"]); L_ = D.law()
    lost = ws & ~kinD
    hist = {}
    for lo_, hi_ in ((0, 30.5), (30.5, 109.5), (109.5, 113.5), (113.5, 117.6), (117.6, 120.2), (120.2, 123.6), (123.6, 130), (130, 180)):
        m = ws & (th >= lo_) & (th < hi_); hist[f"{lo_}-{hi_}"] = f"{int(kinD[m].sum())}/{int(m.sum())}"
    return dict(kin360_law=round(float(kin[ws].mean()), 4), kin360=round(float(kinD[ws].mean()), 4), n_ws=int(ws.sum()),
                ov_law=f"{int(kin[ov].sum())}/{int(ov.sum())}", ov=f"{int(kinD[ov].sum())}/{int(ov.sum())}",
                th_max_taken=round(float(th[ws & kinD].max()), 1) if (ws & kinD).any() else None,
                dK_taken_max=round(float(dK[ws & kinD].max()), 1) if (ws & kinD).any() else None,
                lost_drive_wall=int((ws & kin & ~kinD).sum()), th_hist_taken=hist,
                a1=round(a1A, 2), a2=round(a2, 2), window=[round(abs(a1A - a2) + 5, 1), round(amax + a2 - 5, 1)],
                law=dict(why_end=L_.get("why_end"), dK_max=round(L_.get("dK_max", 0), 1), th_max=L_.get("th_max")),
                cam=r1.get("cam"),
                fast=dict(gap=r1["gap"], plain=r1.get("plain"), near1=r1.get("gap_near1"), reach=r1["reach"], follow=r1["follow"],
                          inband14=r1["inband14"], contact=r1["contact"], why=r1.get("why"), honest=r1.get("honest"),
                          ovh=(r1.get("overhead140") or {}).get("reach"), parts=r1.get("parts_ib14"), pairs=r1.get("parts_pairs")))


def frozen(P, nc=110, nw=360):
    out = SC.frozen(_clamp(dict(PARAMS, **P)), nc, nw); return out
def frozen_held(P): return SC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)
def frozen_flood(P, nc=110, nw=360): return SC.frozen_flood(_clamp(dict(PARAMS, **P)), nc, nw)


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "gate":
        t = time.time(); out = gate(par); out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=a.get("overhead140"), parts=out.get("parts_ib14"),
                              connected=out.get("connected"), sidecar=out.get("sidecar"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          idle=r.get("drive_idle"), cam_short=r.get("cam_short"), pa_fail=r.get("pa_fail"), why=r.get("why"),
                          ovh=r.get("overhead140"), ws_inband=r.get("ws_inband"), cam=r.get("cam"), parts=r.get("parts_ib14"), pairs=r.get("parts_pairs"),
                          split=contact_split(M, B) if mode == "split" else None,
                          clear=getattr(M, "last_clear", None), secs=round(time.time() - t)), default=float))
