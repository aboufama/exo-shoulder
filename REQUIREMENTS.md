# Requirements

Every requirement is a number with a pass/fail threshold and **one judge that is not the design pipeline and not the agent's
opinion**. `judge/requirements.json` is the machine-readable copy; `judge/scorecard.py` evaluates a design against it.

The user's original statement of the goal, which outranks everything below:

> The whole mechanism must ride less than ~1 cm from the skin across the whole shoulder, over the full range of motion
> (overhead matters most). At most 4 degrees of freedom: 3 joints + a sliding cuff, or 4 joints and no cuff. Everything
> else (mechanism family, joint placement, link shapes, materials, attachment points) is free.

Added by the user on 2026-10-14 (their words):

> "Honestly it would be amazing if it can be handled in only 3 degrees of freedom (less actuators)" ... "3 dof is
> theoretically possible, it just takes a lot of engineering" ... "you could even put upper arm rotation in its own DOF
> farther down from the shoulder and just have to handle 2 at the shoulder joint! If they could fully overlap each
> other, you'd get rid of a lot of collision issues, also you can make it within 14mm if you really need to"

So: **3 DOF is the target** (the cap stays 4); **10 mm stays the target band**, 14 mm is allowed where it is really
needed (e.g. nested links) and is always reported separately (score_design.py `BAND_HI=14`).

And later the same day (their words): "Yes you can download, I mean kinematicly 3dof so nothing is powered we view all
joints as the same. Unless you can find a way to leave one joint unpowered and not require torque to it to use full ROM
that is an exception if you know what I'm saying you can make it as thin as possible, we're using titanium after all".
So: **DOF are counted kinematically - every joint counts, powered or not.** **One exception**: a joint that is left
unpowered and needs no torque (no effort from the wearer) over the full ROM, e.g. a gravity-balanced, self-aligning
passive slider that only lets the rotation centre follow the girdle. **Links as thin as titanium allows** (thickness is
a design variable sized by FEA, not a fixed 5.5 mm). The user approved downloading OpenSim and the Seth 2016 model and
accepted its CC BY-NC-SA 3.0 licence (the experimental bone-pin data in that archive is restricted to verifying the
Seth model and was not used).

**User decisions, 2026-10-15.** Base: "It should ride the scapula, as the next kinematic element is the scapula
handler" - the scapula handler is "a separate part I already designed, you only have to worry about the exactly 3
degrees of freedom found in the shoulder, the minimum possible solution is 3 dof, which is why I'm pushing so hard for
it". Joint count: "I would REALLY like 3 joints, but just push for as low a joint count as possible, this is a huge
reward". Proximity: pass at 14 mm, aim for 10 mm (both reported).

**User decisions, 2026-10-15 (after the sim-to-real register, docs/research/sim_to_real_gaps.md).** Actuation:
remote motors with cables to the joints. Assist: "Don't worry about this at all since they're offset but it would be
very subtle just a bit more than gravity" -> design load = gravity support of the arm plus a margin (~10 N.m peak at
90 deg elevation for an average arm; R9's 25 N.m is retired as the design case). GH-centre error: torque-free passive
self-aligning slides at the cuff, outside the 3-DOF count. Bearings: "use actual tiny needle bearings if possible try
to optimize assuming very high quality bearings" -> rolling (needle / thin-section) bearings at every joint; the
plain-bearing self-locking risk (G6) is designed out, the joint keep-out becomes bearing + cable pulley.

**Scope, user 2026-10-15:** "You should not design the gear ratios, or any of the pulley system, your task is to
design a kinematic proof of concept, with some basic bearings, that I will redesign to have rotation measurement, and
for the second MVP, we will power, the first part is just getting full body tracking to even work". So MVP1 = an
UNPOWERED kinematic proof of concept: the chain follows the arm through the full range (the arm drives it; transparency
and no self-locking matter most), basic rolling bearings, no actuators, pulleys or gearing (MVP2). Also: right
shoulder; fit a larger male - the user is 6'1" (185 cm) with a 6'4" (193 cm) wingspan, and people around that size
(the rig is 174.7 cm: to be scaled); worn over a thin base layer; a shoulder-pad cover will go over the mechanism
(outside pushes and pinch points are the cover's job, still worth keeping in mind); reaching behind the back: "Aim for
fully working, and see how close we can get"; worn for hours, most of the day (sustained-pressure limits); custom-part
mass 500 g for the shoulder ("mass is not really a huge driver I just want low DOF and low profile"); R10 4 mm confirmed.

**Range first, user 2026-10-15 (after r16's diagnosis):** "maybe 90% range first?" - the chain must follow >= 90 % of
a FUNCTIONAL everyday workspace (published ADL ranges until the user's OpenCap max-ROM exists), then be as close as
possible (R1 on the clips). New requirement R16 below. Overnight GPU cap raised to $20; one 4-joint comparison batch
allowed ("Yes, as a comparison"); scaling the rig to the user is low priority ("any design can be scaled by a few
percent").

| ID | Requirement | Threshold | Judge | Why this threshold |
|---|---|---|---|---|
| R1 | Proximity: share of the covered skin that is 2-14 mm from the metal, while following | >= 90 % (aim: the same at 2-10 mm, reported as R1-aim) | `pipeline/full-exo/score_design.py` with BAND_HI=14 (exact posed skin, 30 fps) | the 1 cm rule with the user's allowance: pass at 14 mm, aim for 10 (2026-10-15); 2 mm keeps the liner/clearance |
| R2 | No part enters the body, any frame of any clip | <= 0.5 mm | `judge/body_contact.py` (exact signed distance to the posed, closed body mesh). It also reports, per part, the owner (this project's parts incl. BOTTOM vs the user's own arm parts) and the **attributable** depth: the depth beyond the rig's own self-intersection (the rig has no soft-tissue contact: its arm passes ~90 mm into its chest in Wash opposite shoulder, its forearm into its biceps at deep flexion), in full inside the part's own limb, elsewhere only below its own limb's skin (`judge/body_regions.py`, validated in `judge/test_body_contact.py`). Body: the rig, or with `BODY_FIT=user` the rig bounded by the user's own arm parts (`pipeline/avg/user_fit.py`: the cuffs bound the user's limb; option, default off) | 0.5 mm = tessellation tolerance; anything more is visible pass-through |
| R3 | The exo follows the arm (frames tracked rather than held at a joint limit) | >= 95 % of frames | `score_design.py` | a held frame means the user's arm is blocked |
| R4 | Overhead works: "Raise overhead" clip score (14 mm band) | >= 80 % | `score_design.py` BAND_HI=14 | the user called earlier designs "unusable" overhead |
| R5 | Degrees of freedom of the shoulder chain (scapula base to arm), counted kinematically (every joint, powered or not) | <= 4; **aim exactly 3** (R5-aim) | `design.json` | user cap and counting rule (2026-10-14); the user's scapula handler is a separate part outside the count, and 3 is the minimum and the goal (2026-10-15) |
| R6 | No interference between parts that move relative to each other | <= 0.15 mm | `judge/part_contact.py` (geometry only) | designed coaxial fits (pin in sleeve, washer on seat) sit inside 0.15 mm |
| R7 | Every custom part is one valid, closed solid | all | `judge/part_validity.py` (OCC BRepCheck on the exported STEP) | a supplier must be able to read and machine it |
| R8 | Custom-part mass | <= 500 g (user 2026-10-15) | `parts_full.json` (mesh volume x density) | placeholder budget, **confirm with the user** |
| R9 | Strength SF >= 1.5 at the design load (arm gravity support + margin, ~10 N.m; was 25 N.m), worst direction; deflection keeps the 2 mm floor; fatigue bounded | - | **independent FEA (CalculiX)** - today only the in-house hex8 study (`pipeline/conformal/thin_study/REPORT.md`) | 25 N.m = assist torque design load |
| R10 | The base rides the scapula on the user's scapula handler: worst-frame GH-centre misalignment from the handler slipping over the bone | <= 4 mm (confirmed by the user 2026-10-15) | `judge/base_mount.py` + `judge/base_slip.py`: girdle mount -> literature skin-slip model (the handler as an acromion marker cluster: per-axis ISB scapula error angles vs humeral elevation from Karduna 2001 / van Andel 2009 / Lempereur 2014, 4.2 mm translation slip, lever from the OpenSim Seth 2016 scapula; central law = the number, low / high laws bracket it; docs/research/base_slip_model.md). Thorax bases keep the three-girdle-law check (rig, bone-pin chain, **OpenSim Seth 2016**) | 4 mm = half the 2-10 mm band: a misalignment shifts the metal against the skin by up to that much (docs/P0_BASE_MOUNT.md). For a spherical chain the number is design-independent: only the handler, the motions or a passive slider move it |
| R11 | Interface pressure. **Simulation part:** worst mean pressure the exo adds on the upper-arm cuff (incl. the arm-side parts' weight hanging on it) over the MVP1 rolling-bearing cases; and the ISO/TS 15066 quasi-static limits for the upper arm | <= 7.5 kPa from the exo (14 kPa sustained all-day budget - 6.5 kPa strap preload) **and** <= 150 N, <= 190 N/cm2 at the 2x edge peak (ISO/TS 15066 Annex A, Table A.2: upper arm / elbow 150 N, deltoid 190, humerus 220 N/cm2; forearm 160 N, 180 N/cm2); aim: <= 4.3 kPa (32 mmHg capillary closing, Landis 1930) | `judge/dynamics.py` (MuJoCo cuff force) -> `judge/scorecard.py` interface_pressure(); **the prototype pressure-film / FSR check stays part of R11** (the simulation has one rigid cuff, a mean pressure and no base-side or forearm-cuff pressure) | worn for hours, most of the day (user): sustained-compression discomfort ~13.7 kPa (Kermavnar et al.), strap comfort threshold 15 kPa (Van Vlerken et al.), 50-80 mmHg optimum (Langlois et al.); ISO/TS 15066 values are pain-onset limits for collisions (1 cm2 probe), not wear values, and never bind here |
| R12 | CAD standard: G2 surfaces, flat seats under every seat, no visible screws or seams | - | zebra / curvature check (`pipeline/full-exo/parts.html`) + user review | the user's own parts set the bar (docs/CAD_STANDARD.md) |
| R13 | Manufacturable | - | supplier DFM review and quote (CNC Ti-6Al-4V / 7075, SLM AlSi10Mg) | only a supplier can say yes |
| R14 | Generalises to motions and bodies never used to design it | - | held-out OpenCap / AMASS clips and SMPL-X bodies (`data/raw/`) | the 8 design clips are synthetic and were optimised against |
| R15 | Works on real bodies | - | printed prototype on the user + one very different body: OpenCap reach vs bare arm, zero contact on skin FSR strips | the final judge |
| R16 | Follows the functional everyday workspace: share of its poses the chain moves through without skin contact, squeeze or part collision | >= 90 % (user 2026-10-15) | the band evaluator's envelope (`pack_envelope.py --functional`) today; an L1-CAD judge over the same poses next | "full range of motion": six clips are not the range (r16 followed only 40-44 % of the workspace) |
| R17 | Moves freely unpowered (MVP1): the arm drives the chain through every clip | peak <= 1 N.m about the shoulder (0.5 rms), <= 5 N and <= 5 deg twist at the cuff, no stall, no undriven spare joint (proposed) | `judge/dynamics.py` (MuJoCo, rolling bearings, load-dependent friction; `judge/test_dynamics.py`) | 1 N.m ~ one just-noticeable difference of the arm's own ~10 N.m (Jones 1986); MVP1 is unpowered (user) - a 4R's spare joint falls under its own weight |

R1-R8, R10, R11 (simulation part), R16 and R17 are measured today. R9 and R12-R15, and the prototype half of R11, are the work that turns this from a simulation result into an engineering result.
