/* Header, tabs and links; redraws the visible tab whenever data or the width changes. */
(function () {
  const X = window.EXO, el = X.el, mark = X.mark;
  const tabs = [...document.querySelectorAll('.sw-tab')];
  const pages = tabs.map((t) => document.getElementById(t.dataset.tab));

  function header() {
    const take = document.getElementById('takeaway'), fresh = document.getElementById('fresh');
    const built = document.getElementById('fresh-built'), last = document.getElementById('fresh-last');
    const stS = X.st('summary'), stM = X.st('meta');
    const meta = X.rows('meta')[0], s = X.rows('summary')[0];
    [built, last].forEach((e) => e.classList.toggle('dash-skeleton', false));
    built.textContent = meta ? X.ago(meta.built_at) : stM === 'loading' ? '—' : 'unknown';
    if (meta) built.setAttribute('datetime', meta.built_at);
    last.textContent = s && s.t_last ? X.ago(s.t_last) : stS === 'loading' ? '—' : 'none yet';
    if (s && s.t_last) last.setAttribute('datetime', s.t_last);
    const age = meta ? (Date.now() - new Date(meta.built_at)) / 60000 : null;
    fresh.dataset.state = stM === 'error' || stS === 'error' ? 'bad' : age === null ? 'idle' : age > 30 ? 'warn' : 'ok';
    fresh.title = '';
    take.replaceChildren();
    if (stS !== 'ok' || !s) { take.appendChild(el('span', stS === 'loading' ? 'dash-skeleton' : null, stS === 'loading' ? '—' : 'The numbers did not load.')); return; }
    const b = (txt, field, cls) => mark(el('b', cls || null, txt), 'summary', field, 0);
    const T = (t) => document.createTextNode(t);
    if (s.ver_id) {
      const win = s.base_gap !== null && s.ver_gap < s.base_gap;
      if (win) take.append(el('span', 'sw-take-win', 'Winner'));
      take.append(T('Concept-bench leader: '), b(s.ver_name, 'ver_name', 'sw-acc'), T(', verified gap '), b(X.gapf(s.ver_gap), 'ver_gap'),
        T(win ? ', ' : ' ('), b(X.gapf(Math.abs(s.ver_delta)), 'ver_delta'), T(win ? ' below the 3R baseline. ' : ' above the 3R baseline). '));
    } else if (s.claim_id && (s.sweep_gap === null || s.claim_gap <= s.sweep_gap)) {
      const below = s.claim_delta < 0;
      take.append(T('No verified concept-bench leader yet. Best evidence: '), b(s.claim_name, 'claim_name'), T('’s claimed row, gap '), b(X.gapf(s.claim_gap), 'claim_gap'),
        T(', '), b(X.gapf(Math.abs(s.claim_delta)), 'claim_delta'), T(below ? ' below the 3R baseline (waiting for the verifier). ' : ' above the 3R baseline. '));
    } else if (s.sweep_id) {
      const below = s.sweep_delta < 0;
      take.append(T('No verified concept-bench leader yet. Best evidence: '), b(s.sweep_name, 'sweep_name'), T('’s best sweep configuration, gap '), b(X.gapf(s.sweep_gap), 'sweep_gap'),
        T(', '), b(X.gapf(Math.abs(s.sweep_delta)), 'sweep_delta'), T(below ? ' below the 3R baseline (unverified). ' : ' above the 3R baseline. '));
    } else if (s.base_gap !== null) {
      take.append(T('No bench result yet; the bar to beat is the 3R baseline, gap '), b(X.gapf(s.base_gap), 'base_gap'), T('. '));
    }
    if (s.cad_r1 !== null) take.append(T('Built CAD: best 3-DOF R1 '), b(X.pct(s.cad_r1), 'cad_r1'), T(' (pass 90%); '));
    take.append(b(String(s.reqs_pass), 'reqs_pass'), T(' of '), b(String(s.reqs_total), 'reqs_total'), T(' requirements pass on the best judged design.'));
  }

  function show(name, focus) {
    tabs.forEach((t) => t.setAttribute('aria-selected', String(t.dataset.tab === name)));
    pages.forEach((p) => { p.hidden = p.id !== name; });
    if (X.tabs[name]) X.tabs[name]();
    if (focus) focus.scrollIntoView();
  }
  tabs.forEach((t) => t.addEventListener('click', () => { show(t.dataset.tab); dash.setLink(t.dataset.tab); }));
  tabs.forEach((t, i) => t.addEventListener('keydown', (ev) => {
    if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
    const n = tabs[(i + (ev.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; n.focus(); n.click();
  }));

  let first = true;
  dash.onData(() => {
    header();
    const a = X.active();
    if (X.tabs[a]) X.tabs[a]();
    if (first) {
      first = false;
      const named = location.hash ? document.getElementById(decodeURIComponent(location.hash.slice(1))) : null;
      if (named) {
        const page = named.closest('.sw-page');
        if (page && page.id !== a) requestAnimationFrame(() => show(page.id, page.id === named.id ? null : named));
        else if (page && page.id !== named.id) requestAnimationFrame(() => named.scrollIntoView());
      }
    }
  });
})();
