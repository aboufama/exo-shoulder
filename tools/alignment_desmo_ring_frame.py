#!/usr/bin/env python3
"""Alignment audit instrument (new file; the model, verifier and bench run UNCHANGED): re-wear desmo-conecut-knuckle-3r's
verified config with the stage-1 cap-ring metal sampled in link 2's TRUE member frame.

Why: DCModel._desmo_build_B (docs/concepts/models/desmo-conecut-knuckle-3r.py, line 205) maps the groove into link 2 with
rotm(u2, -(q2 - q_on)), i.e. the frame link 2 has at the K onset (q_on = 7.28 deg), then attaches the ring samples to
link 2's member as if they were in its home frame (q2 = 0). The gen-9 CAD (pipeline/full-exo/designs/user_desmo_conecut)
found the samples 7.28 deg off about u2. This tool
  1. MEASURES which frame the pin really runs in: the stage-1 pin (crank member 9, home point F0) carried through every
     kin-ok pose's own transforms into link 2's home frame, its azimuth about u2 on the model's (bx, by) basis, against
     the azimuth span of the model's ring samples (as built and rotated by -q_on);
  2. with --fix (default) rotates ring2 (rigid) and the ring contact set by -q_on about u2 after the model built them,
     and re-wears through the verifier's own harness (docs/concepts/verify/desmo-conecut-knuckle-3r.py wear, --blend:
     the blended-law IK of the verified 18.98).

  CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_desmo_ring_frame.py <bench|held> <out.json> --blend
        [--nofix] [--set k=v ...] [--dump PATH]
--set changes a parameter (e.g. glev / a_s / psi for the stage-1 level re-wear); it is a variant, reported as such.
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--blend" not in sys.argv: sys.argv.append("--blend")       # the verified number is the blended-law IK wear


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("desmoconecut_verify_ringframe", os.path.join(REPO, "docs", "concepts", "verify", "desmo-conecut-knuckle-3r.py"))
DC, S = V.DC, V.S
FIX = "--nofix" not in sys.argv
LOG = []
_orig = DC.DCModel._desmo_build_B


def _rot(u, a):
    R = np.asarray(S.rotm(np.asarray(u, float), a), float)
    return R[0] if R.ndim == 3 else R


def _az(P, bx, by):
    return np.degrees(np.unwrap(np.arctan2(P @ by, P @ bx)))


def build_wrapped(self):
    n0 = len(self.contact)
    out = _orig(self)
    d = getattr(self, "_desmo", None)
    if not d or "ring2" not in self.rigid: return out
    u2, q_on, bx, by, F0 = d["u2"], float(d["q_on"]), d["bx"], d["by"], d["F0"]
    m2, ring = self.rigid["ring2"]
    R = _rot(u2, -q_on)
    rec = dict(q_on_deg=round(math.degrees(q_on), 3), n_ring=int(len(ring)))
    az_model = _az(ring, bx, by); rec["ring_az_model_deg"] = [round(float(az_model.min()), 2), round(float(az_model.max()), 2)]
    az_fix = _az(ring @ R.T, bx, by); rec["ring_az_fixed_deg"] = [round(float(az_fix.min()), 2), round(float(az_fix.max()), 2)]
    # where the pin really runs in link 2's home frame (the posed transforms of the crank (member 9) and link 2)
    try:
        idx = np.nonzero(np.asarray(self.kin_ok, bool))[0]; az_pin, kk = [], []
        for i in idx:
            R9, t9 = self.T(9, i); R2, t2 = self.T(m2, i)
            pw = R9 @ F0 + t9; p2 = R2.T @ (pw - t2)
            az_pin.append(math.degrees(math.atan2(float(p2 @ by), float(p2 @ bx)))); kk.append(abs(math.degrees(float(self.dK[i]))))
        az_pin = np.array(az_pin); kk = np.array(kk); mv = kk > 0.01
        rec["pin_az_in_link2_deg"] = dict(all=[round(float(az_pin.min()), 2), round(float(az_pin.max()), 2)],
                                          moving=[round(float(az_pin[mv].min()), 2), round(float(az_pin[mv].max()), 2)] if mv.any() else None,
                                          n=int(len(az_pin)), n_moving=int(mv.sum()), dK_max=round(float(kk.max()), 2))
        # model groove centreline G2 rebuilt the model's way would sit at the ring's azimuth band minus the 3-deg pads
        rec["pin_inside_model_ring_band"] = float(np.mean((az_pin >= az_model.min()) & (az_pin <= az_model.max())))
        rec["pin_inside_fixed_ring_band"] = float(np.mean((az_pin >= az_fix.min()) & (az_pin <= az_fix.max())))
    except Exception as e:
        rec["pin_check_error"] = repr(e)[:300]
    if FIX:
        self.rigid["ring2"] = (m2, ring @ R.T)
        nfix = 0
        for j in range(n0, len(self.contact)):
            m, X = self.contact[j]
            if m == m2 and len(X): self.contact[j] = (m, np.asarray(X) @ R.T); nfix += 1
        rec["fixed_contact_sets"] = nfix
    rec["fix"] = FIX
    LOG.append(rec)
    return out


DC.DCModel._desmo_build_B = build_wrapped


if __name__ == "__main__":
    which, path = sys.argv[1], sys.argv[2]
    P = dict(V.BEST); sets = {}
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_); sets[k_] = float(v_)
    dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
    t = time.time()
    res = V.wear(P, which, False, dump)
    res.update(exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets, blend=True, blend_ik=dict(V._BL), fix_ring_frame=FIX,
               ring_frame_log=LOG[-3:], n_builds=len(LOG), tool="tools/alignment_desmo_ring_frame.py", secs_total=round(time.time() - t, 1))
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: res.get(k) for k in ("wear", "frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "n_taken", "contacts", "v3_th_margin",
                                              "sets", "fix_ring_frame", "secs_total")} | {"ring": LOG[-1] if LOG else None,
                                                                                       "gates": {k: (res.get("v1_fit_gates") or {}).get(k) for k in ("desmo_fail", "dK_lim", "why_lim", "stage1_pa", "stage1_rc_min")}}, default=float))
