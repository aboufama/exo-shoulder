"""Sweep adapter for tools/concept_baseline.py (the champion spherical 3R on the concept bench), in the
tools/concept_sweep.py model contract: PARAMS + bench_eval(B, params) -> bench report. A config is a partial CHAMP
(az, el, a, w, branch, hub_r, stack, t_link, sing_deg, width, clear, neck_deg) plus "pcts" (profile percentiles tried;
the best gap is reported, its percentile in "pct"). Also the farm's reference model for local-vs-farm checks
(docs/CLOUD_RUN.md, "For screening agents")."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_baseline as CBL                                  # noqa: E402

PARAMS = dict(CBL.CHAMP, pcts=[60, 70, 80, 90, 95, 100])


def bench_eval(B, params):
    p = dict(params); pcts = tuple(p.pop("pcts"))
    best, rows, _ = CBL.build(p, n_clip=sum(k == "clip" for k in B.kind), n_ws=sum(k == "ws" for k in B.kind),
                              pcts=pcts, log=lambda *a: None)
    return best
