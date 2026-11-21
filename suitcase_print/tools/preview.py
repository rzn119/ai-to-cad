"""Exploded preview GLB of the 12 pieces (+ keys) for rendering.
usage: preview.py BUILD_DIR OUT.glb EXPLODE_MM [--keys] [--only P6-CL,P6-BL] [--crop x0,y0,z0 x1,y1,z1]"""
import sys, argparse, glob, os
import numpy as np, trimesh
from trimesh.visual.material import PBRMaterial
ap = argparse.ArgumentParser(); ap.add_argument("build"); ap.add_argument("out"); ap.add_argument("explode", type=float)
ap.add_argument("--keys", action="store_true"); ap.add_argument("--only"); ap.add_argument("--crop", nargs=2)
a = ap.parse_args()
COL = {"6": [0.93, 0.91, 0.86], "7": [0.80, 0.84, 0.88]}
CENTER = np.array([13036.33, -558.0, -84.9])
TO_YUP = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]) @ np.diag([0.001, 0.001, 0.001, 1])
def crop(m):
    if not a.crop: return m
    lo = np.array([float(v) for v in a.crop[0].split(",")]); hi = np.array([float(v) for v in a.crop[1].split(",")])
    for ax in range(3):
        n = np.zeros(3); n[ax] = 1
        if len(m.faces): m = m.slice_plane(lo, n, cap=False)
        if len(m.faces): m = m.slice_plane(hi, -n, cap=False)
    return m
scene = trimesh.Scene()
for f in sorted(glob.glob(f"{a.build}/assembled/*.stl")):
    name = os.path.basename(f)[:-4]
    if a.only and name not in a.only.split(","): continue
    m = trimesh.load(f)
    c = m.bounds.mean(0); d = c - CENTER
    d[2] = np.sign(d[2])
    if abs(d[0]) < 60: d[0] = 0                     # the end-wall middle piece
    d[0], d[1] = np.sign(d[0]), {"A": -1, "B": 0, "C": 1, "E": 1}[name[3]]
    m.apply_translation([d[0] * a.explode * 0.6, d[1] * a.explode, d[2] * a.explode * 0.5])
    m = crop(m)
    if not len(m.faces): continue
    m.apply_transform(TO_YUP)
    m.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=[*COL[name[1]], 1], metallicFactor=0, roughnessFactor=0.6))
    scene.add_geometry(m, geom_name=name)
if a.keys:
    k = trimesh.load(f"{a.build}/connectors.glb")
    back = np.linalg.inv(TO_YUP)
    for g in k.dump(concatenate=False):
        mat = getattr(g.visual, "material", None)
        col = np.array(getattr(mat, "baseColorFactor", None) if mat is not None and getattr(mat, "baseColorFactor", None) is not None
                       else getattr(mat, "main_color", [0, 0, 0, 255]), dtype=float)
        if col.max() > 1.0: col = col / 255.0
        if not (col[0] > 0.15 and col[0] > 3 * col[1]):
            continue                                   # keep keys and dowels (red); pads are in the pieces
        g = g.copy(); g.apply_transform(back); g = crop(g)
        if not len(g.faces): continue
        g.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=[0.75, 0.22, 0.17, 1], metallicFactor=0, roughnessFactor=0.5))
        mat = g.visual.material if hasattr(g.visual, "material") else None
        g.apply_transform(TO_YUP)
        scene.add_geometry(g)
open(a.out, "wb").write(scene.export(file_type="glb"))
