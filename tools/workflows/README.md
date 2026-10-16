# Discovery workflow scripts (copies of the running ones)

The user, 2026-10-16: "dont just stop on round 4 go as far as you can!". Discovery runs as a self-driving loop:

- `discovery-loop.js` (args `{first_round, n_rounds, track, focus}`): per round a planner reads the latest measurements
  (FINDINGS, docs/research/reach_attribution.md, rows, catalogue, events) and writes the round state + 2-3 lenses, then
  runs `discovery-ideate.js` (lenses ideate, a judge picks the top into the catalogue) and `exo-screen.js` (model, farm
  sweep to the convergence gate, red team, motion preview, independent verifier on Bench(110,360) exact frozen) in slices
  of two, and a closer writes docs/concepts/ROUNDS.md + FINDINGS and the next round's focus.
- Generation winners (best verified per round) then get the final polish and the full user-style CAD + stills
  (CLAUDE.md), launched by the session lead.

The scripts reference the session scratchpad paths of the session that wrote them; a new session copies them to its
own scratchpad and fixes `SP` before running them with the Workflow tool.

## Do not message a running workflow agent (measured 2026-10-16)

`SendMessage` to the agentId of an agent running inside a workflow does not reach that agent. It **resumes a second
copy** from the same transcript, as a separate background agent. Both copies then run the same plan on the same files:
they wait on the same farm batch, write the same model files and race each other on the GPU pods' override driver.
This happened twice (Track A of wf_b870688f-426 and the pin-knee GPU search wf_9bce650d-b9e). The fix was to stop the
workflow and keep the informed copy, or to split the duties between the two copies. Later messages to that agentId go
to the resumed copy only. To steer workflow agents, put the facts in the repo (row / FINDINGS / a note file the
prompt tells them to read), or stop the workflow and relaunch the stage with the new facts in its prompt (resume keeps
the finished agents cached).
