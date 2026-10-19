# docs/alignment - the alignment auditor's outputs

The user, 2026-10-16 ~20:10 UTC: "please require an agent on the side that is a superfan that targets misalgnment ...
see if models are cheating the system or gaming the system in some way to scro ehigher witout actually being beter ...
it needs to be a crucial aprt of our loop". The rule is in CLAUDE.md ("Alignment auditor"); the catalogue of gaming
patterns and the thresholds are in [`../ALIGNMENT.md`](../ALIGNMENT.md).

| file | written by | what |
|---|---|---|
| `ledger.jsonl` | `tools/alignment_ledger.py` (append-only, merges by union) | one line per ruling: `{time, id, verdict, reasons, claim, claim_field, stage: audit / skeptic, by, ...}`. The latest line per id is the verdict. |
| `<id>.json` | `tools/alignment_audit.py audit <id>` | the 12 automatic checks, each ok / watch / gamed with a measured reason |
| `<id>.findings.json` | the auditor agent | the judgement pass: patterns of ALIGNMENT.md section 2 found by reading the design |
| `<id>.rulings.json` | the skeptic agent | each reason refuted (with evidence) or upheld |
| `<id>.md` | auditor + skeptic | the human report: verdict, what the wearer gets, findings, rulings |
| `remeasure/` | `tools/alignment_audit.py remeasure` | frozen claims re-worn with the models unchanged |
| `live_audit_2026-10-16*` | the first live audit | dashboard, metric and leaderboard findings with proposals P1-P8 |

How it runs: `tools/workflows/alignment-audit.js` (auditor, then a skeptic on every gamed / watch verdict) after every
claim, verification, new leader and judge / metric change, inside the discovery loop (Audit phase between Screen and
Close) and hourly. `python3 tools/alignment_ledger.py latest` shows every verdict; `get <id>` exits 3 when the design is
gamed; `due --since <ISO>` lists what needs an audit. A 'gamed' design cannot be called verified, a winner or a leader
until the finding is resolved. The dashboard's morphs dataset carries the latest verdict per design (`alignment*` fields).
The verdicts verify only arithmetic and records: the ledger tool computes every verdict from the checks, the findings and
the rulings, so no agent grades its own audit.
