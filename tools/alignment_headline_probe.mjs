// Alignment probe of the dashboard headline (docs/ALIGNMENT.md, R patterns): re-runs the page's OWN 'board' and 'leader'
// calcs, extracted verbatim from the page (from "const live = (m)" up to "dash.calc('reqsum'"), on docs/dashboard/data/
// morphs.json as published and on what-if copies held only in memory. It never edits the page, the data or a row.
//   node tools/alignment_headline_probe.mjs <page.html> <morphs.json> <sweeps.json> [out.json]
// What-ifs (each one changes one field of one row in memory):
//   A the tie target (the current headline) is flagged 'gamed'      B the tie target is refuted
//   C a new verified 3-joint row beats the tie target by 0.04        D the tie row's leader_ruling is removed
//   E the ruling text starts with a space                            F the tie row's status is 'screened' (pre-promotion)
import fs from 'fs';
const [page, morphsPath, sweepsPath, outPath] = process.argv.slice(2);
const html = fs.readFileSync(page, 'utf8');
const a = html.indexOf('const live = (m)'), b = html.indexOf("dash.calc('reqsum'");
if (a < 0 || b < 0) { console.error('page calcs not found'); process.exit(2); }
const calcs = {}; const dash = { calc: (n, o) => { calcs[n] = o.fn; } };
new Function('dash', html.slice(a, b))(dash);
const M0 = JSON.parse(fs.readFileSync(morphsPath, 'utf8'));
let S = []; try { S = JSON.parse(fs.readFileSync(sweepsPath, 'utf8')); if (!Array.isArray(S)) S = S.rows || []; } catch (e) { S = []; }
const clone = () => JSON.parse(JSON.stringify(M0));
const ties = M0.filter((m) => /^tie/i.test(m.leader_ruling || ''));
const out = { page, morphs: morphsPath, tie_rows: ties.map((m) => ({ id: m.id, v_gap: m.v_gap, target: (m.leader_ruling || '').slice(4).split('|')[0].trim() })), runs: [] };
const run = (label, M) => {
  const board = calcs.board(M, S), L = calcs.leader(board)[0];
  const head = board.find((r) => r.id === L.id) || {};
  const above = board.filter((r) => r.basis === 'verified' && r.state === 'Verified' && (r.active_dof == null || r.active_dof <= 3) && r.gap < (head.gap ?? 1e9))
    .map((r) => ({ id: r.id, gap: r.gap, ruling: (r.leader_ruling || '').slice(0, 40), named_in_headline: (L.short || '').includes(r.short) }));
  out.runs.push({ label, headline: L.id, headline_gap: head.gap ?? null, headline_text: L.short, score: L.score, lower_gap_3joint_verified_not_headline: above });
  console.log(`[${label}] headline ${L.id} gap ${head.gap} "${L.short}"`);
  above.forEach((r) => console.log(`    lower-gap verified <=3-joint row kept out of the headline: ${r.id} ${r.gap} named=${r.named_in_headline} ruling="${r.ruling}"`));
};
const set = (id, f) => { const M = clone(); const m = M.find((x) => x.id === id); if (m) f(m); return M; };
run('as published', clone());
for (const t of ties) {
  const tgt = (t.leader_ruling || '').slice(4).split('|')[0].trim();
  run(`A ${tgt} flagged gamed`, set(tgt, (m) => { m.alignment = 'gamed'; }));
  run(`B ${tgt} refuted`, set(tgt, (m) => { m.status = 'refuted'; }));
  run(`C new verified 3-joint row 0.04 below ${tgt}`, (() => { const M = clone(); const s = M.find((x) => x.id === tgt); if (s) { const n = JSON.parse(JSON.stringify(s)); n.id = 'whatif-new-leader-3r'; n.name = 'whatif new leader'; n.v_gap = Math.round((s.v_gap - 0.04) * 100) / 100; n.leader_ruling = ''; M.push(n); } return M; })());
  run(`D ${t.id} ruling removed`, set(t.id, (m) => { m.leader_ruling = ''; }));
  run(`E ${t.id} ruling with a leading space`, set(t.id, (m) => { m.leader_ruling = ' ' + m.leader_ruling; }));
  run(`F ${t.id} status screened (before the polished promotion)`, set(t.id, (m) => { m.status = 'screened'; }));
}
if (outPath) fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
