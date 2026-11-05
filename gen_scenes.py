#!/usr/bin/env python3
"""Generate illustrated scene images (SVG -> WebP 1200w + 600w, JPG for schema) for home, service and location pages."""
import subprocess, random
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site/assets/img/scenes"
W, H = 1200, 750
NAVY, BLUE, LBLUE, ORANGE, SKY = "#0B2545", "#1368AA", "#9FC9EE", "#C2410C", "#DCEBF7"
WATER = "#3B8FD9"

# ------------------------------------------------------------------ primitives
def svg(body, bg="#EEF2F6"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>'

def g(inner, x=0, y=0, s=1):
    return f'<g transform="translate({x} {y}) scale({s})">{inner}</g>'

def room(wall="#E9EEF3", floor="#C9A27A", horizon=520, window=True, x_win=760):
    o = f'<rect width="{W}" height="{horizon}" fill="{wall}"/>'
    o += f'<polygon points="0,{horizon} {W},{horizon} {W},{H} 0,{H}" fill="{floor}"/>'
    for i in range(1, 9):  # floor boards in perspective
        x = i * W / 9
        o += f'<line x1="{x}" y1="{horizon}" x2="{(x - W/2) * 1.6 + W/2}" y2="{H}" stroke="#000" stroke-opacity=".07" stroke-width="3"/>'
    o += f'<rect y="{horizon - 22}" width="{W}" height="22" fill="#fff"/><rect y="{horizon - 2}" width="{W}" height="4" fill="#000" opacity=".08"/>'
    if window:
        o += f'<rect x="{x_win}" y="90" width="260" height="230" rx="6" fill="#fff"/><rect x="{x_win+14}" y="104" width="232" height="202" fill="{SKY}"/>'
        o += f'<path d="M{x_win+14} 270 q60 -40 120 -10 t112 -20 v66 h-232z" fill="#B5D3A8"/>'
        o += f'<rect x="{x_win+127}" y="104" width="6" height="202" fill="#fff"/><rect x="{x_win+14}" y="202" width="232" height="6" fill="#fff"/>'
        o += f'<rect x="{x_win-10}" y="318" width="280" height="12" rx="3" fill="#fff"/>'
    return o

def water(level=600, color=WATER, op=.55):
    d = f"M0 {level} " + " ".join(f"q 37.5 {-10 if i % 2 == 0 else 10} 75 0" for i in range(16)) + f" V{H} H0z"
    o = f'<path d="{d}" fill="{color}" opacity="{op}"/>'
    for x, y, w in [(180, level + 40, 90), (520, level + 70, 120), (900, level + 35, 80), (330, level + 110, 70), (1040, level + 95, 100)]:
        o += f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="6" fill="#fff" opacity=".35"/>'
    return o

def person(x, y, s=1, suit=NAVY, cap=BLUE, skin="#C68B5E", pose="stand", ppe=False):
    """Feet at (x, y). ~300px tall at s=1."""
    o = ""
    o += f'<rect x="-34" y="-150" width="28" height="150" rx="12" fill="{suit}"/><rect x="6" y="-150" width="28" height="150" rx="12" fill="{suit}"/>'
    o += f'<rect x="-40" y="-8" width="38" height="14" rx="7" fill="#1F2937"/><rect x="2" y="-8" width="38" height="14" rx="7" fill="#1F2937"/>'
    o += f'<rect x="-46" y="-275" width="92" height="140" rx="30" fill="{suit}"/>'
    if not ppe:
        o += f'<rect x="-46" y="-215" width="92" height="12" fill="{ORANGE}"/>'
    if pose == "reach":
        o += f'<rect x="30" y="-262" width="24" height="110" rx="12" fill="{suit}" transform="rotate(-55 42 -262)"/>'
        o += f'<rect x="-54" y="-262" width="24" height="110" rx="12" fill="{suit}" transform="rotate(-35 -42 -262)"/>'
    else:
        o += f'<rect x="38" y="-268" width="24" height="115" rx="12" fill="{suit}" transform="rotate(-20 50 -268)"/>'
        o += f'<rect x="-62" y="-268" width="24" height="115" rx="12" fill="{suit}" transform="rotate(10 -50 -268)"/>'
    o += f'<circle cx="0" cy="-310" r="34" fill="{skin}"/>'
    if ppe:
        o += f'<circle cx="0" cy="-310" r="40" fill="none" stroke="{suit}" stroke-width="12"/><rect x="-26" y="-306" width="52" height="24" rx="10" fill="#374151"/>'
        o += f'<rect x="-30" y="-334" width="60" height="18" rx="8" fill="#A7F3D0" opacity=".8"/>'
    else:
        o += f'<path d="M-36 -318 a36 34 0 0 1 72 0z" fill="{cap}"/><rect x="0" y="-322" width="50" height="10" rx="5" fill="{cap}"/>'
    return g(o, x, y, s)

def air_mover(x, y, s=1, c=ORANGE):
    o = f'<path d="M0 0 h150 a10 10 0 0 0 10 -10 v-40 q0 -70 -80 -80 q-80 -2 -80 76z" fill="{c}"/>'
    o += f'<circle cx="80" cy="-62" r="44" fill="{NAVY}"/><circle cx="80" cy="-62" r="30" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="5" stroke-dasharray="10 7"/>'
    o += f'<rect x="150" y="-48" width="60" height="38" rx="4" fill="{c}"/><rect x="200" y="-52" width="10" height="46" fill="{NAVY}"/>'
    o += f'<rect x="10" y="0" width="140" height="10" rx="5" fill="#1F2937"/>'
    for i in range(3):
        o += f'<path d="M225 {-40 + i * 12} h{50 + i * 10}" stroke="{LBLUE}" stroke-width="5" stroke-linecap="round" opacity=".9"/>'
    return g(o, x, y, s)

def dehu(x, y, s=1, c=NAVY):
    o = f'<rect x="0" y="-230" width="130" height="230" rx="14" fill="{c}"/><rect x="18" y="-212" width="94" height="50" rx="6" fill="#16365F"/>'
    o += f'<rect x="30" y="-200" width="44" height="22" rx="3" fill="#7DD3FC"/><circle cx="92" cy="-189" r="8" fill="#34D399"/>'
    for i in range(7):
        o += f'<rect x="18" y="{-148 + i * 16}" width="94" height="7" rx="3" fill="#000" opacity=".25"/>'
    o += f'<circle cx="22" cy="6" r="10" fill="#1F2937"/><circle cx="108" cy="6" r="10" fill="#1F2937"/><rect x="40" y="-252" width="50" height="26" rx="10" fill="none" stroke="{c}" stroke-width="8"/>'
    return g(o, x, y, s)

def scrubber(x, y, s=1):
    o = f'<rect x="0" y="-150" width="190" height="150" rx="12" fill="#E5E7EB" stroke="#9CA3AF" stroke-width="4"/>'
    o += f'<circle cx="95" cy="-80" r="48" fill="#fff" stroke="#9CA3AF" stroke-width="4"/>'
    for r in (36, 24, 12): o += f'<circle cx="95" cy="-80" r="{r}" fill="none" stroke="{BLUE}" stroke-width="3" opacity=".6"/>'
    o += f'<rect x="190" y="-115" width="50" height="40" fill="{LBLUE}"/><path d="M240 -115 q60 -10 90 -60" stroke="{LBLUE}" stroke-width="40" fill="none"/>'
    o += f'<circle cx="25" cy="6" r="10" fill="#1F2937"/><circle cx="165" cy="6" r="10" fill="#1F2937"/>'
    return g(o, x, y, s)

def plant(x, y, s=1):
    o = f'<path d="M-30 0 h60 l-8 -60 h-44z" fill="{ORANGE}" opacity=".85"/>'
    for a, l in [(-30, 90), (0, 120), (30, 90), (-55, 70), (55, 70)]:
        o += f'<ellipse cx="0" cy="-{60 + l / 2}" rx="16" ry="{l / 2}" fill="#4D7C0F" transform="rotate({a} 0 -60)"/>'
    return g(o, x, y, s)

def couch(x, y, s=1, c="#64748B"):
    o = f'<rect x="0" y="-150" width="360" height="90" rx="26" fill="{c}"/><rect x="-20" y="-90" width="400" height="70" rx="22" fill="{c}"/>'
    o += f'<rect x="-30" y="-120" width="60" height="110" rx="24" fill="#475569"/><rect x="330" y="-120" width="60" height="110" rx="24" fill="#475569"/>'
    o += f'<rect x="0" y="-22" width="14" height="22" fill="#334155"/><rect x="346" y="-22" width="14" height="22" fill="#334155"/>'
    return g(o, x, y, s)

def bucket(x, y, s=1):
    o = f'<path d="M-40 -80 h80 l-10 80 h-60z" fill="{BLUE}"/><ellipse cx="0" cy="-80" rx="40" ry="10" fill="#0E4F85"/><path d="M-38 -80 q38 -60 76 0" stroke="#475569" stroke-width="4" fill="none"/>'
    return g(o, x, y, s)

def drips(x, y0, n=3, gap=40):
    o = ""
    for i in range(n):
        yy = y0 + i * gap
        o += f'<path d="M{x} {yy} q-9 14 0 22 q9 -8 0 -22z" fill="{WATER}"/>'
    return o

def moisture_meter(x, y, s=1):
    o = f'<rect x="0" y="0" width="70" height="120" rx="12" fill="{ORANGE}"/><rect x="10" y="12" width="50" height="34" rx="4" fill="#ECFCCB"/>'
    o += f'<path d="M16 34 h10 l5 -12 l6 20 l5 -8 h12" stroke="#15803D" stroke-width="3" fill="none"/><circle cx="35" cy="72" r="12" fill="{NAVY}"/>'
    o += f'<rect x="22" y="120" width="6" height="26" fill="#9CA3AF"/><rect x="42" y="120" width="6" height="26" fill="#9CA3AF"/>'
    return g(o, x, y, s)

def tree(x, y, s=1, c="#4D7C0F"):
    o = f'<rect x="-10" y="-90" width="20" height="90" fill="#7C5A3A"/><circle cx="0" cy="-130" r="70" fill="{c}"/><circle cx="-40" cy="-100" r="45" fill="{c}"/><circle cx="42" cy="-104" r="48" fill="{c}"/>'
    o += f'<circle cx="-20" cy="-150" r="30" fill="#fff" opacity=".08"/>'
    return g(o, x, y, s)

def pine(x, y, s=1):
    o = '<rect x="-8" y="-40" width="16" height="40" fill="#7C5A3A"/>'
    for i, w in enumerate([90, 72, 54]):
        o += f'<polygon points="{-w},{-40 - i * 55} {w},{-40 - i * 55} 0,{-150 - i * 55}" fill="#3F6212"/>'
    return g(o, x, y, s)

def cloud(x, y, s=1, c="#fff", op=1):
    o = f'<g opacity="{op}"><ellipse cx="0" cy="0" rx="90" ry="40" fill="{c}"/><circle cx="-40" cy="-20" r="40" fill="{c}"/><circle cx="25" cy="-35" r="50" fill="{c}"/><circle cx="70" cy="-5" r="35" fill="{c}"/></g>'
    return g(o, x, y, s)

def rain(x0, x1, y0, y1, n=60, seed=1, op=.6):
    r = random.Random(seed); o = ""
    for _ in range(n):
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        o += f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - 10:.0f}" y2="{y + 34:.0f}" stroke="{LBLUE}" stroke-width="4" stroke-linecap="round" opacity="{op}"/>'
    return o

def house(x, y, s=1, style="colonial", body="#F5EBDD", roof="#5B6B7F", door=ORANGE, trim="#fff"):
    """Base at (x, y)."""
    o = ""
    def win(wx, wy, ww=50, wh=60):
        return f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="{trim}"/><rect x="{wx+5}" y="{wy+5}" width="{ww-10}" height="{wh-10}" fill="{SKY}"/><rect x="{wx + ww/2 - 2}" y="{wy+5}" width="4" height="{wh-10}" fill="{trim}"/>'
    if style == "colonial":
        o += f'<rect x="0" y="-260" width="320" height="260" fill="{body}"/><polygon points="-20,-260 340,-260 160,-370" fill="{roof}"/>'
        o += win(30, -230) + win(135, -230) + win(240, -230) + win(30, -120) + win(240, -120)
        o += f'<rect x="135" y="-110" width="50" height="110" fill="{door}"/><rect x="250" y="-330" width="30" height="60" fill="#8B5E3C"/>'
    elif style == "rambler":
        o += f'<rect x="0" y="-140" width="380" height="140" fill="{body}"/><polygon points="-25,-140 405,-140 340,-215 40,-215" fill="{roof}"/>'
        o += win(30, -110, 70, 55) + win(260, -110, 90, 55) + f'<rect x="160" y="-110" width="48" height="110" fill="{door}"/>'
    elif style == "cape":
        o += f'<rect x="0" y="-150" width="300" height="150" fill="{body}"/><polygon points="-20,-150 320,-150 150,-310" fill="{roof}"/>'
        o += f'<rect x="60" y="-235" width="50" height="45" fill="{roof}"/><rect x="190" y="-235" width="50" height="45" fill="{roof}"/>' + win(65, -228, 40, 38) + win(195, -228, 40, 38)
        o += win(30, -115) + win(220, -115) + f'<rect x="125" y="-110" width="50" height="110" fill="{door}"/>'
    elif style == "split":
        o += f'<rect x="0" y="-150" width="200" height="150" fill="{body}"/><rect x="200" y="-230" width="200" height="230" fill="{body}" stroke="#000" stroke-opacity=".06"/>'
        o += f'<polygon points="-15,-150 215,-150 120,-215 0,-215" fill="{roof}"/><polygon points="185,-230 415,-230 300,-310" fill="{roof}"/>'
        o += win(30, -115, 70, 55) + win(230, -200) + win(320, -200) + win(230, -100) + f'<rect x="130" y="-110" width="45" height="110" fill="{door}"/>'
    elif style == "townrow":
        cols = ["#F5EBDD", "#E7D3C1", "#DCE6EF", "#EADBC8"]
        for i in range(4):
            bx = i * 120; c = cols[i % 4]
            o += f'<rect x="{bx}" y="-260" width="120" height="260" fill="{c}" stroke="#000" stroke-opacity=".08"/>'
            o += f'<polygon points="{bx - 6},-260 {bx + 126},-260 {bx + 60},-305" fill="{roof}"/>'
            o += win(bx + 35, -235) + win(bx + 35, -150) + f'<rect x="{bx + 38}" y="-75" width="44" height="75" fill="{door if i % 2 == 0 else BLUE}"/>'
    elif style == "garden":  # 1930s flat-roof garden homes
        for i in range(3):
            bx = i * 150
            o += f'<rect x="{bx}" y="-170" width="150" height="170" fill="{body}" stroke="#000" stroke-opacity=".08"/><rect x="{bx - 4}" y="-182" width="158" height="14" fill="{roof}"/>'
            o += win(bx + 20, -145, 45, 50) + win(bx + 85, -145, 45, 50) + f'<rect x="{bx + 52}" y="-80" width="44" height="80" fill="{door if i != 1 else BLUE}"/>'
            o += f'<rect x="{bx + 40}" y="-92" width="70" height="10" fill="{roof}"/>'
    elif style == "bungalow":
        o += f'<rect x="0" y="-160" width="280" height="160" fill="{body}"/><polygon points="-30,-160 310,-160 140,-260" fill="{roof}"/>'
        o += f'<rect x="-10" y="-80" width="300" height="12" fill="{roof}"/><rect x="0" y="-80" width="12" height="80" fill="{trim}"/><rect x="268" y="-80" width="12" height="80" fill="{trim}"/>'
        o += win(40, -140, 60, 50) + win(180, -140, 60, 50) + f'<rect x="118" y="-68" width="44" height="68" fill="{door}"/>'
    elif style == "tower":
        o += f'<rect x="0" y="-420" width="170" height="420" fill="#CBD5E1"/>'
        for r in range(9):
            for c in range(4):
                o += f'<rect x="{18 + c * 38}" y="{-400 + r * 44}" width="22" height="28" fill="{SKY}"/>'
    return g(o, x, y, s)

def ground(y=560, c="#A3C585", road=True):
    o = f'<rect y="{y}" width="{W}" height="{H - y}" fill="{c}"/>'
    if road:
        o += f'<rect y="{y + 90}" width="{W}" height="90" fill="#6B7280"/>'
        for i in range(12):
            o += f'<rect x="{i * 110 + 20}" y="{y + 132}" width="60" height="6" fill="#F8FAFC"/>'
        o += f'<rect y="{y + 80}" width="{W}" height="12" fill="#D1D5DB"/>'
    return o

def pin(x, y, s=1):
    o = f'<ellipse cx="0" cy="6" rx="26" ry="8" fill="#000" opacity=".2"/><path d="M0 0 C-12 -30 -48 -55 -48 -95 a48 48 0 0 1 96 0 C48 -55 12 -30 0 0z" fill="{ORANGE}"/>'
    o += f'<circle cx="0" cy="-95" r="22" fill="#fff"/><path d="M0 -112 c-7 10 -14 18 -14 26 a14 14 0 0 0 28 0 c0 -8 -7 -16 -14 -26z" fill="{BLUE}"/>'
    return g(o, x, y, s)

def van(x, y, s=1):
    o = f'<rect x="0" y="-150" width="300" height="130" rx="18" fill="#fff" stroke="#CBD5E1" stroke-width="4"/><path d="M300 -130 h70 l50 60 v50 h-120z" fill="#fff" stroke="#CBD5E1" stroke-width="4"/>'
    o += f'<path d="M312 -118 h52 l36 44 h-88z" fill="{SKY}"/><rect x="0" y="-80" width="420" height="18" fill="{BLUE}"/><rect x="0" y="-62" width="420" height="8" fill="{ORANGE}"/>'
    o += f'<g transform="translate(40 -135) scale(.9)"><path d="M28 8.5C22 17.4 15 25.4 15 33.3a13 13 0 0 0 26 0c0-7.9-7-15.9-13-24.8z" fill="{BLUE}"/></g>'
    for cx in (80, 340):
        o += f'<circle cx="{cx}" cy="-18" r="34" fill="#1F2937"/><circle cx="{cx}" cy="-18" r="14" fill="#9CA3AF"/>'
    return g(o, x, y, s)

def sky(bg=SKY, sun=True, h=560):
    o = f'<rect width="{W}" height="{h}" fill="{bg}"/>'
    if sun: o += f'<circle cx="1050" cy="110" r="60" fill="#FDE68A"/>'
    return o

# ------------------------------------------------------------------ scenes
S = {}

# home
S["home-crew"] = svg(room() + water(640, op=.35) + couch(70, 600, .9) + plant(1110, 600, 1) +
    air_mover(380, 720, 1) + dehu(890, 720, 1) + person(700, 735, 1, pose="reach") + moisture_meter(735, 365, .8))
S["home-laurel"] = svg(sky() + cloud(240, 120, 1) + cloud(700, 90, .8, op=.9) +
    f'<path d="M0 470 q300 -60 600 -10 t600 -20 v140 H0z" fill="#86B06C"/>' +
    house(60, 560, .8, "bungalow") + house(330, 560, .75, "colonial", body="#E7D3C1") + house(620, 560, .8, "cape", body="#DCE6EF") + tree(900, 560, 1.1) + house(960, 560, .55, "townrow") +
    f'<rect y="560" width="{W}" height="190" fill="#A3C585"/><path d="M0 640 q300 -40 600 0 t600 0 v110 H0z" fill="{WATER}" opacity=".75"/>' +
    f'<path d="M0 660 q300 -40 600 0 t600 0" stroke="#fff" stroke-width="4" fill="none" opacity=".5"/>' + pin(470, 420, 1.1))
S["home-process"] = svg(sky(h=600) + ground(520, road=False) + f'<rect y="600" width="{W}" height="150" fill="#6B7280"/>' +
    house(80, 520, .95, "colonial") + tree(520, 520, 1) + van(650, 700, 1.15) + person(560, 720, .7, pose="stand") + dehu(470, 715, .55))

# services
S["svc-emergency-water-removal"] = svg(room() + water(560, op=.6) + couch(60, 640, .8) +
    person(640, 740, 1, pose="reach") + f'<path d="M690 470 q40 130 -30 240" stroke="#111827" stroke-width="14" fill="none"/><rect x="620" y="690" width="90" height="16" rx="6" fill="#374151"/>' +
    f'<path d="M560 470 q-150 -40 -260 -160 q-40 -50 -120 -60" stroke="#111827" stroke-width="16" fill="none" opacity=".85"/>' + air_mover(900, 720, .9))
S["svc-water-mitigation-structural-drying"] = svg(room(window=False) +
    f'<rect x="90" y="140" width="420" height="356" fill="#D6DEE7"/>' + "".join(f'<rect x="{110 + i * 70}" y="140" width="22" height="356" fill="#C8A57E"/>' for i in range(6)) +
    f'<rect x="90" y="140" width="420" height="356" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="14 10"/>' +
    air_mover(140, 720, .9) + air_mover(560, 730, .9) + dehu(900, 720, 1) + moisture_meter(620, 260, 1) +
    "".join(f'<path d="M{600 + i * 40} 100 q14 -30 0 -60" stroke="{LBLUE}" stroke-width="6" fill="none" opacity=".6"/>' for i in range(4)))
S["svc-flooded-basement-cleanup"] = svg(f'<rect width="{W}" height="{H}" fill="#CBD2D9"/>' +
    "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#AEB7C1" stroke-width="4"/>' for y in range(60, 600, 60)) +
    "".join(f'<line x1="{x + (60 if (y // 60) % 2 else 0)}" y1="{y}" x2="{x + (60 if (y // 60) % 2 else 0)}" y2="{y + 60}" stroke="#AEB7C1" stroke-width="4"/>' for y in range(0, 600, 60) for x in range(0, W, 120)) +
    f'<rect x="830" y="60" width="240" height="90" fill="#fff"/><rect x="842" y="72" width="216" height="66" fill="{SKY}"/>' + rain(842, 1058, 60, 120, 14, 3, .9) +
    f'<polygon points="0,180 90,180 90,600 0,600" fill="#8B6B4F"/>' + "".join(f'<rect x="0" y="{200 + i * 50}" width="{90 + i * 18}" height="14" fill="#A37E5E"/>' for i in range(8)) +
    f'<rect y="560" width="{W}" height="190" fill="#9CA3AF"/>' + water(575, op=.6) +
    f'<rect x="420" y="380" width="90" height="190" rx="8" fill="#9CA3AF"/><rect x="440" y="410" width="50" height="80" rx="6" fill="{NAVY}"/><path d="M465 380 V120 H600" stroke="#1F2937" stroke-width="16" fill="none"/>' +
    dehu(980, 640, .8) + person(700, 735, .95, pose="stand") + f'<rect x="160" y="420" width="140" height="120" fill="#B98B5E"/><rect x="180" y="380" width="110" height="60" fill="#C99A6B"/>')
S["svc-burst-pipe-water-damage"] = svg(room(wall="#E4E9EF", window=False) +
    f'<rect x="0" y="180" width="{W}" height="34" fill="#B87333"/><rect x="0" y="186" width="{W}" height="8" fill="#fff" opacity=".25"/>' +
    f'<rect x="520" y="170" width="70" height="54" fill="#9A5B22"/>' +
    "".join(f'<path d="M555 214 q{dx} 80 {dx * 2} 260" stroke="{WATER}" stroke-width="{s}" fill="none" stroke-linecap="round" opacity=".75"/>' for dx, s in [(-120, 10), (-60, 14), (0, 16), (60, 14), (120, 10), (-160, 6), (160, 6)]) +
    "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{WATER}" opacity=".7"/>' for x, y in [(400, 300), (700, 280), (360, 380), (760, 360), (470, 260), (640, 250)]) +
    water(640, op=.5) + f'<rect x="90" y="300" width="160" height="220" fill="#94A3B8"/><circle cx="170" cy="380" r="50" fill="#E2E8F0"/><circle cx="170" cy="380" r="32" fill="{SKY}"/>' +
    person(960, 735, .95, pose="reach") + f'<rect x="1080" y="200" width="22" height="330" fill="#B87333"/><circle cx="1091" cy="470" r="30" fill="none" stroke="#DC2626" stroke-width="10"/><path d="M1061 470 h60 M1091 440 v60" stroke="#DC2626" stroke-width="7"/>')
S["svc-ceiling-drywall-water-damage"] = svg(f'<rect width="{W}" height="{H}" fill="#E9EEF3"/><rect width="{W}" height="200" fill="#F8FAFC"/><rect y="196" width="{W}" height="8" fill="#CBD5E1"/>' +
    f'<ellipse cx="560" cy="110" rx="260" ry="80" fill="#C9A86A" opacity=".45"/><ellipse cx="560" cy="110" rx="170" ry="52" fill="#B08C4F" opacity=".45"/><ellipse cx="560" cy="200" rx="110" ry="40" fill="#E2D4B7"/>' +
    drips(560, 250, 4, 55) + f'<rect y="600" width="{W}" height="150" fill="#C9A27A"/>' + bucket(560, 650, 1.3) +
    air_mover(120, 720, .9) +
    person(880, 745, .95, pose="reach") + moisture_meter(940, 300, .9))
S["svc-sewage-cleanup"] = svg(room(wall="#E5E7EB", floor="#9CA3AF", window=False) +
    water(600, color="#7C6A46", op=.55) + f'<circle cx="420" cy="640" r="40" fill="#4B5563"/><circle cx="420" cy="640" r="26" fill="#1F2937"/>' +
    "".join(f'<path d="M420 640 q{dx} -60 {dx * 1.4} -110" stroke="#7C6A46" stroke-width="10" fill="none" opacity=".7"/>' for dx in (-30, 0, 30)) +
    f'<polygon points="160,140 280,340 40,340" fill="#FACC15" stroke="#1F2937" stroke-width="8" stroke-linejoin="round"/>' +
    f'<g transform="translate(160 268)"><circle r="16" fill="none" stroke="#1F2937" stroke-width="8"/><circle cy="-26" r="16" fill="none" stroke="#1F2937" stroke-width="8"/><circle cx="-24" cy="14" r="16" fill="none" stroke="#1F2937" stroke-width="8"/><circle cx="24" cy="14" r="16" fill="none" stroke="#1F2937" stroke-width="8"/></g>' +
    person(760, 740, 1, suit="#F8FAFC", pose="reach", ppe=True) + scrubber(900, 720, .8))
S["svc-mold-remediation"] = svg(room(window=False) +
    "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#365314" opacity="{o}"/>' for x, y, r, o in [(200, 380, 40, .5), (250, 420, 26, .6), (160, 440, 30, .45), (230, 340, 18, .6), (300, 390, 14, .5), (180, 320, 12, .5), (280, 460, 20, .4), (130, 400, 16, .5)]) +
    f'<rect x="480" y="60" width="380" height="600" fill="{LBLUE}" opacity=".35" stroke="#7FB3E0" stroke-width="6"/>' +
    f'<path d="M670 90 V640" stroke="#475569" stroke-width="6" stroke-dasharray="6 6"/><rect x="660" y="80" width="20" height="22" rx="4" fill="#475569"/>' +
    person(610, 720, .9, suit="#F8FAFC", ppe=True, pose="stand") + scrubber(900, 720, .85))
S["svc-storm-flood-damage"] = svg(sky(bg="#64748B", sun=False, h=560) + cloud(250, 110, 1.4, c="#475569") + cloud(750, 90, 1.6, c="#334155") + cloud(1050, 130, 1.1, c="#475569") +
    f'<polygon points="840,140 800,260 840,260 810,360 890,220 850,220 880,140" fill="#FDE047"/>' + rain(0, W, 140, 560, 110, 7) +
    ground(520, c="#6B8F55", road=False) + house(250, 560, 1.1, "colonial", body="#E7D3C1") + tree(130, 560, 1.1, c="#3F6212") + tree(1000, 560, 1.2, c="#3F6212") +
    f'<path d="M0 600 q300 -30 600 0 t600 0 V{H} H0z" fill="#8D7A52" opacity=".75"/>' + rain(0, W, 560, 700, 40, 9, .5))
S["svc-fire-smoke-damage"] = svg(room(wall="#E5E7EB") +
    f'<defs><linearGradient id="soot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F2937" stop-opacity=".75"/><stop offset="1" stop-color="#1F2937" stop-opacity="0"/></linearGradient></defs>' +
    f'<rect width="{W}" height="330" fill="url(#soot)"/>' + f'<rect x="0" y="0" width="560" height="500" fill="#fff" opacity=".55"/><rect x="556" y="0" width="6" height="500" fill="{ORANGE}"/>' +
    couch(620, 640, .75, c="#57534E") + scrubber(110, 720, .9) + person(470, 735, .95, pose="reach", suit=NAVY) +
    f'<rect x="540" y="250" width="70" height="46" rx="8" fill="#FDE68A" stroke="#CA8A04" stroke-width="4" transform="rotate(-20 575 273)"/>')

# locations
S["loc-bowie-md"] = svg(sky() + cloud(300, 120) + ground() + house(60, 560, .9, "colonial") + house(420, 560, .85, "rambler", body="#DCE6EF") + house(820, 560, .8, "cape", body="#E7D3C1") + tree(760, 560, .9) + pin(560, 360))
S["loc-columbia-md"] = svg(sky() + cloud(860, 120, .9) + f'<rect y="430" width="{W}" height="320" fill="#A3C585"/>' + f'<ellipse cx="600" cy="660" rx="700" ry="110" fill="{WATER}" opacity=".7"/>' +
    house(80, 520, .75, "townrow") + house(560, 520, .8, "colonial", body="#DCE6EF") + tree(950, 520, 1.1) + pine(1120, 520, .9) + tree(40, 520, .8) +
    f'<path d="M0 560 q600 40 1200 0" stroke="#E5E7EB" stroke-width="16" fill="none"/>' + pin(700, 330))
S["loc-greenbelt-md"] = svg(sky() + cloud(250, 100) + ground() + tree(80, 560, 1.1) + house(170, 560, 1, "garden", body="#F1E7D6") + house(680, 560, .8, "garden", body="#E2E8F0") + tree(1120, 560, 1) + pin(450, 330))
S["loc-silver-spring-md"] = svg(sky() + house(720, 470, 1, "tower") + house(900, 470, .8, "tower") + house(560, 470, .7, "tower") + ground() + house(60, 560, .85, "bungalow") + house(380, 560, .8, "cape", body="#DCE6EF") + tree(700, 560, 1) + house(800, 560, .7, "bungalow", body="#E7D3C1") + pin(520, 330))
S["loc-beltsville-md"] = svg(sky() + f'<path d="M0 470 q300 -50 600 -20 t600 -10 v100 H0z" fill="#BFD69B"/>' + "".join(f'<path d="M{i * 90} 500 q300 -20 600 0" stroke="#A3BE7F" stroke-width="6" fill="none"/>' for i in range(-3, 10)) +
    ground() + house(80, 560, .85, "split") + house(520, 560, .85, "rambler", body="#E7D3C1") + tree(470, 560, .8) + tree(1060, 560, 1) + pin(700, 340))
S["loc-burtonsville-md"] = svg(sky() + cloud(500, 120, .9) + pine(60, 560, 1.1) + pine(1130, 560, 1.2) + ground() + house(140, 560, .85, "colonial", body="#DCE6EF") + house(560, 560, .85, "colonial", body="#F5EBDD", roof="#475569") + tree(980, 560, 1) + pin(470, 330))
S["loc-odenton-fort-meade-md"] = svg(sky() + ground() + house(60, 560, .9, "townrow") + house(560, 560, .9, "townrow", roof="#475569") +
    f'<rect y="710" width="{W}" height="40" fill="#78716C"/>' + "".join(f'<rect x="{i * 40}" y="716" width="18" height="30" fill="#57534E"/>' for i in range(31)) + f'<rect y="712" width="{W}" height="5" fill="#D6D3D1"/>' + pin(520, 300))
S["loc-maple-lawn-fulton-md"] = svg(sky() + cloud(900, 110) + ground() + house(40, 560, .85, "colonial", body="#EADBC8", roof="#334155") + house(400, 560, .7, "townrow", roof="#334155") + house(760, 560, .85, "colonial", body="#DCE6EF", roof="#334155") + tree(1150, 560, .8) + pin(620, 320))

ALT = {
    "home-crew": "Illustration of a technician checking moisture while an air mover and dehumidifier dry a wet living room",
    "home-laurel": "Illustration of older Laurel homes near the Patuxent River with a map pin",
    "home-process": "Illustration of a restoration van and technician arriving at a home with drying equipment",
    "svc-emergency-water-removal": "Illustration of a technician extracting standing water from a flooded living room",
    "svc-water-mitigation-structural-drying": "Illustration of an opened wall with air movers, a dehumidifier and a moisture meter drying the framing",
    "svc-flooded-basement-cleanup": "Illustration of a flooded basement with a sump pump, rain at the window and a technician",
    "svc-burst-pipe-water-damage": "Illustration of a burst copper pipe spraying water across a room and a technician closing the shutoff",
    "svc-ceiling-drywall-water-damage": "Illustration of a stained, sagging ceiling dripping into a bucket while a technician checks moisture",
    "svc-sewage-cleanup": "Illustration of a sewage backup from a floor drain with a biohazard sign and a technician in protective gear",
    "svc-mold-remediation": "Illustration of mold on a wall behind plastic containment with a HEPA air scrubber",
    "svc-storm-flood-damage": "Illustration of a house in a thunderstorm with heavy rain and flood water in the yard",
    "svc-fire-smoke-damage": "Illustration of a soot-stained room being cleaned, with a clean section of wall and an air scrubber",
}
LOCALT = {"bowie-md": "colonials, ramblers and Cape Cods", "columbia-md": "townhomes and houses near a lake path", "greenbelt-md": "garden-style row homes",
          "silver-spring-md": "older bungalows with downtown towers behind", "beltsville-md": "split-levels and ramblers near open fields",
          "burtonsville-md": "colonial homes among pine trees", "odenton-fort-meade-md": "townhome rows beside a rail line",
          "maple-lawn-fulton-md": "newer colonials and townhomes"}
NAMES = {"bowie-md": "Bowie", "columbia-md": "Columbia", "greenbelt-md": "Greenbelt", "silver-spring-md": "Silver Spring", "beltsville-md": "Beltsville",
         "burtonsville-md": "Burtonsville", "odenton-fort-meade-md": "Odenton and Fort Meade", "maple-lawn-fulton-md": "Maple Lawn and Fulton"}
for k, v in LOCALT.items():
    ALT["loc-" + k] = f"Illustration of {v} in {NAMES[k]}, MD, with a service map pin"

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, s in S.items():
        p = Path(f"/tmp/{name}.svg"); p.write_text(s); png = Path(f"/tmp/{name}.png")
        subprocess.run(["rsvg-convert", str(p), "-o", str(png)], check=True)
        subprocess.run(["convert", str(png), "-strip", "-quality", "80", "-define", "webp:method=6", str(OUT / f"{name}.webp")], check=True)
        subprocess.run(["convert", str(png), "-resize", "600x", "-strip", "-quality", "78", "-define", "webp:method=6", str(OUT / f"{name}-600.webp")], check=True)
        subprocess.run(["convert", str(png), "-strip", "-quality", "82", str(OUT / f"{name}.jpg")], check=True)
    print("scenes:", len(S))
