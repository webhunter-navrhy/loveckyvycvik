/* Cvičenci a absolventi — vyhledávání, filtry podle zkoušek, postupné načítání */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const esc = (s) => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const NOTES = {
    absolventi: 'Přehled našich úspěšných absolventů — hlavně od roku 2018. Pokud si někdo přeje být uveden, ať pošle e-mail a rádi jej doplníme. Pokud si někdo nepřeje zde být, také ihned mažeme.',
    cvicenci: 'Informace o našich svěřencích, kteří nám pravidelně docházejí na výcvik v roce 2026. Ti, kteří již splnili v minulých letech zkoušky, najdou své výsledky v Absolventech.',
    stari: 'Přehled našich odchovánků, kteří s námi začínali, cvičili a úspěšně absolvovali různé zkoušky do roku 2018.',
  };
  const EXAMS = ['ZV', 'PZ', 'LZ', 'SVP', 'VP', 'VZ', 'OVVR', 'BZ', 'BZH', 'ZN', 'KVP'];
  const LEVELS = [['zac', 'začátečníci'], ['mirne', 'mírně pokročilí'], ['pokr', 'pokročilí']];
  const PAGE = 36;
  let data, tab = 'absolventi', q = '', f = '', shown = PAGE;

  const hasExam = (r, ex) => r.some(x => new RegExp('(^|[\\s(„"])' + ex + '(\\s|$|\\s?-|\\s?\\(|,)').test(x.replace(/[„“"]/g, ' ')));
  const levelOf = (l) => { const n = norm(l); return n.includes('mirne') ? 'mirne' : n.includes('pokrocil') ? 'pokr' : 'zac'; };

  function list() {
    const nq = norm(q);
    if (tab === 'cvicenci') {
      return data.cvicenci.filter(c => (!nq || norm(Object.values(c).join(' ')).includes(nq)) && (!f || levelOf(c.level) === f));
    }
    return data[tab].filter(a => (!nq || norm(a.n + ' ' + a.o + ' ' + a.r.join(' ')).includes(nq)) && (!f || hasExam(a.r, f)));
  }

  function renderFilters() {
    const opts = tab === 'cvicenci' ? LEVELS : EXAMS.map(e => [e, e]);
    $('#kf').innerHTML = `<button class="fchip${!f ? ' on' : ''}" data-f="">Vše</button>` + opts.map(([k, v]) => `<button class="fchip${f === k ? ' on' : ''}" data-f="${k}">${v}</button>`).join('');
    $('#kf').querySelectorAll('button').forEach(b => b.onclick = () => { f = b.dataset.f; shown = PAGE; renderFilters(); render(); });
  }

  function render() {
    const items = list();
    $('#kcount').textContent = `${items.length} ${items.length === 1 ? 'pes' : items.length < 5 && items.length ? 'psi' : 'psů'}`;
    const box = $('#klist');
    if (tab === 'cvicenci') {
      const lv = { zac: '', mirne: 'lvl--2', pokr: 'lvl--3' };
      box.innerHTML = `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Jméno pejska</th><th>Plemeno</th><th>Majitel</th><th>Dosažená úroveň</th><th>Úspěchy</th></tr></thead><tbody>` +
        items.map(c => `<tr><td>${esc(c.name)}</td><td>${esc(c.breed)}</td><td>${esc(c.owner)}</td><td><span class="lvl ${lv[levelOf(c.level)]}">${esc(c.level)}</span></td><td>${esc(c.success)}</td></tr>`).join('') +
        `</tbody></table></div>`;
      $('#kmore').hidden = true;
    } else {
      box.innerHTML = '<div class="agrid">' + items.slice(0, shown).map(a => `<article class="acard">
        <div class="acard-img" style="background-image:url(../assets/logo-color.svg);background-size:34%">${a.i ? `<img src="${a.i}" alt="${esc(a.n)}" loading="lazy">` : ''}</div>
        <div class="acard-body"><b>${esc(a.n)}</b><small>${esc(a.o)}</small><div class="res">${a.r.slice(0, 8).map(r => `<span>${esc(r)}</span>`).join('')}${a.r.length > 8 ? `<span>+${a.r.length - 8}</span>` : ''}</div></div></article>`).join('') + '</div>';
      $('#kmore').hidden = items.length <= shown;
    }
    if (!items.length) box.innerHTML = '<p class="empty">Nic jsme nenašli. Zkuste jiné hledání.</p>';
  }

  document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
    document.querySelectorAll('.tab').forEach(x => x.setAttribute('aria-selected', x === t));
    tab = t.dataset.tab; f = ''; shown = PAGE; $('#tab-note').textContent = NOTES[tab]; renderFilters(); render();
  });
  let deb;
  $('#q').addEventListener('input', e => { clearTimeout(deb); deb = setTimeout(() => { q = e.target.value; shown = PAGE; render(); }, 120); });
  $('#kmore').onclick = () => { shown += PAGE; render(); };

  fetch('../assets/klienti.json').then(r => r.json()).then(j => {
    data = j; $('#tab-note').textContent = NOTES[tab]; renderFilters(); render();
  });
})();
