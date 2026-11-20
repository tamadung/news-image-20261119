#!/usr/bin/env python3
"""compose-v1.py — build the news-image-20261119 v1 front page (1024x1024).

Winner-template build (hazel #1 99.23% + izayoi #2 99.23% on 19 Nov):
cream paper, big serif date masthead, 14 core stories each with its own
flat-illustration panel (generated flat art, no AI text), a large world map
with numbered pins 1-14 tied to the core stories plus gold dots for the
also-on stories, and a numbered ALSO ON list for the rest. Extras from the
winners: a region bar (counts per region), a field bar (counts per field),
a THE DAY IN NUMBERS strip, verification tags (REPORTED/CLAIM/FORECAST)
on every panel, and a DATE CHECK box (stories deliberately left out because
they were first reported on 18 Nov or belong to 20 Nov).
All text is drawn with PIL (DejaVu Serif for headlines, DejaVu Sans for
body) — no AI-generated text anywhere. Deterministic: same inputs, same
bytes. 42 stories in all.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BASE = Path(__file__).resolve().parent
ILLU = BASE / "v1-illu"

PAPER = (247, 241, 222)
INK = (24, 30, 42)
RED = (200, 16, 46)
GOLD = (176, 141, 60)
GREY = (96, 94, 86)
PANEL = (255, 255, 255)
BORDER = (198, 192, 176)
MAP_BG = (255, 255, 255)
MAP_LAND = (232, 222, 196)
MAP_EDGE = (178, 168, 140)
TAG_REPORTED = (27, 94, 32)
TAG_CLAIM = (176, 106, 0)
TAG_FORECAST = (13, 71, 161)

REGIONS = {
    "EUROPE": (13, 71, 161),
    "MIDDLE EAST": (200, 16, 46),
    "ASIA": (27, 94, 32),
    "AFRICA": (106, 27, 154),
    "AMERICAS": (176, 106, 0),
    "OCEANIA": (0, 131, 143),
    "WORLD": (69, 90, 100),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)  # noqa: E731
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)  # noqa: E731
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)  # noqa: E731
F_SANS = lambda s: font("DejaVuSans.ttf", s)  # noqa: E731


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap_lines(d, text, f, max_w, max_lines):
    """Greedy wrap to max_lines; add an ellipsis only if words are cut off."""
    words = text.split()
    lines = []
    idx = 0
    while idx < len(words) and len(lines) < max_lines:
        cur = words[idx]
        idx += 1
        while idx < len(words):
            cand = cur + " " + words[idx]
            if text_w(d, cand, f) <= max_w:
                cur = cand
                idx += 1
            else:
                break
        lines.append(cur)
    if idx < len(words):  # some words did not fit: mark the last line
        last = lines[-1]
        while last and text_w(d, last + "\u2026", f) > max_w:
            last = last[:-1].rstrip()
        lines[-1] = last + "\u2026"
    return lines


def crop_to(im, tw, th, ybias=0.5):
    """Center-crop im to aspect tw/th (vertical bias ybias), then resize."""
    sw, sh = im.size
    ta, sa = tw / th, sw / sh
    if sa > ta:  # source wider: crop width, keep full height
        nw = int(sh * ta)
        x0 = (sw - nw) // 2
        box = (x0, 0, x0 + nw, sh)
    else:  # source narrower: crop height with vertical bias
        nh = int(sw / ta)
        y0 = int((sh - nh) * ybias)
        box = (0, y0, sw, y0 + nh)
    return im.crop(box).resize((tw, th), Image.LANCZOS)


# ---------------------------------------------------------------- stories
# (num, file, region, kicker, headline, deck, lon, lat, tag, ybias)
CORE = [
    (1, "01-summit", "ASIA", "SHENZHEN \u00b7 SUMMIT",
     "Trump, Xi and Putin hold first three-way summit",
     "The US, Chinese and Russian leaders met beside the APEC summit and issued a 'Declaration on Peace'.",
     114, 22, "REPORTED", 0.5),
    (2, "02-gtavi", "WORLD", "WORLDWIDE \u00b7 GAMES",
     "GTA VI goes on sale after 13 years",
     "The midnight launch draws rave reviews; New Zealand first.",
     174, -41, "REPORTED", 0.5),
    (3, "03-icj", "EUROPE", "THE HAGUE \u00b7 JUSTICE",
     "World Court: Myanmar committed genocide",
     "By 9 votes to 6 the ICJ found Myanmar guilty of genocide against the Rohingya.",
     4, 52, "REPORTED", 0.5),
    (4, "04-anthropic", "AMERICAS", "NEW YORK \u00b7 MARKETS",
     "Anthropic starts trading on Nasdaq",
     "Its record $81.3bn share sale was priced at $83.",
     -74, 41, "REPORTED", 0.5),
    (5, "05-crimea", "EUROPE", "CRIMEA \u00b7 WAR",
     "Ukraine hits Crimea bridge a third time",
     "Third strike in a week halts trains to Russia.",
     34, 45, "REPORTED", 0.62),
    (6, "06-cop31", "WORLD", "ANTALYA \u00b7 CLIMATE",
     "COP31 draft drops fossil fuels and $120bn aid goal",
     "The slimmer text has no figure for adaptation aid.",
     30, 37, "REPORTED", 0.5),
    (7, "07-akvan", "ASIA", "ODISHA \u00b7 STORM",
     "Cyclone Akvan nears India's coast",
     "Over 100,000 moved to shelters before Friday's landfall.",
     80, 16, "FORECAST", 0.5),
    (8, "08-riyadh", "MIDDLE EAST", "RIYADH \u00b7 WAR",
     "Saudis shoot down Houthi missiles",
     "Debris fell on the capital; no casualties reported.",
     47, 25, "REPORTED", 0.5),
    (9, "09-gaza-tank", "MIDDLE EAST", "GAZA \u00b7 WAR",
     "Israeli armour pushes into central Gaza",
     "Tanks move toward Salah al-Din Street.",
     34, 31, "CLAIM", 0.5),
    (10, "10-korea-exam", "ASIA", "SEOUL \u00b7 EDUCATION",
     "Half a million sit Korea's big exam",
     "551,864 take the Suneung; flights pause for 35 minutes.",
     127, 38, "REPORTED", 0.5),
    (11, "11-colombia", "AMERICAS", "BOGOT\u00c1 \u00b7 LABOUR",
     "Colombia's unions hold national strike",
     "Marches in three cities against an economic rescue bill.",
     -74, 5, "REPORTED", 0.5),
    (12, "12-australia", "OCEANIA", "CANBERRA \u00b7 ECONOMY",
     "Australia's jobless rate hits 4.9%",
     "Highest since 2024; shares and the dollar slide.",
     149, -35, "REPORTED", 0.5),
    (13, "13-greenland", "EUROPE", "GREENLAND \u00b7 SECURITY",
     "Denmark backs Arctic pact with US",
     "Parliament approves the Greenland security deal 109-0.",
     -42, 74, "REPORTED", 0.5),
    (14, "14-somalia", "AFRICA", "MOGADISHU \u00b7 DIPLOMACY",
     "Somalia expels UAE ambassador",
     "Mogadishu orders the envoy out in 72 hours.",
     45, 2, "REPORTED", 0.5),
]

# (num, region, headline, summary, lon, lat) — ALSO ON, 2 lines each.
ALSO = [
    (15, "AMERICAS", "US\u2013Venezuela military pact", "Hegseth signs deal in Caracas", -66, 7),
    (16, "MIDDLE EAST", "Eisenkot to form government", "Bypasses Netanyahu", 35, 32),
    (17, "WORLD", "Gaza aid call", "4 nations demand access", 35, 32),
    (18, "EUROPE", "Estonia to close Russia border", "Crossings shut from Dec", 24, 59),
    (19, "EUROPE", "Prague mass protest", "Media law draws crowds", 14, 50),
    (20, "AMERICAS", "US details $12bn Venezuela oil", "Maduro revenue report", -66, 7),
    (21, "EUROPE", "France protests: 4th weekend", "Cost-of-living marches", 2, 49),
    (22, "ASIA", "Indonesia passes asset-seizure law", "After an 18-year wait", 107, -6),
    (23, "EUROPE", "French left splits", "Over M\u00e9lenchon pact", 2, 49),
    (24, "AMERICAS", "Floods shut Florida schools", "15 inches of rain", -80, 26),
    (25, "AMERICAS", "Senate defeats Iran war vote", "51\u201348 keeps war powers", -77, 39),
    (26, "AMERICAS", "Elon Musk says he is 'not MAGA'", "Regrets big spending", -122, 37),
    (27, "EUROPE", "Ukraine allies meet in Berlin", "40 nations back Kyiv", 13, 52),
    (28, "EUROPE", "Serbia elects student speaker", "New parliament chief", 21, 44),
    (29, "EUROPE", "Dutch embassy hit in Kyiv", "Russian drone strike", 31, 50),
    (30, "ASIA", "Korea court orders Han retrial", "Ex-PM's conviction void", 127, 38),
    (31, "WORLD", "Bitcoin dips below $63,000", "Then recovers; ETF outflows", -74, 41),
    (32, "AMERICAS", "Carney wraps APEC with gains", "China deal to Dec 2028", -123, 49),
    (33, "MIDDLE EAST", "47 French nationals on trial", "IS charges in Iraq", 44, 33),
    (34, "MIDDLE EAST", "Yemen missile threat to Riyadh", "Coalition warns", 47, 25),
    (35, "EUROPE", "General strike in Spain", "Ports, factories hit", -4, 40),
    (36, "EUROPE", "Germany warns of hybrid threats", "Cyberattacks rising", 13, 52),
    (37, "EUROPE", "AI cyberattack hits EU body", "Commission systems down", 4, 51),
    (38, "ASIA", "India beats Pakistan 2\u20131", "SAFF Championship final", 90, 24),
    (39, "ASIA", "Delhi schools reopen", "Smog curbs lifted", 77, 28),
    (40, "ASIA", "US\u2013Philippines loan package", "Worth over $2bn", 121, 15),
    (41, "AMERICAS", "US sanctions Hezbollah links", "3 entities, 3 people", -77, 39),
    (42, "ASIA", "India\u2013Japan defence review", "Tokyo talks deepen ties", 140, 36),
]

# Region counts (all 42 stories) for the region bar.
REGION_COUNTS = [
    ("EUROPE", 13), ("MIDDLE EAST", 5), ("ASIA", 9), ("AFRICA", 1),
    ("AMERICAS", 9), ("OCEANIA", 1), ("WORLD", 4),
]
# Field counts (all 42 stories) for the field bar.
FIELD_COUNTS = [
    ("War & security", 9), ("Politics & diplomacy", 12),
    ("Economy & labour", 6), ("Society & culture", 7),
    ("Disasters & weather", 2), ("Climate & space", 1),
    ("Justice", 4), ("Tech", 1),
]

ILLU_FILES = {}
for _s in CORE:
    _key = _s[1]
    _cands = sorted((ILLU).glob(f"media-generation-{_key}-*.png"))
    if not _cands:
        _cands = sorted((ILLU).glob(f"{_key}.*"))
    assert _cands, f"illustration missing for {_key}"
    ILLU_FILES[_key] = _cands[0]

# ------------------------------------------------------------- world map
CONTINENTS = {
    "North America": [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
                      (-85, 66), (-80, 73), (-65, 60), (-55, 52), (-60, 47),
                      (-70, 44), (-75, 35), (-80, 32), (-81, 26), (-84, 30),
                      (-90, 21), (-97, 26), (-105, 20), (-105, 23), (-110, 24),
                      (-114, 29), (-117, 33), (-122, 37), (-124, 40), (-124, 48),
                      (-130, 55), (-140, 60), (-155, 58), (-165, 60), (-168, 66)],
    "South America": [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0),
                      (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-57, -38),
                      (-65, -41), (-68, -50), (-70, -54), (-73, -50), (-73, -37),
                      (-70, -30), (-70, -18), (-77, -12), (-81, -6), (-80, 1),
                      (-79, 9)],
    "Africa": [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (10, 37), (20, 32),
               (30, 31), (35, 28), (39, 21), (43, 12), (51, 11), (48, 0),
               (40, -10), (40, -20), (35, -28), (28, -33), (20, -35), (15, -27),
               (12, -18), (13, -10), (9, 4), (-8, 5), (-13, 8), (-17, 15)],
    "Europe": [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53),
               (8, 57), (10, 59), (5, 60), (12, 56), (18, 56), (21, 55),
               (24, 59), (28, 60), (30, 62), (30, 70), (40, 68), (45, 68),
               (50, 69), (55, 68), (60, 69), (68, 73), (75, 73), (80, 73),
               (70, 72), (60, 70), (55, 68), (50, 60), (45, 55), (40, 50),
               (40, 47), (35, 45), (30, 46), (28, 44), (23, 40), (20, 40),
               (15, 38), (10, 38), (5, 38), (0, 38), (-5, 36), (-10, 36)],
    "Asia": [(30, 70), (40, 68), (50, 69), (60, 69), (68, 73), (75, 73),
             (80, 73), (90, 75), (100, 77), (110, 74), (120, 73), (130, 72),
             (140, 72), (150, 70), (160, 70), (170, 67), (178, 65), (170, 60),
             (162, 56), (158, 52), (150, 59), (142, 55), (140, 45), (135, 43),
             (130, 42), (127, 40), (126, 38), (122, 39), (120, 32), (122, 28),
             (118, 25), (110, 20), (108, 12), (105, 9), (100, 7), (98, 10),
             (95, 16), (92, 21), (88, 22), (85, 19), (80, 15), (77, 8),
             (73, 16), (70, 20), (66, 25), (60, 25), (56, 27), (52, 28),
             (50, 30), (48, 30), (44, 29), (40, 30), (36, 36), (30, 36),
             (28, 41), (30, 46), (30, 55), (30, 60), (30, 70)],
    "Oceania": [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
                (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
                (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
                (142, -11), (137, -12), (135, -15), (132, -11), (130, -13),
                (126, -14), (122, -17), (118, -20), (113, -22)],
}

CONTINENT_LABELS = [
    ("NORTH AMERICA", -115, 55), ("SOUTH AMERICA", -60, -15),
    ("AFRICA", 8, 15), ("EUROPE", -15, 60), ("ASIA", 125, 62),
    ("OCEANIA", 134, -25),
]


def project(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 170) / 360 * w, y0 + (1 - (lat + 58) / 148) * h)


def collide(px, py, placed, min_d):
    for qx, qy in placed:
        if (px - qx) ** 2 + (py - qy) ** 2 < min_d ** 2:
            return True
    return False


def place_pin(px, py, placed, min_d, max_r=60):
    """Spiral search for a free spot near (px, py)."""
    if not collide(px, py, placed, min_d):
        return px, py
    for r in range(6, max_r, 4):
        for k in range(16):
            a = k / 16 * 2 * math.pi
            qx, qy = px + r * math.cos(a), py + r * math.sin(a)
            if not collide(qx, qy, placed, min_d):
                return qx, qy
    return px, py


TAG_COLORS = {"REPORTED": TAG_REPORTED, "CLAIM": TAG_CLAIM, "FORECAST": TAG_FORECAST}


def draw_tag(d, x, y, tag):
    """Small verification tag (top-right of a panel)."""
    f = F_SANS_B(8)
    tw = d.textlength(tag, font=f)
    w = int(tw) + 8
    d.rectangle([x - w, y, x, y + 12], fill=TAG_COLORS[tag])
    d.text((x - w + 4, y + 2), tag, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- panels
def draw_badge(d, cx, cy, num, r=10):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=1)
    f = F_SANS_B(11 if num < 10 else 10)
    tw = d.textlength(str(num), font=f)
    d.text((cx - tw / 2, cy - 8 if num < 10 else cy - 7), str(num), font=f, fill=(255, 255, 255))


def draw_panel_large(d, img, x, y, w, h, s):
    """Wide panel (top row): illustration on top, text below."""
    num, key, region, kicker, headline, deck, lon, lat, tag, yb = s
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=BORDER)
    im = Image.open(ILLU_FILES[key]).convert("RGB")
    img.paste(crop_to(im, w - 2, 96, yb), (x + 1, y + 1))
    draw_badge(d, x + 13, y + 13, num)
    draw_tag(d, x + w - 1, y + 1, tag)
    tx = x + 8
    d.text((tx, y + 102), kicker, font=F_SANS_B(10), fill=REGIONS[region])
    hl = wrap_lines(d, headline, F_SERIF_B(16), w - 16, 2)
    yy = y + 118
    for ln in hl:
        d.text((tx, yy), ln, font=F_SERIF_B(16), fill=INK)
        yy += 19
    dk = wrap_lines(d, deck, F_SANS(11), w - 16, 2)
    yy += 1
    for ln in dk:
        d.text((tx, yy), ln, font=F_SANS(11), fill=(58, 58, 58))
        yy += 13


def draw_panel_small(d, img, x, y, w, h, s, hl_size=13, deck_size=10):
    """Single-width panel: illustration on top, text below."""
    num, key, region, kicker, headline, deck, lon, lat, tag, yb = s
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=BORDER)
    im = Image.open(ILLU_FILES[key]).convert("RGB")
    img.paste(crop_to(im, w - 2, 72, yb), (x + 1, y + 1))
    draw_badge(d, x + 12, y + 12, num)
    draw_tag(d, x + w - 1, y + 1, tag)
    tx = x + 6
    d.text((tx, y + 78), kicker, font=F_SANS_B(9), fill=REGIONS[region])
    hl = wrap_lines(d, headline, F_SERIF_B(hl_size), w - 12, 2)
    yy = y + 92
    for ln in hl:
        d.text((tx, yy), ln, font=F_SERIF_B(hl_size), fill=INK)
        yy += hl_size + 3
    dk = wrap_lines(d, deck, F_SANS(deck_size), w - 12, 2)
    for ln in dk:
        d.text((tx, yy), ln, font=F_SANS(deck_size), fill=(58, 58, 58))
        yy += deck_size + 1


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top line ---
    d.text((16, 4), "THE WORLD IN ONE DAY", font=F_SANS_B(11), fill=INK)
    t = "42 STORIES \u00b7 7 REGIONS \u00b7 8 FIELDS \u00b7 14 ILLUSTRATED \u00b7 ALL FROM THURSDAY"
    d.text((1008, 4), t, font=F_SANS_B(11), fill=RED, anchor="ra")

    # --- masthead: big serif date ---
    d.text((512, 18), "Thursday 19 November 2026", font=F_SERIF_B(44),
           fill=INK, anchor="ma")
    d.line([(16, 72), (1008, 72)], fill=RED, width=2)
    d.line([(16, 76), (1008, 76)], fill=INK, width=1)

    # --- sub-headline ---
    sub = ("Trump, Xi and Putin share one table \u00b7 The World Court finds genocide in Myanmar "
           "\u00b7 A 13-year wait for a game ends")
    f = F_SERIF(13)
    tw = d.textlength(sub, font=f)
    d.text(((1024 - tw) / 2, 79), sub, font=f, fill=RED)

    # --- region bar (counts per region, proportional widths) ---
    ry0, ry1 = 96, 112
    total = sum(c for _n, c in REGION_COUNTS)
    x = 16
    for name, count in REGION_COUNTS:
        seg_w = int(992 * count / total)
        d.rectangle([x, ry0, x + seg_w, ry1], fill=REGIONS[name])
        label = f"{name} {count}"
        f = F_SANS_B(10)
        tw = d.textlength(label, font=f)
        if tw + 8 <= seg_w:
            d.text((x + (seg_w - tw) / 2, ry0 + 3), label, font=f,
                   fill=(255, 255, 255))
        x += seg_w

    # --- the day in numbers ---
    ny = 116
    nums = ("THE DAY IN NUMBERS:  3 presidents  \u00b7  9\u20136 genocide vote  \u00b7  "
            "$81.3bn record IPO  \u00b7  109\u20130 Arctic vote  \u00b7  "
            "551,864 exam sitters  \u00b7  4.9% jobless")
    f = F_SANS_B(10)
    tw = d.textlength(nums, font=f)
    d.text(((1024 - tw) / 2, ny), nums, font=f, fill=INK)

    # --- story grid: row 1 = 3 large, row 2 = 5 small, row 3 = 6 small ---
    # row 1: y 132-314 (182 tall), 3 x 330 wide
    row1_y, row1_h = 132, 182
    cols1 = [16, 347, 678]
    for i in range(3):
        draw_panel_large(d, img, cols1[i], row1_y, 330, row1_h, CORE[i])
    # row 2: y 318-464 (146 tall), 5 x 196 wide
    cols5 = [16, 215, 414, 613, 812]
    pw5 = 196
    for i in range(5):
        draw_panel_small(d, img, cols5[i], 318, pw5, 146, CORE[3 + i])
    # row 3: y 468-614 (146 tall), 6 x 162 wide
    cols6 = [16, 182, 348, 514, 680, 846]
    pw6 = 162
    for i in range(6):
        draw_panel_small(d, img, cols6[i], 468, pw6, 146, CORE[8 + i],
                         hl_size=12, deck_size=9)

    # --- bottom band: map (left) + ALSO ON (right) ---
    # Map box
    mx0, my0, mx1, my1 = 16, 618, 424, 1008
    d.rectangle([mx0, my0, mx1, my1], fill=MAP_BG, outline=BORDER)
    d.text((mx0 + 10, my0 + 7), "WHERE IT HAPPENED", font=F_SANS_B(12), fill=INK)
    d.text((mx1 - 10, my0 + 8), "14 numbered stories",
           font=F_SANS(10), fill=GREY, anchor="ra")
    map_x0, map_y0, map_w, map_h = mx0 + 8, my0 + 28, mx1 - mx0 - 16, 300
    for name, pts in CONTINENTS.items():
        xy = [project(lon, lat, map_x0, map_y0, map_w, map_h) for lon, lat in pts]
        d.polygon(xy, fill=MAP_LAND, outline=MAP_EDGE)
    for label, lon, lat in CONTINENT_LABELS:
        lx, ly = project(lon, lat, map_x0, map_y0, map_w, map_h)
        f = F_SANS_B(8)
        d.text((lx - d.textlength(label, font=f) / 2, ly - 4), label,
               font=f, fill=(120, 114, 96))
    # pins: numbered 1-14 first, then gold dots for ALSO ON
    placed = []
    for s in CORE:
        num, _k, _r, _ki, _h, _de, lon, lat, _t, _y = s
        px, py = project(lon, lat, map_x0, map_y0, map_w, map_h)
        px, py = place_pin(px, py, placed, 21)
        placed.append((px, py))
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = F_SANS_B(9)
        tw = d.textlength(str(num), font=f)
        d.text((px - tw / 2, py - 6), str(num), font=f, fill=(255, 255, 255))
    for _n, _r, _h, _s, lon, lat in ALSO:
        px, py = project(lon, lat, map_x0, map_y0, map_w, map_h)
        px, py = place_pin(px, py, placed, 12)
        placed.append((px, py))
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GOLD,
                  outline=(255, 255, 255), width=1)
    # legend + sources
    ly = my1 - 34
    lx = mx0 + 10
    for name in ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]:
        d.rectangle([lx, ly + 2, lx + 8, ly + 10], fill=REGIONS[name])
        lx += 11
        f = F_SANS_B(8)
        d.text((lx, ly), name, font=f, fill=GREY)
        lx += int(d.textlength(name, font=f)) + 8
    d.text((mx0 + 10, my1 - 18),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 UN News \u2014 19 Nov 2026. All drawings original.",
           font=F_SANS(9), fill=GREY)

    # ALSO ON — 3 columns, 2-line wrapped items
    ax0, ax1 = 432, 1008
    d.text((ax0, 624), "ALSO ON THURSDAY 19 NOVEMBER", font=F_SANS_B(14), fill=RED)
    d.line([(ax0, 642), (ax1, 642)], fill=RED, width=1)
    col_x = [432, 624, 816]
    col_w = [184, 184, 192]
    col_items = [ALSO[0:10], ALSO[10:19], ALSO[19:28]]
    for ci in range(3):
        yy = 650
        for num, region, headline, summary, _lon, _lat in col_items[ci]:
            f_num = F_SANS_B(9)
            d.text((col_x[ci], yy), f"{num}.", font=f_num, fill=REGIONS[region])
            num_w = d.textlength(f"{num}.", font=f_num) + 4
            avail = col_w[ci] - num_w
            text = headline + " \u2014 " + summary
            lines = wrap_lines(d, text, F_SANS_B(9), avail, 2)
            x = col_x[ci] + num_w
            f_head = F_SANS_B(9)
            f_body = F_SANS(9)
            for li, ln in enumerate(lines):
                if li == 0 and ln.startswith(headline):
                    d.text((x, yy), headline, font=f_head, fill=INK)
                    hw = d.textlength(headline, font=f_head)
                    rest = ln[len(headline):]
                    if rest:
                        d.text((x + hw, yy), rest, font=f_body, fill=(58, 58, 58))
                else:
                    d.text((x, yy), ln, font=f_body, fill=(58, 58, 58))
                yy += 11
            yy += 1  # gap between items

    # DATE CHECK box (bottom of ALSO ON area)
    dx0, dy0, dx1, dy1 = 432, 880, 1008, 1008
    d.rectangle([dx0, dy0, dx1, dy1], outline=RED, width=1)
    d.text((dx0 + 8, dy0 + 6), "DATE CHECK", font=F_SANS_B(10), fill=RED)
    check = ("Left out on purpose because they were first reported on 18 Nov, "
             "not today: Jeffries named for US speaker, the EU's \u20ac45bn Ukraine "
             "loan plan, Iran firing on Kuwait and Bahrain, Nvidia's results, "
             "Australia's settler sanctions, Voyager 1 one light-day out. "
             "20 Nov: COP31's scheduled close, Cyclone Akvan's landfall. "
             "Tags: REPORTED = confirmed; CLAIM = one side says so; FORECAST = draft or schedule.")
    lines = wrap_lines(d, check, F_SANS(10), dx1 - dx0 - 16, 5)
    yy = dy0 + 22
    for ln in lines:
        d.text((dx0 + 8, yy), ln, font=F_SANS(10), fill=(58, 58, 58))
        yy += 13

    return img


def main():
    img = build()
    out = BASE / "entry-v1.png"
    img.save(out, format="PNG", optimize=True)
    size = out.stat().st_size
    print(f"entry-v1.png: {img.size}, {size} bytes")
    if size > 1_048_576:
        out_jpg = BASE / "entry-v1.jpg"
        img.save(out_jpg, format="JPEG", quality=90)
        print(f"PNG too big; JPEG fallback: {out_jpg.stat().st_size} bytes")


if __name__ == "__main__":
    main()
