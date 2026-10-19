"""minarc-stop-knuckle-4r, VARIANT B under THE KIT'S J1-J3 FOLD RULE (2026-10-16 re-optimisation after the re-measure
docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.md).

The variant-B model (docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py) is loaded UNCHANGED as its own module copy;
only its design class is replaced, so the claim's model keeps its reading. What changes (opt-in, `kitrule` 1 = default here):

  * the J2 hard stops are placed in the KIT's metric (tools/concept_kit.py "THE J1-J3 FOLD MARGIN"): the stops are
    parametrised by the J1-J3 fold margin at which they engage with K on stop A,
        smhi: th_hi = min(a1 + a2, 360 - a1 - a2) - smhi      (stretched stop)
        smlo: th_lo = |a1 - a2| + smlo                        (folded stop)
    and phi_hi / phi_lo are the J2 interior angles of the (a1, a2) dyad at th_hi / th_lo. smhi, smlo >= FOLD_MARGIN
    (5 deg, the user's ruling) are design variables (CLAUDE.md "treat fold stops as a design variable"), so J2 meets its
    stop BEFORE the dyad enters the forbidden band and K opens from there on: no forbidden band between state A and the
    forced states (the island the re-measure found under the claim's phi reading cannot form).
  * EVERY state keeps the kit's margin: the effective J1-J2-J3 dyad (a1e, a2) - a1e = a1 on stop A, the opened arc in
    the forced states - takes a pose only if th lies in [|a1e - a2| + m, min(a1e + a2, 360 - a1e - a2) - m]; the forced
    sub-chain J1-K-J3 keeps its own m (as before); K's dyad (bk1, bk2) keeps m over a1e in [a1, a1max] (as before).
  * `near` 1: the search objective is the NEAR-TOUCH gap (metal < 1 mm counted as contact; CLAUDE.md "Search on the
    near-touch gap"); the plain numbers are kept as *_plain.
  * `phys` 1 (opt-in; default 0 = the virtual interior-angle stop of the claim's law, read in the kit metric): the
    BUILDABLE J2 stop (the independent judge's mechanism lens, docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.md):
    a dowel in an arc slot at J2 stops J2's OWN joint angle q2 (link 1b vs link 2). The q2 window is the state-A q2 at
    th_lo / th_hi (closed form: cos th = A + R cos(q2 - q0) with K on stop A). Past it J2 is locked on the stop and K opens
    to the smallest rotation (in its opening direction, <= stop B) that closes the chain J1 -> K -> (link 1b + link 2
    rigid) -> J3: u1 . R(uK, dK) p = cos th with p = R(u2, q2_stop) u3 - closed form (Paden-Kahan), no scan.
    Margins in every state: state A the dyad (a1, a2); forced states the moving sub-chain J1-K-J3 (b1, c = arc(K, J3)) AND
    (`m3e` 1) the effective dyad (a1e, a2), all >= FOLD_MARGIN.
  * `capK` (mm, opt-in, default 0): hub K's clock-spring cap this much taller than the O20 12.25 stack on the crown side
    (the judge's real spring: 0.3 x 5 mm 1.4310 strip, cap +6 mm): part-part cylinder, crown samples and the skin-contact
    rings of hub K all run F .. F + 12.25 + capK, in the fit AND in every worn (frozen) copy.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py [check] ['<json>']
    hooks: evaluate(B, params) -> (params, report) for tools/concept_cma.py
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("minarc_b_for_kitrule", os.path.join(HERE, "minarc-stop-knuckle-4r-pinknee.py"))
KB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KB)      # own module copy: patching it leaves the claim's model alone
PK, S = KB.PK, KB.S
D2R = math.pi / 180
ID = "minarc-stop-knuckle-4r"; VARIANT = "B kit rule (pin knee + knuckle, J2 stops in the J1-J3 margin metric)"
REPORT_KEYS = KB.REPORT_KEYS + ("gap_near1", "near1_poses", "min_metal_mm", "kitrule", "plain")
PARAMS = dict(KB.PARAMS, kitrule=1, smhi=8.0, smlo=8.0, near=1, phys=0, capK=0.0, m3e=1)


def dyad_phi(a1, a2, th):
    """J2 interior angle (deg) of the spherical dyad (a1, a2) spanning th"""
    c = (math.cos(th * D2R) - math.cos(a1 * D2R) * math.cos(a2 * D2R)) / (math.sin(a1 * D2R) * math.sin(a2 * D2R))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def dyad_margin(th, a1, a2):
    """the kit's J1-J3 fold margin (deg) of the dyad (a1, a2) at th (arrays ok)"""
    a1 = np.asarray(a1, float)
    return np.minimum.reduce([th - np.abs(a1 - a2), np.minimum(a1 + a2, 360 - a1 - a2) - th])


class KRDesign(KB.KDesign):
    def __init__(self, params=None):
        super().__init__(params); P = self.p
        self.kitrule = bool(P.get("kitrule", 0)); self.phys = bool(P.get("phys", 0)); self.stops_ok = True
        if self.kitrule:
            m = KIT.FOLD_MARGIN
            P["smhi"] = max(m, float(P.get("smhi", 8.0))); P["smlo"] = max(m, float(P.get("smlo", 8.0)))
            th_hi = min(self.a1 + self.a2, 360 - self.a1 - self.a2) - P["smhi"]; th_lo = abs(self.a1 - self.a2) + P["smlo"]
            self.stops_ok = th_lo < th_hi - 1.0; self.th_lo, self.th_hi = th_lo, th_hi
            P["phi_hi"] = dyad_phi(self.a1, self.a2, th_hi) if self.stops_ok else 170.0
            P["phi_lo"] = dyad_phi(self.a1, self.a2, th_lo) if self.stops_ok else 10.0
            P["mstop"] = 0                                    # state A is inside [th_lo, th_hi] by construction
        if self.phys:
            assert self.kitrule, "phys needs kitrule (stops placed in the J1-J3 metric)"
            u1, u2, u3 = self.u
            A = float((u1 @ u2) * (u2 @ u3)); Bc = float(u1 @ u3) - A; Cs = float(u1 @ np.cross(u2, u3))
            self._q2c = (A, math.hypot(Bc, Cs), math.atan2(Cs, Bc))  # cos th = A + R cos(q2 - q0), K on stop A
            self.q2sgn = float(P["q2sgn"]) if P.get("q2sgn") else None   # the ik branch's half-turn of q2, carried in params

    def _q2_at(self, th, sgn):
        A, R, q0 = self._q2c
        return q0 + sgn * math.acos(max(-1.0, min(1.0, (math.cos(th * D2R) - A) / R)))

    def ik(self, Q):
        if not hasattr(self, "uK"): return super().ik(Q)
        if not self.phys:
            q, ok, X1, X2, X3, s = super().ik(Q)
            if self.kitrule:
                w = Q @ self.u[2]; th = np.degrees(np.arccos(np.clip(w @ self.u[0], -1, 1)))
                m3e = dyad_margin(th, self._a1e, self.a2); self._m3e = m3e
                ok = ok & (m3e >= KIT.FOLD_MARGIN - 1e-6) & bool(self.stops_ok)
            return q, ok, X1, X2, X3, s
        return self._ik_phys(Q)

    def _ik_phys(self, Q):
        """physical J2 stop on q2; K opens (closed form) past it"""
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]; m = KIT.FOLD_MARGIN
        b1, b2 = float(P["bk1"]), float(P["bk2"])
        # state A: the variant-B closure with K on stop A (the model's own ik at dK = 0: a1max := a1 forces state A or no root)
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        save = (P["phi_lo"], P["phi_hi"], P["a1max"]); P["phi_lo"], P["phi_hi"] = S.SING, 180 - S.SING
        try: qA, okA, X1A, X2A, X3A, sA = super().ik(Q)
        finally: P["phi_lo"], P["phi_hi"], P["a1max"] = save
        dKA = self._dK.copy()
        A, R, q0 = self._q2c
        rel = np.degrees(PK.wrap(qA[:, 1] - q0))
        if self.q2sgn is None:                                # the ik branch's half-turn of q2 (fixed per design)
            sel = okA & (np.abs(dKA) < 1e-9) & (np.abs(rel) > 1)
            self.q2sgn = float(np.sign(np.median(rel[sel]))) if sel.any() else 1.0; P["q2sgn"] = self.q2sgn
        sg = self.q2sgn
        q2hi, q2lo = self._q2_at(self.th_hi, sg), self._q2_at(self.th_lo, sg)
        self.q2_stops = (math.degrees(q2lo), math.degrees(q2hi))
        inA = okA & (np.abs(dKA) < 1e-9) & (np.sign(rel) == sg) & (th >= self.th_lo - 1e-6) & (th <= self.th_hi + 1e-6)
        # forced: J2 locked on the stop, K opens
        st = np.where(th > self.th_hi, 1, np.where(th < self.th_lo, -1, 0)); st = np.where(inA, 0, st)
        q2s = np.where(st == 1, q2hi, q2lo)
        Rq = S.rotm(u2, q2s) if n else np.zeros((0, 3, 3)); p = Rq @ u3
        A0 = (u1 @ uK) * (p @ uK); Bk = p @ u1 - A0; Ck = np.cross(uK, p) @ u1
        Rk = np.hypot(Bk, Ck); f0 = np.arctan2(Ck, Bk); x = (np.cos(th * D2R) - A0) / np.maximum(Rk, 1e-12)
        g = np.arccos(np.clip(x, -1, 1)); sp = np.sign(self.psiA)
        r1 = PK.wrap(f0 - g); r2 = PK.wrap(f0 + g)
        c1 = np.where(r1 * sp >= -1e-9, np.abs(r1), np.inf); c2 = np.where(r2 * sp >= -1e-9, np.abs(r2), np.inf)
        dKf = sp * np.minimum(c1, c2); rootok = (np.abs(x) <= 1) & np.isfinite(dKf) & (st != 0)
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(b1 * D2R) * math.cos(b2 * D2R)) / (math.sin(b1 * D2R) * math.sin(b2 * D2R))
        dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))
        rootok &= np.abs(np.nan_to_num(dKf, posinf=9.0)) <= dKB + 1e-9
        dK = np.where(rootok, np.nan_to_num(dKf, posinf=0.0), 0.0)
        RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3))
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), w)
        R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        R12 = R1 @ RK @ Rq; vv = unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
        R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3)); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        # merge: state A from the model's closure, forced from the locked-J2 closure
        fA = st == 0; fa = fA[:, None]; fa3 = fA[:, None, None]
        q = np.where(fa, qA, np.stack([q1, q2s, q3], 1))
        R1m = np.where(fa3, X1A[0], R1); R2m = np.where(fa3, X2A[0], R12); R3m = np.where(fa3, X3A[0], R123); t3m = np.where(fa, X3A[1], t3)
        RKm = np.where(fa3, np.eye(3)[None], RK); dKm = np.where(fA, 0.0, dK)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RKm, u2) @ u1, -1, 1)))
        cK = np.degrees(np.arccos(np.clip(p @ uK, -1, 1)))
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        m3e = dyad_margin(th, a1e, self.a2)
        ok = np.where(fA, inA, rootok & (msub >= m - 1e-6)) & bool(self.k_ok) & bool(self.stops_ok)
        if P.get("m3e", 1): ok &= m3e >= m - 1e-6
        Z0 = np.zeros((n, 3)); X1 = (R1m, Z0); X1b = (R1m @ RKm, Z0); X2 = (R2m, Z0); X3 = (R3m, t3m)
        sv = np.einsum("nji,nj->ni", Q, t3m); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        self._X1b, self._dK, self._state, self._a1e, self._msub, self._m3e = X1b, dKm, st, a1e, np.where(fA, 99.0, msub), m3e
        return q, ok, X1, X2, X3, s


def unit3(x): x = np.asarray(x, float); return x / np.linalg.norm(x)


KB.KDesign = KRDesign                                         # KB.KModel builds its design through this module global


class _RK(float):
    """hub K's radius carrying its own (taller) crown"""
    crown = S.CROWN


class _CapT(tuple):
    capk = True


def apply_cap(Mo, dh):
    """hub K's clock-spring cap dh mm taller (crown side): cylinder, crown samples and skin-contact rings (= the judge's cap_k,
    re-applied idempotently so a frozen copy carries it too)"""
    if dh <= 0 or "hubK" not in getattr(Mo, "cyl", {}): return
    r = _RK(float(Mo.cyl_r["hubK"])); r.crown = S.CROWN + dh; Mo.cyl_r = dict(Mo.cyl_r); Mo.cyl_r["hubK"] = r
    base = Mo.sd_cylr
    def sd_cyl(Pw, cen, ax, r=None):
        rr = max(Mo.hr) if r is None else r
        return base(Pw, cen, ax, rr, getattr(rr, "crown", S.CROWN))
    Mo.sd_cyl = sd_cyl
    mem, cen, ax = Mo.cyl["hubK"]; e, f = S.frame_of(ax); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); H = S.CROWN + dh
    pts = [cen + z * ax + float(r) * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, H, 7)]
    dd = S.disc(float(r), 4.0); pts.append(cen + H * ax + dd[:, :1] * e + dd[:, 1:] * f); Mo.cyl_surf = dict(Mo.cyl_surf); Mo.cyl_surf["hubK"] = (mem, np.concatenate(pts))
    ang32 = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = float(r) * (np.cos(ang32)[:, None] * e + np.sin(ang32)[:, None] * f)
    extra = [_CapT((mem, cen + z * ax + ring)) for z in np.linspace(S.CROWN, H, 3)]
    dd2 = S.disc(float(r), 2.0); extra.append(_CapT((mem, cen + H * ax + dd2[:, :1] * e + dd2[:, 1:] * f)))
    Mo.contact = [c for c in Mo.contact if not isinstance(c, _CapT)] + extra


_KModel0 = KB.KModel


class KModel(_KModel0):
    def run(self, B=None):
        dh = float(self.p.get("capK", 0) or 0)
        if dh > 0:
            fit0 = self.fit
            def fit_cap(): fit0(); apply_cap(self, dh)
            self.fit = fit_cap
        return super().run()


KB.KModel = KModel                                            # KB._report / frozen() build through this module global
KDesign = KRDesign


def _report(B, params):
    p = dict(PARAMS, **params)
    for k in ("sK",): p[k] = 1 if float(p[k]) >= 0 else -1
    r, M = KB._report(B, p)
    if M.kin_ok.any():
        a = PK.audit(M, B); r["gap_near1"] = a["gap_near1"]; r["near1_poses"] = a["near1_poses"]; r["min_metal_mm"] = a["near_touch_min_mm"]
        r["overhead140"] = a["overhead140"]
    else:
        r["gap_near1"] = r["gap"]; r["near1_poses"] = 0; r["min_metal_mm"] = None
    D = M.D
    if getattr(D, "kitrule", False):
        ko = M.kin_ok; m3 = getattr(D, "_m3e", None)
        q, okk, *_ = D.ik(M.Q); m3 = D._m3e
        r["kitrule"] = dict(phi_lo=round(D.p["phi_lo"], 2), phi_hi=round(D.p["phi_hi"], 2), smlo=round(D.p["smlo"], 2), smhi=round(D.p["smhi"], 2),
                            a_deg=[round(D.a1, 2), round(D.a2, 2)], min_margin_taken=round(float(m3[ko].min()), 2) if ko.any() else None)
    r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
    if p.get("near"): r["gap"] = r["gap_near1"]
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


if __name__ == "__main__":
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "plain", r["plain"], "near1", r["gap_near1"],
          "kitrule", r.get("kitrule"), "why", r["why"], "knuckle", r.get("knuckle"), f"{time.time() - t:.0f}s", B.mode)
