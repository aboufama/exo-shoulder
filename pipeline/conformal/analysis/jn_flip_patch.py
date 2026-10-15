"""Evaluator patch (proposal, not deployed): job / design key "jn_low": "link" puts link N-1 UNDER the arm-end hub at JN
(link N-1 = the lower member of the last joint, the arm part's hub = the upper member that carries the stack top),
instead of the fixed "link N-1 sits on BOTTOM's hub" of band_impl.py. Why (analysis/why_held.py, judge/workspace.py on
cad_r18_n3_s1392_1_f300): the arm-fixed neck from the JN hub to BOTTOM's cut has to climb from the hub (zj4 85.8 mm from
GH) to the bar (underside 96.4) right through link N-1's level (its J3 plate 92.5-96.5), and link N-1 turns about JN
through every direction over the functional workspace, so link N-1 meets the neck / bar whenever it points down the arm
(R16: 'link 2 IN BOTTOM + neck' up to 3.25 mm, 52 of 120 poses). With link N-1 under the hub the neck leaves the hub's
upper plate (zj4 + stack) above link N-1, which only descends from its plate toward the skin: the two cannot cross;
link N-1's hub also drops by T_BOT + T_W (6.65 mm) to the skin face.

Changes (every one guarded by the key; default "arm" = the deployed behaviour, bit for bit):
  - fit_shape: link N-1's JN hub face = zb (was zb + T_BOT + T_W); its ribbon ramps out of zb; link N-1's ribbon must pass
    under the arm hub near JN (zb raised like any other lower member); the neck starts at zb + STACK (the upper hub)
  - collisions: link N-1's JN hub interval zj4 .. zj4 + T_LO (a lower plate), no longer zj4 .. F_N + HUB_UP + CAP_UP
The scored lowest metal at JN stays the turned disc underside (bot_under): same footprint, now link N-1's plate.
    import jn_flip_patch as JP; src = JP.patch(open("band_impl.py").read())     (python3 jn_flip_patch.py > patch.diff)
"""
REPS = [
    ("        self.min_arc = float(job.get(\"min_arc\", MIN_ARC)); self.min_arm = float(job.get(\"min_arm_mm\", MIN_ARM_MM))   # every link has a real arm\n",
     "        self.min_arc = float(job.get(\"min_arc\", MIN_ARC)); self.min_arm = float(job.get(\"min_arm_mm\", MIN_ARM_MM))   # every link has a real arm\n"
     "        self.jn_low0 = str(job.get(\"jn_low\", \"arm\")); self.jn_link = False      # \"link\": link N-1 under the arm hub at JN (analysis/jn_flip_patch.py)\n"),
    ("        self.hub_margin = float(d.get(\"hm\", self.hub_margin0))                # per-design contour margin (searched)\n",
     "        self.hub_margin = float(d.get(\"hm\", self.hub_margin0))                # per-design contour margin (searched)\n"
     "        self.jn_link = str(d.get(\"jn_low\", self.jn_low0)) == \"link\"\n"),
    ("        F_top_bottom = zj4 + T_BOT + T_W\n",
     "        F_top_bottom = zj4 + (0.0 if self.jn_link else T_BOT + T_W)\n"),
    ("            Fb = zb + T_BOT + T_W\n",
     "            Fb = zb + (0.0 if self.jn_link else T_BOT + T_W)\n"),
    # link N-1's ribbon under the arm hub near JN: raise zb (and Fb) like a lower member's face
    ("            for _pass in range(3):\n                h = Lm.clone(); faces = {}\n",
     "            for _pass in range(3):\n                Fb = zb + (0.0 if self.jn_link else T_BOT + T_W)\n                h = Lm.clone(); faces = {}\n"),
    ("                    if float(req) > float(Fj[J]) + 1e-3: Fj[J] = req; moved = True\n                if not moved: break\n",
     "                    if float(req) > float(Fj[J]) + 1e-3: Fj[J] = req; moved = True\n"
     "                if self.jn_link:\n"
     "                    near = rib & (memA == N - 1) & (dBA < HUB_R + 2.5)\n"
     "                    if bool(near.any()):\n"
     "                        req = h[near].max() + T_LO - STACK + 0.1\n"
     "                        if float(req) > float(zb) + 1e-3: zb = req if hasattr(req, 'shape') else t.tensor(req); moved = True\n"
     "                if not moved: break\n"),
    ("                hs0 = zb if ax_[\"start\"] == \"hub\" else",
     "                hs0 = (zb + (STACK if self.jn_link else 0.0)) if ax_[\"start\"] == \"hub\" else"),
    ("                    bot[k_] = F[\"zj4\"]; top[k_] = F[N] + HUB_UP + CAP_UP\n",
     "                    bot[k_] = F[\"zj4\"]; top[k_] = (F[\"zj4\"] + T_LO) if self.jn_link else (F[N] + HUB_UP + CAP_UP)\n"),
]


# v2 (2026-10-15 12:45, after the first GPU runs on band-2026-10-15m): with link N-1 under the hub the neck must also
# STAY above it - v1 let the neck's underside ramp down from the upper hub to the skin envelope like the old hugging
# neck, so it still met link N-1's ribbon wherever both hug the skin: analysis/ws_collisions.py on r20 s1414 #0 found
# every workspace part collision (14.2 % of the poses, 'link 2-neck') unchanged by jn_low=link. Now the neck leaves the
# upper hub level and never drops below it on its way to the bar (a bridge over link N-1's sweep).
REPS2 = [
    ("                u_ = t.maximum(La, hs0 - self.RAMP * t.clamp(ax_[\"dA\"] - 6.0, min=0))\n",
     "                u_ = t.maximum(La, (t.maximum(hs0, zb + T_LO + 0.65) + 0.0 * ax_[\"dA\"]) if (self.jn_link and ax_[\"start\"] == \"hub\") else hs0 - self.RAMP * t.clamp(ax_[\"dA\"] - 6.0, min=0))   # jn_low link: the neck bridges link N-1 (0.65 over its plate: collisions() wants 0.6 between them)\n"),
]


def patch(src, v2=True):
    """v1 (REPS; deployed in band-2026-10-15m) unless already in src, then v2 (REPS2) unless already in src"""
    if "self.jn_link" not in src:
        for a, b in REPS:
            assert src.count(a) == 1, f"band_impl changed, anchor not unique / missing:\n{a}"
            src = src.replace(a, b)
    if v2 and "the neck bridges link N-1" not in src:
        for a, b in REPS2:
            assert src.count(a) == 1, f"band_impl changed, anchor not unique / missing:\n{a}"
            src = src.replace(a, b)
    return src


if __name__ == "__main__":
    import difflib, os, sys
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gpu", "band_impl.py"); s = open(p).read()
    sys.stdout.writelines(difflib.unified_diff(s.splitlines(True), patch(s).splitlines(True), "a/pipeline/conformal/gpu/band_impl.py", "b/pipeline/conformal/gpu/band_impl.py"))
