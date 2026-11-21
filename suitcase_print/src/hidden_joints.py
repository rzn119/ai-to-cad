"""Hidden joints for printing the suitcase body (parts 6 and 7 of part_6_and_7.3dm) on a Bambu A1 mini.

Every connector is inside a cut face; nothing stands on the inside or outside of the shell.
- Vertical seams: a sliding dovetail the full height of the cut face. A rail tapering from
  1.4 mm (root) to 2.0 mm (tip) stands 3.0 mm out of one piece's cut face; the next piece has the
  matching slot, 0.15 mm larger all round and 0.2 mm deeper. The pieces slide together vertically
  and cannot be pulled apart sideways.
- Joint between part 6 and part 7: a continuous tongue 1.6 mm wide x 3.0 mm tall on part 6's top
  edge, following the wall all the way round (corners and handle recesses included), into a groove
  2.0 mm wide x 3.4 mm deep in part 7's bottom edge (0.2 mm clearance per side, 0.4 mm at the end).
  Its outline comes from build/joint_section.json (tools/joint_section.py traces the wall in the .3dm).

Assembled frame: part 6's coordinates in the file, part 7 stacked on it (z -84.90 .. 7.44).
Everything goes together vertically: part 6's pieces slide down past each other, then each part 7
piece slides down past its neighbours and onto part 6's tongue.
"""

import json
import math
from pathlib import Path

import build123d as bd
from cad import model

MIN, C = bd.Align.MIN, bd.Align.CENTER
HERE = Path(__file__).resolve().parent

# --- measured from the .3dm ---------------------------------------------------------
XL_OUT, XL_IN = 12875.61, 12880.07
XR_IN, XR_OUT = 13192.58, 13197.04
YE_IN, YE_OUT = -334.23, -329.76
Y_OPEN = -787.0
Z0, ZJ = -177.24, -84.90
H = ZJ - Z0
ZT = ZJ + H
P7_DX = 494.00
WALL = 4.46

# --- cuts (as before: every piece fits the 180 mm plate, no seam crosses a handle recess) ----
X_MID = 13036.33
X_CUTS = (12948.0, 2 * X_MID - 12948.0)
Y_CUTS = (-652.0, -482.0)
CELLS = {"AL": (XL_OUT - 5, X_MID, Y_OPEN - 5, Y_CUTS[0]), "AR": (X_MID, XR_OUT + 5, Y_OPEN - 5, Y_CUTS[0]),
         "BL": (XL_OUT - 5, X_MID, *Y_CUTS), "BR": (X_MID, XR_OUT + 5, *Y_CUTS),
         "CL": (XL_OUT - 5, X_CUTS[0], Y_CUTS[1], YE_OUT + 5), "CR": (X_CUTS[1], XR_OUT + 5, Y_CUTS[1], YE_OUT + 5),
         "E": (X_CUTS[0], X_CUTS[1], Y_CUTS[1], YE_OUT + 5)}

# --- dovetail rail (vertical seams) ---------------------------------------------------
RAIL_ROOT, RAIL_TIP, RAIL_DEPTH = 1.4, 2.0, 3.0
CLEAR_RAIL = 0.15        # per side, measured square to each face
CLEAR_RAIL_END = 0.2     # extra slot depth past the rail's tip
RAIL_EMBED = 0.5         # the rail starts this far inside its own piece, for a clean union

# --- tongue and groove (joint between the halves) ---------------------------------------
TONGUE_H = 3.0
GROOVE_D = TONGUE_H + 0.4

# A seam: wall, position along the wall, wall centre line, the piece the rail is on (s below the
# seam) and the piece the slot is cut into (s above it). s runs along +y on the side walls, +x on
# the end wall.
SEAMS = [
    ("E", X_CUTS[0], (YE_IN + YE_OUT) / 2, "CL", "E"),
    ("E", X_CUTS[1], (YE_IN + YE_OUT) / 2, "E", "CR"),
    ("L", Y_CUTS[0], (XL_OUT + XL_IN) / 2, "AL", "BL"),
    ("L", Y_CUTS[1], (XL_OUT + XL_IN) / 2, "BL", "CL"),
    ("R", Y_CUTS[0], (XR_IN + XR_OUT) / 2, "AR", "BR"),
    ("R", Y_CUTS[1], (XR_IN + XR_OUT) / 2, "BR", "CR"),
]


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=(MIN, MIN, MIN))


def part_z(part):
    return (Z0, ZJ) if part == 6 else (ZJ, ZT)


def seam_plane(wall, s0, centre, z0):
    if wall == "E":
        return bd.Plane(origin=(s0, centre, z0), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
    return bd.Plane(origin=(centre, s0, z0), x_dir=(0, 1, 0), z_dir=(0, 0, 1))


def rail_profile(clear=0.0, s_start=-RAIL_EMBED, end_extra=0.0):
    """Trapezoid in (s, t): root half-width at s=0, tip half-width at s=RAIL_DEPTH.
    With clear > 0 it is the slot: each side moved out by `clear` square to itself."""
    slope = (RAIL_TIP - RAIL_ROOT) / 2 / RAIL_DEPTH
    shift = clear * math.sqrt(1 + slope * slope)
    def half(s):
        return RAIL_ROOT / 2 + slope * s + shift
    s1 = RAIL_DEPTH + end_extra
    return [(s_start, -half(s_start)), (s1, -half(s1)), (s1, half(s1)), (s_start, half(s_start))]


def rail(seam, part):
    wall, s0, centre, _, _ = seam
    z0, z1 = part_z(part)
    face = bd.Polygon(*rail_profile(), align=None)
    return seam_plane(wall, s0, centre, z0).location * bd.extrude(face, amount=z1 - z0)


def slot(seam, part):
    wall, s0, centre, _, _ = seam
    z0, z1 = part_z(part)
    face = bd.Polygon(*rail_profile(CLEAR_RAIL, s_start=-0.01, end_extra=CLEAR_RAIL_END), align=None)
    return seam_plane(wall, s0, centre, z0 - 1).location * bd.extrude(face, amount=z1 - z0 + 2)


def _band(kind):
    data = json.loads((HERE.parent / "build" / "joint_section.json").read_text())
    faces = []
    for ring in data[kind]:
        f = bd.Polygon(*[tuple(p) for p in ring["exterior"]], align=None)
        for hole in ring["holes"]:
            f -= bd.Polygon(*[tuple(p) for p in hole], align=None)
        faces.append(f)
    return faces


def tongue():
    """On part 6's top edge, standing up into part 7."""
    solids = [bd.Pos(0, 0, ZJ - 0.5) * bd.extrude(f, amount=TONGUE_H + 0.5, dir=(0, 0, 1)) for f in _band("tongue")]
    out = solids[0]
    for s in solids[1:]:
        out += s
    return out


def groove():
    """In part 7's bottom edge."""
    solids = [bd.Pos(0, 0, ZJ - 1.0) * bd.extrude(f, amount=GROOVE_D + 1.0, dir=(0, 0, 1)) for f in _band("groove")]
    out = solids[0]
    for s in solids[1:]:
        out += s
    return out


# --- labels: engraved where they stay hidden --------------------------------------------
LABELS = False          # engraved names off: keeps every face clean (see README for the map)


def label_text(name, size=6.0, advance=5.0):
    chars, x0 = [], -advance * (len(name) - 1) / 2
    for i, ch in enumerate(name):
        chars.append(bd.Pos(x0 + i * advance, 0, 0) * bd.Text(ch, size, font="DejaVu Sans Mono",
                                                                font_style=bd.FontStyle.REGULAR))
    return bd.Compound(children=chars)


def label_cut(part, key):
    """0.4 mm deep on the inside face. Part 6: in the bottom 6 mm, behind the fixed hard panel
    (z -177.3 .. -171.5). Part 7: in the top 7 mm."""
    name = f"P{part}-{key}"
    z = Z0 + 3.0 if part == 6 else ZT - 4.0
    txt = bd.Pos(0, -2.2, 0) * bd.extrude(label_text(name), amount=0.8)   # text centred on z
    x0, x1, y0, y1 = CELLS[key]
    if key == "E":
        plane = bd.Plane(origin=(X_MID, YE_IN + 0.4, z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    elif key[1] == "L":
        ym = (max(y0, Y_OPEN) + min(y1, YE_IN - 30)) / 2
        plane = bd.Plane(origin=(XL_IN - 0.4, ym, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    else:
        ym = (max(y0, Y_OPEN) + min(y1, YE_IN - 30)) / 2
        plane = bd.Plane(origin=(XR_IN + 0.4, ym, z), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
    return plane.location * txt


# --- per piece: what to add and what to cut ------------------------------------------------
def cell_box(part, key, pad=0.0):
    """The piece's own space; pad widens it in x and y (to take in the rails it carries over a seam)."""
    x0, x1, y0, y1 = CELLS[key]
    z0, z1 = part_z(part)
    return box(x0 - pad, x1 + pad, y0 - pad, y1 + pad, z0 - 5, z1 + (TONGUE_H + 1 if part == 6 else 5))


def piece_add(part, key):
    adds = [rail(s, part) for s in SEAMS if s[3] == key]
    if part == 6:
        adds.append(tongue() & cell_box(part, key))
    if not adds:
        return None
    out = adds[0]
    for a in adds[1:]:
        out += a
    return out


def piece_cut(part, key):
    cuts = [slot(s, part) for s in SEAMS if s[4] == key]
    if part == 7:
        cuts.append(groove() & cell_box(part, key, pad=RAIL_DEPTH + 1.0))   # its own rails get the groove too
    if LABELS:
        cuts.append(label_cut(part, key))
    if not cuts:
        return None
    out = cuts[0]
    for c in cuts[1:]:
        out += c
    return out


def pieces():
    return [(p, k) for p in (6, 7) for k in CELLS]


@model
def joint_solids():
    """Every rail, slot, the tongue and the groove in the assembled frame (for checks and Rhino)."""
    kids = []
    for p in (6, 7):
        for i, s in enumerate(SEAMS):
            r = rail(s, p); r.label, r.color = f"p{p}_rail_{s[3]}_{s[4]}", "#c0392b"
            kids.append(r)
    t = tongue(); t.label, t.color = "p6_tongue", "#c0392b"
    kids.append(t)
    return bd.Compound(children=kids, label="joint_solids")


@model
def seam_fit_check():
    """One seam: a rail and the slot it runs in, as solids around them (a block minus the slot)."""
    s = SEAMS[2]
    block = seam_plane(s[0], s[1], s[2], -150).location * box(0, 8, -3, 3, 0, 40)   # the slotted piece only
    block -= slot(s, 6)
    block.label, block.color = "slotted_block", "#9aa5b1"
    r = rail(s, 6) & (seam_plane(s[0], s[1], s[2], -150).location * box(-1, 8, -3, 3, 0, 40))
    r.label, r.color = "rail", "#c0392b"
    return bd.Compound(children=[block, r], label="seam_fit_check")


@model
def tongue_fit_check():
    """A length of the joint: tongue against the groove cut from a block."""
    win = box(12870, 12890, -700, -660, ZJ - 3, ZJ + 6)
    block = (box(12870, 12890, -700, -660, ZJ, ZJ + 6)) - groove()
    block.label, block.color = "grooved_block", "#9aa5b1"
    t = tongue() & win
    t.label, t.color = "tongue", "#c0392b"
    return bd.Compound(children=[block, t], label="tongue_fit_check")


if __name__ == "__main__":
    joint_solids()
    seam_fit_check()
    tongue_fit_check()


# --- fit test: print this first ------------------------------------------------------------
TEST_RAIL_CLEAR = (0.10, 0.15, 0.20)
TEST_GROOVE_CLEAR = (0.15, 0.20, 0.25)


def _notches(solid, n, x0, y_mid, z_top):
    for i in range(n):
        x = x0 + 2.0 + i * 2.5
        solid -= box(x, x + 1.0, y_mid - 5, y_mid + 5, z_top - 1.0, z_top + 1)
    return solid


@model
def fit_test():
    """Wall stubs 4.46 mm thick, printed upright like the pieces.
    Row 1: three dovetail pairs (rail stub + slot stub), slot clearance 0.10 / 0.15 / 0.20 mm
    (1 / 2 / 3 notches on the slot stub). Row 2: one tongue stub and three groove stubs at
    0.15 / 0.20 / 0.25 mm per side (1 / 2 / 3 notches). Slide each pair together vertically."""
    kids, T, Hh = [], WALL, 20.0
    for i, c in enumerate(TEST_RAIL_CLEAR):
        x = i * 36.0
        a = box(x, x + 14, 0, T, 0, Hh)                                   # rail stub, seam at x+14
        prof = rail_profile()
        a += bd.Plane(origin=(x + 14, T / 2, 0), x_dir=(1, 0, 0), z_dir=(0, 0, 1)).location * \
            bd.extrude(bd.Polygon(*prof, align=None), amount=Hh)
        a.label, a.color = f"rail_stub_{i + 1}", "#c0392b"
        b = box(x + 18, x + 32, 0, T, 0, Hh)                              # slot stub, its seam face at x+18
        sl = rail_profile(c, s_start=-0.01, end_extra=CLEAR_RAIL_END)
        b -= bd.Plane(origin=(x + 18, T / 2, -1), x_dir=(1, 0, 0), z_dir=(0, 0, 1)).location * \
            bd.extrude(bd.Polygon(*sl, align=None), amount=Hh + 2)
        b = _notches(b, i + 1, x + 18 + 3.5, T / 2, Hh)
        b.label, b.color = f"slot_stub_{c:.2f}", "#efe9dc"
        kids += [a, b]
    y = 15.0
    t = box(0, 24, y, y + T, 0, 12) + box(0, 24, y + (T - 1.6) / 2, y + (T + 1.6) / 2, 11.5, 12 + TONGUE_H)
    t.label, t.color = "tongue_stub", "#c0392b"
    kids.append(t)
    for i, c in enumerate(TEST_GROOVE_CLEAR):
        x = 30 + i * 28.0
        w = 1.6 + 2 * c
        g = box(x, x + 24, y, y + T, 0, 12) - box(x - 1, x + 25, y + (T - w) / 2, y + (T + w) / 2, -1, GROOVE_D)
        g = _notches(g, i + 1, x + 4, y + T / 2, 12)
        g.label, g.color = f"groove_stub_{c:.2f}", "#efe9dc"
        kids.append(g)
    return bd.Compound(children=kids, label="fit_test")


if __name__ == "__main__":
    fit_test()
