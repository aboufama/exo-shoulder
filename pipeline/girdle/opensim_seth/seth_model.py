"""Seth et al. 2016 scapulothoracic shoulder model in OpenSim 4.6: ISB frames, ISB angles and a rhythm-driven girdle fit.

Run with the isolated OpenSim venv:  .cache/opensim-venv/bin/python pipeline/girdle/opensim_seth/<script>.py

Model: Seth A, Matias R, Veloso AP, Delp SL (2016) PLoS One 11(1):e0141028, "ScapulothorachicJoint_Shoulder.osim"
(Stanford Digital Repository purl.stanford.edu/br087nj9017, CC BY-NC-SA 3.0). The generic model file is read unchanged;
OpenSim 4.6 upgrades the 3.2 XML in memory (its built-in ScapulothoracicJoint replaces the 3.2 plugin).

Frames (all positions in mm):
  model thorax  = the thorax body frame of the model (x anterior, y up, z right; gravity -y; thorax locked to ground).
  ISB thorax    = Wu et al. 2005 from the model's own IJ, C7, PX, T8 markers: origin IJ, Yt = mid(PX,T8) -> mid(IJ,C7),
                  Zt normal to (IJ, C7, mid(PX,T8)) pointing right, Xt = Yt x Zt (anterior). Rotated +7.9 deg about z
                  from the model thorax frame (Yt leans back).
  ISB clavicle  Zc = SC -> AC (markers sc, acc), Xc perpendicular to Zc and Yt (anterior).  Y-X-Z vs ISB thorax.
  ISB scapula   origin AA, Zs = TS -> AA, Xs normal to (AI, AA, TS) anterior, Ys = Zs x Xs.  Y-X-Z vs ISB thorax.
  ISB humerus   Yh = mid(EpL, EpM) -> GH, Xh normal to (EpL, EpM, GH) anterior, Zh = Xh x Yh.  Y-X-Y vs ISB thorax.
Angle signs (Ludewig 2009 reporting, = ISB Y-X-Z intrinsic R = Ry(a) Rx(b) Rz(c)):
  clavicle  retraction = -a, elevation = -b          (axial rotation c is not a DOF of the model's SC joint)
  scapula   internal rotation = a, upward rotation = -b, posterior tilt = c
  humerus   Y-X-Y: plane = a (0 abduction, 90 flexion), elevation = -b, axial = c
"""
import math, os
import numpy as np
import opensim as osim

osim.Logger.setLevelString("error")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODEL = os.path.join(REPO, ".cache", "ext", "seth2016", "x", "ShoulderModel", "ScapulothorachicJoint_Shoulder.osim")
GIRDLE = ["clav_prot", "clav_elev", "scapula_abduction", "scapula_elevation", "scapula_upward_rot", "scapula_winging"]
GHC = ["shoulder_elv", "plane_of_elev", "axial_rot"]
ANG = ["ret", "elev", "IR", "UR", "PT"]                     # clavicle retraction, clavicle elevation, scapula IR, UR, PT
D = math.pi / 180


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def v3(v): return np.array([v.get(0), v.get(1), v.get(2)])


def yxz(R):
    """ISB Y-X-Z intrinsic angles (deg) of R = Ry(a) Rx(b) Rz(c)"""
    b = math.asin(max(-1.0, min(1.0, -R[1, 2]))); a = math.atan2(R[0, 2], R[2, 2]); c = math.atan2(R[1, 0], R[1, 1])
    return np.degrees([a, b, c])


def yxy(R):
    """ISB Y-X-Y intrinsic angles (deg) of R = Ry(a) Rx(b) Ry(c), branch b <= 0 (elevation = -b >= 0)"""
    th = math.acos(max(-1.0, min(1.0, R[1, 1])))
    if th < 1e-9: return np.array([0.0, 0.0, math.degrees(math.atan2(R[0, 2], R[0, 0]))])
    return np.degrees([math.atan2(-R[0, 1], -R[2, 1]), -th, math.atan2(-R[1, 0], R[1, 2])])


class Seth:
    def __init__(self, path=MODEL, relax_deg=None):
        """relax_deg: in memory only, give the 6 girdle coordinates the range +-relax_deg and clamped = False (the
        distributed file clamps all six to +-45 deg); the file on disk is never changed"""
        self.m = osim.Model(path); m = self.m
        if relax_deg:
            for c in m.getCoordinateSet():
                if c.getName() in GIRDLE: c.set_range(0, -relax_deg * D); c.set_range(1, relax_deg * D); c.set_clamped(False)
            m.finalizeFromProperties()
        self.s = m.initSystem(); self.relax_deg = relax_deg
        self.cs = {c.getName(): c for c in m.getCoordinateSet()}
        B = m.getBodySet(); self.body = {n: B.get(n) for n in ["thorax", "clavicle", "scapula", "humerus"]}
        self.mk = {mk.getName(): (mk.getParentFrame().getName(), v3(mk.get_location())) for mk in m.getMarkerSet()}
        ac = osim.PointConstraint.safeDownCast(m.getConstraintSet().get("AC"))
        self.ac_clav, self.ac_scap = v3(ac.get_location_body_1()), v3(ac.get_location_body_2())
        self.ac_bodies = tuple(ac.getSocket(k).getConnecteeAsObject().getName() for k in ("body_1", "body_2"))
        Tg = self.body["thorax"].getTransformInGround(self.s)
        assert np.allclose(v3(Tg.p()), 0) and np.allclose(self.R_of(Tg), np.eye(3)), "thorax not at ground"
        # ISB thorax from the model's thorax markers (thorax frame = ground)
        IJ, C7, PX, T8 = (self.mk[n][1] * 1000 for n in ["ij", "c7", "px", "t8"])
        Y = unit((IJ + C7) / 2 - (PX + T8) / 2); Z = unit(np.cross(C7 - IJ, (PX + T8) / 2 - IJ))
        if Z[2] < 0: Z = -Z
        X = unit(np.cross(Y, Z)); Z = np.cross(X, Y)
        self.RT, self.IJ = np.c_[X, Y, Z], IJ                    # columns = ISB thorax axes in model-thorax coords
        lim = (relax_deg or 90) * D                                     # optimiser bounds: the clamped range, else +-relax (90) deg
        self.lo = np.array([self.cs[n].getRangeMin() if self.cs[n].getDefaultClamped() else -lim for n in GIRDLE])
        self.hi = np.array([self.cs[n].getRangeMax() if self.cs[n].getDefaultClamped() else lim for n in GIRDLE])

    @staticmethod
    def R_of(T):
        M = T.R().asMat33(); return np.array([[M.get(i, j) for j in range(3)] for i in range(3)])

    # ----------------------------------------------------------------- state
    def set_q(self, names, vals):
        for n, v in zip(names, vals): self.cs[n].setValue(self.s, float(v), False)
        self.m.realizePosition(self.s)

    def get_q(self, names): return np.array([self.cs[n].getValue(self.s) for n in names])

    def pose(self):
        """{body: (R, p_mm)} in the model thorax (= ground) frame"""
        out = {}
        for n in ["clavicle", "scapula", "humerus"]:
            T = self.body[n].getTransformInGround(self.s); out[n] = (self.R_of(T), v3(T.p()) * 1000)
        return out

    def points(self, P=None):
        """landmarks in the model thorax frame (mm)"""
        P = P or self.pose(); at = lambda b, loc: P[b][0] @ (np.asarray(loc) * 1000) + P[b][1]
        q = {n: at(b, loc) for n, (b, loc) in self.mk.items() if b in P}
        q["ACj_c"] = at("clavicle", self.ac_clav); q["ACj_s"] = at("scapula", self.ac_scap)
        q["GH"] = P["humerus"][1]; q["SC"] = P["clavicle"][1]
        return q

    def to_isb(self, x): return self.RT.T @ (np.asarray(x) - self.IJ)          # point: model thorax -> ISB thorax (mm)
    def dir_isb(self, v): return self.RT.T @ np.asarray(v)

    # ----------------------------------------------------------------- ISB angles (deg) vs the ISB thorax
    def girdle_angles(self, q):
        Zc = unit(self.dir_isb(q["acc"] - q["sc"]))
        a_c = math.degrees(math.atan2(Zc[0], Zc[2])); b_c = -math.degrees(math.asin(Zc[1]))   # Y-X-Z of the clavicle
        AA, TS, AI = (self.dir_isb(q[n]) for n in ["aa", "ts", "ai"])
        Zs = unit(AA - TS); Xs = unit(np.cross(AA - TS, AI - TS)); Ys = np.cross(Zs, Xs)
        a, b, c = yxz(np.c_[Xs, Ys, Zs])
        return np.array([-a_c, -b_c, a, -b, c])                  # ret, elev, IR, UR, PT

    def humerus_angles(self, q):
        GH, EL, EM = (self.dir_isb(q[n]) for n in ["gu", "EpL", "EpM"])
        Yh = unit(GH - (EL + EM) / 2); Xh = unit(np.cross(EL - GH, EM - GH)); Zh = np.cross(Xh, Yh); Xh = np.cross(Yh, Zh)
        a, b, c = yxy(np.c_[Xh, Yh, Zh]); return np.array([a, -b, c])   # plane, elevation, axial

    def ac_err(self, q): return q["ACj_c"] - q["ACj_s"]

    # ----------------------------------------------------------------- fits
    def fit_girdle(self, target, w=np.ones(5), q0=None, wc=100.0, polish=True):
        """6 girdle coordinates minimising sum (w (angle - target))^2 (deg) with the AC constraint (|AC error| * wc, mm),
        then OpenSim's assembler to close the AC constraint exactly. Returns dict."""
        from scipy.optimize import least_squares
        target, w = np.asarray(target, float), np.asarray(w, float)
        q0 = self.get_q(GIRDLE) if q0 is None else np.clip(q0, self.lo + 1e-9, self.hi - 1e-9)

        def res(x):
            self.set_q(GIRDLE, x); q = self.points(); return np.r_[w * (self.girdle_angles(q) - target), wc * self.ac_err(q)]
        sol = least_squares(res, q0, bounds=(self.lo, self.hi), x_scale=0.1, xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=2000)
        self.set_q(GIRDLE, sol.x)
        if polish: self.m.assemble(self.s); self.m.realizePosition(self.s)
        q = self.points(); x = self.get_q(GIRDLE); ang = self.girdle_angles(q)
        return dict(x=x, ang=ang, res=ang - target, ac_err=float(np.linalg.norm(self.ac_err(q))),
                    qerr=float(np.abs(np.array([self.s.getQErr().get(i) for i in range(self.s.getQErr().size())])).max()) if self.s.getQErr().size() else 0.0,
                    at_bound=[GIRDLE[i] for i in range(6) if min(x[i] - self.lo[i], self.hi[i] - x[i]) < 1e-6], nfev=sol.nfev, pts=q)

    def fit_humerus(self, plane, elev, q0=None):
        """shoulder_elv, plane_of_elev with axial_rot = 0 so that the humerus long axis has ISB thorax plane / elevation"""
        from scipy.optimize import least_squares
        p, t = plane * D, elev * D; d = np.array([math.sin(p) * math.sin(t), -math.cos(t), math.cos(p) * math.sin(t)])
        self.cs["axial_rot"].setValue(self.s, 0.0, False)

        def res(x):
            self.set_q(GHC[:2], x); q = self.points()
            GH, EL, EM = (self.dir_isb(q[n]) for n in ["gu", "EpL", "EpM"]); return unit((EL + EM) / 2 - GH) - d
        q0 = self.get_q(GHC[:2]) if q0 is None else q0
        sol = least_squares(res, q0, xtol=1e-12, ftol=1e-12, gtol=1e-12)
        self.set_q(GHC[:2], sol.x); q = self.points()
        return dict(x=self.get_q(GHC), ang=self.humerus_angles(q), dir_err_deg=math.degrees(2 * math.asin(min(1, np.linalg.norm(sol.fun) / 2))), pts=q)
