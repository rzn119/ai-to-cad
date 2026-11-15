"""Combine the Rhino model's meshes with a joint option's GLB into one GLB for rendering.

usage: compose.py OBJS_DIR OPTION.glb suitcase|shelf OUT.glb [--explode DY] [--crop x0,y0,z0 x1,y1,z1]

Rhino objects the joints replace are left out: the front/back rings (rebuilt in the option),
the panels' T-tongues, the drawn links and pins (screws/nails layer) and the small clevis plates.
In suitcase mode the panels are moved to their closed pose (rotate 23 deg about X, then move).
--explode moves the front panel towards -Y by DY mm so the hardware behind it shows.
"""
import json, sys, argparse
import numpy as np, trimesh
from trimesh.visual.material import PBRMaterial

ap = argparse.ArgumentParser()
ap.add_argument("objs"); ap.add_argument("option_glb"); ap.add_argument("mode"); ap.add_argument("out")
ap.add_argument("--explode", type=float, default=0.0)
ap.add_argument("--crop", nargs=2)
ap.add_argument("--no-option", action="store_true")
a = ap.parse_args()

PALETTE = {"suitcase fillet edge": "#efe9dc", "Default": "#efe9dc", "foldable surface": "#d6d9dc",
           "frame lock": "#c3c7cb", "frame lock::password": "#55595e", "frame lock::key": "#55595e",
           "frame track": "#b9bdc2", "hard bottom inside": "#ddd6c7", "fixed hard panel panel": "#ddd6c7",
           "bottom outside (with wheels)": "#8c8f93", "leather": "#a65f33", "handle": "#3b3f44", "joinery2": "#5c6066"}
YM = 3303.8
a23 = np.radians(23.0)
R = np.array([[1, 0, 0], [0, np.cos(a23), -np.sin(a23)], [0, np.sin(a23), np.cos(a23)]])
t = np.array([0, 254.68, -962.44])

def closed_front(v): return v @ R.T + t
def mirror(v): w = v.copy(); w[:, 1] = 2 * YM - w[:, 1]; return w
def closed_back(v): return mirror(closed_front(mirror(v)))

idx = json.load(open(f"{a.objs}/index.json"))
TO_YUP = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]) @ np.diag([0.001, 0.001, 0.001, 1])
lo = hi = None
if a.crop:
    lo = np.array([float(s) for s in a.crop[0].split(",")]); hi = np.array([float(s) for s in a.crop[1].split(",")])

def crop(m, lo_, hi_):
    for ax in range(3):
        n = np.zeros(3); n[ax] = 1
        if len(m.faces): m = m.slice_plane(lo_, n, cap=False)
        if len(m.faces): m = m.slice_plane(hi_, -n, cap=False)
    return m

scene = trimesh.Scene()
skipped = []
for o in idx:
    L, mn, mx = o["layer"], np.array(o["min"]), np.array(o["max"])
    size = mx - mn
    ring = L == "frame track" and size[1] < 21 and size[2] > 500
    tongue = L == "frame track" and (mx[1] < 3168.5 or mn[1] > 3438.5)
    clevis = L == "foldable surface" and size[0] < 3
    if L == "screws/nails" or ring or tongue or clevis:
        skipped.append(o["i"]); continue
    d = np.load(f"{a.objs}/o{o['i']}.npz"); v, f = d["v"].copy(), d["f"]
    front = mx[1] < 3168.5 and L in ("foldable surface", "leather", "handle")
    back = mn[1] > 3438.5 and L in ("foldable surface", "leather", "handle")
    if a.mode == "suitcase":
        if front: v = closed_front(v) - [0, a.explode, 0]
        if back: v = closed_back(v) + [0, a.explode, 0]
    m = trimesh.Trimesh(v, f, process=False)
    if lo is not None:
        m = crop(m, lo, hi)
        if not len(m.faces): continue
    m.apply_transform(TO_YUP)
    c = PALETTE.get(L, "#cccccc").lstrip("#")
    rgb = [int(c[k:k + 2], 16) / 255 for k in (0, 2, 4)]
    m.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=[*rgb, 1.0], metallicFactor=0.0, roughnessFactor=0.6))
    scene.add_geometry(m, geom_name=f"rhino_{o['i']}")

if not a.no_option:
    opt = trimesh.load(a.option_glb)
    for k, m in enumerate(opt.dump(concatenate=False)):
        if lo is not None:
            back_to_mm = np.linalg.inv(TO_YUP)
            mm = m.copy(); mm.apply_transform(back_to_mm)
            mm = crop(mm, lo, hi)
            if not len(mm.faces): continue
            mm.apply_transform(TO_YUP); mm.visual = m.visual
            m = mm
        scene.add_geometry(m, geom_name=f"joint_{k}")
open(a.out, "wb").write(scene.export(file_type="glb"))
print("left out Rhino objects:", skipped)
