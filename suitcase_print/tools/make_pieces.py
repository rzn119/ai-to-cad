"""Cut part 6 and part 7 into 12 printable pieces with connectors, ready for a Bambu A1 mini.

usage: python make_pieces.py PART_6_AND_7.3dm BUILD_DIR OUT_DIR

Reads the two shells from the .3dm (their render meshes), moves part 7 onto part 6 (the assembled
frame of src/connectors.py), adds build/pads.stl, cuts each piece out, subtracts build/cuts.stl,
then turns each piece to its print orientation and writes OUT_DIR/STL/<piece>.stl.
Needs: rhino3dm, trimesh, manifold3d, mapbox_earcut, numpy.

Print orientation: part 6 pieces upside down, part 7 pieces as they are, so the edge where the two
halves meet lies on the bed for every piece.
"""
import json, sys
import numpy as np, rhino3dm as r, trimesh

SRC, BUILD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

# must match src/connectors.py
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


def brep_mesh(m, idx):
    g = m.Objects[idx].Geometry
    V, F = [], []
    for f in g.Faces:
        p = f.GetMesh(r.MeshType.Any)
        if p is None:
            continue
        p.Faces.ConvertQuadsToTriangles(); b = len(V)
        V += [(p.Vertices[k].X, p.Vertices[k].Y, p.Vertices[k].Z) for k in range(len(p.Vertices))]
        F += [(p.Faces[k][0] + b, p.Faces[k][1] + b, p.Faces[k][2] + b) for k in range(len(p.Faces))]
    t = trimesh.Trimesh(np.array(V), np.array(F), process=True)
    t.merge_vertices()
    return t


def find_part(m, x_lo, x_hi):
    for i, o in enumerate(m.Objects):
        g = o.Geometry
        if isinstance(g, r.Brep) and g.IsSolid:
            bb = g.GetBoundingBox()
            if x_lo < (bb.Min.X + bb.Max.X) / 2 < x_hi and bb.Max.Z - bb.Min.Z > 80:
                return i
    raise SystemExit(f"no part between x {x_lo} and {x_hi}")


def close_bottom(t, z):
    """Part 7's mesh has a small gap in its bottom face: trim 0.02 mm off the bottom and cap it."""
    if t.is_watertight:
        return t, False
    t = t.slice_plane([0, 0, z + 0.02], [0, 0, 1], cap=True)
    t.merge_vertices()
    if not t.is_watertight:
        trimesh.repair.fill_holes(t)
    return t, True


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def boolean(op, a, b):
    return getattr(trimesh.boolean, op)([a, b], engine="manifold")


m = r.File3dm.Read(SRC)
p6 = brep_mesh(m, find_part(m, 12800, 13300))
p7 = brep_mesh(m, find_part(m, 13300, 13800))
p7.apply_translation([-P7_DX, 0, H])                  # stack part 7 on part 6
report = {"source": SRC, "repairs": [], "pieces": {}}
p7, fixed = close_bottom(p7, ZJ)
if fixed:
    report["repairs"].append("part 7: closed a small gap in its bottom face (bottom trimmed 0.02 mm)")
for name, t in (("part 6", p6), ("part 7", p7)):
    assert t.is_watertight, f"{name} mesh is not closed"

pads = trimesh.load(f"{BUILD}/pads.stl")
cuts = trimesh.load(f"{BUILD}/cuts.stl")

# check: away from the 0.5 mm they are meant to reach into the wall, pads must not meet the shell
# (a pad running into a handle recess would show up here)
XL_IN, XR_IN, YE_IN = 12880.07, 13192.58, -334.23
walls = boolean("union", box(XL_OUT - 60, XL_IN + 0.6, -900, 100, -300, 100), box(XR_IN - 0.6, XR_OUT + 60, -900, 100, -300, 100))
walls = boolean("union", walls, box(XL_OUT - 60, XR_OUT + 60, YE_IN - 0.6, 100, -300, 100))
pads_inner = boolean("difference", pads, walls)
for name, shell in (("part 6", p6), ("part 7", p7)):
    clash = boolean("intersection", pads_inner, shell)
    v = float(clash.volume) if len(clash.faces) else 0.0
    report.setdefault("pad_clash_mm3", {})[name] = round(v, 2)
    print(f"pads meeting {name} beyond their 0.5 mm embed: {v:.2f} mm^3")

for part, shell, zr in ((6, p6, (Z0 - 5, ZJ)), (7, p7, (ZJ, ZT + 5))):
    zbox = box(XL_OUT - 50, XR_OUT + 50, Y_OPEN - 50, YE_OUT + 50, *zr)
    body = boolean("union", shell, boolean("intersection", pads, zbox))
    for key, (x0, x1, y0, y1) in CELLS.items():
        if True:
            name = f"P{part}-{key}"
            piece = boolean("intersection", body, box(x0, x1, y0, y1, *zr))
            piece = boolean("difference", piece, cuts)
            piece.export(f"{BUILD}/assembled/{name}.stl")          # in place, for previews
            # print orientation: part 6 upside down; joint edge on the bed for both halves
            if part == 6:
                piece.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
            lo, hi = piece.bounds
            piece.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
            ext = piece.extents
            turn = 0
            if max(ext[0], ext[1]) > PLATE - 5:          # a long strip: lay it across the diagonal
                piece.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 4, [0, 0, 1]))
                lo, hi = piece.bounds
                piece.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, 0])
                ext = piece.extents
                turn = 45
            fits = bool(max(ext[0], ext[1]) <= PLATE - 5 and ext[2] <= PLATE)
            piece.export(f"{OUT}/STL/{name}.stl")
            report["pieces"][name] = {"size_mm": [round(float(v), 1) for v in ext], "turned_on_plate_deg": turn, "volume_cm3": round(float(piece.volume) / 1000, 1),
                                      "watertight": bool(piece.is_watertight), "fits_180_plate_with_5mm_margin": fits}
            print(name, report["pieces"][name])

json.dump(report, open(f"{OUT}/pieces_report.json", "w"), indent=1)
