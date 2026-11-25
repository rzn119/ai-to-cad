# 行李箱生产图纸 / Suitcase factory drawing set

Made from `3d_printing_combined_manufacture.stp` (exported from the Rhino file of the same name).
The parts and quantities come from the assembled (exploded) suitcase in the model.

## What is in `out/`
- `PDF/suitcase_drawings.pdf`: the whole set, 60 pages:
  1. 零件明细表 PARTS LIST (A2): 41 made parts + 4 bought-in parts, quantities per suitcase, material, size, drawing.
  2. 总装爆炸图 EXPLODED ASSEMBLY (A2) with part codes.
  3. One drawing per made part (SC-xxx), A3 (the shell on A2): top, front, right and isometric views, overall
     dimensions, quantity. The 17 bar and frame parts have a second sheet with the profile cross-section (Section A-A).
- `DXF/`: one DXF per sheet (AutoCAD 2010 format, millimetres, text style 宋体 simsun.ttc). Open in AutoCAD and
  "Save As" DWG if the factory wants DWG.
- `STEP/`: one STEP per made part, in the same orientation as its drawing.

Every drawing says: tolerances ISO 2768-m; dimensions not shown are taken from the STEP model; deburr.

## To confirm before sending (marked 待确认 TBC on the drawings)
- Names and materials of parts the model does not label (only the frame = 铝镁合金 and the leather panel are labelled).
- The handle tubes (SC-211) and frame bars are modelled solid: if they are tubes or hollow extrusions, the wall
  thickness must be added.
- In the layout area of the Rhino file the track frame is a slightly different version (2.7 % more material) than in
  the assembled suitcase; the drawing uses the assembled one.
- Not drawn: the hinge options A/B/C (design alternatives in the accessories area), the 3D-print joint keys, and the
  0.2 mm tolerance body (a modelling cutter).

## Rebuild
`cad run src/build_set.py` (needs `build/combined.stp` and `fonts/NotoSansSC-Regular.ttf` from Google Fonts).
`src/catalogue.py` holds the part names, codes and materials; edit it and rebuild to rename or re-assign parts.

## Revision B: one page per component group (`out_groups/`)
Made from the updated export (142 parts, the layout of component groups). `PDF/suitcase_groups.pdf`, 8 pages:
parts list, then 配件 accessories, 行李箱框 frame A, frame B, 行李箱面板 leather panel, 外壳+轮座 shell with the
wheel housing, 行李箱框+拉杆 frame + pull handle, 行李箱框 frame C. Each group is drawn as laid out in Rhino;
overall dimensions rounded to 5 mm. The updated export has no leather panel, so page 5 uses the panel from the
earlier export. `DXF/`: one DXF per page, plus `suitcase_groups_all.dxf` with all 8 pages side by side (each page a block named PAGE_...; explode it to edit). Rebuild: `cad run src/build_groups.py`, then `cad run src/combine_dxf.py`.

## Revision C: quote set from `3d_printing_combined_manufacture2.stp` (`out_v4/`)
That file holds the exploded assembled suitcase (153 parts); its parts are sorted into the seven groups of the layout
image. `PDF/suitcase_quote_drawings.pdf`, 8 pages: page 1 parts list for quoting (48 lines: code, name, quantity per
suitcase, material, size rounded to 5 mm, page), then 配件, 行李箱框 A, 行李箱框 B, 行李箱面板 (×2), 外壳+轮座 (the green
wheel housings with the shell), 行李箱框+拉杆, 行李箱框 C. Overall dimensions rounded to the nearest 5 mm.
`DXF/`: one DXF per page and `suitcase_quote_all.dxf` with all pages. Rebuild: `cad run src/build_v4.py`, then
`cad run src/combine_dxf.py out_v4 suitcase_quote_all.dxf`.
