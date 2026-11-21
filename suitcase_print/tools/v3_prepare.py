"""Prepare the updated part_6_and_7.3dm (pieces already split in Rhino) for hidden joints.

usage: python v3_prepare.py PART_6_AND_7.3dm OUT_DIR

- Reads every piece's render mesh; closes the ones that are not solid (pymeshfix). The left
  "bottom outside" piece of part 7 does not repair cleanly, so it is rebuilt as the mirror of the
  right one about the centre line (the two are mirror images in the file).
- Joins each "frame lock" strip to the part 6 wall piece it sits against.
- Stacks part 6 on part 7: the assembled frame is part 7's place in the file; part 6 moves by
  (+494.01, 0, +92.37) so its bottom edges sit on part 7's top edges (z -84.87). That joins the
  two halves of the side-wall handle recess.
- Moves the floor seam between part 7's open-end pieces and the middle floor panels from
  y -644.23 to -639.23: the middle panels were exactly 180.0 mm long, the full A1 mini plate.
- Traces the joint ring and places the joint keys, each checked against the traced walls.
Writes OUT_DIR/pieces/<name>.stl (assembled frame) and OUT_DIR/joints.json.
Needs: rhino3dm, trimesh, manifold3d, pymeshfix, shapely, numpy.
"""
import json, os, sys
import numpy as np, rhino3dm as r, trimesh, pymeshfix
from shapely.geometry import Polygon, box as sbox, LineString
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(f"{OUT}/pieces", exist_ok=True)

XC = 13530.33                      # part 7 centre line
DX = 13369.61 - 12875.60           # part 6 -> part 7 in x
DZ = -84.87 - (-177.24)            # part 6 bottom onto part 7 top
ZJ = -84.87                        # the joint between the halves
Z_FLOOR = (-177.24, -171.55)       # part 7 floor
ZF = sum(Z_FLOOR) / 2
FLOOR_SEAM_OLD, FLOOR_SEAM_NEW = -644.23, -639.23

# object index in the .3dm -> piece name (positions: B = bottom wall with wheels, S1/S2 = side wall
# from the open end, C = corner with half the end wall, F2/F3 = floor panels; L/R = left/right)
P6 = {3: "P6-B-L", 2: "P6-B-R", 15: "P6-S1-L", 16: "P6-S1-R", 14: "P6-S2-L", 17: "P6-S2-R", 13: "P6-C-L", 12: "P6-C-R"}
P7 = {19: "P7-B-L", 18: "P7-B-R", 31: "P7-S1-L", 30: "P7-S1-R", 24: "P7-S2-L", 25: "P7-S2-R", 26: "P7-C-L", 27: "P7-C-R",
      22: "P7-F2-L", 23: "P7-F2-R", 20: "P7-F3-L", 21: "P7-F3-R"}
FRAME_LOCK = {8: 15, 9: 16, 7: 14, 10: 17, 6: 13, 11: 12, 5: 13, 4: 12}   # strip -> wall piece


def obj_mesh(m, i):
    g = m.Objects[i].Geometry
    if isinstance(g, r.Extrusion):
        g = g.ToBrep(False)
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


def solid(t):
    if t.is_watertight:
        return t, False
    mf = pymeshfix.MeshFix(t.vertices, t.faces); mf.repair(joincomp=True, remove_smallest_components=False)
    return trimesh.Trimesh(mf.points, mf.faces, process=True), True


def boolean(op, a, b):
    return getattr(trimesh.boolean, op)([a, b], engine="manifold")


def tbox(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b


m = r.File3dm.Read(SRC)
report = {"source": SRC, "repairs": [], "changes": []}
pieces = {}
for i, name in {**P6, **P7}.items():
    t, fixed = solid(obj_mesh(m, i))
    if fixed:
        report["repairs"].append(f"{name}: closed gaps in the saved display mesh")
    pieces[name] = t
# part 7 left bottom piece: rebuild as the mirror of the right one
right = pieces["P7-B-R"]; mir = right.copy()
M = np.eye(4); M[0, 0] = -1; M[0, 3] = 2 * XC; mir.apply_transform(M)
if abs(mir.volume - pieces["P7-B-L"].volume) > 0.02 * mir.volume or not pieces["P7-B-L"].is_watertight:
    pieces["P7-B-L"] = mir
    report["repairs"].append("P7-B-L: display mesh would not close cleanly; rebuilt as the mirror of P7-B-R")
# frame lock strips onto their part 6 wall pieces: join a piece's strips to each other first, then
# to the wall (joining them to the wall one at a time can leave a sliver where two strips meet)
by_wall = {}
for strip, wall in FRAME_LOCK.items():
    by_wall.setdefault(wall, []).append(solid(obj_mesh(m, strip))[0])
for wall, strips in by_wall.items():
    s = strips[0]
    for t in strips[1:]:
        s = boolean("union", s, t)
    pieces[P6[wall]] = boolean("union", pieces[P6[wall]], s)
report["changes"].append("frame lock strips joined to the part 6 wall pieces they sit on")
# part 6 right corner: its saved display mesh had gaps, and the repaired mesh keeps surfaces inside
# it where the frame lock strips meet. It is the mirror image of the left corner (corner and strips
# alike, about part 6's centre line x 13036.33), so rebuild it from that one when the volumes agree.
X6C = 13036.33
mir = pieces["P6-C-L"].copy(); M = np.eye(4); M[0, 0] = -1; M[0, 3] = 2 * X6C; mir.apply_transform(M)
if abs(mir.volume - pieces["P6-C-R"].volume) < 0.005 * mir.volume:
    pieces["P6-C-R"] = mir
    report["repairs"].append("P6-C-R: rebuilt as the mirror of P6-C-L (volumes agree within 0.5 %); the repaired mesh had surfaces inside it")
# stack part 6 on part 7
for name in P6.values():
    pieces[name].apply_translation([DX, 0, DZ])
# floor seam: move the 5 mm strip y -644.23..-639.23 from F2 to S1
for side in "LR":
    f2, s1 = pieces[f"P7-F2-{side}"], pieces[f"P7-S1-{side}"]
    strip_box = tbox(13300, 13760, FLOOR_SEAM_OLD - 0.01, FLOOR_SEAM_NEW, -200, -150)
    strip = boolean("intersection", f2, strip_box)
    pieces[f"P7-F2-{side}"] = boolean("difference", f2, strip_box)
    pieces[f"P7-S1-{side}"] = boolean("union", s1, strip)
report["changes"].append("floor seam between P7-S1 and P7-F2 moved from y -644.23 to -639.23 (F2 was 180.0 mm long)")
# 0.2 mm clearance where a floor panel meets a wall (the panels drop in between the walls): cut the
# neighbouring walls' outline at floor level, grown by 0.2 mm, out of each panel (corners included)
WALL_CLEAR = 0.2
for panel, walls in (("P7-F2-L", ["P7-S2-L"]), ("P7-F2-R", ["P7-S2-R"]),
                     ("P7-F3-L", ["P7-C-L", "P7-S2-L"]), ("P7-F3-R", ["P7-C-R", "P7-S2-R"])):
    outline = unary_union([
        unary_union([Polygon(e[:, :2]).buffer(0) for e in pieces[w].section(plane_origin=[0, 0, ZF], plane_normal=[0, 0, 1]).discrete])
        for w in walls]).buffer(WALL_CLEAR, join_style=2)
    for poly in getattr(outline, "geoms", [outline]):
        prism = trimesh.creation.extrude_polygon(poly, 12.0); prism.apply_translation([0, 0, ZF - 6.0])
        pieces[panel] = boolean("difference", pieces[panel], prism)
report["changes"].append("floor panels kept 0.2 mm clear of the walls all round (corners included), so they drop in between the walls")
def clean(t, name):
    """Drop zero-volume slivers that unions sometimes leave behind (checked again after a save and
    reload, where they can show up as edges shared by more than two faces)."""
    t2 = trimesh.Trimesh(t.vertices.copy(), t.faces.copy(), process=True); t2.merge_vertices()
    if t2.is_volume:
        return t
    mf = pymeshfix.MeshFix(t2.vertices, t2.faces); mf.repair(joincomp=False, remove_smallest_components=False)
    r_ = trimesh.Trimesh(mf.points, mf.faces, process=True)
    # the repair can leave the joined parts as separate, overlapping shells: fuse them into one solid
    bodies = sorted([b for b in r_.split(only_watertight=True) if abs(b.volume) > 1.0], key=lambda b: -abs(b.volume))
    r_ = bodies[0]
    for b in bodies[1:]:
        r_ = boolean("union", r_, b)
    change = abs(abs(r_.volume) - abs(t.volume)) / abs(t.volume)
    assert r_.is_volume and change < 0.001, (name, change)
    report["repairs"].append(f"{name}: removed a zero-volume sliver left by joining (volume change {change * 100:.3f} %)")
    return r_


for name in list(pieces):
    pieces[name] = clean(pieces[name], name)
    t = pieces[name]
    t.export(f"{OUT}/pieces/{name}.stl")
    assert trimesh.load(f"{OUT}/pieces/{name}.stl").is_volume, name


# ---------------- traces ----------------
def trace(t, z):
    s = t.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    return Polygon() if s is None else unary_union([Polygon(e[:, :2]).buffer(0) for e in s.discrete if len(e) > 3])

top7 = {n: trace(t, ZJ - 0.4) for n, t in pieces.items() if n.startswith("P7")}
bot6 = {n: trace(t, ZJ + 0.4) for n, t in pieces.items() if n.startswith("P6")}
fl7 = {n: trace(t, ZF) for n, t in pieces.items() if n.startswith("P7")}

# ---------------- ring keys (part 7 top -> part 6 bottom) ----------------
KEY_L, KEY_W = 12.0, 1.6
POCKET_L, POCKET_W = 12.4, 2.0
MIN_WALL = 1.0                       # material left beside a pocket


def rect(cx, cy, length, width, along_y):
    r_ = sbox(-length / 2, -width / 2, length / 2, width / 2)
    if along_y:
        r_ = rotate(r_, 90, origin=(0, 0))
    return translate(r_, cx, cy)


def wall_centre(poly_union, line):
    hit = poly_union.intersection(line)
    segs = [g for g in getattr(hit, "geoms", [hit]) if g.length > 0]
    return segs


ring6 = unary_union(list(bot6.values())); ring7 = unary_union(list(top7.values()))
cands = []
# side walls: scan along y; end wall and bottom wall: scan along x
for y in np.arange(-818.0, -330.0, 1.0):
    for seg in wall_centre(ring7, LineString([(13300, y), (13760, y)])):
        if 3.5 < seg.length < 6.5:
            cx = (seg.coords[0][0] + seg.coords[-1][0]) / 2
            cands.append((cx, y, True))
for x in np.arange(13380.0, 13682.0, 1.0):
    for seg in wall_centre(ring7, LineString([(x, -830), (x, -300)])):
        if 3.5 < seg.length < 6.5:
            cy = (seg.coords[0][1] + seg.coords[-1][1]) / 2
            cands.append((x, cy, False))


def owner(rect_poly, traces, margin):
    for n, tr in traces.items():
        if tr.buffer(-margin).contains(rect_poly):
            return n
    return None


valid = []
for cx, cy, along_y in cands:
    key = rect(cx, cy, KEY_L, KEY_W, along_y)
    pocket = rect(cx, cy, POCKET_L, POCKET_W, along_y)
    o7 = owner(key, top7, 0.6)
    o6 = owner(pocket, bot6, MIN_WALL)
    # keep at least 2 mm of wall between a pocket's end and a seam (1 mm erosion + 1 mm longer test)
    long_pocket = rect(cx, cy, POCKET_L + 2.0, POCKET_W, along_y)
    if o7 and o6 and owner(long_pocket, bot6, MIN_WALL) == o6 and owner(rect(cx, cy, KEY_L + 2.0, KEY_W, along_y), top7, 0.6) == o7:
        valid.append((cx, cy, along_y, o7, o6))
# pick: per (part 7 piece, part 6 piece) pair, keys at least 45 mm apart, at least one each
by_pair = {}
for v in valid:
    by_pair.setdefault((v[3], v[4]), []).append(v)
ring_keys = []
for pair, vs in by_pair.items():
    vs.sort(key=lambda v: (v[1], v[0]) if v[2] else (v[0], v[1]))
    pos = lambda v: v[1] if v[2] else v[0]
    span = pos(vs[-1]) - pos(vs[0])
    if span < 20:                        # a short zone (the 18 mm stagger): one key in the middle
        chosen = [min(vs, key=lambda v: abs(pos(v) - (pos(vs[0]) + pos(vs[-1])) / 2))]
    else:
        chosen, last = [], None
        for v in vs:
            if last is None or abs(pos(v) - last) >= 45.0:
                chosen.append(v); last = pos(v)
        # make sure the far end of a long run gets one too
        if pos(vs[-1]) - last > 25.0:
            chosen.append(vs[-1])
    for v in chosen:
        ring_keys.append({"x": round(float(v[0]), 3), "y": round(float(v[1]), 3), "along_y": bool(v[2]),
                          "on": v[3], "into": v[4]})

# ---------------- floor joints (part 7) ----------------
floor = []
def fkey(kind, owner_, into, x, y, axis, sign, **kw):
    """axis: the direction the key points ('x' or 'y'); sign +1/-1."""
    d = {"kind": kind, "on": owner_, "into": into, "x": x, "y": y, "axis": axis, "sign": sign, "z": ZF}
    d.update(kw); floor.append(d)

# floor seams across the length (keys point along y)
for side, sgn in (("L", -1), ("R", 1)):
    xs = (XC + sgn * 110.0, XC + sgn * 40.0)
    for x in xs:
        fkey("key", f"P7-B-{side}", f"P7-S1-{side}", x, -779.46, "y", +1)           # bottom wall -> S1 floor
        fkey("key", f"P7-S1-{side}", f"P7-F2-{side}", x, FLOOR_SEAM_NEW, "y", +1)   # S1 floor -> F2
        fkey("key", f"P7-F3-{side}", f"P7-F2-{side}", x, -464.23, "y", -1)          # F3 -> F2
        fkey("wallkey", f"P7-C-{side}", f"P7-F3-{side}", x, -326.69, "y", -1)       # end wall -> F3
    xin = 13374.08 if side == "L" else 13686.58                                       # side wall inner face
    s = 1 if side == "L" else -1
    for y in (-600.0, -505.0):
        fkey("wallkey", f"P7-S2-{side}", f"P7-F2-{side}", xin, y, "x", s)
    for y in (-430.0, -370.0):
        fkey("wallkey", f"P7-C-{side}", f"P7-F3-{side}", xin, y, "x", s)
# centre seam: bayonet dovetails, left pieces carry the tab, right pieces the slot
for lp, rp, ys in (("P7-B-L", "P7-B-R", (-795.0,)), ("P7-S1-L", "P7-S1-R", (-700.0, -660.0)),
                   ("P7-F2-L", "P7-F2-R", (-575.0, -500.0)), ("P7-F3-L", "P7-F3-R", (-410.0, -352.0))):
    for y in ys:
        fkey("bayonet", lp, rp, XC, y, "x", +1)

json.dump({"frame": {"DX": DX, "DZ": DZ, "ZJ": ZJ, "ZF": ZF, "XC": XC}, "ring_keys": ring_keys, "floor": floor,
           "report": report}, open(f"{OUT}/joints.json", "w"), indent=1)
print(f"{len(pieces)} pieces; {len(ring_keys)} ring keys over {len(by_pair)} part-6/part-7 pairs; {len(floor)} floor joints")
for pair in sorted(by_pair):
    n = sum(1 for k in ring_keys if (k["on"], k["into"]) == pair)
    print(f"  {pair[0]:9s} -> {pair[1]:9s}: {n} keys")
print(json.dumps(report, indent=1))
