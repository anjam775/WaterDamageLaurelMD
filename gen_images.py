#!/usr/bin/env python3
"""Generate 1200x630 featured images (JPG for social, WebP for display) for each blog post."""
import subprocess, sys, textwrap, html
from pathlib import Path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from data import BLOG
import tomllib, re

OUT = ROOT / "site/assets/img/blog"; OUT.mkdir(parents=True, exist_ok=True)
ACCENT = {"Storms & Flooding": "#1368AA", "Leaks & Prevention": "#0E7490", "Mold": "#4D7C0F", "Insurance & Claims": "#6D28D9", "Restoration Basics": "#C2410C"}

for sl, (cat, _) in BLOG.items():
    raw = (ROOT / "src/content/blog" / f"{sl}.md").read_text()
    fm = tomllib.loads(re.match(r"\+\+\+\n(.*?)\n\+\+\+", raw, re.S).group(1))
    lines = textwrap.wrap(fm["h1"], 28)[:4]
    fs = 62 if len(lines) <= 3 else 54
    y0 = 300 - (len(lines) - 1) * fs * 0.6
    tspans = "".join(f'<text x="80" y="{y0 + i * fs * 1.18:.0f}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{fs}" font-weight="700" fill="#fff">{html.escape(l)}</text>' for i, l in enumerate(lines))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B2545"/><stop offset="1" stop-color="#123A66"/></linearGradient></defs>
<rect width="1200" height="630" fill="url(#g)"/>
<circle cx="1060" cy="120" r="230" fill="{ACCENT[cat]}" opacity=".35"/><circle cx="1130" cy="560" r="160" fill="#1368AA" opacity=".25"/>
<rect x="80" y="70" rx="22" height="44" width="{len(cat) * 15 + 40}" fill="{ACCENT[cat]}"/>
<text x="100" y="100" font-family="DejaVu Sans,Arial,sans-serif" font-size="24" font-weight="700" fill="#fff">{html.escape(cat)}</text>
{tspans}
<g transform="translate(80 520) scale(.9)"><rect width="56" height="56" rx="12" fill="#fff" opacity=".12"/><path d="M28 8.5C22 17.4 15 25.4 15 33.3a13 13 0 0 0 26 0c0-7.9-7-15.9-13-24.8z" fill="#fff"/><path d="M21.2 34.2l5.2 5.2 9.6-10.5" fill="none" stroke="#C2410C" stroke-width="4" stroke-linecap="round"/></g>
<text x="145" y="560" font-family="DejaVu Sans,Arial,sans-serif" font-size="28" font-weight="700" fill="#fff">Laurel Dry Pros</text>
<text x="145" y="590" font-family="DejaVu Sans,Arial,sans-serif" font-size="20" fill="#9FC9EE">Water damage guides for Laurel, MD</text>
</svg>'''
    svgp = Path(f"/tmp/{sl}.svg"); svgp.write_text(svg)
    png = Path(f"/tmp/{sl}.png")
    subprocess.run(["rsvg-convert", str(svgp), "-o", str(png)], check=True)
    subprocess.run(["convert", str(png), "-strip", "-quality", "82", str(OUT / f"{sl}.jpg")], check=True)
    subprocess.run(["convert", str(png), "-strip", "-quality", "80", "-define", "webp:method=6", str(OUT / f"{sl}.webp")], check=True)
print("images:", len(list(OUT.glob("*.webp"))))
