# -*- coding: utf-8 -*-
"""FORGE static site builder. Run: python3 build.py   (writes into ./dist)"""
import os, re, shutil, html, json
from content import LANGS, SVC

# ---------------- configuration: edit these before launch ----------------
SITE_URL = "https://forge.example"      # final domain, no trailing slash
EMAIL = "hello@forge.example"           # company email
WHATSAPP = ""                           # international digits only, e.g. "201001234567"
FORM_ENDPOINT = ""                      # e.g. a Formspree URL; empty = opens visitor's email app
# --------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
KIT = "/mnt/user-data/outputs/FORGE-Brand-Kit"
PAGES = ["home", "services", "work", "about", "contact"]
e = html.escape

def depth(page, lang): return (1 if lang == "ar" else 0) + (0 if page == "home" else 1)
def pre(page, lang): return "../" * depth(page, lang)
def path_of(page, lang):  # path from site root, folder style
    p = ("ar/" if lang == "ar" else "") + ("" if page == "home" else page + "/")
    return p
def link(frm_page, frm_lang, to_page, to_lang, anchor=""):
    rel = pre(frm_page, frm_lang) + path_of(to_page, to_lang)
    return (rel or "./") + anchor
def abs_url(page, lang): return SITE_URL + "/" + path_of(page, lang)

SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-web" viewBox="0 0 24 24"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></symbol>
<symbol id="i-mobile" viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 5h4M11 19h2"/></symbol>
<symbol id="i-systems" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="8.5" y="14" width="7" height="7"/><path d="M6.5 10v2h11v-2M12 12v2"/></symbol>
<symbol id="i-ai" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><circle cx="4" cy="5" r="2"/><circle cx="20" cy="5" r="2"/><circle cx="4" cy="19" r="2"/><circle cx="20" cy="19" r="2"/><path d="m5.5 6.3 4 3.5M18.5 6.3l-4 3.5M5.5 17.7l4-3.5M18.5 17.7l-4-3.5"/></symbol>
<symbol id="i-cloud" viewBox="0 0 24 24"><path d="M7 18h10a4 4 0 0 0 .6-8A6 6 0 0 0 6 8.5 4.8 4.8 0 0 0 7 18Z"/><path d="m9 14 3-3 3 3M12 11v7"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
<symbol id="i-chat" viewBox="0 0 24 24"><path d="M20 11.5a8 8 0 0 1-11.8 7L3 20l1.5-5.1A8 8 0 1 1 20 11.5Z"/><path d="M8 10h8M8 14h5"/></symbol>
</defs></svg>"""
def ic(name, cls="icon", flip=False):
    return f'<svg class="{cls}{" flip" if flip else ""}" aria-hidden="true"><use href="#i-{name}"/></svg>'

HERO_ART = """<svg viewBox="250 170 420 500" role="img" aria-label="FORGE symbol"><defs>
<clipPath id="hc"><path d="M305 458 L565 332 L565 398 Q565 418 548 428 L408 490 L408 560 Q408 575 392 583 L305 630 Z"/></clipPath>
<radialGradient id="hg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#F97316"/><stop offset="1" stop-color="#F97316" stop-opacity="0"/></radialGradient></defs>
<path fill="#E5E7EB" d="M305 352 Q305 332 325 325 L608 203 L608 262 Q608 282 590 292 L305 422 Z"/>
<path fill="#FFFFFF" d="M305 458 L565 332 L565 398 Q565 418 548 428 L408 490 L408 560 Q408 575 392 583 L305 630 Z"/>
<path class="ember" fill="#F97316" d="M305 442 L305 428 L372 390 L520 338 L440 376 Z"/>
<g clip-path="url(#hc)"><ellipse class="glow" cx="440" cy="458" rx="64" ry="30" transform="rotate(-24 440 458)" fill="url(#hg)"/></g></svg>"""

PREVIEW = {
 "restaurant": """<svg viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="400" height="250" fill="#F3F4F6"/>
<rect x="120" y="14" width="160" height="236" rx="16" fill="#fff" stroke="#111827" stroke-width="2"/><rect x="132" y="28" width="136" height="18" rx="3" fill="#111827"/>
<g fill="#E5E7EB"><rect x="132" y="56" width="40" height="14" rx="7"/><rect x="176" y="56" width="40" height="14" rx="7"/><rect x="220" y="56" width="40" height="14" rx="7"/></g><rect x="132" y="56" width="40" height="14" rx="7" fill="#F97316"/>
<g><rect x="132" y="82" width="136" height="34" rx="4" fill="#F3F4F6"/><rect x="138" y="90" width="70" height="6" fill="#111827"/><rect x="138" y="102" width="46" height="5" fill="#9CA3AF"/><rect x="236" y="92" width="26" height="16" rx="3" fill="#111827"/>
<rect x="132" y="122" width="136" height="34" rx="4" fill="#F3F4F6"/><rect x="138" y="130" width="86" height="6" fill="#111827"/><rect x="138" y="142" width="52" height="5" fill="#9CA3AF"/><rect x="236" y="132" width="26" height="16" rx="3" fill="#111827"/>
<rect x="132" y="162" width="136" height="34" rx="4" fill="#F3F4F6"/><rect x="138" y="170" width="60" height="6" fill="#111827"/><rect x="138" y="182" width="40" height="5" fill="#9CA3AF"/><rect x="236" y="172" width="26" height="16" rx="3" fill="#111827"/></g>
<rect x="132" y="214" width="136" height="24" rx="4" fill="#F97316"/>
<rect x="300" y="60" width="84" height="120" rx="4" fill="#fff" stroke="#E5E7EB"/><rect x="308" y="70" width="40" height="6" fill="#111827"/><rect x="308" y="86" width="68" height="14" rx="2" fill="#F3F4F6"/><rect x="308" y="106" width="68" height="14" rx="2" fill="#F3F4F6"/><rect x="308" y="126" width="68" height="14" rx="2" fill="#F97316" opacity=".25"/></svg>""",
 "clinic": """<svg viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="400" height="250" fill="#F3F4F6"/>
<rect x="20" y="20" width="360" height="210" rx="6" fill="#fff" stroke="#E5E7EB"/><rect x="20" y="20" width="62" height="210" rx="6" fill="#111827"/>
<rect x="32" y="36" width="38" height="8" fill="#fff"/><g fill="#6B7280"><rect x="32" y="64" width="38" height="6"/><rect x="32" y="82" width="38" height="6"/><rect x="32" y="100" width="38" height="6"/></g><rect x="32" y="64" width="38" height="6" fill="#F97316"/>
<g><rect x="98" y="36" width="72" height="44" rx="4" fill="#F3F4F6"/><rect x="108" y="46" width="30" height="5" fill="#9CA3AF"/><rect x="108" y="58" width="40" height="12" fill="#111827"/>
<rect x="180" y="36" width="72" height="44" rx="4" fill="#F3F4F6"/><rect x="190" y="46" width="30" height="5" fill="#9CA3AF"/><rect x="190" y="58" width="32" height="12" fill="#111827"/>
<rect x="262" y="36" width="104" height="44" rx="4" fill="#111827"/><rect x="272" y="46" width="40" height="5" fill="#D1D5DB"/><rect x="272" y="58" width="52" height="12" fill="#F97316"/></g>
<g fill="#111827"><rect x="104" y="196" width="14" height="22"/><rect x="128" y="176" width="14" height="42"/><rect x="152" y="186" width="14" height="32"/><rect x="176" y="160" width="14" height="58"/><rect x="200" y="170" width="14" height="48"/></g><rect x="224" y="150" width="14" height="68" fill="#F97316"/>
<g><rect x="262" y="96" width="104" height="14" rx="2" fill="#F3F4F6"/><rect x="262" y="116" width="104" height="14" rx="2" fill="#F3F4F6"/><rect x="262" y="136" width="104" height="14" rx="2" fill="#F3F4F6"/><rect x="262" y="156" width="104" height="14" rx="2" fill="#F3F4F6"/></g></svg>""",
}

def dark_preview(svg):
    m = {"#F3F4F6": "#1B1B20", "#fff": "#141418", "#E5E7EB": "#2A2A30", "#111827": "#F4F4F5", "#9CA3AF": "#71717A"}
    svg = re.sub(r'(fill|stroke)="(#[0-9A-Fa-f]{3,6})"', lambda x: f'{x.group(1)}="{m.get(x.group(2), x.group(2))}"', svg)
    return svg.replace('stroke="#F4F4F5" stroke-width="2"', 'stroke="#3F3F46" stroke-width="2"')
PREVIEW.update({k: dark_preview(v) for k, v in PREVIEW.items()})

def head(page, lang, C):
    title, desc = C["meta"][page]
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{abs_url(page, l)}">' for l in ("en", "ar"))
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{abs_url(page, "en")}">'
    p = pre(page, lang)
    ld = ""
    if page == "home":
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "FORGE", "url": SITE_URL + "/", "logo": SITE_URL + "/assets/img/logo.svg", "email": EMAIL, "slogan": "We Forge Ideas Into Reality."}) + '</script>'
    return f"""<!DOCTYPE html>
<html lang="{C['lang']}" dir="{C['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{abs_url(page, lang)}">
{alts}
<meta property="og:type" content="website"><meta property="og:site_name" content="FORGE">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{abs_url(page, lang)}"><meta property="og:locale" content="{C['locale']}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B0B0D"><meta name="color-scheme" content="dark">
<link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/css/site.css">
{ld}
</head>"""

def header(page, lang, C):
    L = lambda pg: link(page, lang, pg, lang)
    other = "ar" if lang == "en" else "en"
    nav = "".join(f'<a href="{L(pg)}"{" aria-current=\"page\"" if pg == page else ""}>{e(C["nav"][pg])}</a>' for pg in PAGES)
    mnav = nav + f'<a class="btn btn-primary" href="{L("contact")}">{e(C["start"])}</a>'
    p = pre(page, lang)
    return f"""<body>
<a class="skip" href="#main">{e(C['skip'])}</a>
{SPRITE}
<header class="site-header"><div class="container header-inner">
<a class="brand" href="{L('home')}" aria-label="FORGE"><img src="{p}assets/img/logo-white.svg" alt="FORGE" width="132" height="34"></a>
<nav class="nav" aria-label="Main">{nav}</nav>
<div class="header-actions">
<a class="lang" href="{link(page, lang, page, other)}" hreflang="{other}" lang="{other}" aria-label="{e(C['switch_aria'])}">{e(C['switch_label'])}</a>
<a class="btn btn-primary header-cta" href="{L('contact')}">{e(C['start'])}</a>
<button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu"><span class="sr-only" id="menu-label">{e(C['menu_open'])}</span><span class="menu-lines" aria-hidden="true"></span></button>
</div></div>
<div class="mobile-menu" id="mobile-menu" hidden><nav class="container" aria-label="Mobile">{mnav}</nav></div>
</header>
<main id="main">"""

def footer(page, lang, C):
    L = lambda pg, a="": link(page, lang, pg, lang, a)
    p = pre(page, lang)
    svc_links = "".join(f'<li><a href="{L("services", "#" + s)}">{e(C["services"][s]["name"])}</a></li>' for s in SVC)
    nav_links = "".join(f'<li><a href="{L(pg)}">{e(C["nav"][pg])}</a></li>' for pg in PAGES)
    demos = f'<li><a href="{p}demos/restaurant/">{e(C["work"]["restaurant"]["name"])}</a></li><li><a href="{p}demos/clinic/">{e(C["work"]["clinic"]["name"])}</a></li>'
    js = dict(C["js"])
    cfg = json.dumps({"email": EMAIL, "whatsapp": WHATSAPP, "formEndpoint": FORM_ENDPOINT})
    return f"""</main>
<footer class="site-footer"><div class="container">
<div class="footer-grid">
<div><a class="brand" href="{L('home')}" aria-label="FORGE"><img src="{p}assets/img/logo-white.svg" alt="FORGE" width="136" height="36"></a><p class="tag-line">{e(C['tagline'])}</p></div>
<div><h2>{e(C['footer_nav'])}</h2><ul>{nav_links}</ul></div>
<div><h2>{e(C['footer_svc'])}</h2><ul>{svc_links}</ul></div>
<div><h2>{e(C['footer_demo'])}</h2><ul>{demos}</ul></div>
</div>
<div class="footer-bottom"><span>© 2026 FORGE. {e(C['rights'])}</span><span dir="ltr">{e(EMAIL)}</span></div>
</div></footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>window.FORGE_CONFIG={cfg};window.FORGE_STRINGS={json.dumps(js, ensure_ascii=False)};</script>
<script src="{p}assets/js/site.js" defer></script>
</body></html>"""

def cta_block(page, lang, title, body, C):
    return f"""<section class="cta-wrap"><div class="container"><div class="cta">
<div><h2>{e(title)}</h2><p>{e(body)}</p></div>
<a class="btn btn-primary" href="{link(page, lang, 'contact', lang)}">{e(C['start'])}</a></div></div></section>"""

def work_cards(page, lang, C):
    p = pre(page, lang); W = C["work"]; out = []
    for key in ("restaurant", "clinic"):
        w = W[key]
        out.append(f"""<article class="work-card">
<div class="work-media">{PREVIEW[key]}</div>
<div class="work-body"><span class="badge">{e(w['badge'])}</span><h3>{e(w['name'])}</h3><p class="muted">{e(w['summary'])}</p>
<div class="actions"><a class="btn btn-dark" href="{p}demos/{key}/">{e(W['open'])}</a><a class="link" href="{link(page, lang, 'work', lang, '#' + key)}">{e(C['explore_svc'])}</a></div></div></article>""")
    return "".join(out)

def build_home(lang, C):
    h = C["home"]; p = "home"
    aud = "".join(f"<li>{e(x)}</li>" for x in h["aud"])
    rows = "".join(f"""<li><span class="ico">{ic(s)}</span><h3>{e(C['services'][s]['name'])}</h3><p>{e(C['services'][s]['short'])}</p>
<a class="link" href="{link(p, lang, 'services', lang, '#' + s)}">{e(C['explore_svc'])}</a></li>""" for s in SVC)
    steps = "".join(f'<li><span class="n">{i+1:02d}</span><div><h3>{e(h[k][0])}</h3><p>{e(h[k][1])}</p></div></li>' for i, k in enumerate(("p1", "p2", "p3")))
    body = f"""<section class="hero"><div class="container hero-grid">
<div><h1 class="display">{e(h['h1'])}</h1><p class="lead">{e(h['lead'])}</p>
<div class="actions"><a class="btn btn-primary" href="{link(p, lang, 'contact', lang)}">{e(C['start'])}</a><a class="btn btn-dark" href="{link(p, lang, 'services', lang)}">{e(C['explore'])}</a></div></div>
<figure class="hero-art">{HERO_ART}<figcaption>{e(h['art_cap'])}</figcaption></figure></div></section>
<section class="audience" aria-label="{e(h['aud_title'])}"><div class="container"><ul>{aud}</ul></div></section>
<section class="section tint"><div class="container split">
<div><span class="rule"></span><h2 class="h2">{e(h['svc_title'])}</h2><p class="lead" style="margin-block:18px 26px">{e(h['svc_body'])}</p><a class="link" href="{link(p, lang, 'services', lang)}">{e(C['all_services'])}</a></div>
<ul class="rows">{rows}</ul></div></section>
<section class="section"><div class="container">
<div class="head"><div><span class="rule"></span><h2 class="h2">{e(h['work_title'])}</h2></div><p class="lead">{e(h['work_body'])}</p></div>
<div class="works">{work_cards(p, lang, C)}</div></div></section>
<section class="section tint"><div class="container split">
<div><span class="rule"></span><h2 class="h2">{e(h['proc_title'])}</h2><p class="lead" style="margin-block:18px 26px">{e(h['proc_body'])}</p><a class="link" href="{link(p, lang, 'about', lang)}">{e(h['about_link'])}</a></div>
<ol class="steps">{steps}</ol></div></section>
<div style="height:var(--space)" aria-hidden="true"></div>
{cta_block(p, lang, h['cta_t'], h['cta_b'], C)}"""
    return body

def build_services(lang, C):
    S = C["services"]; p = "services"
    jump = "".join(f'<li><a href="#{s}">{e(S[s]["name"])}</a></li>' for s in SVC)
    secs = []
    for i, s in enumerate(SVC):
        d = S[s]
        gets = "".join(f'<li>{ic("check")}<span>{e(g)}</span></li>' for g in d["gets"])
        secs.append(f"""<section class="section{' tint' if i % 2 else ''}" id="{s}" aria-labelledby="{s}-t"><div class="container svc">
<div><h2 id="{s}-t">{e(d['name'])}</h2><p class="lead summary">{e(d['summary'])}</p><h3 class="sr-only">{e(S['get'])}</h3><ul class="checks">{gets}</ul></div>
<aside class="fit"><h3>{e(S['fit'])}</h3><p>{e(d['fit'])}</p><a class="link" href="{link(p, lang, 'contact', lang)}?service={s}">{e(d['cta'])}</a></aside></div></section>""")
    return f"""<section class="page-hero"><div class="container"><span class="rule"></span><h1>{e(S['h1'])}</h1><p class="lead">{e(S['lead'])}</p></div></section>
<nav class="jump" aria-label="{e(S['index'])}"><div class="container"><ul>{jump}</ul></div></nav>
{''.join(secs)}
<div style="height:var(--space)" aria-hidden="true"></div>
{cta_block(p, lang, C['home']['cta_t'], C['home']['cta_b'], C)}"""

def build_work(lang, C):
    W = C["work"]; p = "work"; pp = pre(p, lang); blocks = []
    for key in ("restaurant", "clinic"):
        w = W[key]
        feats = "".join(f'<li>{ic("check")}<span>{e(x)}</span></li>' for x in w["feats"])
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in w["tech"])
        blocks.append(f"""<article class="project" id="{key}"><div>
<span class="badge">{e(w['badge'])}</span><h2>{e(w['name'])}</h2><p class="lead">{e(w['summary'])}</p>
<dl><div><dt>{e(W['problem'])}</dt><dd>{e(w['problem'])}</dd></div><div><dt>{e(W['solution'])}</dt><dd>{e(w['solution'])}</dd></div></dl>
<h3>{e(W['features'])}</h3><ul class="checks">{feats}</ul>
<div class="tags" aria-label="{e(W['tech'])}">{tags}</div>
<div class="actions"><a class="btn btn-primary" href="{pp}demos/{key}/">{e(W['open'])}</a><a class="link" href="{link(p, lang, 'contact', lang)}?project={key}">{e(W['similar'])}</a></div>
<p class="small" style="margin-block-start:14px">{e(W['demo_note'])}</p></div>
<div class="work-media">{PREVIEW[key]}</div></article>""")
    return f"""<section class="page-hero tint section" style="background:var(--light)"><div class="container"><span class="rule"></span><h1>{e(W['h1'])}</h1><p class="lead">{e(W['lead'])}</p></div></section>
<section class="section" style="padding-block-end:0"><div class="container"><div class="notice">{ic('info')}<p>{e(W['notice'])}</p></div>
{''.join(blocks)}</div></section>
<div style="height:var(--space)" aria-hidden="true"></div>
{cta_block(p, lang, W['cta_t'], W['cta_b'], C)}"""

def build_about(lang, C):
    A = C["about"]; p = "about"
    pr = "".join(f"<li>{e(x)}</li>" for x in A["pr"])
    vals = "".join(f"<li><h3>{e(a)}</h3><p>{e(b)}</p></li>" for a, b in A["vals"])
    steps = "".join(f'<li><span class="n">{i+1:02d}</span><div><h3>{e(a)}</h3><p>{e(b)}</p><span class="out"><strong>{e(A["out"])}</strong> {e(c)}</span></div></li>' for i, (a, b, c) in enumerate(A["steps"]))
    return f"""<section class="page-hero dark on-dark"><div class="container about-hero"><div><span class="rule"></span><h1>{e(A['h1'])}</h1><p class="lead">{e(A['lead'])}</p>
<a class="btn btn-primary" href="{link(p, lang, 'contact', lang)}">{e(C['start'])}</a></div><ul class="principles" style="margin-block-start:34px">{pr}</ul></div></section>
<section class="section"><div class="container split"><div><span class="rule"></span><h2 class="h2">{e(A['story_t'])}</h2></div><div class="story"><p>{e(A['s1'])}</p><p>{A['s2']}</p></div></div></section>
<section class="section tint"><div class="container"><div class="head"><div><span class="rule"></span><h2 class="h2">{e(A['phil_t'])}</h2></div></div><ul class="values">{vals}</ul></div></section>
<section class="section"><div class="container split"><div><span class="rule"></span><h2 class="h2">{e(A['proc_t'])}</h2></div><ol class="steps">{steps}</ol></div></section>
{cta_block(p, lang, C['home']['cta_t'], C['home']['cta_b'], C)}"""

def build_contact(lang, C):
    K = C["contact"]; S = C["services"]
    opts = f'<option value="">{e(K["svc_none"])}</option>' + "".join(f'<option value="{s}">{e(S[s]["name"])}</option>' for s in SVC)
    nxt = "".join(f'<li><span>{i+1:02d}</span><div><strong>{e(a)}</strong><p>{e(b)}</p></div></li>' for i, (a, b) in enumerate(K["next"]))
    wa = f'<a class="btn wa" href="#" data-whatsapp>{ic("chat")}<span>{e(K["wa_btn"])}</span></a>'
    wa_note = "" if WHATSAPP else f'<span class="note">{e(K["wa_note"])}</span>'
    mail_note = "" if EMAIL != "hello@forge.example" else f'<span class="note">{e(K["mail_note"])}</span>'
    return f"""<section class="page-hero"><div class="container"><span class="rule"></span><h1>{e(K['h1'])}</h1><p class="lead">{e(K['lead'])}</p></div></section>
<section class="section tint" style="padding-block-start:clamp(2.5rem,5vw,4rem)"><div class="container contact-grid">
<div class="panel"><h2>{e(K['form_t'])}</h2><p class="muted" style="margin-block-start:8px;font-size:14px">{e(K['form_i'])}</p>
<form class="form" id="contact-form" novalidate>
<div class="row2">
<div class="field"><label for="f-name">{e(K['name'])} *</label><input id="f-name" name="name" autocomplete="name" required placeholder="{e(K['name_ph'])}" aria-describedby="f-name-err"><span class="err" id="f-name-err"></span></div>
<div class="field"><label for="f-email">{e(K['email'])} *</label><input class="ltr" id="f-email" name="email" type="email" autocomplete="email" required placeholder="{e(K['email_ph'])}" aria-describedby="f-email-err"><span class="err" id="f-email-err"></span></div></div>
<div class="row2">
<div class="field"><label for="f-phone">{e(K['phone'])} <span class="opt">{e(K['optional'])}</span></label><input class="ltr" id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="{e(K['phone_ph'])}" aria-describedby="f-phone-err"><span class="err" id="f-phone-err"></span></div>
<div class="field"><label for="f-service">{e(K['service'])}</label><select id="f-service" name="service">{opts}</select></div></div>
<div class="field"><label for="f-message">{e(K['message'])} *</label><textarea id="f-message" name="message" required placeholder="{e(K['msg_ph'])}" aria-describedby="f-message-err"></textarea><span class="err" id="f-message-err"></span></div>
<p class="small">{e(K['privacy'])}</p><div class="status" id="form-status" role="status" aria-live="polite"></div>
<button class="btn btn-primary" type="submit">{e(K['submit'])}</button></form></div>
<aside class="panel dark on-dark"><h2>{e(K['direct_t'])}</h2><p style="margin-block-start:8px;color:var(--muted-dark);font-size:14px">{e(K['direct_b'])}</p>
<div class="direct"><div><span class="lbl">{e(K['wa_label'])}</span>{wa}{wa_note}</div>
<div><span class="lbl">{e(K['mail_label'])}</span><a class="mail" href="mailto:{EMAIL}">{e(EMAIL)}</a>{mail_note}</div></div>
<div class="next"><h3>{e(K['next_t'])}</h3><ol>{nxt}</ol></div></aside></div></section>"""

BUILDERS = {"home": build_home, "services": build_services, "work": build_work, "about": build_about, "contact": build_contact}

def write(rel, text):
    fp = os.path.join(DIST, rel); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(text)

def build_assets():
    import cairosvg
    img = os.path.join(DIST, "assets", "img"); os.makedirs(img, exist_ok=True)
    def strip_tag(svg, color):  # remove outlined tagline path, crop to symbol + wordmark
        svg = re.sub(r'<path fill="%s" d="[^"]*"/>' % color, "", svg)
        return re.sub(r'viewBox="[^"]*"', 'viewBox="295 195 1210 445"', svg, count=1)
    def clean(s):  # the output folder adds C2PA provenance metadata to SVGs; drop it from the site files
        s = re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)
        return re.sub(r' xmlns:c2pa="[^"]*"', "", s)
    prim = clean(open(f"{KIT}/logo/svg/forge-logo-primary.svg").read())
    wht = clean(open(f"{KIT}/logo/svg/forge-logo-white.svg").read())
    open(f"{img}/logo.svg", "w").write(strip_tag(prim, "#374151"))
    open(f"{img}/logo-white.svg", "w").write(strip_tag(wht, "#D1D5DB"))
    open(f"{img}/favicon.svg", "w").write(clean(open(f"{KIT}/icons/forge-icon.svg").read()))
    cairosvg.svg2png(bytestring=clean(open(f"{KIT}/icons/forge-app-icon.svg").read()).encode(), write_to=f"{img}/apple-touch-icon.png", output_width=180)
    inner = re.search(r'<svg[^>]*>(.*)</svg>', wht, re.S).group(1)
    og = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#111827"/><g transform="translate(130 140) scale(.74) translate(-240 -150)">{inner}</g><rect y="620" width="1200" height="10" fill="#F97316"/></svg>'
    cairosvg.svg2png(bytestring=og.encode(), write_to=f"{img}/og-image.png", output_width=1200)
    for sub, name in (("css", "site.css"), ("js", "site.js")):
        os.makedirs(os.path.join(DIST, "assets", sub), exist_ok=True)
        shutil.copy(os.path.join(ROOT, "assets", sub, name), os.path.join(DIST, "assets", sub, name))

def build_extra():
    urls = ""
    for pg in PAGES:
        for l in ("en", "ar"):
            urls += f'<url><loc>{abs_url(pg, l)}</loc>' + "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{abs_url(pg, x)}"/>' for x in ("en", "ar")) + '</url>\n'
    for d in ("restaurant", "clinic"):
        urls += f'<url><loc>{SITE_URL}/demos/{d}/</loc></url>\n'
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    write("404.html", """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | FORGE</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#111827;color:#fff;font-family:Inter,system-ui,sans-serif;text-align:center;padding:24px}h1{font-size:clamp(2rem,6vw,3.5rem);margin:0 0 12px}p{color:#D1D5DB;margin:0 0 24px}a{display:inline-block;background:#F97316;color:#111827;font-weight:700;padding:14px 24px;border-radius:4px;text-decoration:none}</style></head>
<body><main><h1>We couldn’t find that page.</h1><p>الصفحة غير موجودة.</p><a href="/">Back to FORGE</a></main></body></html>""")

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    for lang, C in LANGS.items():
        for pg in PAGES:
            doc = head(pg, lang, C) + header(pg, lang, C) + BUILDERS[pg](lang, C) + footer(pg, lang, C)
            write(path_of(pg, lang) + "index.html", doc)
    build_assets(); build_extra()
    demos = os.path.join(ROOT, "demos")
    if os.path.isdir(demos): shutil.copytree(demos, os.path.join(DIST, "demos"))
    print("built", sum(len(f) for _, _, f in os.walk(DIST)), "files")

if __name__ == "__main__":
    main()
