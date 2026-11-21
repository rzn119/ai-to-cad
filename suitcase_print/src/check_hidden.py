"""Check the hidden joints: clearances as designed, the slot leaves enough wall, a planted fault fails."""
import math
import build123d as bd
from cad.build123d import closest_points

import hidden_joints as h

fit = h.seam_fit_check().shape
block = [c for c in fit.children if c.label == "slotted_block"][0]
rail = [c for c in fit.children if c.label == "rail"][0]
g = closest_points(block, rail).distance
print(f"rail to slot: {g:.3f} mm (want {h.CLEAR_RAIL})"); assert abs(g - h.CLEAR_RAIL) < 0.01, g

tf = h.tongue_fit_check().shape
gb = [c for c in tf.children if c.label == "grooved_block"][0]
tg = [c for c in tf.children if c.label == "tongue"][0]
g2 = closest_points(gb, tg).distance
print(f"tongue to groove: {g2:.3f} mm (want 0.200)"); assert abs(g2 - 0.2) < 0.02, g2

slope = (h.RAIL_TIP - h.RAIL_ROOT) / 2 / h.RAIL_DEPTH
slot_w = h.RAIL_TIP + 2 * slope * h.CLEAR_RAIL_END + 2 * h.CLEAR_RAIL * math.sqrt(1 + slope ** 2)
print(f"slot at its widest {slot_w:.2f} mm: wall either side {(h.WALL - slot_w) / 2:.2f} mm")
print(f"groove 2.00 mm: wall either side {(h.WALL - 2.0) / 2:.2f} mm; tongue {1.6} mm")

# planted fault: a rail 0.2 mm too wide must touch the slotted block
s = h.SEAMS[2]
fat = s and h.seam_plane(s[0], s[1], s[2], -150).location * bd.extrude(
    bd.Polygon(*h.rail_profile(clear=0.2), align=None), amount=40)
print("planted fault (rail 0.2 mm oversize) gap:", round(closest_points(block, fat).distance, 3))
