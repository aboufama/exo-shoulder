export const meta = {
  name: 'exo-tracks',
  description: 'Restart stopped work tracks (each: do the work to a hard numeric target in a time box, then an adversarial verifier re-measures)',
  phases: [
    { title: 'Work', detail: 'one agent per track, time-boxed, hard target' },
    { title: 'Verify', detail: 'a skeptic re-measures the track\'s key claim' },
  ],
}

// args: { tracks: [{ key, prompt, verify }] }
const COMMON = `Repo /home/user/exo-shoulder, branch claude/exo-shoulder-mechanism-wy35fx. The CLAUDE.md rules apply in full - especially the ambition rules (speed assumed, outcome = all 19 requirements, a hard numeric target, an outside judge, a red team, new knowledge written down) and the hard rules (paid compute: state type + cost; never print keys; personal data in data/raw/private never leaves the machine; only BOTTOM of the user's parts may change). The machine's 4 cores are saturated by a dozen agents: keep jobs light locally (nice, OMP_NUM_THREADS=1, <= 2 processes) unless you move them to the cloud. One shared working tree: git add ONLY your own files; commit with a message ending in
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HShoE3xJTcjMWRx4v2yePx
and push with git push -u origin claude/exo-shoulder-mechanism-wy35fx (if rejected: git pull --rebase --autostash, then push). Never use pkill -f; kill by PID. Append one line per real result to docs/concepts/events.jsonl: {"time": ISO UTC, "kind": "milestone"|"measurement"|"infra", "event": "..."} (append with >>). Final answer: the measured numbers before/after, what changed, what is still failing and why, and what happens next.`

const VERDICT = { type: 'object', properties: {
  refuted: { type: 'boolean' }, checked: { type: 'string' }, numbers: { type: 'string' }, issues: { type: 'array', items: { type: 'string' } },
}, required: ['refuted', 'checked', 'numbers', 'issues'] }

const res = await pipeline(args.tracks,
  (t) => agent(`${COMMON}\n\nTRACK ${t.key}:\n${t.prompt}`, { label: `work:${t.key}`, phase: 'Work' }),
  (out, t) => agent(`${COMMON}\n\nYou are the VERIFIER (red team) of track ${t.key}. The track reports:\n${out}\n\nTry to refute its key claims: ${t.verify}\nRe-measure rather than re-read; fix nothing yourself except a broken check, which you then report. refuted = true if a headline claim does not hold.`,
    { label: `verify:${t.key}`, phase: 'Verify', schema: VERDICT }).then(v => ({ key: t.key, report: out, verdict: v })))
return res.filter(Boolean)
