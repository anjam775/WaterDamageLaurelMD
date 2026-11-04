# Laurel Dry Pros — Delivery Report

Site: waterdamagerestorationlaurelmd.com · Brand: Laurel Dry Pros · Phone: (301) 368-0221 · Own-business routing · Service-area business (no public address) · Built November 1, 2026

## 1. Folder tree (site/)

```
site/
├── index.html                         Home (pillar: water damage restoration Laurel MD)
├── 404.html                           noindex
├── services/index.html                Services hub (CollectionPage)
│   ├── emergency-water-removal/
│   ├── water-mitigation-structural-drying/
│   ├── flooded-basement-cleanup/
│   ├── burst-pipe-water-damage/
│   ├── ceiling-drywall-water-damage/
│   ├── sewage-cleanup/
│   ├── mold-remediation/
│   ├── storm-flood-damage/
│   └── fire-smoke-damage/
├── locations/index.html               Locations hub (CollectionPage)
│   ├── columbia-md/  silver-spring-md/  bowie-md/  beltsville-md/
│   └── greenbelt-md/  burtonsville-md/  odenton-fort-meade-md/  maple-lawn-fulton-md/
├── blog/index.html                    Blog hub (Blog + categories)
│   └── 23 posts (see blog map)
├── glossary/                          54 terms, DefinedTermSet
├── about/  contact/  disclaimer/  editorial-policy/  privacy-policy/  terms/  accessibility/
├── assets/css/site.css  assets/js/main.js (2.4 KB)  assets/img/ (logo, icons, og, blog/*.jpg|webp)
├── favicon.ico  favicon.svg  apple-touch-icon.png  site.webmanifest
├── robots.txt  sitemap.xml (41 URLs, lastmod + priority)
└── _headers (CSP w/ hash, HSTS, immutable assets)  _redirects (legacy paths)
functions/api/contact.js               Form → Resend (honeypot, validation, consent)
```

53 HTML pages: 1 home + 9 services + 8 locations + 23 posts + 3 hubs + glossary + 7 trust/legal + 404.

## 2. Self-audit (audit.py) — final run: 0 failing checks

| Check | Status | Issue found during build | Fix applied |
|---|---|---|---|
| Internal links resolve (incl. glossary anchors) | PASS | — | — |
| No orphans; click depth ≤ 2 | PASS | — | — |
| ≥ 3 in-text inbound links (services, locations, posts) | PASS | — | Local note / Related reading paragraphs on every service and post |
| Varied, descriptive anchors; no generic anchors | PASS | — | — |
| Titles ≤ 60, metas ≤ 155, all unique | PASS | 13 metas were 156–162 chars | Trimmed |
| One H1, unique H1s, no skipped headings | PASS | — | — |
| Canonical, OG, Twitter, lang=en-US, robots | PASS | — | — |
| Keyword in title/meta/H1/first 100 words/H2/slug | PASS | 5 posts missing kw in an H2 or first 100 words | H2s/short answer rewritten |
| Blog: money link in first 150 words; 3–6 guide links; 2–5 location links; Short answer, Local note, Related reading, author box | PASS | Checklist renderer emitted a stray `</div>` that cut posts short | Renderer fixed |
| Word counts (home 1,200–1,800; services 1,000–1,500*; locations 800–1,200; posts 1,000–2,300) | PASS | 5 locations 760–797 w, storm page 975 w | Added unique local sections |
| Location pages ≥ 60% unique (5-word shingles) | PASS | — | Scores 96.3–98.7% |
| No duplicate paragraphs ≥ 14 words | PASS | NFIP sentence repeated in 2 posts | Reworded |
| Reading level FK ≤ 9 | PASS | — | Range 4.3–7.4 |
| Schema valid, @ids resolve, FAQs visible, entity about/mentions | PASS | — | — |
| No Review/AggregateRating, no address/geo (SAB) | PASS | — | — |
| Banned wording (certified, free estimate, based in, 5-star, etc.) | PASS | "home turf" on Beltsville page | Removed |
| "Licensed" only next to plumber/contractor/mold/HVAC/law | PASS | 2 phrasings | Reworded |
| Single phone number/format; no street address | PASS | — | — |
| Glossary auto-links ≤ 4 per page | PASS | Plurals not matched | Matcher fixed |
| Performance: HTML < 100 KB, images < 200 KB, JS ≤ 10 KB, no render-blocking CSS/JS | PASS | — | Critical CSS inline (CSP hash), full CSS deferred |
| Responsive 360/768/1280 — no horizontal scroll, no console errors (126 page loads) | PASS | — | — |
| Interactive states: dropdowns, mobile menu, sticky call bar, card hover, focus ring, click-to-load map | PASS | Hero H1 inherited navy on navy; logo "DRY PROS" low contrast | Fixed colors |
| Fact accuracy | PASS | Unverifiable "pipes freeze at 20°F" claim; WSSC wrongly implied for Howard/Anne Arundel; 2 unverified source URLs | Removed / corrected / replaced with verified sources |

*Services run 1,013–1,279 words, beating the ranking competitor pages fetched (≈250–750 words main body).

Word counts: home 1,567 · services 1,013–1,279 · locations 823–865 · posts 1,074–1,376.

Known limits of the audit: Lighthouse was not run (no Lighthouse in this environment); performance was checked by budget (sizes, blocking resources, dimensions). Blog competitor word counts were not benchmarked post by post; Semrush SERPs and question data were pulled for all 12 keywords.

## 3. Image list (photos to add when you have real ones)

The site ships with no stock photos (fast LCP, nothing fake). Blog posts use generated branded 1200×630 graphics. Recommended real photos:

| Filename | Placement | Alt text | Source idea |
|---|---|---|---|
| hero-water-extraction.webp | Home hero (right side) | Laurel Dry Pros crew extracting water from a basement carpet | Your own job photo |
| svc-emergency-water-removal.webp | Emergency Water Removal, top | Truck-mounted extractor hose in a flooded room | Job photo |
| svc-drying.webp | Water Mitigation & Drying | Dehumidifier and air movers drying a wall | Job photo |
| svc-basement.webp | Flooded Basement Cleanup | Flood cut on basement drywall during drying | Job photo |
| svc-burst-pipe.webp | Burst Pipe | Split copper pipe in an opened wall | Job photo |
| svc-ceiling.webp | Ceiling & Drywall | Stained ceiling opened for drying | Job photo |
| svc-sewage.webp | Sewage Cleanup | Technician in protective gear with containment | Job photo |
| svc-mold.webp | Mold Remediation | Plastic containment with HEPA air scrubber | Job photo |
| svc-storm.webp | Storm & Flood | Roof tarp after storm damage | Job photo |
| svc-fire.webp | Fire & Smoke | Soot cleaning on a ceiling | Job photo |
| loc-[town].webp (×8) | Each location page | e.g. "Lake Kittamaqundi in Columbia, MD" | Your own photos of local landmarks |
| team.webp | About | The Laurel Dry Pros crew | Real team photo |

Use WebP, < 200 KB, explicit width/height, lazy-load all but the hero.

## 4. Placeholder / owner-action list

- **Social icons** link to platform home pages (facebook.com, instagram.com, x.com, linkedin.com, youtube.com) as you asked. Swap in real profile URLs in `src/data.py` → `SOCIAL`, then add them to Organization `sameAs`.
- **Resend:** set `RESEND_API_KEY`, `LEAD_TO_EMAIL`, `LEAD_FROM_EMAIL` in Cloudflare Pages; verify the sending domain in Resend.
- **Licenses / certifications:** none shown. Add your MHIC number (Maryland requires it on contracts, trucks and ads) once you're ready.
- **Reviews / ratings:** none shown; no review schema.
- **Owner name** on legal pages: currently "Laurel Dry Pros". Add the legal entity name if different.
- **Google Business Profile:** create as a service-area business (hide address), name and phone exactly as on the site.
- **Analytics:** none installed. `main.js` pushes `call_click` and `form_submit` to `dataLayer` if you add GTM (update CSP in `_headers`).
- **Real photos:** see section 3.
- **Hours:** 24/7 is in schema (`openingHoursSpecification`) and copy, per your intake.

## 5. Deploy and launch

1. **GitHub:** code is in `anjam775/WaterDamageLaurelMD` (main).
2. **Cloudflare Pages:** Create project → Connect to Git → pick the repo. Framework: None. Build command: empty. Output directory: `site`. Root: `/`.
3. **Environment variables:** add the three Resend variables (Production), then redeploy.
4. **Custom domain:** Pages → Custom domains → add `waterdamagerestorationlaurelmd.com` and `www`. At Spaceship, point nameservers to Cloudflare (or add the CNAME records Cloudflare shows). Add a redirect rule www → apex.
5. **Check live:** open a few pages, tap the phone link, submit the form once, confirm the Resend email arrives.
6. **Google Search Console:** add the domain property (DNS TXT), submit `https://waterdamagerestorationlaurelmd.com/sitemap.xml`, request indexing for home + 9 services.
7. **Bing Webmaster Tools:** import from GSC; submit the sitemap.
8. **GBP + citations:** create the GBP as a service-area business (Laurel + 8 towns). Use the exact name "Laurel Dry Pros" and phone (301) 368-0221 everywhere (GBP, Bing Places, Apple Business Connect, Yelp, BBB, Angi, Nextdoor). Same NAP, no address shown.
9. **Validate:** run a page through Google's Rich Results Test and PageSpeed Insights.

## 6. Content plan

**Batch 2 published November 4, 2026 (11 posts, all keywords validated in Semrush on Nov 1):** smoke damage cleanup (3,600), does homeowners insurance cover mold (3,600/43), crawl space mold (6,600/9), water in basement after heavy rain (390/8), signs of water damage in walls (390/21), Category 3 water (170/18), how long does water damage restoration take (140/6), what does a water mitigation company do (320), ice dams (3,600/69), sewer backup insurance (320/12), wet carpet drying (210/12). Site now has 23 posts and 53 pages; audit 0 failing checks.

Note: Semrush API credits were exhausted on Nov 4, so batch 2 used the Nov 1 validated volumes; SERP top-10 and question pulls were not re-run for these 11.

**Next (day 60 to 90):** pull Semrush positions, expand pages ranking 8 to 20, then plan the next cluster (slab leaks, commercial water damage, condo leaks, water damage drywall).

Each new post: Semrush SERP brief first, then the Blog Post Criteria checklist, add it to `src/data.py` (BLOG + a service's GUIDES), add 2 to 3 in-text links from older pages, `python3 gen_images.py && python3 build.py && python3 audit.py`.
