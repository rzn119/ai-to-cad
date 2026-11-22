"""Checks for the hinge options (run with a Python that has trimesh, manifold3d, shapely):
1. rebuilt original vs hinge.3dm's meshes; 2. sweep 0..180 deg: the arm touches nothing but the
spring tooth; 3. how far the spring must give at every angle (A, B), and whether lowering is
blocked (B); 4. C's clamp gaps."""
import json, sys
from pathlib import Path
import numpy as np, trimesh
from shapely.geometry import Polygon, Point
from shapely import affinity

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "build" / "params.json").read_text())
XC, AY, AZ, R, CZ0 = P["XC"], P["AY"], P["AZ"], P["R"], P["CZ0"]
L = lambda o, n: trimesh.load(ROOT / "build" / o / f"{n}.stl")
out = {}

def rot(m, deg):
    return m.copy().apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), [1, 0, 0], [XC, AY, AZ]))

def inter(a, b):
    try:
        v = a.intersection(b, engine="manifold").volume
    except Exception:
        return 0.0
    return v

# 1. original
if len(sys.argv) > 1:
    d = Path(sys.argv[1])
    for i, n in ((1, "connector"), (2, "arm"), (0, "end")):
        z = np.load(d / f"o{i}.npz"); src = trimesh.Trimesh(z["v"], z["f"])
        mine = L("original", n)
        pts = src.sample(4000)
        dist = np.abs(trimesh.proximity.signed_distance(mine, pts))
        out[f"original_{n}"] = {"p95_dev_mm": round(float(np.percentile(dist, 95)), 3), "max_dev_mm": round(float(dist.max()), 3)}

# 2. sweep
for opt in ("original", "A", "B", "C"):
    con, arm, end = L(opt, "connector"), L(opt, "arm"), L(opt, "end")
    mov = trimesh.util.concatenate([arm, end])
    keep = con
    if opt in ("A", "B"):        # leave out the spring tooth (checked in 2D below)
        tooth_zone = trimesh.creation.box(bounds=[[XC - 3.01, AY - 3, CZ0 - 0.02], [XC + 3.01, AY + 3, CZ0 + 3]])
        keep = con.difference(tooth_zone, engine="manifold")
    worst, hit = 0, []
    for a in list(range(-10, 0, 1)) + list(range(0, 181, 5)):
        v = inter(rot(mov, a), keep)
        if v > 1e-3:
            hit.append(a)
        if a >= 0:
            worst = max(worst, v)
    out[f"sweep_{opt}"] = {"overlap_mm3_0_180": round(worst, 4), "angles_hitting(-10..180)": hit}

# 3. spring travel (2D, the plane through the spring's middle)
def knuckle_section(opt):
    arm = L(opt, "arm")
    s = arm.section(plane_origin=[XC, 0, 0], plane_normal=[1, 0, 0])
    p2, T = s.to_2D(to_3D=None) if False else (None, None)
    polys = [Polygon(s.vertices[e.points][:, 1:]) for e in s.entities]
    big = max(polys, key=lambda q: q.area)
    holes = [q for q in polys if q is not big and big.contains(q.representative_point())]
    for h in holes:
        big = big.difference(h)
    return big.buffer(0)

for opt in ("A", "B"):
    tooth = Polygon(P[opt]["profile"])
    k = knuckle_section(opt)
    def need(deg):           # how far the spring must give for the arm to be at deg
        kk = affinity.rotate(k, deg, origin=(AY, AZ))
        lo, hi = 0.0, 3.0
        if not kk.intersects(tooth) or kk.intersection(tooth).area < 1e-6:
            return 0.0
        for _ in range(30):
            m = (lo + hi) / 2
            if kk.intersection(affinity.translate(tooth, 0, -m)).area < 1e-6: hi = m
            else: lo = m
        return hi
    degs = np.arange(-2, 182.01, 0.25)
    dn = np.array([need(d) for d in degs])
    at_stops = {int(a): round(float(need(a)), 3) for a in P[opt]["angles"]}
    # clearance to the tooth at each stop
    gaps = {int(a): round(affinity.rotate(k, a, origin=(AY, AZ)).distance(tooth), 3) for a in P[opt]["angles"]}
    # slope of the needed give per mm of rim travel, rising and lowering
    ds = np.diff(dn) / (np.radians(0.25) * R)
    res = {"give_needed_max_mm": round(float(dn.max()), 3), "gap_to_tooth_at_stops_mm": gaps,
           "give_at_stops": at_stops, "steepest_rising": round(float(ds.max()), 2),
           "steepest_lowering": round(float(-ds.min()), 2)}
    if opt == "B":
        # lowering from a stop: the vertical face meets the tooth with no give possible?
        blocked = []
        for a in P[opt]["angles"][1:]:
            kk = affinity.rotate(k, a - 2.0, origin=(AY, AZ))
            # could the pawl dip enough? find the give: if it exceeds the tooth height, it is locked
            g = need(a - 2.0)
            blocked.append(round(g, 2))
        res["give_needed_2deg_below_each_stop"] = blocked
    out[f"spring_{opt}"] = res
    np.savetxt(ROOT / "build" / f"give_{opt}.csv", np.c_[degs, dn], delimiter=",", fmt="%.3f")

json.dump(out, open(ROOT / "build" / "checks.json", "w"), indent=1)
print(json.dumps(out, indent=1))
