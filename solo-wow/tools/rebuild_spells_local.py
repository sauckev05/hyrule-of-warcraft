"""Refresh patch-Z's Spell.dbc and SpellVisual.dbc from build_mastery (its spells are idempotent)."""
import sys
sys.path.insert(0, '/home/claude/hyrule-of-warcraft/solo-wow/content')
sys.path.insert(0, '/home/claude/hyrule-of-warcraft/solo-wow/tools')
import mpq, build_mastery as bm, tempfile, os
src, out = sys.argv[1], sys.argv[2]
a = mpq.Archive(src)
names = a.names() if hasattr(a, 'names') else None
files = {}
lst = [l for l in a.read('(listfile)').decode('latin1').replace('\r', '').split('\n') if l] if a.has('(listfile)') else []
for n in lst:
    if n == '(listfile)': continue
    files[n] = a.read(n)
print(len(files), 'files; has visual', 'DBFilesClient\\SpellVisual.dbc' in files)
tmp = tempfile.mkdtemp()
for key, fn in (('DBFilesClient\\Spell.dbc', bm.patch_spells), ('DBFilesClient\\SpellVisual.dbc', bm.patch_spell_visual)):
    p = os.path.join(tmp, key.split('\\')[-1]); open(p, 'wb').write(files[key])
    files[key] = fn(p)
mpq.write_archive(out, files)
b = mpq.Archive(out)
print('ok', len(files), os.path.getsize(out))
