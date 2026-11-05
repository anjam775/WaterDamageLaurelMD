#!/usr/bin/env python3
"""Download the chosen Pexels photos (free Pexels license) and build WebP 1200w + 600w and JPG 1200x750 versions.
Run only when the photo list changes: python3 fetch_photos.py"""
import subprocess
from PIL import Image, ImageOps
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site/assets/img/photos"

# name: (pexels id, photographer, alt text, gravity for crop)
PHOTOS = {
    "home-crew": (4098778, "Matilda Wormwood", "Technician in protective gear treating a living room", "center"),
    "home-rain": (13307118, None, "Heavy rain pouring off a house gutter", "center"),
    "home-leak": (15206136, "Swastik Arora", "Water dripping from a leaking pipe joint", "center"),
    "svc-emergency-water-removal": (18302377, "Emmanuel Codden", "Standing water covering the floor of a room", "center"),
    "svc-water-mitigation-structural-drying": (6474127, "Tima Miroshnichenko", "Worker smoothing a wall during repairs after drying", "center"),
    "svc-flooded-basement-cleanup": (4092026, "Curtis Adams", "Unfinished basement with block walls, exposed joists and stairs", "center"),
    "svc-burst-pipe-water-damage": (6419128, "Anıl Karakaya", "Plumber's hands tightening a pipe fitting", "center"),
    "svc-ceiling-drywall-water-damage": (6474343, "Tima Miroshnichenko", "Worker sanding a new drywall ceiling", "north"),
    "svc-sewage-cleanup": (4176610, "Michelangelo Buonarroti", "Technician in a protective suit disinfecting a room with a fogger", "center"),
    "svc-mold-remediation": (4099468, "Matilda Wormwood", "Worker in a protective suit and respirator spraying a surface", "north"),
    "svc-storm-flood-damage": (28447774, "Helena Jankovičová Kováčová", "Suburban house surrounded by flood water after heavy rain", "center"),
    "svc-fire-smoke-damage": (25490577, "Jani Kantokoski", "Firefighters working at a burning house with heavy smoke", "center"),
    "loc-bowie-md": (5502221, "Curtis Adams", "Brick two-story home with a front lawn", "center"),
    "loc-columbia-md": (4682073, "Curtis Adams", "Two-story brick home with a lawn and mature trees", "center"),
    "loc-greenbelt-md": (5353946, "Curtis Adams", "Older single-family home with a front porch and garden", "center"),
    "loc-silver-spring-md": (11718917, "Sherry", "White colonial-style house with a lawn and trees", "center"),
    "loc-beltsville-md": (5178060, "Curtis Adams", "Brick suburban home with a front lawn", "center"),
    "loc-burtonsville-md": (8894802, "Clay Elliot", "Suburban house with a tree-lined front yard", "center"),
    "loc-odenton-fort-meade-md": (15409440, "Curtis Adams", "Row of brick townhouses with garages", "center"),
    "loc-maple-lawn-fulton-md": (10628469, "Curtis Adams", "Row of newer townhouses with driveways", "center"),
}

def credit(name):
    who = PHOTOS[name][1]
    return f"Photo: {who} / Pexels" if who else "Photo: Pexels"

def page_url(name):
    return f"https://www.pexels.com/photo/{PHOTOS[name][0]}/"

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    raw = Path("/tmp/px_raw"); raw.mkdir(exist_ok=True)
    for name, (pid, who, alt, grav) in PHOTOS.items():
        src = raw / f"{pid}.jpg"
        if not src.exists() or src.stat().st_size < 10000:
            url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=2000"
            subprocess.run(["curl", "-sfL", "--max-time", "60", "-o", str(src), url], check=True)
        im = ImageOps.fit(Image.open(src).convert("RGB"), (1200, 750), Image.LANCZOS, centering=(0.5, 0.0 if grav == "north" else 0.5))
        small = im.resize((600, 375), Image.LANCZOS)
        for img, out, fmt, qs in [(im, f"{name}.webp", "WEBP", (78, 70, 62, 54, 46, 40)), (small, f"{name}-600.webp", "WEBP", (76, 66)),
                                  (im, f"{name}.jpg", "JPEG", (74, 66, 58, 50, 44, 38))]:
            for q in qs:  # step quality down until the file is under the 180 KB budget
                kw = dict(quality=q, method=6) if fmt == "WEBP" else dict(quality=q, optimize=True, progressive=True)
                img.save(OUT / out, fmt, **kw)
                if (OUT / out).stat().st_size < 180_000: break
    print("photos:", len(PHOTOS))
