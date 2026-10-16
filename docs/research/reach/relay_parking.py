"""Where does hub 2 go when a two-state relay / rocker rescues a folded pose? (2026-10-16, reach attribution lever check)

At a leader's verified seats (J1 scapula-fixed, J3 humerus-fixed, arcs a1 / a2), the kinematic ceiling of a two-state
relay on the J1-J2 arc (a1 -> a1' per pose: a detented mid-joint in link 1) is 0.93-0.95 of the workspace
(docs/research/reach/ceilings.json). This measures the price: per pose, the skin requirement along the J2 axis ray (the
level a hub face on that ray must sit at to clear the skin by 2 mm, K3 march, exact distance) in state A (the leader's
arcs, poses it takes) and in state B (a1', the poses only B closes), both branches. A hub on a GH ray is a disc at ONE
level on its link; if B's poses need it much higher than A's, the relay buys reach with hub 2 off the skin.

    OMP_NUM_THREADS=1 CB_EXACT=1 CB_QUIET_EXACT=1 nice -n 10 python3 docs/research/reach/relay_parking.py [leader] [a1']
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB, concept_kit as K                 # noqa: E402


def main():
    leader = sys.argv[1] if len(sys.argv) > 1 else "pin-knee"
    s = importlib.util.spec_from_file_location("ce", os.path.join(HERE, "ceilings.py")); ce = importlib.util.module_from_spec(s); s.loader.exec_module(ce)
    seats = ce.leader_seats()[leader]; C = json.load(open(os.path.join(HERE, "ceilings.json")))["leaders"][leader]
    a1, a2 = seats["a1"], seats["a2"]; a1b = float(sys.argv[2]) if len(sys.argv) > 2 else float(C["relay_two_state_m10"]["a1"]["alt"])
    t0 = time.time(); B = CB.Bench(110, 360); F = K.frames(B); ws = np.array(B.kind) == "ws"
    el = np.array([p["elev"] for p in B.poses])
    p1 = F.S(seats["u1"]); p3 = F.HG(seats["u3"])
    th = np.degrees(np.arccos(np.clip((K.unit(p1) * K.unit(p3)).sum(-1), -1, 1)))
    inA = (th >= abs(a1 - a2) + 10) & (th <= a1 + a2 - 10); inB = (th >= abs(a1b - a2) + 10) & (th <= min(a1b + a2, 360 - a1b - a2) - 10)
    out = dict(leader=leader, a1=a1, a2=a2, a1_relay=a1b, n_ws=int(ws.sum()), A_ws=round(float(inA[ws].mean()), 4),
               AorB_ws=round(float((inA | inB)[ws].mean()), 4), B_only_ws=int((inB & ~inA & ws).sum()),
               B_only_overhead=int((inB & ~inA & ws & (el >= 140)).sum()))
    I = np.arange(len(B.idx)); res = {}
    for name, a, sel in (("A", a1, inA), ("B", a1b, inB & ~inA)):
        for sg in (1, -1):
            p2, ok, _ = K.closure(p1, p3, a, a2, sg, margin_deg=10.0); m = sel & ok
            R = np.full(len(I), np.nan)
            if m.any(): R[m] = K.requirement(B, I[m], K.unit(p2[m]))
            R = np.where(np.isfinite(R), R, 400.0)
            q = lambda x: round(float(np.percentile(R[m & x], 50)), 1) if (m & x).any() else None
            res[f"{name}_sigma{sg:+d}"] = dict(n=int(m.sum()), med=q(np.ones(len(I), bool)), p10=round(float(np.percentile(R[m], 10)), 1) if m.any() else None,
                                                p90=round(float(np.percentile(R[m], 90)), 1) if m.any() else None,
                                                overhead_med=q(el >= 140), share_le_60=round(float((R[m] <= 60).mean()), 3) if m.any() else None,
                                                share_le_75=round(float((R[m] <= 75).mean()), 3) if m.any() else None)
            print(name, sg, res[f"{name}_sigma{sg:+d}"], flush=True)
    out["hub2_ray_requirement_mm"] = res; out["secs"] = round(time.time() - t0, 1)
    p = os.path.join(HERE, f"relay_parking_{leader}.json"); json.dump(out, open(p, "w"), indent=1, default=float); print(json.dumps(out)[:1500])


if __name__ == "__main__":
    main()
