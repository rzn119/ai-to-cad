import json
from pathlib import Path
from collections import defaultdict
import build123d as bd
ROOT = Path(__file__).resolve().parent.parent
idx = json.load(open(ROOT / "build" / "v2_index.json"))
S = bd.import_brep(str(ROOT / "build" / "combined_v4_solids.brep")).solids()
# cluster by y (exploded direction)
idx.sort(key=lambda e: e["min"][1])
cl, cur = [], []
for e in sorted(idx, key=lambda e: (e["min"][1] + e["max"][1]) / 2):
    c = (e["min"][1] + e["max"][1]) / 2
    if cur and c - max((x["min"][1] + x["max"][1]) / 2 for x in cur) > 25:
        cl.append(cur); cur = []
    cur.append(e)
cl.append(cur)
for i, g in enumerate(cl):
    ys = [(e["min"][1] + e["max"][1]) / 2 for e in g]
    print(f"== cluster {i}: y {min(ys):.0f}..{max(ys):.0f}, {len(g)} solids")
    sig = defaultdict(list)
    for e in g:
        d = tuple(sorted(round(e["max"][k] - e["min"][k], 1) for k in range(3)))
        sig[(d, round(e["vol"]))].append(e["k"])
    for (d, v), ks in sorted(sig.items(), key=lambda kv: -kv[0][1]):
        e = idx[[x["k"] for x in idx].index(ks[0])]
        print(f"   {len(ks)}x {d[2]}x{d[1]}x{d[0]} vol {v} at x{e['min'][0]:.0f} y{e['min'][1]:.0f} z{e['min'][2]:.0f}")
json.dump([[e["k"] for e in g] for g in cl], open(ROOT / "build" / "v4_clusters.json", "w"))
for i, g in enumerate(cl):
    bd.export_gltf(bd.Compound([S[e["k"]] for e in g]), str(ROOT / "build" / f"v4_c{i}.glb"), binary=True, linear_deflection=0.3, angular_deflection=0.3)
