#!/usr/bin/env python3
"""What is a running workflow agent doing? Read the tail of its transcript (stdlib only; read-only).

    python3 tools/agent_tail.py                      list the newest workflow runs of every session (runId, agents, age,
                                                     the script name = the track, e.g. gen5-cad-geneva-rod)
    python3 tools/agent_tail.py wf_ee162f5e-871      list that run's agents: id, label, phase, last activity, done?
    python3 tools/agent_tail.py wf_ee162f5e-871 8    the last 8 entries of every agent of that run still running
    python3 tools/agent_tail.py <agent-id or .jsonl path> [N]   the last N entries (text / tool call / tool result) of one agent

Transcripts live under ~/.claude/projects/<project>/<session>/subagents/workflows/<runId>/agent-<id>.jsonl (+ .meta.json
with the label, journal.jsonl with each agent's started / result records). They belong to the session that launched
the workflow and vanish with its machine - the repo keeps what agents commit, not their transcripts. Use this to
check on agents WITHOUT messaging them: SendMessage to a running workflow agent resumes a second copy
(tools/workflows/README.md).
"""
import glob, json, os, sys, time

ROOT = os.path.expanduser("~/.claude/projects")


def runs():
    return sorted(glob.glob(os.path.join(ROOT, "*", "*", "subagents", "workflows", "wf_*")), key=os.path.getmtime, reverse=True)


def entries(path):
    out = []
    for line in open(path, errors="replace"):
        if not line.strip(): continue
        try: e = json.loads(line)
        except ValueError: continue
        c = (e.get("message") or {}).get("content")
        if isinstance(c, str): out.append((e.get("type"), c[:400])); continue
        for b in c or []:
            t = b.get("type")
            if t == "text": out.append(("text", b["text"][:600]))
            elif t == "tool_use": out.append(("tool", json.dumps(b.get("input"))[:300]))
            elif t == "tool_result":
                cc = b.get("content")
                s = cc if isinstance(cc, str) else " ".join(x.get("text", "") for x in cc or [] if isinstance(x, dict))
                out.append(("result", s[-500:]))
    return out


def tail(path, n):
    for kind, s in entries(path)[-n:]:
        print(kind, "|", s.replace("\n", " / ")); print()


def agents(run):
    done = set()
    jp = os.path.join(run, "journal.jsonl")
    if os.path.exists(jp):
        for line in open(jp):
            try: e = json.loads(line)
            except ValueError: continue
            if e.get("type") == "result": done.add(e.get("agentId"))
    rows = []
    for p in sorted(glob.glob(os.path.join(run, "agent-*.jsonl")), key=os.path.getmtime):
        aid = os.path.basename(p)[6:-6]
        meta = {}
        mp = p[:-6] + ".meta.json"
        if os.path.exists(mp):
            try: meta = json.load(open(mp))
            except ValueError: pass
        rows.append((aid, meta.get("description", "?"), meta.get("workflowPhase", "?"), time.time() - os.path.getmtime(p), aid in done, p))
    return rows


def script_name(run):
    """the launched script is saved as <session>/workflows/scripts/<name>-<runId>.js: its name says which track the run is"""
    sess = os.path.dirname(os.path.dirname(os.path.dirname(run)))
    rid = os.path.basename(run)
    m = glob.glob(os.path.join(sess, "workflows", "scripts", f"*-{rid}.js"))
    if m: return os.path.basename(m[0])[: -len(rid) - 4]
    try: return json.load(open(os.path.join(sess, "workflows", f"{rid}.json"))).get("workflowName") or "?"   # finished runs
    except (OSError, ValueError): pass
    # launched from a file path (e.g. the discovery loop from tools/workflows/): name it from its agents' labels
    labels = set()
    for mp in glob.glob(os.path.join(run, "agent-*.meta.json"))[:60]:
        try: labels.add(str(json.load(open(mp)).get("workflowPhase", "")).lstrip("\u25b8 ").split(" #")[0])
        except (OSError, ValueError): pass
    return "(path launch: " + ", ".join(sorted(x for x in labels if x))[:40] + ")" if labels else "?"


def main(a):
    if not a:
        for r in runs()[:12]:
            n = len(glob.glob(os.path.join(r, "agent-*.jsonl")))
            print(f"{os.path.basename(r)}  {n:3d} agents  last write {int((time.time() - os.path.getmtime(r)) / 60):4d} min ago  {script_name(r):<34} (session {r.split('/')[-4][:8]})")
        return
    n = int(a[1]) if len(a) > 1 else 0
    if a[0].startswith("wf_"):
        m = [r for r in runs() if os.path.basename(r) == a[0]]
        if not m: sys.exit(f"no run {a[0]} under {ROOT}")
        for aid, label, ph, age, fin, p in agents(m[0]):
            # no result record and no write for 30+ min: the agent was most likely stopped (an interrupt, a killed workflow)
            st = "done" if fin else ("RUNNING" if age < 1800 else "STALE?")
            print(f"{aid}  {label:<34} {ph:<10} {st:<8} last write {int(age / 60)} min ago")
            if n and not fin: tail(p, n)
        return
    p = a[0] if a[0].endswith(".jsonl") else next(iter(glob.glob(os.path.join(ROOT, "*", "*", "subagents", "**", f"agent-{a[0]}.jsonl"), recursive=True)), None)
    if not p: sys.exit(f"no transcript for {a[0]}")
    tail(p, n or 6)


if __name__ == "__main__":
    main(sys.argv[1:])
