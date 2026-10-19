<script>
/* ---------- calculations: once each, at the top level ---------- */
dash.calc('ranking', {
  inputs: ['morphs'],
  title: 'Morphologies ranked by gap',
  description: 'Each morphology with the verifier’s numbers where it re-measured one (its own claim where the verifier left a number out), its rank by gap (lower is better; refuted, dropped and the baseline unranked) and whether it beats the 3R baseline’s gap.',
  fn: (morphs) => {
    const n = (v) => (v === null || v === undefined || v === '' || !isFinite(Number(v)) ? null : Number(v));
    const yes = (v) => v === true || String(v).toLowerCase() === 'true' || v === 1 || v === '1';
    const rows = morphs.map((m) => {
      const re = n(m.v_gap) !== null, pick = (f) => (re && n(m['v_' + f]) !== null ? n(m['v_' + f]) : n(m[f]));
      return { id: m.id, name: m.name, family: m.family, lens: m.lens, status: m.status,
        is_baseline: yes(m.is_baseline), remeasured: re,
        verified: ['verified', 'gpu', 'cad', 'judged'].includes(m.status),
        gap: re ? n(m.v_gap) : n(m.gap), claimed_gap: n(m.gap), inband14: pick('inband14'), inband10: pick('inband10'),
        reach: pick('reach'), follow: pick('follow'), contact: pick('contact'), active_dof: n(m.active_dof), passive_dof: n(m.passive_dof),
        t_screened: m.t_screened || null, n_configs: n(m.n_configs), verdict: m.verdict || '', note: m.note || '', doc: m.doc || '' };
    });
    const base = rows.find((r) => r.is_baseline && r.gap !== null);
    const live = rows.filter((r) => !r.is_baseline && r.gap !== null && !['refuted', 'dead'].includes(r.status)).sort((a, b) => a.gap - b.gap);
    return rows.map((r) => ({ ...r, rank: live.includes(r) ? live.indexOf(r) + 1 : null, winner: live.includes(r) && !!base && r.gap < base.gap }));
  }
});
dash.calc('summary', {
  inputs: ['ranking', 'events'],
  title: 'Leader and counts',
  description: 'The ranked-first morphology, the baseline’s gap, how far the leader is ahead of it, when it took the lead, and how many morphologies are screened and beat the baseline.',
  fn: (ranking, events) => {
    const m = ranking.filter((r) => !r.is_baseline), base = ranking.find((r) => r.is_baseline) || null;
    const live = m.filter((r) => r.rank !== null).sort((a, b) => a.rank - b.rank), lead = live[0] || null;
    const named = lead ? events.filter((e) => e.kind === 'leader' && (String(e.event).includes(lead.name) || String(e.event).includes(lead.id))).map((e) => e.time) : [];
    const since = lead ? [lead.t_screened].concat(named).filter(Boolean).sort().pop() || null : null;
    return [{ leader_id: lead ? lead.id : null, leader_name: lead ? lead.name : null, leader_gap: lead ? lead.gap : null,
      leader_verified: lead ? lead.verified : false, leader_winner: lead ? lead.winner : false, leader_since: since,
      baseline_id: base ? base.id : null, baseline_gap: base ? base.gap : null,
      margin: lead && base && base.gap !== null ? Math.round((base.gap - lead.gap) * 100) / 100 : null,
      n_total: m.length, n_screened: m.filter((r) => r.claimed_gap !== null).length,
      n_winners: live.filter((r) => r.winner).length, n_verified_winners: live.filter((r) => r.winner && r.verified).length }];
  }
});
dash.calc('records', {
  inputs: ['ranking'],
  title: 'Best so far, over time',
  description: 'For each bench measure, the morphologies that set a new best when they were screened (refuted, dropped and the baseline left out); claimed marks a record whose number the verifier has not re-measured.',
  fn: (ranking) => {
    const out = [], live = ranking.filter((r) => !r.is_baseline && r.t_screened && !['refuted', 'dead'].includes(r.status))
      .sort((a, b) => (a.t_screened < b.t_screened ? -1 : a.t_screened > b.t_screened ? 1 : 0));
    [['gap', -1], ['inband14', 1], ['inband10', 1], ['reach', 1], ['follow', 1]].forEach(([f, s]) => {
      let best = null;
      live.forEach((r) => { if (r[f] === null) return; if (best === null || s * (r[f] - best) > 0) { best = r[f]; out.push({ metric: f, id: r.id, name: r.name, t: r.t_screened, value: r[f], claimed: !(r.remeasured || r.verified) }); } });
    });
    return out;
  }
});
dash.calc('funnel', {
  inputs: ['ranking'],
  title: 'Morphologies per stage',
  description: 'How many morphologies reached each stage (a later stage counts as having passed the earlier ones; the baseline left out).',
  fn: (ranking) => {
    const m = ranking.filter((r) => !r.is_baseline), at = (s) => m.filter((r) => s.includes(r.status)).length;
    return [{ stage: 'ideated', n: m.length },
      { stage: 'screened', n: m.filter((r) => r.claimed_gap !== null || ['screened', 'verified', 'refuted', 'gpu', 'cad', 'judged'].includes(r.status)).length },
      { stage: 'verified', n: at(['verified', 'gpu', 'cad', 'judged']) }, { stage: 'gpu', n: at(['gpu', 'cad', 'judged']) },
      { stage: 'cad', n: at(['cad', 'judged']) }, { stage: 'judged', n: at(['judged']) }];
  }
});
dash.calc('freshness', {
  inputs: ['events', 'ranking', 'sweeps', 'judged'],
  title: 'Latest activity',
  description: 'The newest time in any dataset: an event, a screening, a sweep configuration or a judged design.',
  fn: (events, ranking, sweeps, judged) => {
    const ts = [].concat(events.map((e) => e.time), ranking.map((r) => r.t_screened), sweeps.map((s) => s.t), judged.map((j) => j.time)).filter(Boolean).sort();
    return [{ t_last: ts.length ? ts[ts.length - 1] : null }];
  }
});
dash.calc('judged_stats', {
  inputs: ['judged', 'reqs'],
  title: 'Latest and best built design, per requirement',
  description: 'Per judged measure, for 3-DOF designs and for all designs: the latest value, and the best value judged under the current rules (after the requirement’s last judging-rule change, from reqs.rules_since), with the design each came from.',
  fn: (judged, reqs) => {
    const out = [], M = [['r1_14', 1, 'R1'], ['r1_10', 1, 'R1-aim'], ['follow', 1, 'R3'], ['overhead_14', 1, 'R4'], ['range_r16', 1, 'R16'], ['parts_mm', -1, 'R6'], ['moves_freely', 1, 'R17']];
    ['3', 'all'].forEach((scope) => {
      const rows = judged.filter((r) => scope === 'all' || Number(r.dof) === 3).sort((a, b) => (a.time < b.time ? -1 : 1));
      M.forEach(([f, s, req]) => {
        const rq = reqs.find((r) => r.req === req), since = rq && rq.rules_since ? rq.rules_since : null;
        const v = rows.filter((r) => r[f] !== null && r[f] !== undefined), val = (r) => (typeof r[f] === 'boolean' ? (r[f] ? 1 : 0) : Number(r[f]));
        const cur = since ? v.filter((r) => r.time >= since) : v;
        if (!v.length) { out.push({ metric: f, scope, latest: null, latest_design: '', best: null, best_design: '', rules_since: since }); return; }
        const last = v[v.length - 1], pool = cur.length ? cur : v, best = pool.reduce((b, r) => (s * (val(r) - val(b)) > 0 ? r : b));
        out.push({ metric: f, scope, latest: last[f], latest_design: last.design, best: best[f], best_design: best.design, rules_since: since });
      });
    });
    return out;
  }
});
dash.calc('reqs_summary', {
  inputs: ['reqs'],
  title: 'Requirements passing',
  description: 'How many of the requirements pass, fail, or are not yet settled.',
  fn: (reqs) => [{ n_total: reqs.length, n_pass: reqs.filter((r) => r.state === 'pass').length, n_fail: reqs.filter((r) => r.state === 'fail').length,
    n_open: reqs.filter((r) => r.state !== 'pass' && r.state !== 'fail').length }]
});
