import json, time
from pathlib import Path
import build123d as bd
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
ROOT = Path(__file__).resolve().parent.parent
t = time.time()
r = STEPControl_Reader(); r.ReadFile(str(ROOT / "build" / "combined.stp")); r.TransferRoots()
shape = bd.Shape.cast(r.OneShape())
print("read", round(time.time() - t, 1), "s")
out = []
solids = shape.solids()
print("solids", len(solids), "shells", len(shape.shells()), "faces", len(shape.faces()))
# free shells (not in solids)
for kind, items in (("solid", solids), ("shell", [s for s in shape.shells()])):
    for i, s in enumerate(items):
        b = s.bounding_box()
        out.append({"kind": kind, "i": i, "min": [round(b.min.X, 2), round(b.min.Y, 2), round(b.min.Z, 2)],
                    "max": [round(b.max.X, 2), round(b.max.Y, 2), round(b.max.Z, 2)], "faces": len(s.faces()),
                    "vol": round(s.volume, 1) if kind == "solid" else None, "closed": s.is_valid})
json.dump(out, open(ROOT / "build" / "step_index.json", "w"))
print(len(out))
