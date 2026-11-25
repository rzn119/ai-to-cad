import json
from pathlib import Path
import build123d as bd
from OCP.STEPControl import STEPControl_Reader
ROOT = Path(__file__).resolve().parent.parent
r = STEPControl_Reader(); r.ReadFile(str(ROOT / "build" / "combined_v4.stp")); r.TransferRoots()
c = bd.Compound(bd.Shape.cast(r.OneShape()).solids())
bd.export_brep(c, str(ROOT / "build" / "combined_v4_solids.brep"))
out = []
for k, s in enumerate(c.solids()):
    b = s.bounding_box()
    out.append({"k": k, "min": [round(b.min.X, 2), round(b.min.Y, 2), round(b.min.Z, 2)], "max": [round(b.max.X, 2), round(b.max.Y, 2), round(b.max.Z, 2)], "vol": round(s.volume, 1), "faces": len(s.faces())})
json.dump(out, open(ROOT / "build" / "v2_index.json", "w"))
print(len(out))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
fig, ax = plt.subplots(figsize=(30, 14))
for e in out:
    ax.add_patch(Rectangle(e["min"][:2], e["max"][0] - e["min"][0], e["max"][1] - e["min"][1], fill=False, lw=.5))
ax.autoscale(); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_xticks(range(8500, 14000, 250)); plt.xticks(fontsize=7)
plt.savefig(ROOT / "build" / "v2_top.png", dpi=45, bbox_inches="tight")
