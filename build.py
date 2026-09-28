#!/usr/bin/env python3
"""Generátor návrhu webu loveckyvycvik.cz — Lovecký výcvik psích plemen (Ing. Zuzana Čechová).

Obsah je převzatý ze stávajícího webu (texty opravené jen o překlepy).
Data: src/data.json (novinky, kalendář, absolventi, cvičenci — vytěženo ze starého webu),
      src/lessons.json (popisy hodin výcviku).
Spuštění: python3 build.py → vygeneruje index.html + podstránky, CSS/JS s ?v=hash.
"""
import hashlib, html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, 'src/data.json'), encoding='utf-8'))
LESSONS = json.load(open(os.path.join(ROOT, 'src/lessons.json'), encoding='utf-8'))
E = html.escape
TODAY = (2026, 9, 28)  # stav obsahu starého webu


def ver(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


# ---------- opravy překlepů z původního webu ----------
TYPOS = {
    'víkednu': 'víkendu', 'víkednové': 'víkendové', 'víkednová': 'víkendová', 'víknedu': 'víkendu',
    'víkndové': 'víkendové', 'gratlujeme': 'gratulujeme', 'podzimnních': 'podzimních', 'doknčila': 'dokončila',
    'Držííme': 'Držíme', 'ppondělí': 'pondělí', 'vyvědčení': 'vysvědčení', 'jetšě': 'ještě',
    'předevdlo': 'předvedlo', 'nněkolik': 'několik', 'cvivičí': 'cvičí', 'strartoval': 'startoval',
    'kalnedáři': 'kalendáři', 'intezivk': 'intenzivk', 'intnzivka': 'intenzivka', 'Honita': 'Honitba',
    'Opakovaní po zimě': 'Opakování po zimě', 'přihlaška': 'přihláška', 'Příprava na  PZ': 'Příprava na PZ',
    'indiviuální': 'individuální', 'načekací': 'na čekací', 'porozumnění': 'porozumění', 'pokorčilí': 'pokročilí',
    'Permamentka': 'Permanentka', 'písněte': 'pípněte', 'Korespondenčí': 'Korespondenční',
    'Restuarace': 'Restaurace', 'napiště': 'napište', 'pakrujte': 'parkujte', 'vyjít vyříct': 'vyjít vstříc',
    'exému': 'ekzému', 'móře': 'moře', 'na tolik': 'natolik', 'zkoušách': 'zkouškách', 'uspěšným': 'úspěšným',
    'dnešním světe': 'dnešním světě', 'píš´talka': 'píšťalka', 'začtečník': 'začátečník', 'začáteník': 'začátečník',
    'Idviduální': 'Individuální', 'Idividuální': 'Individuální', 'nerozhoduje.': 'nerozhoduje', 'pomůžeme Vašemu': 'pomůžeme Vašemu',
    ' ,': ',', 'ZDE': 'zde', '"U"': '„U“', 'Tuto službu jsme zajistit': 'Tuto službu jsme schopni zajistit',
}


def fix(t):
    for a, b in TYPOS.items():
        t = t.replace(a, b)
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'"([^"]+)"', r'„\1“', t)
    t = re.sub(r'„U“(?=\S)', '„U“ ', t)
    return t


def rel(depth):
    return '../' * depth


# ---------- sdílené prvky ----------
NAV = [('vycvik/', 'Výcvik'), ('rozvrh/', 'Rozvrh'), ('akce/', 'Kalendář akcí'), ('cenik/', 'Ceník'),
       ('klienti/', 'Klienti'), ('o-nas/', 'O nás'), ('novinky/', 'Novinky'), ('kontakt/', 'Kontakt')]

ICON = {
    'arr': '<svg class="arr" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" stroke="currentColor" stroke-width="1.4"/></svg>',
    'arr-ur': '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" stroke="currentColor" stroke-width="1.4"/></svg>',
    'info': '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="8.3" stroke="currentColor" stroke-width="1.4"/><path d="M10 9v5M10 6.2v.1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    'search': '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="8.5" cy="8.5" r="6" stroke="currentColor" stroke-width="1.5"/><path d="m13 13 4.5 4.5" stroke="currentColor" stroke-width="1.5"/></svg>',
    'doc': '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M4 1.5h5L12.5 5v9.5h-8.5z" stroke="currentColor" stroke-width="1.3"/><path d="M8.5 1.5V5.5h4" stroke="currentColor" stroke-width="1.3"/></svg>',
    'check': '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" stroke="currentColor" stroke-width="2"/></svg>',
}


def logo(depth, cls=''):
    r = rel(depth)
    return (f'<img class="lg lg-on-dark {cls}" src="{r}assets/logo-light.svg" alt="Lovecký výcvik psích plemen" width="120" height="125">'
            f'<img class="lg lg-on-light {cls}" src="{r}assets/logo-color.svg" alt="" aria-hidden="true" width="120" height="125">')


def head(title, desc, depth, extra=''):
    r = rel(depth)
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#062A09">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{r}assets/img/hero.jpg">
<link rel="icon" href="{r}assets/logo-color.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..600,0..100;1,9..144,300..600,0..100&family=Hanken+Grotesk:wght@300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/style.css?v={ver('assets/style.css')}">
{extra}</head>
'''


def nav(depth, active):
    r = rel(depth)
    links = ''.join(
        f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a></li>' for h, t in NAV)
    mob = ''.join(f'<li><a href="{r}{h}">{t}<small>0{i + 1}</small></a></li>' for i, (h, t) in enumerate(NAV))
    return f'''<header class="nav" id="nav">
  <div class="wrap nav-in">
    <a class="nav-logo" href="{r or './'}" aria-label="Lovecký výcvik — úvod">{logo(depth)}</a>
    <ul class="nav-links">{links}</ul>
    <div class="nav-cta">
      <a class="btn btn--ghost" href="{r}rozvrh/">Přihlásit se</a>
      <a class="btn" href="{r}registrace/">Registrace</a>
    </div>
    <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="drawer-menu" aria-hidden="true">
  <ul>{mob}</ul>
  <div class="drawer-foot"><a class="btn" href="{r}registrace/">Registrace</a><a class="btn btn--ghost" href="{r}rozvrh/">Přihlásit se</a><a class="btn btn--ghost" href="tel:+420777717271">777 717 271</a></div>
</div>
'''


def footer(depth, cta=True):
    r = rel(depth)
    c = ''
    if cta:
        c = f'''<section class="section dark cta">
  <div class="cta-mark" aria-hidden="true"><img src="{r}assets/logo-light.svg" alt=""></div>
  <div class="wrap cta-grid">
    <div class="rv">
      <span class="eyebrow">Jak s námi začít</span>
      <h2 style="margin-top:1.2rem">Napište nám pár informací o&nbsp;Vás, o&nbsp;Vašem pejskovi <em>a&nbsp;Vašich plánech.</em></h2>
      <a class="cta-mail" href="mailto:info@loveckyvycvik.cz">info@loveckyvycvik.cz</a>
    </div>
    <dl class="cta-side rv" style="--d:.15s">
      <div><dt>Telefon</dt><dd><a href="tel:+420777717271">+420 777 717 271</a></dd></div>
      <div><dt>Kde cvičíme</dt><dd>Nebušice · Hájovna Mrákavy · honitby poblíž Prahy</dd></div>
      <div><dt>Další krok</dt><dd><a class="link" href="{r}registrace/">Jak s námi začít {ICON['arr']}</a></dd></div>
    </dl>
  </div>
</section>'''
    return c + f'''
<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <img class="foot-logo" src="{r}assets/logo-light.svg" alt="Lovecký výcvik psích plemen" width="110" height="115">
        <p style="margin-top:1.4rem;max-width:34ch">Výcvik, cvičení a příprava k loveckým zkouškám všech loveckých plemen.</p>
        <div class="foot-partners">
          <a class="partner" href="https://www.lvshop.cz" target="_blank" rel="noopener"><span><b>LV Shop</b><small>pomůcky k prodeji · lvshop.cz</small></span></a>
          <a class="partner" href="https://www.facebook.com/Odczechu" target="_blank" rel="noopener"><span><b>Chovatelská stanice Od Czechu</b><small>na Facebooku</small></span></a>
        </div>
      </div>
      <div>
        <h4>Výcvik</h4>
        <ul>
          <li><a href="{r}vycvik/#seznamovaci-prochazka">Seznamovací procházka</a></li>
          <li><a href="{r}vycvik/#poslusnost">Skupinový výcvik poslušnosti</a></li>
          <li><a href="{r}vycvik/#aporty">Aporty</a></li>
          <li><a href="{r}vycvik/#zkousky">Příprava k loveckým zkouškám</a></li>
          <li><a href="{r}vycvik/#individualni">Individuální výcvik</a></li>
          <li><a href="{r}sluzby/">Výstavy a poradenství</a></li>
          <li><a href="{r}vycvik/#teorie">Teorie</a></li>
        </ul>
      </div>
      <div>
        <h4>Pro cvičence</h4>
        <ul>
          <li><a href="{r}registrace/">Informace k registraci</a></li>
          <li><a href="{r}rozvrh/">Rozvrh cvičení</a></li>
          <li><a href="{r}akce/">Kalendář akcí</a></li>
          <li><a href="{r}cenik/">Ceník</a></li>
          <li><a href="{r}klienti/">Cvičí u nás · Absolventi</a></li>
          <li><a href="{r}kontakt/#dokumenty">Předpisy, řády, termíny</a></li>
          <li><a href="https://loveckyvycvikcz.rajce.idnes.cz/" target="_blank" rel="noopener">Galerie na Rajčeti</a></li>
        </ul>
      </div>
      <div>
        <h4>Kontakt</h4>
        <ul>
          <li>LoveckyVycvik s.r.o.</li>
          <li>Kamenné Žehrovice 37, 273 01</li>
          <li>IČO: 225 44 496</li>
          <li><a href="mailto:info@loveckyvycvik.cz">info@loveckyvycvik.cz</a></li>
          <li><a href="tel:+420777717271">+420 777 717 271</a></li>
          <li><a href="https://www.facebook.com/loveckyvycvik.cz/" target="_blank" rel="noopener">Facebook</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom"><span>© 2026 LoveckyVycvik s.r.o.</span><span>Návrh nového webu · ukázka</span></div>
  </div>
</footer>
<div class="preview" aria-hidden="true"><img alt=""></div>
<script src="{r}assets/app.js?v={ver('assets/app.js')}" defer></script>
'''


def page(path, title, desc, body, active='', depth=1, light=False, scripts='', cta=True):
    doc = head(title, desc, depth) + f'<body class="{"page-light" if light else ""}">\n' + nav(depth, active) + '<main>\n' + body + '\n</main>\n' + footer(depth, cta) + scripts + '\n</body>\n</html>\n'
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(doc)


def img(depth, name, alt, cls='', eager=False, small=False):
    r = rel(depth)
    src = f'{r}assets/img/{name}{"-s" if small else ""}.jpg'
    srcset = f' srcset="{r}assets/img/{name}-s.jpg 900w, {r}assets/img/{name}.jpg 1600w" sizes="(max-width: 767px) 100vw, 60vw"' if not small else ''
    return f'<img src="{src}"{srcset} alt="{E(alt)}" class="{cls}"{" loading=\"lazy\"" if not eager else " fetchpriority=\"high\""} decoding="async">'


def phead(depth, eyebrow, h1, lead='', photo=None, crumbs=''):
    r = rel(depth)
    cr = f'<nav class="crumbs" aria-label="Drobečková navigace"><a href="{r}">Úvod</a><span>/</span><span>{crumbs or eyebrow}</span></nav>'
    if photo:
        return f'''<section class="phead phead--img">{img(depth, photo, '', eager=True)}
  <div class="wrap">{cr}<h1 class="rv in">{h1}</h1>{f'<p class="phead-lead">{lead}</p>' if lead else ''}</div></section>'''
    return f'''<section class="phead"><div class="wrap">{cr}<h1>{h1}</h1>{f'<p class="phead-lead">{lead}</p>' if lead else ''}</div></section>'''


# ---------- katalog hodin ----------
PRICE = {
    'Školička pro štěňátka': ('250 Kč', ''), 'Socializace, výchova – začátečníci': ('250 Kč', ''),
    'Poslušnost - mírně pokročilí': ('250 Kč', ''), 'Poslušnost - pokročilí': ('250 Kč', ''),
    'Downy – úvodní hodina': ('250 Kč', ''), 'Speciální socializační výcvik': ('400 Kč', ''),
    'Aporty – úvodní hodina': ('', ''), 'Aporty – kozlík': ('250 Kč', ''), 'Aporty – zvěř': ('350 Kč', ''),
    'Příprava na zkoušky z norování ZN': ('100 Kč', ''), 'Příprava na zkoušky vloh ZV': ('400 Kč', ''),
    'Příprava na ověřování vrozených vlastností retrívrů OVVR': ('350 Kč', ''),
    'Příprava na podzimní zkoušky PZ – velké pole': ('500 Kč', ''), 'Příprava na podzimní zkoušky PZ – malé pole': ('500 Kč', ''),
    'Příprava na speciální vodní práce SVP': ('', ''), 'Příprava na lesní zkoušky LZ – drobné disciplíny': ('300 Kč', ''),
    'Příprava na lesní zkoušky LZ – aportovací disciplíny': ('400 Kč', ''),
    'Práce na barvě, stopě – úvodní hodina': ('350 Kč', ''), 'Práce na barvě – začátečníci': ('400 Kč', ''),
    'Práce na barvě – pokročilí': ('400 Kč', ''), 'Práce na barvě, stopě – speciál': ('', ''), 'Práce na stopě': ('400 Kč', ''),
}
LID = {  # id pro rozvrh
    'Školička pro štěňátka': 'skolka', 'Socializace, výchova – začátečníci': 'soc-z', 'Poslušnost - mírně pokročilí': 'posl-mp',
    'Poslušnost - pokročilí': 'posl-p', 'Downy – úvodní hodina': 'downy', 'Speciální socializační výcvik': 'spec',
    'Aporty – úvodní hodina': 'aport-u', 'Aporty – kozlík': 'aport-k', 'Aporty – zvěř': 'aport-z',
    'Příprava na zkoušky z norování ZN': 'zn', 'Příprava na zkoušky vloh ZV': 'zv', 'Příprava na ověřování vrozených vlastností retrívrů OVVR': 'ovvr',
    'Příprava na podzimní zkoušky PZ – velké pole': 'pz-vp', 'Příprava na podzimní zkoušky PZ – malé pole': 'pz-mp',
    'Příprava na speciální vodní práce SVP': 'svp', 'Příprava na lesní zkoušky LZ – drobné disciplíny': 'lz-d',
    'Příprava na lesní zkoušky LZ – aportovací disciplíny': 'lz-a', 'Práce na barvě, stopě – úvodní hodina': 'barva-u',
    'Práce na barvě – začátečníci': 'barva-z', 'Práce na barvě – pokročilí': 'barva-p', 'Práce na barvě, stopě – speciál': 'barva-s',
    'Práce na stopě': 'stopa',
}
NICE = {'Poslušnost - mírně pokročilí': 'Poslušnost – mírně pokročilí', 'Poslušnost - pokročilí': 'Poslušnost – pokročilí'}


def lessons_all():
    out = []
    for grp, items in LESSONS.items():
        for L in items:
            f = {k: fix(v) for k, v in L['fields'].items()}
            name = NICE.get(L['name'], L['name'])
            out.append({'id': LID[L['name']], 'group': grp, 'name': name, 'price': PRICE.get(L['name'], ('', ''))[0], 'f': f})
    return out


ALL_LESSONS = lessons_all()
WEATHER = 'S ohledem na počasí: misku s vodou, obleček pro krátkosrsté psy + vhodné sportovní oblečení a obuv.'


def lesson_card(L, depth):
    f = L['f']
    order = ['Věk', 'Skupina', 'Plemeno', 'Předchozí výcvik', 'Pomůcky', 'Předmět cvičení', 'Místo cvičení']
    dl = ''.join(f'<dt>{k}</dt><dd>{E(f[k])}</dd>' for k in order if f.get(k))
    price = f'<div class="lesson-price">{L["price"]}<small>cena lekce</small></div>' if L['price'] else '<div class="lesson-price"><small>cena dle rozvrhu</small></div>'
    return f'''<article class="lesson rv" id="{L['id']}">
  <div class="lesson-top"><h3>{E(L['name'])}</h3>{price}</div>
  <dl>{dl}</dl>
  <div class="lesson-foot"><a class="btn btn--sm btn--dark" href="{rel(depth)}rozvrh/?typ={L['id']}">Termíny v rozvrhu {ICON['arr']}</a></div>
</article>'''


# ======================================================================
#  DOMŮ
# ======================================================================
def build_home():
    d = 0
    news0 = DATA['news'][0]
    wins = [
        'Na VZ ve II. ceně uspěla kraťaska Gréta.',
        'Na LZ v I. ceně zvládly zkoušky NDO Beggy a MOK Temi, která navíc obsadila krásné 3. místo.',
        'Na VP v I. ceně obstála NDO Stella.',
        'Na PZ v I. ceně uspěli maďarští ohaři West a Dolphin, kteří tímto splnili také poslední podmínku chovnosti.',
        'Na ZN obstál jezevčík Fanda.',
        'Na VZ ostatních plemen v I. ceně obstála parsonka Judy, která s námi byla na víkendu v Kašperkách.',
    ]
    # vybraní absolventi s fotkou a výsledky
    pick = []
    for a in DATA['absolventi']:
        if a['img'] and len(a['results']) >= 3:
            pick.append(a)
    pick = pick[::max(1, len(pick) // 10)][:10]
    dogs = ''.join(f'''<article class="dog"><div class="dog-img"><img src="assets/abs/{hashlib.md5(a['img'].encode()).hexdigest()[:12]}.jpg" alt="{E(fix(a['name']))}" loading="lazy"></div>
<div class="dog-body"><b>{E(fix(a['name']))}</b><small>{E(fix(a['owner']))}</small><div class="dog-res">{''.join(f'<span>{E(fix(x))}</span>' for x in a['results'][:4])}</div></div></article>''' for a in pick)

    svc = [
        ('Seznamovací procházka', 'vycvik/#seznamovaci-prochazka', 'les', 'Popovídáme, probereme vaše představy a seznámíme se s vaším pejskem. Podmínka pro vstup do výcvikových hodin.', 'zdarma', ''),
        ('Skupinový výcvik poslušnosti', 'vycvik/#poslusnost', 'stene', 'I lovecký pes musí být vychovaným rodinným společníkem. Od školičky pro štěňátka po pokročilé.', '250 Kč', 'za lekci'),
        ('Aporty', 'vycvik/#aporty', 'aport-bazant', 'Výcvik v přinášení — základ práce loveckého psa, především plemen ohařů a retrívrů.', '250–350 Kč', 'za lekci'),
        ('Příprava k loveckým zkouškám', 'vycvik/#zkousky', 'pole', 'ZN, ZV, OVVR, PZ, SVP, LZ — výcvik pro jednotlivé typy zkoušek dle platných zkušebních řádů.', '100–500 Kč', 'za lekci'),
        ('Práce na barvě a stopě', 'vycvik/#barvy', 'cesta', 'Od úvodní hodiny bez psa po práci na starších a složitějších pobarvených stopách.', '350–400 Kč', 'za lekci'),
        ('Individuální výcvik', 'vycvik/#individualni', 'kontakt-psa', 'Když vám nevyhovují termíny, máte háravou fenku nebo potřebujete doladit disciplíny těsně před zkouškami.', 'dle dohody', ''),
        ('Výstavy a poradenství', 'sluzby/', 'vystava', 'Příprava na výstavy, předvedení psa, výběr štěňátka i individuální poradenství.', 'od 350 Kč', ''),
        ('Teorie', 'vycvik/#teorie', 'teorie', 'Zkušební řády, výstavní předpisy a úskalí jednotlivých disciplín. Bez psů, se zápisníkem a tužkou.', '300 Kč', 'za lekci'),
    ]
    svc_html = ''.join(f'''<a class="svc-row rv" href="{h}" data-img="assets/img/{im}-s.jpg">
  <span class="svc-n">{i + 1:02d}</span><h3>{t}</h3><p>{p}</p>
  <span class="svc-price"><b>{pr}</b><small>{u}</small></span><span class="svc-arr">{ICON['arr-ur']}</span></a>''' for i, (t, h, im, p, pr, u) in enumerate(svc))

    exams = [
        ('ZN', 'nora', 'Zkoušky z norování', 'Nácvik bezkontaktního norování na umělé noře (králík, liška). Cvičení Kladno – Kožova Hora.', ['od 6 měsíců', 'norníci — jezevčíci a teriéři', 'skupina neomezeno']),
        ('ZV', 'vlohy', 'Zkoušky vloh', 'Práce na divoké či vypouštěné zvěři v terénu. U ohařů nutné zvládnutí povelu down, ovladatelnost na píšťalku a základní poslušnost.', ['od 6 měsíců', 'plemeno nerozhoduje', 'do šesti psů']),
        ('OVVR', 'retrivr', 'Ověřování vrozených vlastností retrívrů', 'Příprava na zkoušky dle zkušebních řádů, zvěř pro dohledávání bude zajištěna.', ['od 6 měsíců', 'retrívři', 'do šesti psů']),
        ('PZ', 'pole', 'Podzimní zkoušky — velké a malé pole', 'Práce v terénu na divoké a vypouštěné zvěři, nácvik chování po výstřelu, dohledávky, vlečky, přinášení teplé zvěře. Vypouštěnou zvěř a střelce zajistíme.', ['od 9 měsíců', 'plemeno nerozhoduje', 'do čtyř / pěti psů']),
        ('SVP', 'vodni-prace', 'Speciální vodní práce', 'Ovladatelnost na píšťalku a perfektní zvládnutí výcviku v přinášení (kozlík). Zvěř bude zajištěna.', ['od 9 měsíců', 'plemeno nerozhoduje', 'do šesti psů']),
        ('LZ', 'liska', 'Lesní zkoušky', 'Drobné a aportovací disciplíny zvlášť — od kontaktu psa s vůdcem po těžší aporty, vlečky a dohledávky.', ['od 9 měsíců', 'plemeno nerozhoduje', 'do pěti / šesti psů']),
    ]
    ex_imgs = ''.join(f'<img src="assets/img/{im}.jpg" alt="" data-i="{i}" class="{"on" if i == 0 else ""}" loading="lazy">' for i, (_, im, *_r) in enumerate(exams))
    ex_list = ''.join(f'''<div class="exam" data-i="{i}">
  <div class="exam-img-m"><img src="assets/img/{im}-s.jpg" alt="" loading="lazy"></div>
  <div class="exam-abbr">{ab}</div><h3>{t}</h3><p>{p}</p>
  <div class="exam-meta">{''.join(f'<span class="chip">{c}</span>' for c in chips)}</div></div>''' for i, (ab, im, t, p, chips) in enumerate(exams))

    body = f'''
<section class="hero">
  <div class="hero-media">{img(0, 'hero', 'Hrubosrstý ohař přináší bažanta', eager=True)}</div>
  <div class="wrap hero-in">
    <div>
      <div class="hero-status fade-in" style="animation-delay:.2s"><span class="pulse"></span>Kapacita je naplněna — nové zájemce o výcvik nyní nebereme</div>
      <h1><span class="l1">Lovecký výcvik</span><span class="l2">psích plemen</span></h1>
      <p class="hero-lead fade-in" style="animation-delay:.9s">Výcvik, cvičení a příprava k loveckým zkouškám všech loveckých plemen. Cvičíme tak, aby byl spokojený jak páneček, tak pes — a aby byly vidět výsledky.</p>
      <div class="hero-actions fade-in" style="animation-delay:1.05s">
        <a class="btn" href="rozvrh/">Rozvrh cvičení {ICON['arr']}</a>
        <a class="btn btn--ghost" href="registrace/">Jak s námi začít</a>
      </div>
    </div>
    <aside class="next-card fade-in" style="animation-delay:1.25s" aria-label="Nejbližší hodiny">
      <h2>Nejbližší hodiny <a href="rozvrh/">celý rozvrh →</a></h2>
      <div id="next-list"></div>
      <p class="demo-note">Ukázka nového rozvrhu — termíny jsou ilustrační.</p>
    </aside>
  </div>
  <div class="scroll-cue" aria-hidden="true"></div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">
  {''.join('<span>' + ''.join(f'{w}<i></i>' for w in ['Poslušnost', 'Aporty', 'Práce na barvě', 'Stopy', 'Zkoušky vloh', 'Podzimní zkoušky', 'Vodní práce', 'Lesní zkoušky', 'Norování', 'Výstavy', 'Teorie']) + '</span>' for _ in range(2))}
</div></div>

<section class="section intro">
  <div class="wrap intro-grid">
    <div>
      <span class="eyebrow rv">Jak cvičíme</span>
      <p class="intro-quote rv" style="--d:.1s"><span class="q">„</span>Cvičíme tak, aby byl spokojený jak <em>páneček, tak pes</em> a&nbsp;aby byly vidět výsledky.<span class="q">“</span></p>
      <div class="intro-facts">
        <div class="fact rv"><b>1997</b><span>kynologii se Zuzana Čechová věnuje od roku</span></div>
        <div class="fact rv" style="--d:.1s"><b>2005</b><span>od tohoto roku výcvik loveckých psů</span></div>
        <div class="fact rv" style="--d:.2s"><b>0 Kč</b><span>seznamovací procházka pro nové zájemce je zdarma</span></div>
      </div>
    </div>
    <div class="intro-side">
      <div class="intro-photo clip">{img(0, 'kontakt-psa', 'Vůdkyně s ohařem na poli')}</div>
      <div class="intro-text rv">
        <p>K našim svěřencům se snažíme přistupovat individuálně s přihlédnutím k povaze daného jedince i jeho majitele. Postup výcviku konzultujeme s majitelem, demonstrujeme na našich hafanech a dokládáme výsledky ze zkoušek a z praxe.</p>
        <p class="muted">Z mnoha majitelů pejsků, kteří s námi začínali, jsou nyní zkušení kynologové, chovatelé, vůdci, myslivci či pouze zodpovědní a spokojení majitelé psů.</p>
        <p><a class="link" href="o-nas/">Kdo jsme {ICON['arr']}</a></p>
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="eyebrow rv">Výcvik</span><h2 class="rv" style="--d:.08s">Od školičky pro štěňátka <em>po lovecké zkoušky</em></h2></div>
      <p class="rv" style="--d:.16s">Hodiny jsou rozdělené podle úrovně psa i typu zkoušek. Náplň, pomůcky a cenu každé hodiny najdete u výcviku i přímo v rozvrhu.</p>
    </div>
    <div class="svc">{svc_html}</div>
  </div>
</section>

<section class="section exams" id="zkousky">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="eyebrow rv">Příprava k loveckým zkouškám</span><h2 class="rv" style="--d:.08s">Z gauče <em>do honitby.</em></h2></div>
      <p class="rv" style="--d:.16s">V menších skupinách dojíždíme do terénů a míst, která jsou pro výcvik vhodná. Vůdce i pejsky seznamujeme s průběhem zkoušek, zkušebními řády a učíme se jednotlivé disciplíny.</p>
    </div>
    <div class="exams-grid">
      <div><div class="exams-sticky">{ex_imgs}<div class="exams-cap"><span>Hodiny dle platných ZŘ</span><b id="exam-cap">ZN</b></div></div></div>
      <div class="exam-list">{ex_list}
        <p style="margin-top:2.4rem"><a class="btn" href="vycvik/#zkousky">Všechny přípravy a pomůcky {ICON['arr']}</a></p>
      </div>
    </div>
  </div>
</section>

<section class="section alt">
  <div class="wrap book-grid">
    <div>
      <span class="eyebrow rv">Rozvrh a přihlašování</span>
      <h2 class="rv" style="font-size:var(--h2);margin-top:1.1rem;--d:.08s">Na hodinu se přihlásíte <em>na dvě kliknutí.</em></h2>
      <p class="rv muted" style="margin-top:1.2rem;max-width:46ch;--d:.14s">Hodiny do rozvrhu vypisujeme každý týden v neděli/pondělí. Hlaste se prosím na hodiny pro vás určené — a pokud nemůžete dorazit, odhlaste se.</p>
      <ol class="steps">
        <li class="rv"><div><b>Zašlete e-mail</b><p>S pár informacemi o Vás, o Vašem pejskovi a Vašich plánech a představách.</p></div></li>
        <li class="rv" style="--d:.08s"><div><b>Seznamovací procházka</b><p>Pokud přibíráme nové klienty, domluvíme první individuální schůzku a probereme systém našeho výcviku.</p></div></li>
        <li class="rv" style="--d:.16s"><div><b>Registrace do systému</b><p>Po našem potvrzení se vám otevře rozvrh a můžete se hlásit na hodiny.</p></div></li>
      </ol>
      <p class="rv" style="margin-top:1.6rem"><a class="link" href="registrace/">Informace k registraci {ICON['arr']}</a></p>
    </div>
    <div class="board rv" style="--d:.1s">
      <div class="board-float"><span class="st st--booked"></span>Přihlášeno: <b>Brok</b> · Aporty – kozlík</div>
      <div class="board-top"><b id="board-week">Tento týden</b>
        <div class="legend"><span class="st st--free">volno</span><span class="st st--wait">čekací listina</span><span class="st st--closed">uzavřeno</span></div></div>
      <div class="board-days" id="board-days"></div>
      <div class="board-foot"><span>Ukázka — klikněte na hodinu v rozvrhu</span><a class="btn btn--sm btn--dark" href="rozvrh/">Otevřít rozvrh {ICON['arr']}</a></div>
    </div>
  </div>
</section>

<section class="section dark results">
  <div class="wrap">
    <div class="results-top">
      <div><span class="eyebrow rv">Úspěchy našich oveček</span><h2 class="rv" style="font-size:var(--h2);margin-top:1.1rem;--d:.08s">Nejlepší referencí jsou hafani, kteří dělají <em style="color:var(--lime-2)">páníkům radost.</em></h2></div>
      <p class="rv muted" style="--d:.16s;max-width:46ch">A také úspěchy našich odchovánků na zkouškách. Ze spousty psů, kteří by strávili jistě spokojený život „na gauči“, se stali právoplatní výborní pomocníci při lovu.</p>
    </div>
    <div class="counters">
      <div class="counter rv"><b data-count="{len(DATA['cvicenci'])}">{len(DATA['cvicenci'])}</b><span>psů u nás pravidelně cvičí v roce 2026</span></div>
      <div class="counter rv" style="--d:.1s"><b data-count="{len(DATA['absolventi'])}">{len(DATA['absolventi'])}</b><span>absolventů v přehledu úspěšných od roku 2018</span></div>
      <div class="counter rv" style="--d:.2s"><b data-count="{len(DATA['absolventi_old'])}">{len(DATA['absolventi_old'])}</b><span>dalších v přehledu absolventů do roku 2018</span></div>
    </div>
    <div class="wins">
      <div class="rv"><h3>Úspěšný víkend na všech frontách!</h3><p class="wins-date">Novinky · {news0['date']}</p><p style="margin-top:1.4rem"><a class="link" href="novinky/">Všechny novinky {ICON['arr']}</a></p></div>
      <ul>{''.join(f'<li class="rv" style="--d:{i * .06:.2f}s">{E(w)}</li>' for i, w in enumerate(wins))}</ul>
    </div>
  </div>
  <div class="dogs" aria-label="Naši absolventi">{dogs}</div>
  <div class="wrap" style="margin-top:2rem"><a class="btn btn--ghost" href="klienti/">Galerie úspěšných absolventů {ICON['arr']}</a></div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="eyebrow rv">Kalendář akcí 2026</span><h2 class="rv" style="--d:.08s">Víkendy, tábory <em>a přednášky</em></h2></div>
      <p class="rv" style="--d:.16s">Pobytové přípravy na zkoušky, výcvikový tábor, semináře i přednášky pro všechny majitele a chovatele psů. Počet psů je vždy omezen.</p>
    </div>
    <div class="events">
      <a class="ev-feature rv" href="akce/#tabor">{img(0, 'tabor', 'Účastníci výcvikového tábora se psy')}
        <div class="ev-feature-body"><span class="tag">18.–25. 9. 2026</span><h3>Výcvikový tábor</h3><p>Lučkovice. Pro všechny úrovně výcviku.</p></div></a>
      <ul class="ev-list" id="home-events"></ul>
    </div>
  </div>
</section>

<section class="section alt" style="padding-top:clamp(4rem,8vw,7rem)">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="eyebrow rv">Galerie</span><h2 class="rv" style="--d:.08s">Z výcviku <em>a zkoušek</em></h2></div>
      <p class="rv" style="--d:.16s">Fotečky z víkendů, táborů a zkoušek průběžně přidáváme do galerie na Rajčeti. <a class="link" href="https://loveckyvycvikcz.rajce.idnes.cz/" target="_blank" rel="noopener">Otevřít galerii {ICON['arr-ur']}</a></p>
    </div>
    <div class="bento">
      <figure class="b1 rv">{img(0, 'vodni-prace', 'Pes skáče do vody')}<figcaption>Vodní práce</figcaption></figure>
      <figure class="b2 rv" style="--d:.08s">{img(0, 'vystava', 'Oceněné psy na výstavě', small=True)}<figcaption>Výstavy</figcaption></figure>
      <figure class="b3 rv" style="--d:.16s">{img(0, 'nastup', 'Nástup psů a vůdců na zkouškách', small=True)}<figcaption>Zkoušky</figcaption></figure>
      <figure class="b4 rv">{img(0, 'teorie', 'Výklad s jezevčíkem', small=True)}<figcaption>Teorie v praxi</figcaption></figure>
      <figure class="b5 rv" style="--d:.08s">{img(0, 'voditko', 'Malý münsterlandský ohař na vodítku', small=True)}<figcaption>Poslušnost</figcaption></figure>
      <figure class="b6 rv" style="--d:.16s">{img(0, 'rybnik', 'Výcvik u rybníka', small=True)}<figcaption>U vody</figcaption></figure>
    </div>
  </div>
</section>
'''
    scripts = f'<script src="assets/schedule.js?v={ver("assets/schedule.js")}" defer></script>\n<script src="assets/home.js?v={ver("assets/home.js")}" defer></script>'
    doc = head('Lovecký výcvik psích plemen — výcvik a příprava k loveckým zkouškám',
               'Lovecký výcvik se zabývá výcvikem, cvičením a přípravou k loveckým zkouškám všech loveckých plemen. Nebušice, Hájovna Mrákavy a honitby poblíž Prahy.', 0)
    doc += '<body>\n' + nav(0, '') + '<main>\n' + body + '</main>\n' + footer(0) + scripts + '\n</body>\n</html>\n'
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(doc)


# ======================================================================
#  VÝCVIK
# ======================================================================
def build_vycvik():
    d = 1
    by = lambda g: [L for L in ALL_LESSONS if L['group'] == g]
    posl = by('poslusnost'); aport = by('aporty'); zk = by('zkousky')
    zk_main = [L for L in zk if not L['id'].startswith(('barva', 'stopa'))]
    barvy = [L for L in zk if L['id'].startswith(('barva', 'stopa'))]
    cards = lambda ls: '<div class="lessons">' + ''.join(lesson_card(L, d) for L in ls) + '</div>'
    weather = f'<div class="note note--warn" style="margin-top:1.2rem">{ICON["info"]}<span><b>Nezapomeňte:</b> {WEATHER}</span></div>'
    sub = [('seznamovaci-prochazka', 'Seznamovací procházka'), ('poslusnost', 'Poslušnost'), ('aporty', 'Aporty'),
           ('zkousky', 'Příprava ke zkouškám'), ('barvy', 'Barvy a stopy'), ('individualni', 'Individuální výcvik'),
           ('vystavy', 'Výstavy'), ('teorie', 'Teorie')]
    body = phead(d, 'Výcvik', 'Výcvik, který <em>má výsledky</em>',
                 'Základem úspěšného používání loveckého psa v myslivosti není jen jeho chovatelské prošlechtění, ale především cílevědomý výcvik.', photo='pole')
    body += '<nav class="subnav"><div class="wrap"><ul>' + ''.join(f'<li><a href="#{a}">{t}</a></li>' for a, t in sub) + '</ul></div></nav>'
    body += f'''
<section class="section" id="seznamovaci-prochazka">
  <div class="wrap split">
    <div class="sticky-col"><div class="photo photo--tall clip">{img(d, 'les', 'Skupina se psy na lesní cestě')}</div></div>
    <div>
      <span class="eyebrow">Začínáme tady</span>
      <h2>Seznamovací procházka</h2>
      <div class="prose">
        <p class="lead-p">Procházka je zdarma. Popovídáme, probereme vaše představy a požadavky, seznámíme se s vaším pejskem.</p>
        <p>Pro to, abychom zachovali individuální přístup ke každému pejskovi a pokusili se vyjít vstříc požadavkům a představám páníků, máme jako <b>podmínku</b> pro možnost návštěv našich výcvikových hodin absolvování úvodní seznamovací procházky. Uděláme si obrázek o tom, do které výcvikové skupiny vás zařadíme.</p>
        <p>Seznamovací procházky jsou vypisovány do rozvrhu vždy první týden v měsíci. Pro přihlášení do této hodiny je nutná předchozí registrace. V případě, že by vám termín nevyhovoval, či jste chtěli začít chodit cvičit dříve, než bude vypsán termín, tak není problém dohodnout se na individuálním čase. Neváhejte napsat či zavolat.</p>
      </div>
      <div class="note note--warn" style="margin-top:2rem">{ICON['info']}<span><b>Aktuálně:</b> vzhledem k naplnění kapacity nyní nebereme nové zájemce o výcvik. Děkujeme za pochopení.</span></div>
      <p style="margin-top:1.6rem;display:flex;gap:.6rem;flex-wrap:wrap"><a class="btn" href="../registrace/">Jak s námi začít {ICON['arr']}</a><a class="btn btn--ghost" href="mailto:info@loveckyvycvik.cz">Napsat e-mail</a></p>
    </div>
  </div>
</section>

<section class="section alt" id="poslusnost">
  <div class="wrap lesson-group">
    <div class="lg-head"><div><span class="eyebrow">Skupinový výcvik</span><h2>Poslušnost</h2></div>
      <div><p>I lovecký pes musí být vychovaným rodinným společníkem. Musí se socializovat, naučit „slušnému“ chování ve skupině pejsků, naučit se poslouchat i mezi psími kamarády. Každý pes (i nelovecký) musí umět základní povely, musí být neagresivní a plně ovladatelný ve městě i v přírodě bez vodítka.</p>
      <p class="muted" style="margin-top:.8rem">V hodinách poslušnosti se učíme základní ovladatelnost psa, socializujeme štěňátka, připravujeme na budoucí výstavy a zkoušky (i když to není podmínkou). Těm, kteří se v budoucnu budou chtít výcviku dále věnovat a na zkoušky vyrazit, tyto hodiny dodají potřebný základ.</p></div></div>
    {cards(posl)}{weather}
  </div>
</section>

<section class="section" id="aporty">
  <div class="wrap lesson-group">
    <div class="lg-head"><div><span class="eyebrow">Výcvik v přinášení</span><h2>Aporty</h2></div>
      <div><p>Základem práce loveckého psa – především plemen ohařů a retrívrů. Lovecký pes, který má být dobrým pomocníkem, musí aportovat ve všech situacích, spolehlivě a pracovat s velkou mírou samostatnosti.</p>
      <p class="muted" style="margin-top:.8rem">Aporty začínáme systematickým výcvikem v přinášení kozlíku (dřevěné činky), na kterém se pes naučí nosit bezchybně, bez překusování, hraní si, pokládání apod. Poté se postupně přistupuje k těžším aportům, aportovacím peškům – dummy, atrapám a končí se u samotné zvěře (malou pernatou zvěří počínaje, liškou u ohařů konče). Speciální disciplíny v přinášení, jako jsou dohledávky, vlečky atd., se cvičí v rámci samostatných příprav na dané typy zkoušek.</p></div></div>
    {cards(aport)}{weather}
  </div>
</section>

<section class="section dark" id="zkousky">
  <div class="wrap lesson-group">
    <div class="lg-head"><div><span class="eyebrow">Dle platných ZŘ</span><h2>Příprava k loveckým zkouškám</h2></div>
      <div><p>V hodinách příprav k loveckým zkouškám se specializujeme na výcvik pro jednotlivé typy zkoušek. V menších skupinách dojíždíme do terénů a míst, která jsou pro výcvik vhodná. Vůdce i pejsky seznamujeme s průběhem zkoušek, zkušebními řády a učíme se jednotlivé konkrétní disciplíny.</p></div></div>
    <div style="color:var(--ink)">{cards(zk_main)}</div>
  </div>
</section>

<section class="section alt" id="barvy">
  <div class="wrap lesson-group">
    <div class="lg-head"><div><span class="eyebrow">Barvy a stopy</span><h2>Práce na barvě a stopě</h2></div>
      <div><p>Úvodní hodinu je nutné absolvovat před samotným zahájením cvičení barev a stop — pes na ni může zůstat i doma. Barva i spárky pro kladení stopy budou zajištěny.</p></div></div>
    {cards(barvy)}
  </div>
</section>

<section class="section" id="individualni">
  <div class="wrap split split--rev">
    <div>
      <span class="eyebrow">Výcvik dle dohody</span>
      <h2>Individuální výcvik</h2>
      <div class="prose">
        <p class="lead-p">Nevyhovují vám termíny či není vypsaná hodina „pro vás“? Máte háravou fenku a nemůžete do skupiny? Potřebujete doladit disciplíny těsně před zkouškami?</p>
        <p>Neváhejte, zavolejte či napište mejlíka a zkusíme se s tím poprat a cvičit podle individuálního plánu. Na místě výcviku se domluvíme. Individuální výcvik má kapacitu max. 2 psi, cena dle konkrétního typu cvičení.</p>
      </div>
      <h3 style="font-size:var(--h3);margin-top:2.6rem">Náprava problémového chování</h3>
      <div class="prose" style="margin-top:.8rem">
        <p>Máte doma neurvalce či „namachrovaného“ hafana? Nedá se ten štěkot či ničení interiéru bytu už vydržet? Je to útěkář a „holkař“?</p>
        <p>Probereme s Vámi toto chování, pokusíme se najít příčiny a chování napravit. Napište či zavolejte a domluvíme si schůzku.</p>
      </div>
      <p style="margin-top:1.8rem;display:flex;gap:.6rem;flex-wrap:wrap"><a class="btn btn--dark" href="mailto:info@loveckyvycvik.cz">info@loveckyvycvik.cz</a><a class="btn btn--ghost" href="tel:+420777717271">777 717 271</a></p>
    </div>
    <div class="sticky-col"><div class="photo photo--tall clip">{img(d, 'vudce-terier', 'Vůdce s teriérem na louce')}</div></div>
  </div>
</section>

<section class="section alt" id="vystavy">
  <div class="wrap split">
    <div class="sticky-col"><div class="photo photo--wide clip">{img(d, 'vystava', 'Psi s poháry na výstavě')}</div></div>
    <div>
      <span class="eyebrow">Výstavy</span>
      <h2>Příprava na výstavy</h2>
      <div class="prose">
        <p>Chystáte se na svou první výstavu? Nevíte, jak na výstavní postoj? Jak se pohybovat v kruhu? Jak naučit tohle všechno Vašeho psa? Nevyznáte se v titulech? Má Váš pejsek ve výstavním kruhu problémy či se bojí?</p>
        <p>Rádi Vám pomůžeme s přípravou Vašeho pejska a Vás na výstavu. Poradíme, jak se obléci, jak naučit pejska stát, vysvětlíme výstavní řády a předpisy a dodáme pár tipů a triků. Pomůžeme Vašemu pejskovi získat důvěru v kruhu.</p>
        <p>V případě zájmu o tento výcvik nás kontaktujte a my rádi vypíšeme hodinu do rozvrhu (aby nás bylo více), nebo se sejdeme individuálně.</p>
      </div>
      <p style="margin-top:1.6rem"><a class="link" href="../sluzby/">Předvedení psa na výstavě a poradenství {ICON['arr']}</a></p>
    </div>
  </div>
</section>

<section class="section" id="teorie">
  <div class="wrap split split--rev">
    <div>
      <span class="eyebrow">Bez psů</span>
      <h2>Teorie</h2>
      <div class="prose">
        <p class="lead-p">Pro vysvětlení zkušebních řádů, výstavních a jiných předpisů máme speciální hodiny teorie.</p>
        <p>Na tyto hodiny se scházíme bez psů, nosíme zápisník a tužku. Probíráme zde disciplíny jednotlivých zkoušek, dáváme tipy a rady, jak se s řády a předpisy vyrovnat, upozorňujeme na úskalí jednotlivých disciplín, probíráme celkovou organizaci zkoušek. Vše je doplněno videi, fotografiemi atd. Je zde prostor pro dotazy a individuální vysvětlení nejasností.</p>
        <p>Místo „výuky“ je vždy předem určeno.</p>
      </div>
      <p style="margin-top:1.6rem"><a class="btn btn--dark" href="../rozvrh/?typ=teorie">Teorie v rozvrhu {ICON['arr']}</a></p>
    </div>
    <div class="sticky-col"><div class="photo photo--wide clip">{img(d, 'teorie', 'Výklad s jezevčíkem v lese')}</div></div>
  </div>
</section>
'''
    page('vycvik/index.html', 'Výcvik — Lovecký výcvik psích plemen',
         'Seznamovací procházka, skupinový výcvik poslušnosti, aporty, příprava k loveckým zkouškám ZN, ZV, OVVR, PZ, SVP, LZ, barvy a stopy, individuální výcvik, výstavy a teorie.',
         body, 'vycvik/')


# ======================================================================
#  ROZVRH (ukázka přihlašovacího systému)
# ======================================================================
def build_rozvrh():
    d = 1
    catalog = {L['id']: {'name': L['name'], 'group': L['group'], 'price': L['price'], 'f': L['f']} for L in ALL_LESSONS}
    catalog['teorie'] = {'name': 'Teorie', 'group': 'teorie', 'price': '300 Kč', 'f': {
        'Předmět cvičení': 'Disciplíny jednotlivých zkoušek, zkušební řády a předpisy, úskalí jednotlivých disciplín, organizace zkoušek. Doplněno videi a fotografiemi.',
        'Pomůcky': 'bez psů — zápisník a tužka'}}
    catalog['sezn'] = {'name': 'Seznamovací procházka', 'group': 'sezn', 'price': 'zdarma', 'f': {
        'Předmět cvičení': 'Popovídáme, probereme vaše představy a požadavky. Seznámíme se s vaším pejskem a uděláme si obrázek o tom, do které výcvikové skupiny vás zařadíme.',
        'Předchozí výcvik': 'žádný — pro přihlášení je nutná předchozí registrace'}}
    json.dump(catalog, open(os.path.join(ROOT, 'assets/lekce.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    body = f'''
<section class="app-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Drobečková navigace"><a href="../">Úvod</a><span>/</span><span>Rozvrh cvičení</span></nav>
    <div class="app-top">
      <h1>Rozvrh <em>cvičení</em></h1>
      <div class="acc" id="acc"></div>
    </div>
    <div class="demo-banner">{ICON['info']}<span><b>Ukázka nového přihlašovacího systému.</b> Termíny a obsazenost jsou ilustrační, přihlášení se nikam neodesílá — zkuste si hodinu vybrat, přihlásit psa, zapsat se na čekací listinu i odhlásit.</span></div>
  </div>
</section>
<div class="toolbar"><div class="wrap toolbar-in">
  <div class="weeknav"><button id="wk-prev" aria-label="Předchozí týden">←</button><b id="wk-label">…</b><button id="wk-next" aria-label="Další týden">→</button></div>
  <div class="filters" id="filters"></div>
  <button class="btn btn--sm btn--dark mybtn" id="my-open">Moje přihlášky <span class="badge" id="my-count" hidden>0</span></button>
</div></div>
<section><div class="wrap"><div class="week" id="week" aria-live="polite"></div></div></section>
<section><div class="wrap app-foot">
  <div class="rule"><h3>Barevné značky</h3>
    <div class="legend"><span class="st st--free">hodina je volná</span><span class="st st--wait">hodina je plná — lze se zapsat na čekací listinu</span><span class="st st--closed">přihlašování je uzavřeno</span><span class="st st--booked">jste přihlášeni</span></div></div>
  <div class="rule"><h3>Nemůžete dorazit?</h3><p>Pokud se na hodinu přihlásíte a nemůžete nakonec dorazit, odhlaste se. Na některá cvičení je nutná příprava předem, tak ať zbytečně nelítáme po lese. Někdy máme za vás náhradníka.</p></div>
  <div class="rule"><h3>Cvičení versus počasí</h3><p>V případě, že je nevhodné počasí (prší, sněží atd.), dáváme vědět cca hodinku předem. Ideálně pomocí SMS, pokud na vás nemáme telefon, tak píšeme e-mail. Ne vždy však je déšť na závadu :-).</p></div>
</div></section>

<div class="scrim" id="scrim"></div>
<aside class="panel" id="panel" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="panel-title">
  <div class="panel-h"><span class="eyebrow" id="panel-eyebrow">Hodina</span><button class="panel-x" id="panel-x" aria-label="Zavřít">✕</button></div>
  <div class="panel-b" id="panel-b"></div>
  <div class="panel-f" id="panel-f"></div>
</aside>
<div class="toast" id="toast" role="status"><i></i><span></span></div>
'''
    scripts = f'<script src="../assets/schedule.js?v={ver("assets/schedule.js")}" defer></script>\n<script src="../assets/rozvrh.js?v={ver("assets/rozvrh.js")}" defer></script>'
    page('rozvrh/index.html', 'Rozvrh cvičení — Lovecký výcvik psích plemen',
         'Týdenní rozvrh hodin výcviku: přihlašování psů na hodiny, čekací listina, odhlášení. Ukázka nového systému.',
         body, 'rozvrh/', light=True, scripts=scripts, cta=False)


# ======================================================================
#  REGISTRACE
# ======================================================================
def build_registrace():
    d = 1
    interests = ['Školička pro štěňátka', 'Skupinový výcvik poslušnosti', 'Aporty', 'Příprava k loveckým zkouškám',
                 'Práce na barvě a stopě', 'Individuální výcvik', 'Náprava problémového chování', 'Příprava na výstavy', 'Teorie', 'Poradenství — výběr psa']
    exams = ['ZN', 'ZV', 'OVVR', 'PZ', 'SVP', 'VP', 'LZ', 'zatím nevím']
    body = phead(d, 'Registrace', 'Jak s námi <em>začít cvičit</em>',
                 'Ideální postup, jak se k nám přidat: e-mail s pár informacemi, seznamovací procházka a potom registrace do systému.', photo='nastup-zima')
    body += f'''
<section class="section">
  <div class="wrap reg-grid">
    <div>
      <div class="note note--warn">{ICON['info']}<span><b>Aktuálně:</b> vzhledem k naplnění kapacity nyní nebereme nové zájemce o výcvik. Děkujeme za pochopení. Formulář níže ukazuje, jak bude registrace fungovat, až se místa uvolní.</span></div>
      <ol class="steps" style="margin-top:2rem">
        <li><div><b>Zašlete e-mail</b><p>S pár informacemi o Vás, o Vašem pejskovi a Vašich plánech a představách. E-mailem budete informováni o možnostech a volné kapacitě.</p></div></li>
        <li><div><b>Seznamovací procházka</b><p>Pokud přibíráme nové klienty, domluvíme si první termín individuální schůzky, kde probereme podrobnosti, systém našeho výcviku a zodpovíme případné dotazy.</p></div></li>
        <li><div><b>Registrace do systému</b><p>Vyplňte požadované údaje. Přístup do rozvrhu je povolen až na základě našeho zpětného potvrzení (tzn. ne ihned po odeslání údajů).</p></div></li>
      </ol>
      <div class="pull">Pokud se nenajdete v seznamu našich „oveček“ a přejete si tam být, dejte nám prosím vědět a vše napravíme.</div>
    </div>

    <div class="form-card" id="reg">
      <ol class="progress" aria-hidden="true"><li class="on"><i>1</i><span>Vy</span></li><li><i>2</i><span>Váš pes</span></li><li><i>3</i><span>Plány a souhlas</span></li></ol>
      <form id="reg-form" novalidate>
        <div class="fstep on" data-step="0">
          <h2>Údaje o vás</h2><p>Telefon potřebujeme hlavně kvůli SMS, když kvůli počasí rušíme hodinu.</p>
          <div class="fields">
            <div class="field field--full"><label for="f-name">Jméno a příjmení <em>*</em></label><input id="f-name" name="jmeno" autocomplete="name" required><span class="msg">Vyplňte prosím jméno.</span></div>
            <div class="field"><label for="f-mail">E-mail <em>*</em></label><input id="f-mail" name="email" type="email" autocomplete="email" required><span class="msg">Zadejte platný e-mail.</span></div>
            <div class="field"><label for="f-tel">Telefon <em>*</em></label><input id="f-tel" name="telefon" type="tel" autocomplete="tel" inputmode="tel" placeholder="+420" required><span class="msg">Zadejte telefon.</span></div>
            <div class="field"><label for="f-pw">Heslo <em>*</em></label><input id="f-pw" name="heslo" type="password" autocomplete="new-password" minlength="8" required><span class="hint">Alespoň 8 znaků.</span><span class="msg">Heslo musí mít alespoň 8 znaků.</span></div>
            <div class="field"><label for="f-pw2">Heslo znovu <em>*</em></label><input id="f-pw2" name="heslo2" type="password" autocomplete="new-password" required><span class="msg">Hesla se neshodují.</span></div>
          </div>
        </div>
        <div class="fstep" data-step="1">
          <h2>Váš pes</h2><p>Máte ve smečce víc psů? Přidejte je všechny — na hodiny pak přihlašujete každého zvlášť.</p>
          <div class="fields" id="dogs"></div>
        </div>
        <div class="fstep" data-step="2">
          <h2>Plány a představy</h2><p>Podle toho vám doporučíme vhodnou skupinu.</p>
          <div class="fields">
            <div class="field field--full"><span class="lbl">Co vás zajímá</span><div class="checks">{''.join(f'<label><input type="checkbox" name="zajem" value="{E(i)}">{i}</label>' for i in interests)}</div></div>
            <div class="field field--full"><label for="f-exam">Chystáte se na zkoušky?</label><select id="f-exam" name="zkousky"><option value="">— vyberte —</option>{''.join(f'<option>{x}</option>' for x in exams)}</select></div>
            <div class="field field--full"><label for="f-msg">Pár slov o vás a vašem pejskovi</label><textarea id="f-msg" name="zprava" placeholder="Jaké máte plány a představy, co už pes umí, s čím potřebujete pomoct…"></textarea></div>
            <div class="field field--full">
              <label class="consent"><input type="checkbox" name="souhlas" required><span>Souhlasím se zpracováním uvedených údajů pro potřeby vedení výcviku. <em style="color:var(--closed);font-style:normal">*</em></span></label>
              <label class="consent"><input type="checkbox" name="seznam"><span>Souhlasím s uvedením mého jména a jména mého psa v seznamu cvičenců na webu. Pro uvedení do seznamu absolventů (po absolvování zkoušek) pošlu fotografii.</span></label>
              <span class="msg">Bez souhlasu se zpracováním údajů registraci nelze odeslat.</span>
            </div>
          </div>
        </div>
        <div class="fnav" id="fnav"><button type="button" class="btn btn--ghost btn--sm" id="f-back" hidden>← Zpět</button><small>Pole s <span style="color:var(--closed)">*</span> jsou povinná</small><button type="submit" class="btn btn--dark" id="f-next">Pokračovat {ICON['arr']}</button></div>
      </form>
      <div class="done-box" id="done">
        <div class="done-ico">{ICON['check']}</div>
        <h2>Děkujeme, registrace je připravena.</h2>
        <p>V ostrém provozu by teď registrace čekala na potvrzení. Přístup do rozvrhu povolíme po schválení a dáme vám vědět e-mailem.</p>
        <div class="summary" id="summary"></div>
        <p style="font-size:.82rem"><b>Ukázka:</b> formulář v návrhu nic neodesílá.</p>
        <p style="margin-top:1.6rem"><a class="btn" href="../rozvrh/">Prohlédnout rozvrh {ICON['arr']}</a></p>
      </div>
    </div>
  </div>
</section>
'''
    scripts = f'<script src="../assets/registrace.js?v={ver("assets/registrace.js")}" defer></script>'
    page('registrace/index.html', 'Registrace — Lovecký výcvik psích plemen',
         'Jak s námi začít cvičit: e-mail, seznamovací procházka a registrace do systému rozvrhu.', body, '', scripts=scripts)


# ======================================================================
#  KALENDÁŘ AKCÍ
# ======================================================================
MONTHS = ['leden', 'únor', 'březen', 'duben', 'květen', 'červen', 'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec']
MONTH_W = {'srpen': 8, 'září': 9, 'listopad': 11, 'prosinec': 12}


def ev_month_and_end(date):
    m = re.findall(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date)
    if m:
        dd, mm, yy = map(int, m[-1])
        return mm, (yy, mm, dd)
    for k, v in MONTH_W.items():
        if date.lower().startswith(k):
            return v, (2026, v, 31)
    return 0, (2026, 12, 31)


def nice_date(s):
    s = s.replace('.-', '.–').replace(' ', ' ')
    s = re.sub(r'(\d)\.(\d)', r'\1. \2', s)
    s = re.sub(r'(\d)\.(\d)', r'\1. \2', s)
    return s


def doc_label(l):
    t = l['label'].lower().strip('. ')
    if t.startswith('propozice'): return 'Propozice'
    if 'řád' in t: return 'Řád poháru'
    if 'přihlá' in t or 'přihlaš' in t:
        return 'Přihláška ' + ('DOC' if 'doc' in t else 'PDF')
    if 'předodjezd' in t: return 'Předodjezdové info'
    return 'Informace'


def events_data():
    out = []
    for i, e in enumerate(DATA['akce']):
        m, end = ev_month_and_end(e['date'])
        past = end < TODAY
        out.append(dict(e, month=m, past=past, i=i, typ=fix(e['type']).replace('VÁNOČNÍ VEČÍREK', 'Vánoční večírek'), info=fix(e['info'])))
    return out


def build_akce():
    d = 1
    evs = events_data()
    upcoming = [e for e in evs if not e['past']]
    body = phead(d, 'Kalendář akcí', 'Kalendář <em>akcí 2026</em>',
                 'Termíny zkoušek a akcí v roce 2026. Akce budou postupně doplňovány, propozice na jednotlivé akce budou včas dodány. Počet psů je omezen.', photo='senior')
    body += '<section class="section"><div class="wrap">'
    body += f'<div class="note" style="margin-bottom:2.4rem">{ICON["info"]}<span><b>Nejbližší:</b> ' + ', '.join(f'{E(e["typ"])} ({nice_date(e["date"])})' for e in upcoming[:3]) + '. Přihlašování na akce, bližší informace atd. bude uvedeno v propozicích či na doptání. <a class="link" href="#m' + str(upcoming[0]['month']) + '">Přejít na nejbližší akce ↓</a></span></div>'
    for mi in range(1, 13):
        items = [e for e in evs if e['month'] == mi]
        if not items: continue
        rows = ''
        for e in items:
            if e['links']:
                seen = set(); docs = ''
                for l in e['links']:
                    lab = doc_label(l)
                    if (lab, l['href']) in seen: continue
                    seen.add((lab, l['href']))
                    docs += f'<a class="doc{" doc--main" if lab == "Propozice" else ""}" href="{E(l["href"])}" target="_blank" rel="noopener">{ICON["doc"]}{lab}</a>'
            elif 'rozvrh' in e['reg'] and e['past']:
                docs = '<span class="doc" style="opacity:.7">přihlašování přes rozvrh</span>'
            elif 'rozvrh' in e['reg']:
                docs = f'<a class="doc doc--main" href="../rozvrh/">Přihlásit přes rozvrh →</a>'
            else:
                docs = f'<a class="doc" href="mailto:info@loveckyvycvik.cz">Více e-mailem</a>'
            anchor = ' id="tabor"' if 'tábor' in e['typ'].lower() else ''
            state = '<span class="tag tag--muted">Proběhlo</span>' if e['past'] else '<span class="tag">Připravujeme</span>'
            rows += f'''<article class="cal-ev{' past' if e['past'] else ''}"{anchor}>
  <div class="cal-date">{nice_date(e['date'])}<small>{state}</small></div>
  <div><h3>{E(e['typ'])}</h3><p>{E(e['info'])}</p></div>
  <div class="cal-docs">{docs}</div></article>'''
        body += f'<div class="cal-month rv" id="m{mi}"><h2>{MONTHS[mi - 1].capitalize()}</h2><div>{rows}</div></div>'
    body += '</div></section>'
    page('akce/index.html', 'Kalendář akcí 2026 — Lovecký výcvik psích plemen',
         'Víkendové přípravy na zkoušky, výcvikový tábor, Senior CUP, semináře a přednášky v roce 2026. Propozice a přihlášky ke stažení.',
         body, 'akce/')
    # data pro úvodní stránku
    home = [{'date': nice_date(e['date']), 'typ': e['typ'], 'info': e['info'], 'past': e['past']} for e in evs]
    json.dump(home, open(os.path.join(ROOT, 'assets/akce.json'), 'w', encoding='utf-8'), ensure_ascii=False)


# ======================================================================
#  CENÍK
# ======================================================================
def build_cenik():
    d = 1
    groups = [
        ('Skupinový výcvik poslušnosti', [('Seznamovací lekce', 'zdarma'), ('Školka pro štěňátka', '250 Kč'), ('Poslušnost – začátečníci', '250 Kč'),
                                          ('Poslušnost – mírně pokročilí', '250 Kč'), ('Poslušnost – pokročilí', '250 Kč'), ('Speciální výcvik – ostatní', '400 Kč'), ('Downy', '250 Kč')]),
        ('Aporty', [('Aporty kozlík, přechod na zvěř', '250 Kč'), ('Aporty zvěř', '350 Kč')]),
        ('Příprava k loveckým zkouškám', [('Příprava na ZN', '100 Kč'), ('Vystavení, práce na živé zvěři', '350 Kč'), ('Příprava na ZV', '400 Kč'),
                                          ('Příprava na OVVR', '350 Kč'), ('Příprava na PZ', '500 Kč'), ('Příprava na VP', '350 Kč'),
                                          ('Příprava na LZ – drobné disciplíny', '300 Kč'), ('Příprava na LZ – aportovací disciplíny', '400 Kč'),
                                          ('Příprava na LZ – ohaři, retrívři, slídiči', '500 Kč'), ('Práce na barvě, stopě – úvodní hodina', '350 Kč'),
                                          ('Práce na barvě – začátečníci, mírně pokročilí', '400 Kč'), ('Práce na barvě – pokročilí', '400 Kč'), ('Práce na stopě', '400 Kč')]),
        ('Individuální výcvik — max. kapacita 2 psi', [('Dle konkrétního typu cvičení', 'dle dohody'), ('Náprava problémového chování', 'dle dohody')]),
        ('Výstavy, teorie a ostatní', [('Příprava na výstavy', '350 Kč'), ('Teorie', '300 Kč'), ('Ostatní služby', 'dle dohody')]),
    ]
    g_html = ''.join(f'<div class="pgroup rv"><h2>{t}</h2>' + ''.join(
        f'<div class="prow"><span>{n}</span><i></i><b class="{"free" if p == "zdarma" else ""}">{p}</b></div>' for n, p in rows) + '</div>' for t, rows in groups)
    body = phead(d, 'Ceník', 'Ceník <em>výcviku</em>', 'Ceník platný od 1. 2. 2025. Ceny jsou za jednu lekci — délka lekcí se liší v závislosti na typu cvičení a vždy je uvedená v rozvrhu.')
    body += f'''
<section class="section" style="padding-top:1rem">
  <div class="wrap price-wrap">
    <div>{g_html}
      <p class="muted" style="margin-top:2rem;font-size:.92rem">Ostatní služby — ceny dle individuální dohody. Některé speciální typy hodin se mohou od ceníku lišit, více vždy v rozvrhu či po dohodě. Popis náplně jednotlivých hodin najdete v sekci <a class="link" href="../vycvik/">Výcvik</a>.</p>
    </div>
    <aside class="sticky-col">
      <div class="pay rv">
        <span class="eyebrow">Platba za hodiny</span>
        <h2 style="margin-top:1rem">Hotově, nebo z permanentky</h2>
        <ul><li>hotově po jednotlivé odcvičené hodině</li><li>hotově či převodem na účet — vystavíme permanentku, ze které se bude postupně čerpat kredit</li></ul>
        <div class="perm"><div><b>1 000</b><small>Kč permanentka</small></div><div><b>2 000</b><small>Kč permanentka</small></div></div>
        <div class="acct"><div><small>Číslo účtu</small><b id="acct">3291709012/3030</b></div><button class="copy" data-copy="3291709012/3030">Kopírovat</button></div>
        <p>V případě zájmu o vystavení permice prosím pípněte mejlík na <a href="mailto:info@loveckyvycvik.cz" style="color:var(--lime)">info@loveckyvycvik.cz</a>.</p>
      </div>
    </aside>
  </div>
</section>'''
    page('cenik/index.html', 'Ceník — Lovecký výcvik psích plemen',
         'Ceník výcviku platný od 1. 2. 2025: poslušnost, aporty, příprava k loveckým zkouškám, barvy a stopy, výstavy, teorie. Platba hotově nebo permanentkou.',
         body, 'cenik/', light=True)


# ======================================================================
#  KLIENTI
# ======================================================================
def build_klienti():
    d = 1
    def conv(lst):
        out = []
        for a in lst:
            im = f"../assets/abs/{hashlib.md5(a['img'].encode()).hexdigest()[:12]}.jpg" if a['img'] else ''
            out.append({'n': fix(a['name']).replace('„U“ ', '„U“ ').strip(), 'o': fix(a['owner']), 'r': [fix(x) for x in a['results']], 'i': im})
        return out
    kdata = {
        'cvicenci': [{k: fix(v) for k, v in c.items()} for c in DATA['cvicenci']],
        'absolventi': conv(DATA['absolventi']),
        'stari': conv(DATA['absolventi_old']),
    }
    json.dump(kdata, open(os.path.join(ROOT, 'assets/klienti.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    body = phead(d, 'Klienti', 'Naši cvičenci <em>a absolventi</em>',
                 'Myslíme, že nejlepší referencí jsou hafani, kteří dělají páníkům radost, a také úspěchy našich odchovánků na zkouškách.', photo='tabor')
    body += f'''
<section class="section" style="padding-top:clamp(3rem,6vw,5rem)">
  <div class="wrap">
    <div class="tabs" role="tablist">
      <button class="tab" role="tab" aria-selected="true" data-tab="absolventi">Absolventi od 2018<small>{len(kdata['absolventi'])}</small></button>
      <button class="tab" role="tab" aria-selected="false" data-tab="cvicenci">Cvičí u nás 2026<small>{len(kdata['cvicenci'])}</small></button>
      <button class="tab" role="tab" aria-selected="false" data-tab="stari">Absolventi do 2018<small>{len(kdata['stari'])}</small></button>
    </div>
    <p class="muted" id="tab-note" style="margin-bottom:1.6rem;max-width:70ch"></p>
    <div class="tools">
      <label class="search"><span class="sr">Hledat</span>{ICON['search']}<input id="q" type="search" placeholder="Hledat psa, páníčka, plemeno…"></label>
      <div class="filters" id="kf"></div>
      <span class="count" id="kcount"></span>
    </div>
    <div id="klist"></div>
    <div class="more-wrap"><button class="btn btn--ghost" id="kmore" hidden>Načíst další</button></div>
  </div>
</section>'''
    scripts = f'<script src="../assets/klienti.js?v={ver("assets/klienti.js")}" defer></script>'
    page('klienti/index.html', 'Cvičenci a absolventi — Lovecký výcvik psích plemen',
         'Seznam psů, kteří u nás cvičí v roce 2026, a přehled úspěšných absolventů loveckých zkoušek.', body, 'klienti/', scripts=scripts)


# ======================================================================
#  O NÁS
# ======================================================================
PRESENTED = [
    ('Algeron Laváre Morávia', 'MOK', {'ZV': 1, 'PZ': 1, 'VP': 1}), ('Or Kajan z Baštin', 'MOK', {'ZV': 1, 'PZ': 1, 'LZ': 1, 'VP': 1, 'VZ': 6}),
    ('Orisa z Mečkovské skály', 'NDO', {'PZ': 1}), ('Ambra z Královských vinic', 'MOK', {'ZV': 1, 'PZ': 1}),
    ('Bona od Lodenické stráně', 'FXH', {'ZV': 1, 'LZ': 1, 'BZ': 1, 'ZN': 1}), ('Poly z Lesních chalup', 'AC', {'ZV': 1}),
    ('Beruška Aivor du Néz', 'WSS', {'ZV': 1, 'PZ': 1, 'LZ': 1, 'VP': 1, 'VZ': 1, 'BZ': 1}), ('Artaban Vives Bohemia', 'FXH', {'ZV': 1, 'ZN': 1}),
    ('Bardotte Bertoni Prague', 'MOK', {'ZV': 1, 'PZ': 2, 'LZ': 1, 'VP': 2, 'VZ': 1}), ('Jagger Vives Bohemia', 'MOK', {'ZV': 1, 'PZ': 1, 'LZ': 1, 'VP': 1, 'VZ': 1}),
    ('Donka z Blýskavé', 'J drs', {'ZV': 1, 'BZ': 1, 'ZN': 1}), ('Akira z Podřipské studánky', 'J drs', {'ZV': 1, 'BZ': 1, 'ZN': 1}),
    ('Vinnie Stella Venandi', 'NDO', {'ZV': 1, 'PZ': 2, 'LZ': 1, 'VP': 2, 'VZ': 1, 'FT': 1, 'MFT': 1, 'NFT': 1}),
    ('Xanta Stella Venandi', 'NDO', {'ZV': 1, 'PZ': 1, 'LZ': 1, 'VP': 1}), ('Nord Jokran', 'NKO', {'ZV': 1, 'PZ': 1}),
    ('Pradelinensis Volga', 'NKO', {'ZV': 1}), ('Glorie Excelsis Deo Locura', 'MOK', {'ZV': 1, 'PZ': 1}),
    ('Rebeka z Czarnego Dworu', 'NKO', {'ZV': 1, 'VP': 1}), ('Venus Stella Venandi', 'NDO', {'ZV': 1}),
    ('Rigo ze Stražišťských lesů', 'PP', {'ZV': 1, 'PZ': 1}), ('Dunaj z Talchejow', 'MOD', {'PZ': 1}), ('Conny Apoli Gwen', 'IS', {'VP': 1}),
    ('Laps Eben-Ezer', 'MMO', {'PZ': 1}), ('Arys z Ratenických lán', 'NDO', {'PZ': 1}), ('Eliza Game Power', 'FXH', {'ZV': 1}),
    ('Ugi z Heřmanova domu', 'J drs', {'ZN': 1}), ('Margarita Vives Bohemia', 'MOK', {'VP': 1}),
    ('Sandokan Vives Bohemia', 'MOK', {'ZV': 1, 'PZ': 1, 'VP': 1}), ('Arlon Vives Bohemia', 'NDO', {'ZV': 1, 'PZ': 1, 'LZ': 1, 'VP': 1, 'VZ': 1}),
]


def build_onas():
    d = 1
    cols = ['ZV', 'PZ', 'LZ', 'VP', 'VZ', 'BZ', 'ZN', 'FT', 'MFT', 'NFT']
    rows = ''.join(f'<tr><td>{E(n)}</td><td>{b}</td>' + ''.join(f'<td class="num">{f"<b>{r[c]}</b>" if c in r else ""}</td>' for c in cols) + '</tr>' for n, b, r in PRESENTED)
    body = phead(d, 'O nás', 'Každý jednou <em>začínal</em>',
                 'I my jsme si kdysi pořídili svého prvního loveckého psa a toužili po složení loveckých zkoušek. Nakonec se z koníčka stal doslova kůň…', photo='rozhodci')
    body += '<nav class="subnav"><div class="wrap"><ul>' + ''.join(f'<li><a href="#{a}">{t}</a></li>' for a, t in [('kdo-jsme', 'Kdo jsme'), ('jak-cvicime', 'Jak cvičíme'), ('zkusenosti', 'Zkušenosti'), ('predvedeni-psi', 'Předvedení psi'), ('kde-cvicime', 'Kde cvičíme')]) + '</ul></div></nav>'
    body += f'''
<section class="section" id="kdo-jsme">
  <div class="wrap split">
    <div class="sticky-col"><span class="eyebrow">Kdo jsme</span><h2>Jak jsme se ke cvičení pejsků dostali</h2><div class="photo photo--tall clip" style="margin-top:2rem">{img(d, 'odlozeni', 'Pes odložený v lese')}</div></div>
    <div class="prose">
      <p class="lead-p">Každý jednou začínal… I my jsme si kdysi pořídili svého prvního loveckého psa a toužili po složení loveckých zkoušek, toužili po tom dopřát čtyřnohému příteli radost z lovu, pro který byl vyšlechtěn, a zkrátka jsme chtěli trávit čas s naším hafanem při nějaké smysluplné činnosti.</p>
      <p>Tenkrát jsme zjistili, že cvičáků a škol na poslušnost je moře… Ale kde připraví mého psa ke zkouškám? Kde naučí mne být dobrým vůdcem a mého psa být psem loveckým a pomocníkem do myslivosti? Hledání nebylo vůbec jednoduché. Literatura, internet, články v časopisech… To je sice mnoho informací… ale co si z toho vybrat… A jak vlastně mají jednotlivé popisované disciplíny vypadat?</p>
      <p>Tenkrát nám pomohlo pár kamarádů a lovecké kynologii jsme zcela propadli. Jednoho pejska časem doplnili další členové smečky, jedny odvedené zkoušky následovaly další a začali nás oslovovat lidé, kteří byli ve stejné situaci jako kdysi my, a nakonec se z koníčka stal doslova kůň…</p>
      <p>Naše kynologické aktivity jsme postupně „omezili“ pouze na kynologii loveckou a nutné výstavy, a to proto, že pokud člověk chce něco dělat pořádně, tak je lepší se ubírat jedním směrem. Dále z toho důvodu, že nám lovecká kynologie natolik učarovala, že zabírá téměř veškerý volný čas.</p>
      <div class="pull">Veškeré naše dospělé psy aktivně využíváme v lovecké praxi — účastní se honů, naháněk a dalších akcí.</div>
      <p>Celoročně naši psi pomáhají dosledovat poraněnou zvěř – ať už postřelenou či sraženou autem, pomáhají regulovat škodnou zvěř a jsou nám stálými průvodci, pomocníky a především kamarády. Těmto aktivitám, pro které psy především chováme, předchází zkoušky, výstavy a soutěže. Dospělé psy máme lovecky upotřebitelné s vyššími loveckými zkouškami. Mají splněné exteriérové a zdravotní podmínky k chovnosti.</p>
      <p>Další naší aktivitou je i chov psů a prezentace loveckých plemen a lovecké kynologie na různých veřejných akcích, jako jsou Dny dětí, odborné semináře apod. Také se věnujeme výcviku dalších psů a především jejich pánečků a naši psi nám při tom pomáhají. Podílíme se na organizaci výcvikových akcí, loveckých zkoušek a pobytů a výcviků pro všechny, kteří se chtějí svému loveckému psovi věnovat, nejsou myslivci, neví jak psa cvičit a potřebují do začátků poradit, pomoct a navést správným směrem… Pomáháme cvičit jejich pejsky, pomáháme při výchově, přípravě na výstavy, hlídáme pejsky, cvičíme a předvádíme na zkouškách lovecké psy různých plemen.</p>
      <p>Z mnoha majitelů pejsků, kteří s námi začínali, jsou nyní zkušení kynologové, chovatelé, vůdci, myslivci či pouze zodpovědní a spokojení majitelé psů. Jsme na ně moc pyšní a přejeme, ať se jim daří dál.</p>
    </div>
  </div>
</section>

<section class="section dark" id="jak-cvicime">
  <div class="wrap">
    <span class="eyebrow">Jak cvičíme</span>
    <p class="intro-quote" style="max-width:22ch;color:var(--on-dark)">Cvičíme tak, aby byl spokojený jak <em style="color:var(--lime-2)">páneček, tak pes</em> a aby byly vidět výsledky.</p>
    <div class="split" style="margin-top:clamp(3rem,6vw,5rem)">
      <blockquote class="pull" style="color:var(--on-dark);margin:0">Základem úspěšného používání loveckého psa v myslivosti není jen jeho chovatelské prošlechtění, ale především cílevědomý výcvik. Sebelepší původ, sebelepší nadání ani sebečastější výcviková zralost a fyzická připravenost psa samy o sobě nestačí, aby lovecký pes plnil řádně všechny úkoly, které od něho jako loveckého psa žádáme a žádat musíme, jestliže pro tyto úkoly nebyl vhodným způsobem připraven.<cite style="color:var(--on-dark-muted)">— Jan Báča</cite></blockquote>
      <div class="prose" style="color:var(--on-dark-muted)">
        <p style="color:var(--on-dark)">K našim svěřencům se snažíme přistupovat individuálně s přihlédnutím k povaze daného jedince i jeho majitele. Postup výcviku konzultujeme s majitelem, demonstrujeme na našich hafanech a dokládáme výsledky ze zkoušek a z praxe.</p>
        <p>Je nám jasné, že každý majitel psa má v dnešním světě k dispozici spoustu informací, ať už z knížek, internetu či od známých pejskařů, a každý má určitou představu o tom, jaké principy a techniky chce při výcviku svého miláčka použít. Jak se ale v tom množství informací vyznat? A jaké metody doopravdy fungují? Jak vyřešit konkrétní problém, který způsob zvolit?</p>
        <p>Většinou nikdo nechce svého psa cvičit systémem pokus–omyl. Je jasné, že žádný učený z nebe nespadl a určitě je vám jasné, že podobný problém, jako máte vy, už někdo určitě mnohokrát řešil. Chceme vám v těchto situacích efektivně pomoci, abyste s vaším psem mohli najít společnou řeč a brzy se stali pyšným majitelem vychovaného psa či úspěšným vůdcem na zkouškách.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="zkusenosti">
  <div class="wrap split split--rev">
    <div>
      <span class="eyebrow">Zkušenosti</span>
      <h2>Ing. Zuzana Čechová</h2>
      <div style="display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:1.6rem"><span class="chip"><b>1997</b> kynologie (bez účasti na zkouškách)</span><span class="chip"><b>2005</b> aktivně lovecká kynologie</span></div>
      <div class="prose">
        <p class="lead-p">S kynologií jsem začínala takřka od plenek.</p>
        <p>Tehdy se však nedalo hovořit o výcviku. Mým prvním psem (takovým tím rodinným) byla žíhaná fena německého boxera Arka bez PP, která mne doslova vylízala ze silného ekzému a dokázala nemožné… Tedy to, na co žádné mastičky nezabíraly. Od té doby byla láska ke psům daná :o). Po ní následoval první MŮJ pes – a to potomek této feny, kříženec boxera a pravděpodobně rotvajlera Aron. O jeho matku jsme přišli při porodu a tohoto hafana jsem „spoluodkojila“ od prvních dnů na flašce. Byl to Pan PES, který by za mne i dýchal, a nejlepší parťák a pracant, kterého jsem kdy měla… i když s jeho trochu dominantní povahou a figurou na kila srovnatelnou s mou byl výcvik trochu oříšek. Byl to první pes, se kterým jsem se aktivně věnovala výcviku. Souběžně s tímto psem jsem pomáhala cvičit babičky mazlíka, černého trpasličího pudla bez PP Nika. Od té doby nedám na pudly dopustit :o).</p>
        <p>Po této etapě a po tom, co mne v necelých 17 letech opustil kříženec Aron, jsem dlouho vybírala plemeno. Stále vedl jednoznačně boxer, ale situace tomu nechtěla (naštěstí :o)) a jednou z podmínek mysliveckého sdružení, kde jsem žádala o členství, byl pes lovecký. Pořídila jsem si tedy svého prvního loveckého psa, a to maďarského ohaře krátkosrstého s PP Algerona Laváre Morávia. Tento pes mne mnoho naučil a díky němu jsem doslova propadla lovecké kynologii. Po něm už následovali další členové nyní dosti početné smečky.</p>
        <div class="pull">S našimi hafany jsme dosáhli mnoha úspěchů, ale největším úspěchem jsou pro mne především výsledky mých „oveček“.</div>
        <p>Jsem moc ráda za to, že ze spousty lidiček se stali výborní vůdci a svědomití majitelé a především páníci svých loveckých psů. Ze spousty psů, kteří by strávili jistě spokojený život „na gauči“, se stali právoplatní výborní pomocníci při lovu, lovecky upotřebitelní psi, chovní, vycvičení, ovladatelní a bezproblémoví společníci se spokojeným naplněným životem loveckého psa s velkým P. Těší mne, že jsem mnoha lidem pomohla najít novou lásku – loveckou kynologii a myslivost.</p>
        <p>Mimo psů se věnuji myslivosti, kterou provozuji vlastně opět se psy :o). Ta je časově náročná hlavně v době lovecké sezóny v podobě víkendových honů a naháněk, kde jsou naši psi nutnými a žádanými pomocníky. Jinak mojí největší láskou a časově náročným „koníčkem“ jsou mé dcerky. Takže je pořád co dělat…</p>
      </div>
      <p style="margin-top:1.6rem;display:flex;gap:.6rem;flex-wrap:wrap"><a class="btn btn--dark" href="mailto:info@loveckyvycvik.cz">info@loveckyvycvik.cz</a><a class="btn btn--ghost" href="tel:+420777717271">777 717 271</a></p>
    </div>
    <div class="sticky-col"><div class="photo photo--tall clip">{img(d, 'aport-bazant', 'Ohař přináší bažanta')}</div><p class="caption">Foto z galerie Loveckého výcviku na Rajčeti.</p></div>
  </div>
</section>

<section class="section alt" id="predvedeni-psi">
  <div class="wrap">
    <div class="lg-head"><div><span class="eyebrow">Předvedení psi</span><h2>Psi předvedení na loveckých zkouškách</h2></div><p>Seznam předvedených psů na loveckých zkouškách, vůdce Zuzana Čechová. Čísla udávají počet složených zkoušek daného typu.</p></div>
    <div class="tbl-wrap rv"><table class="tbl"><thead><tr><th>Jméno</th><th>Plemeno</th>{''.join(f'<th class="num">{c}</th>' for c in cols)}</tr></thead><tbody>{rows}</tbody></table></div>
  </div>
</section>

<section class="section" id="kde-cvicime">
  <div class="wrap">
    <div class="lg-head"><div><span class="eyebrow">Kde cvičíme</span><h2>Místa výcviku</h2></div>
      <p>Pro náš výcvik se snažíme najít ty nejvhodnější prostory, které vyhovují socializaci štěňátek, loveckému výcviku a dalším specializovaným cvičením. U každého cvičení je vždy uvedené místo. Další místa výcviku lze individuálně dohodnout. V případě, že neřídíte, není problém se domluvit na odvozu… napište mejlíka.</p></div>
    <div class="split" style="align-items:stretch">
      <div class="map"><iframe title="Mapa — pozemek Nebušice" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox=14.3326%2C50.1015%2C14.3606%2C50.1141&amp;layer=mapnik&amp;marker=50.107810%2C14.346598"></iframe></div>
      <div class="places" style="margin-top:0;grid-template-columns:1fr">
        <div class="place"><h3>Pozemek Nebušice</h3><p>Lovecký výcvik, poslušnost. Nachází se na kraji městské části Praha – Nebušice v ulici Nad Habrovkou.</p><a class="chip" href="https://mapy.cz/zakladni?q=50.107810,14.346598" target="_blank" rel="noopener">50.107810, 14.346598 ↗</a></div>
        <div class="place"><h3>Hájovna Mrákavy</h3><p>Lovecký výcvik, poslušnost. Asi 20 km od Prahy: po karlovarské dálnici, sjezd na 16. km na obec Velká Dobrá, na kruhové křižovatce vlevo do obce Doksy a zde doprava na obec Srby. Na lesní křižovatce (stopka) opět doleva. Asi po 200 m po pravé straně stavení — zabočte, kde končí dřevěný plot (cedule zákaz vjezdu mimo vozidel LČR), rovně asi 100 m ke staré stodole, drátěnému plotu a patrovému šedivému domu.</p><p class="muted" style="font-size:.88rem">Prosíme, parkujte podél drátěného plotu, před stodolou či domem. Děkujeme.</p></div>
        <div class="place"><h3>Restaurace U Čechů</h3><p>Teorie.</p></div>
        <div class="place"><h3>Externí prostory</h3><p>Na specializované výcviky docházíme do domluvených honiteb poblíž Prahy. Pro hodiny poslušnosti a další lekce, kde nepotřebujeme honitbu, se scházíme na k tomu vhodných pozemcích. Vždy uvedeno u hodiny.</p></div>
      </div>
    </div>
  </div>
</section>'''
    page('o-nas/index.html', 'O nás — Lovecký výcvik psích plemen',
         'Kdo jsme, jak cvičíme, zkušenosti Ing. Zuzany Čechové, předvedení psi na loveckých zkouškách a místa výcviku — Nebušice, Hájovna Mrákavy.',
         body, 'o-nas/')


# ======================================================================
#  SLUŽBY
# ======================================================================
def build_sluzby():
    d = 1
    body = phead(d, 'Ostatní služby', 'Výstavy <em>a poradenství</em>', 'Předvedení psa na výstavě, výběr toho pravého štěňátka i individuální poradenství „šité Vám na míru“.', photo='voditko')
    body += f'''
<section class="section">
  <div class="wrap cards3">
    <article class="icard rv"><div class="icard-img">{img(d, 'vystava', 'Psi na výstavě', small=True)}</div><div class="icard-body">
      <span class="eyebrow">Výstavy</span><h3>Předvedení psa na výstavě</h3>
      <p>Nemáte čas objíždět výstavy? Připadáte si ve výstavním kruhu jak „slon v porcelánu“? Nevyznáte se v titulech, na výstavě jste zmatení a pejskovi to spíše kazíte?</p>
      <p>Svěřte nám Vašeho pejska. Jsme schopni zajistit dopravu na výstavu, předvedení, výstavní úpravu Vašeho pejska. Tuto službu jsme schopni zajistit i v době hlídání. Neváhejte zavolat či napsat a rádi dohodneme individuální podmínky.</p>
      <a class="link" href="../vycvik/#vystavy">Příprava na výstavy {ICON['arr']}</a></div></article>
    <article class="icard rv" style="--d:.08s"><div class="icard-img">{img(d, 'stene', 'Štěně s paničkou', small=True)}</div><div class="icard-body">
      <span class="eyebrow">Poradenství</span><h3>Výběr psa — hledáte „toho pravého“?</h3>
      <p>Přemýšlíte o štěňátku loveckého psa? Zvolíte psa či fenku? Nevíte si rady s výběrem konkrétního plemene? Nevyznáte se v mnoha zkratkách v inzerátech? Neznáte chovatelské stanice?</p>
      <p>Rádi Vám poradíme, sjednáme schůzku s chovateli, doporučíme pejska přesně pro Vás a dle Vašich požadavků… Neváhejte napsat či zavolat.</p>
      <a class="link" href="mailto:info@loveckyvycvik.cz">Napsat e-mail {ICON['arr']}</a></div></article>
    <article class="icard rv" style="--d:.16s"><div class="icard-img">{img(d, 'teorie', 'Poradenství v terénu', small=True)}</div><div class="icard-body">
      <span class="eyebrow">Poradenství</span><h3>Individuální poradenství „šité Vám na míru“</h3>
      <p>Potřebujete poradit ohledně hygieny, výchovy, výcviku? Máte konkrétní představu, problém, dotaz?</p>
      <p>Vzhledem k tomu, že se snažíme vyjít vstříc i těm, kterým nevyhovuje žádný z výše uvedených výcviků a služeb, jsme schopni si s vámi sjednat individuální schůzku a probrat, ukázat či poradit, řešit vaše problémy, dotazy a nejasnosti.</p>
      <a class="link" href="tel:+420777717271">Zavolat 777 717 271 {ICON['arr']}</a></div></article>
  </div>
</section>
<section class="section alt">
  <div class="wrap split">
    <div><span class="eyebrow">Pomůcky k prodeji</span><h2>LV Shop</h2>
      <p class="lead-p">Pomůcky pro výcvik nejen loveckého psa a chovatelské potřeby najdete v našem e-shopu.</p>
      <p style="margin-top:1.6rem"><a class="btn" href="https://www.lvshop.cz" target="_blank" rel="noopener">Otevřít lvshop.cz {ICON['arr-ur']}</a></p></div>
    <div><span class="eyebrow">Chov</span><h2>Chovatelská stanice Od Czechu</h2>
      <p class="lead-p">Chovatelská stanice na Facebooku — novinky o vrzích a odchovech.</p>
      <p style="margin-top:1.6rem"><a class="btn btn--ghost" href="https://www.facebook.com/Odczechu" target="_blank" rel="noopener">Facebook Od Czechu {ICON['arr-ur']}</a></p></div>
  </div>
</section>'''
    page('sluzby/index.html', 'Výstavy a poradenství — Lovecký výcvik psích plemen',
         'Předvedení psa na výstavě, výběr štěňátka loveckého psa, individuální poradenství, pomůcky k prodeji v LV Shopu.', body, '')


# ======================================================================
#  NOVINKY
# ======================================================================
def build_novinky():
    d = 1
    posts = ''
    for i, n in enumerate(DATA['news'][:14]):
        paras = ''.join(f'<p>{E(fix(p))}</p>' for p in n['body'] if not p.startswith('http'))
        im = ''
        if n['imgs']:
            src = n['imgs'][0]
            local = {'SENIORCUP.png': 'senior', 'LZ2.png': 'liska', 'VP.png': 'vodni-prace'}
            key = src.rsplit('/', 1)[-1]
            if key in local:
                im = f'<img src="../assets/img/{local[key]}-s.jpg" alt="" loading="lazy">'
        dd, mm, yy = n['date'].split('.')
        posts += f'<article class="post rv{" hidden-post" if i >= 8 else ""}"{" hidden" if i >= 8 else ""}><time datetime="{yy}-{int(mm):02d}-{int(dd):02d}">{int(dd)}. {int(mm)}. {yy}</time><div><h2>{E(fix(n["title"]))}</h2>{paras}{im}</div></article>'
    body = phead(d, 'Novinky', 'Novinky <em>z výcviku</em>', 'Rozvrh na tento týden, informace k akcím a především gratulace k úspěchům na zkouškách.')
    body += f'''
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="note note--warn" style="margin-bottom:2rem">{ICON['info']}<span><b>Vzhledem k naplnění kapacity nyní nebereme nové zájemce o výcvik.</b> Děkujeme za pochopení.</span></div>
    <div class="news">{posts}</div>
    <div class="post-more"><button class="btn btn--ghost" id="more-posts">Starší novinky</button></div>
  </div>
</section>'''
    page('novinky/index.html', 'Novinky — Lovecký výcvik psích plemen', 'Aktuality z výcviku: rozvrh, akce a úspěchy na loveckých zkouškách.', body, 'novinky/', light=True)


# ======================================================================
#  KONTAKT
# ======================================================================
def build_kontakt():
    d = 1
    docs = [
        ('Zkušební řády', 'http://www.cmmj.cz/Kynologie/Zkusebni-rady-%281%29.aspx', 'ČMMJ'),
        ('Termíny zkoušek a jarních svodů', 'http://www.cmmj.cz/Kynologie/Plan-kynologickych-akci.aspx', 'ČMMJ'),
        ('Termíny výstav', 'http://www.cmku.cz/index2.php?stranka=vystavy', 'ČMKU'),
        ('Přihláška na jarní svod loveckých psů', 'http://www.loveckyvycvik.cz/web/images/stories/10.1.2012/Prihlaska-Jarni-svod.jpg', 'obrázek'),
        ('Přihláška na zkoušky loveckých psů', 'http://www.loveckyvycvik.cz/web/images/stories/9.5.2012/prihlaskazkousky.jpg', 'obrázek'),
        ('Více dokumentů ke stažení OMS Kladno', 'http://www.omskladno.cz/dokumenty-ke-stazeni/', 'OMS Kladno'),
    ]
    body = phead(d, 'Kontakt', 'Napište <em>nebo zavolejte</em>', 'Nejrychleji nás zastihnete e-mailem. Pokud na vás máme telefon, o změnách kvůli počasí dáváme vědět SMS.')
    body += f'''
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="contact-grid">
      <div class="ccard rv"><h3>E-mail</h3><a class="big" href="mailto:info@loveckyvycvik.cz">info@<wbr>loveckyvycvik.cz</a></div>
      <div class="ccard rv" style="--d:.08s"><h3>Telefon</h3><a class="big" href="tel:+420777717271">+420 777 717 271</a></div>
      <div class="ccard rv" style="--d:.16s"><h3>Sociální sítě</h3><p><a class="link" href="https://www.facebook.com/loveckyvycvik.cz/" target="_blank" rel="noopener">Facebook {ICON['arr-ur']}</a></p><p style="margin-top:.4rem"><a class="link" href="https://loveckyvycvikcz.rajce.idnes.cz/" target="_blank" rel="noopener">Galerie na Rajčeti {ICON['arr-ur']}</a></p></div>
      <div class="ccard rv"><h3>Sídlo</h3><p><b>LoveckyVycvik s.r.o.</b><br>Kamenné Žehrovice 37<br>273 01<br>IČO: 225 44 496</p></div>
      <div class="ccard rv" style="--d:.08s"><h3>Korespondenční adresa</h3><p>Ing. Zuzana Čechová<br>K Vinicím 215<br>Praha 6 – Nebušice<br>164 00</p></div>
      <div class="ccard rv" style="--d:.16s"><h3>Platby</h3><p>Číslo účtu<br><b style="font-family:var(--display);font-size:1.3rem;font-weight:400">3291709012/3030</b></p><p style="margin-top:.4rem"><a class="link" href="../cenik/">Ceník a permanentky {ICON['arr']}</a></p></div>
    </div>
  </div>
</section>
<section class="section alt" id="dokumenty">
  <div class="wrap split">
    <div><span class="eyebrow">Dokumenty a termíny</span><h2>Předpisy, řády, termíny</h2><p class="muted">Zkušební řády, plány kynologických akcí a přihlášky na svody a zkoušky ke stažení.</p><p style="margin-top:1.4rem"><a class="link" href="../akce/">Náš kalendář akcí 2026 {ICON['arr']}</a></p></div>
    <div>{''.join(f'<a class="prow" href="{E(u)}" target="_blank" rel="noopener" style="text-decoration:none"><span>{t}</span><i></i><b style="font-family:var(--body);font-size:.85rem;color:var(--muted)">{s} ↗</b></a>' for t, u, s in docs)}</div>
  </div>
</section>'''
    page('kontakt/index.html', 'Kontakt — Lovecký výcvik psích plemen',
         'LoveckyVycvik s.r.o., Kamenné Žehrovice 37. Ing. Zuzana Čechová, info@loveckyvycvik.cz, +420 777 717 271.', body, 'kontakt/', light=True)


def build_404():
    doc = head('Stránka nenalezena — Lovecký výcvik', 'Stránka nenalezena.', 0).replace('href="assets/', 'href="/loveckyvycvik/assets/').replace('content="assets/', 'content="/loveckyvycvik/assets/')
    doc += '''<body><main class="not-found"><div><img src="/loveckyvycvik/assets/logo-light.svg" alt="" width="120" style="margin:0 auto 1.5rem"><h1>404</h1><p style="margin:1rem 0 2rem">Tahle stopa nikam nevede.</p><a class="btn" href="/loveckyvycvik/">Zpět na úvod</a></div></main></body></html>'''
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(doc)


if __name__ == '__main__':
    # nejdřív data (akce.json, lekce.json, klienti.json), pak stránky, které na ně odkazují hashem
    build_akce(); build_rozvrh(); build_klienti()
    build_home(); build_vycvik(); build_registrace(); build_cenik(); build_onas(); build_sluzby(); build_novinky(); build_kontakt(); build_404()
    print('hotovo')
