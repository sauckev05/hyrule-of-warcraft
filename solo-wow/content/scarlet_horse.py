"""The Scarlet Warhorse's skin: the paladin warhorse's (Creature\\WarHorse\\WarHorse.blp) recoloured to
the level 40 set's colours - the blue barding crimson, the silver plates and ornaments gold.

    python3 scarlet_horse.py WarHorse.blp out.png        (a preview)
"""
import colorsys
import sys

# the barding plates and ornaments, in the 256x256 texture: boxes the silver may be recoloured in
# (the coat around them is the same grey, so the colour alone can't tell them apart)
METAL_BOXES = [
    (15, 0, 75, 63),        # the shoulder plate, top left
    (155, 37, 223, 85),     # the crupper plates, right
    (202, 72, 240, 125),
    (70, 8, 170, 42),       # the saddle's studs
    (30, 60, 212, 140),     # the ornaments and studs on the barding
    (50, 142, 163, 223),    # the leg plates
    (160, 147, 228, 222),   # the face plate
    (200, 172, 250, 222),
    (105, 222, 168, 256),   # the hoof plate
]


def _in_metal(x, y):
    return any(x0 <= x < x1 and y0 <= y < y1 for x0, y0, x1, y1 in METAL_BOXES)


def recolor(image):
    """RGBA in, RGBA out."""
    image = image.convert('RGBA')
    px = image.load()
    w, h = image.size
    sx, sy = 256.0 / w, 256.0 / h
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            hh, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            deg = hh * 360
            if 165 <= deg <= 250 and s > 0.22:
                # the blue cloth: crimson
                nh, ns, nv = 352 / 360.0, min(1.0, s * 1.1 + 0.1), min(1.0, v * 1.12)
            elif _in_metal(x * sx, y * sy) and s < 0.3 and (deg >= 58 or s < 0.08) and v > 0.08:
                # silver: gold, the highlights paler as polished gold is
                nh = 42 / 360.0
                ns = max(0.18, 0.78 - 0.55 * v * v)
                nv = min(1.0, v * 1.04)
            elif 15 <= deg <= 45 and s > 0.35 and v < 0.75 and _in_metal(x * sx, y * sy) is False:
                # the leather: a deeper, redder brown
                nh, ns, nv = (deg - 12) / 360.0, min(1.0, s * 1.05), v * 0.85
            else:
                continue
            nr, ng, nb = colorsys.hsv_to_rgb(nh, ns, nv)
            px[x, y] = (int(nr * 255 + 0.5), int(ng * 255 + 0.5), int(nb * 255 + 0.5), a)
    return image


def blp_raw1_alpha(image):
    """A BLP2 with a 256-colour palette (compression 1), 8-bit alpha, and every mip level."""
    import struct
    from PIL import Image
    image = image.convert('RGBA')
    w, h = image.size
    rgb = image.convert('RGB')
    pal_img = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    palette = pal_img.getpalette()[:768]
    palette += [0] * (768 - len(palette))
    levels = []
    lw, lh = w, h
    while True:
        lvl = image.resize((lw, lh), Image.LANCZOS) if (lw, lh) != (w, h) else image
        idx = lvl.convert('RGB').quantize(palette=pal_img, dither=Image.Dither.NONE).tobytes()
        levels.append(idx + lvl.split()[3].tobytes())
        if lw == 1 and lh == 1:
            break
        lw, lh = max(1, lw // 2), max(1, lh // 2)
    header_size = 4 + 4 + 4 + 8 + 64 + 64 + 1024
    offsets, sizes, pos = [], [], header_size
    for data in levels:
        offsets.append(pos)
        sizes.append(len(data))
        pos += len(data)
    offsets += [0] * (16 - len(offsets))
    sizes += [0] * (16 - len(sizes))
    out = bytearray(b'BLP2')
    out += struct.pack('<I', 1)
    out += struct.pack('<BBBB', 1, 8, 0, 1)        # palette, 8-bit alpha, alpha type 0, mips
    out += struct.pack('<II', w, h)
    out += struct.pack('<16I', *offsets)
    out += struct.pack('<16I', *sizes)
    for i in range(256):
        rr, gg, bb = palette[i * 3:i * 3 + 3]
        out += bytes((bb, gg, rr, 0))
    for data in levels:
        out += data
    return bytes(out)


def build(source_blp_bytes):
    import io
    from PIL import Image
    return blp_raw1_alpha(recolor(Image.open(io.BytesIO(source_blp_bytes))))


if __name__ == '__main__':
    from PIL import Image
    img = recolor(Image.open(sys.argv[1]))
    img.save(sys.argv[2])
    Image.alpha_composite(Image.new('RGBA', img.size, (40, 40, 40, 255)), img).convert('RGB').resize((512, 512)).save(sys.argv[2].replace('.png', '_big.png'))
