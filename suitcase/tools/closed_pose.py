"""Work out the rigid move that takes the front panel from its leg pose (as drawn) to closed."""
import json, numpy as np, rhino3dm as r
import sys
F = sys.argv[1]   # path to ai_to_cad_suitcase_demo.3dm
m = r.File3dm.Read(F)
a = np.radians(23.0)
R = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
def verts(g):
    b = g if isinstance(g, r.Brep) else (g.ToBrep(False) if isinstance(g, r.Extrusion) else None)
    return np.array([[v.Location.X, v.Location.Y, v.Location.Z] for v in b.Vertices]) if b else None
panel, tongue_heads, pins = [], [], []
for i, o in enumerate(m.Objects):
    g, L = o.Geometry, o.Attributes.LayerIndex
    bb = g.GetBoundingBox()
    if bb.Max.Y < 3168.5 and L in (7, 16, 17, 11):
        panel.append(i)
    if L == 11 and bb.Max.Y < 3168.5 and bb.Min.X < 10960 and (bb.Max.X - bb.Min.X) < 30:
        tongue_heads.append((i, verts(g)))
    if L == 12 and bb.Max.Y < 3168.5 and bb.Min.Y > 3140 and bb.Max.Y < 3150:
        pins.append((i, bb))
P = np.vstack([verts(m.Objects[i].Geometry) for i in panel if verts(m.Objects[i].Geometry) is not None])
Pr = P @ R.T
# the tongue head: the wider (10.5) of the two tongue solids
heads = [(i, v) for i, v in tongue_heads if np.ptp(v[:, 0]) > 10]
hv = heads[0][1] @ R.T
print("panel objects:", len(panel))
print("rotated tongue head y range", hv[:, 1].min(), hv[:, 1].max(), "x", hv[:, 0].min(), hv[:, 0].max())
dy = 3170.8 - hv[:, 1].min()            # head's inner face onto the slot's chamber start
print("rotated panel z range", Pr[:, 2].min(), Pr[:, 2].max(), "len", np.ptp(Pr[:, 2]))
zc_ring = (-285.6 + 284.8) / 2
dz = zc_ring - (Pr[:, 2].min() + Pr[:, 2].max()) / 2
T = np.eye(4); T[:3, :3] = R; T[:3, 3] = [0, dy, dz]
print("dy %.2f dz %.2f" % (dy, dz))
Pc = Pr + [0, dy, dz]
print("closed panel bbox", Pc.min(0).round(1), Pc.max(0).round(1))
for i, bb in pins:
    c = np.array([(bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, (bb.Min.Z + bb.Max.Z) / 2])
    cc = R @ c + [0, dy, dz]
    print("panel pivot pin", i, "leg", c.round(2), "-> closed", cc.round(2))
json.dump({"T_closed": T.tolist(), "panel_objects": panel}, open("closed.json", "w"))
