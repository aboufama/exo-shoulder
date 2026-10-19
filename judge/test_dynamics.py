"""Validation of judge/dynamics.py.
  1. Single hinge, analytic (the judge's own solver options, option_xml, and friction update, load_friction_update):
     a link on a hinge whose axis passes through the origin, driven through a stiff torsion spring by a prescribed angle.
     (a) constant speed, no gravity: the steady spring torque is the Coulomb friction (0.2 N.m), also at 0.01 rad/s,
         where MuJoCo's default soft frictionloss gives a viscous 0.001 N.m (the reason for noslip in the judge);
     (b) constant angular acceleration: torque = I_axis alpha + friction (inertia about the axis through the origin);
     (c) below breakaway: a constant 0.15 N.m against 0.2 N.m friction does not move the joint;
     (d) load-dependent friction: the COM sits off the hinge so gravity loads the bearing with a known tilt couple
         m g x d about the bearing centre; the steady spring torque is tau0 + mu m g d.
  2. The chain, quasi-static (judge.dynamics.validate): band_r14_3r_s1351_1 at x0.25 speed, no gravity, stiff cuff:
     |M_GH| / friction vs transmission.py's friction amplification on its 10 fps frames, p95 relative error < 3 %.
  3. The load-dependent friction vs rt_wedge.py (judge.dynamics.validate_wedge, Wash opposite shoulder, mu_eff 0.25):
     unlocked frames match the exact quasi-static solution, frames rt_wedge.py calls locked need >= 10x the
     constant-friction moment.
  4. (--general) the general N-member chain judge.dynamics.GenDesign against the spherical path on the same 3R (part4).
    python3 judge/test_dynamics.py [--fast]   (--fast: 2 clips in part 2; about 1-2 min on 4 cores)
    python3 judge/test_dynamics.py --general  (part 4 only)"""
import math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mujoco
import dynamics as DY

def hinge_model(friction, I=2e-4, m=0.1, com=(0.0, 0.0, 0.0), gravity=False, dt=2e-4, soft=False):
    opt = DY.option_xml(dt, gravity) if not soft else f'<option timestep="{dt}" gravity="0 {-9.81 if gravity else 0} 0" integrator="implicitfast"/>'
    xml = f"""<mujoco>{opt}<worldbody><body name="l"><joint name="j" type="hinge" axis="0 0 1" frictionloss="{friction}"/>
    <inertial pos="{com[0]} {com[1]} {com[2]}" mass="{m}" diaginertia="{I} {I} {I}"/></body></worldbody></mujoco>"""
    M = mujoco.MjModel.from_xml_string(xml); return M, mujoco.MjData(M)

def drive(M, d, theta, T, K=200.0, load=None):
    """drive the hinge through a torsion spring K from the prescribed angle theta(t); mean spring torque over the 2nd half"""
    dt = M.opt.timestep; I = M.body_inertia[1][2] + M.body_mass[1] * (M.body_ipos[1][0] ** 2 + M.body_ipos[1][1] ** 2); C = 2 * 0.7 * math.sqrt(K * I)
    taus = []
    for i in range(int(round(T / dt))):
        t = d.time; th, w = theta(t)
        tau = K * (th - d.qpos[0]) + C * (w - d.qvel[0]); d.qfrc_applied[0] = tau; mujoco.mj_step(M, d)
        if load: load(M, d)
        if t > T / 2: taus.append(tau)
    return float(np.mean(taus)), float(np.std(taus))

def part1():
    ok = True; tf = 0.2
    for w in (0.01, 1.0):
        for soft in (False, True):
            M, d = hinge_model(tf, soft=soft); mu, sd = drive(M, d, lambda t: (w * t, w), 2.0)
            good = abs(mu - tf) < 0.005 * tf if not soft else True
            print(f"  (a) {'default soft friction' if soft else 'judge options      '} speed {w:5.2f} rad/s: spring torque {mu:.5f} N.m (Coulomb {tf}) {'' if soft else ('ok' if good else 'FAIL')}")
            ok &= good
    al = 5.0; I = 2e-4; m = 0.1; com = (0.05, 0.0, 0.0); Iax = I + m * 0.05 ** 2
    M, d = hinge_model(tf, I=I, m=m, com=com); d.qvel[0] = 0.5                              # start sliding so the sign is known
    mu, sd = drive(M, d, lambda t: (0.5 * t + 0.5 * al * t * t, 0.5 + al * t), 1.0, K=2000.0)
    exp = Iax * al + tf; g = abs(mu - exp) < 0.01 * exp; ok &= g
    print(f"  (b) constant acceleration {al} rad/s^2, I_axis {Iax:.2e} kg m^2: spring torque {mu:.5f} vs I alpha + friction {exp:.5f} {'ok' if g else 'FAIL'}")
    M, d = hinge_model(tf); moved = 0.0
    for _ in range(5000): d.qfrc_applied[0] = 0.15; mujoco.mj_step(M, d); moved = max(moved, abs(d.qpos[0]))
    g = moved < 1e-6; ok &= g; print(f"  (c) 0.15 N.m against 0.2 N.m friction: joint moved {moved:.2e} rad {'ok' if g else 'FAIL'}")
    tau0, mu_e, mm, dz = 0.02, 0.25, 0.5, 0.04                                                 # COM 40 mm along the axis from the bearing centre, 30 mm off it
    M, d = hinge_model(tau0, I=1e-4, m=mm, com=(0.03, 0.0, dz), gravity=True)               # gravity -y, hinge axis z: tilt couple = m g dz about x
    jid = [0]; child = [1]; root = 1
    upd = lambda M_, d_: DY.load_friction_update(M_, d_, child, jid, [0], [0.0], root, tau0, mu_e)
    mujoco.mj_forward(M, d); upd(M, d)
    # the hinge also carries gravity's moment about the axis (m g x cos q): drive at constant speed over a full turn so it averages out
    w = 2 * math.pi / 2.0; mu, sd = drive(M, d, lambda t: (w * t, w), 4.0, K=400.0, load=upd)
    exp = tau0 + mu_e * mm * 9.81 * math.hypot(dz, 0.0)
    # tilt couple about the bearing centre (origin) from gravity: |r x F| perpendicular to z = m g dz (exact, any angle)
    g = abs(mu - exp) < 0.02 * exp; ok &= g
    print(f"  (d) load-dependent friction tau0 {tau0} + mu {mu_e} x tilt {mm * 9.81 * dz:.4f} N.m: mean spring torque over a turn {mu:.5f} vs {exp:.5f} {'ok' if g else 'FAIL'}")
    return ok

def part4(clips=("Raise overhead", "Wash opposite shoulder")):
    """the general N-member chain (GenDesign: hinges fitted to the clips' member frames, used for offset-axis / split-member /
    knee designs) against the original spherical-chain path on the same 3R design, contacts off in both: (a) constant
    friction 0.05 N.m (the chain construction alone: within 2 % or the summaries' rounding step), (b) the nominal rolling-bearing law (also differs by
    the bearing centre: the hinge anchor at the hub stack centre vs a point on the GH ray at the hubs' mid-radius)"""
    ok = True; dS = DY.Design("band_r14_3r_s1351_1"); dG = DY.GenDesign("band_r14_3r_s1351_1")
    print(f"  hinge fit residuals {[(k, v['rot_residual_deg'], v['point_residual_mm']) for k, v in dG.fit.items()]}")
    for lab, kw, tol in (("constant 0.05 N.m", dict(friction=0.05), 0.02), ("rolling mu 0.005", dict(mu_eff=0.005, tau0=0.001, tilt="hub"), 0.05)):
        for c in clips:
            ci = [x["name"] for x in dS.clips].index(c)
            DY.DES = dS; a = DY.run(dS, ci, contacts=False, **kw)[0]; DY.DES = dG; b = DY.run(dG, ci, contacts=False, **kw)[0]
            pairs = [("M_GH peak", a["moment_gh_Nm"]["peak"], b["moment_gh_Nm"]["peak"], 0.005), ("M_GH rms", a["moment_gh_Nm"]["rms"], b["moment_gh_Nm"]["rms"], 0.005),
                     ("F peak", a["force_N"]["peak"], b["force_N"]["peak"], 0.0101), ("twist peak", a["tracking_deg"]["twist_peak"], b["tracking_deg"]["twist_peak"], 0.0501)]
            rel = max(abs(y - x) / max(abs(x), 1e-3) for _, x, y, _ in pairs)                # the summaries are rounded (N to 0.01): small values also pass on the rounding step
            g = all(abs(y - x) <= max(tol * abs(x), at) for _, x, y, at in pairs); ok &= g
            print(f"  ({lab}) {c:24s} " + "  ".join(f"{n} {x:.4f}/{y:.4f}" for n, x, y, _ in pairs) + f"  max rel diff {rel:.4f} {'ok' if g else 'FAIL'}")
    return ok

if __name__ == "__main__":
    fast = "--fast" in sys.argv; t0 = time.time(); ok = True
    if "--general" in sys.argv:
        print("4. general N-member chain vs the spherical chain (band_r14_3r_s1351_1)"); ok = part4()
        print(f"{'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f}s)"); sys.exit(0 if ok else 1)
    print("1. single hinge, analytic"); ok &= part1()
    print("2. chain vs transmission.py (quasi-static, constant friction)")
    des = DY.Design("band_r14_3r_s1351_1")
    v = DY.validate(des, clips=["Wash opposite shoulder", "Raise overhead"] if fast else None, jobs=min(4, os.cpu_count() or 1), log=lambda *_: None)
    print(f"  {v['frames_compared']} frames: relative error median {v['rel_err_median']}, p95 {v['rel_err_p95']}, max {v['rel_err_max']} -> {'ok' if v['ok'] else 'FAIL'}"); ok &= bool(v["ok"])
    print("3. load-dependent friction vs rt_wedge.py (Wash opposite shoulder, mu_eff 0.25)")
    w = DY.validate_wedge(des, mus=(0.25,), jobs=min(4, os.cpu_count() or 1), log=lambda *_: None, clips=["Wash opposite shoulder"])
    print(f"  unlocked {w['unlocked_frames']} frames: rel. error median {w['unlocked_rel_err_median']} p95 {w['unlocked_rel_err_p95']}; locked {w['locked_frames']} frames need "
          f"{w['locked_moment_over_constant_friction']} x the constant-friction moment; onset {w['onset']} -> {'ok' if w['ok'] else 'FAIL'}"); ok &= bool(w["ok"])
    print(f"{'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f}s)")
    sys.exit(0 if ok else 1)
