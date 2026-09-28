/* Úvodní stránka: nejbližší hodiny, náhled rozvrhu, nejbližší akce */
(() => {
  const S = window.LVS; if (!S) return;
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let names = {};
  const load = fetch('assets/lekce.json').then(r => r.json()).then(j => { names = j; }).catch(() => {});

  load.then(() => {
    const now = new Date();
    const all = [...S.week(0).lessons, ...S.week(1).lessons];
    const up = all.filter(L => !S.status(L).closed && L.start > now);

    /* karta v hero */
    const list = document.getElementById('next-list');
    if (list) list.innerHTML = up.slice(0, 3).map(L => {
      const st = S.status(L); const n = names[L.id] ? names[L.id].name : L.id;
      const lab = st.st === 'free' ? `volno ${st.free}` : 'čekací listina';
      return `<a class="next-row" href="rozvrh/?hodina=${encodeURIComponent(L.key)}">
        <div class="next-day"><b>${L.day.getDate()}.</b><small>${S.DAYS[(L.day.getDay() + 6) % 7]}</small></div>
        <div><div class="next-title">${esc(n)}</div><div class="next-meta">${L.s} · ${S.PLACES[L.place].name}</div></div>
        <span class="st st--${st.st}">${lab}</span></a>`;
    }).join('');

    /* náhled rozvrhu */
    const board = document.getElementById('board-days');
    if (board) {
      const byDay = new Map();
      up.forEach(L => { const k = S.iso(L.day); if (!byDay.has(k)) byDay.set(k, []); byDay.get(k).push(L); });
      const days = [...byDay.values()].slice(0, 3);
      const wk = document.getElementById('board-week');
      if (wk && days[0]) wk.textContent = 'Týden ' + S.wlabel(S.week(days[0][0].day >= S.week(1).start ? 1 : 0).start);
      board.innerHTML = days.map(ls => {
        const d = ls[0].day;
        return `<div class="board-day"><h4>${S.DAYS_LONG[(d.getDay() + 6) % 7]} ${S.dnum(d)}</h4>` + ls.slice(0, 2).map(L => {
          const st = S.status(L); const n = names[L.id] ? names[L.id].name : L.id;
          const capTxt = st.st === 'wait' ? `plno · čeká ${st.queue}` : `${st.taken}/${L.cap}`;
          return `<a class="lcard s-${st.st}" href="rozvrh/?hodina=${encodeURIComponent(L.key)}">
            <span class="lcard-time"><span>${L.s}–${L.e}</span></span>
            <span class="lcard-title">${esc(n)}</span><span class="lcard-place">${S.PLACES[L.place].name}</span>
            <span class="cap"><span class="cap-bar"><i style="width:${Math.round(st.taken / L.cap * 100)}%"></i></span>${capTxt}</span></a>`;
        }).join('') + '</div>';
      }).join('');
    }
  });

  /* akce */
  const ev = document.getElementById('home-events');
  if (ev) fetch('assets/akce.json').then(r => r.json()).then(list => {
    const next = list.filter(e => !e.past);
    const last = list.filter(e => e.past && !/tábor/i.test(e.typ)).slice(-1);
    ev.innerHTML = [...next.slice(0, 3), ...last].map(e => `<li class="ev-row">
      <div class="ev-date">${esc(e.date)}<small>${e.past ? 'proběhlo' : 'připravujeme'}</small></div>
      <div><b>${esc(e.typ)}</b><p>${esc(e.info)}</p></div></li>`).join('') +
      `<li style="padding-top:1.4rem;list-style:none"><a class="link" href="akce/">Celý kalendář akcí 2026 →</a></li>`;
  }).catch(() => {});
})();
