import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import build123d as bd
from load import solids, ROOT
S = solids(); print(len(S))
cols = [("assembled", 8600, 9100), ("accessories", 10100, 10700), ("frame1", 10700, 11200), ("frame2", 11200, 11700), ("shell", 12300, 12800), ("grid", 12800, 14000)]
for nm, a, b in cols:
    g = [s for s in S if a <= s.bounding_box().min.X < b]
    bd.export_gltf(bd.Compound(g), str(ROOT / "build" / f"col_{nm}.glb"), binary=True, linear_deflection=0.3, angular_deflection=0.3)
    print(nm, len(g))
