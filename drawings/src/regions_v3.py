import json
from pathlib import Path
import build123d as bd
from OCP.STEPControl import STEPControl_Reader
ROOT = Path(__file__).resolve().parent.parent
idx = json.load(open(ROOT / "build" / "v2_index.json"))
R = {"accessories": (10200, 10600, -700, -300), "frame_top1": (10780, 11200, -900, -300), "frame_top2": (11200, 11700, -900, -300),
     "shell": (12300, 12800, -900, -300), "handle_frame": (10400, 11200, -1700, -1000), "frame_bottom": (11200, 11700, -1700, -1000)}
used = set()
for nm, (x0, x1, y0, y1) in R.items():
    g = [e for e in idx if x0 <= e["min"][0] and e["max"][0] <= x1 and y0 <= e["min"][1] and e["max"][1] <= y1]
    used |= {e["k"] for e in g}
    print(f"== {nm}: {len(g)} solids")
    for e in sorted(g, key=lambda e: -e["vol"])[:8]:
        print("   ", [round(e["max"][i] - e["min"][i], 1) for i in range(3)], e["vol"], e["faces"], e["min"])
print("unassigned", [(e["min"], e["max"]) for e in idx if e["k"] not in used])
r = STEPControl_Reader(); r.ReadFile(str(ROOT / "build" / "combined_v3.stp")); r.TransferRoots()
sh = bd.Shape.cast(r.OneShape())
sol_bb = [tuple(round(v, 1) for v in (e["min"] + e["max"])) for e in idx]
for s in sh.shells():
    b = s.bounding_box(); t = tuple(round(v, 1) for v in (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z))
    if t not in sol_bb:
        print("open surface", t, len(s.faces()))
