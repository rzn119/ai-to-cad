"""Write the connector deliverables. Run: cad run src/exports.py (then tools/make_pieces.py)."""
from pathlib import Path

from cad import model

import connectors as c

ROOT = Path(__file__).resolve().parent.parent
EX, BUILD = ROOT / "exports", ROOT / "build"

if __name__ == "__main__":
    model.export(c.rhino_part6(), EX / "STEP" / "rhino_part6_connectors.step")
    model.export(c.rhino_part7(), EX / "STEP" / "rhino_part7_connectors.step")
    model.export(c.connectors_assembled(), EX / "STEP" / "connectors_assembled.step")
    model.export(c.connectors_assembled(), BUILD / "connectors.glb")
    model.export(c.pads_all(), BUILD / "pads.stl", tolerance=0.02)
    model.export(c.cuts_all(), BUILD / "cuts.stl", tolerance=0.02)
    for name, fn in (("dovetail_key", c.key_print), ("dowel_5x28", c.dowel_print), ("fit_test", c.fit_test)):
        h = fn()
        model.export(h, EX / "STEP" / f"{name}.step")
        model.export(h, EX / "STL" / f"{name}.stl", tolerance=0.01)
        print(name, h.id)
