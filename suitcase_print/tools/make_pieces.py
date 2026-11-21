"""Cut part 6 and part 7 into 14 printable pieces with hidden joints, for a Bambu A1 mini.

usage: python make_pieces.py PART_6_AND_7.3dm BUILD_DIR OUT_DIR

Reads the two shells from the .3dm (their render meshes), stacks part 7 on part 6 (the assembled
frame of src/hidden_joints.py), cuts each piece out, adds its rails/tongue and cuts its
slots/groove/label (BUILD_DIR/joints/<piece>_add.stl, _cut.stl from `cad run src/build_parts.py`),
then lays it on the plate and writes OUT_DIR/STL/<piece>.stl.

Both halves print upright as they stand in the suitcase: part 6's tongue points up, part 7's
groove opens at the bed. Needs: rhino3dm, trimesh, manifold3d, mapbox_earcut, numpy.
"""
import json, os, sys
import numpy as np, rhino3dm as r, trimesh

SRC, BUILD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

# must match src/hidden_joints.py
XL_OUT, XR_OUT, YE_OUT, Y_OPEN = 12875.61, 13197.04, -329.76, -787.0
Z0, ZJ = -177.24, -84.90
H = ZJ - Z0
ZT = ZJ + H
P7_DX = 494.00
X_MID = 13036.33
X_CUTS = (12948.0, 2 * X_MID - 12948.0)
Y_CUTS = (-652.0, -482.0)
CELLS = {"AL": (XL_OUT - 5, X_MID, Y_OPEN - 5, Y_CUTS[0]), "AR": (X_MID, XR_OUT + 5, Y_OPEN - 5, Y_CUTS[0]),
         "BL": (XL_OUT - 5, X_MID, *Y_CUTS), "BR": (X_MID, XR_OUT + 5, *Y_CUTS),
         "CL": (XL_OUT - 5, X_CUTS[0], Y_CUTS[1], YE_OUT + 5), "CR": (X_CUTS[1], XR_OUT + 5, Y_CUTS[1], YE_OUT + 5),
         "E": (X_CUTS[0], X_CUTS[1], Y_CUTS[1], YE_OUT + 5)}
PLATE = 180.0


def brep_mesh(m, x_lo, x_hi):
    for o in m.Objects:
        g = o.Geometry
        if isinstance(g, r.Brep) and g.IsSolid:
            bb = g.GetBoundingBox()
            if x_lo < (bb.Min.X + bb.Max.X) / 2 < x_hi and bb.Max.Z - bb.Min.Z > 80:
                V, F = [], []
                for f in g.Faces:
                    p = f.GetMesh(r.MeshType.Any)
                    if p is None:
                        continue
                    p.Faces.ConvertQuadsToTriangles(); b = len(V)
                    V += [(p.Vertices[k].X, p.Vertices[k].Y, p.Vertices[k].Z) for k in range(len(p.Vertices))]
                    F += [(p.Faces[k][0] + b, p.Faces[k][1] + b, p.Faces[k][2] + b) for k in range(len(p.Faces))]
                t = trimesh.Trimesh(np.array(V), np.array(F), process=True); t.merge_vertices()
                return t
    raise SystemExit(f"no part between x {x_lo} and {x_hi}")


def close_bottom(t, z):
    """Part 7's mesh has a small gap in its bottom face: trim 0.02 mm off the bottom and cap it."""
    if t.is_watertight:
        return t, False
    t = t.slice_plane([0, 0, z + 0.02], [0, 0, 1], cap=True); t.merge_vertices()
    if not t.is_watertight:
        trimesh.repair.fill_holes(t)
    return t, True


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b


def boolean(op, a, b):
    return getattr(trimesh.boolean, op)([a, b], engine="manifold")


m = r.File3dm.Read(SRC)
p6 = brep_mesh(m, 12800, 13300)
p7 = brep_mesh(m, 13300, 13800); p7.apply_translation([-P7_DX, 0, H])
report = {"source": SRC, "repairs": [], "pieces": {}}
p7, fixed = close_bottom(p7, ZJ)
if fixed:
    report["repairs"].append("part 7: closed a small gap in its bottom face (bottom trimmed 0.02 mm)")
for name, t in (("part 6", p6), ("part 7", p7)):
    assert t.is_watertight, f"{name} mesh is not closed"
os.makedirs(f"{OUT}/STL", exist_ok=True); os.makedirs(f"{BUILD}/assembled", exist_ok=True)

for part, shell in ((6, p6), (7, p7)):
    z0, z1 = (Z0 - 5, ZJ) if part == 6 else (ZJ, ZT + 5)
    for key, (x0, x1, y0, y1) in CELLS.items():
        name = f"P{part}-{key}"
        piece = boolean("intersection", shell, box(x0, x1, y0, y1, z0, z1))
        add = f"{BUILD}/joints/{name}_add.stl"
        if os.path.exists(add):
            piece = boolean("union", piece, trimesh.load(add))
        cut = f"{BUILD}/joints/{name}_cut.stl"
        if os.path.exists(cut):
            piece = boolean("difference", piece, trimesh.load(cut))
        piece.export(f"{BUILD}/assembled/{name}.stl")                # in place, for previews
        # on the plate: upright as in the suitcase, centred, bottom on the bed
        lo, hi = piece.bounds
        piece.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
        ext = piece.extents; turn = 0
        if max(ext[0], ext[1]) > PLATE - 5:                          # a long strip: lay it across the diagonal
            piece.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 4, [0, 0, 1]))
            lo, hi = piece.bounds
            piece.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, 0]); ext = piece.extents; turn = 45
        piece.export(f"{OUT}/STL/{name}.stl")
        report["pieces"][name] = {"size_mm": [round(float(v), 1) for v in ext], "turned_on_plate_deg": turn,
                                  "volume_cm3": round(float(piece.volume) / 1000, 1), "watertight": bool(piece.is_watertight),
                                  "fits_180_plate_with_5mm_margin": bool(max(ext[0], ext[1]) <= PLATE - 5 and ext[2] <= PLATE)}
        print(name, report["pieces"][name])

json.dump(report, open(f"{OUT}/pieces_report.json", "w"), indent=1)
