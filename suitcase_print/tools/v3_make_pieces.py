"""Apply the hidden joints to the 20 prepared pieces and lay each on the A1 mini plate.

usage: python v3_make_pieces.py BUILD_V3_DIR OUT_DIR
Reads BUILD_V3_DIR/pieces/<name>.stl and joints/<name>_add.stl / _cut.stl, writes
OUT_DIR/STL/<name>.stl (print orientation), BUILD_V3_DIR/assembled/<name>.stl and
OUT_DIR/pieces_report.json, then checks that no two assembled pieces overlap.

Print orientation: part 7 as it stands in the suitcase (floor down, keys up); part 6 upside down
(its top edge on the bed, key pockets opening upwards: far less support than upright); the floor
panels lie flat. A piece too long for the
plate square-on is turned 45 degrees.
"""
import itertools, json, os, sys
import numpy as np, trimesh

B, OUT = sys.argv[1], sys.argv[2]
PLATE = 180.0
os.makedirs(f"{OUT}/STL", exist_ok=True); os.makedirs(f"{B}/assembled", exist_ok=True)


def boolean(op, a, b):
    return getattr(trimesh.boolean, op)([a, b], engine="manifold")


report = {"pieces": {}}
names = sorted(f[:-4] for f in os.listdir(f"{B}/pieces") if f.endswith(".stl"))
assembled = {}
for name in names:
    p = trimesh.load(f"{B}/pieces/{name}.stl")
    for kind, op in (("add", "union"), ("cut", "difference")):
        f = f"{B}/joints/{name}_{kind}.stl"
        if os.path.exists(f):
            p = boolean(op, p, trimesh.load(f))
    assembled[name] = p.copy()
    p.export(f"{B}/assembled/{name}.stl")
    if name.startswith("P6"):            # part 6 prints upside down: far less support, pockets open upwards
        p.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    lo, hi = p.bounds
    p.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    ext = p.extents; turn = 0
    if max(ext[0], ext[1]) > PLATE - 5:                  # try it across the diagonal; keep what is smaller
        q = p.copy(); q.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 4, [0, 0, 1]))
        if max(q.extents[0], q.extents[1]) < max(ext[0], ext[1]):
            lo, hi = q.bounds
            q.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, 0]); p = q; ext = p.extents; turn = 45
    p.export(f"{OUT}/STL/{name}.stl")
    report["pieces"][name] = {"size_mm": [round(float(v), 1) for v in ext], "turned_on_plate_deg": turn,
                              "volume_cm3": round(float(p.volume) / 1000, 1), "watertight": bool(p.is_watertight),
                              "fits_180_plate_with_2mm_margin_each_side": bool(max(ext[0], ext[1]) <= PLATE - 4 and ext[2] <= PLATE)}
    print(name, report["pieces"][name])

# no two assembled pieces may overlap
worst, pairs, clashes = 0.0, 0, []
for a, b in itertools.combinations(names, 2):
    A, Bm = assembled[a], assembled[b]
    if not ((A.bounds[0] - 0.01 <= Bm.bounds[1]).all() and (Bm.bounds[0] - 0.01 <= A.bounds[1]).all()):
        continue
    pairs += 1
    i = boolean("intersection", A, Bm)
    v = float(i.volume) if len(i.faces) else 0.0
    if v > 0.01:
        th = v / max(i.area / 2, 1e-9) if len(i.faces) else 0.0      # mean thickness of the overlap
        clashes.append((a, b, round(v, 3), round(th, 4)))
    worst = max(worst, v)
report["overlap_check"] = {"touching_pairs": pairs, "largest_overlap_mm3": round(worst, 4), "clashes": clashes}
print("overlap check:", report["overlap_check"])
json.dump(report, open(f"{OUT}/pieces_report.json", "w"), indent=1)
