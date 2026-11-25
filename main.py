#!/usr/bin/env python3
"""The World in One Day — a newspaper front page summing up the world news
of Tuesday 24 November 2026 in a single 800x800 PNG.

Drawn from scratch with the Python standard library only: a hand-drawn
5x7 bitmap font, pure-Python pixel routines and a hand-rolled PNG encoder.
No network, no randomness — two runs write byte-identical output.
"""
import os
import struct
import zlib

W, H = 800, 800

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 229)
INK = (25, 25, 25)
RED = (168, 35, 26)
NAVY = (30, 58, 95)
SEA = (46, 95, 122)
SKY = (214, 228, 235)
FLAME = (224, 123, 31)
FLAME_Y = (242, 194, 48)
SMOKE = (138, 138, 138)
GREY = (120, 116, 108)
WHITE = (255, 255, 255)
GOLD = (176, 138, 44)

# ------------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = ink. Uppercase, digits and punctuation.
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "'": ["..#..", "..#..", "..#..", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}
# Bullet and em dash reuse simple shapes.
GLYPHS["\u2022"] = [".....", ".....", ".###.", ".###.", ".###.", ".....", "....."]
GLYPHS["\u2014"] = [".....", ".....", ".....", "#####", ".....", ".....", "....."]

# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Filled triangle via horizontal spans.
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        def span(y, p, q):
            if p[1] == q[1]:
                return None
            t = (y - p[1]) / (q[1] - p[1])
            return p[0] + t * (q[0] - p[0])
        for y in range(ay, cy + 1):
            xs = []
            for p, q in ((ys[0], ys[1]), (ys[1], ys[2]), (ys[0], ys[2])):
                v = span(y, p, q)
                if v is not None:
                    xs.append(v)
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, y, xb - xa + 1, 1, c)

# -------------------------------------------------------------------- text
def char_w(scale):
    return 6 * scale

def text_w(text, scale):
    return len(text) * char_w(scale) - scale if text else 0

def draw_char(cv, x, y, ch, scale, color):
    g = GLYPHS.get(ch.upper(), GLYPHS["?"])
    for r, row in enumerate(g):
        for col, bit in enumerate(row):
            if bit == "#":
                cv.fill_rect(x + col * scale, y + r * scale, scale, scale, color)

def draw_text(cv, x, y, text, scale, color):
    cx = x
    for ch in text:
        draw_char(cv, cx, y, ch, scale, color)
        cx += char_w(scale)

def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_w(text, scale) // 2, y, text, scale, color)

def wrap(text, max_w, scale):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def draw_block(cv, x, y, text, max_w, scale, color, pitch=None):
    lines = wrap(text, max_w, scale)
    p = pitch if pitch is not None else 8 * scale
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * p, line, scale, color)
    return y + len(lines) * p

# --------------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ------------------------------------------------------------------ layout
def rule(cv, x, y, w, color=INK, t=2):
    cv.hline(x, y, w, color, t)

def kicker(cv, x, y, text, color=RED):
    draw_text(cv, x, y, text, 2, color)

def draw_tanker_scene(cv, x0, y0, x1, y1):
    """Sea, tanker, flames and a naval mine inside the hero panel."""
    # Sky strip.
    cv.fill_rect(x0, y0, x1 - x0, y1 - y0, SKY)
    # Sea.
    sea_y = y0 + 46
    cv.fill_rect(x0, sea_y, x1 - x0, y1 - sea_y, SEA)
    for wy in (sea_y + 12, sea_y + 26, sea_y + 40):
        for wx in range(x0 + 12, x1 - 30, 46):
            cv.hline(wx, wy, 26, WHITE, 2)
    # Smoke puffs.
    for cx, cy, r in ((252, y0 + 8, 9), (268, y0 + 2, 11), (288, y0 + 9, 8)):
        cv.disc(cx, cy, r, SMOKE)
        cv.disc(cx - 3, cy - 3, r - 4, GREY)
    # Flames above the tanker midship.
    cv.triangle(232, y0 + 44, 252, y0 + 6, 272, y0 + 44, FLAME)
    cv.triangle(258, y0 + 44, 276, y0 + 14, 294, y0 + 44, FLAME_Y)
    cv.triangle(300, y0 + 44, 314, y0 + 18, 328, y0 + 44, FLAME)
    # Hull.
    cv.fill_rect(110, y0 + 44, 300, 20, INK)
    cv.triangle(410, y0 + 44, 436, y0 + 44, 410, y0 + 64, INK)
    # Deck: bridge and funnel.
    cv.fill_rect(150, y0 + 26, 34, 18, WHITE)
    cv.fill_rect(156, y0 + 30, 22, 4, NAVY)
    cv.fill_rect(360, y0 + 28, 16, 16, RED)
    cv.fill_rect(360, y0 + 28, 16, 4, INK)
    # Containers.
    cv.fill_rect(200, y0 + 32, 22, 12, GOLD)
    cv.fill_rect(226, y0 + 32, 22, 12, NAVY)
    # Naval mine in the water, right of the tanker.
    mx, my = 452, sea_y + 22
    cv.disc(mx, my, 8, INK)
    for dx, dy in ((0, -12), (0, 12), (-12, 0), (12, 0),
                   (-9, -9), (9, -9), (-9, 9), (9, 9)):
        cv.line(mx, my, mx + dx, my + dy, INK)

def build():
    cv = Canvas(W, H, PAPER)
    # Frame.
    cv.fill_rect(0, 0, W, 4, INK)
    cv.fill_rect(0, H - 4, W, 4, INK)

    # ---- masthead
    draw_text_centered(cv, W // 2, 22, "THE WORLD IN ONE DAY", 5, INK)
    rule(cv, 20, 66, 760)
    rule(cv, 20, 70, 760)
    draw_text_centered(cv, W // 2, 80, "TUESDAY, 24 NOVEMBER 2026", 3, RED)
    rule(cv, 20, 110, 760)
    draw_text_centered(cv, W // 2, 118, "ONE DAY OF WORLD NEWS - IN A SINGLE PICTURE", 2, INK)
    rule(cv, 20, 140, 760, INK, 2)

    # ---- hero: Strait of Hormuz
    hx, hy, hw = 20, 150, 476
    kicker(cv, hx, hy + 8, "THE LEAD STORY - IRAN WAR")
    draw_block(cv, hx, hy + 30, "FOUR TANKERS HIT MINES IN HORMUZ",
               hw - 40, 4, INK, pitch=32)
    draw_block(cv, hx, hy + 104,
               "Iran says four oil tankers exploded and caught fire east of "
               "the Strait of Hormuz, as its navy warns ships off "
               "'unauthorised' routes.",
               hw - 40, 2, INK, pitch=16)
    draw_tanker_scene(cv, hx + 12, hy + 176, hx + hw - 12, hy + 272)
    cv.vline(hx + hw + 4, hy, 282, INK, 2)

    # ---- right column: Gaza and Ukraine
    rx = 512
    rw = 268
    # Gaza
    kicker(cv, rx, 158, "GAZA - ISRAEL-HAMAS WAR")
    draw_block(cv, rx, 180, "HAMAS SECURITY CHIEF KILLED", rw - 16, 3, INK, pitch=24)
    draw_block(cv, rx, 232,
               "Israeli airstrikes kill Naeem Abu Nahel and six others in "
               "Gaza, medics say.",
               rw - 16, 2, INK, pitch=16)
    rule(cv, rx, 286, rw, GREY, 1)
    # Ukraine
    kicker(cv, rx, 292, "UKRAINE - RUSSIA'S WAR")
    draw_block(cv, rx, 314, "RUSSIAN STRIKE HITS FLATS IN ZAPORIZHZHIA",
               rw - 16, 3, INK, pitch=24)
    draw_block(cv, rx, 388,
               "Two killed, 40 hurt, four of them children.",
               rw - 16, 2, INK, pitch=16)

    # ---- row two: Korea, markets, trade
    rule(cv, 20, 438, 760, INK, 2)
    panels = [
        (20, "ASIA - KOREA",
         "RUSSIAN JETS TRIGGER SEOUL AIR ALERT",
         "Russian warplanes enter South Korea's air defence zone; Seoul "
         "briefly warns residents to take cover."),
        (276, "MARKETS",
         "NASDAQ SELLS OFF AS HUANG RALLY FADES",
         "US consumer confidence jumps to 103.3 in November, up from 91.9 "
         "in October."),
        (532, "TRADE - US-CHINA",
         "CHINA PAUSES MINERAL CURBS TO US",
         "Beijing suspends export curbs until January; Washington readies "
         "new tariffs on China."),
    ]
    for px, kick, head, sub in panels:
        pw = 248
        kicker(cv, px, 450, kick)
        draw_block(cv, px, 474, head, pw - 16, 3, INK, pitch=24)
        # Sub sits below the headline; headline takes 3 lines (72px).
        draw_block(cv, px, 474 + 76, sub, pw - 16, 2, INK, pitch=16)
        if px < 500:
            cv.vline(px + pw + 4, 448, 182, GREY, 1)

    # ---- footer ticker
    rule(cv, 20, 642, 760, INK, 2)
    kicker(cv, 20, 652, "ALSO TODAY")
    ticker = ("Germany first to use Ukraine's Delta system \u2022 Oregon, "
              "Virginia sue SpaceX over Grok images \u2022 Venezuela reveals "
              "$237bn debt \u2022 NATO vows to defend space \u2022 Singapore "
              "set for best year since 2011 \u2022 Bus crash in UAE kills 11 "
              "\u2022 UN urges probe into Benghazi attacks")
    draw_block(cv, 20, 676, ticker, 760, 2, INK, pitch=16)
    rule(cv, 20, 764, 760, GREY, 1)
    draw_text_centered(cv, W // 2, 774,
                       "SOURCES: REUTERS, AP, DOW JONES, JUST SECURITY",
                       2, GREY)
    return cv

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    data = png_bytes(cv)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()
