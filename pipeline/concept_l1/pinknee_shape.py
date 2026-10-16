"""Export / load the FROZEN fitted shape of a skin-normal-3r-pin-knee configuration, so a builder that cannot see the fit
bench can still wear the verified shape exactly.

Why: the polished H1 was verified under the polish protocol - fit on Bench(110,360) FAST, worn exact - and that bench's
fast grid cache (key 14f156cb6fc8) exists only on the farm, while the full user-style CAD (user_style_pinknee.py) needs
OCC (cadquery), which only this box has. So the farm fits the model and pickles exactly the attributes the verifiers hand
over in their frozen-shape protocol (docs/concepts/verify/skin-normal-3r-pin-knee.py frozen_model: g, fr, geo, rigid,
link_pts, f, tr, zb, _tr_fit, cyl, box, strap, cyl_surf, Emid, Hneed, Lneed, hEx, _Ex, _h12, contact; params + m_fix)
plus the fit's link rows (build_pinknee_l1.link_rows on the FIT model, whose drop mask belongs to the fit bench); the
builder then wears that shape on any local bench (no refit) - the same hand-over the verifier made.

    farm:  python3 tools/osn_polish.py assemble 110 360 osnp/b110_360 /tmp/osnpb && \
           python3 pipeline/concept_l1/pinknee_shape.py --fit-bench 110,360 --out .cache/pk_shapes/h1_b110_360.pkl [--params-file F]
    local: import pinknee_shape; M, shape = pinknee_shape.wear(".cache/pk_shapes/h1_b110_360.pkl")   (Bench(60,160) fast)
"""
import argparse, json, os, pickle, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_pinknee_l1 as PK                                                   # noqa: E402

ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
         "Hneed", "Lneed", "hEx", "_Ex", "_h12")


def _register():
    sys.modules[PK.MK.__name__] = PK.MK                                         # pickle finds _Geo etc. by module name


def export(P, src, fb, out):
    import concept_kit as KIT
    t0 = time.time(); M, rep = PK.fit(P, fb); _register()
    shape = dict(params=P, source=src, fit_bench=list(fb), mode=M.B.mode, fold_margin=float(KIT.FOLD_MARGIN),
                 p=dict(M.p), m_fix=[float(x) for x in M.D.m], hr=list(M.hr),
                 attrs={a: getattr(M, a) for a in ATTRS if hasattr(M, a)}, contact=list(M.contact),
                 link_rows=PK.link_rows(M),
                 report={k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "f", "min_clear_taken", "parts_ib14")},
                 created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as fh: pickle.dump(shape, fh, protocol=4)
    print(f"fit ({src}) on Bench{tuple(fb)} {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: gap {rep['gap']} f {np.round(M.f, 3).tolist()} "
          f"tr {M.tr:.3f} m {np.round(M.D.m, 3).tolist()} -> {out} ({os.path.getsize(out) / 1e6:.1f} MB, {time.time() - t0:.0f} s)", flush=True)


def load(path):
    _register()
    with open(path, "rb") as fh: return pickle.load(fh)


def wear(path, bench=(60, 160)):
    """the frozen shape worn on a local FAST bench (no refit): returns (M, shape); M._bench, M._link_rows set for the builders"""
    shape = load(path); CB = PK.CB
    old = os.environ.pop("CB_EXACT", None)
    try: B = CB.Bench(int(bench[0]), int(bench[1]))
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(shape["p"]); P2["m_fix"] = list(shape["m_fix"])

    class Frozen(PK.MK.Model):
        def fit(self):
            for a, v in shape["attrs"].items(): setattr(self, a, v)
            self.contact = list(shape["contact"]); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(B, P2); r = M.run(); M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q); M._link_rows = shape["link_rows"]; M._wear_report = r
    return M, shape


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--params"); ap.add_argument("--params-file"); ap.add_argument("--k", type=int); ap.add_argument("--hubs")
    ap.add_argument("--fit-bench", default="110,360")
    a = ap.parse_args(); P, src = PK.params_from(a); export(P, src, tuple(int(x) for x in a.fit_bench.split(",")), a.out)


if __name__ == "__main__":
    main()
