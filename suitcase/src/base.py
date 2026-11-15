"""Geometry taken from ai_to_cad_suitcase_demo.3dm (millimetres, Z up, the file's own coordinates).

Measured from the Rhino file:
- Front frame ring: 20 x 20 mm bars, front face y=3168.8, back face y=3188.8, x 10926.5..11286.5,
  z -280..280. The two uprights carry a T-slot on their front face (8 mm mouth, 2 mm lips deep,
  10 x 8 mm chamber) from z -270 to z 232. The back ring mirrors it about y=3303.8.
- Panels lean 23.0 degrees from vertical in shelf form (as drawn). Closed (suitcase form) a panel
  is the drawn panel rotated +23 degrees about X and moved by (0, 254.68, -962.44): its side rail
  then sits on the ring's upright (rail x 10926.4..10946.4, y 3138.8..3168.8, z -280.4..279.6).
- Hinge as drawn: a link from the ring slot to a 7 mm pivot pin through the panel at
  (y 3145.75, z -31.74), pin x 10924.1..10946.4.

This study changes the ring's slot chamber from 10 to 14 mm wide, so the lips are 3 mm, not 1 mm.
"""

import build123d as bd

C, MIN = bd.Align.CENTER, bd.Align.MIN

# colours
ALU = "#b9bdc2"
STEEL = "#5c6066"
DARK = "#3a3d42"
ACCENT = "#c0392b"      # what the user presses, pulls or turns
CUT = "#e67e22"         # cut tools (material to remove from the Rhino parts)

# ring
X_OUT_L, X_OUT_R = 10926.5, 11286.5
XC = (X_OUT_L + X_OUT_R) / 2            # 11106.5, left/right mirror plane
Y_F, Y_B = 3168.8, 3188.8               # front ring front / back face
YM = 3303.8                             # front/back mirror plane
Z_LO, Z_HI = -280.0, 280.0
BAR = 20.0
X0 = 10936.5                            # left slot centre line
NECK_W, NECK_D = 8.0, 2.0
CH_W, CH_D = 14.0, 8.0                  # widened chamber (was 10 wide)
Y_CH0, Y_CH1 = Y_F + NECK_D, Y_F + NECK_D + CH_D      # 3170.8 .. 3178.8
SLOT_Z0, SLOT_Z1 = -270.0, 232.0

# panel, closed pose (suitcase form)
RAIL_X0, RAIL_X1 = 10926.4, 10946.4
RAIL_Y0, RAIL_Y1 = 3138.8, 3168.8       # outer face .. inner face (on the ring)
PANEL_Z0, PANEL_Z1 = -280.4, 279.6
T_CLOSED = bd.Pos(0, 254.68, -962.44) * bd.Rot(23, 0, 0)   # drawn (leg) pose -> closed pose
T_LEG = T_CLOSED.inverse()                                 # closed pose -> drawn (leg) pose

# hinge, leg pose
PIVOT_Y, PIVOT_Z = 3145.75, -31.74
PIN_X0, PIN_X1 = 10924.1, 10946.4
PIN_R = 3.5
LINK_X0, LINK_X1 = 10931.7, 10941.3     # link band, as drawn


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=(MIN, MIN, MIN))


def cyl_y(x, z, y0, y1, r):
    return bd.Pos(x, y0, z) * bd.Rot(-90, 0, 0) * bd.Cylinder(r, y1 - y0, align=(C, C, MIN))


def cyl_x(y, z, x0, x1, r):
    return bd.Pos(x0, y, z) * bd.Rot(0, 90, 0) * bd.Cylinder(r, x1 - x0, align=(C, C, MIN))


def tag(shape, label, color):
    shape.label = label
    shape.color = color
    return shape


def mirror_x(shape):
    return shape.mirror(bd.Plane(origin=(XC, 0, 0), z_dir=(1, 0, 0)))


def mirror_y(shape):
    return shape.mirror(bd.Plane(origin=(0, YM, 0), z_dir=(0, 1, 0)))


def four_corners(parts):
    """parts: list of (shape, label, colour) for the front-left corner -> all four corners."""
    out = []
    for s, lab, col in parts:
        out.append(tag(s, f"FL_{lab}", col))
        out.append(tag(mirror_x(s), f"FR_{lab}", col))
        out.append(tag(mirror_y(s), f"BL_{lab}", col))
        out.append(tag(mirror_y(mirror_x(s)), f"BR_{lab}", col))
    return out


def ring(slot_cuts=()):
    """Front frame ring rebuilt from the file's dimensions, with the widened T-slot and any
    extra cuts (windows, holes) on the left upright; the right upright mirrors them."""
    outer = box(X_OUT_L, X_OUT_R, Y_F, Y_B, Z_LO, Z_HI)
    inner = box(X_OUT_L + BAR, X_OUT_R - BAR, Y_F - 1, Y_B + 1, Z_LO + BAR, Z_HI - BAR)
    r = outer - inner
    r = bd.fillet(r.edges().filter_by(bd.Axis.Y).group_by(bd.Axis.X)[0] + r.edges().filter_by(bd.Axis.Y).group_by(bd.Axis.X)[-1], 6)
    cuts = slot_profile_cut()
    for c in slot_cuts:
        cuts += c
    cuts_both = cuts + mirror_x(cuts)
    return r - cuts_both


def slot_profile_cut():
    neck = box(X0 - NECK_W / 2, X0 + NECK_W / 2, Y_F - 0.01, Y_CH0 + 0.01, SLOT_Z0, SLOT_Z1)
    chamber = box(X0 - CH_W / 2, X0 + CH_W / 2, Y_CH0, Y_CH1, SLOT_Z0, SLOT_Z1)
    return neck + chamber


def t_block(z0, z1, y_face=Y_F):
    """T-shaped slider that fits the widened slot: 7.6 mm neck, 13.2 x 7.4 mm head."""
    neck = box(X0 - 3.8, X0 + 3.8, y_face, Y_CH0 + 0.1, z0, z1)
    head = box(X0 - 6.6, X0 + 6.6, Y_CH0 + 0.1, Y_CH1 - 0.5, z0, z1)
    return neck + head


def hull2d(points):
    pts = sorted(set(points))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def link_arm(plate_z0, plate_z1, plate_y0=Y_F - 8.0):
    """Link from a shoe plate on the ring's front face up to the panel pivot (leg pose).
    The arm is the drawn link's 9.6 mm band; the eye takes the pivot pin."""
    import math
    eye_r = 7.0
    pts = [(plate_y0, plate_z0), (Y_F - 0.2, plate_z0), (Y_F - 0.2, plate_z1), (plate_y0, plate_z1)]
    pts += [(PIVOT_Y + eye_r * math.cos(a / 16 * 2 * math.pi), PIVOT_Z + eye_r * math.sin(a / 16 * 2 * math.pi)) for a in range(16)]
    hull = [(round(y, 3), round(z, 3)) for y, z in hull2d([(round(p[0], 3), round(p[1], 3)) for p in pts])]
    face = bd.Plane.YZ * bd.Polygon(*hull, align=None)
    arm = bd.Pos(LINK_X0, 0, 0) * bd.extrude(face, amount=LINK_X1 - LINK_X0)
    return arm - cyl_x(PIVOT_Y, PIVOT_Z, LINK_X0 - 1, LINK_X1 + 1, PIN_R + 0.1)


def quick_release_pin():
    """Ball-lock pin replacing the drawn pivot pin: push-button head and pull ring outside the rail."""
    shaft = cyl_x(PIVOT_Y, PIVOT_Z, PIN_X0, PIN_X1 + 4, PIN_R)
    head = cyl_x(PIVOT_Y, PIVOT_Z, PIN_X0 - 6, PIN_X0, 6.5)
    button = cyl_x(PIVOT_Y, PIVOT_Z, PIN_X0 - 8, PIN_X0 - 6, 2.5)
    ring_ = bd.Pos(PIN_X0 - 4, PIVOT_Y, PIVOT_Z - 15) * bd.Rot(0, 90, 0) * bd.Torus(7, 1.3)
    balls = [bd.Pos(PIN_X1 + 2.0, PIVOT_Y + s * PIN_R, PIVOT_Z) * bd.Sphere(1.2) for s in (-1, 1)]
    pin = shaft + head + button
    for b in balls:
        pin += b
    return pin, ring_


def panel_clevis_cut():
    """Cut tool, leg pose: the slot the link needs through the panel's top bar and rail (as drawn,
    the drawn link passes through the panel here too)."""
    clevis = box(LINK_X0 - 0.3, LINK_X1 + 0.3, 3115.0, 3168.0, -70.0, 20.0)
    bore = cyl_x(PIVOT_Y, PIVOT_Z, PIN_X0 - 0.1, PIN_X1, PIN_R + 0.1)
    ball_pocket = cyl_x(PIVOT_Y, PIVOT_Z, PIN_X1 - 0.1, PIN_X1 + 5.0, 5.0)   # balls spring out here
    return clevis + bore + ball_pocket
