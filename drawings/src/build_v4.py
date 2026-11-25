"""Quote / manufacturing set from 3d_printing_combined_manufacture2.stp (the exploded assembled suitcase):
page 1 parts list for quoting, then one page per component group (as in the designer's layout image).
Dimensions rounded to the nearest 5 mm. Writes out_v4/PDF/suitcase_quote_drawings.pdf and out_v4/DXF/*.dxf."""
import sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))
import build123d as bd
from cad.eng_drawing import Sheet
from drawkit import render, write, ROOT, LAST_NOTES
from front_sheets import bom_sheet
from catalogue import MAKE, BUY

OUT = ROOT / "out_v4"
S = bd.import_brep(str(ROOT / "build" / "combined_v4_solids.brep")).solids()
CL = json.load(open(ROOT / "build" / "v4_clusters.json"))
OLD = json.load(open(ROOT / "build" / "assembled_groups.json"))


def dims(s):
    b = s.bounding_box()
    return tuple(sorted((round(b.size.X, 1), round(b.size.Y, 1), round(b.size.Z, 1))))


def near(d, ref, tol=0.25):
    return all(abs(a - b) <= tol for a, b in zip(d, ref))


CASTER = [(14.7, 45.5, 45.5), (17.6, 17.6, 40.6), (19.0, 21.1, 21.1), (25.5, 32.0, 41.0), (25.5, 32.0, 41.1)]
HANDLE = [(13.4, 15.8, 125.0)]
HINGE = [(8.0, 12.1, 23.0), (8.0, 12.0, 23.0), (8.0, 10.0, 11.6), (1.5, 12.1, 12.1), (1.5, 12.0, 12.1), (4.2, 8.7, 8.7),
         (4.2, 8.6, 8.7), (3.1, 5.9, 5.9), (4.0, 8.2, 8.2)]
LOCK = [(7.1, 11.8, 33.8), (4.1, 10.9, 12.4), (4.8, 7.8, 8.8), (3.9, 7.9, 8.9), (3.6, 4.5, 7.9)]
LEATHER = [(3.0, 294.6, 414.5)]
HOUSING = [(22.2, 30.8, 40.2)]
BASE = [(5.7, 312.5, 452.8)]


def kind(s):
    d = dims(s)
    for nm, lst in (("caster", CASTER), ("handle", HANDLE), ("hinge", HINGE), ("lock", LOCK), ("leather", LEATHER),
                    ("housing", HOUSING), ("base", BASE)):
        if any(near(d, r) for r in lst):
            return nm
    return "part"


def cl(i, drop=()):
    return [S[k] for k in CL[i] if kind(S[k]) not in drop]


def pick(i, k):
    return [S[j] for j in CL[i] if kind(S[j]) == k]


ACC = ("caster", "handle", "hinge", "lock")
leather = pick(0, "leather")[0]
shell_body = cl(4, ACC) + cl(3, ACC) + pick(5, "housing") + pick(5, "base")
shell = shell_body + cl(2, ACC)


def one_caster():
    parts = [S[k] for k in CL[5] if kind(S[k]) == "caster"]
    x0 = min(p.bounding_box().min.X for p in parts)
    return [p for p in parts if p.bounding_box().min.X < x0 + 60]


def one_hinge():
    parts = [S[k] for k in CL[0] if kind(S[k]) == "hinge"]
    x0 = min(p.bounding_box().min.X for p in parts)
    return [p for p in parts if p.bounding_box().min.X < x0 + 30]


def row(sets, gap=25.0):
    """Lay sets of parts side by side along x."""
    out, x = [], 0.0
    for parts in sets:
        b = bd.Compound(parts).bounding_box()
        out += [bd.Pos(x - b.min.X, -b.min.Y, -b.min.Z) * p for p in parts]
        x += b.size.X + gap
    return out


GROUPS = [  # code, CN, EN, material, parts (one of each for accessories), quantities note, sets for the parts list
    ("G-01", "配件", "ACCESSORIES", "外购 BOUGHT-IN",
     row([one_caster(), pick(4, "handle")[:1], one_hinge(), pick(3, "lock")]),
     ["从左至右: 万向轮×4, 把手×2, 阻尼铰链×4, 密码锁×1", "LEFT TO RIGHT: CASTER×4, HANDLE×2, HINGE×4, LOCK×1"]),
    ("G-02", "行李箱框", "SUITCASE FRAME A", "铝镁合金 Al-Mg ALLOY", cl(1, ACC), []),
    ("G-03", "行李箱框", "SUITCASE FRAME B", "铝镁合金 Al-Mg ALLOY", cl(0, ACC + ("leather",)), []),
    ("G-04", "行李箱面板", "SUITCASE PANEL", "皮革 LEATHER", [leather], ["数量 QTY: 2 / 每箱"]),
    ("G-05", "外壳+轮座", "SHELL + WHEEL BASE", "待确认 TBC", shell,
     ["外壳与轮座合并 / SHELL WITH WHEEL HOUSING", "封边框为爆炸位置, 尺寸不含 / EDGE BAND EXPLODED, NOT IN DIMS"]),
    ("G-06", "行李箱框+拉杆", "FRAME + HANDLE", "铝镁合金 Al-Mg ALLOY", cl(6, ACC + ("leather",)), []),
    ("G-07", "行李箱框", "SUITCASE FRAME C", "铝镁合金 Al-Mg ALLOY", cl(5, ACC + ("housing", "base")), []),
]
QTY_SETS = {"G-01": None, "G-04": 2}
NOTE5 = "尺寸圆整至5mm / DIMENSIONS ROUNDED TO 5 mm"
ORDER = [("A3", c) for c in (1, 0.5, 0.4, 0.2)] + [("A2", c) for c in (1, 0.5, 0.4, 0.2, 0.1)]


def r5(v):
    return f"{5 * round(v / 5):g}" if v >= 5 else f"{round(v * 2) / 2:g}"


def upright(parts):
    """The assembly is exploded along y with its faces upright: lay each group flat (y -> z)."""
    return [p.rotate(bd.Axis.X, 90) for p in parts]


def group_sheet(code, cn, en, mat, parts, notes, n_check, dim_parts=None):
    lay = upright if code != "G-01" else (lambda x: x)
    comp = bd.Compound(lay(parts))
    b = comp.bounding_box()
    move = bd.Pos(-b.min.X, -b.min.Y, -b.min.Z)
    comp = move * comp
    db = (move * bd.Compound(lay(dim_parts or parts))).bounding_box()     # what the dimensions measure
    X0, Y0, Z0, X1, Y1, Z1 = db.min.X, db.min.Y, db.min.Z, db.max.X, db.max.Y, db.max.Z
    L, W, H = X1 - X0, Y1 - Y0, Z1 - Z0
    last = None
    for size, sc in ORDER:
        sh = Sheet(size, scale=sc, title=f"{cn} {en}", part_number=code, material=mat, revision="C",
                   general_tolerance="ISO 2768-m",
                   notes=notes + [f"共 {n_check} 件 / {n_check} PIECES", NOTE5, "其余尺寸见STEP模型 / OTHER DIMS: SEE STEP"])
        top, front, right = sh.three_views(comp)
        span = 0.9 * (L + W + H) / 1.6
        isc = next((c for c in [1, 0.5, 0.4, 0.2, 0.1, 0.05] if span * c <= 85), 0.05)
        sh.view(comp, "iso", at=(sh.width - 78, sh.height - 62), scale=isc, hidden=False,
                label="轴测图 ISOMETRIC 1:1" if isc >= 1 else f"轴测图 ISOMETRIC 1:{1 / isc:g}")
        top.dim((X0, Y0, Z1), (X0, Y1, Z1), orientation="v", text=r5(W))
        front.dim((X0, Y0, Z0), (X1, Y0, Z0), orientation="h", offset=-(8 + 4 / sc if sc < 1 else 8), text=r5(L))
        front.dim((X1, Y0, Z0), (X1, Y0, Z1), orientation="v", text=r5(H))
        try:
            doc = render([sh], code)[0]
        except ValueError as e:
            last = e; continue
        from build_set import inside_frame
        if inside_frame(doc, sh) and not any("overlap" in n for n in LAST_NOTES):
            return sh, doc, (size, sc), (L, W, H)
        last = ValueError(f"{code}: does not fit at {size} {sc}")
    raise last


def old_name(s):
    d, v = dims(s), s.volume
    for gi, g in enumerate(OLD):
        if near(d, tuple(g["sig"][1]), 0.6) and abs(g["sig"][0] - v) / max(v, 1) < 0.01:
            for code, groups, cn, en, mat in MAKE:
                if gi in groups:
                    return code, cn, en, mat
    return None


def parts_rows(page_of):
    rows, no = [], 1
    acc = [("BP-01", "万向轮", "SWIVEL CASTER", 4), ("BP-02", "把手", "CARRY HANDLE", 2),
           ("BP-03", "阻尼铰链", "DAMPING HINGE", 4), ("BP-04", "密码锁", "COMBINATION LOCK", 1)]
    for code, cn, en, n in acc:
        rows.append((no, code, cn, en, n, "外购 BOUGHT", "外购 BUY", "见第2页 SEE P.2", f"G-01 {page_of['G-01']}")); no += 1
    for gcode, gcn, gen, gmat, parts, _ in GROUPS[1:]:
        seen = {}
        mult = 2 if gcode == "G-04" else 1
        for p in parts:
            key = (tuple(round(x * 2) / 2 for x in dims(p)), round(p.volume / 50))
            seen.setdefault(key, [p, 0])[1] += 1
        for key, (p, n) in sorted(seen.items(), key=lambda kv: -kv[1][0].volume):
            nm = old_name(p)
            code, cn, en, mat = nm if nm else ("—", "零件", "PART", gmat)
            d = sorted(dims(p), reverse=True)
            rows.append((no, code, cn, en, n * mult, mat, "自制 MAKE", " × ".join(r5(x) for x in d), f"{gcode} {page_of[gcode]}"))
            no += 1
    return rows


if __name__ == "__main__":
    sheets, docs, names, page_of = [], [], [], {}
    for i, (code, cn, en, mat, parts, notes) in enumerate(GROUPS):
        n = len(parts)
        sh, doc, (size, sc), _ = group_sheet(code, cn, en, mat, parts, notes, n,
                                             dim_parts=shell_body if code == "G-05" else None)
        sheets.append(sh); docs.append(doc); names.append(code)
        page_of[code] = f"P.{i + 2}"
        print(code, en, size, sc, n, "pieces")
    rows = parts_rows(page_of)
    print(len(rows), "rows in the parts list")
    bom = bom_sheet(rows, size="A2" if len(rows) > 30 else "A3")
    (OUT / "DXF").mkdir(parents=True, exist_ok=True)
    write([bom[1]] + docs, [bom[0]] + sheets, OUT / "PDF" / "suitcase_quote_drawings.pdf",
          [OUT / "DXF" / "00_PARTS_LIST.dxf"] + [OUT / "DXF" / f"{n}.dxf" for n in names])
    json.dump([list(map(str, r)) for r in rows], open(OUT / "parts_list.json", "w"), ensure_ascii=False, indent=0)
    print("done")
