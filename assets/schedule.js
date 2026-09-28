/* Ukázkový rozvrh — generuje hodiny relativně k dnešnímu týdnu, aby návrh nikdy nevypadal zastarale.
   Typy hodin, místa a kapacity skupin odpovídají textům na webu; konkrétní časy a obsazenost jsou ilustrační. */
(() => {
  const PLACES = {
    neb: { name: 'Nebušice', full: 'Pozemek Nebušice, ulice Nad Habrovkou', map: 'https://mapy.cz/zakladni?q=50.107810,14.346598' },
    mra: { name: 'Hájovna Mrákavy', full: 'Hájovna Mrákavy, cca 20 km od Prahy', map: 'o-nas/#kde-cvicime' },
    kla: { name: 'Kladno – Kožova Hora', full: 'Kladno – Kožova Hora (umělá nora)', map: '' },
    hon: { name: 'Honitba u Prahy', full: 'Domluvená honitba poblíž Prahy — upřesníme u hodiny', map: '' },
    cech: { name: 'Restaurace U Čechů', full: 'Restaurace U Čechů (teorie bez psů)', map: '' },
  };
  const A = [
    [['17:00', '18:00', 'posl-mp', 'neb', 8], ['18:15', '19:15', 'posl-p', 'neb', 10]],
    [['09:30', '12:00', 'pz-vp', 'hon', 4], ['16:30', '17:30', 'skolka', 'neb', 6], ['17:45', '18:45', 'soc-z', 'neb', 6]],
    [['10:00', '12:00', 'zn', 'kla', 10], ['17:00', '18:30', 'aport-k', 'mra', 6]],
    [['09:00', '12:00', 'pz-mp', 'hon', 5], ['17:00', '19:00', 'barva-z', 'mra', 4]],
    [['18:00', '20:00', 'teorie', 'cech', 20]],
    [['08:30', '12:30', 'lz-a', 'hon', 5], ['13:30', '15:30', 'aport-z', 'mra', 6]],
    [['10:00', '11:00', 'downy', 'neb', 8]],
  ];
  const B = [
    [['16:00', '17:00', 'spec', 'neb', 6], ['17:15', '18:15', 'posl-mp', 'neb', 8], ['18:30', '19:30', 'posl-p', 'neb', 10]],
    [['09:30', '12:00', 'zv', 'hon', 6], ['16:30', '17:30', 'skolka', 'neb', 6], ['17:45', '18:45', 'soc-z', 'neb', 6]],
    [['17:00', '18:30', 'ovvr', 'mra', 6], ['18:45', '19:45', 'aport-u', 'mra', 6]],
    [['09:00', '12:00', 'pz-vp', 'hon', 4], ['17:00', '19:00', 'barva-p', 'mra', 3]],
    [],
    [['08:30', '12:00', 'lz-d', 'hon', 6], ['13:00', '15:00', 'svp', 'hon', 6]],
    [['09:00', '11:00', 'barva-u', 'mra', 6], ['11:30', '13:00', 'stopa', 'mra', 4]],
  ];
  const CAT = {
    posl: 'Poslušnost', aport: 'Aporty', zk: 'Příprava ke zkouškám', barva: 'Barvy a stopy', teorie: 'Teorie', sezn: 'Seznamovací procházka',
  };
  const catOf = (id) => {
    if (/^(skolka|soc-z|posl|downy|spec)/.test(id)) return 'posl';
    if (id.startsWith('aport')) return 'aport';
    if (/^(barva|stopa)/.test(id)) return 'barva';
    if (id === 'teorie') return 'teorie';
    if (id === 'sezn') return 'sezn';
    return 'zk';
  };
  const hash = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; };
  const monday = (d) => { const x = new Date(d); x.setHours(0, 0, 0, 0); const wd = (x.getDay() + 6) % 7; x.setDate(x.getDate() - wd); return x; };
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const at = (day, hm) => { const [h, m] = hm.split(':').map(Number); const x = new Date(day); x.setHours(h, m, 0, 0); return x; };
  const weekNo = (d) => Math.floor((monday(d) - new Date(2026, 0, 5)) / 6048e5);

  function week(offset = 0) {
    const start = monday(new Date()); start.setDate(start.getDate() + offset * 7);
    const tpl = (Math.abs(weekNo(start)) % 2) ? B : A;
    const out = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(start); day.setDate(start.getDate() + i);
      const slots = tpl[i].slice();
      if (i === 3 && day.getDate() <= 7) slots.unshift(['16:00', '17:00', 'sezn', 'neb', 2]); // první týden v měsíci
      slots.forEach(([s, e, id, pl, cap]) => {
        const key = `${iso(day)}_${s}_${id}`;
        const r = hash(key);
        let taken = Math.min(cap + 2, Math.floor(r * (cap + 2.2)));
        if (id === 'sezn') taken = r > 0.5 ? 1 : 0;
        out.push({ key, id, cat: catOf(id), day, start: at(day, s), end: at(day, e), s, e, place: pl, cap, taken });
      });
    }
    return { start, lessons: out };
  }

  const DAYS = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne'];
  const DAYS_LONG = ['pondělí', 'úterý', 'středa', 'čtvrtek', 'pátek', 'sobota', 'neděle'];
  const dnum = (d) => `${d.getDate()}. ${d.getMonth() + 1}.`;
  const wlabel = (start) => { const e = new Date(start); e.setDate(e.getDate() + 6); return `${dnum(start)} – ${dnum(e)} ${e.getFullYear()}`; };

  /* stav hodiny vzhledem k přihláškám uživatele */
  function status(L, mine) {
    const now = new Date();
    const inC = mine ? Object.values(mine).filter(v => v === 'in').length : 0;
    const waitC = mine ? Object.values(mine).filter(v => v === 'wait').length : 0;
    const taken = Math.min(L.taken, L.cap) + inC; // kolik míst je obsazeno
    const queue = Math.max(0, L.taken - L.cap) + waitC;
    const closed = L.end < now || (L.start - now) < 2 * 3600e3;
    let st = closed ? 'closed' : (taken >= L.cap ? 'wait' : 'free');
    let me = inC ? 'booked' : (waitC ? 'waitme' : '');
    return { st, me, taken: Math.min(taken, L.cap), queue, free: Math.max(0, L.cap - taken), closed };
  }

  window.LVS = { week, status, PLACES, CAT, catOf, DAYS, DAYS_LONG, dnum, wlabel, iso };
})();
