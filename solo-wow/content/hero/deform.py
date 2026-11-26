"""Reshape the 1.12 human male (HumanMale.m2) into a slimmer, younger build without touching the skeleton:
every vertex is moved by the bones it is weighted to (the weighted sum of each bone's own deformation),
so the skin still follows the same bones and animations."""
import math

# 1.12 bone index -> region (port_roll.py's map)
REGION = {18: 'pelvis', 21: 'hips', 20: 'waist', 22: 'chest', 48: 'neck', 64: 'head', 49: 'shoulder', 50: 'shoulder',
          65: 'upperarm', 66: 'upperarm', 78: 'forearm', 79: 'forearm', 95: 'hand', 97: 'hand',
          25: 'thigh', 26: 'thigh', 53: 'shin', 54: 'shin', 68: 'foot', 70: 'foot', 80: 'foot', 81: 'foot'}
JAW = 77
LIMB_CHILD = {65: 78, 66: 79, 78: 95, 79: 97, 25: 53, 26: 54, 53: 68, 54: 70}

VARIANTS = {
    'A': dict(upperarm=0.86, forearm=0.88, thigh=0.90, shin=0.92, chest_w=0.90, chest_d=0.93, waist=0.91, hips=0.95,
              shoulder=0.90, neck=0.86, head=1.04, jaw=0.94, hand=0.92, foot=0.95),
    'B': dict(upperarm=0.74, forearm=0.78, thigh=0.82, shin=0.86, chest_w=0.82, chest_d=0.86, waist=0.84, hips=0.91,
              shoulder=0.82, neck=0.76, head=1.08, jaw=0.88, hand=0.84, foot=0.90),
    'C': dict(upperarm=0.64, forearm=0.70, thigh=0.75, shin=0.80, chest_w=0.75, chest_d=0.80, waist=0.78, hips=0.87,
              shoulder=0.74, neck=0.68, head=1.12, jaw=0.84, hand=0.78, foot=0.86),
}

def regions(m):
    out = []
    for i, b in enumerate(m.bones):
        j, jaw = i, False
        while j >= 0 and j not in REGION:
            if j == JAW: jaw = True
            j = m.bones[j]['parent']
        if i == JAW: jaw = True
        out.append((j if j >= 0 else None, REGION.get(j), jaw))
    return out

def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def mul(a, k): return (a[0]*k, a[1]*k, a[2]*k)
def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def bone_deform(m, reg, bi, p, f):
    anchor, region, jaw = reg[bi]
    if region is None:
        return p
    piv = m.bones[anchor]['pivot']
    if region in ('upperarm', 'forearm', 'thigh', 'shin'):
        tip = m.bones[LIMB_CHILD[anchor]]['pivot']
        ax = sub(tip, piv); L = math.sqrt(dot(ax, ax)) or 1.0; ax = mul(ax, 1.0 / L)
        d = sub(p, piv); along = dot(d, ax)
        perp = sub(d, mul(ax, along))
        return add(add(piv, mul(ax, along)), mul(perp, f[region]))
    if region in ('chest', 'waist', 'hips', 'pelvis', 'shoulder', 'neck'):
        kw = {'chest': f['chest_w'], 'waist': f['waist'], 'hips': f['hips'], 'pelvis': f['hips'],
              'shoulder': f['shoulder'], 'neck': f['neck']}[region]
        kd = {'chest': f['chest_d'], 'neck': f['neck']}.get(region, (1.0 + kw) / 2)
        cx = piv[0]; cy = 0.0                       # the spine's vertical line (the body is symmetric about y=0)
        return (cx + (p[0] - cx) * kd, cy + (p[1] - cy) * kw, p[2])
    if region == 'head':
        q = add(piv, mul(sub(p, piv), f['head']))
        if jaw:                                     # a narrower, softer jaw
            q = (q[0], q[1] * f['jaw'], q[2])
        return q
    if region in ('hand', 'foot'):                  # smaller hands and feet, about the wrist and ankle
        return add(piv, mul(sub(p, piv), f[region]))
    return p

def deform(m, f):
    reg = regions(m)
    out = []
    for v in m.verts:
        p = v['pos']; tw = sum(v['w']) or 1
        acc = (0.0, 0.0, 0.0)
        for w, bi in zip(v['w'], v['bi']):
            if w:
                acc = add(acc, mul(bone_deform(m, reg, bi, p, f), w / tw))
        out.append(acc)
    return out
