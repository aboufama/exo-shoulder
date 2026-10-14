# Shoulder morphology research — findings (2026-10-13)

Body: BodyParts3D (CC BY-SA 2.1 JP) male, rigged (body.js / anatomy-build/build_body.py), scaled to the exo's 411 mm
upper arm; scapulohumeral rhythm + girdle elevation; 3,993 natural shoulder poses (ISB plane/elevation/axial).
Collision grids: signed skin distance, inside = closer to tissue than to skin, arm/trunk ownership by nearest bone
(make_mesh_grids.py; 5 mm shoulder grids + 8 mm grids to the elbow).

## 1. The physical ceiling (any mechanism)
For each pose: is there ANY path through free space (within the profile envelope, >= clearance off the skin) from a
scapula-mounted base to an attachment on the upper arm? Best base / attachment pair, `ceiling` script in the log:

| clearance (link centreline to skin) | 140 mm | 160 mm | 180 mm |
|---|---|---|---|
| 11 mm (12 mm bars) | 77% | 81% | 85-90% |
| 6 mm (thin strips) | 90% | 90% | 93% |

The unreachable poses are almost all the arm pressed against the body (across the chest, behind the back): the arm
attachment itself is buried. 100% is impossible for any exo with a rigid attachment on the arm.

## 2. Why rigid chains fall short: the sweep principle
Relative to each link, the body sweeps around that link's joint axes:
- last link: the arm sweeps an annulus around the last joint axis (zero if that axis IS the humerus axis);
- first link: the trunk sweeps around the base axis over its travel.
A fixed upper-arm post (off the humerus axis) makes humeral axial rotation swing the whole chain around the shoulder;
that is what caps every shell design.

## 3. The Orbit Joint (new, ring-free virtual axial joint) — orbit_joint.py
Crank on the upper-arm bar (pivot P) + translating coupler (held by tendon loop 1) + cuff bracket on the coupler
(turned 1:1 by tendon loop 2). With crank vector = bracket offset from the arm axis, the cuff motion is EXACTLY a
rotation about the humerus axis (verified 0.0 mm error over +-120 deg). 3 pivots + 2 tendon loops, nothing encircles
the arm, no dead points; travel limited by the crank knee nearing the arm (+-120 deg). On the body its moving parts
touch the trunk in only ~1.5% of poses. Needs +-90 deg for 92%, +-110 deg for 97% kinematic coverage of the
two-pivot pointing chain (family V).

## 4. Results (corrected body, links >= 9 mm inner face from skin)
| family | 124 | 136 | 148 mm |
|---|---|---|---|
| A current CAD scissor | 15% | | |
| B scissor re-optimised | 50% | 51% | 52% |
| C 3 pivots | 50% | 55% | 61% |
| D 4 pivots (1 spare) | 65% | 72% | 76% |
| E five-bar | 35% | 39% | 39% |
- D sits at ~95% of the physical ceiling for its profile.
- 2 pointing pivots + ideal axial joint (family V): 67% (150 mm), 77% (180 mm) before joint hardware.
- tendon-coupling the spare joint of D to another joint (non-redundant 4-pivot): ~50% (single linear law).

## 5. Thin-link runs (clearance 4 mm at the inner face) — see anat_C_clear4.log, anat_D_clear4.log
| family (thin links, inner face >= 4 mm off skin) | 124 | 136 | 148 mm |
|---|---|---|---|
| C 3 pivots, post +-90 | 59% | 64% | 65% |
| C 3 pivots, post limited only by contact | 62% | 70% | 73% |
| D 4 pivots (1 spare) | 76% | 81% | 85% |
Thin-link physical ceiling ~90% (140-160 mm) / 93% (180 mm): D reaches ~94% of it; the best non-redundant 73%.

## 6. Open directions
- non-redundant shape adaptation: a cam (not linear) coupling of D's spare joint; a scissor with more rhombi (thinner band).
- the Orbit Joint on a two-pivot pointing chain whose pole is moved off the resting arm (base-link sweep).
- skin-riding padded links (clearance -> 3-6 mm) are the single biggest lever on the ceiling.
