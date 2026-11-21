"""Check: the key's clearance to its groove is the intended 0.20 mm, and the dowel's to its hole."""
from cad.build123d import closest_points

import connectors as c

pad = c.key_pads()[1] - c.grooves()[1]
key = c.keys_in_place()[1]
gap = closest_points(pad, key).distance
print(f"key to groove: {gap:.3f} mm (want {c.CLEAR_KEY})")
assert abs(gap - c.CLEAR_KEY) < 0.02, gap
# planted fault: a key 0.3 mm too wide must touch the pad
import build123d as bd
w, s0 = c.SEAMS[1]
fat = c.wall_prism(w, s0, c.groove_profile(c.CLEAR_KEY - 0.3), -160, -100)
print("planted fault (key 0.1 mm oversize) gap:", round(closest_points(pad, fat).distance, 3))
print("dowel hole Ø", 2 * (c.DOWEL_D / 2 + c.CLEAR_DOWEL), "for pin Ø", c.DOWEL_D)

pad = c.dowel_pads()[0] - c.dowel_holes()[0]
pin = c.dowels_in_place()[0]
g = closest_points(pad, pin).distance
print(f"dowel to hole: {g:.3f} mm (want {c.CLEAR_DOWEL}; the flat side has more)")
assert abs(g - c.CLEAR_DOWEL) < 0.02, g
