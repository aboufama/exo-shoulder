# Concept families (wide-tree stage, 2026-10-15)

The user, 2026-10-15: "have intelligent agents instead of GPUs run the first find and look for promising families or
weird concepts, and then do a gpu optimization on that family, so we can spread a wider tree". Families are
categorised by ACTIVE DOF (REQUIREMENTS.md: a passive element the arm drives - e.g. a cuff slide set by the chain's
closure - is outside the count); the target is 3 active DOF. GPU sweeps are short, per subtype within a family.

Each family gets docs/concepts/<family>.md: the idea, a sketch, active / passive DOF count and why, an idealised model
measured with tools/concept_bench.py (same rig, same poses, same metrics for every family: reach, follow, in-band
2-14 / 2-10, contact), what limits it, unpowered behaviour (does anything sag or self-lock?), manufacturability / CAD
standard notes, and a parameterisation for a short GPU sweep. A row goes into docs/concepts/families.json.

Baseline to beat (the current family, spherical 3R with every joint axis through the GH centre, O20 hubs):
evaluator ~75 % of the everyday workspace, ~40 % in band at 14 mm, ~95-98 % follow; built CAD R1 41-58 %,
R3 98.2 % (r20 s1414 #4), R16 78.3 % (c1).
