"""Draw Preview/icon.png: a striped sunset over the ocean, under a Miami night sky.

Pure Python, no dependency:
    python tools/generate-icon.py
"""
import math
import pathlib
import struct
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'Preview' / 'icon.png'

SIZE = 128
SAMPLES = 4  # supersampling per axis, for smooth edges

SKY_TOP = (0x12, 0x14, 0x2B)
SKY_HORIZON = (0x6B, 0x2A, 0x7A)
SUN_TOP = (0xFF, 0xD4, 0x79)
SUN_MIDDLE = (0xFF, 0x8A, 0x3D)
SUN_BOTTOM = (0xFF, 0x4F, 0x9A)
OCEAN = (0x0B, 0x3F, 0x55)
OCEAN_LINE = (0x2E, 0xE6, 0xD6)
PALM = (0x0A, 0x0C, 0x1C)

HORIZON = 0.66
SUN_CENTER = (0.5, 0.58)
SUN_RADIUS = 0.33
RADIUS = 0.2  # corner radius of the tile


def mix(a, b, t):
    t = min(1.0, max(0.0, t))
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def inside_rounded_square(x, y):
    dx = max(abs(x - 0.5) - (0.5 - RADIUS), 0.0)
    dy = max(abs(y - 0.5) - (0.5 - RADIUS), 0.0)
    return dx * dx + dy * dy <= RADIUS * RADIUS


def in_palm(x, y):
    """A palm tree on the left: a leaning trunk and a few leaves."""
    # Trunk: a slightly curved band from the bottom up to the crown
    crown = (0.27, 0.30)
    if 0.30 <= y <= 1.0:
        t = (y - crown[1]) / (1.0 - crown[1])
        center = crown[0] - 0.10 * t + 0.04 * t * t
        if abs(x - center) <= 0.018 + 0.012 * t:
            return True
    # Leaves: thin arcs radiating from the crown
    for angle, length in ((-160, 0.20), (-125, 0.17), (-60, 0.18), (-20, 0.21), (15, 0.16), (165, 0.14)):
        a = math.radians(angle)
        for i in range(24):
            s = i / 23
            px = crown[0] + math.cos(a) * length * s
            py = crown[1] + math.sin(a) * length * s + 0.10 * s * s
            if (x - px) ** 2 + (y - py) ** 2 <= (0.022 * (1 - s) + 0.006) ** 2:
                return True
    return False


def color_at(x, y):
    if not inside_rounded_square(x, y):
        return None
    if in_palm(x, y):
        return PALM

    if y < HORIZON:
        color = mix(SKY_TOP, SKY_HORIZON, (y / HORIZON) ** 1.6)
        sx, sy = SUN_CENTER
        if (x - sx) ** 2 + (y - sy) ** 2 <= SUN_RADIUS ** 2:
            t = (y - (sy - SUN_RADIUS)) / (HORIZON - (sy - SUN_RADIUS))
            # Retro stripes cut the lower half of the sun, wider near the horizon
            if t > 0.45:
                band = (t - 0.45) / 0.55
                period = 0.075
                phase = ((HORIZON - y) % period) / period
                if phase < 0.15 + 0.35 * band:
                    return color
            return mix(SUN_TOP, SUN_MIDDLE, t * 1.6) if t < 0.62 else mix(SUN_MIDDLE, SUN_BOTTOM, (t - 0.62) / 0.38)
        return color

    # Ocean with the sun reflected as glowing lines
    color = OCEAN
    depth = (y - HORIZON) / (1 - HORIZON)
    for i, row in enumerate((0.03, 0.09, 0.17, 0.27)):
        if abs(depth - row) < 0.018:
            half = 0.26 - 0.05 * i
            if abs(x - 0.5) < half:
                return mix(OCEAN_LINE, SUN_BOTTOM, i / 3)
    return color


def render():
    rows = []
    for py in range(SIZE):
        row = bytearray([0])
        for px in range(SIZE):
            r = g = b = a = 0.0
            for sy in range(SAMPLES):
                for sx in range(SAMPLES):
                    c = color_at((px + (sx + 0.5) / SAMPLES) / SIZE, (py + (sy + 0.5) / SAMPLES) / SIZE)
                    if c:
                        r += c[0]
                        g += c[1]
                        b += c[2]
                        a += 1
            if a:
                row += bytes((round(r / a), round(g / a), round(b / a), round(255 * a / SAMPLES ** 2)))
            else:
                row += bytes(4)
        rows.append(bytes(row))
    return b''.join(rows)


def png(width, height, rgba):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(rgba, 9)) + chunk(b'IEND', b'')


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_bytes(png(SIZE, SIZE, render()))
    print(f'{OUTPUT.relative_to(ROOT)} generated')


if __name__ == '__main__':
    main()
