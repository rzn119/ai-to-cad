"""Write, for every piece, the joint geometry to add (rails, tongue) and to cut (slots, groove,
label) as STL for tools/make_pieces.py, plus STEP files for Rhino. Run: cad run src/build_parts.py"""
from pathlib import Path

import build123d as bd
from cad import model

import hidden_joints as h

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "joints"
OUT.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    for part, key in h.pieces():
        name = f"P{part}-{key}"
        add, cut = h.piece_add(part, key), h.piece_cut(part, key)
        for kind, shape in (("add", add), ("cut", cut)):
            path = OUT / f"{name}_{kind}.stl"
            if shape is None:
                path.unlink(missing_ok=True)          # nothing of this kind for this piece
            else:
                bd.export_stl(shape, str(path), tolerance=0.01, angular_tolerance=0.1)
        print(name, "add" if add is not None else "-", "cut" if cut is not None else "-")
    model.export(h.joint_solids(), ROOT / "exports" / "STEP" / "hidden_joints_assembled.step")
