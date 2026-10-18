"""Alignment probe adapter for proxtrack-relay-knuckle-4r (and its verifier's buildable-stack price), read-only.

The model (docs/concepts/models/proxtrack-relay-knuckle-4r.py) has no frozen() / PK.audit, so tools/alignment_audit.py
remeasure and tools/alignment_paired.py dump cannot wrap it. This adapter runs the claim UNCHANGED through the
buildability verifier's own harness (docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability.py: one prepare =
lead fit on Bench(60,160) fast at phi 0, frozen, least-phi relay solve, frozen exact wear; then PT.wear re-records the
relay hardware), for two variants on ONE prepared wear:
  base      the claim as modelled (gate 14.40 / plain 14.02 on file)
  stackfix  the verifier's minimal buildable pin-a stack (the row's v_gap 17.46 / held 21.46)
and records what the score does not see. Nothing is patched except what the verifier itself patches (bump_amounts for
stackfix) and an instance-level wrapper on B.dist that only RECORDS the lowest metal per pose over every distance call of
the re-record (chain, relay underside, carriage / shell tops, contact-only sets), so the clearance floor includes the
contact-only metal the in-band read leaves out.

Outputs (docs/alignment/remeasure/):
  proxtrack-relay-knuckle-4r_<wear>_<variant>_perpose.json   tools/alignment_paired.py format; ns / nib are CHAIN-ONLY
      (the gate's in-band, the row's v_gap reading), ns_all / nib_all pooled; frozen.gap = the gate the row claims,
      frozen.plain = pooled; recomputed = gap_parts(poses) (must equal frozen.gap +-0.05)
  proxtrack-relay-knuckle-4r_<wear>_probe.json               tools/alignment_wear_probe.py analyse() per variant + the
      floor over ALL metal, th margins, workspace chain-only in-band, overhead / raised-arm reach

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_proxtrack.py bench|held [base,stackfix]
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_wear_probe as W      # noqa: E402
import alignment_paired as AP         # noqa: E402

RID = "proxtrack-relay-knuckle-4r"
REM = os.path.join(REPO, "docs", "alignment", "remeasure")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def main(wear, variants):
    BV = _load("bv_proxtrack_probe", os.path.join(REPO, "docs", "concepts", "verify", RID + "-buildability.py"))
    PT, CB = BV.PT, BV.CB
    t0 = time.time()
    S = PT.prepare(BV.CLAIM, -1, -1, exact=True) if wear == "held" else PT.prepare(BV.CLAIM, 110, 360, exact=True)
    prep = round(time.time() - t0, 1)
    M, B = S["M"], S["B"]
    nC = int(sum(len(X) for (_, X) in M.rigid.values()) + sum(len(X) for (_, X) in M.link_pts.values()))
    floor = {}; orig_dist = B.dist

    def rec_dist(i, X):
        d = orig_dist(i, X)
        if len(d): floor[i] = min(floor.get(i, 1e9), float(np.min(d)))
        return d
    B.dist = rec_dist
    probe = dict(id=RID, wear=wear, exact=os.environ.get("CB_EXACT") == "1", prepare_secs=prep, nC=nC, variants={})
    for v in variants:
        PT.bump_amounts, PT.rerecord, PT.relay_points = BV._ORIG["bump_amounts"], BV._ORIG["rerecord"], BV._ORIG["relay_points"]
        if v == "stackfix": PT.bump_amounts = BV.stackfix_amounts
        elif v != "base": raise SystemExit("variant " + v)
        floor.clear(); t1 = time.time()
        o = PT.wear(S, BV.CLAIM)
        PT.bump_amounts = BV._ORIG["bump_amounts"]
        poses = AP._dump_bench(M, B)
        for p in poses:
            i = p["i"]; p["floor_all_mm"] = None if i not in floor or B.res[i] is None else round(floor[i], 3)
            if p["kind"] == "clip" and p["taken"]:
                d = np.asarray(B.res[i], float); dc = d[:nC]
                p["ns_all"], p["nib_all"] = p["ns"], p["nib"]; p["ns"] = int(len(dc)); p["nib"] = int(((dc >= 2) & (dc <= 14)).sum())
        rec = AP.gap_parts(poses)
        kind = np.array(B.kind); el = np.array([q["elev"] for q in B.poses])
        tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
        fl = {j: floor.get(j, float(np.min(B.res[j]))) for j in tk}

        def cnt(sel, t): return int(sum(1 for j in sel if fl[j] < t))
        tw = [j for j in tk if kind[j] == "ws"]; tc = [j for j in tk if kind[j] == "clip"]; toh = [j for j in tw if el[j] >= 140]
        wsd = np.concatenate([np.asarray(B.res[j], float)[:nC] for j in tw]) if tw else np.zeros(0)
        wso = np.concatenate([np.asarray(B.res[j], float)[:nC] for j in toh]) if toh else np.zeros(0)
        ib = lambda a: round(float(((a >= 2) & (a <= 14)).mean()), 4) if len(a) else None
        ws_all = [j for j in range(len(B.idx)) if kind[j] == "ws"]
        extra = dict(
            gate_gap=o["gate_gap"], plain_gap=o["wear"]["gap"], near1_gap=o["near1_gap"], near2_gap=o["near2_gap"], ib14_gate=o["ib14_gate"],
            ib14_chain_only=o["hw"]["ib14_chain_only"], recomputed=rec,
            overhead140=[len(toh), int(sum(1 for j in ws_all if el[j] >= 140))],
            raised90=[int(sum(1 for j in tw if el[j] >= 90)), int(sum(1 for j in ws_all if el[j] >= 90))],
            floor_all=dict(taken=len(tk), lt1=cnt(tk, 1), lt2=cnt(tk, 2), lt3=cnt(tk, 3), clip_lt2=cnt(tc, 2), ws_lt2=cnt(tw, 2), overhead_lt2=cnt(toh, 2),
                           overhead_lt3=cnt(toh, 3), min=round(min(fl.values()), 3) if fl else None,
                           lowest=[dict(i=int(j), kind=str(kind[j]), pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], mm=round(fl[j], 3),
                                        phi=round(float(S["phi_b"][j]), 1)) for j in sorted(fl, key=fl.get)[:8]]),
            ws_taken_chain_ib14=ib(wsd), overhead_taken_chain_ib14=ib(wso), ws_taken_chain_over14=round(float((wsd > 14).mean()), 4) if len(wsd) else None,
            jams=o["hw"]["jams"], contacts=o["contacts"], relayed=o["relayed"], why=o["why"], continuity=o["continuity"] and {k: o["continuity"][k] for k in ("dropped_relayed", "phi0_taken_not_connected")},
            th_margin=BV.th_margin(M, B), secs=round(time.time() - t1, 1))
        an = W.analyse(M, B)
        probe["variants"][v] = dict(probe=an, **extra)
        dump = dict(id=RID, wear=wear, variant=v, params=BV.CLAIM, exact=probe["exact"], nC=nC,
                    frozen=dict(gap=o["gate_gap"], plain=o["wear"]["gap"], near1=o["near1_gap"], reading="gate = chain-only in-band (row v_gap protocol)"),
                    report=B.report() and {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                    poses=poses, recomputed=rec, git=os.popen(f"git -C {REPO} rev-parse --short HEAD").read().strip())
        os.makedirs(REM, exist_ok=True)
        json.dump(dump, open(os.path.join(REM, f"{RID}_{wear}_{v}_perpose.json"), "w"), default=float)
        print(json.dumps(dict(variant=v, gate=o["gate_gap"], plain=o["wear"]["gap"], near1=o["near1_gap"], recomputed=rec, floor=extra["floor_all"],
                              overhead=extra["overhead140"], raised90=extra["raised90"], th=extra["th_margin"]["min"]), default=float), flush=True)
        json.dump(probe, open(os.path.join(REM, f"{RID}_{wear}_probe.json"), "w"), indent=1, default=float)
    B.dist = orig_dist
    return probe


if __name__ == "__main__":
    main(sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "base,stackfix").split(","))
