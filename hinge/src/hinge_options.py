"""Three ways to make the cone-pivot hinge in hinge.3dm hold an angle, built on its geometry, in
the .3dm's coordinates (mm). Pivot axis along x through (y, z) = (AY, AZ); the arm lies along +y
at 0 deg and folds up and back to 180 deg (rotation about +x).

A  click detent   - 13 V-notches on the back of the knuckle, every 15 deg; a V-nub on a springy
                    bridge in the channel floor clicks into them. No hardware, push to move.
B  ratchet        - saw notches every 30 deg; a pawl (cantilever spring) in the floor lets the arm
                    rise freely, click by click, and stops it being pushed down. Press the pawl's
                    front end down to lower the arm.
C  clamp          - the cone pivots replaced by an M4 bolt with a printed thumb knob; the walls
                    beside the knuckle are slit into flexible ears, so tightening the knob clamps
                    the knuckle at any angle.
Clearance between parts that move: 0.2 mm; slits 0.8 mm (as in the original, 0.19 at the knuckle faces).
"""
import math

import build123d as bd
from cad import model
from shapely.geometry import Polygon as SPoly

MIN = bd.Align.MIN
CLEAR = 0.20

# --- the original, measured from hinge.3dm ---------------------------------------------------
XC, AY, AZ, R = 10919.40, -397.146, -162.16, 6.18          # axis (x centre), knuckle radius
BX0, BX1, BY0, BY1, BZ0, BZ1 = 10910.472, 10928.330, -429.454, -384.749, -177.237, -157.236
CX0, CX1, CY0, CZ0 = 10913.596, 10925.204, -428.592, -169.236   # channel (open top and front)
KX0, KX1 = 10913.782, 10925.019                             # knuckle faces
AX0, AX1 = 10915.382, 10923.420                             # arm sides
BOSS_R, BOSS_TIP_R, BOSS_H = 4.33, 0.48, 4.204              # cone bosses on the walls
SLOPE = (BOSS_R - BOSS_TIP_R) / BOSS_H
ARM = [(-380.111, -167.944), (-380.111, -157.945), (-392.73, -158.057), (AY, -158.10), (AY, -168.15)]
END_Y0, END_Y1 = -380.111, -368.495                         # the end piece (layer screws/nails)
END_Z0, END_Z1 = -167.944, -157.893
STEP_DEG = 15
ANGLES = list(range(0, 181, STEP_DEG))                      # 0, 15, ... 180


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=(MIN, MIN, MIN))


AXIS = bd.Axis((XC, AY, AZ), (1, 0, 0))


def turned(shape, deg):
    """Rotate about the hinge axis (positive: the arm lifts)."""
    return shape.rotate(AXIS, deg)


def cone_x(x_base, r_base, x_tip, r_tip):
    h = abs(x_tip - x_base)
    c = bd.Cone(r_base, r_tip, h)                          # base at -h/2, tip at +h/2 along z
    rot = bd.Rot(0, -90, 0) if x_tip < x_base else bd.Rot(0, 90, 0)
    return bd.Pos((x_base + x_tip) / 2, AY, AZ) * rot * c


def yz_prism(pts, x0, x1):
    """Polygon in the (y, z) plane swept along x from x0 to x1."""
    pl = bd.Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))   # local (u, v) = (y, z)
    return bd.extrude(pl.location * bd.Polygon(*pts, align=None), amount=x1 - x0, dir=(1, 0, 0))


def grow(pts, d):
    return list(SPoly(pts).buffer(d, join_style=2, mitre_limit=4).exterior.coords)[:-1]


# --- original parts ---------------------------------------------------------------------------
def connector_shell():
    return box(BX0, BX1, BY0, BY1, BZ0, BZ1) - box(CX0, CX1, CY0, BY1 + 1, CZ0, BZ1 + 1)


def bosses():
    return (cone_x(CX1, BOSS_R, CX1 - BOSS_H, BOSS_TIP_R)
            + cone_x(CX0, BOSS_R, CX0 + BOSS_H, BOSS_TIP_R))    # the left one is missing in the .3dm


def knuckle_arm():
    k = bd.Pos(XC, AY, AZ) * bd.Rot(0, 90, 0) * bd.Cylinder(R, KX1 - KX0)
    return k + yz_prism(ARM, AX0, AX1)


def recesses():
    """Cone sockets 0.2 mm off the bosses (as in the .3dm)."""
    d = CLEAR / math.cos(math.atan(SLOPE))                   # radial growth for 0.2 mm normal gap
    def r_at(x_from_tip):
        return BOSS_TIP_R + SLOPE * x_from_tip + d
    out = None
    for wall, sgn in ((CX1, -1), (CX0, 1)):
        tip = wall + sgn * BOSS_H                            # boss tip
        rtip = tip + sgn * CLEAR                             # socket bottom 0.2 further in
        far = wall - sgn * 0.3                               # past the knuckle face
        c = cone_x(far, r_at(abs(far - tip)), rtip, r_at(-CLEAR))
        out = c if out is None else out + c
    return out


def end_piece():
    s = box(AX0, AX1, END_Y0, END_Y1, END_Z0, END_Z1) - box(AX0 - 1, AX1 + 1, -375.553, -370.328, -162.91, END_Z1 + 1)
    return s


# --- A: click detent --------------------------------------------------------------------------
SPR_X0, SPR_X1, SLIT = XC - 3.0, XC + 3.0, 0.8              # spring 6 mm wide, 0.8 mm slits
A_Y0, A_Y1, A_T = -411.0, -386.5, 1.0                       # bridge (fixed both ends), 1.0 thick
A_DEPTH, A_W = 0.60, 0.90                                   # nub reaches 0.6 inside the rim


def a_nub_profile():
    tip = AZ - R + A_DEPTH
    return [(AY - A_W, CZ0 - 0.01), (AY - A_W, tip - A_W), (AY, tip), (AY + A_W, tip - A_W), (AY + A_W, CZ0 - 0.01)]


# --- B: ratchet -------------------------------------------------------------------------------
B_Y0, B_Y1, B_T = -410.0, BY1, 1.2                          # pawl root at the back, free at the front
B_DEPTH = 1.0
B_ANGLES = list(range(0, 181, 30))                       # a ratchet tooth needs a 30 deg pitch on this knuckle


def b_tooth_profile():
    top = AZ - R + B_DEPTH
    # back face a 55 deg ramp (the rim pushes the pawl down as the arm rises); front face vertical
    run = (top - CZ0) / math.tan(math.radians(55))
    return [(AY - 0.4 - run, CZ0 - 0.01), (AY - 0.4, top), (AY + 0.4, top), (AY + 0.4, CZ0 - 0.01)]


def notches(profile, angles):
    """The tooth grown by 0.2 mm, placed where it sits at each angle, in the arm's own frame."""
    g = yz_prism(grow(profile, CLEAR), SPR_X0 - CLEAR, SPR_X1 + CLEAR)
    out = None
    for a in angles:
        n = turned(g, -a)
        out = n if out is None else out + n
    return out


def spring_cuts(y0, y1, t, open_front):
    """Slits beside the spring and a pocket under it, open to the bottom (or, printed on its side,
    to that side), so the spring is a plain wall in print."""
    yf = y1 + (1 if open_front else 0)
    s = box(SPR_X0 - SLIT, SPR_X0, y0, yf, CZ0 - t - 0.01, CZ0 + 0.01)
    s += box(SPR_X1, SPR_X1 + SLIT, y0, yf, CZ0 - t - 0.01, CZ0 + 0.01)
    s += box(SPR_X0 - SLIT, SPR_X1 + SLIT, y0, yf, BZ0 - 1, CZ0 - t)
    return s


def spring_tooth(profile):
    return yz_prism(profile, SPR_X0, SPR_X1)


# --- C: clamp ---------------------------------------------------------------------------------
BOLT_D, HOLE_D = 4.0, 4.4
EAR_Y0, EAR_ROOT_Z, EAR_SLIT, EAR_GROOVE = -406.5, -174.0, 0.8, 0.8
KNOB_D, KNOB_T, NUT_AF, NUT_T = 18.0, 6.0, 7.0, 3.2


def c_axis_hole(x0, x1, d):
    return bd.Pos((x0 + x1) / 2, AY, AZ) * bd.Rot(0, 90, 0) * bd.Cylinder(d / 2, x1 - x0)


def c_ear_cuts():
    s = None
    for wx0, wx1, gx0, gx1 in ((BX0 - 1, CX0, CX0, CX0 + EAR_GROOVE), (CX1, BX1 + 1, CX1 - EAR_GROOVE, CX1)):
        slit = box(wx0, wx1, EAR_Y0 - EAR_SLIT, EAR_Y0, EAR_ROOT_Z, BZ1 + 1)       # behind the ear
        slit += box(gx0, gx1, EAR_Y0 - EAR_SLIT, BY1 + 1, EAR_ROOT_Z, CZ0 + 0.01)  # groove in the floor
        s = slit if s is None else s + slit
    return s


def c_knob():
    k = bd.Pos(BX0 - KNOB_T / 2, AY, AZ) * bd.Rot(0, 90, 0) * bd.Cylinder(KNOB_D / 2, KNOB_T)
    for i in range(12):                                         # finger grooves
        a = math.radians(i * 30)
        k -= bd.Pos(BX0 - KNOB_T / 2, AY + KNOB_D / 2 * math.cos(a), AZ + KNOB_D / 2 * math.sin(a)) * \
            bd.Rot(0, 90, 0) * bd.Cylinder(1.3, KNOB_T + 1)
    k -= c_axis_hole(BX0 - KNOB_T - 1, BX0 + 1, HOLE_D)
    hexp = bd.Pos(BX0 - KNOB_T - 0.01, AY, AZ) * bd.Rot(0, 90, 0) * bd.extrude(
        bd.RegularPolygon((NUT_AF + 0.3) / math.sqrt(3), 6), amount=NUT_T + 0.3)
    return k - hexp


def c_bolt():
    """M4 x 25 hex-socket bolt and nut, for show."""
    head = bd.Pos(BX1 + 1.4, AY, AZ) * bd.Rot(0, 90, 0) * bd.Cylinder(3.5, 2.8)
    shank = c_axis_hole(BX1 - 25, BX1, BOLT_D)
    nut = bd.Pos(BX0 - KNOB_T + 0.3, AY, AZ) * bd.Rot(0, 90, 0) * bd.extrude(
        bd.RegularPolygon(NUT_AF / math.sqrt(3), 6), amount=NUT_T)
    return head + shank + nut


# --- the options ------------------------------------------------------------------------------
def option(name):
    """Returns dict: connector, arm (knuckle + arm), end, extras (list of (label, solid))."""
    con, arm, extras = connector_shell(), knuckle_arm(), []
    if name in ("original", "A", "B"):
        con, arm = con + bosses(), arm - recesses()
    if name == "A":
        con = con - spring_cuts(A_Y0, A_Y1, A_T, False) + spring_tooth(a_nub_profile())
        arm = arm - notches(a_nub_profile(), ANGLES)
    elif name == "B":
        con = con - spring_cuts(B_Y0, B_Y1, B_T, True) + spring_tooth(b_tooth_profile())
        arm = arm - notches(b_tooth_profile(), B_ANGLES)
    elif name == "C":
        con = con - c_ear_cuts() - c_axis_hole(BX0 - 1, BX1 + 1, HOLE_D)
        arm = arm - c_axis_hole(KX0 - 1, KX1 + 1, HOLE_D)
        extras = [("knob", c_knob()), ("bolt_nut_M4x25", c_bolt())]
    return {"connector": con, "arm": arm, "end": end_piece(), "extras": extras}


COL = {"connector": "#8fb0d8", "arm": "#efe9dc", "end": "#d0614d", "knob": "#3c4650", "bolt_nut_M4x25": "#9aa0a6"}


def compound(name, deg=0):
    o = option(name)
    kids = []
    for lab in ("connector", "arm", "end"):
        s = o[lab] if lab == "connector" else turned(o[lab], deg)
        s.label, s.color = f"{name}_{lab}", COL[lab]
        kids.append(s)
    for lab, s in o["extras"]:
        s.label, s.color = f"{name}_{lab}", COL[lab]
        kids.append(s)
    return bd.Compound(children=kids, label=f"hinge_{name}")


@model
def hinge_A():
    return compound("A")


@model
def hinge_B():
    return compound("B")


@model
def hinge_C():
    return compound("C")


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    for name in ("original", "A", "B", "C"):
        o = option(name)
        d = root / "build" / name
        d.mkdir(parents=True, exist_ok=True)
        parts = [("connector", o["connector"]), ("arm", o["arm"]), ("end", o["end"])] + o["extras"]
        for lab, s in parts:
            bd.export_stl(s, str(d / f"{lab}.stl"), tolerance=0.005, angular_tolerance=0.05)
            print(name, lab, round(s.volume, 1), "mm3", "valid" if s.is_valid else "INVALID")
        if name != "original":
            model.export({"A": hinge_A, "B": hinge_B, "C": hinge_C}[name](), root / "exports" / f"hinge_{name}.step")
    # print files, placed on the plate. A, B: printed in place, upright as in the .3dm (floor on
    # the plate). C: connector upright, arm on its side, knob on its outer face.
    pr = root / "exports" / "print"
    def on_bed(shapes, side=False):
        rot = [(bd.Rot(0, -90, 0) * x if side else x) for x in shapes]
        bb = bd.Compound(children=rot).bounding_box()
        return [bd.Pos(-bb.min.X - bb.size.X / 2, -bb.min.Y - bb.size.Y / 2, -bb.min.Z) * x for x in rot]
    for name in ("A", "B", "C"):
        o = option(name)
        (pr / name).mkdir(parents=True, exist_ok=True)
        for f in (pr / name).glob("*.stl"):
            f.unlink()
        if name in ("A", "B"):
            plate = [("connector", o["connector"]), ("arm_with_end", o["arm"] + o["end"])]
            for (lab, _), s in zip(plate, on_bed([x for _, x in plate])):
                bd.export_stl(s, str(pr / name / f"hinge_{name}_{lab}.stl"), tolerance=0.005, angular_tolerance=0.05)
        else:
            for lab, s, side in (("connector", o["connector"], False), ("arm_with_end", o["arm"] + o["end"], True),
                                 ("knob", o["extras"][0][1], True)):
                bd.export_stl(on_bed([s], side)[0], str(pr / name / f"hinge_C_{lab}.stl"), tolerance=0.005, angular_tolerance=0.05)
    # for the viewer: the spring (bridge / pawl with its tooth) on its own, and the connector without it
    for name, prof, (y0, y1, t) in (("A", a_nub_profile(), (A_Y0, A_Y1, A_T)), ("B", b_tooth_profile(), (B_Y0, B_Y1, B_T))):
        con = option(name)["connector"]
        top = max(z for _, z in prof) + 0.05
        cutbox = box(SPR_X0, SPR_X1, y0, y1, CZ0 - t - 0.01, top)
        spring = con & cutbox
        bd.export_stl(con - cutbox, str(root / "build" / name / "connector_fixed.stl"), tolerance=0.005, angular_tolerance=0.05)
        bd.export_stl(spring, str(root / "build" / name / "spring.stl"), tolerance=0.005, angular_tolerance=0.05)
        print(name, "spring", round(spring.volume, 1))
    json.dump({"XC": XC, "AY": AY, "AZ": AZ, "R": R, "ANGLES": ANGLES, "CZ0": CZ0,
               "A": {"angles": ANGLES, "profile": a_nub_profile(), "spring": [SPR_X0, SPR_X1, A_Y0, A_Y1, A_T], "span": [A_Y0, A_Y1]},
               "B": {"angles": B_ANGLES, "profile": b_tooth_profile(), "spring": [SPR_X0, SPR_X1, B_Y0, B_Y1, B_T], "span": [B_Y0, B_Y1]}},
              open(root / "build" / "params.json", "w"), indent=1)
