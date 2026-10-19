import json, sys, numpy as np
def load(f):
    d = json.load(open(f)); P = d["poses"]; return d, P
def gap(P, idx=None):
    if idx is None: idx = np.arange(len(P))
    Q = [P[i] for i in idx]
    ws = [p for p in Q if p["kind"] == "ws"]; cl = [p for p in Q if p["kind"] == "clip"]
    reach = np.mean([p["taken"] for p in ws]); follow = np.mean([p["taken"] for p in cl])
    ns = sum(p["ns"] for p in cl if p["taken"]); nib = sum(p["nib"] for p in cl if p["taken"])
    ib = nib / ns if ns else 0
    ev = [p for p in Q if p.get("ev")]; contact = np.mean([p["contact"] for p in ev]) if ev else 0
    return 100 * (max(0, .9 - ib) + max(0, .95 - follow) + max(0, .9 - reach)) + 100 * contact, dict(reach=reach, follow=follow, ib=ib, contact=contact, nev=len(ev))
a = sys.argv[1]; b = sys.argv[2]
da, Pa = load(a); db, Pb = load(b)
ga, ia = gap(Pa); gb, ib = gap(Pb)
print("A", round(ga, 3), {k: round(float(v), 4) for k, v in ia.items()}, "frozen", da["frozen"]["gap"])
print("B", round(gb, 3), {k: round(float(v), 4) for k, v in ib.items()}, "frozen", db["frozen"]["gap"])
assert [p["i"] for p in Pa] == [p["i"] for p in Pb]
ws = np.array([p["kind"] == "ws" for p in Pa])
ta = np.array([p["taken"] for p in Pa]); tb = np.array([p["taken"] for p in Pb]); ca = np.array([p["contact"] for p in Pa]); cb = np.array([p["contact"] for p in Pb])
print("ws taken A/B", int(ta[ws].sum()), int(tb[ws].sum()), " gained", int((~ta & tb & ws).sum()), "lost", int((ta & ~tb & ws).sum()), " contacts A/B", int(ca.sum()), int(cb.sum()))
print("clip taken A/B", int(ta[~ws].sum()), int(tb[~ws].sum()))
rng = np.random.default_rng(0); n = len(Pa); diffs = []
for _ in range(1000):
    s = rng.integers(0, n, n); diffs.append(gap(Pa, s)[0] - gap(Pb, s)[0])
diffs = np.array(diffs); print("gain A-B", round(ga - gb, 3), "bootstrap 5/50/95 %", np.round(np.percentile(diffs, [5, 50, 95]), 3), "P(gain>=1)", round(float(np.mean(diffs >= 1)), 3), "P(gain>0)", round(float(np.mean(diffs > 0)), 3))
