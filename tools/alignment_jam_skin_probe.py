"""Alignment probe (new file, audit 2026-10-19; read-only): how deep is the metal in the skin at the poses a pin-knee-style
model scores as PART JAMS?

The H1-family run loop (docs/concepts/models/skin-normal-3r-pin-knee.py _run_batched) checks part clearances first: a
pose whose clearance is < S.PART_CLEAR is recorded as not taken (res None) and its skin distance is never evaluated. The
bench's contact term counts only evaluated poses (tools/concept_bench.py report(): contact over res is not None). So a
pose where the parts jam AND the metal is inside the arm costs reach / follow only, while the same pose without the jam
costs reach / follow AND 100 / n_evaluated contact. This probe wears the frozen claim exactly as the model's frozen()
does (fit Bench(60,160) fast, shape frozen, wear Bench(110,360) exact) and, at the wear only, evaluates the skin distance
of every pose the model records as a part jam (same metal + contact-only samples, same B.dist), with the deepest part.
The model runs UNCHANGED: only its run() on the EXACT wear bench is swapped for a copy of the loop that stops after the
jam poses (the fit bench keeps the original run). No score is changed; the 'as if contact' gap is a proposal reading.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_jam_skin_probe.py <id> <out.json> [ModelClassName, default Model]
"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_audit as AA                                   # noqa: E402


class _Done(Exception):
    pass


def run(rid, cls_name=None):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row["best_params"])
    mod = AA._load("jamprobe_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    S = mod.PK.S; Model = getattr(mod, cls_name or "Model"); box = {}
    # the copied loop below is H1's _run_batched: patch it where the class chain defines it (a subclass run() that only
    # wraps fit and calls super().run(), as the knuckle family's KModel.run, keeps working); refuse any other loop
    base = next((c for c in Model.__mro__ if getattr(c.__dict__.get("run"), "__name__", "") == "_run_batched"), None)
    if base is None: raise SystemExit(f"{rid}: no H1 _run_batched in {Model.__name__}'s class chain")
    orig = base.run

    def jam_run(self, B=None):
        B = self.B
        if B.mode != "exact" or len(B.idx) != 470: return orig(self)      # the fit bench Bench(60,160) keeps the original run
        B.reset(); self.fit()
        valid = set(self.poses_fit.tolist()); dropped = set(self.poses_fit[self.drop].tolist()); self.last_pair = {}
        names = list(self.rigid) + list(self.link_pts)
        jams, n_eval_ok, why = [], 0, {}
        for i in range(len(B.idx)):
            if i not in valid: continue
            cl = self.collide(i); pair = min(self.last_clear, key=self.last_clear.get)
            if cl < S.PART_CLEAR and not (self.p.get("jam_contact") and i in dropped):
                mp = self.metal_points(i); cw = [self.world(m, i, Pc) for m, Pc in self.contact]
                sizes = [len(X) for _, X in self.rigid.values()] + [len(X) for _, X in self.link_pts.values()]
                cut = np.cumsum([0] + sizes)
                dd = B.dist(i, np.concatenate([mp] + cw)); d = dd[:len(mp)]
                j = int(np.argmin(d)); part = names[int(np.searchsorted(cut, j, side="right") - 1)]
                dc = float(dd[len(mp):].min()) if len(dd) > len(mp) else 1e9
                per = {nm: round(float(d[cut[k]:cut[k + 1]].min()), 2) for k, nm in enumerate(names) if cut[k + 1] > cut[k]}
                jams.append(dict(i=i, kind=B.kind[i], **{k: round(B.poses[i][k], 1) for k in ("plane", "elev", "axial")},
                                 pair=pair, clear=round(float(cl), 3), min_metal_mm=round(float(d.min()), 2), deepest_part=part,
                                 contact_only_min_mm=round(dc, 2), inside=bool(min(float(d.min()), dc) < 0), per_part_min=per))
            else:
                n_eval_ok += 1
        box.update(jams=jams, n_valid=len(valid), n_nonjam_valid=n_eval_ok)
        raise _Done()

    base.run = jam_run
    t = time.time()
    try:
        mod.frozen(P)
    except _Done:
        pass
    finally:
        base.run = orig
    J = box.get("jams", [])
    ins = [j for j in J if j["inside"]]
    out = dict(id=rid, params=P, exact=os.environ.get("CB_EXACT") == "1", secs=round(time.time() - t, 1), git=AA._git("rev-parse", "--short", "HEAD"),
               n_valid=box.get("n_valid"), n_jam=len(J), n_jam_inside=len(ins),
               n_jam_inside_by_kind={k: sum(1 for j in ins if j["kind"] == k) for k in ("clip", "ws")},
               jam_inside_sum_mm=round(float(-sum(min(j["min_metal_mm"], j["contact_only_min_mm"]) for j in ins)), 2),
               jam_inside_max_mm=round(float(-min([min(j["min_metal_mm"], j["contact_only_min_mm"]) for j in ins] or [0])), 2),
               jam_inside_deepest_parts={p: sum(1 for j in ins if j["deepest_part"] == p) for p in sorted({j["deepest_part"] for j in ins})},
               jam_inside_overhead140=sum(1 for j in ins if j["kind"] == "ws" and j["elev"] >= 140),
               jams=sorted(J, key=lambda j: j["min_metal_mm"]))
    return out


if __name__ == "__main__":
    rid, path = sys.argv[1], sys.argv[2]
    out = run(rid, sys.argv[3] if len(sys.argv) > 3 else None); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "jams"}, default=float))
