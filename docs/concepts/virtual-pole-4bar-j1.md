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

## Coarse sweeps (farm, Bench(60,160) fast, every kit check on)

All gaps are on the screening bench. Honest means march + dense K2 + K6 + a clean audit. A member that some pose sends
into the body parks at 400 mm; the audit then flags its sampling as sparse, and the row is not honest.

| stage | configs | honest | best honest gap | best any gap | closure p50 |
|---|---|---|---|---|---|
| v1 random layouts (before the member fix: same-body straps were separate K6 pairs) | 220 | 2 | 237.75 | 200.15 | 0.00 |
| v2 structured from the free-space map (before the member fix) | 150 | 1 | 275.0 | 214.91 | 0.12 |
| v3 = v2 + 60 of v1, final members, q in {0.93, 0.97, 1.0} | 210 | 15 | 274.37 | 152.69 | 0.08 |
| rp: remote-pole family (cranks 55-115 deg from the pole, nearly parallel) | 210 | 5 | 268.32 | 182.68 | 0.00 |

The base pins do what the map promised. In the v3 best (152.69), hub A0, hub B0 and the base strap are **100 %** in band.
They are the first scapula-fixed metal on a fold-free J1 line to be in band in every pose.

The chain dies anyway. Measured with scratch `phidiff.py`: the four-bar's J2 compared with the plain 3R's J2 at the same
axes, on both 3R branches.
* **On jfront (J1 bvec(120, 60)) the four-bar reproduces J1 well.** In the v3 best, J2 follows the 3R's +1 branch
  within 3.4 deg (median; p95 27). It then fails exactly where the 3R fails: the J2 hub, link 1 and link 2 are 0 % in
  band, which is the known hub-2 failure of that base (it swings over the abducted, externally rotated arm, FINDINGS
  2026-10-16). The J1 four-bar fixes a hub that was already 93 % in band there and does nothing for hub 2.
* **On front132 (fold-free 0.96, hub 1 out of band) the four-bar is the right fix, but it cannot turn far enough.**
  The rp layouts reproduce the 3R's J2 within 0.1-0.2 deg (median), yet they close in only 16-48 of 220 poses. Link 1
  of that layout must turn almost a full circle about J1: the 3R's J2 azimuth spans p5 -165 to p95 +170 deg.
* **Coupler turning range.** Measured on the 580 coarse layouts: a four-bar coupler inside the [25, 155] deg
  transmission window turns p50 53 deg, p90 129 deg, and only 8 % reach 160 deg.

**Verdict after the coarse sweep: dead as a J1 replacement.** Measured reason: a four-bar coupler cannot turn as far
as J1 must (about 160-330 deg) while keeping its transmission angle, and where it does turn far enough (jfront), J1 was
not the problem. The 2 CMA streams that had already started ran to their budget as extra evidence (below). The time
went to virtual-pole-4bar-j2.
