# Round 8 ideation: judge and red team (2026-10-16 ~18:20 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275), tools/concept_bench.py). The real target is
gap 0, and 95 (gap 13.75) at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

Lead to beat: frontload-lobe-stopb-knuckle-3r. It is verified at 22.82 on Bench(110,360) exact frozen (score 91.70),
complexity 49. Its gap splits as in-band 4.54 + reach 17.22 + contact 1.06. The planner's arithmetic for 95: put the
drive metal in band (in-band 0.905, gap ~18.3), then win 16 of the 86 fold poses (reach 0.773).

## Red-team checks made by the judge

1. **Complexity re-priced with tools/simplicity.py** from each proposer's mechanism record. Lead 49.0, roller-flank
   45.25, crank-rod 36.0, lost-motion 43.0, sidecar 49.0. All match the claims.
2. **The dyad drive arithmetic checks** (spherical law of cosines, interior angle psi at K):
   - the lead's dyad 30.05 / 37.57 needs psi 66.4 -> 133.9, which is dK 67.5 for a1e 36.1 -> 61.7. That matches the
     law's 67.4.
   - 35 / 45 needs dK 86.5 for a1e 75, as the wide-dyad proposer said.
   - 30 / 44 needs dK 70.7 for a1e 66.
3. **The lead never uses its stretched range.** Taken poses use dK <= 44.3, so psi <= 110.7 and a1e <= ~54.7, well
   short of a1max 61.7. The walls that bind are m3e, lift-off, rate and contact, not only the straight line
   a1max + a2 - 5. Raising a1max alone buys poses only where those walls also move. That is consistent with the
   wide-dyad window model being +0.036 optimistic on the lead.
4. **The sidecar gates check.**
   - The pressure angle is tan(pa) = 2 * 5 * 13 / (16 * 8.5), so pa = 43.7 deg.
   - The crest is 8.5 + 5 * 0.524 = 11.12.
   - K slop is 0.05 / 14.5 rad = 0.20 deg.

   **Caps:** pa <= 45 and crest <= 11.5 give kK <= ~2.06 at La 16 / r_h 13. They give
   dK <= (11.5 - r_lobe) / s_arm * La / r_h = 42.7 deg at La 18 / r_h 14.5. That is just below the lead's 44.3 taken.
   La / r_h >= 1.3 with r_lobe ~7 keeps the stretched poses.

   **Pinch point:** the far ball cup at r_h 14.5, cup radius 3.5, sits 14.5 - 3.5 - 10 = 1.0 mm off hub K's cylinder.
   It is beside the stack, below the crown. That meets the 1 mm part-pair rule with zero margin, so take r_h >= 15 or a
   catalogued cup envelope.
5. **The in-band ceiling.** In-band is scored max(0, 0.90 - ib), so a strap-level drive can buy at most the lead's 4.54
   frozen points. The sidecar's -0.007 reach costs ~0.7 of them, so expect ~19 frozen, not 95. The reach half has to
   come from picks 3-4.
6. **The bk1 proxy is contradicted by the real model.** The wide-dyad proxy kept hub K at 0.926 for bk1 35 and has no
   contact term. In the real model, the sidecar-longdyad proposer measured bk1 34 / bk2 40 at 5 contact poses and
   36 / 44 at 7 skin + 4 contact. The lever is bk2, not bk1.
7. **The crest-seat precedent.** Round 4's crest seats (deltoid-crest-j3-3r) turned +0.07 of fast closure into
   +0.017 of frozen reach. The leaders lose ~0.08 reach from 160 to 360 by selection. Proxy-only seat gains are
   discounted by ~2/3.
8. **The msub reading.** The crank-rod measures 48.7 fast with msub applied wherever K is open. The proposer's
   technical argument has merit: with K = f(q2), the pointing Jacobian columns are u1, u2 + f'(q2) uK and u3, and the
   sub-dyad fold u1 / uK / u3 is not by itself a rank drop. But the fold reading is the user's call (CLAUDE.md "The
   fold margin is read in ONE metric"), and ROUNDS.md already lists the question.

## Verdicts

| candidate | verdict | reason |
|---|---|---|
| sidecar-parallelogram-knuckle-3r | **PICK 1** | The only same-harness metal measurement against the lead: 11.88 vs 16.20 fast, untuned, in-band 0.904. Real parts (MR63ZZ, M2 ball links to catalogue, GE4E fallback). 0 passive translations, cx 49. Red team: in-band ceiling 4.54 frozen; pa / crest gain cap ~43 deg of K; cup-to-hub-K 1.0 mm at r_h 14.5; rod sampled at rest. Kill gate: per-pose placement at the lead's seats must hold <= 14.0 fast near-touch. |
| sidecar-roller-flank-knuckle-3r | **PICK 2** | Heights measured: 12.26 fast, in-band 0.896. It lowers complexity 49 -> 45.25, the only strap-level drive that does. Gain ratio La / r_c 1.73 gives crest headroom for the lead's kK ~2.9. Red team: two force-closed cams in series; conjugate flank unmodelled (59 deg between the contact velocities at rest); bent arm ~0-3 mm off hub K's skirt before the arc is drawn. Kill gate: a flank with both pa <= 45 over >= 30 deg of K. |
| twist-long-a2-knuckle-3r (+ crest-j3-wide-dyad-knuckle-3r merged) | **PICK 3** | The round's only lever on the reach half of 95. By proxy: parked reach 0.881 vs 0.831 (seed A, wdir(70, 15), a2 66) and hub 3 0.836 / L2 0.960 (seed B, crest wdir(88, 30), a2 58). The two candidates are the same lever (a J3 re-seat on the widened dyad), so they are merged with two seeds. Red team: proxy-only (no knee, neck, member 3 or drive metal); discount +0.05 -> ~+0.02 by the round-4 precedent; seed B's in-band gain is worthless once pick 1 reaches 0.90, so seed A leads; overhead stays hub-2-bound (axial-0 ray, +45..+99 mm); a2 66 raises the folded wall 31 -> 35. Worn on pick 1's drive; its law-only kill gate starts now. |
| sidecar-longdyad-knuckle-3r (+ wide-dyad-knuckle-3r merged) | **PICK 4** | The stretched-wall lever (a1max via bk2) on the in-band drive. Measured fast fold 30 -> 26 and in-band 0.911, but untuned near-touch is worse than pick 1 (13.91 vs 11.88). wide-dyad-knuckle-3r is the same lever on the crown-high rod: its bk1 35 is contradicted by real-model contact (check 6), and its rod stays 0 % in band, so it is merged here as a check cell (35 / 45 / 75). Red team: the lead's taken a1e stops at ~54.7, so the binding walls are m3e / lift-off / contact (check 3); a1max 66-75 needs dK 71-87, beyond the drive's crest / pa cap unless La / r_h >= 1.5. Kept separate from pick 1 because a local CMA from the lead's dyad will not cross the near-touch valley. |
| crest-j3-wide-dyad-knuckle-3r | merged into pick 3 | The same J3 re-seat lever; it becomes seed B. |
| wide-dyad-knuckle-3r | merged into pick 4 | The same a1max lever. Its bk1 widening is contradicted by the real-model contact measurement, and the crown-high rod stays 0 % in band. |
| lost-motion-swivel-knuckle-3r | not picked (valid, low rank) | Buildable: a 3 mm rod sliding in an igubal-class ball bore (1 passive translation, determined by |C - H| with K on stop A). It keeps the lobe's exact law and cuts complexity 49 -> 43, but expected gap reduction is 0. The rod stays crown-high (0 % in band) with an unmeasured ~11 mm tail over K's cap, and it adds a passive translation. Revisit only if complexity becomes the objective (score >= 95) and the msub ruling kills the crank-rod line. |
| crank-rod-knuckle-3r | parked: needs the user's say | Determined and buildable (RSSR, transmission 64 deg, cx 36.0), but under the current fold reading msub applies and it measures 48.7 fast. Even msub-free it misses its own gate: 16.91 vs 15.57 is 1.34 > 1.0. The msub question for a positively slaved K goes to the user (check 8). |
| bighorn-crank-rod-knuckle-3r | parked: needs the user's say | It inherits the msub ruling, and its only metal measurement is a rigid-rod probe that lost 87 poses to ROD-L1a (reach 0.46). If the user rules msub off for a driven K, it is the first follow-up: it is the strap-level crank-rod, the cx-36 route to 95 at low complexity. |

No candidate needs more than 2 passive translations. None has an undetermined passive coordinate: K is slaved and
never read, and the knee pins are sensed as in the lead. Every joint maps to a catalogue or machinable part.

## Ranking

Ranked by expected gap reduction vs the lead x confidence x buildability (0 passive translations first).

1. **sidecar-parallelogram-knuckle-3r**: about -3.8 frozen (to ~19), confidence high. This is the in-band half.
2. **sidecar-roller-flank-knuckle-3r**: about -3 frozen, confidence medium, complexity -3.75.
3. **twist-long-a2-knuckle-3r**: about -2 (reach +0.02 after discount) on top of pick 1, confidence low-medium. This is
   the reach half.
4. **sidecar-longdyad-knuckle-3r**: about -1 to -2.5 on top of pick 1, confidence low-medium. It holds the stretched
   wall.

Not picked: lost-motion (0 gain, 1 passive translation). Parked for the user: crank-rod and bighorn (msub).

## What runs next (parallel, nothing waits)

- Pick 1's model file is the base for picks 2 and 4 and the drive for pick 3. Build it first with the per-pose rod.
- Picks 3 and 4 start their law-only kill gates at once on the lead's model (no drive metal), and switch to pick 1's
  file when it lands.
- Pick 2 starts from the proposer's `camx` patch. The flank feasibility gate needs no seats re-fit.
- If picks 1 and 3 both pass, wear pick 3's seats on pick 1's drive (the planner's two halves of 95). Then the near-touch
  CMA, the frozen exact claim and the verifier.
- Question for the user (big update only, with the round result): does msub (the u1-uK-J3 sub-dyad margin) apply to a
  K that a positive four-bar drives from q2? A "no" opens crank-rod / bighorn at complexity 36.
