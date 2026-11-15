"""Write every option's STEP (for Rhino) and GLB (for rendering). Run: cad run src/exports.py"""
from pathlib import Path

from cad import model

import options

OUT = Path(__file__).resolve().parent.parent / "exports"
NAMES = ["a_suitcase", "a_suitcase_pulled", "a_shelf", "a_cuts",
         "b_suitcase", "b_suitcase_pulled", "b_shelf", "b_cuts",
         "c_suitcase", "c_suitcase_pulled", "c_shelf", "c_cuts",
         "a_detail_suitcase", "a_detail_shelf", "b_detail_suitcase", "b_detail_shelf",
         "c_detail_suitcase", "c_detail_shelf"]

if __name__ == "__main__":
    for name in NAMES:
        handle = getattr(options, name)()
        model.export(handle, OUT / "STEP" / f"{name}.step")
        model.export(handle, OUT / "GLB" / f"{name}.glb")
        print(name, handle.id)
