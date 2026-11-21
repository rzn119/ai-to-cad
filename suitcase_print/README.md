# Suitcase body: printable pieces with connectors (Bambu A1 mini)

Parts 6 and 7 from `part_6_and_7.3dm`, cut into **14 pieces (7 per part)** that each fit the
A1 mini's 180 × 180 × 180 mm build volume with at least 5 mm to spare, plus the connectors that
join them by hand after printing.

## What changed from the drawn grid, and why

- **Side-wall cuts moved to y −652 and −482** (the grid had −662.2 and −482.2). The grid's middle
  row was exactly 180.0 mm long, the full plate, and the cut at −662.2 would have left no room for
  a connector clear of the side-wall handle recess (y −634 to −500). The longest straight piece is
  now 170 mm.
- **The end wall is cut either side of its handle recess (x 12948 and 13124.7) instead of in the
  middle**, giving 7 pieces per part rather than 6. The end wall carries a 140 mm handle recess right
  where the drawn centre cut is; a seam there would split the handle the suitcase is lifted by, and
  there is no flat face for a connector. The middle piece (E) holds the whole handle and fits the
  plate turned 45°.
- **Part 7 stacks on part 6** (its bottom edge on part 6's top edge), which completes the two
  handle recesses that cross the joint.

## Connectors

| Joint | Connector | Fit |
| --- | --- | --- |
| Vertical seams (6: two on the end wall, two on each side wall) | Pads on the inside carry half a dovetail groove each; one printed dovetail key per seam (166 mm) slides up from below through part 6 into part 7 | 0.20 mm clearance per side, every face |
| Joint between part 6 and part 7, between the seams (5 places) | Ø5 × 28 mm dowels in pads either side of the joint | Ø5.4 holes for Ø5.0 pins (0.20 per side), 0.5 mm entry chamfers |

The keys lock each seam, and because they run through both halves they also tie part 6 to part 7.
The dowels keep the long joint between them in line. The 7 mm fixed hard panel inside the bottom of
part 6 sits below every pad (pads start at z −170, the panel's top is −171.5) and stops the keys
from sliding out.

## Print

1. **Print `exports/STL/fit_test.stl` first** (a small plate, 103 × 55 mm). Try the three keys (1, 2, 3
   notches = 0.15, 0.20, 0.25 mm) in the groove and a dowel in the Ø5.2 / 5.4 / 5.6 holes. If
   0.20 is too tight or too loose on your printer, change `CLEAR_KEY` / `CLEAR_DOWEL` in
   `src/connectors.py` and rebuild (below).
2. Pieces `exports/STL/P6-*.stl` and `P7-*.stl`, one per plate, **already in print orientation**:
   part 6 pieces upside down, part 7 pieces upright, so the edge where the halves meet is on the bed
   and every pad starts on the plate. P6-E and P7-E are already turned 45° to fit.
   - Supports: tree supports only under the handle recesses (P6-BR, P7-BR, P6-E, P7-E). The other
     pieces need none.
   - The long thin pieces (A and B, 13.5 mm thick, 92 mm tall): use a 5 mm brim.
   - Suggested: 0.2 mm layers, 4 walls (the 4.46 mm walls print almost solid), PLA or PETG.
3. `exports/3MF/keys_and_dowels_plate.3mf`: 7 keys (6 + 1 spare) and 7 dowels (5 + 2 spare) on one
   plate, laid flat. No supports.

Material, roughly: 1.27 litres of part, about 1.5–1.6 kg of PLA at near-solid walls.

## Assemble

1. Stand the part 6 pieces up in place (labels P6-AL … P6-E are engraved on the inside faces).
2. Push the dowels into the holes along part 6's top edge.
3. Lower the part 7 pieces onto part 6: dowels into holes, seams in line.
4. From inside, slide a key up into each of the 6 seam grooves from the bottom edge until it stops.
5. Fit the hard panel into the bottom of part 6. It also holds the keys in.

A drop of CA glue on the keys makes the shell permanent; without glue it can be taken apart again.

## Files

- `exports/STL/` – 14 pieces, the key, the dowel and the fit test, ready for Bambu Studio.
- `exports/3MF/keys_and_dowels_plate.3mf` – the small parts on one plate.
- `exports/STEP/rhino_part6_connectors.step`, `rhino_part7_connectors.step` – for Rhino, placed
  exactly where parts 6 and 7 are in your file: union `part*_pads_to_add`, BooleanDifference
  `part*_cut_tools`, then split at x 13036.33 (side walls), x 12948 / 13124.66 (end wall) and
  y −652 / −482.
- `exports/STEP/connectors_assembled.step` – pads, keys and dowels with part 7 stacked on part 6.
- `exports/pieces_report.json` – size, volume and checks for every piece.
- `src/connectors.py` – every connector dimension and tolerance; `src/check_fit.py` checks the
  clearances; `src/exports.py` writes the files.
- `tools/make_pieces.py` – reads the .3dm, cuts and joins the meshes, writes the pieces;
  `tools/make_plates.py`, `tools/preview.py` – plate and previews.

Rebuild after a change:

```bash
cad run src/exports.py
python tools/make_pieces.py part_6_and_7.3dm build exports
python tools/make_plates.py exports
```

(`make_pieces.py` needs `pip install rhino3dm trimesh manifold3d mapbox_earcut`.)

## Limits

- The pieces are cut from the render meshes saved in the .3dm (about 4,000–9,000 triangles per
  part), so the corner fillets are faceted. For smoother prints, export each part from Rhino as a
  fine STL and point `make_pieces.py` at it, or send me the parts as STEP.
- Part 7's mesh had a small gap in its bottom face; it was closed by trimming 0.02 mm off the
  bottom edge.
- The print check passes on every piece but one: P7-AL has a 0.59 mm rib inside the engraved
  letter "A", a cosmetic 0.6 mm-deep detail.
- No strength check was run on the joints.
