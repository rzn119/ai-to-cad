"""GLBs for the viewer and renders: per option, the connector (fixed) and the arm + end (moving),
moved so the pivot axis is the x axis through the origin, y up (three.js), mm.
Usage: python tools/hinge_glb.py [angle_deg]  (angle > 0 also writes build/<opt>_at.glb, posed)"""
import json, sys
from pathlib import Path
import numpy as np, trimesh
from trimesh.visual.material import PBRMaterial

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "build" / "params.json").read_text())
SHIFT = trimesh.transformations.translation_matrix([-P["XC"], -P["AY"], -P["AZ"]])
YUP = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
COL = {"connector": [0.56, 0.69, 0.85, 1], "moving": [0.94, 0.91, 0.86, 1], "knob": [0.24, 0.27, 0.31, 1],
       "bolt": [0.62, 0.64, 0.66, 1]}

def mesh(path, col, extra=np.eye(4)):
    m = trimesh.load(path); m.merge_vertices()
    m.apply_transform(YUP @ extra @ SHIFT)
    m.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=col, metallicFactor=0.1 if col != COL["bolt"] else 0.8, roughnessFactor=0.55))
    return m

def scene(opt, deg=0.0):
    d = ROOT / "build" / opt
    rot = trimesh.transformations.rotation_matrix(np.radians(deg), [1, 0, 0])   # applied after SHIFT: axis at origin
    sc = trimesh.Scene()
    sc.add_geometry(mesh(d / "connector.stl", COL["connector"]), geom_name="connector", node_name="connector")
    mov = trimesh.util.concatenate([trimesh.load(d / "arm.stl"), trimesh.load(d / "end.stl")])
    mov.export(d / "moving.stl")
    sc.add_geometry(mesh(d / "moving.stl", COL["moving"], rot), geom_name="moving", node_name="moving")
    if (d / "knob.stl").exists():
        sc.add_geometry(mesh(d / "knob.stl", COL["knob"]), geom_name="knob", node_name="knob")
        sc.add_geometry(mesh(d / "bolt_nut_M4x25.stl", COL["bolt"]), geom_name="bolt", node_name="bolt")
    return sc

if __name__ == "__main__":
    deg = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    for opt in ("original", "A", "B", "C"):
        open(ROOT / "build" / f"{opt}.glb", "wb").write(scene(opt).export(file_type="glb"))
        if deg:
            open(ROOT / "build" / f"{opt}_at.glb", "wb").write(scene(opt, deg).export(file_type="glb"))
    print({p.name: p.stat().st_size for p in (ROOT / "build").glob("*.glb")})
