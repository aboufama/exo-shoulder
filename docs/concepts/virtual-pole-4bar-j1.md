# virtual-pole-4bar-j1: J1 as a scapula-grounded spherical four-bar with a virtual pole

Model: `docs/concepts/models/virtual-pole-4bar-j1.py`. It loads the shared implementation in
`docs/concepts/models/virtual-pole-4bar-j2.py` with at=1; the mechanism notes, mobility proof and member rules are in
`docs/concepts/virtual-pole-4bar-j2.md`. Sweeps: `docs/concepts/sweeps/virtual-pole-4bar-j1.json`. Row:
`docs/concepts/rows/virtual-pole-4bar-j1.json`.

## Depth answers

**What would a top practitioner of spherical / deployable linkages do here?** The fold frontier wants the J1 LINE
near-horizontal and anterolateral (bvec(132, 16), or the joint frontier's bvec(120, 60)). Its hub would sit where the
anterior deltoid rises 44 mm (p90) under the acromion front (FINDINGS 2026-10-16). A linkage designer keeps the line
and drops the bearing. Link 1 becomes the coupler of a four-bar grounded on the scapula base. The pole (the crossing of
the crank great circles) sits on the wanted line at home, and the two ground pins sit on scapula-fixed skin that never
moves. This is the RCM move done the spherical way. The planar double parallelogram does not exist on a sphere
(no translations), so a moving pole is the price.

**Rawest material.** The posed skin per bench pose, seen from the scapula (ground pins) and from link 1 (coupler
pins): the body-frame free-space map (scratch `pinmap2.py`).
* At the joint-frontier base J1 bvec(120, 60), scapula-fixed rays 30-45 deg from the pole on the ψ 300-90 side keep one
  hub height in band in **100 %** of closing poses.
* Link-1 rays 30-45 deg from the pole on the side away from J2 keep it in **93-100 %**.
* The pole ray itself manages 0.73-0.75.

**Instrument / outside judge.** As for virtual-pole-4bar-j2: closed-form spherical four-bar, 1-D coupler-curve root
(here against the circle of radius a2 around the arm's J3 axis, pose by pose), and the kit's honest evaluate. The
judges are Bench(60,160) fast for the search and the frozen shape on Bench(110,360) exact.

## Mechanism

```
scapula base ==A0== crank A ==A1== coupler = link 1 -J2 (O20)- link 2 -J3 (O20)- arm -> K7 neck
             ==B0== crank B ==B1==
```

Mobility 3(6-1) - 2*6 = 3, loop 1. There are 0 passive translations, and six bearing pairs at the O20 envelope. The
base strap A0 - B0 is real metal on the scapula skin and is fitted like every other part. MVP2 drives crank A from the
base.

Key risk, stated before the sweep: link 1 of the frontier layouts turns about J1 through about 160 deg over the
workspace (the J2 azimuth spans p5 -162 to p95 +2 deg at bvec(120, 60)). A four-bar coupler turns that far relative to
its ground only near a change point, and the transmission-angle rule [25, 155] cuts that off.
