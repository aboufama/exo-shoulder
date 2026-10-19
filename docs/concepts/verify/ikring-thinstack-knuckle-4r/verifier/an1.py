import json, sys, numpy as np
V='/home/user/exo-shoulder/docs/concepts/verify/ikring-thinstack-knuckle-4r/'
o=json.load(open(V+'ik_bench_spec.json')); pp=json.load(open(V+'ik_bench_spec_perpose.json'))
first=json.load(open(V+'ik_bench.json'))
ch=first['ik']['choice']; KS=first['ik']['ks']
P=pp['poses']; print('report',pp['report'] if not isinstance(pp['report'],dict) else {k:v for k,v in pp['report'].items() if k!='poses'}); print('recomputed',pp['recomputed'])
ws=[p for p in P if p['kind']=='ws']; cl=[p for p in P if p['kind']=='clip']
tk=[p for p in ws if p['taken']]; print('ws taken',len(tk),'contacts',[(p['i'],p['min_mm']) for p in P if p['contact']])
mt=sorted([(p['min_mm'],p['i']) for p in P if p['taken']])[:8]; print('T1 lowest taken metal',mt)
print('T5 sum', round(sum(-p['min_mm'] for p in P if p['contact']),2))
# new takes
nl=o['ik']['new_list']; print('new takes',len(nl))
single=[];runs=[];at40=0
for t in nl:
    c=ch[str(t['i'])]; tks=sorted(float(k) for k in c['takes']); k=t['k']
    # contiguous run containing k
    s=set(tks); lo=k; hi=k
    while round(lo-2.5,3) in s: lo=round(lo-2.5,3)
    while round(hi+2.5,3) in s: hi=round(hi+2.5,3)
    runs.append((t['i'],t['pose'],k,t['mm'],len(tks),lo,hi))
    if len(tks)==1: single.append(t['i'])
    if k==40: at40+=1
print('single-k',single,'at k=40',at40)
for r in runs: print(r)
# under-2mm new takes
print('new under 2', [(t['i'],t['pose'],t['k'],t['mm']) for t in nl if t['mm']<2])
