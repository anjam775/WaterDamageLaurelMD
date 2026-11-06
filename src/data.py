"""Site-wide data: business facts, services, locations, blog map. Single source of truth."""
BRAND = "Laurel Dry Pros"
DOMAIN = "https://waterdamagerestorationlaurelmd.com"
PHONE = "(301) 368-0221"          # display format (one format site-wide)
TEL = "+13013680221"               # tel: value (one value site-wide)
PUBLISHED = "2026-11-01"
PUBLISHED_H = "November 1, 2026"
OWNER_NOTE = "Laurel Dry Pros"
SOCIAL = [  # owner asked for platform logos with default links; real profile URLs to be added later
    ("Facebook", "https://www.facebook.com/"),
    ("Instagram", "https://www.instagram.com/"),
    ("X", "https://x.com/"),
    ("LinkedIn", "https://www.linkedin.com/"),
    ("YouTube", "https://www.youtube.com/"),
]

SERVICES = [
    # slug, short name, H1 service name, icon, card line
    ("emergency-water-removal", "Emergency Water Removal", "Emergency Water Removal", "drop",
     "Standing water pumped and extracted from floors, carpet and pad."),
    ("water-mitigation-structural-drying", "Water Mitigation & Drying", "Water Mitigation & Structural Drying", "fan",
     "Dehumidifiers, air movers and daily moisture readings until materials are dry."),
    ("flooded-basement-cleanup", "Flooded Basement Cleanup", "Flooded Basement Cleanup", "house",
     "Basement water out, wet finishes removed and the space dried and cleaned."),
    ("burst-pipe-water-damage", "Burst Pipe Water Damage", "Burst Pipe Water Damage Cleanup", "pipe",
     "Fast cleanup after frozen, split or leaking supply lines."),
    ("ceiling-drywall-water-damage", "Ceiling & Drywall Repair", "Ceiling & Drywall Water Damage Repair", "ceiling",
     "Sagging, stained or wet ceilings and walls opened, dried and rebuilt."),
    ("sewage-cleanup", "Sewage Cleanup", "Sewage Cleanup", "bio",
     "Safe removal and disinfection after sewer backups and toilet overflows."),
    ("mold-remediation", "Mold Remediation", "Mold Remediation", "mold",
     "Containment, HEPA filtration and removal of mold-damaged materials."),
    ("storm-flood-damage", "Storm & Flood Damage", "Storm & Flood Damage Restoration", "storm",
     "Cleanup after river flooding, flash floods, wind and roof leaks."),
    ("fire-smoke-damage", "Fire & Smoke Damage", "Fire & Smoke Damage Restoration", "fire",
     "Soot, smoke odor and firefighting water cleaned up and dried."),
]
SVC = {s[0]: s for s in SERVICES}

RELATED = {
    "emergency-water-removal": ["water-mitigation-structural-drying", "flooded-basement-cleanup", "burst-pipe-water-damage"],
    "water-mitigation-structural-drying": ["emergency-water-removal", "mold-remediation", "ceiling-drywall-water-damage"],
    "flooded-basement-cleanup": ["sewage-cleanup", "emergency-water-removal", "storm-flood-damage"],
    "burst-pipe-water-damage": ["emergency-water-removal", "ceiling-drywall-water-damage", "water-mitigation-structural-drying"],
    "ceiling-drywall-water-damage": ["burst-pipe-water-damage", "mold-remediation", "water-mitigation-structural-drying"],
    "sewage-cleanup": ["flooded-basement-cleanup", "mold-remediation", "storm-flood-damage"],
    "mold-remediation": ["water-mitigation-structural-drying", "flooded-basement-cleanup", "ceiling-drywall-water-damage"],
    "storm-flood-damage": ["flooded-basement-cleanup", "emergency-water-removal", "sewage-cleanup"],
    "fire-smoke-damage": ["emergency-water-removal", "water-mitigation-structural-drying", "mold-remediation"],
}

LOCATIONS = [
    # slug, display name, county, place type, zips, nearby slugs
    ("columbia-md", "Columbia", "Howard County", "Place", "21044, 21045 and 21046",
     ["maple-lawn-fulton-md", "burtonsville-md", "odenton-fort-meade-md"]),
    ("silver-spring-md", "Silver Spring", "Montgomery County", "Place", "20901 through 20906 and 20910",
     ["burtonsville-md", "beltsville-md", "greenbelt-md"]),
    ("bowie-md", "Bowie", "Prince George's County", "City", "20715, 20716, 20720 and 20721",
     ["greenbelt-md", "odenton-fort-meade-md", "beltsville-md"]),
    ("beltsville-md", "Beltsville", "Prince George's County", "Place", "20705",
     ["greenbelt-md", "burtonsville-md", "silver-spring-md"]),
    ("greenbelt-md", "Greenbelt", "Prince George's County", "City", "20770",
     ["beltsville-md", "bowie-md", "silver-spring-md"]),
    ("burtonsville-md", "Burtonsville", "Montgomery County", "Place", "20866",
     ["silver-spring-md", "beltsville-md", "maple-lawn-fulton-md"]),
    ("odenton-fort-meade-md", "Odenton & Fort Meade", "Anne Arundel County", "Place", "21113 and 20755",
     ["bowie-md", "columbia-md", "greenbelt-md"]),
    ("maple-lawn-fulton-md", "Maple Lawn & Fulton", "Howard County", "Place", "20759",
     ["columbia-md", "burtonsville-md", "odenton-fort-meade-md"]),
]
LOC = {l[0]: l for l in LOCATIONS}

BLOG_CATS = ["Storms & Flooding", "Leaks & Prevention", "Mold", "Insurance & Claims", "Restoration Basics"]

# slug -> (category, money page path)
BLOG = {
    "frozen-pipes-burst": ("Leaks & Prevention", "/services/burst-pipe-water-damage/"),
    "water-damage-restoration-cost": ("Restoration Basics", "/"),
    "does-homeowners-insurance-cover-water-damage": ("Insurance & Claims", "/"),
    "what-to-do-when-your-basement-floods": ("Storms & Flooding", "/services/flooded-basement-cleanup/"),
    "sump-pump-not-working": ("Leaks & Prevention", "/services/flooded-basement-cleanup/"),
    "how-long-does-it-take-for-mold-to-grow": ("Mold", "/services/mold-remediation/"),
    "musty-smell-in-basement": ("Mold", "/services/mold-remediation/"),
    "water-damage-on-ceiling": ("Leaks & Prevention", "/services/ceiling-drywall-water-damage/"),
    "sewage-backup-cleanup": ("Restoration Basics", "/services/sewage-cleanup/"),
    "water-mitigation-vs-restoration": ("Restoration Basics", "/services/water-mitigation-structural-drying/"),
    "water-heater-leaking": ("Leaks & Prevention", "/services/emergency-water-removal/"),
    "how-to-prepare-for-a-flood": ("Storms & Flooding", "/services/storm-flood-damage/"),
    # batch 2 (published 2026-11-04)
    "smoke-damage-cleanup": ("Restoration Basics", "/services/fire-smoke-damage/"),
    "does-homeowners-insurance-cover-mold": ("Insurance & Claims", "/services/mold-remediation/"),
    "crawl-space-mold": ("Mold", "/services/mold-remediation/"),
    "water-in-basement-after-heavy-rain": ("Storms & Flooding", "/services/flooded-basement-cleanup/"),
    "signs-of-water-damage-in-walls": ("Leaks & Prevention", "/services/ceiling-drywall-water-damage/"),
    "category-3-water": ("Restoration Basics", "/services/sewage-cleanup/"),
    "how-long-does-water-damage-restoration-take": ("Restoration Basics", "/services/water-mitigation-structural-drying/"),
    "what-does-a-water-mitigation-company-do": ("Restoration Basics", "/services/water-mitigation-structural-drying/"),
    "ice-dams": ("Storms & Flooding", "/services/ceiling-drywall-water-damage/"),
    "sewer-backup-insurance-maryland": ("Insurance & Claims", "/services/sewage-cleanup/"),
    "wet-carpet-drying": ("Leaks & Prevention", "/services/emergency-water-removal/"),
}

GUIDES = {  # helpful guides on each service page (supporting post first)
    "emergency-water-removal": ["wet-carpet-drying", "water-heater-leaking", "water-mitigation-vs-restoration"],
    "water-mitigation-structural-drying": ["what-does-a-water-mitigation-company-do", "how-long-does-water-damage-restoration-take", "water-mitigation-vs-restoration"],
    "flooded-basement-cleanup": ["water-in-basement-after-heavy-rain", "what-to-do-when-your-basement-floods", "sump-pump-not-working"],
    "burst-pipe-water-damage": ["frozen-pipes-burst", "signs-of-water-damage-in-walls", "does-homeowners-insurance-cover-water-damage"],
    "ceiling-drywall-water-damage": ["signs-of-water-damage-in-walls", "ice-dams", "water-damage-on-ceiling"],
    "sewage-cleanup": ["category-3-water", "sewer-backup-insurance-maryland", "sewage-backup-cleanup"],
    "mold-remediation": ["crawl-space-mold", "does-homeowners-insurance-cover-mold", "how-long-does-it-take-for-mold-to-grow"],
    "storm-flood-damage": ["how-to-prepare-for-a-flood", "water-in-basement-after-heavy-rain", "ice-dams"],
    "fire-smoke-damage": ["smoke-damage-cleanup", "does-homeowners-insurance-cover-water-damage", "water-damage-restoration-cost"],
}

# Wikipedia entities (sameAs) used in about/mentions; all are long-standing articles.
WIKI = {
    "Water damage": "https://en.wikipedia.org/wiki/Water_damage",
    "Flood": "https://en.wikipedia.org/wiki/Flood",
    "Indoor mold": "https://en.wikipedia.org/wiki/Indoor_mold",
    "Mold": "https://en.wikipedia.org/wiki/Mold",
    "Sanitary sewer overflow": "https://en.wikipedia.org/wiki/Sanitary_sewer_overflow",
    "Dehumidifier": "https://en.wikipedia.org/wiki/Dehumidifier",
    "Sump pump": "https://en.wikipedia.org/wiki/Sump_pump",
    "Water heating": "https://en.wikipedia.org/wiki/Water_heating",
    "Drywall": "https://en.wikipedia.org/wiki/Drywall",
    "Soot": "https://en.wikipedia.org/wiki/Soot",
    "Home insurance": "https://en.wikipedia.org/wiki/Home_insurance",
    "National Flood Insurance Program": "https://en.wikipedia.org/wiki/National_Flood_Insurance_Program",
    "Patuxent River": "https://en.wikipedia.org/wiki/Patuxent_River",
    "Laurel, Maryland": "https://en.wikipedia.org/wiki/Laurel,_Maryland",
    "Prince George's County, Maryland": "https://en.wikipedia.org/wiki/Prince_George%27s_County,_Maryland",
    "Howard County, Maryland": "https://en.wikipedia.org/wiki/Howard_County,_Maryland",
    "Montgomery County, Maryland": "https://en.wikipedia.org/wiki/Montgomery_County,_Maryland",
    "Anne Arundel County, Maryland": "https://en.wikipedia.org/wiki/Anne_Arundel_County,_Maryland",
    "Columbia, Maryland": "https://en.wikipedia.org/wiki/Columbia,_Maryland",
    "Silver Spring, Maryland": "https://en.wikipedia.org/wiki/Silver_Spring,_Maryland",
    "Bowie, Maryland": "https://en.wikipedia.org/wiki/Bowie,_Maryland",
    "Beltsville, Maryland": "https://en.wikipedia.org/wiki/Beltsville,_Maryland",
    "Greenbelt, Maryland": "https://en.wikipedia.org/wiki/Greenbelt,_Maryland",
    "Burtonsville, Maryland": "https://en.wikipedia.org/wiki/Burtonsville,_Maryland",
    "Odenton, Maryland": "https://en.wikipedia.org/wiki/Odenton,_Maryland",
    "Fort Meade, Maryland": "https://en.wikipedia.org/wiki/Fort_Meade,_Maryland",
    "Fulton, Maryland": "https://en.wikipedia.org/wiki/Fulton,_Maryland",
    "Frost": "https://en.wikipedia.org/wiki/Frost",
    "Plumbing": "https://en.wikipedia.org/wiki/Plumbing",
}

LOC_WIKI = {"columbia-md": ["Columbia, Maryland"], "silver-spring-md": ["Silver Spring, Maryland"],
            "bowie-md": ["Bowie, Maryland"], "beltsville-md": ["Beltsville, Maryland"],
            "greenbelt-md": ["Greenbelt, Maryland"], "burtonsville-md": ["Burtonsville, Maryland"],
            "odenton-fort-meade-md": ["Odenton, Maryland", "Fort Meade, Maryland"],
            "maple-lawn-fulton-md": ["Fulton, Maryland"]}
COUNTY_WIKI = {"Howard County": "Howard County, Maryland", "Montgomery County": "Montgomery County, Maryland",
               "Prince George's County": "Prince George's County, Maryland", "Anne Arundel County": "Anne Arundel County, Maryland"}

# pages changed after launch -> sitemap lastmod
UPDATED = "2026-11-04"

GA_ID = "G-DVX0GTXHKZ"  # Google Analytics 4 measurement ID
