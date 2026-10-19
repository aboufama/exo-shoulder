# ikring-distalshell-knuckle-4r - the lead with a short knee and a round J4 shell distal of every mover

Round 301 (O1, track overhead), lens rocker-redundant-4r, judge pick 3 (docs/concepts/round301_ideation.md 1.3 / 4.3).
A LABELLED 4-JOINT OPTION (4 active joints: J1, J2, J3 + the J4 ring), never the lead.

## Deeper version first (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask.** Treat the knee re-centre as a constrained
   design problem, not a copy: the spec copies the pin knee's proportions (lE 59.6), but the binding constraint is only
   "every mover above s0 - 7", so the right move is to map the whole trade curve gap(psi=0) vs max-mover station and
   then pick s0 where the shell's roundness (clip p90 defect) and the knee's take count cross - a longer knee with the
   shell a little more distal may beat the pin-knee proportions. Second, read the J4 shell as what it is - an
   arm-fixed arc that must clear the TORSO at the posterior end on IR-heavy low-elevation poses - and place its ends
   per pose on envsel, not on the generic arc. Third, before trusting any ring take, ask whether the ring is earning
   its place versus the cheaper 3-joint lead (the measured question: ring-added takes vs ring-made contacts / shell).
2. **Rawest material.** The posed skin itself (concept_bench exact signed distance on the posed meshes, Bench(110,360)
   and Bench(60,160)), the motion clips' per-frame poses (the 60 / 110 clip frames carry the in-band read), the
   skin-motion map pipeline/conformal/analysis/skin_motion_map_14.json (the arm's own surface drift under the cuff), and
   the raw ray profile about a_r (scratchpad ring301/round.json, the judge's shellaxis.py read) - not the digested
   ideation tables.
3. **Methods and tools.** tools/concept_bench.py (fast cache for the fit, CB_EXACT=1 for every claim), the lead model
   docs/concepts/models/conecut-knee-knuckle-3r.py with the knee overridden, the ring machinery imported read-only from
   docs/concepts/models/ikring-thinstack-knuckle-4r.py (k-table, lead-first take-only IK, the 1432-grid IK flood) and
   phi40 / proxtrack's shell geometry (relay_points / rerecord jam rule) with the shell set DISTAL (ds < 0 side, bump
   amounts read, not assumed, to be 0), BV.th_margin for the 5-deg rule, random + local search for the knee.
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact frozen, never selected on), an
   adversarial verifier re-running the claim from the row's params, the alignment auditor's watch list (shell count of
   every new take, 2 mm reading vs the lead's 34.84, static vs connected, held overhead), and the red-team pose list
   below (the posterior-end torso poses at plane 75-120 / elev 30-45, the lead's drive contacts 237 / 264, the
   behind-back ER anterior-end cap at +49-51 deg).

