# Laurel Dry Pros — waterdamagerestorationlaurelmd.com

Static lead-gen site for water damage restoration in Laurel, MD (own-business call routing, service-area business, phone (301) 368-0221). Built for Cloudflare Pages.

## Layout

```
site/            ← deploy this folder (Cloudflare Pages "build output directory")
functions/api/   ← Cloudflare Pages Function: contact form → Resend
src/             ← content (Markdown + TOML front matter), CSS, JS, data, glossary
build.py         ← builds src/ → site/
gen_images.py    ← builds blog featured images (JPG + WebP, 1200×630)
fetch_photos.py  ← downloads the Pexels photos for home, service and location pages (WebP 1200w + 600w, JPG for schema/OG)
audit.py         ← self-audit (links, SEO, schema, uniqueness, readability, compliance, performance)
DELIVERY.md      ← delivery report: audit, image list, placeholders, deploy steps, 90-day plan
```

## Edit and rebuild

```bash
pip install markdown beautifulsoup4 lxml     # once
python3 gen_images.py     # only if blog titles change
python3 fetch_photos.py   # only if the photo list changes
python3 build.py
python3 audit.py          # must end with "0 failing checks"
```

All business facts (brand, phone, domain, services, locations, blog map) live in `src/data.py`. Change the phone there and rebuild; it updates every page, tel: link and schema node.

## Cloudflare Pages settings

- Framework preset: None
- Build command: *(leave empty — `site/` is committed pre-built)*
- Build output directory: `site`
- Root directory: `/` (so `functions/` is picked up)
- Environment variables (Production): `RESEND_API_KEY`, `LEAD_TO_EMAIL`, `LEAD_FROM_EMAIL`
