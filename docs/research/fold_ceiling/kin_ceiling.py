"""fold-ceiling step 2a: the EXACT kinematic reach ceiling of the family (J1 scapula-fixed, J3 humerus-fixed, J2 on a GH
ray, a knuckle K that changes the J1-J2 arc a1e within [a1lo, a1hi]) on the frozen bench's 360 workspace poses and the
952 held-out ones. A pose closes with the 5 deg fold margin iff th = angle(u1, Q u3) lies in the union over a1e of
[|a1e - a2| + 5, min(a1e + a2, 360 - a1e - a2) - 5], i.e. (a1lo <= a2 <= a1hi gives lo = 5)
    th in [max(5, min_a1e |a1e - a2| + 5), a1hi + a2 - 5]                                        (W = window width)
For a one-sided knuckle (K opens on the stretched side only, every leader) a1lo = a1 (stop A) and, with a1 <= a2,
W = a1 + a1hi - 10: a2 only SHIFTS the window. This script measures, for every seat pair in the user's J1 ruling (back
of the shoulder + acromion top) and J3 on the upper arm, the share of poses inside the best window of width W, and the
leader's own seats with its window moved.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/kin_ceiling.py
"""
import importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402

Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
ws_id = names.index("Workspace (envelope)")
b_idx = CB._select(110, 360)[0]; b_ws = b_idx[cid[b_idx] == ws_id]
used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
h_ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in used], int)
f_ws = CB._select(60, 160)[0]; f_ws = f_ws[cid[f_ws] == ws_id]
QB, QH, QF = (Z["HG"][ix].astype(float) for ix in (b_ws, h_ws, f_ws))
POSE = Z["POSE"]; elevB = POSE[b_ws][:, 1]; elevH = POSE[h_ws][:, 1]
lead = json.load(open(os.path.join(HERE, "lost_poses_roller-longdyad-knuckle-3r.json")))
u1L, u3L = np.array(lead["u1"]), np.array(lead["u3"])


def th_of(Q, u1, u3):
    """(n_seat1, n_seat3, P) th in deg for seat sets u1 (a, 3), u3 (b, 3)"""
    w = np.einsum("pij,bj->bpi", Q, u3)
    return np.degrees(np.arccos(np.clip(np.einsum("ai,bpi->abp", u1, w), -1, 1)))


def best_window(th, W, lo_min=5.0):
    """share of poses inside the best window [lo, lo + W], lo >= lo_min, per seat pair: th (..., P) -> (...,), lo"""
    s = np.sort(th, -1); P = s.shape[-1]
    hi_idx = np.stack([np.searchsorted(r, np.maximum(r, lo_min) + W, side="right") for r in s.reshape(-1, P)]).reshape(s.shape)
    lo_ok = s >= lo_min - 1e-9
    cnt = np.where(lo_ok, hi_idx - np.arange(P), 0)
    # windows starting below the first pose >= lo_min: [lo_min, lo_min + W]
    c0 = ((s >= lo_min) & (s <= lo_min + W)).sum(-1)
    best = np.maximum(cnt.max(-1), c0)
    return best / P


# seat grids: J1 in the user's ruling (back of the shoulder az -90..90 el -20..80; acromion top az 90..135 el >= 50), J3 on the arm
az = np.arange(-90, 136, 7.5); el = np.arange(-20, 86, 7.5)
A1 = [(a, e) for a in az for e in el if (a <= 90) or (e >= 50)]
U1 = K.bvec(np.array([a for a, e in A1]), np.array([e for a, e in A1]))
dd = np.arange(30, 151, 7.5); aa = np.arange(-180, 180, 10)
A3 = [(x, y) for x in dd for y in aa]
U3 = K.wdir(np.array([x for x, y in A3]), np.array([y for x, y in A3]))
out = dict(n_seats1=len(A1), n_seats3=len(A3), bench_ws=len(b_ws), held_ws=len(h_ws), curves={})

# 1) the leader's own seats: th of every pose, the share inside [lo, hi] for the walls the levers move
thL = th_of(QB, u1L[None], u3L[None])[0, 0]; thLH = th_of(QH, u1L[None], u3L[None])[0, 0]
lo0, hi0 = lead["window"]
lead_tab = {}
for lo in (5.0, 10.0, 15.0, 20.0, lo0):
    for hi in (hi0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 150.0):
        lead_tab[f"{lo:.2f}-{hi:.1f}"] = [int(((thL >= lo) & (thL <= hi)).sum()), int(((thLH >= lo) & (thLH <= hi)).sum())]
out["leader_seats"] = dict(window=[lo0, hi0], counts_bench_held=lead_tab,
                           best_W={W: [round(float(best_window(thL[None], W)[0]), 4), round(float(best_window(thLH[None], W)[0]), 4)]
                                   for W in (70, 80, 86.3, 90, 95, 100, 105, 110, 115, 120, 130)})

# 2) every allowed seat pair: best share at window width W (fit on the bench's 360, then the SAME seats + window on held out).
#    Exact counts via a 0.5 deg cumulative histogram of th per seat pair (a window edge is rounded OUTWARD by < 0.5 deg:
#    an upper bound on the share, never below it); the winner is re-counted exactly.
TH = th_of(QB, U1, U3)                                                     # (a, b, 360)
na, nb, P = TH.shape; nbin = 361
bins = np.clip(np.floor(TH * 2).astype(np.int32), 0, nbin - 1).reshape(na * nb, P)
H = np.zeros((na * nb, nbin), np.int16)
for j in range(P): H[np.arange(na * nb), bins[:, j]] += 1
C = np.concatenate([np.zeros((na * nb, 1), np.int16), np.cumsum(H, 1, dtype=np.int16)], 1)    # C[:, k] = # th < k / 2
del TH
for W in (80, 86.3, 90, 95, 100, 105, 110, 115, 120, 130):
    w2 = int(math.ceil(W * 2)) + 1; los = np.arange(10, nbin - w2 + 1)          # lo >= 5 deg
    cnt = C[:, los + w2] - C[:, los]                                            # (pairs, L): # th in [lo/2, (lo + w2)/2)
    best = cnt.max(1); k = int(np.argmax(best)); lo_b = los[np.argmax(cnt[k])] / 2.0
    ka, kb = divmod(k, nb)
    thh = th_of(QH, U1[ka][None], U3[kb][None])[0, 0]; thb = th_of(QB, U1[ka][None], U3[kb][None])[0, 0]
    out["curves"][str(W)] = dict(bench=round(float(best[k] / P), 4), bench_exact=round(float(((thb >= lo_b) & (thb <= lo_b + W)).mean()), 4),
                                 lo=float(lo_b), seat1=A1[ka], seat3=A3[kb],
                                 held_same=round(float(((thh >= lo_b) & (thh <= lo_b + W)).mean()), 4),
                                 n_pairs_ge_083=int((best / P >= 0.83).sum()), n_pairs=int(na * nb))
    print(W, out["curves"][str(W)], flush=True)
json.dump(out, open(os.path.join(HERE, "kin_ceiling.json"), "w"), indent=1, default=float)
print(json.dumps(out["leader_seats"], default=float))
