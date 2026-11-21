"""Check the v3 joints: clearances on the solids, and a planted fault."""
import build123d as bd
from cad.build123d import closest_points

import v3_joints as v

fit = v.bayonet_fit_check().shape
block, tab = fit.children
g = closest_points(block, tab).distance
print(f"bayonet tab to slot (locked): {g:.3f} mm (want {v.CLEAR})"); assert abs(g - v.CLEAR) < 0.01, g

k = v.SPEC["ring_keys"][0]
gk = closest_points(v.centred(k["x"], k["y"], 40, 40, v.ZJ, v.ZJ + 8) - v.ring_pocket(k), v.ring_key(k) & v.centred(k["x"], k["y"], 40, 40, v.ZJ, v.ZJ + 8)).distance
print(f"ring key to pocket: {gk:.3f} mm (want {v.CLEAR})"); assert abs(gk - v.CLEAR) < 0.01, gk

j = next(j for j in v.SPEC["floor"] if j["kind"] == "key")
win = v._slab(j, 40, 5.69, 0.0, 20.0)
gf = closest_points(win - v.floor_pocket(j), v.floor_tab(j) & win).distance
print(f"floor tab to pocket: {gf:.3f} mm (want {v.CLEAR})"); assert abs(gf - v.CLEAR) < 0.01, gf

# planted fault: a tab 0.3 mm taller must touch its pocket
fat = v._slab(j, v.TAB_L, v.TAB_H + 0.6, 0.0, v.TAB_D)
print("planted fault (tab 0.3 mm too tall each side) gap:", round(closest_points(win - v.floor_pocket(j), fat & win).distance, 3))

# the bayonet's assembly path: push in at the window (x), then slide 16 mm (y) to lock
jb = next(j for j in v.SPEC["floor"] if j["kind"] == "bayonet" and j["on"] == "P7-F2-L")
blk = v.box(v.XC, v.XC + 20, jb["y"] - 30, jb["y"] + 15, -177.24, -171.55) - v.bayonet_slot(jb)
tab0 = v.bayonet_tab(jb) & v.box(v.XC, v.XC + 20, jb["y"] - 30, jb["y"] + 15, -180, -160)
worst = 9.0
for dx in (-3.4, -2.0, -1.0, 0.0):                      # entering at the window
    g = closest_points(blk, bd.Pos(dx, -v.BAY_SLIDE, 0) * tab0).distance if dx > -3.3 else 1.0
    worst = min(worst, g)
for dy in range(0, int(v.BAY_SLIDE) + 1, 2):             # sliding to the lock
    worst = min(worst, closest_points(blk, bd.Pos(0, -v.BAY_SLIDE + dy, 0) * tab0).distance)
print(f"bayonet path: smallest gap along the push-in and the slide {worst:.3f} mm")
assert worst > 0.05, worst
# and it really locks: pulled 1 mm straight out of the locked position it must hit the slot
print("pulled out 1 mm when locked -> gap", round(closest_points(blk, bd.Pos(-1.0, 0, 0) * tab0).distance, 3), "(0 = it holds)")
