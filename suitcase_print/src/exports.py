"""Write the Rhino and fit-test files. Run after `cad run src/build_parts.py`:
    cad run src/exports.py"""
from pathlib import Path

import build123d as bd
from cad import model

import hidden_joints as h

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "exports"


def for_rhino(part):
    """Each piece's joint geometry where the part lies in the .3dm (part 7 sits 494 mm along x
    from part 6 and is not stacked there). Union '<piece> add', BooleanDifference '<piece> cut'
    after splitting the part at the seams."""
    kids = []
    for p, key in h.pieces():
        if p != part:
            continue
        for kind, shape, col in (("add", h.piece_add(p, key), "#c0392b"), ("cut", h.piece_cut(p, key), "#e67e22")):
            if shape is None:
                continue
            if part == 7:
                shape = bd.Pos(h.P7_DX, 0, -h.H) * shape
            shape.label, shape.color = f"P{p}-{key} {kind}", col
            kids.append(shape)
    return bd.Compound(children=kids, label=f"part{part}_joints")


@model
def rhino_part6():
    return for_rhino(6)


@model
def rhino_part7():
    return for_rhino(7)


if __name__ == "__main__":
    model.export(rhino_part6(), EX / "STEP" / "rhino_part6_joints.step")
    model.export(rhino_part7(), EX / "STEP" / "rhino_part7_joints.step")
    ft = h.fit_test()
    model.export(ft, EX / "STEP" / "fit_test.step")
    model.export(ft, EX / "STL" / "fit_test.stl", tolerance=0.01)
