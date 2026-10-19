import json, numpy as np
V='/home/user/exo-shoulder/docs/concepts/verify/ikring-thinstack-knuckle-4r/'
o=json.load(open(V+'ik_bench_spec.json')); first=json.load(open(V+'ik_bench.json'))
ch=first['ik']['choice']; nl={t['i']:t for t in o['ik']['new_list']}
pp=json.load(open(V+'ik_bench_spec_perpose.json'))['poses']
el={p['i']:p['elev'] for p in pp}
def count(ks):
    ks=set(round(k,3) for k in ks); n=0; ov=0
    for j,t in nl.items():
        c=ch[str(j)]
        if any(round(float(k),3) in ks for k in c['takes']): n+=1; ov+= el[j]>=140
    return n,ov
grids={'2.5 (claim)':np.arange(0,40.01,2.5),'5.0':np.arange(0,40.01,5),'10.0':np.arange(0,40.01,10),'0..35 step2.5':np.arange(0,35.01,2.5),'0..30':np.arange(0,30.01,2.5),'0..20':np.arange(0,20.01,2.5),'0..37.5':np.arange(0,37.51,2.5)}
for g,ks in grids.items():
    n,ov=count(ks); ws=260+n; reach=ws/360
    print(g,'new takes',n,'ovh new',ov,'ws',ws,'reach',round(reach,4),'gap_est(chain-only ib .8901, same contacts)',round(100*(0.9-reach)+0.99+0.98,2))
# take-only with margin: require min metal >= 1 at chosen k (any k)
for thr in (0.5,1.0,2.0):
    n=sum(1 for j in nl if max(ch[str(j)]['takes'].values())>=thr); print('new takes with some k at metal >=',thr,':',n)
