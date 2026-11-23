"""The factory drawing set: BOM sheet, assembly sheet, one sheet per made part.
Writes out/PDF/suitcase_drawings.pdf, out/DXF/<code>.dxf, out/STEP/<code>.step."""
import sys, json, math
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))
import build123d as bd
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.gp import gp_Trsf, gp_Ax3, gp_Pnt, gp_Dir
from cad.eng_drawing import Sheet
from drawkit import render, write, ROOT, LAST_NOTES
from load import solids
from catalogue import MAKE, BUY, SKIP

S = solids()
G = json.load(open(ROOT / "build" / "assembled_groups.json"))
OUT = ROOT / "out"
SCALES = [5, 2, 1, 0.5, 0.4, 0.2, 0.1, 0.05]
DATE = "2026-11-23"
GEN_NOTES = ["未注尺寸以3D模型(STEP)为准 / DIMENSIONS NOT SHOWN: SEE STEP MODEL",
             "去毛刺, 锐边倒钝 / DEBURR, BREAK SHARP EDGES"]


def qty(groups):
    return sum(len(G[g]["items"]) for g in groups)


def first(groups):
    return S[G[groups[0]]["items"][0][0]]


def oriented(s):
    """Largest extent along x, then y, smallest along z; min corner at the origin."""
    b = s.bounding_box()
    ext = [b.size.X, b.size.Y, b.size.Z]
    order = sorted(range(3), key=lambda i: -ext[i])
    axes = [[1 if j == i else 0 for j in range(3)] for i in order]
    # right-handed: z = x cross y
    x, y = axes[0], axes[1]
    z = [x[1] * y[2] - x[2] * y[1], x[2] * y[0] - x[0] * y[2], x[0] * y[1] - x[1] * y[0]]
    t = gp_Trsf()
    t.SetTransformation(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(*z), gp_Dir(*x)))   # world -> this frame
    r = bd.Shape.cast(s.wrapped.Moved(bd.Location(t).wrapped)) if False else s.transform_shape(bd.Matrix(t))
    b = r.bounding_box()
    return bd.Pos(-b.min.X, -b.min.Y, -b.min.Z) * r


def holes(part):
    """Round holes (concave cylinders closing at least 330 deg) along x, y or z:
    {axis: [(dia, centre, length)]}."""
    found = defaultdict(list)
    bb = part.bounding_box()
    for f in part.faces():
        a = BRepAdaptor_Surface(f.wrapped)
        if a.GetType() != GeomAbs_Cylinder:
            continue
        c = a.Cylinder(); ax = c.Axis(); d = ax.Direction(); p = ax.Location()
        dv = (d.X(), d.Y(), d.Z())
        k = max(range(3), key=lambda i: abs(dv[i]))
        if abs(abs(dv[k]) - 1) > 1e-3:
            continue
        span = a.LastUParameter() - a.FirstUParameter()
        # concave? the face normal at its centre points towards the axis
        ctr = f.center(); n = f.normal_at(ctr)
        to_ax = [0, 0, 0]; pc = [p.X(), p.Y(), p.Z()]; cc = [ctr.X, ctr.Y, ctr.Z]
        for i in range(3):
            if i != k:
                to_ax[i] = pc[i] - cc[i]
        if sum(to_ax[i] * (n.X, n.Y, n.Z)[i] for i in range(3)) <= 0:
            continue
        fb = f.bounding_box()
        lo, hi = (fb.min.X, fb.min.Y, fb.min.Z)[k], (fb.max.X, fb.max.Y, fb.max.Z)[k]
        centre = list(pc); centre[k] = hi
        found[(k, round(c.Radius() * 2, 2), tuple(round(centre[i], 2) for i in range(3) if i != k))].append((span, lo, hi, centre))
    out = defaultdict(list)
    for (k, dia, _), parts in found.items():
        if sum(p[0] for p in parts) < math.radians(330):
            continue
        lo = min(p[1] for p in parts); hi = max(p[2] for p in parts)
        ext = (bb.size.X, bb.size.Y, bb.size.Z)[k]
        out[k].append((dia, parts[0][3], hi - lo, hi - lo >= ext - 0.05))
    return out


def part_sheet(code, cn, en, mat, n, part):
    part = oriented(part)
    hs = holes(part)
    last = None
    order = [("A3", c) for c in SCALES if c >= 0.2] + [("A2", c) for c in SCALES if c >= 0.2] + [("A2", c) for c in SCALES if c < 0.2]
    for size, sc in order:
        sh = Sheet(size, scale=sc, title=f"{cn} {en}", part_number=code, material=mat, revision="A",
                   general_tolerance="ISO 2768-m",
                   notes=[f"数量 QTY: {n} / 每箱 PER SUITCASE"] + GEN_NOTES)
        top, front, right = sh.three_views(part)
        pbb = part.bounding_box()
        span = 0.9 * (pbb.size.X + pbb.size.Y + pbb.size.Z) / 1.6
        isc = next((c for c in [5, 2, 1, 0.5, 0.4, 0.2, 0.1, 0.05] if span * c <= 85), 0.05)
        sh.view(part, "iso", at=(sh.width - 78, sh.height - 62), scale=isc, hidden=False,
                label=f"轴测图 ISOMETRIC {isc:g}:1" if isc >= 1 else f"轴测图 ISOMETRIC 1:{1 / isc:g}")
        pb = part.bounding_box()
        top.dim((0, 0, pb.size.Z), (0, pb.size.Y, pb.size.Z), orientation="v")                 # width, left of top
        front.dim((0, 0, 0), (pb.size.X, 0, 0), orientation="h", offset=-(8 + 4 / sc if sc < 1 else 8))   # length, below front
        front.dim((pb.size.X, 0, 0), (pb.size.X, 0, pb.size.Z), orientation="v")              # thickness
        views = {2: top, 1: front, 0: right}
        for k, lst in hs.items():
            byd = defaultdict(list)
            for dia, c, depth, thru in lst:
                byd[(dia, thru, round(depth, 1))].append(c)
            for j, ((dia, thru, depth), cs) in enumerate(sorted(byd.items())[:4]):
                kw = {"thru": True} if thru else {"depth": depth}
                views[k].hole(tuple(cs[0]), dia, count=len(cs) if len(cs) > 1 else None, angle=45 + 30 * j, **kw)
        try:
            docs = render([sh], code)
        except ValueError as e:
            last = e
            continue
        if not inside_frame(docs[0], sh) or any("overlap" in n for n in LAST_NOTES):
            last = ValueError(f"{code}: annotation off the sheet or overlapping at scale {sc}: {LAST_NOTES[:1]}")
            continue
        for n in LAST_NOTES:
            print(code, n)
        return sh, docs[0], (size, sc), part
    raise last


def inside_frame(doc, sh, margin=10.5):
    from ezdxf import bbox
    import re
    msp = doc.modelspace()
    ents = [e for e in msp if e.dxf.layer in ("DIM", "NOTES", "VISIBLE", "HIDDEN")]
    ext = bbox.extents(ents, fast=True)
    if not (ext.has_data and ext.extmin.x >= margin and ext.extmin.y >= margin and
            ext.extmax.x <= sh.width - margin and ext.extmax.y <= sh.height - margin):
        return False
    # nothing drawn may reach down into the notes block (bottom left) or the title block
    def is_note(e):
        return e.dxftype() == "TEXT" and re.match(r"^\s*(NOTES:|\d+\.)", e.dxf.text or "")
    notes = [e for e in msp if e.dxf.layer == "NOTES" and is_note(e)]
    title = [e for e in msp if e.dxf.layer == "TITLE"]
    zones = []
    for grp in (notes, title):
        z = bbox.extents(grp, fast=True)
        if z.has_data:
            zones.append((z.extmin.x - 2, z.extmin.y - 2, z.extmax.x + 2, z.extmax.y + 3))
    for e in ents:
        if e in notes:
            continue
        b = bbox.extents([e], fast=True)
        if not b.has_data:
            continue
        for x0, y0, x1, y1 in zones:
            if b.extmin.x < x1 and b.extmax.x > x0 and b.extmin.y < y1 and b.extmax.y > y0:
                return False
    return True


PROFILE_SCALES = [10, 5, 2, 1]


def section_sheet(code, cn, en, mat, part):
    """Profile parts (long and slender): the cross-section half-way along, enlarged."""
    b = part.bounding_box()
    L, Wd, T = b.size.X, b.size.Y, b.size.Z
    x = L / 2
    band = min(Wd, 60.0)
    cut = part & bd.Pos(x - 0.05, -1, -1) * bd.Box(0.1, band + 1, T + 2, align=(bd.Align.MIN,) * 3)
    if not cut.solids():
        return None
    cut = bd.Compound(cut.solids())
    last = None
    for sc in PROFILE_SCALES:
        sh = Sheet("A3", scale=sc, title=f"{cn} {en}", part_number=code, material=mat, revision="A",
                   general_tolerance="ISO 2768-m",
                   notes=[f"截面A-A: 距端面 {x:.1f} mm / SECTION A-A AT {x:.1f} mm FROM END",
                          "型材截面, 全长一致除注明外 / PROFILE CONSTANT ALONG LENGTH UNLESS SHOWN"])
        v = sh.view(cut, "right", at=(sh.width * 0.42, sh.height * 0.58), label=f"截面 SECTION A-A  {sc:g}:1", hidden=False)
        v.overall()
        try:
            docs = render([sh], code)
        except ValueError as e:
            last = e; continue
        if inside_frame(docs[0], sh):
            return sh, docs[0]
    return None


def main():
    (OUT / "STEP").mkdir(parents=True, exist_ok=True)
    sheets, docs, names, log = [], [], [], []
    for code, groups, cn, en, mat in MAKE:
        part = first(groups); n = qty(groups)
        try:
            sh, doc, sc, op = part_sheet(code, cn, en, mat, n, part)
        except Exception as e:
            print("FAILED", code, e); log.append((code, "failed", str(e))); continue
        bd.export_step(op, str(OUT / "STEP" / f"{code}.step"))
        b = op.bounding_box()
        extra = None
        ring = op.volume / (b.size.X * b.size.Y * b.size.Z) < 0.5
        if b.size.X >= 100 and b.size.Z <= 30 and (b.size.Y <= 60 or ring) and "LEATHER" not in mat and "STRIP" not in en:
            extra = section_sheet(code, cn, en, mat, op)
        if extra:
            pair = render([sh, extra[0]], code)          # SHEET 1 OF 2, 2 OF 2
            sheets += [sh, extra[0]]; docs += pair; names += [f"{code}_1", f"{code}_2"]
        else:
            sheets.append(sh); docs.append(doc); names.append(code)
        log.append((code, cn, en, mat, n, sc, [round(b.size.X, 1), round(b.size.Y, 1), round(b.size.Z, 1)]))
        print(code, en, "scale", sc, "qty", n)
    json.dump(log, open(ROOT / "build" / "parts_log.json", "w"), ensure_ascii=False, indent=0)
    return sheets, docs, names


def front(names):
    from front_sheets import bom_sheet, assembly_sheet
    log = {r[0]: r for r in json.load(open(ROOT / "build" / "parts_log.json")) if len(r) > 5}
    rows, no = [], 1
    for code, groups, cn, en, mat in MAKE:
        r = log.get(code)
        if not r:
            continue
        size, sc = r[5]
        d = r[6]
        two = f"{code}_2" in names
        rows.append((no, code, cn, en, r[4], mat, "自制 MAKE", f"{d[0]:g} × {d[1]:g} × {d[2]:g}",
                     f"{size} 1:{1 / sc:g}" + (" +截面" if two else "") if sc < 1 else f"{size} {sc:g}:1" + (" +截面" if two else "")))
        no += 1
    for code, groups, cn, en, n in BUY:
        rows.append((no, code, cn, en, n, "外购 BOUGHT", "外购 BUY", "见3D模型 SEE STEP", "—")); no += 1
    bom = bom_sheet(rows)
    # exploded assembly: the assembled suitcase as it sits in the STEP
    asm_idx = sorted({it[0] for g in G for it in g["items"]})
    asm = bd.Compound([S[k] for k in asm_idx])
    balloons = []
    for code, groups, *_ in MAKE + BUY:
        s0 = first(groups)
        if s0.bounding_box().diagonal < 60 and not code.startswith("BP"):
            continue
        f = max(s0.faces(), key=lambda f: f.area)
        balloons.append((code, tuple(f.center())))
    a = assembly_sheet(asm, balloons)
    return [bom, a[:2]], a[2]


if __name__ == "__main__":
    sheets, docs, names = main()
    fr, notes = front(names)
    for n in notes:
        print("assembly:", n)
    # one PDF: parts list, assembly, then the parts; one DXF per sheet
    part_sheets, part_docs, part_names = sheets, docs, names
    all_sheets = [x[0] for x in fr] + part_sheets
    all_docs = [x[1] for x in fr] + part_docs
    all_names = ["00_PARTS_LIST", "01_ASSEMBLY"] + part_names
    write(all_docs, all_sheets, OUT / "PDF" / "suitcase_drawings.pdf", [OUT / "DXF" / f"{n}.dxf" for n in all_names])
    (OUT / "PDF" / "parts.pdf").unlink(missing_ok=True)
