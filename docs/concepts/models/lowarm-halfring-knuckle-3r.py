"""lowarm-halfring-knuckle-3r (round 14, the knuckle-o20-overhead lens): desmo-conecut-knuckle-3r's verified chain (seats,
K law, dyad, conecut knee, J3 dowel, inverted stage 2) with three changes, run as cells on ONE harness:

  * CELL A0 (control) - the HALF RING: stage 1's groove under link 2's cap ring keeps its INNER wall over the dwell and the
    rise; its OUTER wall (the only stage-1 metal outside hub 2's O20 rim) is cut back to the rise + the blend + owd_margin
    deg of q2. Implemented as the proposer's patch of DCModel._desmo_build_B: the sector of the ring that is built (and
    sampled as rigid link-2 metal) is the azimuth span of the groove points with x >= -half_blend - owd_margin / s_th.
    In the dwell the crank is held at phi = 0 by the inner wall (phi > 0) and an own-angle STOP PAD on link 1b under the
    crank arm (phi < 0). The pad sits on link 1b's TOP face where the arm crosses link 1b at phi = 0 (checked here: the
    arm's phi = 0 centreline must pass over link 1b; the pad is then covered from the skin side by link 1b and adds no
    skin-facing metal). Stage-1 pin at the robust window a_s 9.2 / psi 149.5 / glev -1.0.
  * CELL A - the LOW ARM: A0 with the crank's free span 2.0 mm (zr) above link 1b's skin-face level beside link 1b (was
    4.03); the parent's arm builder already joins its levels with 60-deg ramps (the crank is 5-axis machined, stated).
  * CELL B - the LINK-2 ROOT LIFT: A plus link 2's bar leaving the hub-2 stack l2_lift mm higher (radially from GH) for
    r_u2 <= l2_rfull (r_u2 = distance from J2's axis), returning to its fitted level on an S-BEND of two tangent arcs over
    l2_len mm (clamped to the R15-inner bend length sqrt(4 R h - h^2), R = 16.5 mm at the 3 mm bar's centreline: 9.84 mm at
    h 1.5). Every link-2 sample moves (rigid underside, contact top copy, strap mid-surface, the per-pose l2_check), the
    cap ring / ring2 (inside the stack) does not.

GATES ADDED (reported in r['cam']['lowarm']): the dwell-hold over the TWO-BODY stack (J2 radial runout + ring-insert
concentricity at the pin's inner-wall contact, the pad lap at the pad's lever from the crank axis, converted to K through
the stage-1 geometry and the drive law, plus the stage-2 slot slop at K0 = 0) against the 0.25-deg gate; the pad seat
(arm over link 1b at phi = 0, lever from dR).

3 ACTIVE DOF (J1, J2, J3); K slaved by the drive (never read), crank pivot / knee pins passive rotations, two higher pairs;
0 passive translations, no springs / gears / pulleys / cables (MVP1).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lowarm-halfring-knuckle-3r.py [check|frozen|held|flood|redteam] ['<json>'|cellA0|cellA|cellB] [out.json]
"""
import importlib.util, inspect, json, math, os, sys, textwrap, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("desmoconecut_for_lowarm", os.path.join(HERE, "desmo-conecut-knuckle-3r.py"))
DC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(DC)
DS, RF, S, SC, FL, BM = DC.DS, DC.RF, DC.S, DC.SC, DC.FL, DC.BM
unit = DC.unit
ID = "lowarm-halfring-knuckle-3r"

# ---- (a) the half ring: the built ring sector is the groove's azimuth span from the blend's start - owd_margin (deg of q2)
_src = textwrap.dedent(inspect.getsource(DC.DCModel._desmo_build_B))
_old = "used = Kb <= lim + 1e-12; Gu = G2[used]"
assert _src.count(_old) == 1, "desmo-conecut's _desmo_build_B changed"
_new = ("_owm = float(P.get('owd_margin', -1.0)); used = (Kb <= lim + 1e-12) & ((x >= -hb_ - math.radians(_owm) / sa) if _owm >= 0 else True); "
        "Gu = G2[used]; self._owd = dict(owd_margin=_owm, n_used=int(used.sum()), n_all=int((Kb <= lim + 1e-12).sum()))")
_ns = {}; exec(compile(_src.replace(_old, _new), "lowarm_halfring", "exec"), DC.__dict__, _ns)
_build_B_halfring = _ns["_desmo_build_B"]

LH = dict(owd_margin=2.0, l2_lift=0.0, l2_rfull=16.0, l2_len=9.84, pad_tol=0.03, runout=0.010, conc=0.005)
PARAMS = dict(DC.PARAMS); PARAMS.update(LH)
CELL_A0 = dict(DC.BEST, a_s=9.2, psi=149.5, glev=-1.0, kslot=46.0, owd_margin=2.0, zr=4.03)
CELL_A = dict(CELL_A0, zr=2.0)
CELL_B = dict(CELL_A, l2_lift=1.5, l2_rfull=16.0, l2_len=9.84)
BEST = dict(CELL_B)
R_BEND = 16.5                                                 # R15 inner on the 3 mm bar: centreline radius
_dcclamp = DC._clamp


def lmin(h): return math.sqrt(max(4.0 * R_BEND * h - h * h, 0.0))


def _clamp(p):
    lift, rf, ln = p.get("l2_lift", 0.0), p.get("l2_rfull", 16.0), p.get("l2_len", 9.84)
    q = _dcclamp(p)
    q["owd_margin"] = float(p.get("owd_margin", 2.0))
    q["l2_lift"] = min(max(float(lift), 0.0), 3.0); q["l2_rfull"] = min(max(float(rf), 11.5), 30.0)
    q["l2_len"] = max(float(ln), lmin(q["l2_lift"]))           # hard box edge: the R15-inner S-bend length
    for k in ("pad_tol", "runout", "conc"): q[k] = float(p.get(k, LH[k]))
    return q


def s_profile(r, h, rfull, L):
    """lift of link 2's bar at distance r from J2's axis: h for r <= rfull, an S-bend of two tangent arcs down to 0 at rfull + L"""
    t = np.clip(np.asarray(r, float) - rfull, 0.0, L); Rp = ((L / 2) ** 2 + (h / 2) ** 2) / max(h, 1e-9)
    z1 = h - (Rp - np.sqrt(np.maximum(Rp ** 2 - t ** 2, 0.0))); z2 = Rp - np.sqrt(np.maximum(Rp ** 2 - (L - t) ** 2, 0.0))
    return np.where(t <= L / 2, z1, z2)


class LHModel(DC.DCModel):
    def _lift_L2(self):
        P = self.D.p; h = float(P.get("l2_lift", 0.0))
        if h <= 0 or "L2" not in getattr(self, "link_pts", {}): return
        m2, X = self.link_pts["L2"]
        if getattr(self, "_l2_lifted", None) is X or not len(X): return
        u2 = np.asarray(self.D.u[1], float); c2 = np.asarray(self.D.c[1], float)
        w = X - c2; r = np.linalg.norm(w - np.outer(w @ u2, u2), axis=1)
        z = s_profile(r, h, float(P["l2_rfull"]), float(P["l2_len"]))
        Y = X + z[:, None] * unit(X)
        self.link_pts["L2"] = (m2, Y); self._l2_lifted = Y
        self._l2_lift_info = dict(h=h, rfull=float(P["l2_rfull"]), L=float(P["l2_len"]), n_moved=int((z > 1e-6).sum()), n=len(X),
                                  r_moved_max=round(float(r[z > 1e-6].max()), 2) if (z > 1e-6).any() else None)

    def _contact_only(self):
        self._lift_L2()
        return super()._contact_only()

    def _desmo_build_B(self):
        _build_B_halfring(self)
        try: self._lowarm_gates()
        except Exception as ex_:                                   # a gate that cannot be read is reported, never silently passed
            self._lowarm = dict(error=repr(ex_))
        info = getattr(self, "_sc_info", None)
        if info is not None: info.setdefault("desmo", {})["lowarm"] = getattr(self, "_lowarm", None)

    def _lowarm_gates(self):
        """dwell hold over the two-body stack + the pad seat"""
        P = self.D.p; g = self._scg; dm = self._desmo
        dR, gg, cc, sig = g["dR"], g["g"], g.get("c", 0.0), g["sig"]
        F0, s0, u2 = dm["F0"], dm["s0"], dm["u2"]
        A0 = s0 * dR
        # pin velocity per unit phi and the inner wall's normal at the dwell (radial from J2's axis, in hub 2's plane)
        vF = np.cross(dR, F0)
        nW = unit(F0 - (F0 @ u2) * u2)                             # the groove walls are circles about u2 in the dwell
        vn = abs(float(vF @ nW))                                    # mm of wall-normal pin motion per rad of phi
        dphi_dK = abs(float(RF.dphi_of(np.array([1e-4]), gg, cc)[0]))
        # pad: the arm's phi = 0 centreline over link 1b (the crossing nearest the crank axis = the pad lever)
        vz = getattr(self, "_viz_rod", {}) or {}
        L1b = np.asarray(self.link_pts["L1b"][1], float); L1d = unit(L1b); w_ok = S.W_LINK / 2 + 1.0
        arm = np.asarray(vz.get("armPts") if vz.get("armPts") is not None else [], float).reshape(-1, 3)
        pad = None
        if len(arm):
            ang = np.array([np.arccos(np.clip(L1d @ unit(a), -1, 1)).min() * np.linalg.norm(a) for a in arm])
            over = ang < w_ok
            if over.any():
                aa = arm[over]; lev = np.linalg.norm(aa - np.outer(aa @ dR, dR), axis=1)
                j = int(np.argmax(lev)); pad = dict(lever_mm=round(float(lev[j]), 2), n_arm_over=int(over.sum()), n_arm=len(arm),
                                                    lever_range=[round(float(lev.min()), 2), round(float(lev.max()), 2)])
        Lp = pad["lever_mm"] if pad else 25.0
        kd = lambda e_mm: math.degrees(e_mm / max(vn, 1e-9) / max(dphi_dK, 1e-9))
        k_run, k_conc = kd(float(P["runout"])), kd(float(P["conc"]))
        k_pad = math.degrees(float(P["pad_tol"]) / Lp / max(dphi_dK, 1e-9))
        slot = 0.04
        try: slot = float(((self._sc_info.get("desmo") or {}).get("slop") or {}).get("slotB", {}).get("slop_max", 0.04))
        except Exception: pass
        tot = k_run + k_conc + k_pad + slot
        self._lowarm = dict(pin_wall_mm_per_rad=round(vn, 3), dphi_dK=round(dphi_dK, 4), K_deg_per_mm_at_pin=round(kd(1.0), 3),
                            pad=pad, pad_seat_ok=bool(pad is not None), pad_lever_used=round(Lp, 2),
                            dwell_K_play=dict(runout=round(k_run, 3), conc=round(k_conc, 3), pad_lap=round(k_pad, 3), slot=round(slot, 3),
                                              total=round(tot, 3), gate=0.25, ok=bool(tot <= 0.25 + 1e-9),
                                              inputs=dict(runout_mm=float(P["runout"]), conc_mm=float(P["conc"]), pad_tol_mm=float(P["pad_tol"]))),
                            owd=getattr(self, "_owd", None), l2_lift=getattr(self, "_l2_lift_info", None))


DC.DCModel = LHModel; DS.PARAMS = PARAMS; DS._clamp = _clamp; DS.DSModel = LHModel
SC.SCModel = LHModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = LHModel; FL.FLModel_SC = LHModel; BM.PARAMS = PARAMS
DC.PARAMS = PARAMS; DC._clamp = _clamp

_report, evaluate, bench_eval, frozen, frozen_held, frozen_flood, redteam, viz_export = (
    DS._report, DS.evaluate, DS.bench_eval, DS.frozen, DS.frozen_held, DS.frozen_flood, DS.redteam, DS.viz_export)
_report_dc = DC._report_dc


def _par(a):
    if a in ("cellA0", "cellA", "cellB", "best"): return dict({"cellA0": CELL_A0, "cellA": CELL_A, "cellB": CELL_B, "best": BEST}[a])
    return dict(BEST, **json.loads(a)) if a else dict(BEST)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = _par(sys.argv[2] if len(sys.argv) > 2 else "")
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"),
                              ovh=out.get("overhead"), l2=out.get("l2"), dK_taken_max=out.get("dK_taken_max"),
                              lowarm=((out.get("cam") or {}).get("desmo") or {}).get("lowarm"), connected=out.get("connected"), secs=out["secs"]),
                         default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report_dc(B, par)
    print(json.dumps(dict(gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"],
                          near1=r.get("gap_near1"), honest=r.get("honest"), why=r.get("why"), l2=r.get("l2"), parts=r.get("parts_ib14"),
                          lowarm=getattr(M, "_lowarm", None), desmo_fail=r.get("desmo_fail"), secs=round(time.time() - t, 1)), default=float))
