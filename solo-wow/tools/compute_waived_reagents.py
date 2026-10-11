# Computes solo-wow/content/waived_reagents.json. Run from a folder holding dbq.py and db.pickle (the
# classic-db world dump parsed), with ../world.sql and ../dbc2/{Spell,SkillLineAbility}.dbc from the server.
import sys, struct, re, json, collections
sys.path.insert(0, '.')
from dbq import parse_values
import pickle

def load(path):
    d=open(path,'rb').read()
    n,f,rs,ss=struct.unpack('<4x4I',d[:20])
    strs=d[20+n*rs:]
    rows={}
    for i in range(n):
        v=struct.unpack('<%dI'%f,d[20+i*rs:20+(i+1)*rs]); rows[v[0]]=v
    def s(o):
        try: return strs[o:strs.index(b'\0',o)].decode('utf-8','replace')
        except: return ''
    return rows,s

sql=open('../world.sql',encoding='utf-8',errors='replace').read()
def table(name):
    out=[]
    for m in re.finditer(r"INSERT INTO `%s` VALUES "%name, sql):
        rows,_=parse_values(sql, m.end()); out+=rows
    return out
skin=table('skinning_loot_template'); ref=table('reference_loot_template')
# columns: entry,item,ChanceOrQuestChance,groupid,mincountOrRef,maxcount,condition_id
refitems=collections.defaultdict(set)
for r in ref:
    if r[4]>0: refitems[r[0]].add(r[1])
skinned=set()
for r in skin:
    if r[4]>0: skinned.add(r[1])
    else: skinned|=refitems[-r[4]]

sp,ss=load('../dbc2/Spell.dbc')
sla,_=load('../dbc2/SkillLineAbility.dbc')
skill_of=collections.defaultdict(set)
for r in sla.values():
    skill_of[r[2]].add(r[1])
PROF={164:'Blacksmithing',165:'Leatherworking',197:'Tailoring',202:'Engineering',171:'Alchemy',333:'Enchanting',
      186:'Mining',182:'Herbalism',393:'Skinning',185:'Cooking',129:'First Aid',356:'Fishing'}
ALLOWED={164:{164,186},165:{165,393},197:{197},202:{202,186},171:{171,182},333:{333}}
origin=collections.defaultdict(set)
for sid,r in sp.items():
    profs=[k for k in skill_of.get(sid,()) if k in PROF]
    if not profs: continue
    for e in range(3):
        if r[61+e]==24 and r[103+e]:
            origin[r[103+e]].update(profs)
_names={r['entry']:r['name'] for r in pickle.load(open('db.pickle','rb'))['item_template']}
for it in skinned:
    n=_names.get(it,'')
    if re.search(r'Leather|Hide|Scale|Skin|Chitin|Carapace', n) and 'Fish' not in n:
        origin[it]={393}
pairs=[]
for sid,r in sp.items():
    crafts=[k for k in skill_of.get(sid,()) if k in ALLOWED]
    if not crafts: continue
    allowed=set().union(*(ALLOWED[k] for k in crafts))
    regs=[r[42+i] for i in range(8) if r[42+i] and r[50+i]]
    waive=[item for item in regs if origin.get(item) and not (origin[item] & allowed)]
    if len(waive) < len(regs):          # a recipe always keeps at least one material of its own
        pairs += [(sid,item) for item in waive]
pairs=sorted(set(pairs))
db=pickle.load(open('db.pickle','rb'))
names={r['entry']:r['name'] for r in db['item_template']}
by=collections.Counter(tuple(sorted(PROF[o] for o in origin[i])) for _,i in pairs)
print(len(pairs),'pairs; by origin',by.most_common(12))
for sid,item in pairs[:0]: pass
# examples: axes
for sid,item in pairs:
    if 'Axe' in ss(sp[sid][120]) or sid in (2738,2739,3294): print(sid, ss(sp[sid][120]), '->', names.get(item))
json.dump(pairs, open('waived.json','w'))
