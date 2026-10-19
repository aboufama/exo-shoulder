"""Alignment audit probe (new file, 2026-10-18): does trimlug-k165-knuckle-3r's contact-depth gain depend on reading its
"1.5 mm wall" at the lug's mid-plane only?

The CAD check of the round-11 winner CAD (docs/research/user_slipper_nose_fix_check.md, O2) found that the lug trim
r_trim = farthest flank contact + trim_wall is read at the lug's mid-plane (contact max 19.80 mm); at the lug's top edge
(+1.5 mm along ez) the farthest contact is 20.22 mm over [0, dK_lim] and 20.48 mm over the built stroke (51.75 deg), so
the wall left past the last contact is 1.08 / 0.82 mm, not 1.5. This probe wears the claim's frozen shape (the model
UNCHANGED, only trim_wall varied) with the wall that keeps 1.5 mm at the top edge:
  trim_wall 1.95 -> r_trim 21.72 (20.22 + 1.5), trim_wall 2.21 -> r_trim 21.98 (20.48 + 1.5); 1.5 = the claim; 99 = no trim.
  bench: the model's own `k165` mode (the two elev-165 bench contact poses 237 / 264, Bench(110,360) exact)
  held : the held-out set restricted to the claim's 10 held contact poses (docs/alignment/remeasure/<id>_held_perpose.json)

    SN_CELL=lead CB_EXACT=1 CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_trimlug_edgewall.py 1.5,1.95,2.21,99 out.json
"""
import json, os, sys, importlib.util
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))
RID = "trimlug-k165-knuckle-3r"
sp = importlib.util.spec_from_file_location("tl_edgewall", os.path.join(REPO, "docs", "concepts", "models", RID + ".py"))
TL = importlib.util.module_from_spec(sp); sp.loader.exec_module(TL)
CB = TL.CB
_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
          "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "_trim_info")


def held_subset(P, keep):
    """the claim protocol of the model's frozen() (fit Bench(60,160) fast, shape frozen), worn on the held-out poses keep"""
    P = TL._clamp(dict(TL.PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = TL.TLModel(B1, dict(P)); M1.run(); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(TL.TLModel):
        def fit(self):
            for a in _ATTRS:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    s2 = importlib.util.spec_from_file_location("pkv_edgewall", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    PV = importlib.util.module_from_spec(s2); s2.loader.exec_module(PV); B = PV.held_bench()
    kk = np.asarray(keep, int)
    B.idx = B.idx[kk]; B.kind = [B.kind[j] for j in kk]; B.clip = [B.clip[j] for j in kk]; B.poses = [B.poses[j] for j in kk]; B.res = [None] * len(B.idx)
    M = Frozen(B, P2); M.run()
    return dict(trim=getattr(M1, "_trim_info", None), t5=TL.t5(B, M))


def main(walls, out):
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", RID + ".json")))
    held = json.load(open(os.path.join(REPO, "docs", "alignment", "remeasure", RID + "_held_perpose.json")))
    keep = [p["i"] for p in held["poses"] if p["contact"]]
    res = {}
    for w in walls:
        P = dict(row["best_params"], trim_wall=w)
        b = TL.frozen(dict(P), 110, 360, keep="k165"); h = held_subset(dict(P), keep)
        res[str(w)] = dict(bench_k165=dict(trim=b.get("trim"), t5=b.get("t5")), held_contacts=h)
        print(w, b["t5"]["sum_mm"], h["t5"]["sum_mm"], flush=True)
    json.dump(dict(id=RID, keep_held=keep, walls=res, note=__doc__), open(out, "w"), indent=1, default=float)


if __name__ == "__main__":
    main([float(x) for x in sys.argv[1].split(",")], sys.argv[2])
