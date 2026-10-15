/* Requirements tab (the board) and Log tab (events, GPU spend). */
(function () {
  const X = window.EXO, el = X.el, mark = X.mark;
  const fmtV = (v, unit, rid) => {
    if (v === null || v === undefined) return '—';
    if (['R7', 'R17'].includes(rid)) return v ? 'yes' : 'no';
    if (unit === '%') return X.pct(v);
    return d3.format(Math.abs(v) < 10 ? '.2~f' : '.1~f')(v) + (unit ? ' ' + unit : '');
  };

  function board() {
    const box = document.getElementById('board-grid'), sum = document.getElementById('board-sum');
    box.replaceChildren(); sum.replaceChildren();
    const st = X.st('reqs');
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const R = X.rows('reqs');
    if (!R.length) { box.appendChild(el('div', 'sw-msg', 'No requirement data yet.')); return; }
    const s = X.rows('summary')[0];
    if (s) {
      sum.append(mark(el('b', null, String(s.reqs_pass)), 'summary', 'reqs_pass', 0), document.createTextNode(' of '), mark(el('b', null, String(s.reqs_total)), 'summary', 'reqs_total', 0),
        document.createTextNode(' pass on '), mark(el('b', null, s.reqs_design || '–'), 'summary', 'reqs_design', 0));
    }
    R.forEach((r) => {
      const w = 'req=' + X.enc(r.req);
      const c = el('div', 'sw-rq'); c.dataset.s = r.state; c.id = 'req-' + r.req;
      const top = el('div', 'sw-rq-top');
      top.appendChild(el('span', 'sw-rq-id', r.req));
      const stt = mark(el('span', 'sw-st', r.state), 'reqs', 'state', w); stt.dataset.s = r.state; top.appendChild(stt);
      c.appendChild(top);
      c.appendChild(mark(el('span', 'sw-rq-name', r.name), 'reqs', 'name', w));
      const v = el('span', 'sw-rq-val');
      if (r.value !== null) v.append(mark(el('b', null, fmtV(r.value, r.unit, r.req)), 'reqs', 'value', w), document.createTextNode(' · pass ' + (r.target || '–')));
      else v.append(document.createTextNode(r.target ? 'pass ' + r.target : 'no numeric threshold'));
      c.appendChild(v);
      if (r.best_design && r.value !== null && r.best_design !== r.design) {
        const b = el('span', 'sw-rq-best');
        b.append(document.createTextNode('best any 3-DOF design: '), mark(el('b', null, fmtV(r.best_value, r.unit, r.req)), 'reqs', 'best_value', w), document.createTextNode(' (' + r.best_design + ')'));
        c.appendChild(b);
      }
      if (r.rules_since) c.appendChild(el('span', 'sw-rq-old', 'judging rule changed ' + d3.utcFormat('%b %-d %H:%M UTC')(new Date(r.rules_since)) + ' (' + r.rules_why + '); older values are not compared'));
      if (r.judge) c.appendChild(el('span', 'sw-rq-judge', 'judge: ' + r.judge));
      box.appendChild(c);
    });
  }

  let kind = 'all';
  const KINDS = [['all', 'All'], ['leader', 'Records'], ['milestone', 'Milestones'], ['judged', 'Judged designs'], ['measurement', 'Measurement changes'], ['infra', 'Infrastructure']];
  function log() {
    const list = document.getElementById('log-list'), seg = document.getElementById('log-kind');
    if (!seg.children.length) KINDS.forEach(([k, label]) => {
      const b = el('button', null, label); b.type = 'button'; b.dataset.k = k; b.setAttribute('aria-pressed', String(k === kind));
      b.addEventListener('click', () => { kind = k; seg.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.k === kind))); log(); });
      seg.appendChild(b);
    });
    list.replaceChildren();
    const st = X.st('events');
    list.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') list.appendChild(el('li', 'sw-msg sw-failed', 'Failed to load')); return; }
    const E = X.rows('events').filter((e) => kind === 'all' || e.kind === kind).slice().sort((a, b) => (a.time < b.time ? 1 : a.time > b.time ? -1 : 0));
    document.getElementById('log-count').textContent = E.length + ' events';
    if (!E.length) { list.appendChild(el('li', 'sw-msg', 'Nothing of this kind yet.')); return; }
    E.slice(0, 400).forEach((e) => {
      const li = el('li'); li.dataset.k = e.kind;
      const t = el('span', 'sw-log-t'); t.appendChild(el('time', null, d3.utcFormat('%b %-d, %H:%M UTC')(new Date(e.time)))); t.appendChild(el('small', null, X.ago(e.time)));
      const k = el('span'); const ch = el('span', 'sw-chip', e.kind); ch.dataset.k = e.kind; k.appendChild(ch);
      li.append(t, k, el('span', 'sw-log-e', e.event));
      list.appendChild(li);
    });
  }

  function spend() {
    const box = document.getElementById('spend-chart');
    const st = X.st('spend');
    const S = X.rows('spend');
    if (!X.ready(box, st, S.length ? null : 'No logged GPU spend.')) return;
    const xd = X.timeDomain(S.map((r) => X.date(r.time)));
    X.timeChart(box, { H: 170, x: xd, y: { domain: [0, Math.max(1, d3.max(S, (r) => r.spent) * 1.2)], fmt: (v) => '$' + d3.format('.2~f')(v) },
      lines: [{ pts: S.map((r) => ({ t: X.date(r.time), v: r.spent })), color: X.acc(), width: 2 }],
      dots: S.map((r) => ({ t: X.date(r.time), v: r.spent, r: 3.5, fill: X.acc(), head: X.tUTC(X.date(r.time)), tip: [r.endpoint, ['spent so far', '$' + d3.format('.2f')(r.spent)], ['balance after', '$' + d3.format('.2f')(r.balance)]] })) });
  }

  X.tabs.reqs = () => { board(); };
  X.tabs.log = () => { log(); spend(); };
})();
