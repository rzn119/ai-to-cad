"""One A1 mini plate with every small part: 7 dovetail keys (6 + 1 spare) and 7 dowels (5 + 2 spare).
usage: make_plates.py EXPORTS_DIR"""
import sys
import numpy as np, trimesh
ex = sys.argv[1]
key = trimesh.load(f"{ex}/STL/dovetail_key.stl"); dowel = trimesh.load(f"{ex}/STL/dowel_5x28.stl")
for m in (key, dowel):
    m.apply_translation(-m.bounds[0])
scene = trimesh.Scene()
for i in range(7):
    k = key.copy(); k.apply_translation([5 + i * (key.extents[0] + 4), 5, 0]); scene.add_geometry(k, geom_name=f"key_{i + 1}")
for i in range(7):
    d = dowel.copy(); d.apply_translation([130, 5 + i * (dowel.extents[1] + 5), 0]); scene.add_geometry(d, geom_name=f"dowel_{i + 1}")
lo, hi = scene.bounds
print("plate layout extents", (hi - lo).round(1), "fits 180 x 180:", bool((hi - lo)[:2].max() <= 175))
open(f"{ex}/3MF/keys_and_dowels_plate.3mf", "wb").write(scene.export(file_type="3mf"))
