"""Shared geometry for the suitcase joint study coupons.

Units are mm, +Z up. Suitcase-form coupons show one front corner of the box:
the body lies behind y=0 (y<0) and the aluminium frame sits in front of it (y>0).
Shelf-form coupons show one vertical leg rail of a frame (x 0..30, y 0..18)
with a piece of the box side wall in front of it (y<0).
"""

import build123d as bd

C, MIN = bd.Align.CENTER, bd.Align.MIN

# Colours
CREAM = "#efe9dc"      # suitcase body
ALU = "#b9bdc2"        # aluminium frame / rail
LEATHER = "#a65f33"
STEEL = "#5c6066"      # studs, pins, rods
MAGNET = "#2f3236"
ACCENT = "#c0392b"     # parts the user operates (knobs, levers, tabs)

# Suitcase-form coupon sizes
WALL = 15.0            # body wall thickness
LEG = 160.0            # length of each leg of the corner coupon
DEPTH = 80.0           # how far the body coupon runs back (-y)
FW = 30.0              # frame bar width
FT = 14.0              # frame bar thickness (y)

# Shelf-form coupon sizes
RAIL_W = 30.0
RAIL_T = 18.0
RAIL_H = 420.0
BOX_GAP = 1.0          # air between box side wall and rail face
BOX_T = 15.0

# Layout: exploded copy sits to the right of the assembled one
EXPLODE_X = 260.0


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min/max coordinates."""
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=(MIN, MIN, MIN))


def cyl_y(x, z, y0, y1, r):
    """Cylinder along Y from y0 to y1 (y1 > y0), centred on (x, z)."""
    return bd.Pos(x, y0, z) * bd.Rot(-90, 0, 0) * bd.Cylinder(r, y1 - y0, align=(C, C, MIN))


def cyl_x(y, z, x0, x1, r):
    """Cylinder along X from x0 to x1, centred on (y, z)."""
    return bd.Pos(x0, y, z) * bd.Rot(0, 90, 0) * bd.Cylinder(r, x1 - x0, align=(C, C, MIN))


def cone_minus_y(x, z, y_base, length, r_base, r_tip):
    """Cone whose base sits at y_base and whose tip points towards -Y."""
    return bd.Pos(x, y_base, z) * bd.Rot(90, 0, 0) * bd.Cone(r_base, r_tip, length, align=(C, C, MIN))


def slot_y(x, z_top, z_bot, y0, y1, width):
    """Vertical rounded slot (stadium) cut along Y, from z_bot to z_top."""
    r = width / 2
    return box(x - r, x + r, y0, y1, z_bot, z_top) + cyl_y(x, z_top, y0, y1, r) + cyl_y(x, z_bot, y0, y1, r)


def keyhole_cut(x, z_head, travel, y_face, plate, chamber, into=+1, head_d=10.5, neck_w=6.4):
    """A keyhole slot cut into a face at y=y_face; ``into`` is +1 or -1 (the
    direction the material lies in from the face).

    The face plate (``plate`` thick) carries a head hole at z_head and a narrow
    slot running down by ``travel``; behind it a chamber as wide as the head
    lets the stud's head slide down behind the plate.
    """
    def span(a, b):  # depth range measured from the face, as (y_lo, y_hi)
        ya, yb = y_face + into * a, y_face + into * b
        return min(ya, yb), max(ya, yb)

    p0, p1 = span(-0.01, plate)
    c0, c1 = span(plate - 0.01, plate + chamber)
    cut = cyl_y(x, z_head, p0, p1, head_d / 2)
    cut += slot_y(x, z_head, z_head - travel, p0, p1, neck_w)
    cut += slot_y(x, z_head, z_head - travel, c0, c1, head_d)
    return cut


def stud(x, z, y_root, neck_len, out=+1, head_t=3.0, neck_d=6.0, head_d=10.0):
    """Mushroom stud standing off a face at y_root, pointing +Y (out=+1) or -Y (out=-1)."""
    def span(a, b):
        ya, yb = y_root + out * a, y_root + out * b
        return min(ya, yb), max(ya, yb)

    n0, n1 = span(0, neck_len)
    h0, h1 = span(neck_len, neck_len + head_t)
    return cyl_y(x, z, n0, n1, neck_d / 2) + cyl_y(x, z, h0, h1, head_d / 2)


def tag(shape, label, color):
    shape.label = label
    shape.color = color
    return shape


def corner_body(extra=None):
    """L-shaped front corner of the suitcase body (bottom wall + side wall)."""
    body = box(0, LEG, -DEPTH, 0, 0, WALL) + box(0, WALL, -DEPTH, 0, 0, LEG)
    if extra is not None:
        body += extra
    return body


def corner_frame():
    """L-shaped corner of the aluminium frame with a rebate for the leather panel."""
    frame = box(0, LEG, 0, FT, 0, FW) + box(0, FW, 0, FT, 0, LEG)
    frame -= box(FW - 5, LEG + 1, 2, 10, FW - 5, LEG + 1)
    leather = box(FW - 5, LEG, 2, 10, FW - 5, LEG)
    return frame, leather


def moved(shape, dx=0.0, dy=0.0, dz=0.0):
    return bd.Pos(dx, dy, dz) * shape


def pair(label, body_parts, frame_parts, hinge_x, explode_x=EXPLODE_X):
    """Assembled copy at the origin, "opened book" copy to the right.

    body_parts / frame_parts are lists of (shape, label, colour). In the opened
    copy the frame side is swung 180 degrees about a vertical axis at x=hinge_x,
    y=0, so both mating faces point the same way and can be seen in one view.
    """
    swing = bd.Pos(2 * hinge_x, 0, 0) * bd.Rot(0, 0, 180)

    def build(dx, opened):
        kids = [tag(moved(s, dx), lab, col) for s, lab, col in body_parts]
        for s, lab, col in frame_parts:
            placed = swing * s if opened else s
            kids.append(tag(moved(placed, dx), lab, col))
        return kids

    assembled = bd.Compound(children=build(0.0, False), label="assembled")
    opened = bd.Compound(children=build(explode_x, True), label="opened")
    return bd.Compound(children=[assembled, opened], label=label)
