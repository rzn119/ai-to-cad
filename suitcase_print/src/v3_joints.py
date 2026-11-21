"""Hidden joints for the updated part_6_and_7.3dm (pieces split in Rhino), 0.2 mm clearance.

Positions come from build/v3/joints.json (tools/v3_prepare.py places them against the traced walls).
Assembled frame: part 7 where it is in the .3dm; part 6 stacked on it (moved +DX, +DZ).

- Ring keys, joint between part 6 (top) and part 7 (bottom): a key 12 x 1.6 x 4.0 mm on part 7's
  top edge (top edges chamfered 0.4) into a pocket 12.4 x 2.0 x 4.4 mm in part 6's bottom edge.
- Floor keys, part 7's floor (5.7 mm thick): a tab 12 x 2.0 mm standing 3.0 mm out of one edge, at
  mid-thickness, into a pocket 12.4 x 2.4 x 3.4 mm in the next edge. Between floor pieces, from the
  bottom wall into the floor, and from the walls into the floor panels.
- Bayonet T-locks, part 7's centre floor seam: a T-shaped tab (1.6 mm neck, 3.2 mm head, 3.0 mm
  out) runs in a T-slot 0.2 mm larger all round; a straight window 16 mm along the seam lets it in. Push the halves together at the windows, slide the right half 16 mm towards the
  open end, and the halves cannot be pulled apart.
"""
import json
import math
from pathlib import Path

import build123d as bd
from cad import model

MIN = bd.Align.MIN
ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "build" / "v3" / "joints.json").read_text())
F = SPEC["frame"]
DX, DZ, ZJ, ZF, XC = F["DX"], F["DZ"], F["ZJ"], F["ZF"], F["XC"]

CLEAR = 0.20
# ring keys
KEY_L, KEY_W, KEY_H, KEY_EMBED = 10.0, 1.6, 4.0, 0.5
# part 7 wall-seam tabs (in the cut face, 4.46 mm wall)
SEAM_W, SEAM_H = 1.6, 12.0
# part 6 sliding T-rails (in the cut face): 1.2 mm neck for 1.2 mm, then a 2.0 mm head to 3.0 mm out.
# Square shoulders catch after 0.2 mm of pull (a dovetail that fits a 4.46 mm wall tapers so little
# that it let the seam open 2.5 mm before gripping).
RAIL_NECK, RAIL_NECK_D, RAIL_HEAD, RAIL_D, RAIL_END = 1.2, 1.2, 2.0, 3.0, 0.2
# floor keys
TAB_L, TAB_H, TAB_D, TAB_EMBED = 12.0, 2.0, 3.0, 0.5
# bayonet (T-head)
BAY_L, BAY_NECK, BAY_HEAD, BAY_NECK_D, BAY_D, BAY_SLIDE = 12.0, 1.6, 3.2, 1.5, 3.0, 16.0


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=(MIN, MIN, MIN))


def centred(cx, cy, lx, ly, z0, z1):
    return box(cx - lx / 2, cx + lx / 2, cy - ly / 2, cy + ly / 2, z0, z1)


def ring_key(k):
    lx, ly = (KEY_W, KEY_L) if k["along_y"] else (KEY_L, KEY_W)
    s = centred(k["x"], k["y"], lx, ly, ZJ - KEY_EMBED, ZJ + KEY_H)
    top = s.edges().group_by(bd.Axis.Z)[-1]
    return bd.chamfer(top, 0.4)


def ring_pocket(k):
    l, w = KEY_L + 2 * CLEAR, KEY_W + 2 * CLEAR
    lx, ly = (w, l) if k["along_y"] else (l, w)
    return centred(k["x"], k["y"], lx, ly, ZJ - 1.0, ZJ + KEY_H + 2 * CLEAR)


def _slab(j, length, height, d0, d1):
    """Box at a seam: `length` along the seam, `height` in z about the floor's mid-plane, from d0
    to d1 measured from the seam plane in the key's pointing direction."""
    s = j["sign"]
    a, b = sorted((s * d0, s * d1))
    z0, z1 = j["z"] - height / 2, j["z"] + height / 2
    if j["axis"] == "y":
        return box(j["x"] - length / 2, j["x"] + length / 2, j["y"] + a, j["y"] + b, z0, z1)
    return box(j["x"] + a, j["x"] + b, j["y"] - length / 2, j["y"] + length / 2, z0, z1)


def seam_tab(j):
    return _slab(j, SEAM_W, SEAM_H, -TAB_EMBED, TAB_D)


def seam_pocket(j):
    return _slab(j, SEAM_W + 2 * CLEAR, SEAM_H + 2 * CLEAR, -0.01, TAB_D + 2 * CLEAR)


def _rail_profile(clear, s0, s1):
    """(s, t): s out from the seam, t across the wall. A T: neck, then head. clear > 0: the slot,
    every face moved out by `clear`."""
    n, h = RAIL_NECK / 2 + clear, RAIL_HEAD / 2 + clear
    sn = RAIL_NECK_D - clear
    return [(s0, -n), (sn, -n), (sn, -h), (s1, -h), (s1, h), (sn, h), (sn, n), (s0, n)]


def _rail_solid(r, profile, z0, z1):
    """Profile in the plane across the seam: s along the wall away from the seam, t across it."""
    if r["axis"] == "y":     # side wall: s -> +y, t -> x about the wall centre line
        plane = bd.Plane(origin=(r["centre"], r["s"], z0), x_dir=(0, 1, 0), z_dir=(0, 0, 1))
    else:                    # end / bottom wall: s -> +x, t -> y about the wall centre line
        plane = bd.Plane(origin=(r["s"], r["centre"], z0), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
    face = plane.location * bd.Polygon(*profile, align=None)
    return bd.extrude(face, amount=z1 - z0, dir=(0, 0, 1))


def rail(r):
    return _rail_solid(r, _rail_profile(0.0, -TAB_EMBED, RAIL_D), r["z0"], r["z1"])


def rail_slot(r):
    z0, z1 = r["z0"] - CLEAR, r["z1"] + CLEAR
    if r["open"] in ("both", "bottom"):
        z0 = ZJ - 2.0                        # through part 6's bottom edge
    if r["open"] in ("both", "top"):
        z1 = ZJ + 92.32 + 2.0                # through part 6's top edge
    return _rail_solid(r, _rail_profile(CLEAR, -0.01, RAIL_D + RAIL_END), z0, z1)


def floor_tab(j):
    return _slab(j, TAB_L, TAB_H, -TAB_EMBED, TAB_D)


def floor_pocket(j):
    return _slab(j, TAB_L + 2 * CLEAR, TAB_H + 2 * CLEAR, -0.01, TAB_D + 2 * CLEAR)


def _bay_profile(clear, d_end=None):
    """(p, h): p out from the seam (+x), h about the floor's mid-plane. A T: neck 1.6 mm tall for
    the first 1.5 mm, then a head 3.2 mm tall to 3.0 mm. With clear > 0 it is the slot: every face
    moved out by `clear`, so a locked tab catches after 0.2 mm of pull."""
    n, hd = BAY_NECK / 2 + clear, BAY_HEAD / 2 + clear
    p0 = -TAB_EMBED if clear == 0 else -0.01
    pn = BAY_NECK_D - clear                       # where the head starts
    pe = BAY_D + clear
    return [(p0, -n), (pn, -n), (pn, -hd), (pe, -hd), (pe, hd), (pn, hd), (pn, n), (p0, n)]


def _bay_extrude(profile, y0, y1):
    """Profile (p, h) in the x-z plane at the seam (x = XC + p, z = ZF + h), swept along +y."""
    plane = bd.Plane(origin=(XC, y0, ZF), x_dir=(1, 0, 0), z_dir=(0, 1, 0))   # its local y is -z
    face = plane.location * bd.Polygon(*[(p, -h) for p, h in profile], align=None)
    return bd.extrude(face, amount=y1 - y0, dir=(0, 1, 0))


def bayonet_tab(j):
    return _bay_extrude(_bay_profile(0.0), j["y"] - BAY_L / 2, j["y"] + BAY_L / 2)


def bayonet_slot(j):
    """Slot in the right piece: the dovetail channel from the window to the locked position, plus
    the window (straight-sided, as tall as the tab's tip + clearance)."""
    y_lock, y_win = j["y"], j["y"] - BAY_SLIDE
    half_l = BAY_L / 2 + CLEAR
    channel = _bay_extrude(_bay_profile(CLEAR), y_win - half_l, y_lock + half_l)
    h = BAY_HEAD / 2 + CLEAR
    window = box(XC - 0.01, XC + BAY_D + CLEAR, y_win - half_l, y_win + half_l, ZF - h, ZF + h)
    return channel + window


# --- per piece -------------------------------------------------------------------------
def piece_names():
    names = set()
    for k in SPEC["ring_keys"]:
        names |= {k["on"], k["into"]}
    for j in SPEC["floor"] + SPEC.get("rails", []):
        names |= {j["on"], j["into"]}
    return sorted(names)


def adds_cuts(name):
    adds, cuts = [], []
    for k in SPEC["ring_keys"]:
        if k["on"] == name:
            adds.append(ring_key(k))
        if k["into"] == name:
            cuts.append(ring_pocket(k))
    for r in SPEC.get("rails", []):
        if r["on"] == name:
            adds.append(rail(r))
        if r["into"] == name:
            cuts.append(rail_slot(r))
    for j in SPEC["floor"]:
        tab, pocket = {"bayonet": (bayonet_tab, bayonet_slot), "seamkey": (seam_tab, seam_pocket)}.get(
            j["kind"], (floor_tab, floor_pocket))
        if j["on"] == name:
            adds.append(tab(j))
        if j["into"] == name:
            cuts.append(pocket(j))
    def fuse(lst):
        if not lst:
            return None
        out = lst[0]
        for s in lst[1:]:
            out += s
        return out
    return fuse(adds), fuse(cuts)


@model
def v3_joint_solids():
    kids = []
    for name in piece_names():
        a, c = adds_cuts(name)
        if a is not None:
            a.label, a.color = f"{name} add", "#c0392b"; kids.append(a)
    return bd.Compound(children=kids, label="v3_joint_solids")


@model
def bayonet_fit_check():
    """One bayonet in its locked place: the right piece's floor (a block) with the slot cut, and the tab."""
    j = next(j for j in SPEC["floor"] if j["kind"] == "bayonet" and j["on"] == "P7-F2-L")
    block = box(XC, XC + 20, j["y"] - 30, j["y"] + 15, -177.24, -171.55) - bayonet_slot(j)
    block.label, block.color = "right_floor", "#9aa5b1"
    tab = bayonet_tab(j) & box(XC, XC + 20, j["y"] - 30, j["y"] + 15, -180, -160)
    tab.label, tab.color = "tab", "#c0392b"
    return bd.Compound(children=[block, tab], label="bayonet_fit_check")


if __name__ == "__main__":
    v3_joint_solids()
    bayonet_fit_check()
