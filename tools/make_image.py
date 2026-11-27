#!/usr/bin/env python3
"""Draw the front page for Thursday 26 November 2026.

A single broadsheet page, drawn with Pillow and the DejaVu fonts only.
Everything is fixed geometry and fixed text: no randomness, no network,
no timestamps, so two runs produce byte-identical PNGs.

Layout, top to bottom:
  masthead + red dateline
  lead story (Hormuz) with a drawn night-sea panel
  four secondary stories in a 2 x 2 grid
  an "ALSO TODAY" strip of eight briefs
  a footer repeating the date
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY_DIR = os.path.dirname(HERE)
OUT = os.path.join(ENTRY_DIR, "entry.png")

W, H = 1024, 1024
MARGIN = 42
CONTENT_W = W - 2 * MARGIN

PAPER = (253, 252, 247)   # warm off-white newsprint
INK = (20, 20, 20)        # near-black
RED = (176, 30, 36)       # headline red
GREY = (90, 90, 90)       # secondary text
FAINT = (170, 168, 160)   # rules
SKY = (13, 28, 48)        # night sky over the strait
SEA = (24, 52, 84)        # night sea
MOON = (240, 232, 200)    # pale moon
FLAME = (240, 123, 29)    # fire orange
EMBER = (255, 197, 61)    # fire yellow
HULL = (8, 12, 18)        # tanker silhouette

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"


def wrap(text, fnt, max_w):
    """Greedy word wrap by measured pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, max_w, max_lines):
    """Wrap text; drop trailing words until it fits max_lines lines."""
    lines = wrap(text, fnt, max_w)
    while len(lines) > max_lines:
        words = text.split()
        text = " ".join(words[:-1])
        lines = wrap(text, fnt, max_w)
    return lines


def draw_center(draw, cx, y, text, fnt, fill):
    draw.text((cx - fnt.getlength(text) / 2, y), text, font=fnt, fill=fill)


def rule(draw, x0, x1, y, fill=INK, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_masthead(draw):
    title = font(SERIF_B, 62)
    draw_center(draw, W / 2, 18, "THE WORLD TODAY", title, INK)
    rule(draw, MARGIN, W - MARGIN, 96, INK, 3)
    rule(draw, MARGIN, W - MARGIN, 101, INK, 1)
    date_f = font(SANS_B, 20)
    draw_center(draw, W / 2, 112, "THURSDAY, 26 NOVEMBER 2026", date_f, RED)


def draw_lead(draw):
    # Kicker + headline, centred.
    kicker = font(SANS_B, 17)
    draw_center(draw, W / 2, 146, "STRAIT OF HORMUZ", kicker, RED)
    head = font(SERIF_B, 50)
    draw_center(draw, W / 2, 168, "TWO MORE TANKERS", head, INK)
    draw_center(draw, W / 2, 222, "HIT MINES IN HORMUZ", head, INK)
    deck = font(SANS, 21)
    deck_lines = [
        "Iran says two vessels \u2014 one a supertanker carrying more",
        "than 2m barrels of crude \u2014 exploded and caught fire",
        "after striking naval mines off Oman.",
    ]
    y = 282
    for line in deck_lines:
        draw_center(draw, W / 2, y, line, deck, (50, 50, 50))
        y += 27
    draw_sea_panel(draw, MARGIN, 368, W - MARGIN, 472)


def draw_sea_panel(draw, x0, y0, x1, y1):
    """Night strait: moon, two burning tankers, drifting mines."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    horizon = y0 + 52
    draw.rectangle([x0, horizon, x1, y1], fill=SEA)
    # Moon and its reflection.
    mx, my = x0 + 92, y0 + 30
    draw.ellipse([mx - 20, my - 20, mx + 20, my + 20], fill=MOON)
    for i, w in enumerate((70, 46, 26)):
        draw.line([(mx - w / 2, horizon + 8 + i * 9),
                   (mx + w / 2, horizon + 8 + i * 9)],
                  fill=(120, 140, 165), width=2)
    # Wave strokes, kept inside the panel.
    for wy in (horizon + 16, horizon + 32):
        for wx in range(x0 + 14, x1 - 60, 96):
            draw.arc([wx, wy, wx + 56, wy + 12], 0, 180,
                     fill=(70, 100, 135), width=2)
    # Two tankers: dark hulls riding the horizon line.
    draw_tanker(draw, x0 + 250, horizon - 6, 300, 26)
    draw_tanker(draw, x0 + 600, horizon - 6, 260, 22)
    # Flames on each deck.
    draw_flames(draw, x0 + 330, horizon - 6)
    draw_flames(draw, x0 + 690, horizon - 6)
    # Drifting mines in the foreground water.
    draw_mine(draw, x0 + 90, y1 - 22, 9)
    draw_mine(draw, x0 + 480, y1 - 14, 7)
    draw_mine(draw, x0 + 830, y1 - 26, 8)


def draw_tanker(draw, x, y, length, height):
    """A flat tanker silhouette: hull, bow, bridge block, funnel."""
    draw.polygon([(x, y), (x + length, y), (x + length - 18, y + height),
                  (x + 8, y + height)], fill=HULL)
    draw.rectangle([x + length - 62, y - 16, x + length - 30, y], fill=HULL)
    draw.rectangle([x + 34, y - 10, x + 48, y], fill=HULL)


def draw_flames(draw, x, y):
    """Three stylised flame tongues rising from a deck point."""
    draw.polygon([(x - 16, y), (x - 6, y - 28), (x + 2, y)], fill=FLAME)
    draw.polygon([(x - 4, y), (x + 6, y - 38), (x + 16, y)], fill=EMBER)
    draw.polygon([(x + 12, y), (x + 20, y - 22), (x + 28, y)], fill=FLAME)
    draw.ellipse([x - 20, y - 46, x + 28, y - 28], fill=(120, 120, 120))


def draw_mine(draw, cx, cy, r):
    """A spiked naval mine: dark ball with radiating spikes."""
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)):
        draw.line([(cx + dx * r, cy + dy * r),
                   (cx + dx * (r + 7), cy + dy * (r + 7))],
                  fill=(5, 8, 12), width=3)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(5, 8, 12))


def draw_secondaries(draw):
    rule(draw, MARGIN, W - MARGIN, 486, INK, 2)
    cells = [
        ("KUWAIT", "Drone strike kills two Italians; Iran denies role",
         "Tehran is blamed for an attack on a Kuwaiti air-defence "
         "station where two Rheinmetall technicians worked."),
        ("BANGKOK", "Blast at oil refinery injures nine",
         "Fire at Bangchak's Phra Khanong plant is put out in "
         "30 minutes; all production units are shut down."),
        ("KYIV", "Missiles hit mall overnight; seven hurt",
         "Russia strikes a shopping centre and two other buildings; "
         "Zelenskyy warns a new mass strike is coming."),
        ("FRANKFURT", "Spain's de Cos picked to lead ECB",
         "EU leaders choose the former Bank of Spain chief to "
         "succeed Christine Lagarde in February."),
    ]
    col_w = (CONTENT_W - 30) // 2
    xs = [MARGIN, MARGIN + col_w + 30]
    ys = [500, 626]
    for i, (tag, head, deck) in enumerate(cells):
        x = xs[i % 2]
        y = ys[i // 2]
        tag_f = font(SANS_B, 15)
        draw.text((x, y), tag, font=tag_f, fill=RED)
        head_f = font(SERIF_B, 23)
        lines = fit_lines(head, head_f, col_w, 2)
        hy = y + 22
        for line in lines:
            draw.text((x, hy), line, font=head_f, fill=INK)
            hy += 28
        deck_f = font(SANS, 16)
        dlines = fit_lines(deck, deck_f, col_w, 2)
        dy = hy + 4
        for line in dlines:
            draw.text((x, dy), line, font=deck_f, fill=(50, 50, 50))
            dy += 21


def draw_briefs(draw):
    rule(draw, MARGIN, W - MARGIN, 762, INK, 2)
    head_f = font(SANS_B, 18)
    draw.text((MARGIN, 774), "ALSO TODAY", font=head_f, fill=INK)
    briefs = [
        ("CAIRO", "Driver detained after tanker blaze kills 31."),
        ("CONGO", "Ebola passes 12,000 cases; 5,904 dead."),
        ("BOGOR", "Mine flood toll rises to 13 dead, 13 missing."),
        ("LONDON", "UK net migration falls to 77,000."),
        ("NEW YORK", "Macy's parade postponed by storm, a first in 100 years."),
        ("GAZA", "Israeli strikes kill 9, incl. Hamas deputy minister."),
        ("TRADE", "China and Brazil push back on new US tariffs."),
        ("TECH", "Nvidia halts server shipments to four SE Asian states."),
    ]
    col_w = (CONTENT_W - 30) // 2
    xs = [MARGIN, MARGIN + col_w + 30]
    lead_f = font(SANS_B, 15)
    body_f = font(SANS, 15)
    for i, (lead, text) in enumerate(briefs):
        x = xs[i % 2]
        y = 806 + (i // 2) * 42
        draw.text((x, y), lead + "  ", font=lead_f, fill=RED)
        lw = lead_f.getlength(lead + "  ")
        lines = fit_lines(text, body_f, col_w - lw, 2)
        for j, line in enumerate(lines):
            draw.text((x + lw, y + j * 19), line, font=body_f, fill=INK)


def draw_footer(draw):
    rule(draw, MARGIN, W - MARGIN, 986, FAINT, 1)
    foot = font(SANS, 13)
    draw_center(draw, W / 2, 994,
                "THE WORLD TODAY  \u00b7  Thursday, 26 November 2026  "
                "\u00b7  One day's news in one image",
                foot, GREY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw)
    draw_secondaries(draw)
    draw_briefs(draw)
    draw_footer(draw)
    img.save(OUT, format="PNG")


if __name__ == "__main__":
    main()
