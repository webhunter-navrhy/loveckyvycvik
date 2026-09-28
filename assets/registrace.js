/* Registrace — vícekrokový formulář (ukázka, nic se neodesílá) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const form = $('#reg-form'); if (!form) return;
  const steps = $$('.fstep', form), prog = $$('.progress li');
  const back = $('#f-back'), next = $('#f-next');
  let step = 0, dogN = 0;

  const dogsBox = $('#dogs');
  function addDog() {
    dogN++;
    const i = dogN;
    const el = document.createElement('div');
    el.className = 'dogbox';
    el.innerHTML = `<div class="dogbox-h"><span>Pes ${dogsBox.querySelectorAll('.dogbox').length + 1}</span>${i > 1 ? '<button type="button" class="dogbox-x">Odebrat</button>' : ''}</div>
      <div class="field"><label for="d-name-${i}">Jméno psa <em>*</em></label><input id="d-name-${i}" name="pes" placeholder="celé jméno včetně chovatelské stanice" required><span class="msg">Vyplňte jméno psa.</span></div>
      <div class="field"><label for="d-call-${i}">Volací jméno</label><input id="d-call-${i}" name="volaci" placeholder="např. Brok"></div>
      <div class="field"><label for="d-breed-${i}">Plemeno <em>*</em></label><input id="d-breed-${i}" name="plemeno" placeholder="např. maďarský ohař krátkosrstý" required><span class="msg">Vyplňte plemeno.</span></div>
      <div class="field"><label for="d-birth-${i}">Datum narození psa</label><input id="d-birth-${i}" name="narozen" type="date"></div>
      <div class="field"><label for="d-sex-${i}">Pes / fena</label><select id="d-sex-${i}" name="pohlavi"><option value="">—</option><option>pes</option><option>fena</option></select></div>`;
    dogsBox.insertBefore(el, $('.addbtn', dogsBox));
    const x = $('.dogbox-x', el);
    if (x) x.onclick = () => { el.remove(); $$('.dogbox-h span', dogsBox).forEach((s, k) => (s.textContent = 'Pes ' + (k + 1))); };
  }
  const add = document.createElement('button');
  add.type = 'button'; add.className = 'addbtn'; add.textContent = '+ Přidat dalšího psa';
  add.onclick = addDog;
  dogsBox.appendChild(add);
  addDog();

  function validate(s) {
    let ok = true;
    $$('.field', steps[s]).forEach(f => f.classList.remove('err'));
    $$('[required]', steps[s]).forEach(inp => {
      const f = inp.closest('.field');
      let bad = inp.type === 'checkbox' ? !inp.checked : !inp.value.trim();
      if (!bad && inp.type === 'email') bad = !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(inp.value);
      if (!bad && inp.minLength > 0) bad = inp.value.length < inp.minLength;
      if (bad) { f.classList.add('err'); ok = false; }
    });
    if (s === 0) {
      const p1 = $('#f-pw'), p2 = $('#f-pw2');
      if (p2.value !== p1.value || !p2.value) { p2.closest('.field').classList.add('err'); ok = false; }
    }
    if (!ok) { const first = $('.err input, .err select, .err textarea', steps[s]); if (first) first.focus(); }
    return ok;
  }

  function go(n) {
    step = n;
    steps.forEach((s, i) => s.classList.toggle('on', i === n));
    prog.forEach((p, i) => { p.classList.toggle('on', i === n); p.classList.toggle('done', i < n); });
    back.hidden = n === 0;
    next.innerHTML = n === steps.length - 1 ? 'Odeslat registraci' : 'Pokračovat <svg class="arr" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" stroke="currentColor" stroke-width="1.4"/></svg>';
    const top = $('#reg').getBoundingClientRect().top + scrollY - 90;
    if (scrollY > top) scrollTo({ top, behavior: 'smooth' });
  }
  back.onclick = () => go(step - 1);

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!validate(step)) return;
    if (step < steps.length - 1) return go(step + 1);
    const fd = new FormData(form);
    const dogs = $$('.dogbox', dogsBox).map(b => {
      const v = (n) => $(`[name=${n}]`, b).value.trim();
      return `${v('volaci') ? v('volaci') + ' — ' : ''}${v('pes')} (${v('plemeno')})`;
    });
    const rows = [['Jméno', fd.get('jmeno')], ['E-mail', fd.get('email')], ['Telefon', fd.get('telefon')], ...dogs.map((d, i) => [`Pes ${i + 1}`, d]),
      ['Zájem', fd.getAll('zajem').join(', ') || '—'], ['Zkoušky', fd.get('zkousky') || '—']];
    $('#summary').innerHTML = rows.map(([k, v]) => `<div><span>${k}</span><b>${String(v).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]))}</b></div>`).join('');
    form.hidden = true; $('.progress').hidden = true;
    $('#done').classList.add('on');
    $('#reg').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  form.addEventListener('input', (e) => { const f = e.target.closest('.field'); if (f) f.classList.remove('err'); });
})();
