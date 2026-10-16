# sidecar-longdyad-knuckle-3r final polish on the envelope bench (2026-10-16)

Self-measured. The round-8 winner (verified 18.91, score 93.12, held out 22.67) is polished on the representative
envelope bench `env` and claimed on the held-out set and on the verified protocol through the verifier's own harness
(`docs/concepts/verify/sidecar-longdyad-knuckle-3r.py`, imported unchanged; `tools/sidecar_env_polish.py claim` only swaps
the fit bench and adds the th-margin read-out). A polished config replaces the CAD's config only after an independent
verifier confirms a held-out gain >= 1 gap point AND it beats the verified config on the plain gap and at 2 mm
(the user's dominance gate, 2026-10-16 ~21:05).

__RESULTS__
