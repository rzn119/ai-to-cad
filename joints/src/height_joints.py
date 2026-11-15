"""Part 2: nail-free height adjustment of the box along the frame legs (shelf form).

Each model is one vertical leg rail of a frame (aluminium, x 0..30, y 0..18,
420 mm tall) and a piece of the box's side wall in front of it (y < 0).
Left: assembled. Right: "opened book" -- the box side swung round beside the
rail so the rail's face and the box's hardware both face the camera.
"""

import build123d as bd
from cad import model

from common import (
    ACCENT, ALU, CREAM, RAIL_H, RAIL_T, RAIL_W, STEEL,
    box, cyl_x, cyl_y, keyhole_cut, pair, stud,
)

WALL_Y0, WALL_Y1 = -16.0, -1.0          # box side wall, 1 mm off the rail face
WALL_X0, WALL_X1 = -40.0, 70.0
HINGE = WALL_X1 + 30.0
OPEN_X = 330.0
CX = RAIL_W / 2                          # hardware centre line


def rail_solid():
    return box(0, RAIL_W, 0, RAIL_T, 0, RAIL_H)


def c_channel():
    """Rail with an internal channel open towards the box: 14 mm mouth, 22 mm inside."""
    r = rail_solid()
    r -= box(4, 26, 3, 14, -1, RAIL_H + 1)
    r -= box(8, 22, -0.01, 3.01, -1, RAIL_H + 1)
    return r


def box_wall(z0, z1):
    return box(WALL_X0, WALL_X1, WALL_Y0, WALL_Y1, z0, z1)


def guide_block(z0, z1, head_y1=13.5):
    """T-shaped slider on the box that runs inside the C-channel (0.5 mm clearance each side)."""
    return box(8.5, 21.5, WALL_Y1, 3.5, z0, z1) + box(4.5, 25.5, 3.5, head_y1, z0, z1)


# --- 2-1: keyhole ladder -----------------------------------------------------

LADDER_PITCH = 45.0
LADDER_FIRST = 60.0
LADDER_N = 8
TRAVEL = 12.0
STUD_SLOTS = (2, 4)                      # the box hangs on these two keyholes


def keyhole_ladder():
    heads = [LADDER_FIRST + LADDER_PITCH * i for i in range(LADDER_N)]
    rail = rail_solid()
    for zh in heads:
        rail -= keyhole_cut(CX, zh, TRAVEL, 0.0, 3.0, 5.0, into=+1)
    stud_z = [heads[i] - TRAVEL for i in STUD_SLOTS]
    wall = box_wall(stud_z[0] - 40, stud_z[1] + 45)
    studs = [stud(CX, z, WALL_Y1, -WALL_Y1 + 3.2, out=+1) for z in stud_z]
    box_parts = [(wall, "box_side_wall", CREAM)] + [(s, "stud", STEEL) for s in studs]
    return pair("2-1_keyhole_ladder", [(rail, "leg_rail", ALU)], box_parts, HINGE, OPEN_X)


@model
def height_1_keyhole_ladder():
    return keyhole_ladder()


# --- 2-2: indexed channel + spring plunger -----------------------------------

INDEX_PITCH = 35.0
INDEX_FIRST = 70.0
INDEX_N = 10
PIN_D = 8.0
PIN_Z = INDEX_FIRST + 3 * INDEX_PITCH    # engaged in the 4th hole


def spring_plunger():
    rail = c_channel()
    for i in range(INDEX_N):
        rail -= cyl_y(CX, INDEX_FIRST + INDEX_PITCH * i, 13.9, RAIL_T + 0.1, PIN_D / 2 + 0.2)
    z = PIN_Z
    bore = cyl_y(CX, z, -40, 14, PIN_D / 2 + 0.2)
    wall = box_wall(z - 65, z + 65) - bore
    block = guide_block(z - 30, z + 30) - bore
    housing = cyl_y(CX, z, -36, WALL_Y0, 9) - bore      # spring lives in here
    pin = cyl_y(CX, z, -40, 17.5, PIN_D / 2)
    knob = cyl_y(CX, z, -48, -40, 11)
    box_parts = [(wall, "box_side_wall", CREAM), (block, "guide_block", STEEL),
                 (housing, "spring_housing", STEEL), (pin, "index_pin", STEEL),
                 (knob, "pull_knob", ACCENT)]
    return pair("2-2_spring_plunger", [(rail, "leg_rail_c_channel", ALU)], box_parts, HINGE, OPEN_X)


@model
def height_2_spring_plunger():
    return spring_plunger()


# --- 2-3: sawtooth rack + gravity pawl ---------------------------------------

TOOTH_PITCH = 22.0
TOOTH_DEPTH = 8.0
RACK_Z0 = 40.0
RACK_N = 16
LEDGE_INDEX = 6                          # the pawl rests on this tooth's ledge


def rack():
    """Sawtooth strip on the channel's back wall: flat ledges face up, slopes face down."""
    back, tip = 16.0, 14.0 - TOOTH_DEPTH
    pts = [(back, RACK_Z0), (14.0, RACK_Z0)]
    for i in range(RACK_N):
        top = RACK_Z0 + TOOTH_PITCH * (i + 1)
        pts += [(tip, top), (14.0, top)]
    pts.append((back, pts[-1][1]))
    face = bd.Plane.YZ * bd.Polygon(*pts, align=None)
    strip = bd.Pos(8, 0, 0) * bd.extrude(face, amount=14)
    return strip - c_channel()   # back face sits on the channel wall


def pawl_parts(ledge_z):
    """Pawl as a strut: tip on a ledge, pivot inside the box wall, release tab above."""
    pivot = (-6.0, ledge_z + 32.0)
    pts = [(7, ledge_z), (11, ledge_z), (-2, ledge_z + 26), (-2, ledge_z + 44),
           (-10, ledge_z + 44), (-10, ledge_z + 28)]
    pawl = bd.Pos(10, 0, 0) * bd.extrude(bd.Plane.YZ * bd.Polygon(*pts, align=None), amount=10)
    pin = cyl_x(pivot[0], pivot[1], 6, 24, 2)
    pawl -= cyl_x(pivot[0], pivot[1], 9, 21, 2.1)
    tab = box(10, 20, -14, -2, ledge_z + 44, ledge_z + 50)
    return pawl, pin, tab


def rack_and_pawl():
    rail = c_channel()
    ledge = RACK_Z0 + TOOTH_PITCH * (LEDGE_INDEX + 1)
    pawl, pin, tab = pawl_parts(ledge)
    wall = box_wall(ledge - 95, ledge + 70)
    wall -= box(8, 22, WALL_Y0 - 0.1, WALL_Y1 + 0.1, ledge + 10, ledge + 56)   # pawl pocket, open inside
    wall -= pin                                                                  # pivot pin holes
    block = guide_block(ledge - 75, ledge - 20, head_y1=5.5)   # low head: clears the rack teeth
    box_parts = [(wall, "box_side_wall", CREAM), (block, "guide_block", STEEL),
                 (pawl, "pawl", STEEL), (pin, "pawl_pivot", STEEL), (tab, "release_tab", ACCENT)]
    rail_parts = [(rail, "leg_rail_c_channel", ALU), (rack(), "sawtooth_rack", STEEL)]
    return pair("2-3_rack_and_pawl", rail_parts, box_parts, HINGE, OPEN_X)


@model
def height_3_rack_and_pawl():
    return rack_and_pawl()


# --- 2-4: T-slot + cam-lever clamp -------------------------------------------

CLAMP_Z = 190.0


def cam_clamp():
    rail = rail_solid()
    rail -= box(9, 21, -0.01, 5, -1, RAIL_H + 1)     # T-slot neck
    rail -= box(4, 26, 5, 13, -1, RAIL_H + 1)        # T-slot chamber
    z = CLAMP_Z
    rod_hole = cyl_y(CX, z, -20, 13, 4.5)
    wall = box_wall(z - 70, z + 70) - rod_hole
    t_nut = box(5, 25, 6, 12, z - 30, z + 30) - cyl_y(CX, z, 5, 13, 4.2)
    rod = cyl_y(CX, z, -30, 11, 4)
    washer = box(5, 25, -19, WALL_Y0, z - 15, z + 15) - rod_hole
    # lever: two eccentric cam cheeks either side of the rod, a bridge and a handle
    cheeks = cyl_x(-28, z, 5, 10.5, 9) + cyl_x(-28, z, 19.5, 25, 9)
    lever = cheeks + box(5, 25, -40, -30, z + 6, z + 14) + box(5, 25, -40, -34, z + 6, z + 75)
    pivot = cyl_x(-31, z, 4, 26, 2)
    lever -= pivot
    rod -= pivot
    box_parts = [(wall, "box_side_wall", CREAM), (t_nut, "t_nut", STEEL), (rod, "clamp_rod", STEEL),
                 (washer, "washer_plate", STEEL), (lever, "cam_lever", ACCENT), (pivot, "lever_pivot", STEEL)]
    return pair("2-4_cam_clamp", [(rail, "leg_rail_t_slot", ALU)], box_parts, HINGE, OPEN_X)


@model
def height_4_cam_clamp():
    return cam_clamp()


if __name__ == "__main__":
    height_1_keyhole_ladder()
    height_2_spring_plunger()
    height_3_rack_and_pawl()
    height_4_cam_clamp()
