# roller-longdyad-knuckle-3r final polish on the envelope bench (2026-10-17): tool built, farm search NOT run

Self-measured. The generation-6 winner (verified 18.67 frozen exact on Bench(110,360), score 93.21; held out 23.73) was
to be polished on the representative envelope bench `env` and claimed on the held-out set through the verifier's own
harness. **The search did not run.** The farm batch that carries it (8 CMA runs + 2 env re-scores, about $0.4 of the
$1.5 budget) was refused by this session's permission policy at launch (paid compute). The env fast caches exist only
on the farm volume. Rebuilding them here was measured at about 6.5 s per pose per process: 530 + 470 poses, about an
hour with 2 processes under this box's load of 11-15 from other agents. That does not fit the 120-minute time box.

**Verdict: no polished config. The verified config stays the CAD config (held-out gain 0, nothing claimed).** What did
run, locally with 2 processes, is the claim harness on the verified config. It answers the alignment audit's four
watches as measurements. Everything is ready for one farm command once the farm is permitted (section 6).

RESULTS_PLACEHOLDER
