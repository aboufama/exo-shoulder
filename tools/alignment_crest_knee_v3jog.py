"""Alignment audit adapter (crest-knee-3r, 2026-10-19): run the round-3 skeptic's NEW checks
(docs/concepts/verify/crest-knee-3r-v3.py: J2 single arc from body transforms, J3 window on the true link2->member3
angle, knee-pin rotations, per-part sample density, pin-a stack) on the cell the row's v_* fields actually carry, the
JOGGLED knee (row key best_params_joggle, kj=1, CK.JogModel). The 12:06 re-run applied them to the flat cell only.

The v3 source is executed UNCHANGED except three lines: the model class (JogModel, as the joggle verifier does), the
parameter set (best_params_joggle) and the two output paths (redirected to docs/alignment/remeasure/
crest-knee-3r_v3jog_<wear>{,_perpose}.json so no verifier file is touched). No bench, model or row is edited.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_crest_knee_v3jog.py <bench|held>
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "docs", "concepts", "verify", "crest-knee-3r-v3.py")
which = sys.argv[1]
src = open(SRC).read()
reps = [
    ('which = sys.argv[1]; P = dict(V.ROW["best_params"]); t0 = time.time()',
     'which = sys.argv[1]; V.CK.Model = V.CK.JogModel; P = dict(V.ROW["best_params_joggle"]); assert P.get("kj") == 1; '
     'V.ROW = dict(V.ROW); V.ROW["best_params"] = P; t0 = time.time()'),
    ('open(os.path.join(OUT, f"crest-knee-3r_v3_{which}_perpose.json"), "w")',
     'open(os.path.join(OUT, f"crest-knee-3r_v3jog_{which}_perpose.json"), "w")'),
    ('open(os.path.join(VOUT, f"crest-knee-3r-v3_{which}.json"), "w")',
     'open(os.path.join(OUT, f"crest-knee-3r_v3jog_{which}.json"), "w")'),
]
for a, b in reps:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
sys.argv = [SRC, which]
g = {"__name__": "__main__", "__file__": SRC}
exec(compile(src, SRC, "exec"), g)
