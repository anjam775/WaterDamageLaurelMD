#!/usr/bin/env python3
"""Self-audit for the built site. Prints a check table and exits non-zero on failures."""
import json, re, sys
from collections import defaultdict, deque
from pathlib import Path
from bs4 import BeautifulSoup

def _syl(w):
    w = w.lower().strip(".,;:!?()\"'")
    if len(w) <= 3: return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w); w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))
def fk_grade(t):
    sents = max(1, len(re.findall(r"[.!?]+(?:\s|$)", t)))
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", t)
    if not words: return 0
    syl = sum(_syl(w) for w in words)
    return round(0.39 * len(words) / sents + 11.8 * syl / len(words) - 15.59, 1)

ROOT = Path(__file__).parent; SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "src"))
from data import *

pages = {}
for f in SITE.rglob("*.html"):
    rel = "/" + str(f.relative_to(SITE)).replace("index.html", "")
    if rel == "/404.html": pass
    pages[rel] = BeautifulSoup(f.read_text(), "lxml")

issues = defaultdict(list)
def bad(check, msg): issues[check].append(msg)

def ptype(p):
    if p == "/": return "home"
    for t in ("services", "locations", "blog"):
        if p.startswith(f"/{t}/") and p != f"/{t}/": return t
    return "other"

def main_text(s):
    m = s.select_one("main .prose")
    if not m: return ""
    m = BeautifulSoup(str(m), "lxml")
    for x in m.select(".src, .author, .cta-box, .faq, h2#faq"): x.decompose()
    return m.get_text(" ", strip=True)

def body_words(s):
    """Visible main content words (prose incl. FAQ, excl. sources/author/CTA)."""
    m = s.select_one("main .prose")
    if not m: return 0
    m = BeautifulSoup(str(m), "lxml")
    for x in m.select(".src, .author, .cta-box, img"): x.decompose()
    return len(re.findall(r"[A-Za-z0-9][\w'’-]*", m.get_text(" ", strip=True)))

# ---------- 1. links & anchors
ids_by_page = {p: {e.get("id") for e in s.find_all(id=True)} for p, s in pages.items()}
inbound = defaultdict(set); intext_in = defaultdict(set); anchors_in = defaultdict(list)
for p, s in pages.items():
    for a in s.find_all("a", href=True):
        h = a["href"]
        if h.startswith(("http", "tel:", "mailto:")):
            if h.startswith("http") and "waterdamagerestorationlaurelmd.com" not in h and a.find_parent("main") and a.get("rel") is None and not a.find_parent(class_="soc"):
                bad("External links", f"{p}: {h} missing rel=noopener")
            continue
        path, _, frag = h.partition("#")
        if not path: path = p
        if path not in pages:
            bad("Internal links resolve", f"{p} -> {h}"); continue
        if frag and frag not in ids_by_page[path]:
            bad("Internal links resolve", f"{p} -> {h} (missing anchor)")
        if path != p: inbound[path].add(p)
        in_prose = a.find_parent(class_="prose") and not a.find_parent(class_=["card", "pills", "grid", "src", "author"])
        if in_prose and path != p:
            intext_in[path].add(p); anchors_in[path].append(a.get_text(strip=True).lower())

for p in pages:
    if p in ("/", "/404.html"): continue
    if not inbound[p]: bad("No orphans", p)
    if ptype(p) in ("services", "locations", "blog") and len(intext_in[p]) < 3:
        bad("3+ in-text inbound links", f"{p}: {len(intext_in[p])} ({sorted(intext_in[p])})")
    if ptype(p) == "blog" and len(set(anchors_in[p])) < 2:
        bad("Varied anchors", f"{p}: {set(anchors_in[p])}")

GENERIC = {"click here", "read more", "here", "learn more", "this page", "more"}
for p, s in pages.items():
    for a in s.select("main a[href]"):
        if a.get_text(strip=True).lower() in GENERIC: bad("No generic anchors", f"{p}: '{a.get_text(strip=True)}'")

# click depth
depth = {"/": 0}; q = deque(["/"])
while q:
    c = q.popleft()
    for a in pages[c].find_all("a", href=True):
        h = a["href"].partition("#")[0]
        if h in pages and h not in depth: depth[h] = depth[c] + 1; q.append(h)
for p in pages:
    if p == "/404.html": continue
    if depth.get(p, 99) > 2: bad("Click depth <= 2", f"{p}: {depth.get(p)}")

# ---------- 2. on-page SEO
titles, metas, h1s = defaultdict(list), defaultdict(list), defaultdict(list)
for p, s in pages.items():
    t = s.title.get_text(); m = s.find("meta", attrs={"name": "description"})["content"]
    titles[t].append(p); metas[m].append(p)
    if len(t) > 60: bad("Title <= 60 chars", f"{p}: {len(t)} '{t}'")
    if len(m) > 155: bad("Meta <= 155 chars", f"{p}: {len(m)}")
    h1 = s.find_all("h1")
    if len(h1) != 1: bad("One H1", f"{p}: {len(h1)}")
    else: h1s[h1[0].get_text(strip=True)].append(p)
    lvls = [int(h.name[1]) for h in s.select("main h1, main h2, main h3, main h4")]
    for a, b in zip(lvls, lvls[1:]):
        if b > a + 1: bad("No skipped headings", f"{p}: h{a}->h{b}"); break
    can = s.find("link", rel="canonical")
    if not can or can["href"] != DOMAIN + (p if p != "/404.html" else "/404.html"): bad("Canonical", p)
    for need in ["og:title", "og:description", "og:image", "og:url"]:
        if not s.find("meta", property=need): bad("OG tags", f"{p} {need}")
    if not s.find("meta", attrs={"name": "twitter:card"}): bad("Twitter card", p)
    if s.html.get("lang") != "en-US": bad("lang", p)
    for img in s.find_all("img"):
        if not img.get("alt") or not img.get("width") or not img.get("height"): bad("Image alt + dimensions", f"{p}: {img.get('src')}")
for d, name in ((titles, "Unique titles"), (metas, "Unique metas"), (h1s, "Unique H1s")):
    for k, v in d.items():
        if len(v) > 1: bad(name, f"{v}")

# ---------- 3. keyword map adherence (money pages)
KW = {"/": ("water damage restoration", "laurel")}
for s_ in SERVICES:
    core = {"emergency-water-removal": "water removal", "water-mitigation-structural-drying": "mitigation", "flooded-basement-cleanup": "flooded basement",
            "burst-pipe-water-damage": "burst pipe", "ceiling-drywall-water-damage": "ceiling", "sewage-cleanup": "sewage cleanup",
            "mold-remediation": "mold remediation", "storm-flood-damage": "flood damage", "fire-smoke-damage": "fire"}[s_[0]]
    KW[f"/services/{s_[0]}/"] = (core, "laurel")
for l in LOCATIONS:
    KW[f"/locations/{l[0]}/"] = ("water damage restoration", l[1].split(" & ")[0].lower())
for p, (k1, k2) in KW.items():
    s = pages[p]
    t = s.title.get_text().lower(); m = s.find("meta", attrs={"name": "description"})["content"].lower(); h1 = s.h1.get_text().lower()
    first = " ".join(main_text(s).lower().split()[:100])
    h2 = " ".join(h.get_text().lower() for h in s.select("main h2"))
    for where, txt in (("title", t), ("meta", m), ("H1", h1), ("first 100 words", first), ("an H2", h2)):
        if k1 not in txt or (k2 not in txt and where != "an H2"):
            bad("Keyword placement", f"{p}: '{k1}'/'{k2}' missing in {where}")
BLOG_KW = {"frozen-pipes-burst": "frozen pipes", "water-damage-restoration-cost": "water damage restoration cost", "does-homeowners-insurance-cover-water-damage": "homeowners insurance",
           "what-to-do-when-your-basement-floods": "basement floods", "sump-pump-not-working": "sump pump", "how-long-does-it-take-for-mold-to-grow": "mold to grow",
           "musty-smell-in-basement": "musty smell", "water-damage-on-ceiling": "ceiling", "sewage-backup-cleanup": "sewage backup", "water-mitigation-vs-restoration": "mitigation",
           "water-heater-leaking": "water heater", "how-to-prepare-for-a-flood": "prepare for a flood"}
for sl, k in BLOG_KW.items():
    p = f"/blog/{sl}/"; s = pages[p]
    t = s.title.get_text().lower(); m = s.find("meta", attrs={"name": "description"})["content"].lower(); h1 = s.h1.get_text().lower()
    first = " ".join(main_text(s).lower().split()[:100]); h2 = " ".join(h.get_text().lower() for h in s.select("main h2"))
    for where, txt in (("title", t), ("meta", m), ("H1", h1), ("first 100 words", first), ("an H2", h2)):
        if k not in txt: bad("Keyword placement", f"{p}: '{k}' missing in {where}")
    # money page link in first 150 words
    prose = s.select_one("main .prose"); money = BLOG[sl][1]
    words = 0; found = False
    for el in prose.find_all(["p", "li", "td"]):
        if el.find_parent(class_="short"): continue
        for a in el.find_all("a", href=True):
            if a["href"] == money and words < 150: found = True
        words += len(el.get_text().split())
        if words > 170: break
    if not found: bad("Money link in first 150 words", p)
    links = [a["href"] for a in prose.find_all("a", href=True) if not a.find_parent(class_=["card", "grid", "src", "author"])]
    guides = {h for h in links if h.startswith("/blog/") and h != p}
    locs = {h for h in links if h.startswith("/locations/")}
    if not 3 <= len(guides) <= 6: bad("Blog: 3-6 in-text guide links", f"{p}: {len(guides)}")
    if not 2 <= len(locs) <= 5: bad("Blog: 2-5 location links", f"{p}: {len(locs)}")
    txt = prose.get_text()
    for need in ("Local note:", "Related reading:", "Short answer:"):
        if need not in txt: bad("Blog structure", f"{p}: missing '{need}'")
    if not s.find(string=re.compile("About this article")): bad("Blog structure", f"{p}: author box")

# ---------- 4. word counts
RANGES = {"home": (1200, 1800), "services": (1000, 1900), "locations": (800, 1200), "blog": (1000, 2300)}
WC = {}
for p, s in pages.items():
    t = ptype(p)
    if t in RANGES:
        w = body_words(s); WC[p] = w
        lo, hi = RANGES[t]
        if not lo <= w <= hi: bad("Word counts", f"{p}: {w} (target {lo}-{hi})")

# ---------- 5. uniqueness
def shingles(txt, n=5):
    w = re.findall(r"[a-z0-9']+", txt.lower()); return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
locs = [f"/locations/{l[0]}/" for l in LOCATIONS]
SH = {p: shingles(main_text(pages[p])) for p in locs}
UNIQ = {}
for p in locs:
    worst = 100
    for o in locs:
        if o == p: continue
        u = 100 * len(SH[p] - SH[o]) / max(1, len(SH[p])); worst = min(worst, u)
    UNIQ[p] = round(worst, 1)
    if worst < 60: bad("Location pages >= 60% unique", f"{p}: {worst:.1f}%")
paras = defaultdict(set)
SKIP = ("About this article", "Last reviewed", "Document:", "By Laurel Dry Pros Editorial")
for p, s in pages.items():
    for el in s.select("main p, main li"):
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        if len(t.split()) >= 14 and not any(t.startswith(x) for x in SKIP) and not el.find_parent(class_=["band", "card", "cta-box", "author"]):
            paras[t].add(p)
for t, ps in paras.items():
    if len(ps) > 1: bad("No duplicate paragraphs (14+ words)", f"{sorted(ps)}: '{t[:90]}…'")

# ---------- 6. readability
FK = {}
LEGAL = {"/privacy-policy/", "/terms/", "/disclaimer/", "/accessibility/", "/editorial-policy/", "/404.html", "/glossary/"}
for p, s in pages.items():
    if p in LEGAL: continue
    m = s.select_one("main .prose")
    if not m: continue
    m = BeautifulSoup(str(m), "lxml")
    for x in m.select("table, .src"): x.decompose()
    txt = ". ".join(e.get_text(" ", strip=True).rstrip(".") for e in m.find_all(["p", "li", "h2", "h3", "summary"]))
    g = fk_grade(txt); FK[p] = g
    if g > 9: bad("Reading level FK <= 9", f"{p}: {g}")

# ---------- 7. schema
all_ids = set(); refs = []
for p, s in pages.items():
    for sc in s.find_all("script", type="application/ld+json"):
        try: data = json.loads(sc.string)
        except Exception as e: bad("Schema valid JSON", f"{p}: {e}"); continue
        def walk(o, top=False):
            if isinstance(o, dict):
                if "@id" in o and len(o) > 1: all_ids.add(o["@id"])
                elif "@id" in o and len(o) == 1: refs.append((p, o["@id"]))
                for k, v in o.items():
                    if k in ("@type",) and v in ("Review", "AggregateRating"): bad("No ratings/reviews", p)
                    if k in ("address", "geo", "aggregateRating", "review"): bad("No address/geo/ratings (SAB)", f"{p}: {k}")
                    walk(v)
            elif isinstance(o, list):
                for x in o: walk(x)
        walk(data)
        for node in data.get("@graph", []):
            if node.get("@type") == "FAQPage":
                vis = s.get_text(" ")
                for qn in node["mainEntity"]:
                    if qn["name"] not in vis: bad("FAQ schema visible", f"{p}: {qn['name']}")
for p, r in refs:
    if r not in all_ids: bad("Schema @id references resolve", f"{p}: {r}")
for p in [x for x in pages if ptype(x) in ("home", "services")]:
    js = " ".join(sc.string for sc in pages[p].find_all("script", type="application/ld+json"))
    if '"about"' not in js or '"mentions"' not in js: bad("Entity links (about/mentions)", p)

# ---------- 8. compliance
BANNED = [r"\bcertified\b", r"IICRC-certified", r"licensed technicians", r"insured and bonded", r"5-star", r"award-winning", r"minutes away",
          r"\b60 minutes\b", r"free estimate", r"\bbased in\b", r"\bhome base\b", r"\blorem\b", r"coming soon", r"example\.com", r"\[PLACEHOLDER\]",
          r"live person", r"live agent", r"real person", r"we guarantee", r"guaranteed", r"\b#1\b", r"best in", r"arrival window"]
for p, s in pages.items():
    vis = s.get_text(" ")
    for b in BANNED:
        if re.search(b, vis, re.I): bad("Banned wording", f"{p}: /{b}/")
    for m in re.finditer(r"\blicensed\b(\s+\w+){0,2}", vis, re.I):
        ctx = m.group(0).lower()
        if not re.search(r"licensed\s+(mold|plumber|plumbers|hvac|contractor|electrician|home improvement|professional|trades?)", ctx) and "law" not in ctx:
            bad("'Licensed' rule", f"{p}: '{m.group(0)}'")
    for m in re.finditer(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b", vis):
        if m.group(0) not in ("(301) 368-0221",): bad("Single phone number", f"{p}: {m.group(0)}")
    for a in s.find_all("a", href=re.compile("^tel:")):
        if a["href"] != "tel:" + TEL: bad("Single phone number", f"{p}: {a['href']}")
    if "Somerset" in vis or "11248" in vis or "20705" in vis and ptype(p) != "locations" and p not in ("/locations/",):
        if "Somerset" in vis or "11248" in vis: bad("No street address (SAB)", p)

# ---------- 9. glossary auto links
for p, s in pages.items():
    n = len([a for a in s.select("main .prose p a[href^='/glossary/#']")])
    if n > 4 and p != "/glossary/": bad("Glossary links <= 4", f"{p}: {n}")

# ---------- 10. performance
for f in SITE.rglob("*.html"):
    if f.stat().st_size > 100_000: bad("HTML < 100 KB", f"{f}: {f.stat().st_size}")
for f in SITE.rglob("*"):
    if f.suffix in (".jpg", ".webp", ".png") and f.stat().st_size > 200_000: bad("Images < 200 KB", f"{f.name}")
js = (SITE / "assets/js/main.js").stat().st_size
if js > 10_240: bad("JS <= 10 KB", js)
for p, s in pages.items():
    for sc in s.find_all("script", src=True):
        if not sc.has_attr("defer"): bad("No render-blocking JS", p)
    for l in s.find_all("link", rel="stylesheet"):
        if l.get("media") != "print" and not l.find_parent("noscript"): bad("No render-blocking CSS", p)

# ---------- report
checks = ["Internal links resolve", "No orphans", "Click depth <= 2", "3+ in-text inbound links", "Varied anchors", "No generic anchors", "External links",
          "Title <= 60 chars", "Meta <= 155 chars", "Unique titles", "Unique metas", "Unique H1s", "One H1", "No skipped headings", "Canonical", "OG tags", "Twitter card", "lang",
          "Image alt + dimensions", "Keyword placement", "Money link in first 150 words", "Blog: 3-6 in-text guide links", "Blog: 2-5 location links", "Blog structure",
          "Word counts", "Location pages >= 60% unique", "No duplicate paragraphs (14+ words)", "Reading level FK <= 9", "Schema valid JSON", "Schema @id references resolve",
          "FAQ schema visible", "No ratings/reviews", "No address/geo/ratings (SAB)", "Entity links (about/mentions)", "Banned wording", "'Licensed' rule", "Single phone number",
          "No street address (SAB)", "Glossary links <= 4", "HTML < 100 KB", "Images < 200 KB", "JS <= 10 KB", "No render-blocking JS", "No render-blocking CSS"]
fails = 0
for c in checks:
    st = "PASS" if not issues.get(c) else "FAIL"
    if st == "FAIL": fails += 1
    print(f"{st:4} | {c}" + ("" if st == "PASS" else f" | {len(issues[c])} issue(s)"))
    for m in issues.get(c, [])[:12]: print("       -", m)
extra = set(issues) - set(checks)
for c in extra: print("FAIL |", c, issues[c][:5])
json.dump({"wc": WC, "uniq": UNIQ, "fk": FK, "fails": fails, "issues": issues}, open(ROOT / "audit.json", "w"), indent=1, default=list)
print(f"\n{len(pages)} pages, {fails} failing checks")
sys.exit(1 if fails else 0)
