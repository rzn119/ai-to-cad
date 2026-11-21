"""Connectors for printing the suitcase body (part 6 + part 7 of part_6_and_7.3dm) on a Bambu A1 mini.

Geometry measured from the Rhino file (mm, the file's own coordinates):
- Each part is a U of 4.46 mm walls, 92.34 mm tall: left wall x 12875.61..12880.07, right wall
  x 13192.58..13197.04, end wall y -334.23..-329.76, open end at y -787.0, z -177.24..-84.90.
  Part 7 is the same U moved +494.00 in x; it stacks on part 6 (its bottom edge on part 6's top
  edge), which joins the two halves of the handle recess on the right wall (y -634.1..-500.2).
- The 7 mm fixed hard panel sits inside part 6's bottom (z -177.3..-171.5).

Everything here is built in the assembled frame (part 6's coordinates, part 7 stacked above it,
z -84.90..7.44). `to_p7` moves part-7 geometry back to where part 7 lies in the file.

Joints:
- 5 vertical seams per part (x = 13036.33 on the end wall; y = -652 and -482 on both side walls).
  Each gets a pad on the inside carrying half a dovetail groove; one key per seam slides up from
  below through part 6 into part 7, locking the seam and tying the halves together there.
- The horizontal joint between part 6 and part 7 gets Ø5 dowels in pads between the seams.
"""

import build123d as bd
from cad import model

MIN, C = bd.Align.MIN, bd.Align.CENTER

# --- measured -----------------------------------------------------------------
XL_OUT, XL_IN = 12875.61, 12880.07
XR_IN, XR_OUT = 13192.58, 13197.04
YE_IN, YE_OUT = -334.23, -329.76
Y_OPEN = -787.0
Z0, ZJ = -177.24, -84.90                  # part 6 bottom, joint (part 6 top = part 7 bottom)
H = ZJ - Z0                               # 92.34
ZT = ZJ + H                               # part 7 top when stacked: 7.44
P7_DX = 494.00
PANEL_TOP = -171.5

# --- splits (moved from the drawn grid so every piece fits the 180 mm plate and no seam crosses a
# handle recess: the side-wall recess y -634..-500 and the end-wall recess x 12966..13106)
X_MID = 13036.33                          # side walls: left pieces x < X_MID, right pieces x > X_MID
X_CUTS = (12948.0, 2 * X_MID - 12948.0)   # end wall: either side of its handle recess (13124.66)
Y_CUTS = (-652.0, -482.0)

# --- connector sizes (mm) ------------------------------------------------------
PAD_T = 7.0           # pad thickness, inward from the wall
PAD_HALF = 14.0       # pad half-width along the wall, each side of the seam
EMBED = 0.5           # pads reach this far into the wall so the union is clean
PAD_Z0 = -170.0       # key pads start above the hard panel
PAD_Z1 = ZT - 5.0     # and stop 5 mm below part 7's top
GROOVE_FLOOR = 2.0    # pad left under the groove
GROOVE_W_FLOOR = 14.0
GROOVE_W_OPEN = 10.0
GROOVE_STOP = 5.0     # groove closed this far below the pad top
CLEAR_KEY = 0.20      # sliding clearance per side, key in groove
KEY_GAP_END = 1.0     # key shorter than the groove at the top

DOWEL_D = 5.0
CLEAR_DOWEL = 0.20    # per side: hole Ø5.4
DOWEL_PAD_W, DOWEL_PAD_T, DOWEL_PAD_H = 16.0, 9.0, 24.0
DOWEL_DEPTH = 15.0    # hole depth each side of the joint
DOWEL_LEN = 2 * DOWEL_DEPTH - 2.0
DOWEL_FLAT = 0.4      # flat on the pin so it prints lying down and lets air out


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=(MIN, MIN, MIN))


def to_p7(shape):
    return bd.Pos(P7_DX, 0, -H) * shape


# --- seams: wall frames ----------------------------------------------------------
# A seam is (wall, s0): wall in {"L", "R", "E"}; s0 the seam's position along the wall.
SEAMS = [("E", x) for x in X_CUTS] + [(w, y) for w in ("L", "R") for y in Y_CUTS]


def wall_box(wall, s0, s1, t0, t1, z0, z1):
    """Box in a wall's frame: s along the wall, t inward from the inner face."""
    if wall == "L":
        return box(XL_IN + t0, XL_IN + t1, s0, s1, z0, z1)
    if wall == "R":
        return box(XR_IN - t1, XR_IN - t0, s0, s1, z0, z1)
    return box(s0, s1, YE_IN - t1, YE_IN - t0, z0, z1)          # end wall: inward is -y


# Each wall's frame as a plane: x = along the wall, y = inward (t), z = up. The profiles used
# here are symmetric in s, so the along-wall direction is picked to keep a right-handed frame.
WALL_PLANE_DIRS = {"L": ((0, -1, 0), (1, 0, 0)), "R": ((0, 1, 0), (-1, 0, 0)), "E": ((-1, 0, 0), (0, -1, 0))}


def wall_plane(wall, s_center, z0):
    x_dir, _ = WALL_PLANE_DIRS[wall]
    origin = {"L": (XL_IN, s_center, z0), "R": (XR_IN, s_center, z0), "E": (s_center, YE_IN, z0)}[wall]
    return bd.Plane(origin=origin, x_dir=x_dir, z_dir=(0, 0, 1))


def wall_prism(wall, s_center, profile_st, z0, z1):
    """Extrude a polygon given in (s offset, t inward) along z, placed on a wall."""
    solid = bd.extrude(bd.Polygon(*profile_st, align=None), amount=z1 - z0)
    return wall_plane(wall, s_center, z0).location * solid


def groove_profile(clear=0.0):
    """Dovetail groove in (s, t): wide at the floor (t = GROOVE_FLOOR), narrow at the opening
    (t = PAD_T). With clear > 0 it is the key: every face moved in by `clear`, measured square to
    the face, so the clearance is the same on the floor and on the sloped sides."""
    import math
    slope = (GROOVE_W_OPEN / 2 - GROOVE_W_FLOOR / 2) / (PAD_T - GROOVE_FLOOR)   # ds/dt (negative)
    side_shift = clear * math.sqrt(1 + slope * slope)                           # along s
    def half(t):
        return GROOVE_W_FLOOR / 2 + slope * (t - GROOVE_FLOOR) - side_shift
    t0 = GROOVE_FLOOR + clear
    t1 = PAD_T + (0.6 if clear == 0 else 0.0)        # the groove cut runs out past the pad face
    return [(-half(t0), t0), (half(t0), t0), (half(t1), t1), (-half(t1), t1)]


# --- the solids ---------------------------------------------------------------
def key_pads():
    """Pads at every seam, part 6 and part 7 together (split at the joint later)."""
    return [wall_box(w, s - PAD_HALF, s + PAD_HALF, -EMBED, PAD_T, PAD_Z0, PAD_Z1) for w, s in SEAMS]


def grooves():
    z1 = PAD_Z1 - GROOVE_STOP
    return [wall_prism(w, s, groove_profile(), PAD_Z0 - 1.0, z1) for w, s in SEAMS]


def key_solid():
    """One key, upright, in its seam frame at the origin (s along x, t along y)."""
    z0, z1 = PAD_Z0 + 0.0, PAD_Z1 - GROOVE_STOP - KEY_GAP_END
    prof = groove_profile(CLEAR_KEY)
    return bd.extrude(bd.Polygon(*prof, align=None), amount=z1 - z0), z0, z1


def keys_in_place():
    k, z0, z1 = key_solid()
    return [wall_prism(w, s, groove_profile(CLEAR_KEY), z0, z1) for w, s in SEAMS]


# dowel stations (wall, s): between seams, clear of corners and the recess (right wall, middle)
DOWELS = [("L", -719.5), ("L", -567.0), ("L", -420.0),
          ("R", -719.5), ("R", -420.0)]


def dowel_pads():
    return [wall_box(w, s - DOWEL_PAD_W / 2, s + DOWEL_PAD_W / 2, -EMBED, DOWEL_PAD_T, ZJ - DOWEL_PAD_H, ZJ + DOWEL_PAD_H)
            for w, s in DOWELS]


def _wall_point(w, s, t):
    if w == "L":
        return (XL_IN + t, s)
    if w == "R":
        return (XR_IN - t, s)
    return (s, YE_IN - t)


def dowel_holes():
    r = DOWEL_D / 2 + CLEAR_DOWEL
    out = []
    for w, s in DOWELS:
        x, y = _wall_point(w, s, DOWEL_PAD_T / 2 + 0.5)
        hole = bd.Pos(x, y, ZJ - DOWEL_DEPTH) * bd.Cylinder(r, 2 * DOWEL_DEPTH, align=(C, C, MIN))
        # 0.5 mm entry chamfers on both sides of the joint
        for zc, flip in ((ZJ, 1), (ZJ, -1)):
            cone = bd.Cone(r + 0.5, r, 0.5, align=(C, C, MIN))
            hole += bd.Pos(x, y, zc) * (cone if flip == 1 else bd.Rot(180, 0, 0) * cone)
        out.append(hole)
    return out


def dowel_solid():
    pin = bd.Cylinder(DOWEL_D / 2, DOWEL_LEN, align=(C, C, MIN))
    pin = bd.chamfer(pin.edges().filter_by(bd.GeomType.CIRCLE), 0.4)
    return pin - box(DOWEL_D / 2 - DOWEL_FLAT, DOWEL_D, -DOWEL_D, DOWEL_D, -1, DOWEL_LEN + 1)


# --- pieces and labels -----------------------------------------------------------
# 7 pieces per part: A and B are straight side-wall pieces, C the two corners, E the end-wall middle
CELLS = {"AL": (XL_OUT - 5, X_MID, Y_OPEN - 5, Y_CUTS[0]), "AR": (X_MID, XR_OUT + 5, Y_OPEN - 5, Y_CUTS[0]),
         "BL": (XL_OUT - 5, X_MID, *Y_CUTS), "BR": (X_MID, XR_OUT + 5, *Y_CUTS),
         "CL": (XL_OUT - 5, X_CUTS[0], Y_CUTS[1], YE_OUT + 5), "CR": (X_CUTS[1], XR_OUT + 5, Y_CUTS[1], YE_OUT + 5),
         "E": (X_CUTS[0], X_CUTS[1], Y_CUTS[1], YE_OUT + 5)}


def piece_names():
    return [(p, k) for p in (6, 7) for k in CELLS]


def label_text(name, size=9.0, advance=7.5):
    """Monospaced, regular weight, each character set 7.5 mm apart: at least ~1.5 mm between
    letters, so the engraving leaves no hair-thin ribs."""
    chars = []
    x0 = -advance * (len(name) - 1) / 2
    for i, ch in enumerate(name):
        chars.append(bd.Pos(x0 + i * advance, 0, 0) * bd.Text(ch, size, font="DejaVu Sans Mono",
                                                                font_style=bd.FontStyle.REGULAR))
    return bd.Compound(children=chars)


def label_cut(part, key):
    """Engraved name on the piece's inner face, 0.6 mm deep, upright and readable from inside
    when assembled."""
    name = f"P{part}-{key}"
    x0, x1, y0, y1 = CELLS[key]
    zm = (Z0 + ZJ) / 2 if part == 6 else (ZJ + ZT) / 2
    if part == 7 and key == "E":
        zm = -46.5                        # between part 7's two end-wall recesses
    txt = bd.extrude(label_text(name), amount=1.2)
    if key == "E":
        return _end_label(name, part)
    ym = (max(y0, Y_OPEN) + min(y1, YE_IN - 30)) / 2
    if key[1] == "L":   # inner face looks towards +x
        plane = bd.Plane(origin=(XL_IN - 0.6, ym, zm), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    else:               # inner face looks towards -x
        plane = bd.Plane(origin=(XR_IN + 0.6, ym, zm), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
    return plane.location * txt


def _end_label(name, part):
    """End-wall middle piece: the inner face (y = YE_IN) looks towards -y. Someone inside looks
    towards +y with +x on their right. Placed clear of the handle recesses."""
    txt = bd.extrude(label_text(name), amount=1.2)
    z = -150.0 if part == 6 else -46.5
    plane = bd.Plane(origin=(X_MID, YE_IN + 0.6, z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return plane.location * txt


# --- models -----------------------------------------------------------------------
def _compound(parts, label):
    kids = []
    for shape, lab, col in parts:
        shape.label, shape.color = lab, col
        kids.append(shape)
    return bd.Compound(children=kids, label=label)


@model
def connectors_assembled():
    """All connector geometry in the assembled frame (part 7 stacked on part 6)."""
    parts = [(p - g, f"key_pad_{i}", "#9aa5b1") for i, (p, g) in enumerate(zip(key_pads(), grooves()))]
    parts += [(p - h, f"dowel_pad_{i}", "#9aa5b1") for i, (p, h) in enumerate(zip(dowel_pads(), dowel_holes()))]
    parts += [(k, f"key_{i}", "#c0392b") for i, k in enumerate(keys_in_place())]
    parts += [(d, f"dowel_{i}", "#8e2a1f") for i, d in enumerate(dowels_in_place())]
    return _compound(parts, "connectors_assembled")


def dowels_in_place():
    out = []
    for w, s in DOWELS:
        x, y = _wall_point(w, s, DOWEL_PAD_T / 2 + 0.5)
        out.append(bd.Pos(x, y, ZJ - DOWEL_LEN / 2) * dowel_solid())
    return out


@model
def key_print():
    k, _, _ = key_solid()
    # lay it on its wide face (the groove floor side) for printing
    k = bd.Rot(90, 0, 0) * k
    bb = k.bounding_box()
    k = bd.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * k
    k.label, k.color = "dovetail_key", "#c0392b"
    return k


@model
def dowel_print():
    d = bd.Rot(0, 90, 0) * dowel_solid()         # lying down along x, the flat (+x side) now faces down
    bb = d.bounding_box()
    d = bd.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * d
    d.label, d.color = "dowel_5mm", "#c0392b"
    return d


if __name__ == "__main__":
    connectors_assembled()
    key_print()
    dowel_print()


@model
def pads_all():
    """Everything added to the shell (assembled frame): key pads and dowel pads, one solid."""
    s = key_pads()[0]
    for p in key_pads()[1:] + dowel_pads():
        s = s + p
    s.label, s.color = "pads", "#9aa5b1"
    return s


@model
def cuts_all():
    """Everything removed from the shell (assembled frame): grooves, dowel holes, labels."""
    s = grooves()[0]
    for c in grooves()[1:] + dowel_holes() + [label_cut(p, k) for p, k in piece_names()]:
        s = s + c
    s.label, s.color = "cuts", "#e67e22"
    return s


@model
def seam_fit_check():
    """One seam with its pad (grooved) and key in place: the key must not touch the pad."""
    w, s0 = SEAMS[1]
    pad = key_pads()[1] - grooves()[1]
    pad.label, pad.color = "pad_grooved", "#9aa5b1"
    key = keys_in_place()[1]
    key.label, key.color = "key", "#c0392b"
    return bd.Compound(children=[pad, key], label="seam_fit_check")


if __name__ == "__main__":
    pads_all()
    cuts_all()
    seam_fit_check()


# --- fit test: print this first ------------------------------------------------------
TEST_KEY_CLEARANCES = (0.15, 0.20, 0.25)
TEST_HOLE_DIAMETERS = (5.2, 5.4, 5.6)


def _engrave(solid, text, origin, x_dir, normal, size=5.0):
    t = bd.extrude(label_text(text, size=size, advance=size * 0.85), amount=1.0)
    plane = bd.Plane(origin=origin, x_dir=x_dir, z_dir=normal)
    return solid - plane.location * t


@model
def fit_test():
    """Printed as laid out here (z up). A grooved block exactly as the pads are made (25 mm of
    groove, printed upright like the pieces), three 24 mm keys at 0.15 / 0.20 / 0.25 mm clearance
    (1, 2, 3 notches), a block with Ø5.2 / 5.4 / 5.6 holes printed upright like the dowel holes,
    and two dowels."""
    kids = []
    # grooved block: wall + pad, groove along z, open at the top
    wall_t = XR_OUT - XR_IN
    blk = box(-20, 20, -wall_t, PAD_T, 0, 25)
    groove = bd.extrude(bd.Polygon(*groove_profile(), align=None), amount=30)
    blk -= bd.Pos(0, 0, 2) * groove                                # 2 mm floor, open at the top
    blk = _engrave(blk, "KEY", (-12, -wall_t + 0.5, 12.5), (1, 0, 0), (0, -1, 0))
    blk.label, blk.color = "groove_block", "#efe9dc"
    kids.append(blk)
    for i, c in enumerate(TEST_KEY_CLEARANCES):
        k = bd.extrude(bd.Polygon(*groove_profile(c), align=None), amount=24)
        k = bd.Rot(90, 0, 0) * k                                  # lay it on its wide face
        bb = k.bounding_box()
        k = bd.Pos(30 + i * 20 - bb.min.X, -bb.min.Y - 12, -bb.min.Z) * k
        bbk = k.bounding_box()
        cx = (bbk.min.X + bbk.max.X) / 2
        for n in range(i + 1):                                    # 1..3 notches, centred on one end
            x = cx + (n - i / 2) * 2.6
            k -= box(x - 0.6, x + 0.6, bbk.max.Y - 1.5, bbk.max.Y + 1, -1, 10)
        k.label, k.color = f"key_{c:.2f}", "#c0392b"
        kids.append(k)
    hb = box(-20, 20, 25, 25 + DOWEL_PAD_T + 3, 0, 18)
    for i, d in enumerate(TEST_HOLE_DIAMETERS):
        hb -= bd.Pos(-12 + 12 * i, 25 + (DOWEL_PAD_T + 3) / 2, 3) * bd.Cylinder(d / 2, 20, align=(C, C, MIN))
        hb = _engrave(hb, f"{d:.1f}"[-2:], (-12 + 12 * i - 3, 25 + 0.5, 9), (1, 0, 0), (0, -1, 0), 4.0)
    hb.label, hb.color = "hole_block", "#efe9dc"
    kids.append(hb)
    for i in range(2):
        p = bd.Rot(0, 90, 0) * dowel_solid()
        bb = p.bounding_box()
        p = bd.Pos(30 - bb.min.X, 30 + i * 8 - bb.min.Y, -bb.min.Z) * p
        p.label, p.color = "dowel", "#8e2a1f"
        kids.append(p)
    return bd.Compound(children=kids, label="fit_test")


if __name__ == "__main__":
    fit_test()


# --- for Rhino: each part's added and removed geometry where the part lies in the .3dm ----------
def _zslab(part):
    return box(XL_OUT - 60, XR_OUT + 60, Y_OPEN - 60, YE_OUT + 60, *((Z0 - 10, ZJ) if part == 6 else (ZJ, ZT + 10)))


def _rhino(part, kind):
    from cad import model as _m  # noqa: F401
    src = pads_all().shape if kind == "add" else cuts_all().shape
    s = src & _zslab(part)
    if part == 7:
        s = to_p7(s)
    s.label = f"part{part}_{'pads_to_add' if kind == 'add' else 'cut_tools'}"
    s.color = "#9aa5b1" if kind == "add" else "#e67e22"
    return s


@model
def rhino_part6():
    """Part 6 in place: union the pads, BooleanDifference the cut tools, then split at the seams."""
    return bd.Compound(children=[_rhino(6, "add"), _rhino(6, "cut")], label="part6_connectors")


@model
def rhino_part7():
    return bd.Compound(children=[_rhino(7, "add"), _rhino(7, "cut")], label="part7_connectors")


if __name__ == "__main__":
    rhino_part6()
    rhino_part7()
