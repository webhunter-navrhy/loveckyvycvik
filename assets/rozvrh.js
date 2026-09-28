/* Rozvrh cvičení — ukázka přihlašovacího systému (nic se neodesílá, stav se drží jen v prohlížeči) */
(() => {
  const S = window.LVS; if (!S) return;
  const $ = (s, c = document) => c.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const DOGS = [{ id: 'brok', name: 'Brok', breed: 'český fousek' }, { id: 'dina', name: 'Dina', breed: 'maďarský ohař krátkosrstý' }];
  const KEY = 'lv-demo-rozvrh';
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } },
    set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch { /* bez úložiště */ } },
  };
  let st = Object.assign({ book: {}, guest: false }, store.get());
  const save = () => store.set(st);
  const params = new URLSearchParams(location.search);
  let offset = 0, filter = 'all', cat = {}, focusKey = params.get('hodina');
  const typ = params.get('typ');
  if (typ) filter = S.catOf(typ);

  const toastEl = $('#toast');
  let tt;
  const toast = (msg) => { $('span', toastEl).textContent = msg; toastEl.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('on'), 3400); };

  const nameOf = (L) => cat[L.id] ? cat[L.id].name : L.id;
  const priceOf = (L) => cat[L.id] && cat[L.id].price ? cat[L.id].price : 'dle rozvrhu';
  const dlabel = (L) => `${S.DAYS_LONG[(L.day.getDay() + 6) % 7]} ${S.dnum(L.day)} ${L.day.getFullYear()}, ${L.s}–${L.e}`;

  /* ---- účet ---- */
  function renderAcc() {
    const box = $('#acc');
    if (st.guest) {
      box.innerHTML = `<div class="acc-who"><div class="avatar" style="background:var(--paper-2);color:var(--muted)">?</div><div>Nejste přihlášeni<small>Na hodiny se hlásí registrovaní klienti</small></div></div>
        <button class="btn btn--sm btn--dark" id="login">Přihlásit se (ukázka)</button><a class="btn btn--sm btn--ghost" href="../registrace/">Registrace</a>`;
      $('#login').onclick = () => { st.guest = false; save(); renderAll(); toast('Přihlášeno jako ukázkový klient'); };
    } else {
      box.innerHTML = `<div class="acc-who"><div class="avatar">UK</div><div>Ukázkový klient<small>${DOGS.map(d => d.name).join(' · ')} — ukázkový účet</small></div></div>
        <button class="btn btn--sm btn--ghost" id="logout">Odhlásit</button>`;
      $('#logout').onclick = () => { st.guest = true; save(); renderAll(); };
    }
    const n = Object.values(st.book).reduce((a, b) => a + Object.keys(b).length, 0);
    const badge = $('#my-count'); badge.hidden = !n || st.guest; badge.textContent = n;
    $('#my-open').hidden = st.guest;
  }

  /* ---- filtry ---- */
  function renderFilters() {
    const f = $('#filters');
    const opts = [['all', 'Vše'], ...Object.entries(S.CAT)];
    f.innerHTML = opts.map(([k, v]) => `<button class="fchip${filter === k ? ' on' : ''}" data-f="${k}">${v}</button>`).join('');
    f.querySelectorAll('button').forEach(b => b.onclick = () => { filter = b.dataset.f; renderFilters(); renderWeek(); });
  }

  /* ---- týden ---- */
  let current = [];
  function renderWeek() {
    const w = S.week(offset);
    current = w.lessons;
    $('#wk-label').textContent = S.wlabel(w.start);
    $('#wk-prev').disabled = offset <= -1;
    $('#wk-next').disabled = offset >= 1;
    $('#wk-next').title = offset >= 1 ? 'Hodiny do rozvrhu vypisujeme každý týden v neděli/pondělí' : '';
    const today = S.iso(new Date());
    let html = '';
    for (let i = 0; i < 7; i++) {
      const day = new Date(w.start); day.setDate(w.start.getDate() + i);
      const ls = w.lessons.filter(L => S.iso(L.day) === S.iso(day) && (filter === 'all' || L.cat === filter));
      html += `<div class="day${S.iso(day) === today ? ' today' : ''}"><div class="day-h"><b>${S.DAYS[i]}</b><span>${day.getDate()}. ${day.getMonth() + 1}.</span></div>`;
      html += ls.length ? ls.map(card).join('') : '<p class="day-empty">bez hodin</p>';
      html += '</div>';
    }
    $('#week').innerHTML = html;
    $('#week').querySelectorAll('.lcard').forEach(b => b.onclick = () => openLesson(b.dataset.key));
  }
  function card(L) {
    const s = S.status(L, st.book[L.key]);
    const cls = s.me ? `s-${s.me}` : `s-${s.st}`;
    const lab = s.me === 'booked' ? 'přihlášeno' : s.me === 'waitme' ? 'čekací listina' : s.st === 'free' ? 'volno' : s.st === 'wait' ? 'plno' : 'uzavřeno';
    const stc = s.me === 'booked' ? 'booked' : s.me === 'waitme' ? 'wait' : s.st;
    const capTxt = s.queue && !s.closed ? `${s.taken}/${L.cap} · čeká ${s.queue}` : `${s.taken}/${L.cap}`;
    return `<button class="lcard ${cls}" data-key="${L.key}">
      <span class="lcard-time"><span>${L.s}–${L.e}</span><span class="st st--${stc}">${lab}</span></span>
      <span class="lcard-title">${esc(nameOf(L))}</span>
      <span class="lcard-place">${S.PLACES[L.place].name}</span>
      <span class="cap"><span class="cap-bar"><i style="width:${Math.round(s.taken / L.cap * 100)}%"></i></span>${capTxt}</span></button>`;
  }

  /* ---- panel ---- */
  const panel = $('#panel'), scrim = $('#scrim');
  let lastFocus = null;
  const openPanel = () => { lastFocus = document.activeElement; panel.classList.add('on'); scrim.classList.add('on'); panel.setAttribute('aria-hidden', 'false'); document.documentElement.style.overflow = 'hidden'; setTimeout(() => $('#panel-x').focus(), 50); };
  const closePanel = () => { panel.classList.remove('on'); scrim.classList.remove('on'); panel.setAttribute('aria-hidden', 'true'); document.documentElement.style.overflow = ''; if (lastFocus) lastFocus.focus(); };
  $('#panel-x').onclick = closePanel; scrim.onclick = closePanel;
  addEventListener('keydown', e => { if (e.key === 'Escape' && panel.classList.contains('on')) closePanel(); });

  function findLesson(key) {
    for (const o of [-1, 0, 1]) { const L = S.week(o).lessons.find(x => x.key === key); if (L) return { L, o }; }
    return null;
  }

  function openLesson(key) {
    const hit = findLesson(key); if (!hit) return;
    const L = hit.L; const c = cat[L.id] || { f: {} };
    const mine = st.book[L.key] || {};
    const s = S.status(L, mine);
    const P = S.PLACES[L.place];
    const place = P.map ? `${esc(P.full)} · <a href="${P.map.startsWith('http') ? P.map : '../' + P.map}"${P.map.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>jak se k nám dostanete</a>` : esc(P.full);
    const order = ['Věk', 'Skupina', 'Plemeno', 'Předchozí výcvik', 'Pomůcky', 'Předmět cvičení'];
    const fields = order.filter(k => c.f[k]).map(k => `<dt>${k}</dt><dd>${esc(c.f[k])}</dd>`).join('');
    const lab = s.closed ? 'přihlašování je uzavřeno' : s.me === 'booked' ? 'jste přihlášeni' : s.me === 'waitme' ? 'jste na čekací listině' : s.st === 'free' ? `volno — ${s.free} z ${L.cap} míst` : `hodina je plná${s.queue ? ` — čekací listina: ${s.queue}` : ''} — lze se zapsat na čekací listinu`;
    const stc = s.closed ? 'closed' : s.me === 'booked' ? 'booked' : s.me === 'waitme' ? 'wait' : s.st;
    $('#panel-eyebrow').textContent = S.CAT[L.cat];
    $('#panel-b').innerHTML = `
      <span class="st st--${stc}">${lab}</span>
      <h2 id="panel-title">${esc(nameOf(L))}</h2>
      <dl class="kv"><dt>Termín</dt><dd>${dlabel(L)}</dd><dt>Místo</dt><dd>${place}</dd><dt>Cena</dt><dd>${esc(priceOf(L))}</dd><dt>Obsazenost</dt><dd>${s.taken} z ${L.cap} míst${s.queue ? ` · čekací listina ${s.queue}` : ''}</dd></dl>
      ${fields ? `<dl class="kv">${fields}</dl>` : ''}
      ${L.cat !== 'teorie' ? '<div class="note note--warn" style="margin-top:.4rem"><span><b>S ohledem na počasí:</b> misku s vodou, obleček pro krátkosrsté psy + vhodné sportovní oblečení a obuv.</span></div>' : ''}`;
    renderActions(L, s, mine);
    if (!panel.classList.contains('on')) openPanel();
  }

  function renderActions(L, s, mine) {
    const f = $('#panel-f');
    if (st.guest) {
      f.innerHTML = `<div class="row"><button class="btn btn--dark" id="p-login">Přihlásit se (ukázka)</button><a class="btn btn--ghost" href="../registrace/">Registrace</a></div><p>Na hodiny se mohou hlásit registrovaní klienti po potvrzení registrace.</p>`;
      $('#p-login').onclick = () => { st.guest = false; save(); renderAll(); openLesson(L.key); };
      return;
    }
    const rows = DOGS.map(d => {
      const m = mine[d.id];
      if (m) return `<label style="cursor:default"><span class="st st--${m === 'in' ? 'booked' : 'wait'}"></span><span><b>${d.name}</b> — ${m === 'in' ? 'přihlášen/a' : 'na čekací listině'}</span>${s.closed ? '' : `<button class="btn btn--sm btn--ghost" data-off="${d.id}" style="margin-left:auto">Odhlásit</button>`}</label>`;
      return `<label><input type="checkbox" value="${d.id}"${s.closed ? ' disabled' : ''}><span><b>${d.name}</b></span><small>${d.breed}</small></label>`;
    }).join('');
    const canFree = s.st === 'free';
    const btn = s.closed ? `<button class="btn" disabled>Přihlašování uzavřeno</button>`
      : canFree ? `<button class="btn btn--dark" id="p-book" disabled>Vyberte psa</button>`
        : `<button class="btn" id="p-book" style="--bg:var(--wait);--fg:#2a1d00" disabled>Vyberte psa pro čekací listinu</button>`;
    f.innerHTML = `<div class="pick">${rows}</div><div style="margin-top:.9rem">${btn}</div>
      <p>${s.closed ? 'Hodina už proběhla nebo začíná během dvou hodin.' : 'Když nemůžete dorazit, odhlaste se — někdy máme za vás náhradníka.'}</p>`;
    const book = $('#p-book');
    const boxes = [...f.querySelectorAll('input[type=checkbox]')];
    const upd = () => {
      const n = boxes.filter(b => b.checked).length;
      if (!book) return;
      book.disabled = !n;
      if (canFree) book.textContent = n ? (n > s.free ? `Přihlásit ${s.free}, zbytek na čekací listinu` : `Přihlásit ${n === 1 ? 'psa' : n + ' psy'}`) : 'Vyberte psa';
      else book.textContent = n ? 'Zapsat na čekací listinu' : 'Vyberte psa pro čekací listinu';
    };
    boxes.forEach(b => b.onchange = upd);
    if (book) book.onclick = () => {
      const sel = boxes.filter(b => b.checked).map(b => b.value);
      const m = st.book[L.key] = st.book[L.key] || {};
      let free = s.st === 'free' ? s.free : 0; const inN = [], waitN = [];
      sel.forEach(id => { const nm = DOGS.find(d => d.id === id).name; if (free > 0) { m[id] = 'in'; free--; inN.push(nm); } else { m[id] = 'wait'; waitN.push(nm); } });
      save(); renderAll(); openLesson(L.key);
      toast(inN.length ? `${inN.join(' a ')} ${inN.length > 1 ? 'jsou přihlášeni' : 'je přihlášen/a'} — ${nameOf(L)}, ${S.dnum(L.day)}` : `Zapsáno na čekací listinu — dáme vědět, když se místo uvolní`);
    };
    f.querySelectorAll('[data-off]').forEach(b => b.onclick = (e) => {
      e.preventDefault();
      const m = st.book[L.key]; delete m[b.dataset.off]; if (!Object.keys(m).length) delete st.book[L.key];
      save(); renderAll(); openLesson(L.key); toast('Odhlášeno. Děkujeme, že dáváte vědět.');
    });
  }

  /* ---- moje přihlášky ---- */
  $('#my-open').onclick = () => {
    const items = Object.entries(st.book).map(([k, m]) => ({ hit: findLesson(k), m })).filter(x => x.hit).sort((a, b) => a.hit.L.start - b.hit.L.start);
    $('#panel-eyebrow').textContent = 'Ukázkový účet';
    $('#panel-b').innerHTML = `<h2 id="panel-title">Moje přihlášky</h2>` + (items.length ? `<ul class="mylist">` + items.map(({ hit, m }) => {
      const L = hit.L; return Object.entries(m).map(([dog, v]) => `<li class="${v === 'wait' ? 'w' : ''}"><div><b>${esc(nameOf(L))}</b><small>${dlabel(L)} · ${S.PLACES[L.place].name}<br>${DOGS.find(d => d.id === dog).name} — ${v === 'in' ? 'přihlášen/a' : 'čekací listina'}</small></div><button class="btn btn--sm btn--ghost" data-k="${L.key}" data-d="${dog}">Odhlásit</button></li>`).join('');
    }).join('') + '</ul>' : `<p class="empty">Zatím nejste přihlášeni na žádnou hodinu.<br>Vyberte si hodinu v rozvrhu.</p>`);
    $('#panel-f').innerHTML = `<p style="margin:0">Kredit z permanentky se v ostrém provozu odečte po odcvičené hodině.</p>`;
    $('#panel-b').querySelectorAll('[data-k]').forEach(b => b.onclick = () => {
      const m = st.book[b.dataset.k]; delete m[b.dataset.d]; if (!Object.keys(m).length) delete st.book[b.dataset.k];
      save(); renderAll(); $('#my-open').click(); toast('Odhlášeno. Děkujeme, že dáváte vědět.');
    });
    if (!panel.classList.contains('on')) openPanel();
  };

  $('#wk-prev').onclick = () => { offset--; renderWeek(); };
  $('#wk-next').onclick = () => { offset++; renderWeek(); };

  function renderAll() { renderAcc(); renderWeek(); }

  fetch('../assets/lekce.json').then(r => r.json()).then(j => { cat = j; }).catch(() => {}).finally(() => {
    renderFilters(); renderAll();
    if (focusKey) {
      const hit = findLesson(focusKey);
      if (hit) { offset = hit.o; renderWeek(); openLesson(focusKey); }
    }
  });
})();
