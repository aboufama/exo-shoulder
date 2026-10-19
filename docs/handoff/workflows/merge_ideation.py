import json, sys, time
wf, src, lenses, tag = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4]
J=f"/root/.claude/projects/-home-user-exo-shoulder/83445525-dbfd-5a74-afa6-eaabc370b170/subagents/workflows/{wf}/journal.jsonl"
res=[json.loads(l) for l in open(J)]; res=[e for e in res if e.get("type")=="result" and isinstance(e.get("result"),dict) and "morphologies" in e["result"]]
now=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
cat=json.load(open("docs/concepts/catalogue.json")); have={e["id"] for e in cat}
new=[]
for k,e0 in enumerate(res):
    for m in e0["result"]["morphologies"]:
        e=dict(m); e["lenses"]=[lenses[min(k,len(lenses)-1)]]; e["t_ideated"]=now; e["source"]=src
        if e["id"] in have: e["id"]+="-"+tag.lower()
        have.add(e["id"]); cat.append(e); new.append((e["id"], e["name"][:90], e["active_dof"], e["passive_dof"], e["topology"][:100]))
json.dump(cat, open("docs/concepts/catalogue.json","w"), indent=1)
for n in new: print(n)
print(len(cat), "catalogue;", len(new), "new")
