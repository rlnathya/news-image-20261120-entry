#!/usr/bin/env python3
"""Draw the front page for the make.fun news-image-20261120 entry.

A newspaper front page summing up Friday 20 November 2026 in one image.
Deterministic: no timestamps, no randomness, no network, fixed fonts and
fixed layout, so the script always writes the same PNG bytes.

Usage: python3 render_frontpage.py [output-path]
Default output: entry.png next to this script.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width: 952

BLACK = (17, 17, 17)
RED = (192, 0, 0)
DARK_BLUE = (31, 58, 95)
GREY = (102, 102, 102)
LIGHT_GREY = (242, 242, 242)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
ORANGE = (230, 120, 0)
GOLD = (255, 180, 0)

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(text, fnt, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if fnt.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def draw_centered(draw, cx, y, text, fnt, fill):
    w = fnt.getlength(text)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return text_height(fnt)


def draw_block(draw, x, y, lines, fnt, fill, leading):
    """Draw wrapped lines left-aligned. Returns the y after the block."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, x1, y, weight=2, fill=BLACK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


# ---------------------------------------------------------------------------
# Small illustrations, drawn only with PIL shapes.
# Each takes the draw object and a box (x0, y0, x1, y1) to fill.
# ---------------------------------------------------------------------------

def art_scales(draw, x0, y0, x1, y1):
    """Scales of justice."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    cx = (x0 + x1) // 2
    top = y0 + 14
    base = y1 - 14
    mid = (top + base) // 2
    # base and pole
    draw.rectangle([cx - 34, base - 6, cx + 34, base], fill=DARK_BLUE)
    draw.rectangle([cx - 3, top + 16, cx + 3, base - 6], fill=DARK_BLUE)
    # finial
    draw.ellipse([cx - 7, top, cx + 7, top + 14], fill=RED)
    # beam
    draw.rectangle([cx - 78, mid - 3, cx + 78, mid + 3], fill=DARK_BLUE)
    for sign in (-1, 1):
        px = cx + sign * 62
        # hanger lines
        draw.line([px, mid + 3, px - 20, mid + 34], fill=DARK_BLUE, width=2)
        draw.line([px, mid + 3, px + 20, mid + 34], fill=DARK_BLUE, width=2)
        # pan
        draw.pieslice([px - 22, mid + 30, px + 22, mid + 62],
                      0, 180, fill=RED)
        draw.rectangle([px - 22, mid + 30, px + 22, mid + 33], fill=RED)


def art_flags(draw, x0, y0, x1, y1):
    """Three flags: United States, China, Russia."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    # three poles
    poles = [x0 + w * 0.22, x0 + w * 0.50, x0 + w * 0.78]
    flag_w, flag_h = 52, 32
    top = y0 + 10
    for i, px in enumerate(poles):
        draw.rectangle([px - 2, top, px + 2, y1 - 8], fill=BLACK)
        fx0, fy0 = int(px + 2), top
        fx1, fy1 = fx0 + flag_w, fy0 + flag_h
        if i == 0:  # United States: stripes + blue canton
            for s in range(7):
                col = (178, 34, 52) if s % 2 == 0 else WHITE
                draw.rectangle([fx0, fy0 + s * 5, fx1, fy0 + s * 5 + 5],
                               fill=col)
            draw.rectangle([fx0, fy0, fx0 + 22, fy0 + 16], fill=DARK_BLUE)
            for sx in (6, 14):
                for sy in (5, 11):
                    draw.ellipse([fx0 + sx, fy0 + sy, fx0 + sx + 3,
                                  fy0 + sy + 3], fill=WHITE)
        elif i == 1:  # China: red field, yellow stars
            draw.rectangle([fx0, fy0, fx1, fy1], fill=(222, 41, 16))
            draw.ellipse([fx0 + 6, fy0 + 6, fx0 + 14, fy0 + 14], fill=GOLD)
            for sx, sy in ((26, 5), (34, 11), (34, 19), (26, 24)):
                draw.ellipse([fx0 + sx, fy0 + sy, fx0 + sx + 4,
                              fy0 + sy + 4], fill=GOLD)
        else:  # Russia: white, blue, red horizontal bands
            draw.rectangle([fx0, fy0, fx1, fy0 + 11], fill=WHITE)
            draw.rectangle([fx0, fy0 + 11, fx1, fy0 + 22], fill=(0, 57, 166))
            draw.rectangle([fx0, fy0 + 22, fx1, fy1], fill=(213, 0, 50))
        draw.rectangle([fx0, fy0, fx1, fy1], outline=BLACK, width=1)


def art_parliament(draw, x0, y0, x1, y1):
    """A parliament building: pediment, columns, steps. Wide, short box."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    cx = (x0 + x1) // 2
    h = y1 - y0
    # pediment: small triangle centred above the columns
    ped_h = max(12, h // 4)
    draw.polygon([(cx - 52, y0 + ped_h + 2), (cx + 52, y0 + ped_h + 2),
                  (cx, y0 + 3)], fill=DARK_BLUE)
    draw.ellipse([cx - 5, y0 + ped_h - 4, cx + 5, y0 + ped_h + 6],
                 fill=WHITE)
    # columns: short bars standing on the base
    base_y = y1 - 9
    col_top = y0 + ped_h + 4
    for i in range(7):
        col_x = x0 + 26 + i * 58
        draw.rectangle([col_x, col_top, col_x + 14, base_y], fill=DARK_BLUE)
    # base and steps
    draw.rectangle([x0 + 12, base_y, x1 - 12, base_y + 4], fill=DARK_BLUE)
    draw.rectangle([x0 + 6, base_y + 5, x1 - 6, y1 - 1], fill=GREY)


def art_chart(draw, x0, y0, x1, y1):
    """A rising stock chart with a +17% label. Fully box-relative."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    h = y1 - y0
    # grid
    for gx in range(x0 + 24, x1 - 8, 34):
        draw.line([gx, y0 + 8, gx, y1 - 6], fill=(220, 220, 220), width=1)
    for gy in range(y0 + 12, y1 - 4, 14):
        draw.line([x0 + 8, gy, x1 - 8, gy], fill=(220, 220, 220), width=1)
    # rising line, from bottom-left to top-right, inside the box
    base = y1 - 8
    top = y0 + 14
    span = base - top
    fracs = [0.0, 0.25, 0.18, 0.55, 0.65, 1.0]
    xs = [x0 + 14, x0 + 52, x0 + 86, x0 + 120, x0 + 154, x0 + 188]
    pts = [(x, base - int(span * f)) for x, f in zip(xs, fracs)]
    draw.line(pts, fill=GREEN, width=4, joint="curve")
    # arrowhead at the last point
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 14, ey + 2), (ex - 4, ey + 12)],
                 fill=GREEN)
    fnt = font(SANS_BOLD, 22)
    draw.text((x0 + 12, y0 + 4), "+17%", font=fnt, fill=GREEN)


def art_tanker(draw, x0, y0, x1, y1):
    """A tanker at sea with flames above it. Scales to any box height."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    h = y1 - y0
    sea_top = y1 - max(12, h // 4)
    deck = sea_top - 10
    # sea
    draw.rectangle([x0, sea_top, x1, y1], fill=(90, 140, 190))
    # hull
    draw.polygon([(x0 + 22, sea_top), (x0 + 196, sea_top),
                  (x0 + 182, sea_top + 10), (x0 + 36, sea_top + 10)],
                 fill=BLACK)
    # deck + containers
    draw.rectangle([x0 + 40, deck - 8, x0 + 90, sea_top], fill=(200, 60, 40))
    draw.rectangle([x0 + 96, deck - 8, x0 + 146, sea_top],
                   fill=(60, 120, 180))
    draw.rectangle([x0 + 152, deck - 14, x0 + 176, sea_top], fill=GREY)
    # flames: heights scaled to the space above the deck
    room = deck - y0 - 4
    for fx, frac, col in ((x0 + 56, 0.75, ORANGE), (x0 + 82, 1.0, RED),
                          (x0 + 108, 0.65, GOLD), (x0 + 132, 0.85, ORANGE)):
        fh = max(8, int(room * frac))
        draw.polygon([(fx - 11, deck - 8), (fx, deck - 8 - fh),
                      (fx + 11, deck - 8)], fill=col)
    # smoke puffs at the top
    for sx, sy, r in ((x0 + 60, y0 + 7, 5), (x0 + 84, y0 + 4, 6),
                      (x0 + 110, y0 + 7, 5)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(150, 150, 150))


def art_globe(draw, x0, y0, x1, y1):
    """A globe with a green leaf."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    cx, cy = (x0 + x1) // 2 - 14, (y0 + y1) // 2
    r = 30
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=DARK_BLUE,
                 width=3)
    draw.ellipse([cx - 12, cy - r, cx + 12, cy + r], outline=DARK_BLUE,
                 width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=DARK_BLUE, width=2)
    draw.arc([cx - r, cy - 16, cx + r, cy + 16], 200, 340, fill=DARK_BLUE,
             width=2)
    # leaf
    lx, ly = cx + 34, cy + 8
    draw.pieslice([lx - 4, ly - 22, lx + 20, ly + 4], 270, 90, fill=GREEN)
    draw.line([lx, ly, lx + 20, ly - 22], fill=GREEN, width=2)
    # small sun
    draw.ellipse([x1 - 34, y0 + 10, x1 - 18, y0 + 26], fill=GOLD)


ART = {
    "scales": art_scales,
    "flags": art_flags,
    "parliament": art_parliament,
    "chart": art_chart,
    "tanker": art_tanker,
    "globe": art_globe,
}

# ---------------------------------------------------------------------------
# Stories. Wording verified against reporting of 20 November 2026:
# ICJ Myanmar genocide ruling; Shenzhen trilateral peace declaration;
# Berlin coalition-of-the-willing meeting; Anthropic Nasdaq debut (+17%,
# S&P 500 down a sixth straight session); Hormuz tanker mine strikes and
# Houthi missiles hitting Riyadh's PIF tower; COP31 draft dropping fossil
# fuels in Antalya.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "THE HAGUE  •  WORLD COURT",
    "headline": "UN COURT: MYANMAR COMMITTED GENOCIDE",
    "subhead": ("The International Court of Justice rules Myanmar committed "
                "genocide against the Rohingya in 2017 — a first against a "
                "state. Refugees in Bangladesh cheered."),
    "art": "scales",
}

BODY = [
    {
        "kicker": "SHENZHEN  •  SUMMIT",
        "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
        "subhead": ("First-ever trilateral summit issues a four-point "
                    "declaration. It does not mention Ukraine."),
        "art": "flags",
    },
    {
        "kicker": "BERLIN  •  EUROPE",
        "headline": "EUROPE READY FOR RUSSIA TALKS",
        "subhead": ("Allies meet in Berlin, united on Ukraine. Putin "
                    "invites European leaders to Moscow."),
        "art": "parliament",
    },
    {
        "kicker": "NEW YORK  •  MARKETS",
        "headline": "ANTHROPIC SOARS IN RECORD DEBUT",
        "subhead": ("Shares close up 17% on their Nasdaq debut. The S&P "
                    "500 falls for a sixth straight session."),
        "art": "chart",
    },
    {
        "kicker": "THE GULF  •  WAR AT SEA",
        "headline": "GULF IN FLAMES",
        "subhead": ("Mine strikes set tankers ablaze in the Strait of "
                    "Hormuz. Houthis hit Riyadh's tallest tower."),
        "art": "tanker",
    },
]

CLOSER = {
    "kicker": "ANTALYA  •  CLIMATE",
    "headline": "COP31 DRAFT DROPS FOSSIL FUELS",
    "subhead": ("Outcry in Antalya as fossil fuels are removed from the "
                "latest draft of the UN climate deal."),
    "art": "globe",
}

TICKER_LINES = [
    "Kyiv hit by four ballistic missiles  •  Genoa airport halts flights "
    "after drone sightings",
    "India evacuates 80,000 as Cyclone Dana makes landfall  •  Migrant "
    "boat sinks off Senegal, dozens missing",
]


def render():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    y = 14
    # ---- Masthead ----
    rule(draw, MARGIN, W - MARGIN, y, 3)
    y += 6
    mast_fnt = font(SERIF_BLACK, 84)
    draw_centered(draw, W // 2, y, "THE WORLD", mast_fnt, BLACK)
    y += text_height(mast_fnt) + 2
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6
    # ---- Dateline: the day must be unmistakable ----
    date_fnt = font(SANS_BOLD, 36)
    draw_centered(draw, W // 2, y, "FRIDAY, 20 NOVEMBER 2026", date_fnt,
                  RED)
    y += text_height(date_fnt) + 6
    rule(draw, MARGIN, W - MARGIN, y, 4)
    y += 10

    # ---- Lead story (full width, art on the right) ----
    lead_top = y
    art_w = 300
    art_x0 = W - MARGIN - art_w
    text_w = art_x0 - 24 - MARGIN
    kicker_fnt = font(SANS_BOLD, 18)
    head_fnt = font(SERIF_BOLD, 44)
    sub_fnt = font(SANS, 21)
    draw.text((MARGIN, lead_top), LEAD["kicker"], font=kicker_fnt, fill=RED)
    hy = lead_top + 24
    head_lines = wrap(LEAD["headline"], head_fnt, text_w)
    hy = draw_block(draw, MARGIN, hy, head_lines, head_fnt, BLACK, 48)
    sub_lines = wrap(LEAD["subhead"], sub_fnt, text_w)
    sy = hy + 6
    sy = draw_block(draw, MARGIN, sy, sub_lines, sub_fnt, BLACK, 25)
    content_h = sy - lead_top
    art_h = max(content_h, 150)
    ART[LEAD["art"]](draw, art_x0, lead_top, W - MARGIN, lead_top + art_h)
    y = lead_top + max(art_h, content_h) + 10
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6

    # ---- Body stories: two columns, two rows.
    # Each cell's height is measured from its own wrapped text, so no
    # divider ever crosses a line of text.
    col_w = (CW - 24) // 2
    for row in range(2):
        row_top = y
        row_bottom = row_top
        for col in range(2):
            story = BODY[row * 2 + col]
            x0 = MARGIN + col * (col_w + 24)
            cy = row_top
            ART[story["art"]](draw, x0, cy, x0 + col_w, cy + 48)
            cy += 48 + 6
            kf = font(SANS_BOLD, 16)
            draw.text((x0, cy), story["kicker"], font=kf, fill=RED)
            cy += 20
            hf = font(SERIF_BOLD, 31)
            lines = wrap(story["headline"], hf, col_w)
            cy = draw_block(draw, x0, cy, lines, hf, BLACK, 36)
            cy += 3
            sf = font(SANS, 18)
            slines = wrap(story["subhead"], sf, col_w)
            cy = draw_block(draw, x0, cy, slines, sf, BLACK, 21)
            row_bottom = max(row_bottom, cy)
        y = row_bottom + 10
        rule(draw, MARGIN, W - MARGIN, y, 2)
        y += 6

    # ---- Closer story (full width, art on the left) ----
    closer_top = y
    art_w2 = 130
    ART[CLOSER["art"]](draw, MARGIN, closer_top, MARGIN + art_w2,
                       closer_top + 100)
    tx = MARGIN + art_w2 + 20
    tw = W - MARGIN - tx
    kf = font(SANS_BOLD, 16)
    draw.text((tx, closer_top), CLOSER["kicker"], font=kf, fill=RED)
    cy = closer_top + 20
    hf = font(SERIF_BOLD, 36)
    lines = wrap(CLOSER["headline"], hf, tw)
    cy = draw_block(draw, tx, cy, lines, hf, BLACK, 42)
    cy += 2
    sf = font(SANS, 19)
    slines = wrap(CLOSER["subhead"], sf, tw)
    cy = draw_block(draw, tx, cy, slines, sf, BLACK, 23)
    y = max(closer_top + 100, cy) + 10
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6

    # ---- Bottom ticker ----
    ticker_h = 42
    assert y + ticker_h <= H - 8, "layout overflow: ticker ends at %d" % (
        y + ticker_h)
    draw.rectangle([MARGIN, y, W - MARGIN, y + ticker_h], fill=RED)
    tf = font(SANS_BOLD, 17)
    ty = y + 3
    for line in TICKER_LINES:
        twd = tf.getlength(line)
        draw.text((W // 2 - twd / 2, ty), line, font=tf, fill=WHITE)
        ty += 19

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, format="PNG")
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
