"""One page per component group, as laid out in the Rhino file, dimensions rounded to 5 mm.
Writes out_groups/PDF/suitcase_groups.pdf and out_groups/DXF/*.dxf."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import build123d as bd
from OCP.STEPControl import STEPControl_Reader
from cad.eng_drawing import Sheet
from drawkit import render, write, ROOT, LAST_NOTES
from build_set import inside_frame, S, G
from front_sheets import bom_sheet

OUT = ROOT / "out_groups"
NOTE5 = "尺寸圆整至5mm / DIMENSIONS ROUNDED TO 5 mm"


def r5(v):
    return f"{5 * round(v / 5):g}" if v >= 5 else f"{round(v * 2) / 2:g}"


V3 = bd.import_brep(str(ROOT / "build" / "combined_v3_solids.brep")).solids()


def region(x0, x1, y0, y1):
    out = []
    for s_ in V3:
        b = s_.bounding_box()
        if x0 <= b.min.X and b.max.X <= x1 and y0 <= b.min.Y and b.max.Y <= y1:
            out.append(s_)
    return out


def wheel_housing():
    r = STEPControl_Reader(); r.ReadFile(str(ROOT / "build" / "combined_v3.stp")); r.TransferRoots()
    for sh in bd.Shape.cast(r.OneShape()).shells():
        b = sh.bounding_box()
        if abs(b.min.X - 12397.6) < 1 and abs(b.max.Y + 799.5) < 1:
            return sh
    raise RuntimeError("wheel housing not found")


leather = S[G[3]["items"][0][0]]          # from the previous export: this one has no leather panel
GROUPS = [
    ("G-01", "配件", "ACCESSORIES (BOUGHT-IN)", "外购 BOUGHT-IN", region(10200, 10600, -700, -300),
     ["把手×2 HANDLE, 阻尼铰链×4 HINGE, 万向轮×4 CASTER"]),
    ("G-02", "行李箱框", "SUITCASE FRAME A", "铝镁合金 Al-Mg ALLOY", region(10780, 11200, -900, -300), []),
    ("G-03", "行李箱框", "SUITCASE FRAME B", "铝镁合金 Al-Mg ALLOY", region(11200, 11700, -900, -300), []),
    ("G-04", "行李箱面板", "SUITCASE PANEL", "皮革 LEATHER", [leather], ["数量 QTY: 2 / 每箱"]),
    ("G-05", "外壳+轮座", "SHELL + WHEEL BASE", "待确认 TBC", region(12300, 12800, -900, -300) + [wheel_housing()],
     ["外壳与轮座合并 / SHELL WITH WHEEL HOUSING"]),
    ("G-06", "行李箱框+拉杆", "FRAME + HANDLE", "铝镁合金 Al-Mg ALLOY", region(10400, 11200, -1700, -1000), []),
    ("G-07", "行李箱框", "SUITCASE FRAME C", "铝镁合金 Al-Mg ALLOY", region(11200, 11700, -1700, -1000), []),
]
ORDER = [("A3", c) for c in (1, 0.5, 0.4, 0.2)] + [("A2", c) for c in (0.4, 0.2, 0.1)]


def group_sheet(code, cn, en, mat, shapes, notes):
    if len(shapes) == 1 and shapes[0].bounding_box().size.Z > shapes[0].bounding_box().size.Y:
        pass
    comp = bd.Compound(shapes)
    b = comp.bounding_box()
    if b.size.Z > b.size.Y and b.size.Z > b.size.X * 0.9 and len(shapes) == 1:   # lay single plates flat
        comp = comp.rotate(bd.Axis.X, 90); b = comp.bounding_box()
    comp = bd.Pos(-b.min.X, -b.min.Y, -b.min.Z) * comp
    L, W, H = b.size.X, b.size.Y, b.size.Z
    last = None
    for size, sc in ORDER:
        sh = Sheet(size, scale=sc, title=f"{cn} {en}", part_number=code, material=mat, revision="B",
                   general_tolerance="ISO 2768-m",
                   notes=notes + [f"共 {len(shapes)} 件 / {len(shapes)} PIECES", NOTE5,
                                  "其余尺寸见STEP模型 / OTHER DIMS: SEE STEP"])
        top, front, right = sh.three_views(comp)
        span = 0.9 * (L + W + H) / 1.6
        isc = next((c for c in [1, 0.5, 0.4, 0.2, 0.1, 0.05] if span * c <= 85), 0.05)
        sh.view(comp, "iso", at=(sh.width - 78, sh.height - 62), scale=isc, hidden=False,
                label=f"轴测图 ISOMETRIC 1:{1 / isc:g}" if isc < 1 else "轴测图 ISOMETRIC 1:1")
        top.dim((0, 0, H), (0, W, H), orientation="v", text=r5(W))
        front.dim((0, 0, 0), (L, 0, 0), orientation="h", offset=-(8 + 4 / sc if sc < 1 else 8), text=r5(L))
        front.dim((L, 0, 0), (L, 0, H), orientation="v", text=r5(H))
        try:
            doc = render([sh], code)[0]
        except ValueError as e:
            last = e; continue
        if inside_frame(doc, sh) and not any("overlap" in n for n in LAST_NOTES):
            return sh, doc, (size, sc), (L, W, H)
        last = ValueError(f"{code}: does not fit at {size} {sc}")
    raise last


if __name__ == "__main__":
    sheets, docs, names, rows = [], [], [], []
    for i, (code, cn, en, mat, shapes, notes) in enumerate(GROUPS, 1):
        sh, doc, (size, sc), (L, W, H) = group_sheet(code, cn, en, mat, shapes, notes)
        sheets.append(sh); docs.append(doc); names.append(f"{code}")
        qty = 2 if code == "G-04" else 1
        rows.append((i, code, cn, en, qty, mat, "外购 BUY" if code == "G-01" else "自制 MAKE",
                     f"{r5(L)} × {r5(W)} × {r5(H)}", f"第{i + 1}页 P.{i + 1}  {size} 1:{1 / sc:g}"))
        print(code, en, size, sc, len(shapes), "pieces")
    bom = bom_sheet(rows, size="A3")
    write([bom[1]] + docs, [bom[0]] + sheets, OUT / "PDF" / "suitcase_groups.pdf",
          [OUT / "DXF" / "00_PARTS_LIST.dxf"] + [OUT / "DXF" / f"{n}.dxf" for n in names])
    print("done")
