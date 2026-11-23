"""Shared set-up for the drawing set: Chinese font, robust edge sampling, DXF + PDF output."""
import sys
from pathlib import Path
import cad.eng_drawing as ed
from ezdxf.fonts import fonts

ROOT = Path(__file__).resolve().parent.parent
PDF_FONT = "NotoSansSC-Regular.ttf"     # embedded in the PDF
DXF_FONT = "simsun.ttc"                 # 宋体, on every Chinese Windows / AutoCAD install
fonts.build_system_font_cache()
fonts.font_manager.scan_folder(ROOT / "fonts")

_orig = ed._edge_polyline


def _safe_polyline(edge, samples: int = 24):
    try:
        return _orig(edge, samples)
    except Exception:
        try:      # sample by parameter instead of by length (degenerate projected edges)
            return [(float(v.X), float(v.Y)) for v in (edge.position_at(i / (samples - 1), position_mode=__import__("build123d").PositionMode.PARAMETER) for i in range(samples))]
        except Exception:
            return [(float(edge.start_point().X), float(edge.start_point().Y))] * 2


ed._edge_polyline = _safe_polyline


LAST_NOTES = []


def render(sheets, label):
    docs = []
    LAST_NOTES.clear()
    for i, sh in enumerate(sheets, 1):
        notes = []
        doc = ed._render_sheet(sh, index=i, count=len(sheets), label=label, warnings=notes)
        LAST_NOTES.extend(notes)
        docs.append(doc)
    return docs


def set_font(doc, font):
    for st in doc.styles:
        st.dxf.font = font


def write(docs, sheets, pdf_path, dxf_paths):
    for d in docs:
        set_font(d, PDF_FONT)
    ed._write_pdf(docs, sheets, Path(pdf_path))
    for d, p in zip(docs, dxf_paths):
        set_font(d, DXF_FONT)
        Path(p).parent.mkdir(parents=True, exist_ok=True)
        d.saveas(p, encoding="utf-8")
