import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from load import solids, ROOT
S = solids()
G = json.load(open(ROOT / "build" / "assembled_groups.json"))
info = []
for k, s in enumerate(S):
    b = s.bounding_box()
    info.append((k, b.min.X, sorted((round(b.size.X, 1), round(b.size.Y, 1), round(b.size.Z, 1))), round(s.volume), len(s.faces())))
lay = [x for x in info if x[1] >= 10100]
for gi, g in enumerate(G):
    dims = g["sig"][1]; vol = g["sig"][0]
    m = [x for x in lay if all(abs(a - b) < 0.6 for a, b in zip(x[2], dims))]
    if m:
        same = [x for x in m if abs(x[3] - vol) / vol < 0.002]
        print(f"G{gi} {dims} vol {vol}: layout matches {len(m)} (same vol {len(same)})", "" if same else f"DIFF vols {[x[3] for x in m]} faces {[x[4] for x in m]} vs {g['sig'][2]}")
