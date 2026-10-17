# spiral-lobe-longdyad-knuckle-3r (round 12, pick 1)

Spiral-lobe long-dyad knuckle 3R: inband-rssr pick3's in-band RSSR K drive on an efficient 34/48 K dyad, an early K
onset and a log-spiral hub-2 lobe. Merged: desmo-spiral-rssr (spring-free cell C) and conecut-longdyad (the re-centred
knee + J3 stop column). 3 active DOF (J1, J2, J3), K slaved and never read, 0 passive translations.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the K law as a per-pose decision,
   not a gain. The judge measured that the long dyad's extra closures split into takes and hub-2 / link-2 skin hits.
   A designer would not search kK blindly. They would tabulate each newly closed pose (K, th, the part in the skin,
   elevation, axial) and read the law off it. The law has three cuts: the gain (how fast K opens), the onset (smhi:
   where it starts) and stop B (a1max: where it ends). If the contact poses sit at large K, stop B turns them into
   plain fold losses. Each such pose saves about 0.25 points (a contact costs reach plus the contact term; a fold
   costs reach only), and the takes at smaller K stay. They would also check the reverse: whether the knee column
   re-opens the extra knee slides (10 -> 13) without new metal.
2. **The rawest material.** The posed skin itself (concept_bench's exact signed distance per pose: CB_EXACT=1,
   Bench(110,360)). The per-pose metal of every part (M.rigid, M.contact, M.link_pts) in that pose's frame. The
   workspace pose list (plane / elev / axial) and the clip frames. Not the digested "fold 64, contact 14" counts:
   the per-pose table (g0_*.json in the scratch dir) is the data the law is chosen from.
3. **Methods and tools.** The real chain model (docs/concepts/models/inband-rssr-knuckle-3r.py, loaded unchanged, with
   IB_GHOST=all for gate 0 and the drive metal back for gate A). The frozen protocol: fit Bench(60,160) fast, shape
   frozen, worn on Bench(110,360) exact. The conecut knee + J3-stop subclass. A per-pose attribution harness
   (part-by-part signed distance). Then a small grid on (kK, smhi, a1max), then CMA on the envelope bench, but only
   if gate 0 passes. The farm is at its budget line ($24.42 at 15:21 UTC against the $24.40 line), so everything
   runs locally, at most 2 niced processes.
4. **What, other than me, shows the number is right.** The bench's exact path (CB_EXACT=1) on the frozen shape. The
   judge's own reproduction (pick3 ghost 18.32, seed ghost 18.84) re-run first as the control. Later the adversarial
   verifier and the alignment auditor (paired against slipper-nose, `tools/alignment_audit.py audit --ref
   slipper-nose-knuckle-3r`). And the red-team pose list: the contact poses by part and depth, the knee-slide poses,
   the overhead cone (elev >= 140), all in the per-pose dump.
