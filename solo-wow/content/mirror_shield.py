"""The Mirror Shield's skin: the High Warlord's Shield Wall's (Item\\ObjectComponents\\Shield\\
Shield_PVPHorde_A_01.blp) with its orange field turned royal blue and its silver - the emblem, the
plate icons, the studs - turned gold; the steel frames stay as they are.

    python3 mirror_shield.py Shield_PVPHorde_A_01.blp out.png        (a preview)
"""
import colorsys
import sys


def recolor(image):
    image = image.convert('RGB')
    px = image.load()
    w, h = image.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            hh, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            deg = hh * 360
            if v < 0.16:
                continue
            if (deg < 45 or deg > 345) and s > 0.45:           # the orange field: royal blue
                nh, ns, nv = 222 / 360.0, 0.8, v * 0.85
            elif 190 <= deg <= 270 and s < 0.45:               # the steel frames stay
                continue
            elif s < 0.3 and v > 0.45:                         # silver: gold
                nh, ns, nv = 45 / 360.0, max(0.25, 0.7 - 0.5 * v * v), min(1.0, v * 1.02)
            else:
                continue
            nr, ng, nb = colorsys.hsv_to_rgb(nh, ns, nv)
            px[x, y] = (int(nr * 255 + 0.5), int(ng * 255 + 0.5), int(nb * 255 + 0.5))
    return image


def build(source_blp_bytes):
    import io
    import os
    from PIL import Image
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import shards
    return shards.blp_raw1(recolor(Image.open(io.BytesIO(source_blp_bytes))))


if __name__ == '__main__':
    from PIL import Image
    img = recolor(Image.open(sys.argv[1]))
    img.save(sys.argv[2])
    img.resize((512, 512)).save(sys.argv[2].replace('.png', '_big.png'))
