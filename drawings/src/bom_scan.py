import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from collections import defaultdict
from load import solids, ROOT
S = solids()
idx = json.load(open(ROOT / "build" / "step_index_layers.json"))
sol_idx = [e for e in idx if e["kind"] == "solid"]
groups = defaultdict(list)
for k, s in enumerate(S):
    b = s.bounding_box()
    if not (8600 <= b.min.X < 9100):
        continue
    dims = tuple(sorted((round(b.size.X, 1), round(b.size.Y, 1), round(b.size.Z, 1))))
    sig = (round(s.volume, 0), dims, len(s.faces()))
    groups[sig].append((k, [round(b.min.X, 1), round(b.min.Y, 1), round(b.min.Z, 1)], sol_idx[k].get("layer")))
rows = sorted(groups.items(), key=lambda kv: -kv[0][0])
for sig, items in rows:
    print(len(items), "x", sig, items[0][2], "first", items[0][0], items[0][1])
json.dump([{"sig": [sig[0], list(sig[1]), sig[2]], "items": items} for sig, items in rows], open(ROOT / "build" / "assembled_groups.json", "w"))
