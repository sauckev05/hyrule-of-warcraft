# Computes solo-wow/content/dungeon_vendors.json (Beedle spots: entrance, middle, end of each dungeon and
# raid). Run from a folder holding db.pickle (the classic-db world dump parsed by dbq.py).
import pickle, math, json
db=pickle.load(open('db.pickle','rb'))
ct={r['Entry']:r for r in db['creature_template']}
at={r['id']:r for r in db['areatrigger_teleport']}
spawns={}
for c in db['creature']:
    spawns.setdefault(c['map'],[]).append(c)
def spawn_of(e):
    for c in db['creature']:
        if c['id']==e: return c
# (name, entrance areatrigger, final boss entry)
D=[('Ragefire Chasm',2230,11520),('The Deadmines',78,639),('Wailing Caverns',228,5775),('Shadowfang Keep',145,4275),
   ('Blackfathom Deeps',257,4829),('The Stockade',101,1716),('Gnomeregan',324,7800),('Razorfen Kraul',244,4421),
   ('Scarlet Monastery Graveyard',45,4543),('Scarlet Monastery Library',614,6487),('Scarlet Monastery Armory',612,3975),
   ('Scarlet Monastery Cathedral',610,3977),('Razorfen Downs',442,7358),('Uldaman',286,2748),("Zul'Farrak",924,7267),
   ('Maraudon (Orange)',3133,12201),('Maraudon (Purple)',3134,12201),('Sunken Temple',446,5709),
   ('Blackrock Depths',1466,9019),('Lower Blackrock Spire',1468,9568),('Upper Blackrock Spire',None,10363),
   ('Dire Maul East',3183,11492),('Dire Maul West',3186,11486),('Dire Maul North',3189,11501),
   ('Scholomance',2567,10508),('Stratholme Live',2216,10812),('Stratholme Undead',2214,10440),
   ('Molten Core',2886,12098),("Onyxia's Lair",2848,10184),('Blackwing Lair',3726,10162),("Zul'Gurub",3928,14834),
   ("Ruins of Ahn'Qiraj",4008,15339),("Temple of Ahn'Qiraj",4010,15727),('Naxxramas',4156,15990)]
out=[]
d3=lambda a,b: math.dist(a,b)
for name,trig,boss in D:
    b=spawn_of(boss)
    if not b: print('NO BOSS', name, boss); continue
    m=b['map']; B=(b['position_x'],b['position_y'],b['position_z'])
    pts=[s for s in spawns[m] if s['id'] not in (boss,)]
    P=lambda s:(s['position_x'],s['position_y'],s['position_z'])
    if trig:
        t=at[trig]; E=(t['target_position_x'],t['target_position_y'],t['target_position_z']); eo=t['target_orientation']
        # entrance: a few yards in, along the way the trigger faces
        ent=(E[0]+3*math.cos(eo), E[1]+3*math.sin(eo), E[2], eo)
        out.append((name,'entrance',m)+ent)
    else:
        E=None
    total=d3(E,B) if E else None
    if E:
        cand=[s for s in pts if d3(E,P(s))+d3(P(s),B) <= 1.35*total and d3(E,P(s))>0.25*total and d3(P(s),B)>0.25*total]
        if cand:
            mid=min(cand,key=lambda s: abs(d3(E,P(s))-d3(P(s),B)))
            out.append((name,'middle',m)+P(mid)+(math.atan2(B[1]-mid['position_y'],B[0]-mid['position_x']),))
        else: print('no middle', name)
    # end: near the last boss - a nearby creature's spot (a real floor), else beside the boss
    cand=[s for s in pts if 8<=d3(P(s),B)<=35 and abs(s['position_z']-B[2])<8]
    if E: cand=[s for s in cand if d3(E,P(s))<d3(E,B)+5] or cand
    if cand:
        end=min(cand,key=lambda s: abs(d3(P(s),B)-15))
        ex,ey,ez=P(end)
    else:
        bo=b['orientation']
        ex,ey,ez=B[0]+6*math.cos(bo),B[1]+6*math.sin(bo),B[2]
    out.append((name,'end',m,ex,ey,ez,math.atan2(B[1]-ey,B[0]-ex)))
for o in out: print(o[0],o[1],o[2],[round(v,1) for v in o[3:]])
print(len(out))
json.dump([dict(dungeon=o[0],spot=o[1],map=o[2],x=round(o[3],2),y=round(o[4],2),z=round(o[5],2),o=round(o[6]%(2*math.pi),3)) for o in out],
          open('/home/claude/hyrule-of-warcraft/solo-wow/content/dungeon_vendors.json','w'),indent=1)
