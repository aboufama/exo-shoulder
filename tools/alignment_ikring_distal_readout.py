#!/usr/bin/env python3
"""Alignment readout for ikring-distalshell-knuckle-4r (read-only, 2026-10-19): what the wearer gets, from the per-pose
dumps on file, next to the verified 3R lead (conecut-knee-knuckle-3r), pick 1 (ikring-thinstack-knuckle-4r, the same ring
machinery with the lead's long knee) and phi40-thinstack-relay-4r (the ring with its coil, MVP1-determinate twin).
It changes no score, no row, no model, no bench.

1. readout per dump: taken clip / ws poses with metal < 1 / 2 / 3 mm (metal = min(min_mm, cmin), the near-touch reading),
   overhead (ws elev >= 140) and raised-arm (ws elev >= 90) reach, contact poses with depth (sum, deepest), and the
   near-touch gaps (a taken pose under N mm counted as contact, tools/alignment_paired.gap_parts). The dumps carry the
   POOLED in-band (chain + shell samples); this design's gate reads chain-only in-band (0.894 on the bench: +0.60 gap
   points over the pooled plain), which a per-pose dump cannot reproduce - noted, never mixed in.
2. strict shell reading: the arm-fixed shell is on the arm at every pose; the verifier found 9 bench ws poses that the
   mechanism reaches (some k in 12.5-40 closes) with the shell in the torso, which the take-only IK records as 'not
   taken' (psi held at 0). Re-read with those 9 as contacts.
3. psi continuity on the claim bench: the commanded psi of grid-adjacent taken ws poses (one of plane / elev / axial
   differs by one 15-deg step), max jump and jumps > 20 deg.
4. copies the verifier's bench dump and the held ws dump on file to docs/alignment/remeasure/<id>_{bench,held}_perpose.json
   (unchanged poses; a provenance note added) so the audit's own dump readers find them.

    python3 tools/alignment_ikring_distal_readout.py <out.json>
"""
import json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP  # noqa: E402

ID = "ikring-distalshell-knuckle-4r"
V = f"docs/concepts/verify/{ID}/"
P1 = "docs/concepts/verify/ikring-thinstack-knuckle-4r/"
REM = "docs/alignment/remeasure/"
DUMPS = [("distal_bench_verifier", V + "verifier/v_bench_perpose.json"), ("distal_bench_claim", V + "ik_bench_fixk_perpose.json"),
         ("distal_bench_importedtable", V + "ik_bench_perpose.json"),
         ("distal_heldws_importedtable", V + "ik_heldws_perpose.json"), ("distal_heldws_ownfix", REM + ID + "_heldfix_perpose.json"),
         ("lead_bench", REM + "conecut-knee-knuckle-3r_bench_perpose.json"), ("lead_held", REM + "conecut-knee-knuckle-3r_held_perpose.json"),
         ("pick1_bench_verifier", P1 + "verifier/v_bench_full_perpose.json"), ("pick1_heldws", P1 + "ik_heldws_specrule_perpose.json"),
         ("phi40_bench", REM + "phi40-thinstack-relay-4r_bench_perpose.json"), ("phi40_held", REM + "phi40-thinstack-relay-4r_held_perpose.json")]
STRICT9 = [354, 417, 431, 441, 454, 457, 459, 464, 466]


def eff(p):
    if p.get("min_mm") is None: return None
    return min(p["min_mm"], p["cmin"] if p.get("cmin") is not None else 9e9)


def readout(f):
    d = json.load(open(os.path.join(REPO, f))); P = d["poses"]
    out = dict(src=f, dump_report_gap=(d.get("recomputed") or d.get("report") or {}).get("gap"), recomputed=AP.gap_parts(P))
    for kind in ("clip", "ws"):
        Q = [p for p in P if p["kind"] == kind]; tk = [p for p in Q if p.get("taken")]
        mm = np.array([eff(p) for p in tk if eff(p) is not None])
        o = dict(n=len(Q), taken=len(tk), under1=int((mm < 1).sum()), under2=int((mm < 2).sum()), under3=int((mm < 3).sum()),
                 median_min_mm=round(float(np.median(mm)), 2) if len(mm) else None, min_mm=round(float(mm.min()), 3) if len(mm) else None)
        if kind == "ws":
            for lab, lo in (("overhead140", 140), ("raised90", 90)):
                QQ = [p for p in Q if p["elev"] >= lo]; TT = [p for p in QQ if p.get("taken")]
                o[lab] = [len(TT), len(QQ)]; o[lab + "_under2"] = sum(1 for p in TT if eff(p) is not None and eff(p) < 2)
        out[kind] = o
    for thr in (1.0, 2.0, 3.0):
        Q = []
        for p in P:
            q = dict(p)
            if p["taken"] and eff(p) is not None and eff(p) < thr: q["taken"] = False; q["contact"] = True
            Q.append(q)
        out[f"gap_near{thr:g}"] = AP.gap_parts(Q)["gap"]
    C = [p for p in P if p.get("contact")]
    out["contacts"] = sorted([dict(i=p["i"], kind=p["kind"], pose=[round(p["plane"], 1), round(p["elev"], 1), round(p["axial"], 1)], mm=p["min_mm"]) for p in C],
                             key=lambda x: x["mm"])
    dd = [-p["min_mm"] for p in C]
    out.update(contact_n=len(C), contact_sum_mm=round(sum(dd), 2), contact_max_mm=round(max(dd), 2) if dd else 0.0,
               contact_overhead140=sum(1 for p in C if p["elev"] >= 140))
    return out, P


def strict_shell(P):
    Q = []
    for p in P:
        q = dict(p)
        if p["kind"] == "ws" and p["i"] in STRICT9: q["taken"] = False; q["contact"] = True
        Q.append(q)
    return dict(poses=STRICT9, plain_strict=AP.gap_parts(Q)["gap"], plain=AP.gap_parts(P)["gap"],
                note="pooled-in-band plain; the chain-only gate adds +0.60 on the bench (0.894 vs 0.90)")


def psi_jumps():
    ch = json.load(open(os.path.join(REPO, V + "ik_bench_fixk_choice.json")))["ik"]["choice"]
    P = json.load(open(os.path.join(REPO, V + "verifier/v_bench_perpose.json")))["poses"]
    ws = {p["i"]: p for p in P if p["kind"] == "ws" and p["taken"]}
    psi = {i: float(ch[str(i)]["k"]) if str(i) in ch else 0.0 for i in ws}
    key = {(round(p["plane"]), round(p["elev"]), round(p["axial"])): i for i, p in ws.items()}
    jumps = []
    for (pl, el, ax), i in key.items():
        for d in ((15, 0, 0), (0, 15, 0), (0, 0, 15)):
            j = key.get((pl + d[0], el + d[1], ax + d[2]))
            if j is not None: jumps.append((abs(psi[i] - psi[j]), i, j))
    jumps.sort(reverse=True)
    return dict(pairs=len(jumps), over20=sum(1 for x in jumps if x[0] > 20), over10=sum(1 for x in jumps if x[0] > 10),
                max=jumps[0][0] if jumps else None, top=[list(x) for x in jumps[:6]],
                psi_nonzero_taken=sum(1 for i in ws if psi[i] != 0))


def copy_dumps():
    for src, wear in ((V + "verifier/v_bench_perpose.json", "bench"), (V + "ik_heldws_perpose.json", "held")):
        d = json.load(open(os.path.join(REPO, src)))
        d["audit_copy"] = dict(src=src, wear=wear, note=("verifier per-pose dump of the verified config, copied unchanged (plain 9.94 pooled in-band; "
                                                         "the row's v_gap 10.54 is the chain-only gate)") if wear == "bench" else
                               ("held ws sample (every held ws pose + every 100th held clip frame) worn with pick 1's held IK table, copied unchanged "
                                "(gate 15.62; the table was chosen for pick 1's metal: see _heldfix for this design's own k-table)"))
        json.dump(d, open(os.path.join(REPO, REM + f"{ID}_{wear}_perpose.json"), "w"), default=float)


def main(outp):
    copy_dumps()
    res = dict(id=ID, rule="near-touch: a taken pose with min(min_mm, cmin) < N mm counted as contact (report only)", dumps={})
    PP = {}
    for lab, f in DUMPS:
        if not os.path.exists(os.path.join(REPO, f)): res["dumps"][lab] = dict(src=f, missing=True); continue
        r, P = readout(f); r.pop("contacts") if len(r["contacts"]) > 40 else None; res["dumps"][lab] = r; PP[lab] = P
    res["strict_shell_bench"] = strict_shell(PP["distal_bench_verifier"])
    res["psi_jumps_bench"] = psi_jumps()
    k0 = json.load(open(os.path.join(REPO, V + "k0_parked.json"))); ch = json.load(open(os.path.join(REPO, V + "chain_psi0.json")))
    res["parked_psi0"] = dict(k0_parked={k: k0.get(k) for k in ("gate_gap", "chain_only_gap", "near2_gap", "wear", "ws_taken", "overhead") if k in k0},
                              chain_psi0={k: ch.get(k) for k in ("gate_gap", "chain_only_gap", "near2_gap", "wear", "ws_taken", "overhead") if k in ch})
    json.dump(res, open(outp, "w"), indent=1, default=float)
    for lab, r in res["dumps"].items():
        if r.get("missing"): print(lab, "MISSING", r["src"]); continue
        print(lab, "gap", r["recomputed"]["gap"], "(dump", r["dump_report_gap"], ") n1", r["gap_near1"], "n2", r["gap_near2"], "n3", r["gap_near3"],
              "| ws", r["ws"]["taken"], "/", r["ws"]["n"], "oh140", r["ws"]["overhead140"], "r90", r["ws"]["raised90"],
              "| ws<1/2/3", r["ws"]["under1"], r["ws"]["under2"], r["ws"]["under3"], "clip<1/2", r["clip"]["under1"], r["clip"]["under2"], "/", r["clip"]["taken"],
              "| contacts", r["contact_n"], "sum", r["contact_sum_mm"], "max", r["contact_max_mm"], "oh", r["contact_overhead140"])
    print("strict", res["strict_shell_bench"]); print("psi", res["psi_jumps_bench"]); print("parked", json.dumps(res["parked_psi0"])[:600])


if __name__ == "__main__":
    main(sys.argv[1])
