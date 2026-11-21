"""Trace the wall at the joint between part 6 and part 7 and write the tongue and groove outlines.

usage: joint_section.py PART_6_AND_7.3dm OUT.json
The wall is cut 0.5 mm below part 6's top edge and 0.5 mm above part 7's bottom edge (stacked);
the two traces are checked against each other. The tongue is the trace shrunk 1.43 mm from both
faces (1.6 mm wide); the groove is shrunk 1.23 mm (2.0 mm wide: 0.2 mm clearance per side).
Needs: rhino3dm, trimesh, shapely.
"""
import json, sys
import numpy as np, rhino3dm as r, trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

SRC, OUT = sys.argv[1], sys.argv[2]
Z0, ZJ, P7_DX = -177.24, -84.90, 494.00
H = ZJ - Z0
WALL = 4.46
TONGUE_W, GROOVE_W = 1.6, 2.0


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
    raise SystemExit("part not found")


def trace(mesh, z):
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    polys = [Polygon(e[:, :2]).buffer(0) for e in sec.discrete if len(e) > 3]
    return unary_union([p for p in polys if p.area > 1.0])


m = r.File3dm.Read(SRC)
p6 = brep_mesh(m, 12800, 13300)
p7 = brep_mesh(m, 13300, 13800); p7.apply_translation([-P7_DX, 0, H])
w6, w7 = trace(p6, ZJ - 0.5), trace(p7, ZJ + 0.5)
mismatch = w6.symmetric_difference(w7).area
print(f"wall trace at the joint: part 6 {w6.area:.0f} mm2, part 7 {w7.area:.0f} mm2, mismatch {mismatch:.1f} mm2")
wall = w6.intersection(w7)                      # where both halves have wall
inset_t = (WALL - TONGUE_W) / 2
inset_g = (WALL - GROOVE_W) / 2


def rings(geom):
    geoms = getattr(geom, "geoms", [geom])
    out = []
    for g in geoms:
        if g.area < 0.5:
            continue
        g = g.simplify(0.02)
        out.append({"exterior": [list(map(float, c)) for c in g.exterior.coords][:-1],
                    "holes": [[list(map(float, c)) for c in h.coords][:-1] for h in g.interiors]})
    return out


tongue = wall.buffer(-inset_t, join_style=2, mitre_limit=3)
groove = wall.buffer(-inset_g, join_style=2, mitre_limit=3)
print(f"tongue band {tongue.area:.0f} mm2 (~{tongue.area / TONGUE_W:.0f} mm long), groove band {groove.area:.0f} mm2")
json.dump({"z_joint": ZJ, "tongue_width": TONGUE_W, "groove_width": GROOVE_W, "wall_mismatch_mm2": round(mismatch, 1),
           "tongue": rings(tongue), "groove": rings(groove)}, open(OUT, "w"))
