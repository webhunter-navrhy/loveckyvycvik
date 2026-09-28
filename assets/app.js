/* Lovecký výcvik — společné chování stránek (bez knihoven, nativní scroll) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* navigace: plné pozadí po odscrollování */
  const nav = $('#nav');
  const onScroll = () => nav && nav.classList.toggle('solid', scrollY > 40);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  /* mobilní menu */
  const burger = $('.burger');
  if (burger) {
    const menu = $('.drawer-menu');
    const toggle = (open) => {
      document.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', open);
      menu.setAttribute('aria-hidden', !open);
      document.documentElement.style.overflow = open ? 'hidden' : '';
    };
    burger.addEventListener('click', () => toggle(!document.body.classList.contains('menu-open')));
    $$('a', menu).forEach(a => a.addEventListener('click', () => toggle(false)));
    addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });
  }

  /* hero nadpis po slovech */
  $$('.hero h1 > span').forEach((line, li) => {
    const words = line.textContent.trim().split(/\s+/);
    line.innerHTML = words.map((w, i) => `<span class="w"><span style="animation-delay:${(0.25 + li * 0.18 + i * 0.08).toFixed(2)}s">${w}</span></span>`).join(' ');
  });

  /* odhalování při scrollu */
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('.rv, .clip').forEach(el => reduce ? el.classList.add('in') : io.observe(el));

  /* počítadla */
  const fmt = n => n.toLocaleString('cs-CZ').replace(/\s/g, ' ');
  const cio = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target; cio.unobserve(el);
      const to = +el.dataset.count; const from = to > 1900 ? to - 28 : 0;
      const t0 = performance.now(); const dur = 1600;
      const step = (t) => {
        const p = Math.min(1, (t - t0) / dur); const e = 1 - Math.pow(1 - p, 3);
        const v = Math.round(from + (to - from) * e);
        el.textContent = to > 1900 ? v : fmt(v);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.5 });
  if (!reduce) $$('[data-count]').forEach(el => cio.observe(el));

  /* náhled fotky u řádků výcviku */
  const prev = $('.preview');
  if (prev && matchMedia('(hover: hover) and (min-width: 768px)').matches) {
    const pimg = $('img', prev);
    let x = 0, y = 0, raf = 0;
    const move = () => { prev.style.transform = `translate(${x + 24}px, ${y - 110}px)`; raf = 0; };
    $$('.svc-row[data-img]').forEach(row => {
      row.addEventListener('mouseenter', () => { pimg.src = row.dataset.img; prev.classList.add('on'); });
      row.addEventListener('mouseleave', () => prev.classList.remove('on'));
      row.addEventListener('mousemove', e => { x = e.clientX; y = e.clientY; if (!raf) raf = requestAnimationFrame(move); });
    });
  }

  /* zkoušky: sticky fotka se mění podle aktivního bloku */
  const exams = $$('.exam');
  if (exams.length) {
    const imgs = $$('.exams-sticky img'); const cap = $('#exam-cap');
    const eio = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        const i = en.target.dataset.i;
        exams.forEach(x => x.classList.toggle('on', x === en.target));
        imgs.forEach(im => im.classList.toggle('on', im.dataset.i === i));
        if (cap) cap.textContent = $('.exam-abbr', en.target).textContent;
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    exams.forEach(x => eio.observe(x));
    exams[0].classList.add('on');
  }

  /* podnavigace: aktivní sekce */
  const sub = $$('.subnav a');
  if (sub.length) {
    const map = new Map(sub.map(a => [a.getAttribute('href').slice(1), a]));
    const sio = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        sub.forEach(a => a.classList.remove('on'));
        const a = map.get(en.target.id);
        if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' }); }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    map.forEach((a, id) => { const s = document.getElementById(id); if (s) sio.observe(s); });
  }

  /* kopírování čísla účtu */
  $$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Zkopírováno'; }
    catch { b.textContent = b.dataset.copy; }
    setTimeout(() => (b.textContent = 'Kopírovat'), 2200);
  }));

  /* novinky: starší příspěvky */
  const more = $('#more-posts');
  if (more) more.addEventListener('click', () => {
    $$('.hidden-post').forEach(p => { p.hidden = false; p.classList.add('in'); });
    more.remove();
  });
})();
