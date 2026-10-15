"""Why does a pure 3R shoulder chain lose a clip? Kinematics only (no skin, no shape): in the scapula frame J1's axis b
is fixed and J3's axis is carried by the humerus (HG w). The spherical 3R closes iff the angle theta between them lies
in [|a1 - a2|, a1 + a2]; band_impl.py also keeps J2 sing_deg (10 deg) from folding / stretching. So per frame:
reachable = |a1 - a2| + s <= theta <= a1 + a2 - s (approximately; the exact test is band_impl's chain()).
Reports, per design and clip, the share of frames the KINEMATICS can follow and the theta range the clip needs.
    python3 reach3r.py <designs json (list, or {"designs": [...]})>"""
import json, math, os, sys
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu")); import band_impl as BI

def load():
    P = BI.load_poses(open(os.path.join(HERE, "..", "band_poses.b64")).read(), torch.device("cpu"))
    return {k: (v.numpy() if hasattr(v, "numpy") else v) for k, v in P.items()}

def theta(P, d):
    b = np.array(BI.bvec(d["az"], d["el"])); w = np.array(BI.w_dir(*d["w"])); pz = P["HG"] @ w
    return np.degrees(np.arccos(np.clip(pz @ b, -1, 1)))

def exact_ok(P, d):
    """band_impl's own chain() on CPU: the evaluator's kinematic validity per frame"""
    class _B: pass
    B = BI.Band.__new__(BI.Band); B.t = torch; B.dev = torch.device("cpu"); B.f32 = torch.float32; B.q_step = 12.0; B.SING = 10.0 * BI.D2R
    _, ok, _ = B.chain(dict(d), torch.tensor(P["HG"], dtype=torch.float32)); return ok[:, 0].numpy()

if __name__ == "__main__":
    D = json.load(open(sys.argv[1])); D = D["designs"] if isinstance(D, dict) else D
    P = load(); names = [str(x) for x in P["NAMES"]]; cid = P["CID"]; out = []
    for d in D:
        if d.get("n", 3) != 3 or d.get("cuff"): continue
        th = theta(P, d); ok = exact_ok(P, d); a1, a2 = d["a"]; lo, hi = abs(a1 - a2), a1 + a2
        row = dict(src=d.get("_src", ""), a=[round(a1, 1), round(a2, 1)], theta_window=[round(lo, 1), round(hi, 1)], clips={})
        print(f"{d.get('_src', '')[:58]:58s} arcs {a1:5.1f} + {a2:5.1f}: closes for theta in [{lo:5.1f}, {hi:5.1f}] deg (minus the 10 deg J2 margin)")
        for k, n in enumerate(names):
            m = cid == k; t = th[m]
            row["clips"][n] = dict(kin_follow=round(float(ok[m].mean()), 3), theta_min=round(float(t.min()), 1), theta_max=round(float(t.max()), 1))
            print(f"    {n:24s} kinematics follow {100 * ok[m].mean():5.1f}%   theta needed {t.min():5.1f} .. {t.max():5.1f} deg")
        out.append(row)
    json.dump(out, open(os.path.join(HERE, "reach3r.json"), "w"), indent=1)
