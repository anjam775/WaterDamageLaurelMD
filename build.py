#!/usr/bin/env python3
"""Static site builder for Laurel Dry Pros. Reads src/content/*.md (TOML front matter + Markdown) -> site/."""
import base64, hashlib, html, json, os, re, shutil, subprocess, sys, tomllib
from pathlib import Path
import markdown
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "site"
sys.path.insert(0, str(SRC))
from data import *  # noqa
import icons

E = html.escape
MD = markdown.Markdown(extensions=["tables", "attr_list", "md_in_html", "sane_lists"])

# ---------------------------------------------------------------- helpers
def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{}:;,>])\s*", r"\1", s)
    return s.replace(";}", "}").strip()

def minify_html(s):
    parts = re.split(r"(<script[^>]*>.*?</script>|<pre>.*?</pre>|<textarea[^>]*>.*?</textarea>)", s, flags=re.S)
    out = []
    for p in parts:
        if p.startswith(("<script", "<pre", "<textarea")):
            if p.startswith('<script type="application/ld+json"'):
                m = re.match(r'(<script[^>]*>)(.*)(</script>)', p, re.S)
                p = m.group(1) + json.dumps(json.loads(m.group(2)), separators=(",", ":"), ensure_ascii=False) + m.group(3)
            out.append(p)
        else:
            p = re.sub(r">\s+<", "> <", p)
            p = re.sub(r"\s{2,}", " ", p)
            out.append(p)
    return "".join(out).strip()

def read_md(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"\+\+\+\n(.*?)\n\+\+\+\n(.*)", raw, re.S)
    fm = tomllib.loads(m.group(1)); body = m.group(2)
    return fm, body

def call_btn(loc="inline", label=None, cls="btn btn-call"):
    label = label or f"Call {PHONE}"
    return f'<a class="{cls}" href="tel:{TEL}" data-loc="{loc}">{icons.PHONE}<span class="t">{E(label)}</span></a>'

def directives(body):
    """Custom line directives -> HTML (before Markdown)."""
    out = []
    lines = body.split("\n"); i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("!quick "):
            out.append(f'<div class="quick" markdown="1">\n\n**Quick answer:** {ln[7:]}\n\n</div>')
        elif ln.startswith("!short "):
            out.append(f'<div class="short" markdown="1">\n\n**Short answer:** {ln[7:]}\n\n</div>')
        elif ln.startswith("!cta "):
            out.append(f'<div class="cta-box"><p>{inline(ln[5:])}</p>{call_btn("cta")}</div>')
        elif ln.strip() == "!checks":
            block = []; i += 1
            while i < len(lines) and lines[i].strip():
                block.append(lines[i]); i += 1
            out.append('<div class="checks-wrap" markdown="1">\n\n' + "\n".join(block) + '\n\n</div>')
            continue
        elif ln.startswith("!") and re.match(r"!\w[\w-]*$", ln.strip()):
            out.append(f"<!--AUTO:{ln.strip()[1:]}-->")
        else:
            out.append(ln)
        i += 1
    return "\n".join(out)

def inline(s):
    return markdown.markdown(s).removeprefix("<p>").removesuffix("</p>")

def render_md(body):
    MD.reset()
    h = MD.convert(directives(body))
    h = h.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    # checklists: lists inside checks-wrap get class
    h = re.sub(r'<div class="checks-wrap">\s*<ul>', '<ul class="checks">', h)
    h = re.sub(r'(<ul class="checks">.*?</ul>)\s*</div>', r"\1", h, flags=re.S)
    h = re.sub(r"<ol>", '<ol class="steps">', h)
    # external links open new tab
    h = re.sub(r'<a href="(https?://(?!waterdamagerestorationlaurelmd)[^"]+)"', r'<a href="\1" target="_blank" rel="noopener">', h)
    return h

# ---------------------------------------------------------------- glossary
GLOSS = tomllib.loads((SRC / "glossary.toml").read_text())["term"]
GLOSS_SORTED = sorted(GLOSS, key=lambda t: -len(t["term"]))

def gloss_apply(html_main, self_path, limit=4):
    """Simpler, reliable implementation: string-level replace inside <p> blocks only."""
    used = 0; done = set(); out = []
    pos = 0
    for m in re.finditer(r"<p>(.*?)</p>", html_main, re.S):
        out.append(html_main[pos:m.start()]); pos = m.end()
        para = m.group(1)
        if used < limit and "<strong>Quick answer" not in para and "<strong>Short answer" not in para:
            for t in GLOSS_SORTED:
                if used >= limit: break
                if t["slug"] in done or t.get("link") == self_path: continue
                # split para into tag/text tokens, skip text inside <a>
                toks = re.split(r"(<[^>]+>)", para); depth = 0; hit = False
                for k, tok in enumerate(toks):
                    if tok.startswith("<a ") or tok == "<a>": depth += 1; continue
                    if tok == "</a>": depth -= 1; continue
                    if tok.startswith("<") or depth: continue
                    mm = re.search(r"\b(" + re.escape(t["term"]) + r"(?:s|es)?)\b", tok, re.I)
                    if mm:
                        toks[k] = tok[:mm.start()] + f'<a href="/glossary/#{t["slug"]}">{mm.group(1)}</a>' + tok[mm.end():]
                        hit = True; break
                if hit:
                    para = "".join(toks); done.add(t["slug"]); used += 1
        out.append(f"<p>{para}</p>")
    out.append(html_main[pos:])
    return "".join(out)

# ---------------------------------------------------------------- layout
CRIT = minify_css((SRC / "critical.css").read_text())
CRIT_HASH = "sha256-" + base64.b64encode(hashlib.sha256(CRIT.encode()).digest()).decode()
SITE_CSS = minify_css((SRC / "site.css").read_text())
CSS_VER = hashlib.md5(SITE_CSS.encode()).hexdigest()[:8]
JS = (SRC / "main.js").read_text().replace("__GA_ID__", GA_ID).replace("__GA_HOST__", DOMAIN.split("//")[1])
JS_MIN = re.sub(r"\n\s*", "", JS)
JS_VER = hashlib.md5(JS_MIN.encode()).hexdigest()[:8]

def nav_html(cur):
    svc = "".join(f'<li><a href="/services/{s[0]}/">{E(s[1])}</a></li>' for s in SERVICES)
    loc = "".join(f'<li><a href="/locations/{l[0]}/">{E(l[1])}, MD</a></li>' for l in LOCATIONS)
    def ac(p): return ' aria-current="page"' if cur == p else ""
    desk = f'''<nav class="nav" aria-label="Main"><ul>
<li><button class="dd" aria-expanded="false" aria-haspopup="true">Services<span class="car" aria-hidden="true">▾</span></button><ul class="dd-menu"><li><a href="/services/">All services</a></li>{svc}</ul></li>
<li><button class="dd" aria-expanded="false" aria-haspopup="true">Locations<span class="car" aria-hidden="true">▾</span></button><ul class="dd-menu"><li><a href="/locations/">All service areas</a></li>{loc}</ul></li>
<li><a href="/blog/"{ac("/blog/")}>Blog</a></li><li><a href="/about/"{ac("/about/")}>About</a></li><li><a href="/contact/"{ac("/contact/")}>Contact</a></li></ul></nav>'''
    mob = f'''<nav class="mnav" id="mnav" aria-label="Mobile"><ul>
<li><span class="lbl">Services</span></li><li class="sub"><a href="/services/">All services</a></li>{svc.replace("<li>", '<li class="sub">')}
<li><span class="lbl">Locations</span></li><li class="sub"><a href="/locations/">All service areas</a></li>{loc.replace("<li>", '<li class="sub">')}
<li><span class="lbl">Company</span></li><li><a href="/blog/">Blog</a></li><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li></ul></nav>'''
    return desk, mob

def header(cur):
    desk, mob = nav_html(cur)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="hdr"><div class="wrap"><a class="logo" href="/" aria-label="{BRAND} home">{icons.LOGO}</a>{desk}
<div class="hdr-act">{call_btn("header", PHONE)}<button class="menu-btn" aria-expanded="false" aria-controls="mnav" aria-label="Open menu">{icons.MENU}</button></div></div>{mob}</header>'''

def footer():
    svc = "".join(f'<li><a href="/services/{s[0]}/">{E(s[1])}</a></li>' for s in SERVICES)
    loc = "".join(f'<li><a href="/locations/{l[0]}/">{E(l[1])}</a></li>' for l in LOCATIONS)
    soc = "".join(f'<a href="{u}" target="_blank" rel="noopener nofollow" aria-label="{n}">{icons.SOCIAL[n]}</a>' for n, u in SOCIAL)
    return f'''<footer class="ftr"><div class="wrap"><div class="cols">
<div><a class="logo" href="/" aria-label="{BRAND} home">{icons.LOGO}</a>
<p>Water damage restoration for Laurel, MD and nearby communities in Prince George's, Howard, Anne Arundel and Montgomery counties.</p>
<p><a class="tel" href="tel:{TEL}" data-loc="footer">{PHONE}</a><br>Open 24/7. Service-area business: we come to you.</p>
<div class="soc">{soc}</div></div>
<div><h2>Services</h2><ul><li><a href="/services/">All services</a></li>{svc}</ul></div>
<div><h2>Service areas</h2><ul><li><a href="/">Laurel, MD</a></li>{loc}<li><a href="/locations/">All service areas</a></li></ul></div>
<div><h2>Company</h2><ul><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/blog/">Blog</a></li><li><a href="/glossary/">Glossary</a></li><li><a href="/disclaimer/">Disclaimer</a></li><li><a href="/editorial-policy/">Editorial policy</a></li><li><a href="/privacy-policy/">Privacy policy</a></li><li><a href="/terms/">Terms</a></li><li><a href="/accessibility/">Accessibility</a></li></ul></div>
</div><div class="legal"><p>© 2026 {BRAND}. Content on this site is general information, not professional, legal or insurance advice. See the <a href="/disclaimer/">disclaimer</a>.</p></div></div></footer>
<div class="callbar"><a href="tel:{TEL}" data-loc="sticky">{icons.PHONE}Call {PHONE}</a></div>'''

def page(path, title, meta, body, schema=None, og_img="/assets/img/og-default.jpg", og_type="website", noindex=False, extra_head="", lastmod=None, og_h=630):
    url = DOMAIN + path
    sch = ""
    if schema:
        sch = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": schema}, ensure_ascii=False)}</script>'
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    doc = f'''<!DOCTYPE html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(meta)}"><link rel="canonical" href="{url}"><meta name="robots" content="{robots}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(meta)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{DOMAIN}{og_img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="{og_h}"><meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(meta)}"><meta name="twitter:image" content="{DOMAIN}{og_img}">{extra_head}
<meta name="theme-color" content="#0B2545"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<style>{CRIT}</style><link rel="stylesheet" href="/assets/css/site.css?v={CSS_VER}" media="print" id="fullcss"><noscript><link rel="stylesheet" href="/assets/css/site.css?v={CSS_VER}"></noscript>
<script src="/assets/js/main.js?v={JS_VER}" defer></script>{sch}</head><body>
{header(path)}<main id="main">{body}</main>{footer()}</body></html>'''
    dest = OUT / path.strip("/") / "index.html" if path != "/404.html" else OUT / "404.html"
    if path == "/": dest = OUT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(minify_html(doc), encoding="utf-8")
    PAGES.append(dict(path=path, title=title, meta=meta, noindex=noindex, lastmod=lastmod or LASTMOD.get(path, PUBLISHED)))

PAGES = []

def crumbs_html(items):
    lis = []
    for i, (name, href) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li><span aria-current="page">{E(name)}</span></li>')
        else:
            lis.append(f'<li><a href="{href}">{E(name)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'

def crumbs_schema(items, path):
    return {"@type": "BreadcrumbList", "@id": DOMAIN + path + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + h} for i, (n, h) in enumerate(items)]}

def hero(h1, lead, crumbs=None, chips=None, call=True, byline=None):
    c = crumbs_html(crumbs) if crumbs else ""
    ch = "<ul class=\"chips\">" + "".join(f"<li>{E(x)}</li>" for x in chips) + "</ul>" if chips else ""
    ctas = f'<div class="ctas">{call_btn("hero")}</div>' if call else ""
    lead_html = f'<p class="lead">{inline(lead)}</p>' if lead else ""
    by = f'<p class="byline">{byline}</p>' if byline else ""
    return f'<section class="hero"><div class="wrap">{c}<h1>{E(h1)}</h1>{lead_html}{by}{ctas}{ch}</div></section>'

def faq_html(faqs, title):
    if not faqs: return ""
    items = "".join(f'<details><summary><h3>{E(f["q"])}</h3></summary><div class="a">{markdown.markdown(f["a"])}</div></details>' for f in faqs)
    return f'<h2 id="faq">{E(title)}</h2><div class="faq">{items}</div>'

def faq_schema(faqs, path):
    if not faqs: return None
    return {"@type": "FAQPage", "@id": DOMAIN + path + "#faq", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", markdown.markdown(f["a"])).strip()}} for f in faqs]}

def sources_html(src, reviewed=True):
    if not src: return ""
    lis = "".join(f'<li><a href="{s["u"]}" target="_blank" rel="noopener">{E(s["t"])}</a></li>' for s in src)
    rv = f'<p class="note">Last reviewed {PUBLISHED_H}. This page is general information, not professional, legal or insurance advice. See our <a href="/editorial-policy/">editorial policy</a>.</p>' if reviewed else ""
    return f'<section class="src"><h2>Sources</h2><ol>{lis}</ol>{rv}</section>'

def band(h="Water in your home or business?", p="Call Laurel Dry Pros. We answer 24/7 for water damage in Laurel and nearby Maryland communities."):
    return f'<section class="band"><div class="wrap"><h2>{E(h)}</h2><p>{E(p)}</p><a class="tel" href="tel:{TEL}" data-loc="band">{PHONE}</a>{call_btn("band", "Call now")}</div></section>'

def svc_cards(slugs=None, h="h3"):
    slugs = slugs or [s[0] for s in SERVICES]
    cards = []
    for sl in slugs:
        s = SVC[sl]
        cards.append(f'<a class="card" href="/services/{sl}/"><span class="ico">{icons.SVC[s[3]]}</span><{h}>{E(s[1])}</{h}><p>{E(s[4])}</p><span class="more">{E(s[1])} details →</span></a>')
    return f'<div class="grid">{"".join(cards)}</div>'

LOC_CARD = {}
def loc_cards(slugs=None):
    slugs = slugs or [l[0] for l in LOCATIONS]
    return '<div class="grid">' + "".join(
        f'<a class="card" href="/locations/{sl}/"><span class="ico">{icons.PIN}</span><h3>{E(LOC[sl][1])}, MD</h3><p>{E(LOC_CARD.get(sl, LOC[sl][2]))}</p><span class="more">Water damage help in {E(LOC[sl][1])} →</span></a>' for sl in slugs) + "</div>"

def loc_pills(slugs=None, home=True, all_link=True):
    slugs = slugs or [l[0] for l in LOCATIONS]
    items = []
    if home: items.append('<li><a href="/">Laurel, MD</a></li>')
    items += [f'<li><a href="/locations/{s}/">{E(LOC[s][1])}, MD</a></li>' for s in slugs]
    if all_link: items.append('<li><a href="/locations/">All service areas</a></li>')
    return f'<ul class="pills">{"".join(items)}</ul>'

POSTS = {}
def post_cards(slugs):
    out = []
    for sl in slugs:
        p = POSTS[sl]
        out.append(f'<a class="card" href="/blog/{sl}/"><img src="/assets/img/blog/{sl}.webp" alt="{E(p["fm"]["alt"])}" width="1200" height="630" loading="lazy" decoding="async"><span class="cat">{E(p["cat"])}</span><h3>{E(p["fm"]["crumb"])}</h3><p>{E(p["fm"]["card"])}</p><span class="more">Read the {E(p["fm"]["crumb"].lower())} guide →</span></a>')
    return f'<div class="grid">{"".join(out)}</div>'

def thing(name):
    return {"@type": "Thing", "name": name, "sameAs": WIKI[name]}

# ---------------------------------------------------------------- schema base
ORG_ID = DOMAIN + "/#organization"; BIZ_ID = DOMAIN + "/#business"; SITE_ID = DOMAIN + "/#website"

def area_nodes():
    nodes = [{"@type": "City", "name": "Laurel", "sameAs": WIKI["Laurel, Maryland"], "containedInPlace": {"@type": "State", "name": "Maryland"}}]
    for l in LOCATIONS:
        nodes.append({"@type": "City" if l[3] == "City" else "Place", "name": f"{l[1]}, MD", "containedInPlace": {"@type": "AdministrativeArea", "name": f"{l[2]}, Maryland", "sameAs": WIKI[COUNTY_WIKI[l[2]]]}})
    return nodes

def biz_node(full=False):
    n = {"@type": "HomeAndConstructionBusiness", "@id": BIZ_ID, "additionalType": "https://en.wikipedia.org/wiki/Water_damage",
         "name": BRAND, "url": DOMAIN + "/", "telephone": TEL, "image": DOMAIN + "/assets/img/og-default.jpg", "logo": DOMAIN + "/assets/img/logo.svg",
         "parentOrganization": {"@id": ORG_ID}}
    if full:
        n.update({"description": "Water damage restoration, water removal, drying, mold remediation, sewage cleanup and fire and smoke cleanup for Laurel, MD and nearby communities. Service-area business.",
                  "areaServed": area_nodes(),
                  "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}],
                  "knowsAbout": ["Water damage restoration", "Water extraction", "Structural drying", "Mold remediation", "Sewage cleanup", "Fire and smoke damage restoration"],
                  "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Water damage restoration services", "itemListElement": [
                      {"@type": "Offer", "itemOffered": {"@id": f"{DOMAIN}/services/{s[0]}/#service"}} for s in SERVICES]},
                  "sameAs": []})
        n.pop("sameAs")
    return n

def org_node():
    return {"@type": "Organization", "@id": ORG_ID, "name": BRAND, "url": DOMAIN + "/", "logo": {"@type": "ImageObject", "url": DOMAIN + "/assets/img/logo.svg"},
            "telephone": TEL, "publishingPrinciples": DOMAIN + "/editorial-policy/",
            "contactPoint": {"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service", "areaServed": "US-MD", "availableLanguage": "en", "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}}}

def website_node():
    return {"@type": "WebSite", "@id": SITE_ID, "url": DOMAIN + "/", "name": BRAND, "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}

def webpage(path, name, desc, about=None, mentions=None, citation=None, ptype="WebPage", crumbs=True, extra=None):
    n = {"@type": ptype, "@id": DOMAIN + path + "#webpage", "url": DOMAIN + path, "name": name, "description": desc,
         "isPartOf": {"@id": SITE_ID}, "inLanguage": "en-US", "dateModified": PUBLISHED}
    if about: n["about"] = about
    if mentions: n["mentions"] = mentions
    if citation: n["citation"] = [{"@type": "CreativeWork", "name": c["t"], "url": c["u"]} for c in citation]
    if crumbs: n["breadcrumb"] = {"@id": DOMAIN + path + "#breadcrumb"}
    if extra: n.update(extra)
    return n


# ---------------------------------------------------------------- scene illustrations
sys.path.insert(0, str(ROOT))
from fetch_photos import PHOTOS, credit as photo_credit, page_url as photo_url
SCENE_CAP = {
    "home-crew": "Water and sewage jobs end with cleaning and disinfecting, so the room is safe to use again.",
    "home-rain": "Heavy storms put a lot of water against foundations. Low areas near the Patuxent and its streams can flood.",
    "home-leak": "Small, slow leaks are easy to miss. Stains, drips and musty smells are early warning signs.",
    "svc-emergency-water-removal": "Standing water comes out first. Left in place, it soaks walls and can lead to mold.",
    "svc-water-mitigation-structural-drying": "Walls are repaired only after meter readings show the framing behind them is dry.",
    "svc-flooded-basement-cleanup": "Basements flood from rain, sump failures and backups. The source decides how cleanup is done.",
    "svc-burst-pipe-water-damage": "Shut off the main water valve first. The pipe gets repaired while the wet areas are dried.",
    "svc-ceiling-drywall-water-damage": "Wet ceiling drywall is dried or replaced, then taped, sanded and painted to match.",
    "svc-sewage-cleanup": "Sewage is Category 3 water. Crews wear protective gear and filter the air during cleanup.",
    "svc-mold-remediation": "Mold work calls for protective gear, containment and HEPA air filtering.",
    "svc-storm-flood-damage": "Storm water that crosses the ground into a home is treated as contaminated water.",
    "svc-fire-smoke-damage": "The water used to put out a fire soaks floors and walls, so drying starts along with smoke cleanup.",
}
def scene(name, cap=None):
    src = f"/assets/img/photos/{name}"
    cap = cap or SCENE_CAP.get(name, "")
    cr = f'<a href="{photo_url(name)}" rel="nofollow noopener" target="_blank">{E(photo_credit(name))}</a>'
    return (f'<figure class="scene"><img src="{src}.webp" srcset="{src}-600.webp 600w, {src}.webp 1200w" sizes="(max-width: 800px) 100vw, 800px" '
            f'alt="{E(PHOTOS[name][2])}" width="1200" height="750" loading="lazy" decoding="async">'
            f'<figcaption>{E(cap)} <span class="credit">{cr}</span></figcaption></figure>')

def _text_after(html_s, pos):
    """Words of flowing text after the h2 starting at pos, up to the next table, h2 or block."""
    end = html_s.find("</h2>", pos) + 5
    stops = [i for i in (html_s.find(s, end) for s in ('<div class="tbl"', "<h2", '<div class="cta', '<figure', '<div class="cards')) if i != -1]
    seg = html_s[end:min(stops) if stops else len(html_s)]
    return len(re.sub(r"<[^>]+>", " ", seg).split())

def before_h2(html_s, n, fig, min_words=70):
    """Insert fig before the first h2 (from the n-th on) whose section opens with enough text to wrap around the photo."""
    idx = [m.start() for m in re.finditer(r"<h2", html_s)]
    if not idx: return html_s + fig
    pick = next((i for i in idx[n:-1] if _text_after(html_s, i) >= min_words), idx[min(n, len(idx) - 1)])
    return html_s[:pick] + fig + html_s[pick:]

def before_h2_match(html_s, pat, fig):
    m = re.search(r"<h2[^>]*>[^<]*(?:" + pat + r")", html_s, re.I)
    return html_s[:m.start()] + fig + html_s[m.start():] if m else html_s

# ---------------------------------------------------------------- build steps
def load_posts():
    for sl, (cat, money) in BLOG.items():
        fm, body = read_md(SRC / "content" / "blog" / f"{sl}.md")
        POSTS[sl] = dict(fm=fm, body=body, cat=cat, money=money)

def img_obj(name):
    return {"@type": "ImageObject", "url": f"{DOMAIN}/assets/img/photos/{name}.jpg", "width": 1200, "height": 750}

LOC_CAP = {"bowie-md": "colonials to ramblers and Cape Cods", "columbia-md": "village townhomes to single-family homes near the lakes",
           "greenbelt-md": "historic garden homes to newer townhomes", "silver-spring-md": "older bungalows to high-rise condos",
           "beltsville-md": "split-levels to ramblers on larger lots", "burtonsville-md": "newer colonials to older homes on wooded lots",
           "odenton-fort-meade-md": "townhome rows to single-family homes", "maple-lawn-fulton-md": "new townhomes to large single-family homes"}

def build_service(sl):
    fm, body = read_md(SRC / "content" / "services" / f"{sl}.md")
    s = SVC[sl]; path = f"/services/{sl}/"
    crumbs = [("Home", "/"), ("Services", "/services/"), (fm.get("crumb", s[1]), path)]
    main = gloss_apply(render_md(body), path)
    main = before_h2(main, 1, scene("svc-" + sl))
    rel = f'<h2>Related water damage services</h2>{svc_cards(RELATED[sl])}'
    near = f'<h2>{E(s[1])} near you</h2><p>{E(fm["near"])}</p>{loc_pills()}'
    guides = f'<h2>Helpful guides</h2>{post_cards(GUIDES[sl])}'
    html_body = hero(fm["h1"], fm["lead"], crumbs, fm.get("chips", DEFAULT_CHIPS)) + \
        f'<section class="sec"><div class="wrap"><div class="prose">{main}{faq_html(fm["faq"], fm.get("faq_title", s[1] + " questions"))}{sources_html(fm["src"])}</div></div></section>' + \
        f'<section class="sec alt"><div class="wrap">{rel}{near}{guides}</div></section>' + band(fm.get("band_h", "Need help with " + s[1].lower() + "?"), fm.get("band_p", "Call Laurel Dry Pros 24/7. Tell us what happened and your ZIP code."))
    service = {"@type": "Service", "@id": DOMAIN + path + "#service", "name": fm["h1"], "serviceType": fm["service_type"], "description": fm["meta"],
               "provider": {"@id": BIZ_ID}, "areaServed": area_nodes(), "url": DOMAIN + path,
               "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service"}, "serviceUrl": DOMAIN + path}}
    wp = webpage(path, fm["title"], fm["meta"], about=[{"@id": BIZ_ID}, {"@id": DOMAIN + path + "#service"}] + [thing(a) for a in fm.get("about", [])],
                 mentions=[thing(m) for m in fm.get("mentions", [])] + [thing("Laurel, Maryland")], citation=fm["src"])
    service["image"] = img_obj("svc-" + sl); wp["primaryImageOfPage"] = img_obj("svc-" + sl)
    graph = [org_node(), website_node(), biz_node(), wp, service, crumbs_schema(crumbs, path)]
    fs = faq_schema(fm["faq"], path)
    if fs: graph.append(fs)
    page(path, fm["title"], fm["meta"], html_body, graph, og_img=f"/assets/img/photos/svc-{sl}.jpg", og_h=750)
    SOURCES_TXT[path] = (fm, body)

def build_location(lo):
    sl, name, county, ptype, zips, nearby = lo
    fm, body = read_md(SRC / "content" / "locations" / f"{sl}.md")
    path = f"/locations/{sl}/"
    LOC_CARD[sl] = fm["card"]
    crumbs = [("Home", "/"), ("Locations", "/locations/"), (fm.get("crumb", name), path)]
    main = gloss_apply(render_md(body), path)
    main = before_h2(main, 1, scene("loc-" + sl, f"We serve homes across {name}, from {LOC_CAP[sl]}."))
    svc = f'<h2>{E(fm["svc_h2"])}</h2>{svc_cards()}'
    near = f'<h2>Nearby areas covered</h2>{loc_pills(nearby)}'
    html_body = hero(fm["h1"], fm["lead"], crumbs, fm.get("chips")) + \
        f'<section class="sec"><div class="wrap"><div class="prose">{main}{faq_html(fm["faq"], fm.get("faq_title", "Water damage questions in " + name))}{sources_html(fm.get("src", []), reviewed=False)}</div></div></section>' + \
        f'<section class="sec alt"><div class="wrap">{svc}{near}</div></section>' + band(f"Water damage in {name}?", f"Call Laurel Dry Pros 24/7 for water removal, drying and cleanup in {name}.")
    places = [{"@type": "City" if ptype == "City" else "Place", "name": f"{n}, MD", "sameAs": WIKI[n + ", Maryland"] if (n + ", Maryland") in WIKI else None,
               "containedInPlace": {"@type": "AdministrativeArea", "name": f"{county}, Maryland", "sameAs": WIKI[COUNTY_WIKI[county]]}} for n in fm["places"]]
    for p in places:
        if p["sameAs"] is None: p.pop("sameAs")
    service = {"@type": "Service", "@id": DOMAIN + path + "#service", "name": fm["h1"], "serviceType": "Water damage restoration", "provider": {"@id": BIZ_ID},
               "areaServed": places, "url": DOMAIN + path, "description": fm["meta"],
               "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service"}}}
    wp = webpage(path, fm["title"], fm["meta"], about=[{"@id": BIZ_ID}, thing("Water damage")], mentions=[thing(x) for x in LOC_WIKI[sl]] + [thing(COUNTY_WIKI[county])] + [thing(m) for m in fm.get("mentions", [])], citation=fm.get("src"))
    service["image"] = img_obj("loc-" + sl); wp["primaryImageOfPage"] = img_obj("loc-" + sl)
    graph = [org_node(), website_node(), biz_node(), wp, service, crumbs_schema(crumbs, path)]
    fs = faq_schema(fm["faq"], path)
    if fs: graph.append(fs)
    page(path, fm["title"], fm["meta"], html_body, graph, og_img=f"/assets/img/photos/loc-{sl}.jpg", og_h=750)
    SOURCES_TXT[path] = (fm, body)

def build_post(sl):
    p = POSTS[sl]; fm, body = p["fm"], p["body"]; path = f"/blog/{sl}/"
    crumbs = [("Home", "/"), ("Blog", "/blog/"), (fm["crumb"], path)]
    words = len(re.findall(r"\b\w[\w'-]*\b", re.sub(r"<[^>]+>|\[|\]\([^)]*\)", " ", body)))
    mins = max(4, round(words / 230))
    pub = fm.get("date", PUBLISHED); upd = fm.get("updated", pub)
    hd = lambda d: __import__("datetime").date.fromisoformat(d).strftime("%B %-d, %Y")
    by = f'By {BRAND} Editorial · Published {hd(pub)} · Updated {hd(upd)} · {mins} min read'
    main = gloss_apply(render_md(body), path)
    img = f'<img class="feat" src="/assets/img/blog/{sl}.webp" alt="{E(fm["alt"])}" width="1200" height="630" fetchpriority="high" decoding="async">'
    author = f'<div class="author"><p><strong>About this article.</strong> Written by {BRAND} Editorial and checked against the sources listed above. Last updated {hd(upd)}. General information, not legal, insurance or professional advice. Read our <a href="/editorial-policy/">editorial policy</a> and <a href="/disclaimer/">disclaimer</a>.</p></div>'
    rel = f'<h2>Related guides</h2>{post_cards(fm["related"])}'
    html_body = hero(fm["h1"], None, crumbs, None, call=False, byline=by) + \
        f'<section class="sec"><div class="wrap"><div class="prose">{img}{main}{faq_html(fm["faq"], "Frequently asked questions")}{sources_html(fm["src"], reviewed=False)}{author}</div></div></section>' + \
        f'<section class="sec alt"><div class="wrap">{rel}</div></section>' + band(fm.get("band_h", "Water damage in Laurel?"), fm.get("band_p", "Call Laurel Dry Pros 24/7 for water removal, drying and cleanup."))
    bp = {"@type": "BlogPosting", "@id": DOMAIN + path + "#article", "headline": fm["h1"], "description": fm["meta"], "image": {"@type": "ImageObject", "url": f"{DOMAIN}/assets/img/blog/{sl}.jpg", "width": 1200, "height": 630},
          "datePublished": pub, "dateModified": upd, "author": {"@type": "Organization", "name": f"{BRAND} Editorial", "url": DOMAIN + "/editorial-policy/"},
          "publisher": {"@id": ORG_ID}, "inLanguage": "en-US", "wordCount": WC.get(path, words), "articleSection": p["cat"], "mainEntityOfPage": {"@id": DOMAIN + path + "#webpage"},
          "isPartOf": {"@id": DOMAIN + "/blog/#blog"}, "citation": [{"@type": "CreativeWork", "name": c["t"], "url": c["u"]} for c in fm["src"]]}
    wp = webpage(path, fm["title"], fm["meta"], about=[thing(fm["about"])], mentions=[thing(m) for m in fm.get("mentions", [])])
    graph = [org_node(), website_node(), wp, bp, crumbs_schema(crumbs, path)]
    fs = faq_schema(fm["faq"], path)
    if fs: graph.append(fs)
    page(path, fm["title"], fm["meta"], html_body, graph, og_img=f"/assets/img/blog/{sl}.jpg", og_type="article",
         extra_head=f'<meta property="article:published_time" content="{pub}T09:00:00-05:00"><meta property="article:modified_time" content="{upd}T09:00:00-05:00">', lastmod=upd)
    SOURCES_TXT[path] = (fm, body)

WC = {}
SOURCES_TXT = {}
LASTMOD = {}  # path -> date for pages edited after launch (set in data.py)
DEFAULT_CHIPS = ["Open 24/7", "10+ years in business", "Laurel & nearby Maryland", "Homes & businesses"]

def auto_replace(h, mapping):
    for k, v in mapping.items():
        h = h.replace(f"<!--AUTO:{k}-->", v).replace(f"<p><!--AUTO:{k}--></p>", v)
    return h

def build_home():
    fm, body = read_md(SRC / "content" / "pages" / "home.md")
    main = render_md(body)
    main = gloss_apply(main, "/")
    main = auto_replace(main, {"services": svc_cards(), "areas": loc_cards(),
                               "call": f'<div class="cta-box"><p>{inline(fm["mid_cta"])}</p>{call_btn("cta")}</div>'})
    main = before_h2_match(main, r"Why Laurel homeowners", scene("home-crew"))
    main = before_h2_match(main, r"Why water damage in Laurel is different", scene("home-rain"))
    main = before_h2_match(main, r"Warning signs of hidden water damage", scene("home-leak"))
    html_body = hero(fm["h1"], fm["lead"], None, fm["chips"]) + f'<section class="sec"><div class="wrap"><div class="prose wide">{main}{faq_html(fm["faq"], "Water damage restoration questions")}{sources_html(fm["src"])}</div></div></section>' + band()
    wp = webpage("/", fm["title"], fm["meta"], about=[{"@id": BIZ_ID}, thing("Water damage")],
                 mentions=[thing("Laurel, Maryland"), thing("Prince George's County, Maryland"), thing("Patuxent River"), thing("Indoor mold")], citation=fm["src"], crumbs=False)
    wp["primaryImageOfPage"] = img_obj("home-crew")
    graph = [org_node(), website_node(), biz_node(full=True), wp]
    for s in SERVICES:
        graph.append({"@type": "Service", "@id": f"{DOMAIN}/services/{s[0]}/#service", "name": s[2] + " in Laurel, MD", "url": f"{DOMAIN}/services/{s[0]}/", "provider": {"@id": BIZ_ID}})
    graph.append(faq_schema(fm["faq"], "/"))
    page("/", fm["title"], fm["meta"], html_body, graph)
    SOURCES_TXT["/"] = (fm, body)

def build_simple(slug, kind="WebPage", extra_auto=None, crumbs_name=None, sources=True, schema_extra=None):
    fm, body = read_md(SRC / "content" / "pages" / f"{slug}.md")
    path = f"/{slug}/"
    crumbs = [("Home", "/"), (fm.get("crumb", crumbs_name or fm["h1"]), path)]
    main = render_md(body)
    if extra_auto: main = auto_replace(main, extra_auto)
    if fm.get("gloss", False): main = gloss_apply(main, path)
    faq = faq_html(fm.get("faq"), fm.get("faq_title", "Questions")) if fm.get("faq") else ""
    html_body = hero(fm["h1"], fm.get("lead"), crumbs, fm.get("chips"), call=fm.get("call", True)) + \
        f'<section class="sec"><div class="wrap"><div class="prose{" wide" if fm.get("wide") else ""}">{main}{faq}{sources_html(fm.get("src"), reviewed=False) if sources else ""}</div></div></section>' + (band() if fm.get("band", True) else "")
    wp = webpage(path, fm["title"], fm["meta"], ptype=kind, about=[{"@id": BIZ_ID}] if kind in ("AboutPage", "ContactPage") else None)
    graph = [org_node(), website_node(), wp, crumbs_schema(crumbs, path)]
    if kind in ("AboutPage", "ContactPage"): graph.insert(2, biz_node(full=True))
    if fm.get("faq"): graph.append(faq_schema(fm["faq"], path))
    if schema_extra: graph += schema_extra
    page(path, fm["title"], fm["meta"], html_body, graph)
    SOURCES_TXT[path] = (fm, body)

def build_hubs():
    # services hub
    build_simple("services", "CollectionPage", {"services": svc_cards(h="h3")}, schema_extra=[{"@type": "ItemList", "@id": DOMAIN + "/services/#list", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{DOMAIN}/services/{s[0]}/", "name": s[2]} for i, s in enumerate(SERVICES)]}])
    build_simple("locations", "CollectionPage", {"locations": loc_cards()}, schema_extra=[{"@type": "ItemList", "@id": DOMAIN + "/locations/#list", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{DOMAIN}/locations/{l[0]}/", "name": f"{l[1]}, MD"} for i, l in enumerate(LOCATIONS)]}])
    # blog hub
    groups = ""
    for cat in BLOG_CATS:
        sl = [k for k, v in BLOG.items() if v[0] == cat]
        if sl: groups += f'<h2>{E(cat)}</h2>{post_cards(sl)}'
    blog_node = {"@type": "Blog", "@id": DOMAIN + "/blog/#blog", "name": f"{BRAND} Blog", "url": DOMAIN + "/blog/", "publisher": {"@id": ORG_ID},
                 "blogPost": [{"@id": f"{DOMAIN}/blog/{k}/#article"} for k in BLOG]}
    build_simple("blog", "CollectionPage", {"posts": groups}, schema_extra=[blog_node])

def build_glossary():
    fm, body = read_md(SRC / "content" / "pages" / "glossary.md")
    path = "/glossary/"
    terms = sorted(GLOSS, key=lambda t: t["term"].lower())
    letters = sorted({t["term"][0].upper() for t in terms})
    az = '<ul class="az">' + "".join(f'<li><a href="#letter-{L}">{L}</a></li>' for L in letters) + "</ul>"
    dl = ""
    cur = None
    for t in terms:
        L = t["term"][0].upper()
        if L != cur:
            if cur: dl += "</dl>"
            dl += f'<h2 id="letter-{L}">{L}</h2><dl class="gl">'; cur = L
        link = f' <a href="{t["link"]}">{E(t["anchor"])}</a>.' if t.get("link") else ""
        dl += f'<dt id="{t["slug"]}">{E(t["term"])}</dt><dd>{E(t["def"])}{link}</dd>'
    dl += "</dl>"
    main = render_md(body) + az + dl
    crumbs = [("Home", "/"), ("Glossary", path)]
    html_body = hero(fm["h1"], fm["lead"], crumbs, call=False) + f'<section class="sec"><div class="wrap"><div class="prose">{main}</div></div></section>' + band()
    dts = {"@type": "DefinedTermSet", "@id": DOMAIN + path + "#terms", "name": "Water damage restoration glossary", "hasDefinedTerm": [
        {"@type": "DefinedTerm", "@id": f"{DOMAIN}{path}#{t['slug']}", "name": t["term"], "description": t["def"], "inDefinedTermSet": {"@id": DOMAIN + path + "#terms"}} for t in terms]}
    graph = [org_node(), website_node(), webpage(path, fm["title"], fm["meta"]), dts, crumbs_schema(crumbs, path)]
    page(path, fm["title"], fm["meta"], html_body, graph)
    SOURCES_TXT[path] = (fm, body + " ".join(t["def"] for t in terms))

def build_404():
    body = hero("Page not found", "The page you asked for isn't here. It may have moved. These links will get you where you need to go.", None, None) + \
        f'<section class="sec"><div class="wrap"><div class="prose"><h2>Popular pages</h2><ul><li><a href="/">Water damage restoration in Laurel, MD</a></li><li><a href="/services/">All water damage services</a></li><li><a href="/locations/">Service areas</a></li><li><a href="/blog/">Water damage guides</a></li><li><a href="/contact/">Contact Laurel Dry Pros</a></li></ul></div></div></section>' + band()
    page("/404.html", f"Page Not Found | {BRAND}", "This page could not be found. Call Laurel Dry Pros for water damage help in Laurel, MD.", body, noindex=True)

def write_static():
    (OUT / "assets/css").mkdir(parents=True, exist_ok=True); (OUT / "assets/js").mkdir(parents=True, exist_ok=True)
    (OUT / "assets/css/site.css").write_text(SITE_CSS)
    (OUT / "assets/js/main.js").write_text(JS_MIN)
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    pri = lambda p: "1.0" if p == "/" else "0.9" if p.startswith("/services/") and p != "/services/" else "0.8" if p in ("/services/", "/locations/", "/blog/") or p.startswith("/locations/") else "0.7" if p.startswith("/blog/") else "0.6" if p == "/glossary/" else "0.4"
    urls = "".join(f"<url><loc>{DOMAIN}{p['path']}</loc><lastmod>{p['lastmod']}</lastmod><priority>{pri(p['path'])}</priority></url>" for p in PAGES if not p["noindex"])
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "site.webmanifest").write_text(json.dumps({"name": BRAND, "short_name": "Dry Pros", "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#0B2545",
        "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1))
    csp = ("default-src 'self'; script-src 'self' https://www.googletagmanager.com https://static.cloudflareinsights.com; style-src 'self' '" + CRIT_HASH + "'; img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com; font-src 'self'; "
           "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://cloudflareinsights.com; "
           "frame-src https://www.google.com; form-action 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; upgrade-insecure-requests")
    (OUT / "_headers").write_text(f"""/*
  Content-Security-Policy: {csp}
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Cache-Control: public, max-age=300, must-revalidate

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/favicon.ico
  Cache-Control: public, max-age=604800
/favicon.svg
  Cache-Control: public, max-age=604800
/apple-touch-icon.png
  Cache-Control: public, max-age=604800

/sitemap.xml
  Cache-Control: public, max-age=3600
""")
    (OUT / "_redirects").write_text("""# Clean URLs: Cloudflare Pages serves folder/index.html at /folder/ and adds the trailing slash automatically.
# Legacy / common alternate paths -> canonical pages
/index.html / 301
/home / 301
/services/water-damage-restoration/ / 301
/water-damage-restoration-laurel-md/ / 301
/service-areas/ /locations/ 301
/areas/ /locations/ 301
/mold-removal/ /services/mold-remediation/ 301
/water-removal/ /services/emergency-water-removal/ 301
/privacy/ /privacy-policy/ 301
/terms-of-service/ /terms/ 301
""")

def main():
    for p in OUT.glob("*"):
        if p.name in ("assets", "favicon.svg", "favicon.ico", "apple-touch-icon.png"): continue
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    load_posts()
    LASTMOD.update({p: UPDATED for p in ["/blog/", "/glossary/"] + [f"/services/{k}/" for k in GUIDES]})
    for lo in LOCATIONS:  # card text needed before hubs
        fm, _ = read_md(SRC / "content" / "locations" / f"{lo[0]}.md"); LOC_CARD[lo[0]] = fm["card"]
    build_home()
    for s in SERVICES: build_service(s[0])
    for lo in LOCATIONS: build_location(lo)
    for sl in BLOG: build_post(sl)
    build_hubs(); build_glossary()
    build_simple("about", "AboutPage")
    build_simple("contact", "ContactPage", {"form": icons.FORM(SERVICES), "map": icons.MAP})
    for lg in ["disclaimer", "editorial-policy", "privacy-policy", "terms", "accessibility"]:
        build_simple(lg, "WebPage")
    build_404(); write_static()
    print(f"built {len(PAGES)} pages")

if __name__ == "__main__":
    main()
