"""Builds docs/blueprints/index.html: the blueprints of the best verified design (A, offset-shortcar-relay-4r on the
3-joint lead's chain user_conecut_knee) and the simplest high scorer (B, skin-normal-3r-pin-knee H1, built as
user_pinknee_h1b), every part of both built CADs on white (tools/part_cards.py), and the white three-pose snapshot of
every built design (pipeline/evolution/*/snapshot.png). Numbers come from the rows, the CAD files and the verifiers'
reports (sources listed on the page). Also writes docs/blueprints/files.json, the supporting-file map for publishing.

    python3 docs/blueprints/build_blueprints.py
"""
import html, json, math, os, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(REPO, "docs", "blueprints")
E = html.escape


def J(p):
    return json.load(open(os.path.join(REPO, p)))


def git_time(path):
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cI", "--", path], cwd=REPO, capture_output=True, text=True).stdout.split()
    return out[-1][:16].replace("T", " ") if out else ""


AS_OF = subprocess.run(["date", "-u", "+%Y-%m-%d %H:%M UTC"], capture_output=True, text=True).stdout.strip()
MORPHS = {r["id"]: r for r in J("docs/dashboard/data/morphs.json")}

# ---------------------------------------------------------------- part titles (the CAD names are build notes, not titles)
YOURS = " (your part)"
TITLES = {
    "user_conecut_knee": [
        "MR117-2RS ball bearing 7 x 11 x 3 (2 per hub: J1, K, J2, J3)", "Hub outer spacer, 17-4PH", "Hub inner spacer, ground (sets the preload)",
        "Hub ring nut M7 x 0.5", "Hub dome cap O20 (J1, J3)", "K hub cap with the clock-spring chamber", "K clock spring (holds K on its stop)",
        "J2 cap O20 (seat of the lobe ring)", "D8-02a link 1a (J1 to K, carries the flank lug)", "D8-02b link 1b (K to J2, carries the crank pin)",
        "K stop dowel O3 (pair)", "J2 stop dowel O3", "D8-03 link 2 (J2 to J3)", "D9-02 drive lobe ring (cam on hub 2)", "D9-01 drive bell crank",
        "683ZZ bearing 3 x 7 x 3 (crank pivot pair)", "MR63ZZ bearing 3 x 6 x 2.5 (4 in the knee, 1 cam follower)", "Follower inner-ring shim O4.5 x 0.2",
        "Follower pin O3 x 10, 17-4PH", "Nose dowel O2.5 x 6, 440C with DLC (rides the flank)", "Crank pivot pin O3, 17-4PH", "Crank pivot e-clip DIN 6799 RS 2.3",
        "Crank inner-ring spacer O4.5 x 0.175", "Shim O4.5 x 0.1 (crank preload, knee pins)", "Crank preload wave washer O6",
        "D8-04 member 3 (J3 disc + E strap to pin a)", "Knee pin O3 x 9.7, 440C (pins a and b)", "Knee pin spacer O4.5 x 0.5", "Knee pin e-clip DIN 6799 RS 2.3",
        "D8-05 knee link (with the knee stop tooth)", "J3 stop dowel O2 x 3.9, 440C", "D8-06 BOTTOM + arm pad + pad mount (one part)", "D8-01 scapula base at the J1 ring",
        "M4 x 6 ultra-low socket screw" + YOURS, "Forearm cuff" + YOURS, "M4 x 8 countersunk screw" + YOURS, "TOP" + YOURS,
        "igus iglide J thrust washer 30 x 39 x 1.5" + YOURS, "MIDDLE" + YOURS, "N42 magnet O5 x 2.5" + YOURS, "Ball O2.3 (x18, cuff bearing)" + YOURS,
        "Thin ring O24.9 x 0.38" + YOURS, "Ring O26.9 x 4" + YOURS, "Ring O21.8 x 4" + YOURS, "Upper-arm cuff plate, AlSi10Mg",
        "M4 x 6 countersunk screw ISO 10642 (upper cuff to BOTTOM)"],
    "user_pinknee_h1b": [
        "MR117-2RS ball bearing 7 x 11 x 3 (2 per hub: J1, J2, J3)", "Hub outer spacer, 17-4PH", "Hub inner spacer, ground (sets the preload)", "Hub ring nut M7 x 0.5",
        "J1 dome cap O20", "J2 dome cap O20", "J3 dome cap O20", "D8-02 link 1 (J1 to J2)", "D8-03 link 2 (J2 to J3, flies over the knee)",
        "D8-04 member 3 (J3 disc + E strap to pin a)", "iglidur thrust washer 4 x 8 x 0.5 (knee pins)", "iglidur G sleeve 4 x 5.5 x 1.89 (knee pins)",
        "Knee pin E-clip DIN 6799-3.2", "D8-05 knee link", "D8-06 BOTTOM + arm pad + pad mount (one part, pin b integral)", "D8-01 scapula base at the J1 ring",
        "M4 x 6 ultra-low socket screw" + YOURS, "Forearm cuff" + YOURS, "M4 x 8 countersunk screw" + YOURS, "TOP" + YOURS,
        "igus iglide J thrust washer 30 x 39 x 1.5" + YOURS, "MIDDLE" + YOURS, "N42 magnet O5 x 2.5" + YOURS, "Ball O2.3 (x18, cuff bearing)" + YOURS,
        "Thin ring O24.9 x 0.38" + YOURS, "Ring O26.9 x 4" + YOURS, "Ring O21.8 x 4" + YOURS, "Upper-arm cuff plate, AlSi10Mg",
        "M4 x 6 countersunk screw ISO 10642 (upper cuff to BOTTOM)"],
}


def parts(design):
    P = J(f"docs/blueprints/parts/{design}/parts.json")["parts"]
    T = TITLES[design]
    assert len(T) == len(P), (design, len(T), len(P))
    out = []
    for p, t in zip(P, T):
        out.append({"img": f"parts/{design}/{p['file']}" if p["file"] else None, "t": t.replace(" O", " Ø") if " O" in t else t,
                    "q": p["qty"], "m": p["material"] if p["material"] != "user part" else "", "g": p["mass_g"],
                    "s": p["size_mm"], "b": p["bodies"], "u": p["user_part"], "d": p["descs"]})
    return out


# ---------------------------------------------------------------- iteration gallery (every built design)
EV = [
    ("l1_seed-offset-3r-slides", "Seed: offset 3R with crossed cuff slides", "seed-offset-3r-slides"),
    ("param2_r20_n3_s1414_4", "Parametric 3R sweep (r20, n3)", None),
    ("l1_3r-k2221", "Offset 3R, config k2221", None),
    ("l1_rail-elbow", "Rail elbow", "rail-elbow"),
    ("l1_offset-skin-normal-3r", "Offset skin-normal 3R", "offset-skin-normal-3r"),
    ("user_osn_k4216", "Offset skin-normal 3R (config k4216)", "offset-skin-normal-3r"),
    ("l1_skin-normal-3r-pin-knee", "Pin knee, config k4598 (10° fold margin)", "skin-normal-3r-pin-knee"),
    ("l1_skin-normal-3r-pin-knee-h1", "Pin knee, polished config H1", "skin-normal-3r-pin-knee"),
    ("l1_skin-normal-3r-pin-knee-k4598-m5", "Pin knee, config k4598 (5° fold margin)", "skin-normal-3r-pin-knee"),
    ("user_pinknee_h1", "Pin knee H1, bent bars", "skin-normal-3r-pin-knee"),
    ("user_pinknee_h1b", "Pin knee H1b, machined bars (design B)", "skin-normal-3r-pin-knee"),
    ("l1_minarc-bdp", "Min-arc stop knuckle, 4 joints (config bdp)", "minarc-stop-knuckle-4r"),
    ("user_minarc_bdp", "Min-arc stop knuckle, 4 joints (config bdp)", "minarc-stop-knuckle-4r"),
    ("l1_minarc-pick1", "Min-arc stop knuckle, 4 joints (pick 1)", "minarc-stop-knuckle-4r"),
    ("l1_geneva-rod", "Geneva knuckle with pushrod", "geneva-tail-knuckle-pinknee-3r"),
    ("user_minarc_pick1", "Min-arc stop knuckle, 4 joints (pick 1)", "minarc-stop-knuckle-4r"),
    ("user_geneva_rod", "Geneva knuckle with pushrod", "geneva-tail-knuckle-pinknee-3r"),
    ("user_geneva_rod_v2", "Geneva knuckle with pushrod, v2", "geneva-tail-knuckle-pinknee-3r"),
    ("l1_roller-longdyad", "Roller long-dyad knuckle", "roller-longdyad-knuckle-3r"),
    ("user_roller_longdyad", "Roller long-dyad knuckle", "roller-longdyad-knuckle-3r"),
    ("l1_slipper-nose", "Slipper-nose knuckle (lead until 10-17)", "slipper-nose-knuckle-3r"),
    ("user_slipper_nose", "Slipper-nose knuckle (lead until 10-17)", "slipper-nose-knuckle-3r"),
    ("user_trimlug_k165", "Trim-lug knuckle (config k165)", "trimlug-k165-knuckle-3r"),
    ("l1_conecut-knee", "Cone-cut pin knee: the 3-joint lead (A's chain)", "conecut-knee-knuckle-3r"),
    ("user_conecut_knee", "Cone-cut pin knee: the 3-joint lead (A's chain)", "conecut-knee-knuckle-3r"),
    ("l1_desmo-conecut", "Desmo cone-cut knuckle (drive flagged unbuildable)", "desmo-conecut-knuckle-3r"),
    ("user_desmo_conecut", "Desmo cone-cut knuckle (drive flagged unbuildable)", "desmo-conecut-knuckle-3r"),
]


def gallery():
    rows = []
    for ev, name, rid in EV:
        snap = f"pipeline/evolution/{ev}/snapshot.png"
        if not os.path.exists(os.path.join(REPO, snap)):
            continue
        scp = os.path.join(REPO, "pipeline", "evolution", ev, "scorecard.json")
        sc = {r["id"]: r for r in json.load(open(scp))} if os.path.exists(scp) else {}
        v = lambda k: sc[k]["value"] if k in sc and isinstance(sc[k]["value"], (int, float)) else None
        r = MORPHS.get(rid) if rid else None
        note = ""
        if r:
            if r.get("alignment") == "gamed":
                note = "audit: gamed"
            elif r.get("status") in ("refuted", "dead"):
                note = r["status"]
        rows.append({"img": f"evolution/{ev}.png", "src": snap, "name": name, "id": ev, "full": ev.startswith("user_"),
                     "t": git_time(snap), "r1": v("R1"), "aim": v("R1-aim"), "r4": v("R4"),
                     "pass": sum(1 for x in sc.values() if x.get("status") == "PASS"), "n": len(sc),
                     "vgap": r.get("v_gap") if r else None, "dof": r.get("active_dof") if r else None, "note": note})
    rows.sort(key=lambda x: x["t"])
    return rows


# ---------------------------------------------------------------- drawings
def chain_svg(relay):
    """topology: bodies (rectangles) and joints (circles) from the scapula handler to the arm"""
    seq = [("b", "Scapula handler", "yours, not counted"), ("j", "J1", "hub · encoder"), ("b", "Link 1a", "Ti 8×3 bar"),
           ("k", "K", "slaved knuckle"), ("b", "Link 1b", "Ti 8×3 bar"), ("j", "J2", "hub · encoder"), ("b", "Link 2", "Ti 8×3 bar"),
           ("j", "J3", "hub · encoder · stop"), ("b", "Member 3", "J3 disc + E strap"), ("p", "pin a", "MR63ZZ pair"),
           ("b", "Knee link", "Ti plate"), ("p", "pin b", "MR63ZZ pair"), ("b", "Arm pad", "+ BOTTOM")] if relay is not None else \
          [("b", "Scapula handler", "yours, not counted"), ("j", "J1", "hub · encoder"), ("b", "Link 1", "Ti 8×3 bar"),
           ("j", "J2", "hub · encoder"), ("b", "Link 2", "Ti 8×3 bar"), ("j", "J3", "hub · encoder"), ("b", "Member 3", "J3 disc + E strap"),
           ("p", "pin a", "iglidur sleeve"), ("b", "Knee link", "Ti plate"), ("p", "pin b", "iglidur sleeve"), ("b", "Arm pad", "= BOTTOM, one part")]
    if relay:
        seq += [("b", "Bracket", "Ti 2×10"), ("r", "Relay", "4th joint · coil + stops"), ("b", "Shell", "strapped to the arm")]
    W = {"b": 104, "j": 54, "k": 54, "p": 50, "r": 58}
    gap = 14
    total = sum(W[s[0]] for s in seq) + gap * (len(seq) - 1) + 20
    h = 150
    x = 10
    out = [f'<svg viewBox="0 0 {total} {h}" width="{total}" height="{h}" role="img" aria-label="Joint chain diagram">']
    y = 58
    for i, (kind, name, sub) in enumerate(seq):
        w = W[kind]
        if i:
            out.append(f'<line x1="{x - gap}" y1="{y}" x2="{x}" y2="{y}" class="ln"/>')
        if kind == "b":
            out.append(f'<rect x="{x}" y="{y - 20}" width="{w}" height="40" rx="5" class="bd"/>'
                       f'<text x="{x + w / 2}" y="{y + 4}" class="tbx">{E(name)}</text>'
                       f'<text x="{x + w / 2}" y="{y + 38}" class="ts">{E(sub)}</text>')
        else:
            cls = {"j": "jh", "k": "jk", "p": "jp", "r": "jr"}[kind]
            out.append(f'<circle cx="{x + w / 2}" cy="{y}" r="{w / 2 - 4}" class="{cls}"/>'
                       f'<text x="{x + w / 2}" y="{y + 4}" class="tj {cls}t">{E(name)}</text>'
                       f'<text x="{x + w / 2}" y="{y + 44 if kind != "r" else y + 46}" class="ts">{E(sub)}</text>')
        x += w + gap
    lx = 10
    leg = [("jh", "counted joint (encoded hub)"), ("jk", "slaved, not counted")] if relay is not None else [("jh", "counted joint (encoded hub)")]
    leg += [("jp", "knee pin (cuff alignment, not counted)")]
    if relay:
        leg.append(("jr", "relay: counted 4th joint"))
    for cls, txt in leg:
        out.append(f'<circle cx="{lx + 7}" cy="{h - 12}" r="6" class="{cls}"/><text x="{lx + 18}" y="{h - 8}" class="tl">{E(txt)}</text>')
        lx += 22 + len(txt) * 6.2
    out.append("</svg>")
    return "".join(out)


def clearance_svg(items, lo=2.0, aim=10.0, hi=14.0):
    """median metal-to-skin distance per part, mm, with the 2-10 aim and the 2-14 pass bands"""
    W, rowh, left, right = 640, 22, 150, 40
    H = rowh * len(items) + 50
    sx = lambda mm: left + (W - left - right) * mm / 16.0
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Median distance from the skin per part">']
    o.append(f'<rect x="{sx(lo)}" y="8" width="{sx(hi) - sx(lo)}" height="{rowh * len(items) + 4}" class="band14"/>')
    o.append(f'<rect x="{sx(lo)}" y="8" width="{sx(aim) - sx(lo)}" height="{rowh * len(items) + 4}" class="band10"/>')
    for t in range(0, 17, 2):
        o.append(f'<line x1="{sx(t)}" y1="8" x2="{sx(t)}" y2="{rowh * len(items) + 12}" class="grid"/>'
                 f'<text x="{sx(t)}" y="{rowh * len(items) + 28}" class="tax">{t}</text>')
    o.append(f'<text x="{sx(8)}" y="{rowh * len(items) + 44}" class="tax">median distance from the skin, mm (shaded: 2–10 aim, 2–14 pass)</text>')
    for i, (name, mm) in enumerate(items):
        y = 12 + i * rowh
        o.append(f'<text x="{left - 8}" y="{y + 13}" class="tlab">{E(name)}</text>'
                 f'<rect x="{sx(0)}" y="{y + 3}" width="{sx(mm) - sx(0)}" height="{rowh - 8}" rx="2" class="bar"/>'
                 f'<text x="{sx(mm) + 5}" y="{y + 13}" class="tval">{mm:.1f}</text>')
    o.append("</svg>")
    return "".join(o)


def relay_svg():
    """to-scale section of the relay seen along its axis a_r, with numbered balloons (legend in RELAY_LEGEND); numbers:
    offset-shortcar-relay-4r verifier (claim.json relay_hw / offset_hw)"""
    Rt, Ru, Rskin, Rpad, hc = 80.6, 79.1, 73.6, 73.18, 1.7
    a0, a1, delta, PHI, coil_az = -1.9, 45.9, 4.5, 35.0, -5.46
    S, ROT = 6.0, 19.0                          # px per mm; the drawing is turned so the arc's middle is at the top
    cx, cy = 310, 600
    P = lambda r, deg: (cx + r * S * math.sin(math.radians(deg - ROT)), cy - r * S * math.cos(math.radians(deg - ROT)))
    def arc(r, d0, d1, cls, n=60):
        return f'<polyline points="{" ".join(f"{P(r, d0 + (d1 - d0) * i / n)[0]:.1f},{P(r, d0 + (d1 - d0) * i / n)[1]:.1f}" for i in range(n + 1))}" class="{cls}"/>'
    def band(r0, r1, d0, d1, cls, n=40):
        pts = [P(r1, d0 + (d1 - d0) * i / n) for i in range(n + 1)] + [P(r0, d1 - (d1 - d0) * i / n) for i in range(n + 1)]
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" class="{cls}"/>'
    o = ['<svg viewBox="0 0 620 262" width="100%" role="img" aria-label="Relay section along its axis, to scale">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z" class="ahd"/></marker></defs>']
    o.append(arc(Rskin, -15, 53, "skin"))
    o.append(band(Ru, Rt, a0, a1, "shell"))
    cw = 14.0 / Rt * 180 / math.pi              # carriage width in degrees
    o.append(band(Rt, Rt + hc, delta - cw / 2, delta + cw / 2, "carr"))
    o.append(band(Rt, Rt + hc, delta + PHI - cw / 2, delta + PHI + cw / 2, "carrghost"))
    x, y = P(85.6, coil_az)
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4 * S:.1f}" class="coil"/>')
    xp, yp = P(Rpad, 0)
    o.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="4" class="pad"/>')
    pts = " ".join(f"{P(Rt + 9, delta + PHI * i / 40)[0]:.1f},{P(Rt + 9, delta + PHI * i / 40)[1]:.1f}" for i in range(41))
    o.append(f'<polyline points="{pts}" class="trav" marker-end="url(#ah)"/>')
    balloons = [(P(Rt + hc + 5.5, delta - 1), 1), (P(Rt + 13.5, delta + PHI / 2), 2), (P(Ru - 5.5, 41), 3), (P(Rskin - 5.5, 22), 4),
                (P(85.6 + 8.5, coil_az - 3), 5), (P(Rpad - 6.5, -1), 6)]
    for (bx, by), n in balloons:
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="9" class="bal"/><text x="{bx:.1f}" y="{by + 4:.1f}" class="baln">{n}</text>')
    o.append(f'<line x1="20" y1="248" x2="{20 + 10 * S}" y2="248" class="sbar"/><text x="{26 + 10 * S}" y="252" class="tax2">10 mm</text>')
    o.append("</svg>")
    return "".join(o)


RELAY_LEGEND = ["Carriage 14 × 14 mm, 1.7 mm over the shell, at rest 4.5° anterior of the pad",
                "Travel 0–35°, stop dowels at both ends (dashed outline: the carriage at full travel)",
                "Ti shell, radius 80.6 / 79.1 mm, 12 mm wide, arc −1.9° to +45.9°",
                "Skin envelope (p90, max radius 73.6 mm) under the 4 mm liner",
                "Constant-force return coil Ø8 × 8 mm, arm-fixed beyond the zero end",
                "Arm pad (radius 73.18 mm), joined to the carriage by the 2 × 10 mm bracket"]


def pareto_svg(pts):
    """score vs complexity for the verified designs named on the page"""
    W, H, l, r, t, b = 640, 300, 52, 20, 16, 44
    sx = lambda c: l + (W - l - r) * c / 56.0
    sy = lambda s: t + (H - t - b) * (96 - s) / 8.0
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Score against complexity">']
    for s in range(88, 97, 2):
        o.append(f'<line x1="{l}" y1="{sy(s)}" x2="{W - r}" y2="{sy(s)}" class="grid"/><text x="{l - 8}" y="{sy(s) + 4}" class="taxr">{s}</text>')
    o.append(f'<line x1="{l}" y1="{sy(95)}" x2="{W - r}" y2="{sy(95)}" class="goal"/><text x="{W - r}" y="{sy(95) - 5}" class="taxg">target 95</text>')
    for c in range(0, 57, 8):
        o.append(f'<text x="{sx(c)}" y="{H - b + 18}" class="tax">{c}</text>')
    o.append(f'<text x="{(l + W - r) / 2}" y="{H - 6}" class="tax">complexity (0 = three pinned hubs and three links; lower is simpler)</text>')
    o.append(f'<text x="14" y="{(t + H - b) / 2}" class="tax" transform="rotate(-90 14 {(t + H - b) / 2})">verified score</text>')
    for name, cx_, sc, cls, dx, dy, anc in pts:
        o.append(f'<circle cx="{sx(cx_):.1f}" cy="{sy(sc):.1f}" r="6" class="{cls}"/>'
                 f'<text x="{sx(cx_) + dx:.1f}" y="{sy(sc) + dy:.1f}" class="tpt" text-anchor="{anc}">{E(name)}</text>')
    o.append("</svg>")
    return "".join(o)


def score(gap):
    return round(100 * (1 - gap / 275), 2)


# ---------------------------------------------------------------- page
def table(head, rows, cls="spec"):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def main():
    A_parts, B_parts, G = parts("user_conecut_knee"), parts("user_pinknee_h1b"), gallery()
    exo_mass = lambda P: round(sum((p["g"] or 0) * p["q"] for p in P if not p["u"]), 1)
    renders = ["hero_overhead_chain", "hero_shelf_chain", "rest_back_chain", "parts_knee_macro", "parts_shoulder_top", "parts_knee_lateral"]
    files = {}
    for P, d in ((A_parts, "user_conecut_knee"), (B_parts, "user_pinknee_h1b")):
        for p in P:
            if p["img"]:
                files[p["img"]] = os.path.join("docs", "blueprints", p["img"])
    for g in G:
        files[g["img"]] = g["src"]
    for r in renders:
        files[f"renders/{r}.jpg"] = f"renders/2026-10-16_userstyle_pinknee_h1/{r}.jpg"

    summary = table(
        ["", "3-joint lead<br><span class=sub>A's chain alone</span>", "A · best verified<br><span class=sub>lead chain + relay</span>", "B · simplest<br><span class=sub>pin knee H1</span>"],
        [["Design id", "<code>conecut-knee-knuckle-3r</code>", "<code>offset-shortcar-relay-4r</code>", "<code>skin-normal-3r-pin-knee</code> (H1)"],
         ["Joints counted", "3", "<b>4</b> (not eligible for the 3-joint lead)", "3"],
         ["Verified score", f"{score(18.28)} <span class=sub>gap 18.28</span>", f"<b>{score(14.76)}</b> <span class=sub>gap 14.76</span>", f"{score(27.20)} <span class=sub>gap 27.20</span>"],
         ["Held-out gap <span class=sub>(poses never used in design)</span>", "22.38", "<b>17.77</b>", "29.12"],
         ["Reach <span class=sub>(arm poses followed)</span>", "72.8 %", "79.4 %", "65.8 %"],
         ["Overhead poses followed", "8 of 28", "8 of 28", "5 of 28"],
         ["Poses with metal in the skin", "4 of 360 (deepest 8.9 mm)", "13 of 360 (deepest 9.8 mm)", "9 of 360 (deepest 4.1 mm)"],
         ["Complexity", "18.5", "52.5", "<b>0</b>"],
         ["Full CAD", f"built (gen 8), {exo_mass(A_parts)} g", "relay not built yet", f"built (h1b), {exo_mass(B_parts)} g"],
         ["Audit status", "watch", "watch", "watch"]], "spec cmp")

    A_joints = table(["Joint", "Bearing", "Hub", "Range / stop", "Connects"], [
        ["J1", "MR117-2RS pair 7×11×3", "Ø20 × 12.25, face 50.47 mm from GH", "no stop (frames −127.6…149.2°)", "base D8-01 ↔ link 1a"],
        ["K <span class=sub>slaved</span>", "MR117-2RS pair, no encoder", "Ø20, crown +18.25 (clock-spring cap), face 55.12", "stop A 0° / stop B −62.85° (opposed Ø3 dowels); cam limit 50°", "link 1a ↔ link 1b"],
        ["J2", "MR117-2RS pair 7×11×3", "Ø20 × 12.25, face 62.52", "−15.94…102.07° (one Ø3 dowel in a 118° slot); cam onset 7.28°", "link 1b ↔ link 2"],
        ["J3", "MR117-2RS pair 7×11×3", "Ø20 × 12.25, face 78.17; axis 13.84 mm off GH", "−111.90…122.74° on J3's own angle (Ø2 dowel in a 250° groove)", "link 2 ↔ member 3"],
        ["pin a", "2 × MR63ZZ 3×6×2.5", "Ø9 × 5.5 boss, pin stack 9.75", "knee window 25.22…154.78° (tooth stop); used 59.3…106°", "member 3 ↔ knee link"],
        ["pin b", "2 × MR63ZZ 3×6×2.5", "Ø9 × 5.5 boss", "same loop as pin a", "knee link ↔ arm pad"],
        ["Relay <span class=sub>A only</span>", "carriage on 0.2 mm iglidur strip", "14 × 14 carriage, 1.7 mm over the shell", "0…35° (dowels at both ends), rest +4.5°", "arm pad bracket ↔ shell on the arm"]])

    A_geom = table(["Item", "Value", "Notes"], [
        ["Link arcs (spherical)", "J1–J2 37.55°, J2–J3 57.22°", "with K on stop A; J1–K 26.0°, K–J2 38.03°"],
        ["Hub levels from GH", "J1 50.47 · K 55.12 · J2 62.52 · J3 78.17 mm", "skin-side face of each hub; crown = face + 12.25 (K + 18.25)"],
        ["Knee", "lE 97.14 · lc 24.35 · φE 0.75° · φb −91.80°", "knee link 36.35 × 10 × 2.75 Ti; knee plane 86.97 mm from GH"],
        ["J3 stop groove", "r 7.5, 2.10 × 1.00, 250° arc, 108.6° web left", "dowel Ø2 m6 ground to 3.90, 0.85 mm into the groove; tolerance RSS 0.11°"],
        ["Bars", "8 × 3 Ti-6Al-4V (crank arm 6 × 3)", "link 2 climbs 68° near a hub (limit 70° on parts machined from solid)"],
        ["Cam drive", "gear ratio g 2.39, K law kK 2.15", "lobe ring (17-4PH, wire-EDM) → MR63ZZ follower → bell crank on 2 × 683ZZ → Ø2.5 DLC nose on the flank"],
        ["Seat", "J1 on the acromion top", "the scapula handler's bracket threads onto the J1 M18 × 0.5 spigot in place of the dome cap (no tab)"]])

    A_clear = clearance_svg([("Hub J1", 8.6), ("Hub K", 7.9), ("Hub J2", 11.6), ("Hub J3", 11.5), ("Link 1a", 10.1), ("Link 1b", 8.2),
                             ("Link 2", 12.0), ("E strap", 6.0), ("E boss", 7.5), ("Knee link", 9.7), ("Arm pad", 6.2), ("Bell crank", 11.3), ("Crank horn", 7.5)])

    relay_dims = table(["Item", "Value", "Meaning"], [
        ["Station", "31 mm proximal of the arm pad", "shell centre at s −80 mm along the relay axis (pad at −111)"],
        ["Relay axis", "through GH, tilted 12° from the upper-arm axis toward az 235°", "every chain axis still passes through GH when the relay turns"],
        ["Shell", "R 80.6 (top) / 79.1 (underside), 1.5 × 12 mm, arc 47.8° = 67.2 mm", "slotted Ti track strapped over a 4 mm liner; 6.4° pre-arc at each end"],
        ["Carriage", "14 × 14 mm T-nut, 1.5 mm Ti plate on 0.2 mm iglidur", "rides 1.7 mm over the shell; rests 4.5° anterior of the pad"],
        ["Bracket", "Ti 2 × 10, 25° climb, 6.46 mm planform turn", "carriage distal edge (r 82.3) down to the pad's proximal edge (r 73.18)"],
        ["Return coil", "constant force, Ø8 × 8, ≥ 0.79 N", "arm-fixed beyond the zero end; holds the carriage on its zero dowel"],
        ["Travel", "0–35° (32.94° used on the bench)", "own-angle dowels in the shell slot at both ends"],
        ["Rigid bump", "1.0 mm over the shell / carriage, half-band 9.3 mm, max lift 7.39 mm", "E strap, pin-a boss and knee link raised to fly over the track"]])

    relay_parts = table(["Part", "Spec", "Material", "Bought / made"], [
        ["Shell / track", "R 80.6, 1.5 t × 12 w, 47.8° arc, slotted", "Ti", "made"],
        ["T-nut carriage plate", "14 × 14, 1.5 plate", "Ti", "made"],
        ["T-nut retaining flange", "1 mm key under the shell", "Ti", "made"],
        ["Pad bracket", "2 × 10 bent bar", "Ti", "made"],
        ["Constant-force coil", "Ø8 × 8, ≥ 0.79 N (estimate: 0.05 mm 301 strip)", "stainless", "bought (part number to confirm)"],
        ["Stop dowels × 2", "ISO 8734 Ø2 m6", "hardened steel", "bought"],
        ["Running strip", "0.2 mm", "iglidur", "bought"]])

    A_perf = table(["Bench", "Gap (score)", "Reach", "Follow", "In-band 2–14", "In-band 2–10", "Contact", "Overhead"], [
        ["A · bench", "14.76 (94.63)", "0.794", "1.00", "0.890", "0.561", "0.032 (13)", "8/28"],
        ["A · held-out", "17.77 (93.54)", "0.777", "1.00", "0.889", "–", "43 poses", "19/71"],
        ["Lead · bench", "18.28 (93.35)", "0.728", "1.00", "0.901", "0.574", "0.011 (4)", "8/28"],
        ["Lead · held-out", "22.38 (91.86)", "0.692", "1.00", "0.900", "0.573", "0.016 (14)", "18/71"]])

    A_cad = table(["Judge (built CAD of the lead's chain)", "Result", "Target"], [
        ["R1 skin 2–14 mm from the metal", "81.6 % (L1: 81.95)", "≥ 90 %"], ["R1-aim 2–10 mm", "52.7 %", "≥ 90 %"],
        ["R3 follows the arm", "100 % ✓", "≥ 95 %"], ["R4 overhead clip", "74.1 %", "≥ 80 %"],
        ["R6 parts never collide", "0.0 mm over 451 frames ✓", "0"], ["R7 every part one valid solid", "55 of 55 ✓", "all"],
        ["R8 mass", "216.1 g ✓", "≤ 500 g"], ["R11 pad pressure", "0.253 kPa ✓", "low"],
        ["R16 workspace poses closed", "66.7 %", "–"], ["R17 dynamics (cuff twist, GH moment)", "3.99°, 0.126 N·m ✓", "pass"]])

    A_cav = [
        "<b>4 joints.</b> The relay is a counted joint (complexity 52.5 vs 18.5). Under your 2026-10-17 rule it is an option, never the lead.",
        "<b>95 missed by 1.01 gap points.</b> The gap is reach 10.56 + contact 3.18 + in-band 1.02.",
        "<b>Contacts are deeper.</b> There are 13 bench contacts summing 46.2 mm, against the lead's 20.2 mm (×2.28); held-out the ratio is ×2.84. Every new contact is a pose the lead loses to the fold.",
        "<b>Tolerance cliff.</b> Resting the carriage at 5.0° instead of 4.5° reads 27.53 (37 jams). The E strap clears the carriage by 1.002 mm, and bump 1.2 gives 14.88, the safer number to quote.",
        "<b>Friction unmeasured.</b> The coil's 0.79 N could stall under a ~4 N pad load at μ 0.2. The coil has no modelled mount yet.",
        "<b>Lead chain:</b> J3 stop margin is only 0.74° held-out, and the knee MR63ZZ pairs see 110–125 N at 10 N·m (at their rating). The built bars sit 0.7–1.6 mm outside the model straps (R1 −0.39 vs its L1).",
        "<b>Not built yet:</b> the relay's CAD waits on your 4-joint decision."]

    B_joints = table(["Joint", "Bearing", "Hub", "Range / stop"], [
        ["J1", "MR117-2RS pair 7×11×3", "Ø20 × 12.25, face 51.70 mm from GH", "free (no stop needed)"],
        ["J2", "MR117-2RS pair", "Ø20 × 12.25, face 61.31", "J1–J3 angle kept in 27.2…109.3° with ≥ 5° margin (model check; no stop in the CAD)"],
        ["J3", "MR117-2RS pair", "Ø20 × 12.25, face 76.30; axis 10.72 mm off GH", "181.5° travel used"],
        ["pin a", "iglidur G sleeve + washer + E-clip", "on member 3's integral Ø4 pin", "knee window 30.46…149.54° (model check; no stop in the CAD)"],
        ["pin b", "iglidur G sleeve + washer + E-clip", "Ø4 h9 pin integral to D8-06", "knee used 103.0…147.3°"]])

    B_geom = table(["Item", "Value", "Notes"], [
        ["Link arcs (spherical)", "J1–J2 41.02°, J2–J3 68.26°", "fold window width = 2 · min(a1, a2) − 2 · margin"],
        ["Axes", "J1 (0.085, 0.898, 0.432) · J2 (−0.578, 0.673, 0.462) · J3 (−0.091, −0.199, 0.976)", "J1, J2 through GH; J3 tilted b3 0.284 toward the skin normal"],
        ["Hub levels from GH", "J1 51.70 · J2 61.31 · J3 76.30 mm", "hub centres 40.6 mm (J1–J2) and 84.2 mm (J2–J3) apart"],
        ["Knee", "lE 59.55 · lc 28.24 · φE −5.81° · φb −54.91°", "knee link 40.24 × 10 × 2.59 Ti; knee plane 84.72 mm from GH"],
        ["Arm pad", "82.1 mm from GH, 66.3 mm distal of J3's line", "machined in one piece with your BOTTOM (7075-T6, clear anodised)"],
        ["Bars", "8 × 3 Ti-6Al-4V, 5-axis machined (h1b)", "h1 used bent bars; h1b hugs the model strap (bar over strap ≤ 2.6 / 5.6 mm)"],
        ["Seat", "J1 on the acromion top", "same threaded spigot mount as A"]])

    B_perf = table(["Protocol", "Gap (score)", "Reach", "Follow", "In-band 2–14", "Contact", "Min metal", "Overhead"], [
        ["Bench (fit 60, 5° margin) = verified", "27.20 (90.11)", "0.658", "0.964", "0.895", "0.026 (9)", "0.09 mm", "5/28"],
        ["Held-out (5° margin)", "29.12 (89.41)", "0.633", "1.00", "0.888", "0.012", "0.04 mm", "–"],
        ["Polish claim (fit big, 10° margin)", "26.45 (90.38)", "0.647", "0.964", "0.901", "0.012", "1.38 mm", "–"]])

    B_cad = table(["Judge (built CAD h1b)", "Result", "h1 (bent bars)"], [
        ["R1 skin 2–14 mm", "76.7 %", "71.4 %"], ["R1-aim 2–10 mm", "35.8 %", "32.9 %"], ["R3 follows", "98.7 % ✓", "98.7 % ✓"],
        ["R4 overhead clip", "71.2 % (min gap 1.79 mm)", "68.7 %"], ["R6 parts never collide", "0.0 mm ✓", "✓"], ["R7 valid solids", "29 of 29 ✓", "✓"],
        ["R8 mass", "178.0 g ✓", "178.9 g ✓"], ["R11 pad pressure", "0.216 kPa ✓", "0.303 kPa ✓"], ["R16 workspace closed", "61.7 %", "61.7 %"], ["R17 dynamics", "pass ✓ (rolling-friction case)", "pass"]])

    B_cav = [
        "<b>Built before the 2026-10-17 build rules.</b> The knee pins are iglidur sleeves, but the rule now is MR63ZZ pairs (with plain pins R17 fails: 9.3–10.5° cuff twist). The CAD has no physical knee stop or J2 stop. A rebuild adds both; crest-knee-3r already carries them.",
        "<b>The J2 fold limits reach.</b> The J1–J3 angle can span ~27–109°, but the workspace needs 27–141°. So reach is 0.658 and only 5 of 28 overhead poses are followed. Widening the arcs moves hub 2 onto skin it cannot clear.",
        "<b>Metal hugs the skin.</b> 8 poses come within 1 mm, and 9 bench poses put metal in the skin (deepest 4.08 mm, sum 8.38 mm). All 5 overhead poses it follows have metal under 2 mm.",
        "<b>The knee rides its window edge</b> (149.48° held-out vs the 149.54° limit).",
        "<b>The built CAD trails its L1</b> (R1 80.1 → 76.7 %) because the bars ride over the model strap.",
        "<b>Complexity 0</b> relies on your rule that an unsensed cuff knee adds nothing."]

    pareto = pareto_svg([
        ("B · pin knee H1", 0, score(27.20), "pB", 10, 4, "start"), ("Raglan knee (same cx, lower)", 0, score(27.82), "pg", 10, 16, "start"),
        ("Geneva knuckle", 12.0, score(23.57), "pg", 10, 4, "start"), ("Low-arm K-stop", 16.75, score(18.69), "pg", 10, -8, "start"),
        ("3-joint lead", 18.5, score(18.28), "pL", 10, 14, "start"), ("A · lead + relay (4 joints)", 52.5, score(14.76), "pA", -10, -10, "end")])

    trade = table(["Design", "Complexity", "Verified score", "What it adds over B", "Audit"], [
        ["B · pin knee H1", "0", f"{score(27.20)}", "–", "watch"],
        ["Geneva knuckle with pushrod", "12.0", f"{score(23.57)}", "slaved knuckle K, spiral lobe on J2, rocker pin, Ø3 pushrod with 2 rod ends, J2 stops", "watch"],
        ["Low-arm K-stop knuckle", "16.75", f"{score(18.69)}", "slaved K with a half-ring desmo drive, MR63ZZ crank and knee pins, set-screw stop", "watch (11 findings)"],
        ["Cone-cut pin knee (3-joint lead)", "18.5", f"{score(18.28)}", "slaved K with lobe + bell-crank drive, clock spring, J3 dowel stop, MR63ZZ knee", "watch"],
        ["Raglan knee", "0", f"{score(27.82)}", "same chain, raglan-routed bars: scores lower than B", "watch"],
        ["Crest knee", "0", f"{score(31.5)}", "already has MR63ZZ knee pins + J3 stop; scores lower than B", "watch"]])

    data = {"A": A_parts, "B": B_parts, "G": G}
    page = open(os.path.join(HERE, "template.html")).read()
    rep = {
        "%%ASOF%%": E(AS_OF), "%%SUMMARY%%": summary, "%%A_CHAIN%%": chain_svg(True), "%%A_JOINTS%%": A_joints, "%%A_GEOM%%": A_geom,
        "%%A_CLEAR%%": A_clear, "%%RELAY_SVG%%": relay_svg(), "%%RELAY_LEGEND%%": "".join(f"<li>{E(t)}</li>" for t in RELAY_LEGEND), "%%RELAY_DIMS%%": relay_dims, "%%RELAY_PARTS%%": relay_parts,
        "%%A_PERF%%": A_perf, "%%A_CAD%%": A_cad, "%%A_CAV%%": "".join(f"<li>{c}</li>" for c in A_cav),
        "%%B_CHAIN%%": chain_svg(None), "%%B_JOINTS%%": B_joints, "%%B_GEOM%%": B_geom, "%%B_PERF%%": B_perf, "%%B_CAD%%": B_cad,
        "%%B_CAV%%": "".join(f"<li>{c}</li>" for c in B_cav), "%%PARETO%%": pareto, "%%TRADE%%": trade,
        "%%A_MASS%%": str(exo_mass(A_parts)), "%%B_MASS%%": str(exo_mass(B_parts)),
        "%%A_NPARTS%%": str(sum(p["q"] for p in A_parts if not p["u"])), "%%B_NPARTS%%": str(sum(p["q"] for p in B_parts if not p["u"])),
        "%%NBUILT%%": str(len(G)), "%%DATA%%": json.dumps(data, separators=(",", ":")).replace("</", "<\\/"),
        "%%RENDERS%%": json.dumps(renders),
    }
    for k, v in rep.items():
        page = page.replace(k, v)
    assert "%%" not in page, page[page.index("%%") - 40: page.index("%%") + 40]
    open(os.path.join(HERE, "index.html"), "w").write(page)
    json.dump(files, open(os.path.join(HERE, "files.json"), "w"), indent=0)
    print("wrote docs/blueprints/index.html", len(page) // 1024, "KB;", len(files), "supporting files")


if __name__ == "__main__":
    main()
