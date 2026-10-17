# An in-band RSSR K drive: making the long-stroke drive's metal cost little (2026-10-17)

User, 2026-10-17: "i want higher scores! get to work and do it well!" / "do not stop until i say, keep pushing".
The long-stroke row (docs/research/longstroke_drive.md) measured the prize: with the hub-2 lobe at its PA-42 law (kK 3.0)
the long-dyad chain with the drive's metal DELETED (LS_GHOST=1, attribution only) is **18.25 frozen / 21.11 held**, against
the verified leader slipper-nose-knuckle-3r's 18.49 / 23.45; the same law through the real rod drive is 25.83, and the
real rod re-searched at the steep law 23.31 / 27.67. This task: make the drive's metal cost little.

Files: model `docs/concepts/models/inband-rssr-knuckle-3r.py` (the long-stroke model loaded unchanged, its RSSR metal
re-placed by switches eta / clay / zc / bl_c / bl_h, defaults = the parent), row `docs/concepts/rows/inband-rssr-knuckle-3r.json`,
scripts and data `docs/research/inband_drive/` (attribute.py, screen.py, make_jobs.py, farm/), preview
`docs/concepts/viz/concepts/inband-rssr-knuckle-3r.js`.

## Depth answers (written before the work)

1. **What a top packaging / mechanism designer would do that the brief does not ask.**
   - Price the drive in the bench's own currency before moving metal: the gap is 100 x (0.90 - in-band) + 100 x (0.90 -
     reach) + 100 x contact, and in-band is POOLED over every sample point of the taken clip frames. So a part's cost is
     (its out-of-band points) / (all points) - the bell crank's 73 samples at 0.62 in band are worth ~3 points by
     themselves, the rod's 17 almost nothing - and a contact pose costs twice (it leaves reach AND enters contact).
   - Ask why the crank is high before moving it: it is high because it is STACKED (its pin is in link 1b, so its boss sits
     on link 1b's top + 0.15 running gap), not because it is far from the body. The fix a packaging designer reaches for
     first is a joggled bracket: give the pin a tab one layer DOWN, so the crank runs in link 1b's own layer beside the
     strap - the same thing every hub stack in this project does.
   - Keep stage 1 (the lobe law) untouched: the follower geometry (pivot 16 mm from hub 2's axis, s_arm on the rim lobe)
     carries the law and its pressure angle; repackage only stage 2's metal, so the kinematic claims stay the parent's.
   - Treat the ball-link offset as the second stack: an M2 ball's centre sits 3 mm off the arm face, the rod rides on
     it, so the rod is a layer above the crank; a stud pointing to the skin (ball under the arm) drops the rod 6 mm.
   - Check what the brief did not ask: does the new bracket (the ear) itself cost band or contact, and does the lower
     metal trade in-band for near-touch / contact (the 2 mm objective) - i.e. measure contact depth, not only counts.
2. **The rawest material.** The per-pose signed skin distance of every sample point of every drive part on the frozen
   exact Bench(110,360) and the 952 held-out poses (attribute.py), split by part (crank boss / arm by radius, rod,
   ball-link sockets, horn lug, ear) and by pose class (elevation bands), plus which part makes each contact pose and how
   deep. From that table the bench's score is recomputed with any part deleted - the exact per-part LS_GHOST with the fit
   unchanged.
3. **Methods / tools.** The model's own switches (the parent's LS_DRIVE / LS_GHOST; this row's IB_GHOST per part and the
   repackaging switches whose defaults reproduce the parent to the digit), concept_kit's exact skin (CB_EXACT=1), fast
   screens on Bench(60,160), CMA-ES on the farm (tools/concept_cma.py, 2 mm and 1 mm near-touch objectives, law held steep
   by LS_KK_MIN 2.7 and the drive range by LS_STROKE_MIN 55) to the convergence gate (cma_summary.py), the frozen claim
   protocol, the parent's RSSR range scan (transmission >= 48 = PA <= 42 at both ball ends) unchanged.
4. **What else shows it right.** The control (defaults reproduce the long-stroke row: fast 42.91 / plain 19.40), the
   frozen exact bench and the held-out bench, the per-pose dump (tools/alignment_paired.py), the alignment auditor
   against slipper-nose, and an independent verifier re-running section 7's commands.

(sections below are filled as measured)
