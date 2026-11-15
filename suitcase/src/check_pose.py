"""Check: the closed->leg transform puts the panel pivot back where the Rhino file has it."""
import build123d as bd
from base import T_LEG, T_CLOSED, PIVOT_Y, PIVOT_Z

closed = bd.Vector(10935.26, 3162.76, 237.49)
leg = (T_LEG * bd.Pos(closed)).position
print("pivot closed -> leg:", tuple(round(v, 2) for v in leg), "expected (10935.26, 3145.75, -31.74)")
back = (T_CLOSED * bd.Pos(10936.0, 2969.5, -467.5)).position     # tongue's bottom end as drawn
print("tongue bottom as drawn -> closed:", tuple(round(v, 2) for v in back))
assert abs(leg.Y - PIVOT_Y) < 0.05 and abs(leg.Z - PIVOT_Z) < 0.05
