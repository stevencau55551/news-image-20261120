#!/usr/bin/env python3
"""news-image-20261120: draw one front-page image summing up the world news
of Friday 20 November 2026. Pure Python 3.13 standard library, no network,
fully deterministic: the same bytes on every run.

Layout: newspaper front page, 1024x1024.
  masthead: title + FRIDAY, 20 NOVEMBER 2026
  six panels (2 x 3): the day's biggest stories across regions and fields
  footer: sources + World Children's Day

Stories (all first reported on 20 Nov 2026):
  1. Trump delays Iran war decision to 2027 (Reuters / Times of India)
  2. Cyclone Akvan bears down on Odisha, 300,000 evacuated (The Hindu)
  3. Europe ready for talks with Russia on ending the Ukraine war (BBC)
  4. Hayabusa2 drops its asteroid landing after engine trouble (Space.com)
  5. GTA 6 sales pass $1.8 billion, overtaking The Odyssey (Mezha)
  6. Fiji declares a national disaster over severe drought (20 Nov headlines)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 228)
INK = (26, 26, 26)
WHITE = (255, 255, 255)
RED = (176, 30, 30)
GREY = (110, 108, 100)
LIGHT_GREY = (214, 209, 196)
BLUE = (31, 58, 110)
TEAL = (14, 107, 107)
PURPLE = (91, 45, 142)
ORANGE = (180, 83, 9)
GREEN = (45, 106, 45)
DARKRED = (139, 26, 26)
GOLD = (255, 215, 0)
UKR_BLUE = (0, 87, 183)
EU_BLUE = (0, 51, 153)
SKY = (135, 206, 235)
SUN = (255, 190, 0)
ROCK = (150, 148, 140)
ROCK_DARK = (110, 108, 100)
BROWN = (146, 104, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 characters, '#' = on, '.' = off.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "01010", "01110", "11111", "01110", "01010", "00000"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def rect(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, w=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = w // 2
        while True:
            self.fill_rect(x - half, y - half, w, w, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def triangle(self, pts, color):
        # filled triangle via scanlines (pts: 3 x,y pairs)
        (x0, y0), (x1, y1), (x2, y2) = pts
        ys = sorted([y0, y1, y2])
        for yy in range(ys[0], ys[2] + 1):
            xs = []
            for (ax, ay), (bx, by) in [((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))]:
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                self.fill_rect(int(min(xs)), yy, int(max(xs)) - int(min(xs)) + 1, 1, color)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s:
        # Unknown glyphs render as '?' so a typo is visible, never silent.
        glyph = FONT.get(ch, FONT['?'])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    cv.fill_rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, scale, max_w):
    # Hard-break any single word longer than the line so text can never
    # overflow its panel.
    words = []
    for word in s.split(' '):
        while text_width(word, scale) > max_w and len(word) > 1:
            cut = max_w // (6 * scale)
            words.append(word[:cut])
            word = word[cut:]
        words.append(word)
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_clock(cv, ox, oy):
    cx, cy = ox + 58, oy + 58
    cv.fill_circle(cx, cy, 52, INK)
    cv.fill_circle(cx, cy, 45, WHITE)
    cv.fill_circle(cx, cy, 45, WHITE)
    # tick marks
    for k in range(12):
        import math
        a = k * math.pi / 6
        x0 = int(cx + 38 * math.sin(a))
        y0 = int(cy - 38 * math.cos(a))
        x1 = int(cx + 43 * math.sin(a))
        y1 = int(cy - 43 * math.cos(a))
        cv.line(x0, y0, x1, y1, INK, 3)
    # hands: 10:10
    cv.line(cx, cy, cx - 22, cy - 18, INK, 5)
    cv.line(cx, cy, cx + 26, cy - 16, INK, 5)
    cv.fill_circle(cx, cy, 5, RED)


def icon_cyclone(cv, ox, oy):
    import math
    cx, cy = ox + 58, oy + 56
    pts = []
    steps = 90
    for i in range(steps + 1):
        t = i / steps * 4.0 * math.pi
        r = 6 + 44 * (i / steps)
        pts.append((int(cx + r * math.cos(t)), int(cy + r * math.sin(t))))
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], TEAL, 5)
    cv.fill_circle(cx, cy, 7, TEAL)
    # rain drops under the swirl
    for dx in (-34, 0, 34):
        cv.line(cx + dx, oy + 104, cx + dx - 5, oy + 114, BLUE, 3)


def icon_talks(cv, ox, oy):
    # two flags on poles above a table line (flags do not overlap)
    cv.line(ox + 26, oy + 14, ox + 26, oy + 84, INK, 3)
    cv.line(ox + 100, oy + 14, ox + 100, oy + 84, INK, 3)
    # Ukraine flag (left of left pole's right side): blue over yellow
    cv.fill_rect(ox + 28, oy + 14, 30, 16, UKR_BLUE)
    cv.fill_rect(ox + 28, oy + 30, 30, 16, GOLD)
    # EU flag (right, left of right pole): blue with yellow dots
    cv.fill_rect(ox + 68, oy + 14, 30, 32, EU_BLUE)
    for dx, dy in ((6, 6), (18, 6), (12, 13), (6, 20), (18, 20)):
        cv.fill_rect(ox + 68 + dx, oy + 14 + dy, 4, 4, GOLD)
    # table
    cv.line(ox + 10, oy + 92, ox + 106, oy + 92, INK, 4)
    cv.line(ox + 22, oy + 92, ox + 18, oy + 110, INK, 3)
    cv.line(ox + 94, oy + 92, ox + 98, oy + 110, INK, 3)


def icon_probe(cv, ox, oy):
    # asteroid (grey rock with craters) bottom-left
    cv.fill_circle(ox + 44, oy + 78, 34, ROCK)
    cv.fill_circle(ox + 34, oy + 68, 8, ROCK_DARK)
    cv.fill_circle(ox + 56, oy + 88, 6, ROCK_DARK)
    cv.fill_circle(ox + 50, oy + 64, 5, ROCK_DARK)
    # probe body top-right with panels and dish (bigger, clearly a craft)
    cv.fill_rect(ox + 62, oy + 14, 32, 24, GOLD)
    cv.fill_rect(ox + 50, oy + 18, 12, 16, BLUE)
    cv.fill_rect(ox + 94, oy + 18, 12, 16, BLUE)
    cv.line(ox + 78, oy + 14, ox + 88, oy + 2, INK, 3)
    cv.triangle([(ox + 78, oy + 0), (ox + 98, oy + 0), (ox + 88, oy + 12)], INK)
    # motion dashes trailing behind the probe, aligned with its centre
    for dx in (0, 16, 32):
        cv.line(ox + 6 + dx, oy + 26, ox + 16 + dx, oy + 26, GREY, 3)


def icon_controller(cv, ox, oy):
    # game controller
    cv.fill_rect(ox + 14, oy + 34, 88, 44, INK)
    cv.fill_circle(ox + 20, oy + 78, 14, INK)
    cv.fill_circle(ox + 96, oy + 78, 14, INK)
    # d-pad
    cv.fill_rect(ox + 28, oy + 46, 8, 22, WHITE)
    cv.fill_rect(ox + 21, oy + 53, 22, 8, WHITE)
    # buttons
    cv.fill_circle(ox + 82, oy + 48, 5, RED)
    cv.fill_circle(ox + 94, oy + 56, 5, GOLD)
    cv.fill_circle(ox + 82, oy + 64, 5, GREEN)
    cv.fill_circle(ox + 70, oy + 56, 5, BLUE)
    # triggers
    cv.fill_rect(ox + 26, oy + 26, 18, 8, INK)
    cv.fill_rect(ox + 72, oy + 26, 18, 8, INK)


def icon_drought(cv, ox, oy):
    import math
    # sun with rays, top-left
    cv.fill_circle(ox + 34, oy + 34, 22, SUN)
    for k in range(8):
        a = k * math.pi / 4
        x0 = int(ox + 34 + 28 * math.cos(a))
        y0 = int(oy + 34 + 28 * math.sin(a))
        x1 = int(ox + 34 + 38 * math.cos(a))
        y1 = int(oy + 34 + 38 * math.sin(a))
        cv.line(x0, y0, x1, y1, SUN, 4)
    # water drop with a slash, right (bigger, clearly a drop)
    cx, cy = ox + 86, oy + 42
    cv.triangle([(cx - 15, cy + 8), (cx + 15, cy + 8), (cx, cy - 24)], SKY)
    cv.fill_circle(cx, cy + 8, 15, SKY)
    cv.line(cx - 20, cy - 26, cx + 20, cy + 26, RED, 5)
    # cracked dry ground, bottom
    cv.fill_rect(ox + 8, oy + 88, 100, 22, BROWN)
    cv.line(ox + 20, oy + 88, ox + 30, oy + 110, INK, 4)
    cv.line(ox + 30, oy + 110, ox + 26, oy + 96, INK, 4)
    cv.line(ox + 58, oy + 88, ox + 52, oy + 104, INK, 4)
    cv.line(ox + 88, oy + 88, ox + 96, oy + 110, INK, 4)


# ---------------------------------------------------------------- stories
STORIES = [
    {
        "kicker": "USA - MIDDLE EAST", "color": DARKRED, "icon": icon_clock,
        "stat": "2027", "source": "REUTERS",
        "headline": "TRUMP DELAYS IRAN WAR DECISION TO 2027",
        "body": "PRESIDENT SAYS THERE IS 'NO RUSH' AND HE WILL 'SEE WHAT HAPPENS' AFTER JAN 1, PUSHING ANY CALL INTO NEXT YEAR.",
    },
    {
        "kicker": "INDIA - WEATHER", "color": TEAL, "icon": icon_cyclone,
        "stat": "300,000", "source": "THE HINDU",
        "headline": "CYCLONE AKVAN BEARS DOWN ON ODISHA",
        "body": "300,000 PEOPLE EVACUATED AND 423 RESCUE TEAMS DEPLOYED AS THE STORM NEARS LANDFALL ON THE EAST COAST.",
    },
    {
        "kicker": "EUROPE - UKRAINE", "color": BLUE, "icon": icon_talks,
        "stat": "TALKS", "source": "BBC",
        "headline": "EUROPE READY FOR TALKS WITH RUSSIA",
        "body": "EUROPEAN LEADERS SAY THEY ARE READY TO NEGOTIATE AN END TO THE WAR IN UKRAINE.",
    },
    {
        "kicker": "JAPAN - SPACE", "color": PURPLE, "icon": icon_probe,
        "stat": "NO LANDING", "source": "SPACE.COM",
        "headline": "HAYABUSA2 DROPS ITS ASTEROID LANDING",
        "body": "ENGINE TROUBLE FORCES JAPAN'S PROBE TO ABANDON THE LANDING AND CHANGE ITS PLANS.",
    },
    {
        "kicker": "ENTERTAINMENT", "color": ORANGE, "icon": icon_controller,
        "stat": "$1.8 BN", "source": "MEZHA",
        "headline": "GTA 6 SALES PASS $1.8 BILLION",
        "body": "THE GAME'S GLOBAL SALES OVERTAKE THE ODYSSEY'S $1.80 BN BOX-OFFICE RUN.",
    },
    {
        "kicker": "PACIFIC - CLIMATE", "color": GREEN, "icon": icon_drought,
        "stat": "DROUGHT", "source": "20 NOV HEADLINES",
        "headline": "FIJI DECLARES NATIONAL DISASTER",
        "body": "SEVERE DROUGHT AND WATER SHORTAGES FROM EL NINO PUSH FIJI INTO A STATE OF EMERGENCY.",
    },
]


def draw_panel(cv, x, y, w, h, story):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    # kicker bar
    cv.fill_rect(x + 2, y + 2, w - 4, 36, story["color"])
    draw_text(cv, x + 14, y + 12, story["kicker"], 2, WHITE)
    # icon
    story["icon"](cv, x + 14, y + 50)
    # stat under icon
    draw_text_centered(cv, x + 14 + 58, y + 176, story["stat"], 2, story["color"])
    # headline + body on the right (capped so blocks can never collide)
    tx = x + 162
    tw = w - 162 - 14
    lines = wrap_text(story["headline"], 3, tw)[:3]
    ly = y + 52
    for line in lines:
        draw_text(cv, tx, ly, line, 3, INK)
        ly += 24
    body_lines = wrap_text(story["body"], 2, tw)[:5]
    ly += 10
    for line in body_lines:
        draw_text(cv, tx, ly, line, 2, INK)
        ly += 16
    # source line at the bottom
    draw_text(cv, tx, y + h - 26, "SOURCE: " + story["source"], 2, GREY)


def build_image():
    cv = Canvas(W, H, PAPER)
    # masthead
    draw_text_centered(cv, W // 2, 26, "THE WORLD TODAY", 6, INK)
    draw_text_centered(cv, W // 2, 92, "FRIDAY, 20 NOVEMBER 2026", 4, RED)
    draw_text_centered(cv, W // 2, 140, "SIX STORIES THAT DEFINED THE DAY", 2, GREY)
    cv.fill_rect(0, 164, W, 6, RED)
    # panels 2 x 3
    margin, gap = 16, 14
    col_w = (W - 2 * margin - gap) // 2
    top, bottom = 184, 956
    row_h = (bottom - top - 2 * gap) // 3
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        px = margin + col * (col_w + gap)
        py = top + row * (row_h + gap)
        draw_panel(cv, px, py, col_w, row_h, story)
    # footer
    draw_text_centered(cv, W // 2, 972, "SOURCES: REUTERS - THE HINDU - BBC - SPACE.COM - MEZHA", 2, GREY)
    draw_text_centered(cv, W // 2, 994, "ALSO TODAY: WORLD CHILDREN'S DAY", 2, GREY)
    return cv


# ---------------------------------------------------------------- PNG encode
def encode_png(cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(ctype, data):
        out = struct.pack(">I", len(data)) + ctype + data
        out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build_image())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
