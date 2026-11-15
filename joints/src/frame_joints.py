"""Part 1: nail-free joints between the aluminium frame and the suitcase body.

Each model is one front corner of the box. Left: assembled. Right: exploded,
the frame pulled forward (+Y) so the joint faces can be seen.
"""

import build123d as bd
from cad import model

from common import (
    ACCENT, ALU, CREAM, LEATHER, LEG, MAGNET, STEEL, WALL,
    box, cone_minus_y, corner_body, corner_frame, cyl_y, keyhole_cut, pair, stud,
)


HINGE = LEG + 25.0   # the opened copy swings the frame about this vertical line


# --- 1A: perimeter groove in the body, lip on the frame ----------------------

GROOVE_W, GROOVE_D = 4.0, 5.0
LIP_W, LIP_H = 3.6, 4.5          # 0.2 mm clearance per side, 0.5 mm at the bottom


def groove_and_lip(width, depth, lip_w, lip_h):
    c = WALL / 2
    g, l = width / 2, lip_w / 2
    groove = box(c - g, c + g, -depth, 0.01, c - g, LEG + 1) + box(c - g, LEG + 1, -depth, 0.01, c - g, c + g)
    lip = box(c - l, c + l, -lip_h, 0.01, c - l, LEG) + box(c - l, LEG, -lip_h, 0.01, c - l, c + l)
    body = corner_body() - groove
    frame, leather = corner_frame()
    frame = frame + lip
    return pair(
        "1A_groove_and_lip",
        [(body, "body", CREAM)],
        [(frame, "frame_with_lip", ALU), (leather, "leather", LEATHER)],
        HINGE,
    )


@model
def joint_1a_groove_lip():
    return groove_and_lip(GROOVE_W, GROOVE_D, LIP_W, LIP_H)


# --- 1B: keyhole slots in the body, mushroom studs on the frame -------------

KH_X = 24.0
KH_HEADS = (72.0, 142.0)
KH_TRAVEL = 12.0
KH_PLATE, KH_CHAMBER = 3.0, 5.0


def keyhole_frame():
    # local thickening of the side wall so the keyholes have material around them
    strip = box(WALL, 38, -30, 0, 0, LEG)
    body = corner_body(strip)
    for zh in KH_HEADS:
        body -= keyhole_cut(KH_X, zh, KH_TRAVEL, 0.0, KH_PLATE, KH_CHAMBER, into=-1)
    frame, leather = corner_frame()
    studs = [stud(KH_X, zh - KH_TRAVEL, 0.0, KH_PLATE + 0.2, out=-1) for zh in KH_HEADS]
    frame_parts = [(frame, "frame", ALU), (leather, "leather", LEATHER)]
    frame_parts += [(s, "stud", STEEL) for s in studs]
    return pair("1B_keyhole_slots", [(body, "body", CREAM)], frame_parts, HINGE)


@model
def joint_1b_keyhole():
    return keyhole_frame()


# --- 1C: hidden magnets + tapered locating pins ------------------------------

MAG_D, MAG_T = 10.0, 3.0
POCKET_CLEAR = 0.1
MAGNETS = [(WALL / 2, 45.0), (WALL / 2, 135.0), (90.0, WALL / 2)]   # (x, z)
PINS = [(WALL / 2, 95.0), (135.0, WALL / 2)]


def magnets_and_pins():
    body = corner_body()
    frame, leather = corner_frame()
    body_mags, frame_mags, pins = [], [], []
    pr = MAG_D / 2 + POCKET_CLEAR
    for x, z in MAGNETS:
        body -= cyl_y(x, z, -(MAG_T + POCKET_CLEAR), 0.01, pr)
        frame -= cyl_y(x, z, -0.01, MAG_T + POCKET_CLEAR, pr)
        body_mags.append(cyl_y(x, z, -MAG_T, 0, MAG_D / 2))
        frame_mags.append(cyl_y(x, z, 0, MAG_T, MAG_D / 2))
    for x, z in PINS:
        body -= cone_minus_y(x, z, 0.01, 5.3, 3.2, 2.2)
        pins.append(cone_minus_y(x, z, 0.0, 5.0, 3.0, 2.0))
    body_parts = [(body, "body", CREAM)] + [(m, "magnet_body", MAGNET) for m in body_mags]
    frame_parts = [(frame, "frame", ALU), (leather, "leather", LEATHER)]
    frame_parts += [(m, "magnet_frame", MAGNET) for m in frame_mags]
    frame_parts += [(p, "locating_pin", STEEL) for p in pins]
    return pair("1C_magnets_and_pins", body_parts, frame_parts, HINGE)


@model
def joint_1c_magnets():
    return magnets_and_pins()


# --- 1D: over-centre draw latch on the side face -----------------------------

LATCH_Z = 80.0


def draw_latch():
    body = corner_body()
    frame, leather = corner_frame()
    z = LATCH_Z
    # base plate screwed/riveted to the body's side face (x=0 is the outer side face)
    base = box(-4, 0, -44, -12, z - 12, z + 12)
    # hinge knuckle + lever the user flips
    knuckle = bd.Pos(-6, -16, z) * bd.Cylinder(3, 24)          # axis along Z
    lever = box(-12, -6, -42, -16, z - 10, z + 10)
    tab = box(-15, -12, -46, -38, z - 10, z + 10)
    # wire loop from the lever to the keeper on the frame
    r = 1.2
    loop = cyl_y(-9, z - 8, -18, 7.5, r) + cyl_y(-9, z + 8, -18, 7.5, r)
    loop += bd.Pos(-9, 7.5, z) * bd.Cylinder(r, 16 + 2 * r)       # crossbar sits behind the keeper's hook
    # keeper (catch) on the frame's side face
    keeper = box(-5, 0, 3, 11, z - 11, z + 11) + box(-11, -5, 9, 12, z - 11, z + 11)
    loop = loop - lever - knuckle - keeper
    base, lever = base - knuckle, lever - knuckle   # holes for the hinge pin
    body_parts = [(body, "body", CREAM), (base, "latch_base", STEEL),
                  (knuckle, "latch_hinge", STEEL), (lever, "latch_lever", STEEL),
                  (tab, "latch_tab", ACCENT), (loop, "latch_wire_loop", STEEL)]
    frame_parts = [(frame, "frame", ALU), (leather, "leather", LEATHER), (keeper, "latch_keeper", STEEL)]
    return pair("1D_draw_latch", body_parts, frame_parts, HINGE)


@model
def joint_1d_latch():
    return draw_latch()


if __name__ == "__main__":
    joint_1a_groove_lip()
    joint_1b_keyhole()
    joint_1c_magnets()
    joint_1d_latch()
