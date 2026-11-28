"""Zelda of Warcraft: the Crystal Shards screen (the 9 menu's page before Main Menu): its art, rendered
from the credits' concept art in the player's own interface.MPQ, and the layout the ZeldaControls addon
places it by (shardsdata.lua). Layout F1: the dungeon shards round a stone ring, the raids a hexagon
round Naxxramas over Night's Hollow, Tol Barad behind, carved Gargoyle, Drake, Troll and Naga corners."""
import sys, os, io, math, random, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shards import SHARDS
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def stone(w, h, seed=3, base=(92, 98, 84)):
    """A worn stone slab, Ocarina of Time's subscreen grey-green."""
    rnd = random.Random(seed)
    im = Image.new('RGB', (w, h), base)
    small = Image.new('L', (w // 8 + 1, h // 8 + 1))
    small.putdata([rnd.randint(0, 255) for _ in range(small.size[0] * small.size[1])])
    n1 = small.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
    small2 = Image.new('L', (w // 2 + 1, h // 2 + 1))
    small2.putdata([rnd.randint(0, 255) for _ in range(small2.size[0] * small2.size[1])])
    n2 = small2.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1))
    px = im.load(); a = n1.load(); b = n2.load()
    for y in range(h):
        for x in range(w):
            k = 0.78 + 0.32 * (a[x, y] / 255) + 0.12 * (b[x, y] / 255 - 0.5)
            px[x, y] = tuple(int(min(255, c * k)) for c in base)
    return im

SHAPE = [(0.50, 0.00), (0.80, 0.22), (0.72, 0.78), (0.50, 1.00), (0.28, 0.80), (0.20, 0.24)]   # a crystal shard
FACETS = [((0.50, 0.00), (0.80, 0.22), (0.52, 0.40), 1.00), ((0.50, 0.00), (0.52, 0.40), (0.20, 0.24), 0.80),
          ((0.20, 0.24), (0.52, 0.40), (0.50, 1.00), (0.28, 0.80), 0.55), ((0.80, 0.22), (0.72, 0.78), (0.50, 1.00), (0.52, 0.40), 0.72)]

def pts(poly, x, y, w, h):
    return [(x + px * w, y + py * h) for px, py in poly]

# shapes: (outline, facets (polygon..., shade), width share of the height, highlight line)
SHAPES = {
    'shard': (SHAPE, FACETS, 0.62, [(0.5, 0.04), (0.52, 0.38)]),
    # a cut gem seen from above: a hexagon, its flat table in the middle, six facets round it
    'gem': ([(0.5, 0.0), (0.93, 0.25), (0.93, 0.75), (0.5, 1.0), (0.07, 0.75), (0.07, 0.25)],
            [((0.5, 0.0), (0.93, 0.25), (0.72, 0.37), (0.5, 0.25), 1.0), ((0.93, 0.25), (0.93, 0.75), (0.72, 0.63), (0.72, 0.37), 0.78),
             ((0.93, 0.75), (0.5, 1.0), (0.5, 0.75), (0.72, 0.63), 0.55), ((0.5, 1.0), (0.07, 0.75), (0.28, 0.63), (0.5, 0.75), 0.5),
             ((0.07, 0.75), (0.07, 0.25), (0.28, 0.37), (0.28, 0.63), 0.66), ((0.07, 0.25), (0.5, 0.0), (0.5, 0.25), (0.28, 0.37), 0.92),
             ((0.5, 0.25), (0.72, 0.37), (0.72, 0.63), (0.5, 0.75), (0.28, 0.63), (0.28, 0.37), 0.84)],
            0.9, [(0.32, 0.3), (0.5, 0.2)]),
    # a diamond: four facets meeting at a ridge
    'diamond': ([(0.5, 0.0), (1.0, 0.42), (0.5, 1.0), (0.0, 0.42)],
                [((0.5, 0.0), (1.0, 0.42), (0.5, 0.42), 1.0), ((0.5, 0.0), (0.5, 0.42), (0.0, 0.42), 0.82),
                 ((0.0, 0.42), (0.5, 0.42), (0.5, 1.0), 0.55), ((0.5, 0.42), (1.0, 0.42), (0.5, 1.0), 0.7)],
                0.82, [(0.5, 0.05), (0.5, 0.4)]),
    # a double-ended prism, wide in the middle
    'prism': ([(0.5, 0.0), (0.9, 0.3), (0.9, 0.7), (0.5, 1.0), (0.1, 0.7), (0.1, 0.3)],
              [((0.5, 0.0), (0.9, 0.3), (0.5, 0.3), 1.0), ((0.5, 0.0), (0.5, 0.3), (0.1, 0.3), 0.82),
               ((0.1, 0.3), (0.5, 0.3), (0.5, 0.7), (0.1, 0.7), 0.66), ((0.5, 0.3), (0.9, 0.3), (0.9, 0.7), (0.5, 0.7), 0.88),
               ((0.1, 0.7), (0.5, 0.7), (0.5, 1.0), 0.5), ((0.5, 0.7), (0.9, 0.7), (0.5, 1.0), 0.62)],
              0.7, [(0.5, 0.04), (0.5, 0.3)]),
}


def crystal(size, hsv, shape='shard'):
    outline, facets, share, hl = SHAPES[shape]
    w, h = int(size * share), size
    S = 4
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r, g, b = colorsys.hsv_to_rgb(hsv[0] / 360, hsv[1], hsv[2])
    for f in facets:
        k = f[-1]
        col = tuple(int(255 * min(1, c * k + 0.25 * k * k)) for c in (r, g, b)) + (255,)
        d.polygon(pts(f[:-1], 0, 0, w * S, h * S), fill=col)
    d.line(pts(outline + [outline[0]], 0, 0, w * S, h * S), fill=(255, 255, 255, 200), width=S)
    d.line(pts(hl, 0, 0, w * S, h * S), fill=(255, 255, 255, 230), width=2 * S)
    im = im.resize((w, h), Image.LANCZOS)
    gm = im.split()[3].resize((w, h))
    gl = Image.new('RGBA', (w + 24, h + 24), (int(r * 255), int(g * 255), int(b * 255), 0))
    a = Image.new('L', (w + 24, h + 24), 0); a.paste(gm, (12, 12)); a = a.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.7))
    gl.putalpha(a); gl.alpha_composite(im, (12, 12))
    return gl

def hole(size, shape='shard'):
    """The shard's empty socket: its shape cut into the stone, shadowed at the top, lit at the bottom."""
    outline, _, share, _ = SHAPES[shape]
    w, h = int(size * share), size
    S = 4
    mask = Image.new('L', (w * S, h * S), 0); ImageDraw.Draw(mask).polygon(pts(outline, 0, 0, w * S, h * S), fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    pad = 12
    out = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', out.size, 0); m.paste(mask, (pad, pad))
    dark = Image.new('RGBA', out.size, (28, 30, 24, 255)); dark.putalpha(m.point(lambda v: int(v * 0.85)))
    # inner shadow from the top-left, a light rim at the bottom-right
    sh = Image.new('L', out.size, 0); sh.paste(mask, (pad + 3, pad + 4))
    inner = ImageChops.subtract(m, sh).filter(ImageFilter.GaussianBlur(1.2))
    lit = Image.new('L', out.size, 0); lit.paste(mask, (pad - 2, pad - 2))
    rim = ImageChops.subtract(m, lit).filter(ImageFilter.GaussianBlur(0.8))
    out.alpha_composite(dark)
    s2 = Image.new('RGBA', out.size, (0, 0, 0, 0)); s2.putalpha(inner.point(lambda v: int(v * 0.9))); out.alpha_composite(s2)
    r2 = Image.new('RGBA', out.size, (190, 200, 170, 0)); r2.putalpha(rim.point(lambda v: int(v * 0.8))); out.alpha_composite(r2)
    return out

def panel(w, h, title, owned_n, total):
    im = stone(w, h).convert('RGBA')
    d = ImageDraw.Draw(im)
    # bevelled frame
    for i in range(10):
        c = int(150 - i * 9)
        d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=(c, c + 6, c - 10))
    d.rectangle([12, 12, w - 13, h - 13], outline=(40, 44, 36), width=2)
    f = ImageFont.truetype(FB, 30)
    tw = d.textlength(title, font=f)
    d.text(((w - tw) / 2 + 2, 26), title, font=f, fill=(20, 22, 18))
    d.text(((w - tw) / 2, 24), title, font=f, fill=(236, 220, 150))
    if not STATIC:
        f2 = ImageFont.truetype(FR, 20)
        t = '%d / %d' % (owned_n, total)
        d.text(((w - d.textlength(t, font=f2)) / 2, h - 40), t, font=f2, fill=(236, 220, 150))
    return im

def carve(im, box, radius=0):
    """A recessed panel area."""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=radius, fill=(66, 70, 60), outline=(42, 46, 38), width=2)
    d.line([(x0 + 2, y1 - 1), (x1 - 1, y1 - 1), (x1 - 1, y0 + 2)], fill=(140, 148, 126), width=2)

def place(im, spr, cx, cy):
    im.alpha_composite(spr, (int(cx - spr.size[0] / 2), int(cy - spr.size[1] / 2)))

def label(im, text, cx, y, size=11, col=(225, 215, 170)):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FR, size)
    tw = d.textlength(text, font=f)
    d.text((cx - tw / 2 + 1, y + 1), text, font=f, fill=(15, 15, 12)); d.text((cx - tw / 2, y), text, font=f, fill=col)

SHORT = {'Shadowfang Keep': 'Shadowfang', 'Blackfathom Deeps': 'Blackfathom', 'Blackrock Depths': 'BR Depths',
         'Blackrock Spire': 'BR Spire', 'Ragefire Chasm': 'Ragefire', 'Wailing Caverns': 'Wailing Cav.',
         'Dire Maul North': 'DM North', 'Dire Maul East': 'DM East', 'Dire Maul West': 'DM West', 'Scarlet Monastery Graveyard': 'SM Graveyard', 'Scarlet Monastery Armory': 'SM Armory',
         'Scarlet Monastery Cathedral': 'SM Cathedral', 'Scarlet Monastery Library': 'SM Library',
         'Stormwind Stockade': 'Stockade', "Temple of Ahn'Qiraj": "Temple of AQ", "Ruins of Ahn'Qiraj": 'Ruins of AQ'}

# ------------------------------------------------------------------ the screen
BACKDROP_ALPHA = 105
MIRROR = set()
SHADE = True
RAID_SHAPE = 'prism'       # the raids' crystals: shard, gem, diamond or prism (Naxxramas: CENTRE_SHAPE)
CENTRE_SHAPE = 'gem'
EDGE_COLOURS = 'blend'     # the hexagon's lines: rainbow, own (the raid's colour), or blend (into the next raid's)
from PIL import ImageEnhance, ImageOps
D = [s for s in SHARDS if not s[4]]; R = [s for s in SHARDS if s[4]]
OWNED = set()
ARTS = {}                     # credits art by name, assembled from its 256-pixel tiles (load_credits)
STATIC = False                # the background alone: every slot empty, every line dark, no count


def load_credits(interface_mpq):
    """The credits' concept art (Interface\\Glues\\Credits), each picture laid out from its tiles the way
    CreditsFrame.lua's CreditsArtInfo does: rows of up to four 256-pixel tiles, two rows."""
    import re
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
    import mpq
    a = mpq.Archive(interface_mpq)
    lua = a.read('Interface\\GlueXML\\CreditsFrame.lua').decode('latin1')
    for name, w, h in re.findall(r'CreditsArtInfo\[\d+\] = \{ file="(\w+)", w=(\d+), h=(\d+)', lua):
        w, h = int(w), int(h)
        canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0)); idx = 1
        for i in range(2):
            for j in range(4):
                tw, th = min(256, w - j * 256), min(256, h - i * 256)
                if tw <= 0 or th <= 0:
                    continue
                tile = Image.open(io.BytesIO(a.read('Interface\\Glues\\Credits\\%s%d.blp' % (name, idx)))).convert('RGBA'); idx += 1
                canvas.paste(tile.resize((tw, th)) if tile.size != (tw, th) else tile, (j * 256, i * 256))
        ARTS[name.lower()] = canvas


def art_image(name):
    return ARTS[name.lower()].copy()
def shape_of(s):
    return 'shard' if not s[4] else CENTRE_SHAPE if s is R[6] else RAID_SHAPE


def spr(s, size):
    shape = shape_of(s)
    return crystal(size, s[6], shape) if (s[0] in OWNED and not STATIC) else hole(size, shape)
def edge_colour(k):
    """Raid k's line on to raid k + 1: the rainbow's k-th colour, or blended from its colour to the next's."""
    if EDGE_COLOURS == 'blend':
        return (rgb(R[k][6], 1.0), rgb(R[(k + 1) % 6][6], 1.0))
    if EDGE_COLOURS == 'own':
        return rgb(R[k][6], 1.0)
    return rgb([(0, 1, 1), (30, 1, 1), (58, 1, 1), (120, 0.9, 0.9), (215, 0.9, 1), (275, 0.8, 1)][k])


def rgb(hsv, v=None):
    r, g, b = colorsys.hsv_to_rgb(hsv[0] / 360, hsv[1], v if v is not None else hsv[2]); return (int(r * 255), int(g * 255), int(b * 255))

def seg_line(draw, a, b, col, width, light=False):
    """A line in one colour, or (from, to) shading along it from the one colour to the other."""
    two = isinstance(col[0], (tuple, list))
    steps = 24 if two else 1
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        c = col if not two else tuple(int(col[0][k] + (col[1][k] - col[0][k]) * (t0 + t1) / 2) for k in range(3))
        if light:
            c = tuple(min(255, int(x * 0.4 + 160)) for x in c)
        p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
        p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
        draw.line([p0, p1], fill=tuple(c) + (255,), width=width)


def glow_line(im, a, b, col, lit, width=6):
    """A groove cut in the stone; lit, a glowing line of light in it."""
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line([a, b], fill=(34, 38, 30, 255), width=width + 4)
    d.line([(a[0] + 1, a[1] + 2), (b[0] + 1, b[1] + 2)], fill=(120, 128, 108, 120), width=2)
    im.alpha_composite(lay)
    if lit:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0)); seg_line(ImageDraw.Draw(g), a, b, col, width + 10)
        g = g.filter(ImageFilter.GaussianBlur(7)); im.alpha_composite(g)
        c = Image.new('RGBA', im.size, (0, 0, 0, 0)); dc = ImageDraw.Draw(c)
        seg_line(dc, a, b, col, width)
        seg_line(dc, a, b, col, max(2, width // 3), light=True)
        im.alpha_composite(c)

def art(name, size, alpha, mode='plain'):
    a = art_image(name); a.thumbnail((size, size), Image.LANCZOS)
    if mode == 'carve':     # a relief cut into the stone: the art's light and shade only
        g = ImageOps.grayscale(a).filter(ImageFilter.EMBOSS)
        g = ImageEnhance.Contrast(g).enhance(1.6)
        t = Image.merge('RGBA', (g.point(lambda v: int(v * 0.95)), g, g.point(lambda v: int(v * 0.85)), a.split()[3]))
        a = t
    al = a.split()[3].point(lambda v: int(v * alpha)); a.putalpha(al)
    return a

def screen(deco, middle=None, corners=None, corner_mode='carve', backdrop=None):
    W, H = 840, 860
    im = panel(W, H, 'CRYSTAL SHARDS', len(OWNED), len(SHARDS))
    cx0, cy0 = W / 2, H / 2 + 18
    if backdrop:                  # a credits painting over the slab, inside its frame
        b = art_image(backdrop)
        iw, ih = W - 28, H - 28
        k = max(iw / b.size[0], ih / b.size[1]); b = b.resize((int(b.size[0] * k) + 1, int(b.size[1] * k) + 1), Image.LANCZOS)
        b = b.crop(((b.size[0] - iw) // 2, (b.size[1] - ih) // 2, (b.size[0] - iw) // 2 + iw, (b.size[1] - ih) // 2 + ih))
        flat = Image.new('RGBA', b.size, (20, 20, 20, 255)); flat.alpha_composite(b)
        flat.putalpha(BACKDROP_ALPHA); im.alpha_composite(flat, (14, 14))
        ImageDraw.Draw(im).rectangle([12, 12, W - 13, H - 13], outline=(40, 44, 36), width=2)
        f = ImageFont.truetype(FB, 30); d0 = ImageDraw.Draw(im); t = 'CRYSTAL SHARDS'; tw = d0.textlength(t, font=f)
        d0.text(((W - tw) / 2 + 2, 26), t, font=f, fill=(20, 22, 18)); d0.text(((W - tw) / 2, 24), t, font=f, fill=(236, 220, 150))
        if not STATIC:
            f2 = ImageFont.truetype(FR, 20); t2 = '%d / %d' % (len(OWNED), len(SHARDS))
            d0.text(((W - d0.textlength(t2, font=f2)) / 2 + 1, H - 39), t2, font=f2, fill=(10, 10, 10)); d0.text(((W - d0.textlength(t2, font=f2)) / 2, H - 40), t2, font=f2, fill=(236, 220, 150))
    if deco == 'paint':           # a concept painting faded into the ring's floor
        p = art_image('DragonIsles').resize((640, 430))
        m = Image.new('L', p.size, 0); ImageDraw.Draw(m).ellipse([0, 0, 640, 430], fill=255)
        m = ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(40)), p.split()[3]).point(lambda v: int(v * 0.45))
        p.putalpha(m); im.alpha_composite(p, (int(cx0 - 320), int(cy0 - 215)))
    d = ImageDraw.Draw(im)
    ring = Image.new('RGBA', im.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(ring)
    dr.ellipse([cx0 - 315, cy0 - 315, cx0 + 315, cy0 + 315], fill=(54, 55, 57, 245 if deco != 'paint' else 170), outline=(38, 42, 34, 255), width=4)
    dr.ellipse([cx0 - 205, cy0 - 205, cx0 + 205, cy0 + 205], fill=(82, 88, 74, 245 if deco != 'paint' else 150), outline=(38, 42, 34, 255), width=4)
    im.alpha_composite(ring)
    if SHADE:                     # the ring as a raised band of stone, lit from the upper left
        n = 2
        Wn, Hn = W * n, H * n
        def disc(r, blur=0):
            m = Image.new('L', (Wn, Hn), 0)
            ImageDraw.Draw(m).ellipse([(cx0 - r) * n, (cy0 - r) * n, (cx0 + r) * n, (cy0 + r) * n], fill=255)
            return m.filter(ImageFilter.GaussianBlur(blur * n)) if blur else m
        band = ImageChops.subtract(disc(313), disc(207))
        # a broad slope of light across it
        import numpy as np
        yy, xx = np.mgrid[0:Hn, 0:Wn]
        t = ((xx / n - (cx0 - 313)) + (yy / n - (cy0 - 313))) / (2 * 626)      # 0 at the upper left .. 1 lower right
        grad = Image.fromarray(np.clip(t * 255, 0, 255).astype('uint8'), 'L')
        lit = Image.new('RGBA', (Wn, Hn), (255, 250, 235, 0)); lit.putalpha(ImageChops.multiply(band, grad.point(lambda v: max(0, 140 - v) // 2)))
        dark = Image.new('RGBA', (Wn, Hn), (0, 0, 0, 0)); dark.putalpha(ImageChops.multiply(band, grad.point(lambda v: max(0, v - 120) // 2)))
        # bevels: the band's outer edge catches light at the top left, its inner edge at the bottom right
        def edge(r, dx, dy, blur):
            a = disc(r, blur); b = ImageChops.offset(disc(r, blur), int(dx * n), int(dy * n))
            return ImageChops.subtract(a, b)
        hi = ImageChops.add(edge(313, 5, 5, 2), ImageChops.subtract(ImageChops.offset(disc(207, 2), int(-5 * n), int(-5 * n)), disc(207, 2)))
        lo = ImageChops.add(ImageChops.subtract(ImageChops.offset(disc(313, 2), int(5 * n), int(5 * n)), disc(313, 2)), edge(207, -5, -5, 2))
        hi = ImageChops.multiply(hi, band.filter(ImageFilter.MaxFilter(5)))
        lo = ImageChops.multiply(lo, band.filter(ImageFilter.MaxFilter(5)))
        H1 = Image.new('RGBA', (Wn, Hn), (235, 232, 220, 0)); H1.putalpha(hi.point(lambda v: v * 3 // 5))
        L1 = Image.new('RGBA', (Wn, Hn), (0, 0, 0, 0)); L1.putalpha(lo.point(lambda v: v * 4 // 5))
        shade = Image.new('RGBA', (Wn, Hn), (0, 0, 0, 0))
        for layer in (lit, dark, H1, L1): shade.alpha_composite(layer)
        im.alpha_composite(shade.resize((W, H), Image.LANCZOS))
        # the inner floor sits lower: a shadow cast onto it from the band's upper left
        sh = ImageChops.subtract(disc(207), ImageChops.offset(disc(207), int(7 * n), int(7 * n))).filter(ImageFilter.GaussianBlur(4 * n))
        sh = ImageChops.multiply(sh, disc(207))
        S1 = Image.new('RGBA', (Wn, Hn), (0, 0, 0, 0)); S1.putalpha(sh.point(lambda v: v * 3 // 4))
        im.alpha_composite(S1.resize((W, H), Image.LANCZOS))
    if middle:                    # a credits painting set into the ring's inner floor, its edge fading out
        dia = 410
        p = art_image(middle).resize((dia, dia), Image.LANCZOS)
        m = Image.new('L', (dia, dia), 0); ImageDraw.Draw(m).ellipse([22, 22, dia - 22, dia - 22], fill=255)
        m = ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(16)), p.split()[3]).point(lambda v: int(v * 0.7))
        p.putalpha(m); im.alpha_composite(p, (int(cx0 - dia / 2), int(cy0 - dia / 2)))
    # corners: crests from the credits
    if deco in ('crest', 'paint'):
        for name, (x, y) in (('Acrest', (16, 16)), ('HordeBanner', (W - 196, 16)), ('DwarfCrest', (16, H - 196)), ('OrcShield', (W - 196, H - 196))):
            im.alpha_composite(art(name, 180, 0.8), (x, y))
    if deco == 'carve':
        names = corners or ('tauren_hunter', 'Centaur', 'Orc', 'Tauren')
        for name, corner in zip(names, ('tl', 'tr', 'bl', 'br')):
            # as big as fits in its corner: inside the frame, clear of the ring and the title; the
            # art may sit a little in from the corner when that lets it grow
            clear = {'bl': 319}.get(corner, 326)                 # how far out from the ring's centre it stays
            edge = {'bl': 2}.get(corner, 16)                    # the bottom left right into the frame's corner
            def fits(a, x, y):
                al = a.split()[3].load()
                for py in range(0, a.size[1], 3):
                    for px in range(0, a.size[0], 3):
                        if al[px, py] > 12:
                            gx, gy = x + px, y + py
                            if math.hypot(gx - cx0, gy - cy0) < clear or (gy < 66 and abs(gx - W / 2) < 190) or (gy > H - 52 and abs(gx - W / 2) < 60):
                                return False
                return True
            best = None
            for size in range(440, 60, -8):
                a = art(name, size, 0.75 if corner_mode == 'carve' else 0.9, corner_mode)
                if name in MIRROR: a = ImageOps.mirror(a)
                for dx in range(0, 121, 10):
                    for dy in ((0,) if corner == 'tl' else range(0, 31, 5) if corner == 'tr' else range(0, 61, 10)):
                        x = edge + dx if corner[1] == 'l' else W - edge - dx - a.size[0]
                        y = edge + dy if corner[0] == 't' else H - edge - dy - a.size[1]
                        if fits(a, x, y):
                            best = (a, x, y); break
                    if best: break
                if best: break
            a, x, y = best
            if corner == 'bl':            # its size from the corner, then lifted inside the frame so its feet show
                x, y = 16, H - 18 - a.size[1]
                while not fits(a, x, y):
                    a = a.resize((int(a.size[0] * 0.98), int(a.size[1] * 0.98)), Image.LANCZOS)
                    y = H - 18 - a.size[1]
            k = {'tl': 0.88}.get(corner, 1.0)                     # the top left a little under its most
            if k != 1.0:
                a = a.resize((int(a.size[0] * k), int(a.size[1] * k)), Image.LANCZOS)
            if x < 14 or y < 14 or x + a.size[0] > W - 14 or y + a.size[1] > H - 14:   # clipped to the frame
                l, t = max(0, 14 - x), max(0, 14 - y)
                r, b2 = a.size[0] - max(0, x + a.size[0] - (W - 14)), a.size[1] - max(0, y + a.size[1] - (H - 14))
                a = a.crop((l, t, r, b2)); x += l; y += t
            im.alpha_composite(a, (x, y))
        # small race crests between the dungeon shards and the raids
    # the dungeons round the ring
    for i, s in enumerate(D):
        a = math.radians(-90 + 360 * i / len(D))
        place(im, spr(s, 54), cx0 + 262 * math.cos(a), cy0 + 262 * math.sin(a))
    # the raids: a hexagon round Naxxramas; an owned raid lights the line on to the next (rainbow) and
    # its line in to Naxxramas (its own colour)
    hexp = [(cx0 + 140 * math.cos(math.radians(-90 + 60 * k)), cy0 + 140 * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    rainbow = [(0, 1, 1), (30, 1, 1), (58, 1, 1), (120, 0.9, 0.9), (215, 0.9, 1), (275, 0.8, 1)]
    for k in range(6):
        glow_line(im, hexp[k], (cx0, cy0), rgb(R[k][6], 1.0), R[k][0] in OWNED and not STATIC, 5)
    for k in range(6):
        glow_line(im, hexp[k], hexp[(k + 1) % 6], edge_colour(k), R[k][0] in OWNED and not STATIC, 6)
    for k in range(6): place(im, spr(R[k], 64), *hexp[k])
    place(im, spr(R[6], 80), cx0, cy0)
    return im



# ------------------------------------------------------------------ the game's files
W, H = 840, 860
CX, CY = W / 2, H / 2 + 18
RAINBOW = [(0, 1, 1), (30, 1, 1), (58, 1, 1), (120, 0.9, 0.9), (215, 0.9, 1), (275, 0.8, 1)]
DIR = 'Interface\\Zelda\\Shards\\'
LAYOUT = dict(middle='NightsHollow', corners=('gargoyle', 'drake', 'Troll', 'Naga'), backdrop='tolbarad')


def slots():
    """(shard, centre x, centre y, crystal size) of every slot, in the 840 x 860 screen."""
    out = []
    for i, s_ in enumerate(D):
        a = math.radians(-90 + 360 * i / len(D))
        out.append((s_, CX + 262 * math.cos(a), CY + 262 * math.sin(a), 54))
    hexp = hex_points()
    for k in range(6):
        out.append((R[k], hexp[k][0], hexp[k][1], 64))
    out.append((R[6], CX, CY, 80))
    return out


def hex_points():
    return [(CX + 140 * math.cos(math.radians(-90 + 60 * k)), CY + 140 * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]


def lit_line(a, b, col, width):
    """A raid's line of light alone, on clear ground, the raid slots cut out of it (their stones sit
    over it): the overlay a lit line is, over the background's dark groove."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); seg_line(ImageDraw.Draw(g), a, b, col, width + 10)
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(7)))
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(c)
    seg_line(dc, a, b, col, width)
    seg_line(dc, a, b, col, max(2, width // 3), light=True)
    im.alpha_composite(c)
    cut = Image.new('L', (W, H), 255); dcut = ImageDraw.Draw(cut)
    for (x, y), size, shape in [(p, 64, RAID_SHAPE) for p in hex_points()] + [((CX, CY), 80, CENTRE_SHAPE)]:
        outline, _, share, _ = SHAPES[shape]                     # the stone's own outline, a little in
        w_, h_ = size * share * 0.86, size * 0.86
        dcut.polygon([(x - w_ / 2 + px * w_, y - h_ / 2 + py * h_) for px, py in outline], fill=0)
    im.putalpha(ImageChops.multiply(im.split()[3], cut.filter(ImageFilter.GaussianBlur(2))))
    return im


def boxed(im, cx=None, cy=None):
    """The art's non-clear part in a power-of-two box: (image, left, top), screen pixels. Centred on
    (cx, cy) when given."""
    bbox = im.getbbox()
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if cx is not None:
        w = 2 * max(cx - bbox[0], bbox[2] - cx); h = 2 * max(cy - bbox[1], bbox[3] - cy)
    side = 1
    while side < max(w, h):
        side *= 2
    if cx is None:
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    left, top = int(round(cx - side / 2)), int(round(cy - side / 2))
    box = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    box.alpha_composite(im.crop((max(0, left), max(0, top), min(W, left + side), min(H, top + side))),
                        (max(0, -left), max(0, -top)))
    return box, left, top


def build(interface_mpq):
    """{MPQ path: BLP} for the screen, and shardsdata.lua for the addon."""
    import scarlet_horse
    global STATIC, OWNED
    load_credits(interface_mpq)
    STATIC, OWNED = True, set()
    bg = screen('carve', LAYOUT['middle'], LAYOUT['corners'], 'carve', LAYOUT['backdrop'])
    STATIC = False
    canvas = Image.new('RGB', (1024, 1024), (0, 0, 0)); canvas.paste(bg.convert('RGB'), (0, 0))
    files = {DIR + 'Background.blp': scarlet_horse.blp_raw1_alpha(canvas.convert('RGBA'))}
    lua = ['-- Zelda of Warcraft: the Crystal Shards screen\'s layout (generated by shard_screen.py).',
           '-- Screen pixels of the ' + '%dx%d' % (W, H) + ' picture; Background.blp holds it at its top left.',
           'ZeldaShardScreen = { width = %d, height = %d, texture = 1024, slots = {' % (W, H)]
    for s_, x, y, size in slots():
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); place(lay, crystal(size, s_[6], shape_of(s_)), x, y)
        box, left, top = boxed(lay, x, y)
        name = DIR + 'Crystal%d.blp' % (s_[0] - SHARDS[0][0])
        files[name] = scarlet_horse.blp_raw1_alpha(box)
        lua.append('  { item = %d, name = "%s", raid = %s, x = %.1f, y = %.1f, r = %d, tex = "%s", left = %d, top = %d, size = %d },'
                   % (s_[0], s_[3].replace('"', '\\"'), 'true' if s_[4] else 'false', x, y, size // 2,
                      name[:-4].replace('\\', '\\\\'), left, top, box.size[0]))
    lua.append('}, lines = {')
    hexp = hex_points()
    for k in range(6):
        for kind, a, b, col, width in (('Spoke', hexp[k], (CX, CY), rgb(R[k][6], 1.0), 5),
                                       ('Edge', hexp[k], hexp[(k + 1) % 6], edge_colour(k), 6)):
            box, left, top = boxed(lit_line(a, b, col, width))
            name = DIR + '%s%d.blp' % (kind, k)
            files[name] = scarlet_horse.blp_raw1_alpha(box)
            lua.append('  { item = %d, tex = "%s", left = %d, top = %d, size = %d },'
                       % (R[k][0], name[:-4].replace('\\', '\\\\'), left, top, box.size[0]))
    lua.append('} }')
    return files, '\n'.join(lua) + '\n', bg


if __name__ == '__main__':
    # shard_screen.py <interface.MPQ> <patch-Z in> <patch-Z out> <shardsdata.lua out>
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
    import mpq
    files, lua, bg = build(sys.argv[1])
    a = mpq.Archive(sys.argv[2])
    names = [n for n in a.read('(listfile)').decode().split('\r\n') if n]
    out = {n: a.read(n) for n in names}
    out.update(files)
    mpq.write_archive(sys.argv[3], out)
    b = mpq.Archive(sys.argv[3])
    for n, v in out.items():
        assert b.read(n) == v, n
    open(sys.argv[4], 'w').write(lua)
    print('ok', len(names), '->', len(out), os.path.getsize(sys.argv[3]))
