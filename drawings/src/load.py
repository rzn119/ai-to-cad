"""Read the combined STEP once (cached as BREP) and give the solids with their index."""
import json
from pathlib import Path
import build123d as bd
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "build" / "combined_solids.brep"

def solids():
    if CACHE.exists():
        c = bd.import_brep(str(CACHE))
    else:
        from OCP.STEPControl import STEPControl_Reader
        r = STEPControl_Reader(); r.ReadFile(str(ROOT / "build" / "combined.stp")); r.TransferRoots()
        c = bd.Compound(bd.Shape.cast(r.OneShape()).solids())
        bd.export_brep(c, str(CACHE))
    return c.solids()
