"""Three nail-free joints for the suitcase, each working in both forms, on the Rhino model's geometry.

Every option uses the ring's T-slot twice:
- suitcase form: the panel's side rails fix straight onto the ring's uprights;
- shelf form: each link's shoe is fixed in the same slot at the height you choose,
  and a ball-lock pin (no tools) joins the link to the panel.

Models per option: <opt>_suitcase and <opt>_shelf hold the rebuilt rings and every new part at
all four corners; <opt>_cuts holds the cut tools to subtract from the Rhino parts.
"""

import build123d as bd
from cad import model

from base import (
    ACCENT, ALU, CUT, DARK, STEEL, X0, Y_F, Y_CH0, Y_CH1, LINK_X0, LINK_X1, RAIL_X0,
    T_LEG, box, cyl_x, cyl_y, four_corners, link_arm, mirror_x, mirror_y, panel_clevis_cut,
    quick_release_pin, ring, slot_profile_cut, t_block, tag,
)

PLATE_Y0 = Y_F - 8.0
HULL_Z = (-50.0, -40.0)          # where the arm leaves the shoe plate


def rings(slot_cuts):
    front = ring(slot_cuts)
    return [tag(front, "ring_front", ALU), tag(mirror_y(front), "ring_back", ALU)]


EXPLODE = 120.0                  # "pulled off" copies: panels 120 mm straight off the ring


def assemble(label, slot_cuts, panel_hw, link_hw, shelf, pulled=False):
    kids = rings(slot_cuts)
    if pulled:
        panel_hw = [(bd.Pos(0, -EXPLODE, 0) * s, lab, col) for s, lab, col in panel_hw]
    if shelf:
        parts = [(T_LEG * s, lab, col) for s, lab, col in panel_hw] + link_hw
        pin, pull = quick_release_pin()
        parts += [(pin, "quick_release_pin", STEEL), (pull, "pin_pull_ring", ACCENT)]
    else:
        parts = panel_hw
    kids += four_corners(parts)
    return bd.Compound(children=kids, label=label)


def cut_tools(label, slot_cuts, panel_cuts_closed):
    """Cut tools in the file's coordinates: ring cuts for the drawn rings, panel cuts for the
    panels as drawn (leg pose). BooleanDifference them from the matching Rhino objects."""
    ring_cut = slot_profile_cut()
    for c in slot_cuts:
        ring_cut += c
    parts = [(ring_cut, "cut_ring_slot", CUT)]
    panel_cut = panel_clevis_cut()
    for c in panel_cuts_closed:
        panel_cut += T_LEG * c
    parts.append((panel_cut, "cut_panel", CUT))
    return bd.Compound(children=four_corners(parts), label=label)


# --- Option A: drop-in T-blocks (windows in the slot lips) -------------------
# Lips get 14 mm windows every 40 mm. A T-block drops through a window and slides 20 mm down
# under the lip; a spring ball clicks into a dimple to hold it there.

A_WINDOWS = [210.0 - 40.0 * k for k in range(12)]
A_LOCKS = [w - 20.0 for w in A_WINDOWS]
A_PANEL = [110.0, -10.0, -130.0, -250.0]
A_LINK = [-50.0, -90.0]


def a_slot_cuts():
    cuts = [box(X0 - 7, X0 + 7, Y_F - 0.01, Y_CH0 + 0.01, w - 7, w + 7) for w in A_WINDOWS]
    cuts += [cyl_y(X0, z, Y_CH1 - 0.01, Y_CH1 + 0.7, 1.8) for z in A_LOCKS]     # detent dimples
    return cuts


def a_block(zc, y_face=Y_F):
    ball_c = (X0, Y_CH1 - 0.5 - 1.2, zc)
    blk = t_block(zc - 6, zc + 6, y_face) - bd.Pos(*ball_c) * bd.Sphere(2.0)
    return blk, bd.Pos(*ball_c) * bd.Sphere(2.0)


def a_panel_hw():
    parts = []
    for z in A_PANEL:
        blk, ball = a_block(z)
        parts += [(blk, "panel_t_block", STEEL), (ball, "detent_ball", DARK)]
    return parts


def a_link_hw():
    link = link_arm(*HULL_Z) + box(LINK_X0, LINK_X1, PLATE_Y0, Y_F - 0.2, -100, -40)
    parts = []
    for z in A_LINK:
        blk, ball = a_block(z, y_face=Y_F - 0.2)
        link += blk
        parts.append((ball, "detent_ball", DARK))
    return [(link, "link", STEEL)] + parts


@model
def a_suitcase():
    return assemble("A_drop_in_suitcase", a_slot_cuts(), a_panel_hw(), [], shelf=False)


@model
def a_suitcase_pulled():
    return assemble("A_drop_in_suitcase_pulled", a_slot_cuts(), a_panel_hw(), [], shelf=False, pulled=True)


@model
def a_shelf():
    return assemble("A_drop_in_shelf", a_slot_cuts(), a_panel_hw(), a_link_hw(), shelf=True)


@model
def a_cuts():
    return cut_tools("A_drop_in_cuts", a_slot_cuts(), [])


# --- Option B: spring index pins ---------------------------------------------
# Ø6.2 holes in the slot floor every 30 mm. Spring pins on the panel rails click into them in
# suitcase form; a captive shoe with the same pin sets the link's height in shelf form. Slide the
# red side tab to pull a pin.

B_HOLES = [220.0 - 30.0 * k for k in range(17)]
B_PANEL = [130.0, -200.0]
B_LINK_PIN = -80.0
B_LOAD_WINDOW = (170.0, 230.0)          # the shoe goes in and out here


def b_slot_cuts():
    cuts = [cyl_y(X0, z, Y_CH1 - 0.01, Y_CH1 + 5.0, 3.1) for z in B_HOLES]
    cuts.append(box(X0 - 7, X0 + 7, Y_F - 0.01, Y_CH0 + 0.01, *B_LOAD_WINDOW))
    return cuts


def spring_pin(z, y_head, tip=Y_CH1 + 4.5):
    pin = cyl_y(X0, z, y_head, tip, 3.0) + cyl_y(X0, z, y_head - 3, y_head, 4.5)
    bar = box(10917.0, X0 - 2.0, y_head - 3, y_head, z - 3, z + 3)
    pad = box(10913.0, 10917.0, y_head - 5, y_head + 2, z - 6, z + 6)
    return pin + bar, pad


def b_panel_hw():
    parts = []
    for z in B_PANEL:
        pin, pad = spring_pin(z, y_head=3153.0)
        parts += [(pin, "panel_spring_pin", STEEL), (pad, "pin_tab", ACCENT)]
    return parts


def b_panel_cuts():
    cuts = []
    for z in B_PANEL:
        cuts.append(cyl_y(X0, z, 3146.0, Y_F + 0.1, 3.3))                       # pin bore
        cuts.append(cyl_y(X0, z, 3143.0, 3153.2, 4.8))                          # head + spring counterbore
        cuts.append(box(RAIL_X0 - 0.1, X0, 3145.5, 3157.0, z - 3.5, z + 3.5))   # tab slot, 6 mm travel
    return cuts


def b_link_hw():
    shoe = t_block(-98, -42, y_face=Y_F - 0.2)
    link = link_arm(*HULL_Z) + box(LINK_X0, LINK_X1, PLATE_Y0, Y_F - 0.2, -100, -40) + shoe
    link -= cyl_y(X0, B_LINK_PIN, PLATE_Y0 - 1, Y_CH1, 3.2)
    pin, pad = spring_pin(B_LINK_PIN, y_head=3156.0)
    return [(link, "link_captive_shoe", STEEL), (pin, "link_spring_pin", STEEL), (pad, "pin_tab", ACCENT)]


@model
def b_suitcase():
    return assemble("B_index_pins_suitcase", b_slot_cuts(), b_panel_hw(), [], shelf=False)


@model
def b_suitcase_pulled():
    return assemble("B_index_pins_suitcase_pulled", b_slot_cuts(), b_panel_hw(), [], shelf=False, pulled=True)


@model
def b_shelf():
    return assemble("B_index_pins_shelf", b_slot_cuts(), b_panel_hw(), b_link_hw(), shelf=True)


@model
def b_cuts():
    return cut_tools("B_index_pins_cuts", b_slot_cuts(), b_panel_cuts())


# --- Option C: quarter-turn twist locks (no holes in the ring) ---------------
# A hammer head 6 mm wide passes the 8 mm mouth upright, then a quarter turn sets it across the
# 14 mm chamber behind the lips. Wing knobs on the panel; thumb knobs clamp the link anywhere.

C_PANEL = [130.0, -40.0, -210.0]
C_LINK = [-90.0, -70.0]
HEAD_Y0, HEAD_Y1 = Y_CH0 + 0.8, Y_CH1 - 1.2


def hammer_head(z):
    """Locked: long axis across the slot (X). 12.6 x 6 x 6 mm stadium."""
    core = box(X0 - 3.3, X0 + 3.3, HEAD_Y0, HEAD_Y1, z - 3, z + 3)
    return core + cyl_y(X0 - 3.3, z, HEAD_Y0, HEAD_Y1, 3) + cyl_y(X0 + 3.3, z, HEAD_Y0, HEAD_Y1, 3)


def c_panel_hw():
    parts = []
    for z in C_PANEL:
        bolt = hammer_head(z) + cyl_y(X0, z, 3134.8, HEAD_Y0, 3.0)
        knob = cyl_y(X0, z, 3134.8, 3138.8 - 0.01, 8.0) + box(X0 - 11, X0 + 11, 3130.8, 3134.8, z - 2.5, z + 2.5)
        knob -= cyl_y(X0, z, 3134.0, 3139.0, 3.0)
        parts += [(bolt, "panel_twist_lock", STEEL), (knob, "wing_knob", ACCENT)]
    return parts


def c_panel_cuts():
    return [cyl_y(X0, z, 3138.7, Y_F + 0.1, 3.2) for z in C_PANEL]


def c_link_hw():
    link = link_arm(*HULL_Z) + box(LINK_X0, LINK_X1, PLATE_Y0, Y_F - 0.2, -100, -40)
    parts = []
    for z in C_LINK:
        link -= cyl_y(X0, z, PLATE_Y0 - 1, Y_F + 1, 3.2)
        bolt = hammer_head(z) + cyl_y(X0, z, 3150.8, HEAD_Y0, 3.0)
        knob = cyl_y(X0, z, 3150.8, PLATE_Y0 - 0.01, 7.0) - cyl_y(X0, z, 3150.0, PLATE_Y0, 3.0)
        parts += [(bolt, "link_t_bolt", STEEL), (knob, "thumb_knob", ACCENT)]
    return [(link, "link", STEEL)] + parts


@model
def c_suitcase():
    return assemble("C_twist_lock_suitcase", [], c_panel_hw(), [], shelf=False)


@model
def c_suitcase_pulled():
    return assemble("C_twist_lock_suitcase_pulled", [], c_panel_hw(), [], shelf=False, pulled=True)


@model
def c_shelf():
    return assemble("C_twist_lock_shelf", [], c_panel_hw(), c_link_hw(), shelf=True)


@model
def c_cuts():
    return cut_tools("C_twist_lock_cuts", [], c_panel_cuts())


if __name__ == "__main__":
    for f in (a_suitcase, a_suitcase_pulled, a_shelf, a_cuts, b_suitcase, b_suitcase_pulled, b_shelf, b_cuts,
              c_suitcase, c_suitcase_pulled, c_shelf, c_cuts):
        f()


# --- detail pieces: a short length of the ring's left upright and the panel rail -------------
RAIL_COL = "#d6d9dc"


def clip_box(z0, z1, y0=3080.0, y1=3200.0):
    return box(10900.0, 10960.0, y0, y1, z0, z1)


def detail(label, slot_cuts, hw, panel_cuts, z0, z1, shelf=False, link_hw=()):
    from base import RAIL_X1, RAIL_Y0, RAIL_Y1
    window = clip_box(z0, z1)
    kids = [tag(ring(slot_cuts) & window, "ring_upright", ALU)]
    rail = box(RAIL_X0, RAIL_X1, RAIL_Y0, RAIL_Y1, -280.4, 279.6)
    for c in panel_cuts:
        rail -= c
    if shelf:
        rail = (T_LEG * rail) - panel_clevis_cut()
        rail &= clip_box(z0, z1, 3080, 3168.5)
        kids.append(tag(rail, "panel_rail", RAIL_COL))
        parts = [(T_LEG * s, lab, col) for s, lab, col in hw] + list(link_hw)
        pin, pull = quick_release_pin()
        parts += [(pin, "quick_release_pin", STEEL), (pull, "pin_pull_ring", ACCENT)]
    else:
        kids.append(tag(rail & clip_box(z0, z1), "panel_rail", RAIL_COL))
        parts = hw
    for s, lab, col in parts:
        piece = s & clip_box(z0, z1, 3000, 3200) if shelf else s & clip_box(z0 - 40, z1 + 40, 3000, 3200)
        if piece.volume > 1e-3:
            kids.append(tag(piece, lab, col))
    return bd.Compound(children=kids, label=label)


@model
def a_detail_suitcase():
    return detail("A_detail_suitcase", a_slot_cuts(), a_panel_hw(), [], -45.0, 35.0)


@model
def a_detail_shelf():
    return detail("A_detail_shelf", a_slot_cuts(), a_panel_hw(), [], -115.0, 10.0, shelf=True, link_hw=a_link_hw())


@model
def b_detail_suitcase():
    return detail("B_detail_suitcase", b_slot_cuts(), b_panel_hw(), b_panel_cuts(), 95.0, 165.0)


@model
def b_detail_shelf():
    return detail("B_detail_shelf", b_slot_cuts(), b_panel_hw(), b_panel_cuts(), -115.0, 10.0, shelf=True, link_hw=b_link_hw())


@model
def c_detail_suitcase():
    return detail("C_detail_suitcase", [], c_panel_hw(), c_panel_cuts(), -75.0, -5.0)


@model
def c_detail_shelf():
    return detail("C_detail_shelf", [], c_panel_hw(), c_panel_cuts(), -115.0, 10.0, shelf=True, link_hw=c_link_hw())


if __name__ == "__main__":
    for f in (a_detail_suitcase, a_detail_shelf, b_detail_suitcase, b_detail_shelf, c_detail_suitcase, c_detail_shelf):
        f()
