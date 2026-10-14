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

| ID | Requirement | Threshold | Judge | Why this threshold |
|---|---|---|---|---|
| R1 | Proximity: share of the covered skin that is 2-10 mm from the metal, while following | >= 90 % | `pipeline/full-exo/score_design.py` (exact posed skin, 30 fps) | the 1 cm rule; 2 mm keeps the liner/clearance, 10 mm is the user's limit |
| R2 | No part enters the body, any frame of any clip | <= 0.5 mm | `judge/body_contact.py` (exact signed distance to the posed, closed body mesh) | 0.5 mm = tessellation tolerance; anything more is visible pass-through |
| R3 | The exo follows the arm (frames tracked rather than held at a joint limit) | >= 95 % of frames | `score_design.py` | a held frame means the user's arm is blocked |
| R4 | Overhead works: "Raise overhead" clip score | >= 80 % | `score_design.py` | the user called earlier designs "unusable" overhead |
| R5 | Degrees of freedom | <= 4 | `design.json` | user cap (2026-10-14) |
| R6 | No interference between parts that move relative to each other | <= 0.15 mm | `judge/part_contact.py` (geometry only) | designed coaxial fits (pin in sleeve, washer on seat) sit inside 0.15 mm |
| R7 | Every custom part is one valid, closed solid | all | `judge/part_validity.py` (OCC BRepCheck on the exported STEP) | a supplier must be able to read and machine it |
| R8 | Custom-part mass | <= 300 g (proposed) | `parts_full.json` (mesh volume x density) | placeholder budget, **confirm with the user** |
| R9 | Strength SF >= 1.5 at 25 N.m worst direction; deflection and fatigue bounded | - | **independent FEA (CalculiX)** - today only the in-house hex8 study (`pipeline/conformal/thin_study/REPORT.md`) | 25 N.m = assist torque design load |
| R10 | The base mounts to a thorax-fixed back plate: worst-frame GH-centre misalignment | <= 4 mm (proposed) | `judge/base_mount.py` (thorax-fixed base, rig girdle law today; **OpenSim Seth 2016** / OpenCap to replace the law) | 4 mm = half the 2-10 mm band: a misalignment shifts the metal against the skin by up to that much (docs/P0_BASE_MOUNT.md) |
| R11 | Interface pressure under the ISO/TS 15066 body-region limits | - | coupled human-exo contact simulation, then pressure film / FSRs on a prototype | comfort and safety at the cuffs |
| R12 | CAD standard: G2 surfaces, flat seats under every seat, no visible screws or seams | - | zebra / curvature check (`pipeline/full-exo/parts.html`) + user review | the user's own parts set the bar (docs/CAD_STANDARD.md) |
| R13 | Manufacturable | - | supplier DFM review and quote (CNC Ti-6Al-4V / 7075, SLM AlSi10Mg) | only a supplier can say yes |
| R14 | Generalises to motions and bodies never used to design it | - | held-out OpenCap / AMASS clips and SMPL-X bodies (`data/raw/`) | the 8 design clips are synthetic and were optimised against |
| R15 | Works on real bodies | - | printed prototype on the user + one very different body: OpenCap reach vs bare arm, zero contact on skin FSR strips | the final judge |

R1-R8 and R10 are measured today. R9-R15 are the work that turns this from a simulation result into an engineering result.
