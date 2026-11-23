"""Sheet 1: parts list (BOM). Sheet 2: exploded assembly with part numbers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import build123d as bd
from ezdxf.enums import TextEntityAlignment as TA
from cad.eng_drawing import Sheet
from drawkit import render, LAST_NOTES


def bom_sheet(rows):
    """rows: (no, code, cn, en, qty, material, make_buy, size, sheet_info)"""
    sh = Sheet("A2", title="零件明细表 PARTS LIST", part_number="SC-000", material="—", revision="A",
               notes=["零件名称标注(待确认)者请设计方确认 / NAMES AND MATERIALS MARKED TBC: TO BE CONFIRMED BY DESIGNER",
                      "3D模型(STEP)为加工依据, 图纸未注尺寸以模型为准 / THE STEP MODEL IS THE MASTER FOR ALL GEOMETRY",
                      "表面处理及颜色另行确认 / SURFACE FINISH AND COLOUR TO BE AGREED",
                      "单位: 毫米 / UNITS: mm"])
    doc = render([sh], "SC-000")[0]
    msp = doc.modelspace()
    cols = [("序号\nNO.", 12), ("代号\nCODE", 22), ("名称\nNAME (中文)", 42), ("NAME (ENGLISH)", 62), ("数量\nQTY", 14),
            ("材料\nMATERIAL", 50), ("来源\nMAKE/BUY", 24), ("外形尺寸 SIZE\nL×W×H (mm)", 46), ("图纸\nDRAWING", 40)]
    x0, ytop, rh, hh = 20, sh.height - 20, 6.2, 10
    xs = [x0]
    for _, w in cols:
        xs.append(xs[-1] + w)
    n = len(rows)
    ybot = ytop - hh - n * rh
    L = {"layer": "TITLE"}
    for x in xs:
        msp.add_line((x, ytop), (x, ybot), dxfattribs=L)
    msp.add_line((x0, ytop), (xs[-1], ytop), dxfattribs=L)
    msp.add_line((x0, ytop - hh), (xs[-1], ytop - hh), dxfattribs=L)
    for i in range(n + 1):
        y = ytop - hh - i * rh
        msp.add_line((x0, y), (xs[-1], y), dxfattribs=L)
    for (h, _), xa, xb in zip(cols, xs, xs[1:]):
        for j, line in enumerate(h.split("\n")):
            t = msp.add_text(line, dxfattribs={"height": 2.3, "layer": "TITLE"})
            t.set_placement(((xa + xb) / 2, ytop - 3.3 - j * 3.6 if "\n" in h else ytop - hh / 2), align=TA.MIDDLE_CENTER)
    for i, r in enumerate(rows):
        y = ytop - hh - i * rh - rh / 2
        for k, (v, xa, xb) in enumerate(zip(r, xs, xs[1:])):
            t = msp.add_text(str(v), dxfattribs={"height": 2.2, "layer": "TITLE"})
            if k in (0, 4):
                t.set_placement(((xa + xb) / 2, y), align=TA.MIDDLE_CENTER)
            else:
                t.set_placement((xa + 1.5, y), align=TA.MIDDLE_LEFT)
    return sh, doc


def assembly_sheet(assembly, balloons):
    """assembly: compound of the exploded suitcase; balloons: [(code, point)]"""
    import math
    last, best = None, None
    for sc, phase in [(0.2, k) for k in range(10)] + [(0.1, k) for k in range(10)]:
        sh = Sheet("A2", scale=sc, title="总装爆炸图 EXPLODED ASSEMBLY", part_number="SC-001-ASM",
                   material="—", revision="A",
                   notes=["件号见零件明细表 / ITEM CODES: SEE PARTS LIST (SHEET 1)",
                          "BP- 为外购件 / BP- ITEMS ARE BOUGHT-IN PARTS"])
        v = sh.view(assembly, "iso", at=(sh.width * 0.45, sh.height * 0.57), hidden=False, centre_marks=False,
                    label=f"爆炸轴测图 EXPLODED ISOMETRIC 1:{1 / sc:g}")
        for j, (code, p) in enumerate(balloons):
            ang = (j * 137.5 + phase * 23) % 360
            v.note(code, p, offset=(28 * math.cos(math.radians(ang)), 22 * math.sin(math.radians(ang))))
        try:
            doc = render([sh], "SC-001-ASM")[0]
        except ValueError as e:
            last = e
            continue
        res = (sh, doc, [n for n in LAST_NOTES])
        if not any("overlap" in n for n in res[2]):
            return res
        if best is None or len(res[2]) < len(best[2]):
            best = res
    if best:
        return best
    raise last
