#!/usr/bin/env python3
"""Zelda of Warcraft - hosiery: sheer pantyhose, lace-top stockings with a garter belt, and sheer
feet, in five colors, for female characters. Writes:

  - patch-Z.MPQ: the textures (BLP2) and an ItemDisplayInfo.dbc with the new looks added, for the
    client's Data folder (the Zelda client and the original 1.12 client both load patch-?.MPQ)
  - zelda-sql/005_hosiery.sql: the items and the boutique that sells them

usage: build_hosiery.py <base ItemDisplayInfo.dbc> <output patch-Z.MPQ>

The body-texture layout (from HumanFemale.m2): in the leg-upper (128x64) and leg-lower (128x64)
regions u=0/127 is the inner leg, u~32 the front, u~64 the outer side and u~96 the back; the foot
region (128x32) runs ankle (v=0) to toes (v~31) with the heel around u~96-104.
"""
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
import mpq  # noqa: E402
from build_content import insert, creature_template  # noqa: E402

DISPLAY_BASE = 60001
ITEM_BASE = 190900
BOUTIQUE = 190660
GUID_BASE = 9102001

COLORS = [
    # key, label, rgb, sheer alpha (0-1), seam
    ('Black', 'Black', (14, 14, 18), 0.62, False),
    ('Smoke', 'Light Black, Back Seam', (24, 22, 26), 0.36, True),
    ('White', 'White', (248, 248, 250), 0.64, False),
    ('Red', 'Red', (172, 12, 28), 0.50, False),
    ('Blue', 'Blue', (26, 48, 168), 0.50, False),
]


# ------------------------------------------------------------------ texture painting
def theta(u):
    """The angle around the leg for column u: 0 front, 90 outer side, 180 back, +-90 inner."""
    return math.radians((u - 32.0) / 32.0 * 90.0)


def silhouette(u):
    """1 at the sides of the leg (where sheer fabric looks densest from the front), 0 at front/back."""
    return abs(math.sin(theta(u)))


def shade(rgb, k):
    return tuple(max(0, min(255, int(round(c * k)))) for c in rgb)


def sheer_px(u, rgb, alpha):
    a = alpha + (1.0 - alpha) * 0.45 * silhouette(u) ** 2
    return rgb + (int(round(min(1.0, a) * 255)),)


def is_seam(u):
    return 95 <= u <= 97


def seam_rgb(rgb):
    return shade(rgb, 0.55) if sum(rgb) > 120 else (6, 6, 8)


def paint_hose_lu(rgb, alpha, seam):
    w, h = 128, 64
    px = []
    for v in range(h):
        for u in range(w):
            if v < 7:                                    # the waistband
                px.append(shade(rgb, 0.85) + (225,))
            elif seam and is_seam(u) and v > 14:
                px.append(seam_rgb(rgb) + (235,))
            else:
                px.append(sheer_px(u, rgb, alpha))
    return w, h, px


def paint_hose_ll(rgb, alpha, seam):
    w, h = 128, 64
    px = []
    for v in range(h):
        for u in range(w):
            if seam and is_seam(u):
                px.append(seam_rgb(rgb) + (235,))
            else:
                px.append(sheer_px(u, rgb, alpha))
    return w, h, px


def paint_hose_fo(rgb, alpha, seam):
    w, h = 128, 32
    px = []
    for v in range(h):
        for u in range(w):
            if seam and is_seam(u) and v < 20:           # the seam runs down the back of the heel
                px.append(seam_rgb(rgb) + (235,))
            elif v >= 23:                                 # reinforced toes
                r, g, b, a = sheer_px(u, rgb, min(0.95, alpha + 0.25))
                px.append(shade(rgb, 0.9) + (a,))
            elif 88 <= u <= 112 and v < 12:               # a slightly reinforced heel
                r, g, b, a = sheer_px(u, rgb, min(0.95, alpha + 0.12))
                px.append((r, g, b, a))
            else:
                px.append(sheer_px(u, rgb, alpha))
    return w, h, px


def paint_stocking_lu(rgb, alpha, seam):
    """Garter belt at the waist, straps down front and back, a lace top band, then the stocking."""
    w, h = 128, 64
    lace = shade(rgb, 0.8) if sum(rgb) > 120 else (8, 8, 10)
    belt = shade(rgb, 0.75) if sum(rgb) > 120 else (10, 10, 12)
    px = []
    for v in range(h):
        for u in range(w):
            if v < 8:                                     # the garter belt, a lacy edge at its bottom
                a = 240 if v < 6 else (230 if (u // 2 + v) % 2 == 0 else 0)
                px.append(belt + (a,))
            elif v < 30:                                  # skin, with the garter straps
                if u in (29, 30, 31, 32) or u in (96, 97, 98, 99):
                    px.append(belt + (240,))
                else:
                    px.append((0, 0, 0, 0))
            elif v < 37:                                  # the lace top: scallops and openwork
                scallop = (v == 30) and (u % 6 in (0, 5))
                holes = ((u + 2 * v) % 4 == 0) or ((u - 2 * v) % 5 == 0)
                if scallop:
                    px.append((0, 0, 0, 0))
                elif holes:
                    px.append(lace + (110,))
                else:
                    px.append(lace + (225,))
            elif v < 39:                                  # the welt under the lace
                px.append(shade(rgb, 0.85) + (215,))
            elif seam and is_seam(u):
                px.append(seam_rgb(rgb) + (235,))
            else:
                px.append(sheer_px(u, rgb, alpha))
    return w, h, px


# ------------------------------------------------------------------ BLP2 (palettized, 8-bit alpha)
def mip_chain(w, h, px):
    levels = [(w, h, px)]
    while w > 1 or h > 1:
        nw, nh = max(1, w // 2), max(1, h // 2)
        out = []
        for y in range(nh):
            for x in range(nw):
                acc = [0, 0, 0, 0]
                n = 0
                for dy in (0, 1):
                    for dx in (0, 1):
                        sx, sy = min(w - 1, x * 2 + dx), min(h - 1, y * 2 + dy)
                        p = px[sy * w + sx]
                        for c in range(4):
                            acc[c] += p[c]
                        n += 1
                out.append(tuple(int(round(a / n)) for a in acc))
        w, h, px = nw, nh, out
        levels.append((w, h, px))
    return levels


def write_blp(w, h, px):
    levels = mip_chain(w, h, px)
    # a palette from every level's colors, merged until 256 fit
    colors = {}
    for _, _, lp in levels:
        for p in lp:
            colors[p[:3]] = colors.get(p[:3], 0) + 1
    palette = sorted(colors, key=lambda c: -colors[c])
    step = 1
    while len(palette) > 256:
        step *= 2
        q = {}
        for c, cnt in colors.items():
            k = tuple(min(255, (x // step) * step + step // 2) for x in c)
            q[k] = q.get(k, 0) + cnt
        palette = sorted(q, key=lambda c: -q[c])
    palette = palette[:256]
    lookup = {}

    def index(c):
        if c not in lookup:
            lookup[c] = min(range(len(palette)),
                            key=lambda i: sum((palette[i][k] - c[k]) ** 2 for k in range(3)))
        return lookup[c]

    data, offsets, sizes = bytearray(), [], []
    header_size = 148 + 1024
    for lw, lh, lp in levels:
        offsets.append(header_size + len(data))
        idx = bytes(index(p[:3]) for p in lp)
        alpha = bytes(p[3] for p in lp)
        data += idx + alpha
        sizes.append(len(idx) + len(alpha))
    offsets += [0] * (16 - len(offsets))
    sizes += [0] * (16 - len(sizes))
    head = b'BLP2' + struct.pack('<I', 1) + bytes([1, 8, 8, 1]) + struct.pack('<II', w, h)
    head += struct.pack('<16I', *offsets) + struct.pack('<16I', *sizes)
    pal = b''.join(bytes([c[2], c[1], c[0], 0]) for c in palette) + b'\0' * (4 * (256 - len(palette)))
    return head + pal + bytes(data)


# ------------------------------------------------------------------ ItemDisplayInfo.dbc
def read_dbc(path):
    d = open(path, 'rb').read()
    n, f, rs, ss = struct.unpack('<4x4I', d[:20])
    rows = [list(struct.unpack_from('<%dI' % f, d, 20 + i * rs)) for i in range(n)]
    strings = bytearray(d[20 + n * rs:20 + n * rs + ss])
    return f, rows, strings


def add_string(strings, cache, s):
    if not s:
        return 0
    if s not in cache:
        cache[s] = len(strings)
        strings += s.encode() + b'\0'
    return cache[s]


def write_dbc(f, rows, strings):
    rs = f * 4
    out = bytearray(b'WDBC' + struct.pack('<4I', len(rows), f, rs, len(strings)))
    for r in rows:
        out += struct.pack('<%dI' % f, *r)
    return bytes(out + strings)


# ------------------------------------------------------------------ the catalogue
def catalogue():
    """(entry, name, inventory type, display id, region textures {column: base name}, icon)"""
    items = []
    entry, display = ITEM_BASE, DISPLAY_BASE
    for key, label, rgb, alpha, seam in COLORS:
        items.append((entry, 'Sheer Pantyhose (%s)' % label, 7, display,
                      {19: 'Zelda_Hose_%s_Pant_LU' % key, 20: 'Zelda_Hose_%s_Pant_LL' % key}, 'INV_Pants_Cloth_05'))
        entry += 1
        display += 1
        items.append((entry, 'Lace-Top Stockings & Garter Belt (%s)' % label, 7, display,
                      {19: 'Zelda_Stocking_%s_Pant_LU' % key, 20: 'Zelda_Hose_%s_Pant_LL' % key}, 'INV_Pants_Cloth_08'))
        entry += 1
        display += 1
        items.append((entry, 'Sheer Hosiery Feet (%s)' % label, 8, display,
                      {21: 'Zelda_Hose_%s_Boot_FO' % key}, 'INV_Boots_Cloth_01'))
        entry += 1
        display += 1
    return items


def textures():
    files = {}
    for key, label, rgb, alpha, seam in COLORS:
        for name, painter, region in (('Zelda_Hose_%s_Pant_LU' % key, paint_hose_lu, 'LegUpperTexture'),
                                      ('Zelda_Hose_%s_Pant_LL' % key, paint_hose_ll, 'LegLowerTexture'),
                                      ('Zelda_Hose_%s_Boot_FO' % key, paint_hose_fo, 'FootTexture'),
                                      ('Zelda_Stocking_%s_Pant_LU' % key, paint_stocking_lu, 'LegUpperTexture')):
            w, h, px = painter(rgb, alpha, seam)
            # female only: there is no _M or _U version
            files['Item\\TextureComponents\\%s\\%s_F.blp' % (region, name)] = write_blp(w, h, px)
    return files


def build_patch(base_dbc, out_mpq):
    f, rows, strings = read_dbc(base_dbc)
    cache = {}
    have = {r[0] for r in rows}
    for entry, name, inv, display, tex, icon in catalogue():
        assert display not in have, display
        row = [0] * f
        row[0] = display
        row[5] = add_string(strings, cache, icon)
        row[11] = 1                       # cloth sounds
        for col, base in tex.items():
            row[col] = add_string(strings, cache, base)
        rows.append(row)
    files = textures()
    files['DBFilesClient\\ItemDisplayInfo.dbc'] = write_dbc(f, rows, strings)
    mpq.write_archive(out_mpq, files)
    print('wrote', out_mpq, os.path.getsize(out_mpq), 'bytes,', len(files), 'files')


# ------------------------------------------------------------------ server SQL
# capital-city spots for the boutique (map, x, y, z, orientation): 2.5 yards beside each city's
# cloth or tailoring merchant
BOUTIQUE_SPOTS = [
    (0, -8775.4, 711.7, 99.6, 0.77),   # Stormwind, beside Lisbeth Schneider the clothier
    (0, -4595.8, -1018.4, 512.0, 3.39),   # Ironforge, beside Ingrys Stonebrow the cloth armor merchant
    (1, 9728.6, 2294.6, 1333.1, 3.96),   # Darnassus, beside Vinasia the cloth armor merchant
    (1, 1790.6, -4564.0, 22.9, 0.98),   # Orgrimmar, beside Borya the tailoring supplier
    (1, -1245.3, 43.0, 127.2, 0.59),   # Thunder Bluff, beside Hewa the cloth armor merchant
    (0, 1694.9, 199.5, -62.1, 5.29),   # Undercity, beside Sheldon Von Croy the cloth armor merchant
]


def build_sql():
    out = ['-- Zelda of Warcraft: hosiery (female only) and the Silk & Lace boutique. Generated by',
           '-- build_hosiery.py; applied by the server at startup.']
    items = catalogue()
    ids = ','.join(str(i[0]) for i in items)
    out.append('DELETE FROM `item_template` WHERE `entry` IN (%s);' % ids)
    out.append('DELETE FROM `npc_vendor` WHERE `entry` = %d;' % BOUTIQUE)
    out.append('DELETE FROM `creature` WHERE `id` = %d;' % BOUTIQUE)
    out.append('DELETE FROM `creature_template` WHERE `Entry` = %d;' % BOUTIQUE)
    rows = []
    for entry, name, inv, display, tex, icon in items:
        legs = inv == 7
        row = {'entry': entry, 'class': 4, 'subclass': 1, 'name': name, 'displayid': display, 'Quality': 2,
               'Flags': 0, 'BuyCount': 1, 'BuyPrice': 20000 if legs else 10000, 'SellPrice': 4000 if legs else 2000,
               'InventoryType': inv, 'AllowableClass': -1, 'AllowableRace': -1, 'ItemLevel': 30,
               'RequiredLevel': 1, 'maxcount': 0, 'stackable': 1, 'bonding': 0,
               'description': 'Silk & Lace Boutique. For ladies only.', 'Material': 7, 'sheath': 0,
               'armor': 40 if legs else 28, 'block': 0, 'MaxDurability': 45 if legs else 30, 'itemset': 0,
               'DisenchantID': 0}
        for i in range(1, 11):
            row['stat_type%d' % i] = 0
            row['stat_value%d' % i] = 0
        row['stat_type1'], row['stat_value1'] = 3, (4 if legs else 2)     # agility
        row['stat_type2'], row['stat_value2'] = 6, (4 if legs else 2)     # spirit
        rows.append(row)
    out.append(insert('item_template', rows))

    t = creature_template(BOUTIQUE, 'Celestine Silkwhisper', 'Silk & Lace Boutique', 5444, 35, 0, 45, 1, '')
    t['NpcFlags'] = 0x4
    t['UnitFlags'] = 0x100 | 0x200
    out.append(insert('creature_template', [t]))
    out.append(insert('creature', [dict(guid=GUID_BASE + i, id=BOUTIQUE, map=m, spawnMask=1, position_x=x,
                                        position_y=y, position_z=z, orientation=o, spawntimesecsmin=300,
                                        spawntimesecsmax=300, spawndist=0, MovementType=0)
                                   for i, (m, x, y, z, o) in enumerate(BOUTIQUE_SPOTS)]))
    out.append(insert('npc_vendor', [dict(entry=BOUTIQUE, item=i[0], maxcount=0, incrtime=0, slot=n, condition_id=0)
                                     for n, i in enumerate(items)]))
    with open(os.path.join(HERE, 'zelda-sql', '005_hosiery.sql'), 'w', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote 005_hosiery.sql,', len(rows), 'items')


if __name__ == '__main__':
    build_sql()
    if len(sys.argv) == 3:
        build_patch(sys.argv[1], sys.argv[2])
