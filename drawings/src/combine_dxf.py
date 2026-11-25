"""All pages (each a block, so dimensions keep their geometry; explode in CAD to edit) of out_groups/DXF in one DXF, side by side in model space (page order as in the PDF)."""
import build123d  # noqa: F401  (cad's environment)
from pathlib import Path
import ezdxf
from ezdxf.addons import Importer
from ezdxf.math import Matrix44

ROOT = Path(__file__).resolve().parent.parent
import sys
FOLDER = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "out_groups") / "DXF"
OUTNAME = sys.argv[2] if len(sys.argv) > 2 else "suitcase_groups_all.dxf"
src = sorted(FOLDER.glob("*.dxf"))
src = [p for p in src if not p.name.endswith("_all.dxf")]
out = ezdxf.new("R2010", setup=True)
out.units = ezdxf.units.MM
x, gap = 0.0, 40.0
for p in src:
    d = ezdxf.readfile(p)
    frame = [e for e in d.modelspace() if e.dxf.layer == "SHEET"]
    from ezdxf import bbox
    ext = bbox.extents(d.modelspace(), fast=True)
    w = ext.extmax.x - ext.extmin.x
    blk = out.blocks.new(name=f"PAGE_{p.stem.replace('-', '_')}")
    imp = Importer(d, out)
    imp.import_entities(d.modelspace(), blk)
    imp.finalize()
    ds_src, ds_out = d.dimstyles.get("Standard"), out.dimstyles.get("Standard")
    for k, v in ds_src.dxfattribs().items():           # the page's dimension style (text size, arrows, gaps)
        if k not in ("handle", "owner", "name") and not k.endswith("_handle") and isinstance(v, (int, float)):
            ds_out.dxf.set(k, v)
    for dim in blk.query("DIMENSION"):          # the importer drops the dimension's drawn block: redraw it
        dim.dxf.discard("geometry")
        dim.override().render()
    out.modelspace().add_blockref(blk.name, (x - ext.extmin.x, -ext.extmin.y), dxfattribs={"layer": "SHEET"})
    n = len(blk)
    t = out.modelspace().add_text(p.stem, dxfattribs={"height": 8, "layer": "NOTES"})
    t.set_placement((x, ext.extmax.y - ext.extmin.y + 8))
    print(p.name, n, "entities at x =", round(x))
    x += w + gap
for st in out.styles:
    st.dxf.font = "simsun.ttc"
out.saveas(FOLDER / OUTNAME, encoding="utf-8")
a = ezdxf.readfile(FOLDER / OUTNAME).audit()
print("audit errors", len(a.errors), "fixes", len(a.fixes))
