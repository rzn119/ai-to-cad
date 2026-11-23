import build123d
import ezdxf, glob
from collections import Counter
bad = 0; tot = Counter()
for p in sorted(glob.glob("out/DXF/*.dxf")):
    d = ezdxf.readfile(p); a = d.audit()
    c = Counter(e.dxftype() for e in d.modelspace())
    tot.update(c)
    fonts = {s.dxf.font for s in d.styles}
    cn = any(any('一' <= ch <= '鿿' for ch in (e.dxf.text or "")) for e in d.modelspace() if e.dxftype() == "TEXT")
    if a.has_errors or not cn or c["DIMENSION"] == 0 and "PARTS_LIST" not in p:
        bad += 1; print("CHECK", p, a.has_errors, cn, dict(c))
print("files", len(glob.glob("out/DXF/*.dxf")), "problems", bad, "fonts", fonts, "version", d.dxfversion)
print(dict(tot))
