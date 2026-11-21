"""Write each piece's joint geometry (add / cut STL, assembled frame) for tools/v3_make_pieces.py,
and STEP files for Rhino placed where the pieces are in the .3dm. Run: cad run src/v3_build.py"""
from pathlib import Path

import build123d as bd
from cad import model

import v3_joints as v

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "v3" / "joints"
OUT.mkdir(parents=True, exist_ok=True)


def for_rhino(part):
    kids = []
    for name in v.piece_names():
        if not name.startswith(f"P{part}"):
            continue
        a, c = v.adds_cuts(name)
        for kind, s, col in (("add", a, "#c0392b"), ("cut", c, "#e67e22")):
            if s is None:
                continue
            if part == 6:                       # back to where part 6 is in the .3dm
                s = bd.Pos(-v.DX, 0, -v.DZ) * s
            s.label, s.color = f"{name} {kind}", col
            kids.append(s)
    return bd.Compound(children=kids, label=f"part{part}_joints")


@model
def v3_rhino_part6():
    return for_rhino(6)


@model
def v3_rhino_part7():
    return for_rhino(7)


if __name__ == "__main__":
    for name in v.piece_names():
        a, c = v.adds_cuts(name)
        for kind, s in (("add", a), ("cut", c)):
            p = OUT / f"{name}_{kind}.stl"
            if s is None:
                p.unlink(missing_ok=True)
            else:
                bd.export_stl(s, str(p), tolerance=0.01, angular_tolerance=0.1)
        print(name, "add" if a is not None else "-", "cut" if c is not None else "-")
    model.export(v3_rhino_part6(), ROOT / "exports" / "v3" / "STEP" / "rhino_part6_joints.step")
    model.export(v3_rhino_part7(), ROOT / "exports" / "v3" / "STEP" / "rhino_part7_joints.step")
