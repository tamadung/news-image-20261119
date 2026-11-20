#!/usr/bin/env python3
"""Build the Thursday 19 November 2026 front page (1024 x 1024).

One image that sums up the day: a cream newspaper front page with a big
serif date masthead, fourteen core stories each carrying its own flat
illustration, a region bar and a numbers strip, a large world map with
numbered pins for the core stories and gold dots for the rest, a three
column ALSO ON list, and a DATE CHECK box that names the stories left out
on purpose because they belong to 18 or 20 November. Every panel carries
a verification tag: REPORTED (confirmed), CLAIM (one side says so) or
FORECAST (a draft or a schedule). All lettering is drawn with PIL using
DejaVu; no text comes from the pictures themselves. The output is
deterministic: the same inputs always give the same bytes.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ canvas
PAGE_W, PAGE_H = 1024, 1024
HERE = Path(__file__).resolve().parent
WORK_DIR = Path.home() / "workspace" / "makefun" / "news-image-20261119-work"

# ------------------------------------------------------------------ palette
PAPER = (247, 241, 222)
INK = (24, 30, 42)
RED = (200, 16, 46)
GOLD = (176, 141, 60)
GREY = (96, 94, 86)
BODY = (58, 58, 58)
CARD = (255, 255, 255)
CARD_EDGE = (198, 192, 176)
SEA = (255, 255, 255)
LAND = (232, 222, 196)
COAST = (178, 168, 140)
MAP_TEXT = (120, 114, 96)

VERIFY = {
    "REPORTED": (27, 94, 32),
    "CLAIM": (176, 106, 0),
    "FORECAST": (13, 71, 161),
}

REGION = {
    "EUROPE": (13, 71, 161),
    "MIDDLE EAST": (200, 16, 46),
    "ASIA": (27, 94, 32),
    "AFRICA": (106, 27, 154),
    "AMERICAS": (176, 106, 0),
    "OCEANIA": (0, 131, 143),
    "WORLD": (69, 90, 100),
}

DEJAVU = "/usr/share/fonts/truetype/dejavu"


def _face(filename, size):
    return ImageFont.truetype(f"{DEJAVU}/{filename}", size)


class Type:
    """Font shortcuts, so call sites stay short."""

    @staticmethod
    def serif_b(n):
        return _face("DejaVuSerif-Bold.ttf", n)

    @staticmethod
    def serif(n):
        return _face("DejaVuSerif.ttf", n)

    @staticmethod
    def sans_b(n):
        return _face("DejaVuSans-Bold.ttf", n)

    @staticmethod
    def sans(n):
        return _face("DejaVuSans.ttf", n)


# ------------------------------------------------------------------ helpers
def measure(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, width, limit):
    """Greedy word wrap to at most `limit` lines; ellipsis if words remain."""
    words = text.split()
    lines = []
    current = ""
    pos = 0
    while pos < len(words) and len(lines) < limit:
        word = words[pos]
        trial = (current + " " + word).strip()
        if measure(draw, trial, font) <= width:
            current = trial
            pos += 1
        elif current:
            lines.append(current)
            current = ""
        else:
            # A single word wider than the column: keep it whole on its own line.
            lines.append(word)
            pos += 1
    if current and len(lines) < limit:
        lines.append(current)
    if pos < len(words) and lines:
        last = lines[-1]
        while last and measure(draw, last + "\u2026", font) > width:
            last = last[:-1].rstrip()
        lines[-1] = last + "\u2026"
    return lines


def fit_cover(source, target_w, target_h, focus=0.5):
    """Crop `source` to the target aspect (vertical `focus`) and resize."""
    sw, sh = source.size
    target_ratio = target_w / target_h
    source_ratio = sw / sh
    if source_ratio > target_ratio:
        new_w = int(sh * target_ratio)
        left = (sw - new_w) // 2
        window = (left, 0, left + new_w, sh)
    else:
        new_h = int(sw / target_ratio)
        top = int((sh - new_h) * focus)
        window = (0, top, sw, top + new_h)
    return source.crop(window).resize((target_w, target_h), Image.LANCZOS)


def find_illustration(folder, key):
    """First generated panel for `key`, else a same-named fallback file."""
    generated = sorted(folder.glob(f"media-generation-{key}-*.png"))
    if generated:
        return generated[0]
    fallback = sorted(folder.glob(f"{key}.*"))
    assert fallback, f"no illustration for {key}"
    return fallback[0]


def illustration_dir():
    for candidate in (HERE / "v1-illu", WORK_DIR / "v1-illu"):
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("v1-illu folder not found next to compose.py or in the work dir")


# ------------------------------------------------------------------ stories
# Each core story: number, art key, region, kicker, headline, deck,
# map longitude/latitude, verification tag, illustration vertical focus.
CORE = [
    {"n": 1, "art": "01-summit", "region": "ASIA", "kicker": "SHENZHEN \u00b7 SUMMIT",
     "head": "Trump, Xi and Putin hold first three-way summit",
     "deck": "The US, Chinese and Russian leaders met beside the APEC summit and issued a 'Declaration on Peace'.",
     "lon": 114, "lat": 22, "tag": "REPORTED", "focus": 0.5},
    {"n": 2, "art": "02-gtavi", "region": "WORLD", "kicker": "WORLDWIDE \u00b7 GAMES",
     "head": "GTA VI goes on sale after 13 years",
     "deck": "The midnight launch draws rave reviews; New Zealand first.",
     "lon": 174, "lat": -41, "tag": "REPORTED", "focus": 0.5},
    {"n": 3, "art": "03-icj", "region": "EUROPE", "kicker": "THE HAGUE \u00b7 JUSTICE",
     "head": "World Court: Myanmar committed genocide",
     "deck": "By 9 votes to 6 the ICJ found Myanmar guilty of genocide against the Rohingya.",
     "lon": 4, "lat": 52, "tag": "REPORTED", "focus": 0.5},
    {"n": 4, "art": "04-anthropic", "region": "AMERICAS", "kicker": "NEW YORK \u00b7 MARKETS",
     "head": "Anthropic starts trading on Nasdaq",
     "deck": "Its record $81.3bn share sale was priced at $83.",
     "lon": -74, "lat": 41, "tag": "REPORTED", "focus": 0.5},
    {"n": 5, "art": "05-crimea", "region": "EUROPE", "kicker": "CRIMEA \u00b7 WAR",
     "head": "Ukraine hits Crimea bridge a third time",
     "deck": "Third strike in a week halts trains to Russia.",
     "lon": 34, "lat": 45, "tag": "REPORTED", "focus": 0.62},
    {"n": 6, "art": "06-cop31", "region": "WORLD", "kicker": "ANTALYA \u00b7 CLIMATE",
     "head": "COP31 draft drops fossil fuels and $120bn aid goal",
     "deck": "The slimmer text has no figure for adaptation aid.",
     "lon": 30, "lat": 37, "tag": "REPORTED", "focus": 0.5},
    {"n": 7, "art": "07-akvan", "region": "ASIA", "kicker": "ODISHA \u00b7 STORM",
     "head": "Cyclone Akvan nears India's coast",
     "deck": "Over 100,000 moved to shelters before Friday's landfall.",
     "lon": 80, "lat": 16, "tag": "FORECAST", "focus": 0.5},
    {"n": 8, "art": "08-riyadh", "region": "MIDDLE EAST", "kicker": "RIYADH \u00b7 WAR",
     "head": "Saudis shoot down Houthi missiles",
     "deck": "Debris fell on the capital; no casualties reported.",
     "lon": 47, "lat": 25, "tag": "REPORTED", "focus": 0.5},
    {"n": 9, "art": "09-gaza-tank", "region": "MIDDLE EAST", "kicker": "GAZA \u00b7 WAR",
     "head": "Israeli armour pushes into central Gaza",
     "deck": "Tanks move toward Salah al-Din Street.",
     "lon": 34, "lat": 31, "tag": "CLAIM", "focus": 0.5},
    {"n": 10, "art": "10-korea-exam", "region": "ASIA", "kicker": "SEOUL \u00b7 EDUCATION",
     "head": "Half a million sit Korea's big exam",
     "deck": "551,864 take the Suneung; flights pause for 35 minutes.",
     "lon": 127, "lat": 38, "tag": "REPORTED", "focus": 0.5},
    {"n": 11, "art": "11-colombia", "region": "AMERICAS", "kicker": "BOGOT\u00c1 \u00b7 LABOUR",
     "head": "Colombia's unions hold national strike",
     "deck": "Marches in three cities against an economic rescue bill.",
     "lon": -74, "lat": 5, "tag": "REPORTED", "focus": 0.5},
    {"n": 12, "art": "12-australia", "region": "OCEANIA", "kicker": "CANBERRA \u00b7 ECONOMY",
     "head": "Australia's jobless rate hits 4.9%",
     "deck": "Highest since 2024; shares and the dollar slide.",
     "lon": 149, "lat": -35, "tag": "REPORTED", "focus": 0.5},
    {"n": 13, "art": "13-greenland", "region": "EUROPE", "kicker": "GREENLAND \u00b7 SECURITY",
     "head": "Denmark backs Arctic pact with US",
     "deck": "Parliament approves the Greenland security deal 109-0.",
     "lon": -42, "lat": 74, "tag": "REPORTED", "focus": 0.5},
    {"n": 14, "art": "14-somalia", "region": "AFRICA", "kicker": "MOGADISHU \u00b7 DIPLOMACY",
     "head": "Somalia expels UAE ambassador",
     "deck": "Mogadishu orders the envoy out in 72 hours.",
     "lon": 45, "lat": 2, "tag": "REPORTED", "focus": 0.5},
]

# ALSO ON items: number, region, headline, one-line summary, lon, lat.
ALSO = [
    {"n": 15, "region": "AMERICAS", "head": "US\u2013Venezuela military pact", "sum": "Hegseth signs deal in Caracas", "lon": -66, "lat": 7},
    {"n": 16, "region": "MIDDLE EAST", "head": "Eisenkot to form government", "sum": "Bypasses Netanyahu", "lon": 35, "lat": 32},
    {"n": 17, "region": "WORLD", "head": "Gaza aid call", "sum": "4 nations demand access", "lon": 35, "lat": 32},
    {"n": 18, "region": "EUROPE", "head": "Estonia to close Russia border", "sum": "Crossings shut from Dec", "lon": 24, "lat": 59},
    {"n": 19, "region": "EUROPE", "head": "Prague mass protest", "sum": "Media law draws crowds", "lon": 14, "lat": 50},
    {"n": 20, "region": "AMERICAS", "head": "US details $12bn Venezuela oil", "sum": "Maduro revenue report", "lon": -66, "lat": 7},
    {"n": 21, "region": "EUROPE", "head": "France protests: 4th weekend", "sum": "Cost-of-living marches", "lon": 2, "lat": 49},
    {"n": 22, "region": "ASIA", "head": "Indonesia passes asset-seizure law", "sum": "After an 18-year wait", "lon": 107, "lat": -6},
    {"n": 23, "region": "EUROPE", "head": "French left splits", "sum": "Over M\u00e9lenchon pact", "lon": 2, "lat": 49},
    {"n": 24, "region": "AMERICAS", "head": "Floods shut Florida schools", "sum": "15 inches of rain", "lon": -80, "lat": 26},
    {"n": 25, "region": "AMERICAS", "head": "Senate defeats Iran war vote", "sum": "51\u201348 keeps war powers", "lon": -77, "lat": 39},
    {"n": 26, "region": "AMERICAS", "head": "Elon Musk says he is 'not MAGA'", "sum": "Regrets big spending", "lon": -122, "lat": 37},
    {"n": 27, "region": "EUROPE", "head": "Ukraine allies meet in Berlin", "sum": "40 nations back Kyiv", "lon": 13, "lat": 52},
    {"n": 28, "region": "EUROPE", "head": "Serbia elects student speaker", "sum": "New parliament chief", "lon": 21, "lat": 44},
    {"n": 29, "region": "EUROPE", "head": "Dutch embassy hit in Kyiv", "sum": "Russian drone strike", "lon": 31, "lat": 50},
    {"n": 30, "region": "ASIA", "head": "Korea court orders Han retrial", "sum": "Ex-PM's conviction void", "lon": 127, "lat": 38},
    {"n": 31, "region": "WORLD", "head": "Bitcoin dips below $63,000", "sum": "Then recovers; ETF outflows", "lon": -74, "lat": 41},
    {"n": 32, "region": "AMERICAS", "head": "Carney wraps APEC with gains", "sum": "China deal to Dec 2028", "lon": -123, "lat": 49},
    {"n": 33, "region": "MIDDLE EAST", "head": "47 French nationals on trial", "sum": "IS charges in Iraq", "lon": 44, "lat": 33},
    {"n": 34, "region": "MIDDLE EAST", "head": "Yemen missile threat to Riyadh", "sum": "Coalition warns", "lon": 47, "lat": 25},
    {"n": 35, "region": "EUROPE", "head": "General strike in Spain", "sum": "Ports, factories hit", "lon": -4, "lat": 40},
    {"n": 36, "region": "EUROPE", "head": "Germany warns of hybrid threats", "sum": "Cyberattacks rising", "lon": 13, "lat": 52},
    {"n": 37, "region": "EUROPE", "head": "AI cyberattack hits EU body", "sum": "Commission systems down", "lon": 4, "lat": 51},
    {"n": 38, "region": "ASIA", "head": "India beats Pakistan 2\u20131", "sum": "SAFF Championship final", "lon": 90, "lat": 24},
    {"n": 39, "region": "ASIA", "head": "Delhi schools reopen", "sum": "Smog curbs lifted", "lon": 77, "lat": 28},
    {"n": 40, "region": "ASIA", "head": "US\u2013Philippines loan package", "sum": "Worth over $2bn", "lon": 121, "lat": 15},
    {"n": 41, "region": "AMERICAS", "head": "US sanctions Hezbollah links", "sum": "3 entities, 3 people", "lon": -77, "lat": 39},
    {"n": 42, "region": "ASIA", "head": "India\u2013Japan defence review", "sum": "Tokyo talks deepen ties", "lon": 140, "lat": 36},
]

# Story counts for the two bars (all 42 stories).
REGION_TALLY = [
    ("EUROPE", 13), ("MIDDLE EAST", 5), ("ASIA", 9), ("AFRICA", 1),
    ("AMERICAS", 9), ("OCEANIA", 1), ("WORLD", 4),
]
FIELD_TALLY = [
    ("War & security", 9), ("Politics & diplomacy", 12),
    ("Economy & labour", 6), ("Society & culture", 7),
    ("Disasters & weather", 2), ("Climate & space", 1),
    ("Justice", 4), ("Tech", 1),
]

# ------------------------------------------------------------------ map data
# Rough continent outlines as (lon, lat) chains, drawn with a flat
# equirectangular projection. Good enough for a thumbnail-size locator map.
CONTINENTS = [
    ("North America", [
        (-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
        (-85, 66), (-80, 73), (-65, 60), (-55, 52), (-60, 47),
        (-70, 44), (-75, 35), (-80, 32), (-81, 26), (-84, 30),
        (-90, 21), (-97, 26), (-105, 20), (-105, 23), (-110, 24),
        (-114, 29), (-117, 33), (-122, 37), (-124, 40), (-124, 48),
        (-130, 55), (-140, 60), (-155, 58), (-165, 60), (-168, 66),
    ]),
    ("South America", [
        (-79, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0),
        (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-57, -38),
        (-65, -41), (-68, -50), (-70, -54), (-73, -50), (-73, -37),
        (-70, -30), (-70, -18), (-77, -12), (-81, -6), (-80, 1),
        (-79, 9),
    ]),
    ("Africa", [
        (-17, 15), (-17, 21), (-10, 31), (-5, 35), (10, 37), (20, 32),
        (30, 31), (35, 28), (39, 21), (43, 12), (51, 11), (48, 0),
        (40, -10), (40, -20), (35, -28), (28, -33), (20, -35), (15, -27),
        (12, -18), (13, -10), (9, 4), (-8, 5), (-13, 8), (-17, 15),
    ]),
    ("Europe", [
        (-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53),
        (8, 57), (10, 59), (5, 60), (12, 56), (18, 56), (21, 55),
        (24, 59), (28, 60), (30, 62), (30, 70), (40, 68), (45, 68),
        (50, 69), (55, 68), (60, 69), (68, 73), (75, 73), (80, 73),
        (70, 72), (60, 70), (55, 68), (50, 60), (45, 55), (40, 50),
        (40, 47), (35, 45), (30, 46), (28, 44), (23, 40), (20, 40),
        (15, 38), (10, 38), (5, 38), (0, 38), (-5, 36), (-10, 36),
    ]),
    ("Asia", [
        (30, 70), (40, 68), (50, 69), (60, 69), (68, 73), (75, 73),
        (80, 73), (90, 75), (100, 77), (110, 74), (120, 73), (130, 72),
        (140, 72), (150, 70), (160, 70), (170, 67), (178, 65), (170, 60),
        (162, 56), (158, 52), (150, 59), (142, 55), (140, 45), (135, 43),
        (130, 42), (127, 40), (126, 38), (122, 39), (120, 32), (122, 28),
        (118, 25), (110, 20), (108, 12), (105, 9), (100, 7), (98, 10),
        (95, 16), (92, 21), (88, 22), (85, 19), (80, 15), (77, 8),
        (73, 16), (70, 20), (66, 25), (60, 25), (56, 27), (52, 28),
        (50, 30), (48, 30), (44, 29), (40, 30), (36, 36), (30, 36),
        (28, 41), (30, 46), (30, 55), (30, 60), (30, 70),
    ]),
    ("Oceania", [
        (113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
        (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
        (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
        (142, -11), (137, -12), (135, -15), (132, -11), (130, -13),
        (126, -14), (122, -17), (118, -20), (113, -22),
    ]),
]

CONTINENT_NAMES = [
    ("NORTH AMERICA", -115, 55), ("SOUTH AMERICA", -60, -15),
    ("AFRICA", 8, 15), ("EUROPE", -15, 60), ("ASIA", 125, 62),
    ("OCEANIA", 134, -25),
]


def lonlat_to_xy(lon, lat, ox, oy, width, height):
    """Equirectangular projection into the map rectangle."""
    px = ox + (lon + 170) / 360 * width
    py = oy + (1 - (lat + 58) / 148) * height
    return px, py


def too_close(px, py, placed, gap):
    for qx, qy in placed:
        if (px - qx) ** 2 + (py - qy) ** 2 < gap * gap:
            return True
    return False


def nudge_pin(px, py, placed, gap, limit=60):
    """Spiral out from (px, py) until a spot `gap` away from other pins."""
    if not too_close(px, py, placed, gap):
        return px, py
    radius = 6
    while radius < limit:
        for step in range(16):
            angle = step / 16 * 2 * math.pi
            qx = px + radius * math.cos(angle)
            qy = py + radius * math.sin(angle)
            if not too_close(qx, qy, placed, gap):
                return qx, qy
        radius += 4
    return px, py


# ------------------------------------------------------------------ pieces
class FrontPage:
    """Owns the canvas and draws every section of the front page."""

    def __init__(self):
        self.img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.illu_dir = illustration_dir()
        self.panels = {s["art"]: find_illustration(self.illu_dir, s["art"]) for s in CORE}

    # -- small decorations -------------------------------------------------
    def number_badge(self, cx, cy, num, radius=10):
        self.d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                       fill=RED, outline=(255, 255, 255), width=1)
        f = Type.sans_b(11 if num < 10 else 10)
        tw = measure(self.d, str(num), f)
        top = cy - 8 if num < 10 else cy - 7
        self.d.text((cx - tw / 2, top), str(num), font=f, fill=(255, 255, 255))

    def verify_tag(self, right, top, tag):
        f = Type.sans_b(8)
        tw = measure(self.d, tag, f)
        w = int(tw) + 8
        self.d.rectangle([right - w, top, right, top + 12], fill=VERIFY[tag])
        self.d.text((right - w + 4, top + 2), tag, font=f, fill=(255, 255, 255))

    # -- story panels ------------------------------------------------------
    def panel_wide(self, x, y, w, h, story):
        """Top-row panel: tall picture, then kicker, headline, deck."""
        d = self.d
        d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_EDGE)
        art = Image.open(self.panels[story["art"]]).convert("RGB")
        self.img.paste(fit_cover(art, w - 2, 96, story["focus"]), (x + 1, y + 1))
        self.number_badge(x + 13, y + 13, story["n"])
        self.verify_tag(x + w - 1, y + 1, story["tag"])
        tx = x + 8
        d.text((tx, y + 102), story["kicker"], font=Type.sans_b(10),
               fill=REGION[story["region"]])
        yy = y + 118
        for line in wrap(d, story["head"], Type.serif_b(16), w - 16, 2):
            d.text((tx, yy), line, font=Type.serif_b(16), fill=INK)
            yy += 19
        yy += 1
        for line in wrap(d, story["deck"], Type.sans(11), w - 16, 2):
            d.text((tx, yy), line, font=Type.sans(11), fill=BODY)
            yy += 13

    def panel_narrow(self, x, y, w, h, story, head_size=13, deck_size=10):
        """Single-width panel: shorter picture, tighter type."""
        d = self.d
        d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_EDGE)
        art = Image.open(self.panels[story["art"]]).convert("RGB")
        self.img.paste(fit_cover(art, w - 2, 72, story["focus"]), (x + 1, y + 1))
        self.number_badge(x + 12, y + 12, story["n"])
        self.verify_tag(x + w - 1, y + 1, story["tag"])
        tx = x + 6
        d.text((tx, y + 78), story["kicker"], font=Type.sans_b(9),
               fill=REGION[story["region"]])
        yy = y + 92
        for line in wrap(d, story["head"], Type.serif_b(head_size), w - 12, 2):
            d.text((tx, yy), line, font=Type.serif_b(head_size), fill=INK)
            yy += head_size + 3
        for line in wrap(d, story["deck"], Type.sans(deck_size), w - 12, 2):
            d.text((tx, yy), line, font=Type.sans(deck_size), fill=BODY)
            yy += deck_size + 1

    # -- header ------------------------------------------------------------
    def header(self):
        d = self.d
        d.text((16, 4), "THE WORLD IN ONE DAY", font=Type.sans_b(11), fill=INK)
        topline = ("42 STORIES \u00b7 7 REGIONS \u00b7 8 FIELDS \u00b7 14 ILLUSTRATED "
                   "\u00b7 ALL FROM THURSDAY")
        d.text((1008, 4), topline, font=Type.sans_b(11), fill=RED, anchor="ra")
        d.text((512, 18), "Thursday 19 November 2026", font=Type.serif_b(44),
               fill=INK, anchor="ma")
        d.line([(16, 72), (1008, 72)], fill=RED, width=2)
        d.line([(16, 76), (1008, 76)], fill=INK, width=1)
        sub = ("Trump, Xi and Putin share one table \u00b7 The World Court finds genocide in Myanmar "
               "\u00b7 A 13-year wait for a game ends")
        f = Type.serif(13)
        d.text(((PAGE_W - measure(d, sub, f)) / 2, 79), sub, font=f, fill=RED)

    def region_bar(self):
        d = self.d
        top, bottom = 96, 112
        total = sum(count for _name, count in REGION_TALLY)
        x = 16
        for name, count in REGION_TALLY:
            seg = int(992 * count / total)
            d.rectangle([x, top, x + seg, bottom], fill=REGION[name])
            label = f"{name} {count}"
            f = Type.sans_b(10)
            if measure(d, label, f) + 8 <= seg:
                d.text((x + (seg - measure(d, label, f)) / 2, top + 3), label,
                       font=f, fill=(255, 255, 255))
            x += seg

    def numbers_strip(self):
        d = self.d
        text = ("THE DAY IN NUMBERS:  3 presidents  \u00b7  9\u20136 genocide vote  \u00b7  "
                "$81.3bn record IPO  \u00b7  109\u20130 Arctic vote  \u00b7  "
                "551,864 exam sitters  \u00b7  4.9% jobless")
        f = Type.sans_b(10)
        d.text(((PAGE_W - measure(d, text, f)) / 2, 116), text, font=f, fill=INK)

    def story_grid(self):
        # Row 1: three wide panels.
        for i, x in enumerate((16, 347, 678)):
            self.panel_wide(x, 132, 330, 182, CORE[i])
        # Row 2: five narrow panels.
        for i, x in enumerate((16, 215, 414, 613, 812)):
            self.panel_narrow(x, 318, 196, 146, CORE[3 + i])
        # Row 3: six narrow panels, slightly smaller type.
        for i, x in enumerate((16, 182, 348, 514, 680, 846)):
            self.panel_narrow(x, 468, 162, 146, CORE[8 + i], head_size=12, deck_size=9)

    # -- bottom band: map + also-on -----------------------------------------
    def locator_map(self):
        d = self.d
        x0, y0, x1, y1 = 16, 618, 424, 1008
        d.rectangle([x0, y0, x1, y1], fill=SEA, outline=CARD_EDGE)
        d.text((x0 + 10, y0 + 7), "WHERE IT HAPPENED", font=Type.sans_b(12), fill=INK)
        d.text((x1 - 10, y0 + 8), "14 numbered stories",
               font=Type.sans(10), fill=GREY, anchor="ra")
        ox, oy, mw, mh = x0 + 8, y0 + 28, x1 - x0 - 16, 300
        for _name, points in CONTINENTS:
            xy = [lonlat_to_xy(lon, lat, ox, oy, mw, mh) for lon, lat in points]
            d.polygon(xy, fill=LAND, outline=COAST)
        for label, lon, lat in CONTINENT_NAMES:
            lx, ly = lonlat_to_xy(lon, lat, ox, oy, mw, mh)
            f = Type.sans_b(8)
            d.text((lx - measure(d, label, f) / 2, ly - 4), label,
                   font=f, fill=MAP_TEXT)
        placed = []
        for story in CORE:
            px, py = lonlat_to_xy(story["lon"], story["lat"], ox, oy, mw, mh)
            px, py = nudge_pin(px, py, placed, 21)
            placed.append((px, py))
            d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                      outline=(255, 255, 255), width=1)
            f = Type.sans_b(9)
            tw = measure(d, str(story["n"]), f)
            d.text((px - tw / 2, py - 6), str(story["n"]), font=f,
                   fill=(255, 255, 255))
        for item in ALSO:
            px, py = lonlat_to_xy(item["lon"], item["lat"], ox, oy, mw, mh)
            px, py = nudge_pin(px, py, placed, 12)
            placed.append((px, py))
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GOLD,
                      outline=(255, 255, 255), width=1)
        # Region legend, then the sources line.
        lx = x0 + 10
        ly = y1 - 34
        for name in ("EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"):
            d.rectangle([lx, ly + 2, lx + 8, ly + 10], fill=REGION[name])
            lx += 11
            f = Type.sans_b(8)
            d.text((lx, ly), name, font=f, fill=GREY)
            lx += int(measure(d, name, f)) + 8
        d.text((x0 + 10, y1 - 18),
               "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 UN News \u2014 19 Nov 2026. All drawings original.",
               font=Type.sans(9), fill=GREY)

    def also_on(self):
        d = self.d
        x0, x1 = 432, 1008
        d.text((x0, 624), "ALSO ON THURSDAY 19 NOVEMBER", font=Type.sans_b(14), fill=RED)
        d.line([(x0, 642), (x1, 642)], fill=RED, width=1)
        columns = [
            (432, 184, ALSO[0:10]),
            (624, 184, ALSO[10:19]),
            (816, 192, ALSO[19:28]),
        ]
        for col_x, col_w, items in columns:
            yy = 650
            for item in items:
                num_text = f"{item['n']}."
                f_num = Type.sans_b(9)
                d.text((col_x, yy), num_text, font=f_num,
                       fill=REGION[item["region"]])
                num_w = measure(d, num_text, f_num) + 4
                text = item["head"] + " \u2014 " + item["sum"]
                lines = wrap(d, text, Type.sans_b(9), col_w - num_w, 2)
                x = col_x + num_w
                for li, line in enumerate(lines):
                    if li == 0 and line.startswith(item["head"]):
                        d.text((x, yy), item["head"], font=Type.sans_b(9), fill=INK)
                        rest = line[len(item["head"]):]
                        if rest:
                            hw = measure(d, item["head"], Type.sans_b(9))
                            d.text((x + hw, yy), rest, font=Type.sans(9), fill=BODY)
                    else:
                        d.text((x, yy), line, font=Type.sans(9), fill=BODY)
                    yy += 11
                yy += 1

    def date_check(self):
        d = self.d
        x0, y0, x1, y1 = 432, 880, 1008, 1008
        d.rectangle([x0, y0, x1, y1], outline=RED, width=1)
        d.text((x0 + 8, y0 + 6), "DATE CHECK", font=Type.sans_b(10), fill=RED)
        note = ("Left out on purpose because they were first reported on 18 Nov, "
                "not today: Jeffries named for US speaker, the EU's \u20ac45bn Ukraine "
                "loan plan, Iran firing on Kuwait and Bahrain, Nvidia's results, "
                "Australia's settler sanctions, Voyager 1 one light-day out. "
                "20 Nov: COP31's scheduled close, Cyclone Akvan's landfall. "
                "Tags: REPORTED = confirmed; CLAIM = one side says so; FORECAST = draft or schedule.")
        yy = y0 + 22
        for line in wrap(d, note, Type.sans(10), x1 - x0 - 16, 5):
            d.text((x0 + 8, yy), line, font=Type.sans(10), fill=BODY)
            yy += 13

    def render(self):
        self.header()
        self.region_bar()
        self.numbers_strip()
        self.story_grid()
        self.locator_map()
        self.also_on()
        self.date_check()
        return self.img


def main():
    page = FrontPage().render()
    out = HERE / "entry.png"
    page.save(out, format="PNG", optimize=True)
    size = out.stat().st_size
    print(f"entry.png: {page.size}, {size} bytes")
    if size > 1_048_576:
        jpg = HERE / "entry.jpg"
        page.save(jpg, format="JPEG", quality=90)
        print(f"PNG too big; JPEG fallback: {jpg.stat().st_size} bytes")


if __name__ == "__main__":
    main()
