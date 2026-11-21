"""Preview GLBs of the v3 pieces. usage: v3_preview.py ASSEMBLED_DIR OUT.glb [--lift MM] [--spread MM]
[--only NAME,NAME] [--crop x0,y0,z0 x1,y1,z1]
--lift raises part 6; --spread pulls part 7's pieces apart from its centre (floor joints)."""
import argparse, os
import numpy as np, trimesh
from trimesh.visual.material import PBRMaterial
ap = argparse.ArgumentParser(); ap.add_argument("d"); ap.add_argument("out")
ap.add_argument("--lift", type=float, default=0); ap.add_argument("--spread", type=float, default=0)
ap.add_argument("--only"); ap.add_argument("--crop", nargs=2); a = ap.parse_args()
COL = {"P6": [0.80, 0.84, 0.88], "P7": [0.93, 0.91, 0.86], "F": [0.98, 0.96, 0.90]}
C7 = np.array([13530.33, -572.0])
R = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]) @ np.diag([0.001] * 3 + [1])
sc = trimesh.Scene()
for f in sorted(os.listdir(a.d)):
    n = f[:-4]
    if a.only and n not in a.only.split(","): continue
    m = trimesh.load(f"{a.d}/{f}")
    if n.startswith("P6"): m.apply_translation([0, 0, a.lift])
    if n.startswith("P7") and a.spread:
        c = m.bounds.mean(0)[:2] - C7; c = c / (np.linalg.norm(c) + 1e-9)
        m.apply_translation([c[0] * a.spread, c[1] * a.spread, 0])
    if a.crop:
        lo = np.array([float(v) for v in a.crop[0].split(",")]); hi = np.array([float(v) for v in a.crop[1].split(",")])
        for ax in range(3):
            nv = np.zeros(3); nv[ax] = 1
            if len(m.faces): m = m.slice_plane(lo, nv, cap=False)
            if len(m.faces): m = m.slice_plane(hi, -nv, cap=False)
        if not len(m.faces): continue
    m.apply_transform(R)
    col = COL["F"] if "-F" in n else COL[n[:2]]
    m.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=[*col, 1], metallicFactor=0, roughnessFactor=0.6))
    sc.add_geometry(m, geom_name=n)
open(a.out, "wb").write(sc.export(file_type="glb"))
