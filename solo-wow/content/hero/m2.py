import struct
class M2:
    def __init__(self, path):
        self.data = bytearray(open(path, 'rb').read())
        d = self.data
        u = lambda o: struct.unpack_from('<I', d, o)[0]
        assert d[:4] == b'MD20', d[:4]
        self.version = u(4)
        self.n_bone, self.o_bone = u(0x34), u(0x38)
        self.n_key, self.o_key = u(0x3c), u(0x40)
        self.n_vert, self.o_vert = u(0x44), u(0x48)
        self.n_view, self.o_view = u(0x4c), u(0x50)
        self.bones = []
        for i in range(self.n_bone):
            b = self.o_bone + i * 0x6c
            key, flags = struct.unpack_from('<iI', d, b)
            parent = struct.unpack_from('<h', d, b + 8)[0]
            pivot = struct.unpack_from('<3f', d, b + 0x60)
            self.bones.append(dict(key=key, parent=parent, pivot=pivot))
        self.verts = []
        for i in range(self.n_vert):
            o = self.o_vert + i * 48
            pos = struct.unpack_from('<3f', d, o)
            w = struct.unpack_from('<4B', d, o + 12)
            bi = struct.unpack_from('<4B', d, o + 16)
            nrm = struct.unpack_from('<3f', d, o + 20)
            uv = struct.unpack_from('<2f', d, o + 32)
            self.verts.append(dict(pos=pos, w=w, bi=bi, nrm=nrm, uv=uv))
        # view 0 (LOD 0), inline in the 1.12 .m2
        v = self.o_view
        nI, oI, nT, oT, nP, oP, nS, oS, nU, oU, lod = struct.unpack_from('<11I', d, v)
        self.vlookup = struct.unpack_from('<%dH' % nI, d, oI)
        self.tris = struct.unpack_from('<%dH' % nT, d, oT)
        self.subs = []
        for k in range(nS):
            s = oS + k * 32
            sid, lvl, sv, nv, st, nt, nb, sb, unk, root = struct.unpack_from('<10H', d, s)
            self.subs.append(dict(id=sid, sv=sv, nv=nv, st=st, nt=nt))
    def write_positions(self, positions, normals=None):
        for i, p in enumerate(positions):
            struct.pack_into('<3f', self.data, self.o_vert + i * 48, *p)
            if normals is not None:
                struct.pack_into('<3f', self.data, self.o_vert + i * 48 + 20, *normals[i])
