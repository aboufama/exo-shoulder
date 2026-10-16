# raglan-knee-3r - the zero-passive-translation leader (pin knee on the k4216 seats) with raglan-routed links

Model: `docs/concepts/models/raglan-knee-3r.py` (`check | map | frozen`; imports a private copy of
`skin-normal-3r-pin-knee.py`, so every pin-knee rule and check is inherited, not re-implemented).
Sweep: `docs/concepts/sweeps/raglan-knee-3r.json` (coarse farm sweep + every CMA try, in order).
Sister morphologies: `docs/concepts/raglan-routed-3r.md` (routing on the plain 3R), `docs/concepts/far-end-posterior-3r.md`
(far-end hubs, killed).

## Depth answers (before modelling)

1. **What a top pattern maker / orthotic fitter would do here.** Fit the garment to the body in MOTION, not at rest:
   cast in the positions of use, then place every seam on the line that does not move against the body under it
   (raglan seam, Iberall's lines of non-extension), and every hard landmark (hinge, rivet) on skin that rides with the
   piece it carries. Here the "garment pieces" are the two rigid links of the best buildable design (the pin knee:
   0 passive translations, 26.34 fast / 33.84 frozen exact) and the seams are the link centrelines. So: measure, in
   each link's OWN moving frame, which directions keep one height within 2-14 mm over every pose the chain takes (the
   raglan map), and bend the link along the best line with one planform turn (two straight legs and a tangent arc, a
   constant 8 x 3 section: the user's bent-bar style, no loft). Then let the optimiser move the seats WITH the routes
   (a seat that was bad only because its straight link crossed moving skin becomes reachable), and try the posterior
   J1 line (fold-free on 100 % of poses, the far-end scan's lead) in this family.
2. **Rawest material.** The posed skin of every bench pose (signed-distance grid, Bench(60, 160) fast; the verdict on
   Bench(110, 360) exact); the sphere-traced need (2 mm clearance) of every direction of the link's own frame in every
   pose the chain takes, with link 2 flying over the knee and pad boxes, exactly as the pin knee fits its links.
3. **Instrument.** The pin-knee model (closed-form spherical IK, knee closure in [30, 150] deg, 10 fps continuity, jam
   rule, every part pair, hub walls / crowns / strap tops skin-checked, greedy pose drop recorded as contact), the
   raglan map (`map` mode), the farm (`tools/cloud_run.py sweep`), CMA-ES on the farm (`tools/concept_cma.py`), the
   frozen large-bench protocol (fit on Bench(60, 160) fast, freeze, wear on Bench(110, 360) exact).
4. **Outside judge.** `tools/concept_bench.py` through the pin knee's own scoring (same poses, metrics, contact rule as
   every row); parity with the pin knee at d = 0 (k10: 26.34, every metric to 4 decimals); the frozen Bench(110, 360)
   exact wear; the adversarial verifier.

## Mechanism (every joint a real component)

| element | component | envelope in the model |
|---|---|---|
| J1, J2 (active R) | MR117-2RS bearing pair in an O20 hub on a GH ray | O20 disc at the fitted face, 12.25 mm stack, walls + crown skin-checked |
| J3 (active R) | same, offset skin-normal hub on the deltoid (tilt b3) | as above |
| knee (2 passive R) | two pins: integral O4 Ti pin, iglidur GSM sleeve + 2 GTM washers (tools/hardware_catalogue.json IGLIDUR-PIN) | 5 mm pin stack, O12 bosses, 10 mm knee link, E strap, arm pad |
| link 1, link 2 | 8 x 3 Ti bent bar: two straight legs + one tangent arc (planform radius rc, 10 mm default) | skin-fitted underside per sample, <= 60 deg ramps, link 2 over the knee / pad |
| neck / cuff | the pin knee's E strap, boss, pad on BOTTOM's cuff | as the pin knee |

Passive translations 0. Every coordinate is set by the 3 actuators and the closure (the knee is a closed planar RRR).

## Results

(written as they come in)
