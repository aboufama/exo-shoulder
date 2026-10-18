# phi40-thinstack-relay-4r: a longer one-sided over-pass relay (PHI 40) on the thin stack

Round 107 (J7 track jump), lens A fallback, run in parallel with underpass-bridge-relay-4r. lugcoil-lbracket-relay-4r is
merged here as its PHI 35 cell. 4 counted joints (J1, J2, J3 + the relay). It is a user option, never a lead.

## Deeper-version answers (written before the model)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Price the relay as a whole machine, not as a gap number.
   - The parent's verifier showed a 0.5 deg cliff (E over the carriage) and a 1.002 mm clearance floor.
   - So the designer would choose delta inside a window that is legal on both sides, and read the window BEFORE the
     claim: delta - 1 (the 259 contact comes back) and delta + 1.5 (the E-over-carriage jams).
   - The designer would also check the anterior shell end against the posed torso one bin at a time. A long shell can
     only gain if its last few degrees take poses without touching the skin.
   - The designer would ask whether the extra 5 deg buys reach that a person actually uses. Overhead is the user's
     priority, and the parent's relay bought 0 overhead.
2. **The rawest material.**
   - The posed skin itself: the bench's signed distance on every envsel / claim / held frame.
   - The motion clips and the 1432-pose workspace envelope grid, used by the continuity flood.
   - The clip-p90 skin radius about the relay axis a_r at the station (the proposer's longshell.py profile: 73.60 at
     +2 deg, 72.3 at +28, 69.3 at +44, 66.7 at +56).
   - The per-point shell distances, binned by azimuth (written by this model's 2-deg end bins).
   - Digested summaries are used only as pointers.
3. **Methods and tools.**
   - The parent's verified model, imported read-only (offset-shortcar-relay-4r -> proxtrack buildability ->
     armarc), with three source patches: the thin shell, the L-lug and the 2-deg end bins.
   - tools/env_bench.py envsel for selection, the exact signed-distance path, and Bench(110,360) exact frozen for the
     claim.
   - The held bench for held-out.
   - The armarc continuity flood (2-deg slerp edges, relay jump <= 10 deg) on the 1432-pose envelope grid at PHI 40.
   - tools/alignment_paired.py per-pose dumps (T5).
   - The armarc gravity check (R17).
4. **What, other than me, shows the number is right.**
   - The bench, read once at a pick that was pre-registered on envsel.
   - The held set.
   - An independent verifier rerunning the claim from this file.
   - The alignment auditor.
   - A red-team pose list: the anterior-end bins (envsel 119, behind-back ER), delta + 1.5 (the E-over-carriage cliff),
     delta - 1 (259), and the relayed poses at phi 35-40 that the PHI 35 flood never saw.

## Model (docs/concepts/models/phi40-thinstack-relay-4r.py)

The model imports offset-shortcar-relay-4r read-only. The chain is the verified lead's, with the buildable knee-over-boss
stack in every reading. The changes are:

- **PHI 40.** This needs its own prepare and its own continuity flood (flood_PHI40_t12_a235_s1.json in this row's
  verify dir).
- **Thin stack.**
  - The shell is 1.0 mm thick. The underside stays at R_liner; R_t = R_liner + 1.0, and the carriage, the bump target
    and the coil drop with it.
  - Lean flag: h_c 1.4, the slot end is the PHI stop, one zero dowel.
  - **Spec correction:** the proposer's patch read the pre-arc floors at R_liner + 1.5. Here they are re-read at the thin
    shell's R_t (each end 0.04 deg longer, conservative).
- **Lug coil 12 x 10:** a constant-force strip on the carriage's posterior-proximal lug. It is on the carriage-frame jam
  list and is sampled as metal.
- **Band 8, bump 1.2.**
- **L-lug bracket:** 2 x 10 Ti at the pad azimuth for every s (no planform turn), leaving the carriage at its
  posterior-distal corner.

## Results

(filled in below as the readings land)

### Selection protocol (envsel exact only; registered before each reading)

- Cells read at 19:33 UTC: PHI 40 x delta {3.5, 5.0, 4.0, 5.5}, plus the proposer's control (delta 4.5 with the old
  bracket). PHI 42 x delta {3.5, 5.0}.
- Registered at 19:40 UTC, BEFORE reading it (the PHI 40 / 42 trend is monotone so far): PHI 44 x delta {3.5, 5.0}.
- PHI 38 is a spec cell that was not read in the time box (see below).
- Pick rule (the spec's): the lowest gate with 0 jams whose delta + 1.5 partner reads 0 jams and lies within +0.5 of
  the pick. The claim bench is read ONCE at the pick. A claim-bench delta + 1.5 reading follows it as a red-team
  diagnostic that cannot change the pick.
