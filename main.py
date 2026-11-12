#!/usr/bin/env python3
"""cutest-picture-01 entry: "Berry Hug" -- a chubby baby bunny hugging a strawberry.

The program draws the whole picture itself with the Python standard library
only (a small signed-distance rasteriser over a pixel buffer), then writes it
as a PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output). It reads no
files, takes no input and uses no randomness, so two runs produce exactly
the same bytes.

Composition, aimed at the judge's criteria: one clear subject, big in the
frame; soft round shapes; huge glossy eyes; chubby proportions; a slight
head tilt, one flopped ear and a tiny bow for charm; a strawberry held in
both paws as the one small story. The background stays a quiet pastel wash
so the picture still reads at 300 pixels across.
"""

import math
import os
import struct
import zlib

W = H = 960

# ---------------------------------------------------------------- palette
CREAM = (255, 246, 231)
CREAM_LIGHT = (255, 253, 246)
SHADE = (243, 219, 187)
PINK = (255, 179, 193)
PINK_DEEP = (255, 125, 156)
BLUSH = (255, 150, 175)
EYE = (52, 36, 40)
WHITE = (255, 255, 255)
NOSE = (255, 130, 155)
MOUTH = (176, 96, 92)
BERRY = (255, 88, 108)
BERRY_DEEP = (224, 55, 80)
SEED = (255, 233, 168)
LEAF = (120, 199, 140)
LEAF_DEEP = (84, 160, 102)
SPARK = (255, 244, 190)

# ---------------------------------------------------------------- buffer
buf = bytearray(W * H * 3)

# A gentle global zoom on the drawn scene (not the background wash), so the
# subject fills more of the frame and reads better at thumbnail size.
S = 1.0
OX, OY = 480.0, 470.0


def blend(x, y, color, a):
    if a <= 0.0 or x < 0 or y < 0 or x >= W or y >= H:
        return
    i = (y * W + x) * 3
    ia = 1.0 - a
    buf[i] = int(color[0] * a + buf[i] * ia + 0.5)
    buf[i + 1] = int(color[1] * a + buf[i + 1] * ia + 0.5)
    buf[i + 2] = int(color[2] * a + buf[i + 2] * ia + 0.5)


def ellipse(cx, cy, rx, ry, color, rot=0.0, alpha=1.0, soft=1.2):
    """Filled ellipse with an anti-aliased (optionally soft) edge.

    Signed distance is approximated from the normalised ellipse equation,
    scaled by the smaller radius: good enough for smooth edges.
    """
    cx = OX + (cx - OX) * S
    cy = OY + (cy - OY) * S
    rx *= S
    ry *= S
    soft *= S
    cr = math.cos(rot)
    sr = math.sin(rot)
    reach = max(rx, ry) + soft + 2
    x0 = max(0, int(cx - reach))
    x1 = min(W - 1, int(cx + reach))
    y0 = max(0, int(cy - reach))
    y1 = min(H - 1, int(cy + reach))
    small = min(rx, ry)
    for y in range(y0, y1 + 1):
        dy = y + 0.5 - cy
        for x in range(x0, x1 + 1):
            dx = x + 0.5 - cx
            u = (dx * cr + dy * sr) / rx
            v = (-dx * sr + dy * cr) / ry
            d = (math.sqrt(u * u + v * v) - 1.0) * small
            cov = 0.5 - d / (2.0 * soft)
            if cov > 0.0:
                blend(x, y, color, alpha * (1.0 if cov > 1.0 else cov))


def stroke(points, width, color, alpha=1.0):
    """A polyline with round caps and joins, drawn as stamped circles.
    (The stamps go through ellipse(), which applies the scene zoom.)"""
    r = width / 2.0
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        steps = max(1, int(max(abs(bx - ax), abs(by - ay))))
        for i in range(steps + 1):
            t = i / steps
            ellipse(ax + (bx - ax) * t, ay + (by - ay) * t, r, r, color,
                    alpha=alpha, soft=1.0)


def sparkle(cx, cy, r, color, alpha=0.9):
    """A four-point sparkle: two slim crossed ellipses and a bright core."""
    ellipse(cx, cy, r, r * 0.22, color, alpha=alpha)
    ellipse(cx, cy, r * 0.22, r, color, alpha=alpha)
    ellipse(cx, cy, r * 0.30, r * 0.30, color, alpha=alpha)


def flower(cx, cy, petal, center):
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        ellipse(cx + 13 * math.cos(a), cy + 13 * math.sin(a), 11, 11, petal)
    ellipse(cx, cy, 7, 7, center)


# ---------------------------------------------------------------- scene
def background():
    """A quiet vertical wash, pale rose at the top to warm cream below,
    with a soft light pooled behind the bunny."""
    top = (255, 222, 233)
    bottom = (255, 240, 218)
    gx, gy = 480.0, 430.0
    for y in range(H):
        t = y / (H - 1)
        r = top[0] + (bottom[0] - top[0]) * t
        g = top[1] + (bottom[1] - top[1]) * t
        b = top[2] + (bottom[2] - top[2]) * t
        row = y * W * 3
        for x in range(W):
            dx = (x - gx) / 560.0
            dy = (y - gy) / 560.0
            glow = max(0.0, 1.0 - (dx * dx + dy * dy))
            glow *= glow * 26.0
            i = row + x * 3
            buf[i] = min(255, int(r + glow + 0.5))
            buf[i + 1] = min(255, int(g + glow + 0.5))
            buf[i + 2] = min(255, int(b + glow + 0.5))
    # layered halo so the subject lifts off the wash
    ellipse(480, 470, 330, 320, WHITE, alpha=0.16, soft=60)
    ellipse(480, 470, 265, 255, WHITE, alpha=0.20, soft=50)
    ellipse(480, 470, 205, 198, WHITE, alpha=0.22, soft=40)


def ground_shadow():
    ellipse(480, 818, 238, 34, (216, 150, 116), alpha=0.26, soft=22)
    ellipse(480, 816, 168, 24, (198, 128, 96), alpha=0.22, soft=16)


def strawberry(cx, cy):
    """A plump strawberry centred on (cx, cy), drawn as a tapered body
    (width narrows towards the tip) with seeds, leaves and a stem."""
    top, height, halfw = cy - 58, 118, 60
    # body, one scanline band at a time so the sides can taper: rounded
    # shoulders, a gentle bulge, then a smooth run down to the tip
    for i in range(height):
        t = i / (height - 1)          # 0 at the top, 1 at the tip
        wdt = halfw * (0.88 + 0.12 * math.sin(math.pi * min(1.0, t * 1.6)))
        wdt *= 1.0 - 0.90 * (max(0.0, (t - 0.30) / 0.70) ** 1.7)
        y = top + i
        ellipse(cx, y, max(2.0, wdt), 1.6, BERRY, soft=1.0)
    # gentle shading low on the right, a shine high on the left
    ellipse(cx + 26, cy + 26, 30, 40, BERRY_DEEP, alpha=0.35, soft=16)
    ellipse(cx - 24, cy - 22, 15, 24, WHITE, alpha=0.35, soft=8)
    # seeds in staggered rows
    rows = ((-34, (-26, 0, 26)), (-14, (-38, -13, 13, 38)), (8, (-30, 0, 30)),
            (30, (-22, 8)), (50, (-10,)))
    for dy, offs in rows:
        for dx in offs:
            ellipse(cx + dx, cy + dy, 3.4, 5.2, SEED, rot=0.15, alpha=0.95, soft=0.8)
    # leafy cap and stem
    for a, ln in ((-0.9, 34), (-0.3, 40), (0.3, 40), (0.9, 34)):
        ellipse(cx + 30 * math.sin(a), top + 4 - 6 * math.cos(a), 9, ln / 2,
                LEAF, rot=a, soft=1.2)
    ellipse(cx, top - 12, 5, 12, LEAF_DEEP, rot=0.15, soft=1.0)


def bunny():
    # ---- body and feet (no tilt: the body stays planted)
    ellipse(480, 688, 182, 150, CREAM)                            # chubby body
    ellipse(480, 748, 168, 92, SHADE, alpha=0.38, soft=26)        # grounding shade
    ellipse(480, 716, 118, 100, CREAM_LIGHT, alpha=0.95, soft=10)  # belly
    for fx, rot in ((388, -0.18), (572, 0.18)):                   # feet forward
        ellipse(fx, 800, 66, 31, CREAM, rot=rot)
        ellipse(fx, 796, 27, 15, PINK, rot=rot, alpha=0.9)        # paw pads
    # ---- arms reaching in to hold the berry, shaded so they read
    arm = (250, 234, 206)
    ellipse(388, 694, 63, 28, SHADE, rot=0.62, alpha=0.55, soft=6)
    ellipse(572, 694, 63, 28, SHADE, rot=-0.62, alpha=0.55, soft=6)
    ellipse(388, 690, 60, 25, arm, rot=0.62)
    ellipse(572, 690, 60, 25, arm, rot=-0.62)
    strawberry(480, 706)
    ellipse(416, 716, 22, 15, CREAM, rot=0.5)                     # paws over the berry
    ellipse(544, 716, 22, 15, CREAM, rot=-0.5)

    # ---- head group, tilted a few degrees for charm
    tilt = -0.11
    hx, hy = 480.0, 408.0

    def head_ellipse(cx, cy, rx, ry, color, rot=0.0, alpha=1.0, soft=1.2):
        dx, dy = cx - hx, cy - hy
        cr, sr = math.cos(tilt), math.sin(tilt)
        ellipse(hx + dx * cr - dy * sr, hy + dx * sr + dy * cr,
                rx, ry, color, rot=rot + tilt, alpha=alpha, soft=soft)

    # ears: the left one tall; the right one is a lop ear (drawn over the
    # cheek below, once the head is down)
    head_ellipse(392, 196, 45, 118, CREAM, rot=-0.16)
    head_ellipse(392, 208, 23, 80, PINK, rot=-0.16, alpha=0.95)
    # head
    head_ellipse(480, 408, 170, 162, CREAM)
    head_ellipse(480, 470, 128, 92, CREAM_LIGHT, alpha=0.55, soft=24)  # muzzle glow
    # the flopped ear, draped down the right cheek
    head_ellipse(624, 318, 40, 98, CREAM, rot=0.40)
    head_ellipse(628, 326, 19, 64, PINK, rot=0.40, alpha=0.95)
    # blush
    head_ellipse(362, 474, 32, 17, BLUSH, alpha=0.50, soft=7)
    head_ellipse(598, 474, 32, 17, BLUSH, alpha=0.50, soft=7)
    # eyes: big, glossy, with a large and a small highlight
    for ex in (408, 552):
        head_ellipse(ex, 424, 22, 29, EYE)
        head_ellipse(ex - 7, 414, 8.5, 8.5, WHITE)
        head_ellipse(ex + 7, 436, 4, 4, WHITE, alpha=0.95)
    # tiny lashes
    head_ellipse(384, 398, 10, 4, EYE, rot=-0.7)
    head_ellipse(576, 398, 10, 4, EYE, rot=0.7)
    # nose and a bunny mouth
    head_ellipse(480, 472, 13, 9, NOSE)
    head_ellipse(476, 469, 4.5, 3, WHITE, alpha=0.7)
    pts = [(466, 486), (473, 494), (480, 487), (487, 494), (494, 486)]
    cr, sr = math.cos(tilt), math.sin(tilt)
    pts = [(hx + (x - hx) * cr - (y - hy) * sr, hy + (x - hx) * sr + (y - hy) * cr)
           for x, y in pts]
    stroke(pts, 5, MOUTH)
    # freckle dots on the cheeks
    for fx, fy in ((352, 452), (340, 464), (608, 452), (620, 464)):
        head_ellipse(fx, fy, 3, 3, (232, 180, 143), alpha=0.8)
    # a tiny bow beside the tall ear
    bx, by = 330, 268
    head_ellipse(bx - 20, by, 25, 15, PINK_DEEP, rot=0.5)
    head_ellipse(bx + 20, by, 25, 15, PINK_DEEP, rot=-0.5)
    head_ellipse(bx, by, 10.5, 10.5, (255, 105, 140))
    head_ellipse(bx - 3, by - 3, 3.5, 3.5, WHITE, alpha=0.65)


def dressing():
    sparkle(196, 268, 21, SPARK, alpha=0.85)
    sparkle(772, 216, 16, SPARK, alpha=0.8)
    sparkle(806, 520, 13, WHITE, alpha=0.75)
    sparkle(150, 520, 12, WHITE, alpha=0.7)
    flower(140, 836, PINK, (255, 214, 110))
    flower(828, 852, WHITE, (255, 170, 190))
    flower(874, 800, (255, 214, 224), (255, 214, 110))


# ---------------------------------------------------------------- png out
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]

    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as fh:
        fh.write(png)
    return len(png)


def main():
    global S
    background()
    S = 1.07  # from here on, draw the scene a touch larger
    ground_shadow()
    bunny()
    dressing()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    size = write_png(os.path.join(out_dir, 'entry.png'))
    print('wrote entry.png: %dx%d, %d bytes' % (W, H, size))


if __name__ == '__main__':
    main()
