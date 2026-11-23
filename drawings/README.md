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
