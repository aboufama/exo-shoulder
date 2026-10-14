# CAD standard

**Scope (user, 2026-10-14):** this standard is level **L2** - the CAD of a design that already passed the motion judges
(R1-R6, R10) on held-out data and that the user chose (phase P4). Every iteration before that uses **L1 keep-out CAD**:
joint keep-outs (hub diameter x real stack height), links as constant-thickness slabs at their real height over the
skin, rail / carriage envelopes, one valid solid per part - no fillets, G2 blends, fairing or zebra checks. Fidelity
that matters for the judges (heights, clearances, keep-outs, mass) must be right at L1; looks wait for L2.

The user's own parts (`data/user_cad/RIGHT ARM SUBASSY.step`: TOP, MIDDLE, BOTTOM, FOREARM CUFF) set the bar: clean
feature CAD, few faces (TOP = 17), planes / cylinders / cones + G2 B-spline blends.

## The user's rules

- Every custom part is a genuinely smooth G2 body. No boolean cuts that get filleted afterwards; no hard edges on links
  and brackets ("hard edges are intentional" on cuffs - a deliberate edge is fine, an accidental one is not).
- No visible screws or seams. At most "a screw or two", super low profile, sunk flush.
- Zero collisions across the motion: with the body and between parts (R2, R6).
- Manufacturable (R13). Look: everything bead-blasted aluminium / titanium, polished stainless screws, iglidur orange
  polymer parts. **No black parts.**
- Parts must look *constrained and accurately designed* - not "weirdly meshed". Surfaces fitted to noisy data read as
  sloppy even when they are G2.
- Never edit the user's parts except BOTTOM (which may be cut and merged with the neck into one 5-axis part). Never
  edit their Onshape model.
- Engineering drawings (when needed): only threads and tight tolerances beyond the STEP; no material/finish rules.

## Construction rules learned the hard way

1. **Outlines are sketches**: lines + tangent arcs with set radii (the cuff saddle: 5 lines + 5 arcs; links: O23 hub
   circles + a 14 mm strip). Never a level set of a data field.
2. **Surfaces are fair by construction**: a swept constant section along one fair profile (links), a revolve (hubs), or
   a stiff shrink-wrap (bi-Laplacian obstacle problem) over a *smoothed* envelope (cuff). Never interpolate raw
   envelope data.
3. **Exact seats**: every seat is an exact plane, flat under the whole mating part (the O22 cap skirt needs the hub flat
   to r 11 -> 0.5 mm edge rounds on links).
4. **Stacked joints**: links leave a shared joint parallel to their seats and ramp at <= 35 deg; the lower link
   thickens toward the skin, not up into the upper link.
5. **Booleans**: never let fused faces coincide or touch tangentially. Embed (start the neck 6 mm inside the hub) or use
   the OCC glue fuse for exactly coincident faces (`pipeline/conformal/cad_helpers.glue_fuse`). Cutting tools cross
   faces transversally.
6. **Check before showing**: `judge/part_validity.py` (one valid solid each), then `parts.html` with the zebra mode -
   stripes must run continuously across every blend.
7. OCC `Volume()` is unreliable on the sewn sheet bodies: use the closed tessellation (mesh volume).
