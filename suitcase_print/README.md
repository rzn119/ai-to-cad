# Suitcase body: printable pieces with hidden joints (Bambu A1 mini)

Parts 6 and 7 from `part_6_and_7.3dm`, cut into **14 pieces (7 per part)** that each fit the
A1 mini's 180 × 180 × 180 mm build volume with at least 5 mm to spare. Every joint is **inside the
cut faces**: nothing stands on the inside or the outside of the shell, and the only thing you see
assembled is the seam line.

## The joints

| Joint | What it is | Size | Fit |
| --- | --- | --- | --- |
| 6 vertical seams per part | **Sliding dovetail the full height of the cut face.** A rail stands 3.0 mm out of one piece's face; the next piece has the matching slot | rail 1.4 mm at the root → 2.0 mm at the tip, in the 4.46 mm wall | 0.15 mm per side, 0.2 mm at the slot's end; leaves 1.06 mm of wall beside the slot |
| Part 6 to part 7, all the way round | **Tongue and groove on the edges**, following the wall through the corners and both handle recesses | tongue 1.6 wide × 3.0 tall on part 6's top edge; groove 2.0 wide × 3.4 deep in part 7's bottom edge | 0.2 mm per side, 0.4 mm at the bottom; leaves 1.23 mm of wall beside the groove |

The dovetails stop the pieces pulling apart along the wall; the tongue keeps the two halves in line
and stops them sliding sideways. Everything goes together in one direction, straight down.

## What changed from the drawn grid, and why

- **Side-wall cuts at y −652 and −482** (the grid had −662.2 and −482.2). The grid's middle row was
  exactly 180.0 mm, the whole plate. The longest piece is now 173 mm, rail included.
- **The end wall is cut either side of its handle recess (x 12948 and 13124.7), not in the middle:**
  7 pieces per part instead of 6. The drawn centre cut runs through the 140 mm handle recess the case
  is lifted by. The middle piece (E) holds the whole handle and fits the plate turned 45°.
- **Part 7 stacks on part 6**, completing the two handle recesses that cross that joint.

## Print

1. **Print `exports/STL/fit_test.stl` first** (110 × 20 mm, printed upright like the pieces):
   - three dovetail pairs: slot stubs with 1, 2, 3 notches = 0.10, 0.15, 0.20 mm clearance;
   - one tongue stub and three groove stubs with 1, 2, 3 notches = 0.15, 0.20, 0.25 mm.
   Slide each pair together vertically. If the 0.15 dovetail or the 0.20 groove is tight or loose on
   your printer, set `CLEAR_RAIL` (and the groove width in `tools/joint_section.py`) and rebuild.
2. The 14 pieces, `exports/STL/P6-*.stl` and `P7-*.stl`, one per plate, **already oriented: upright,
   as they stand in the suitcase.** Part 6's tongue points up; part 7's groove opens at the bed.
   P6-E and P7-E are turned 45° to fit.
   - Supports: tree supports under the handle recesses only (P6-BR, P7-BR, P6-E, P7-E).
   - The straight pieces are 4.5 mm thick and up to 173 × 95 mm: use a 5–8 mm brim, and turn on
     "elephant foot compensation" (Bambu Studio's default 0.15 mm is fine) so the groove at part 7's
     bottom stays open.
   - Suggested: 0.2 mm layers, 4 walls, PLA or PETG. About 1.01 litres of part (≈1.26 kg PLA solid).

## Assemble

1. Part 6: stand one piece up, then slide the next one down onto it so its slot runs over the rail
   (or its rail into the slot). Carry on round the U. A piece between two others slides down past
   both at once.
2. Part 7: lower each piece down past its neighbours and onto part 6's tongue.
3. Optional: a little CA glue or 2-part epoxy in the slots and groove before sliding makes it
   permanent. Without glue the dovetails hold the shell together sideways and the tongue holds it
   in line; the halves are held down by their own weight and whatever clamps the shell (the frame
   ring, the hard panel).

Assembly map (looking down into the U, open end at the bottom):

```
          end wall:  CL | E | CR
                     ---+---+---
   left wall:  CL                 CR   right wall
               BL                 BR   (BR holds the side handle)
               AL                 AR
                    (open end)
```
Each position has a P6 piece (lower half) and a P7 piece (upper half). The engraved labels are off
(`LABELS = False` in `src/hidden_joints.py`) to keep every face clean; name the pieces with a pencil
on the cut face, or turn the labels back on.

## Files

- `exports/STL/` – the 14 pieces and the fit test, ready for Bambu Studio.
- `exports/STEP/rhino_part6_joints.step`, `rhino_part7_joints.step` – for Rhino, placed exactly on
  parts 6 and 7 where they sit in your file. Split each part at x 13036.33 (side walls),
  x 12948 / 13124.66 (end wall) and y −652 / −482, then for each piece union `<piece> add` (its rails,
  and part 6's tongue) and BooleanDifference `<piece> cut` (its slots, and part 7's groove).
- `exports/STEP/hidden_joints_assembled.step` – the rails and the tongue in the assembled position.
- `exports/pieces_report.json` – size, volume and checks for every piece.
- `src/hidden_joints.py` – every joint dimension and clearance; `src/check_hidden.py` checks the
  clearances; `src/build_parts.py` writes each piece's add/cut geometry; `src/exports.py` the STEPs
  and the fit test.
- `tools/joint_section.py` traces the wall at the joint in the .3dm (tongue and groove outlines);
  `tools/make_pieces.py` cuts the shells into pieces and applies the joints; `tools/preview.py`
  renders.

Rebuild after a change:

```bash
python tools/joint_section.py part_6_and_7.3dm build/joint_section.json
cad run src/build_parts.py
cad run src/exports.py
python tools/make_pieces.py part_6_and_7.3dm build exports
```

(The Python tools need `pip install rhino3dm trimesh manifold3d mapbox_earcut shapely`.)

## Checks run

- Rail to slot 0.150 mm and tongue to groove 0.200 mm, measured on the solids; a rail made 0.2 mm
  too wide is caught.
- All 14 pieces closed (watertight) and inside the plate with ≥ 5 mm to spare.
- No two pieces overlap when assembled (31 touching pairs, largest overlap 0.0000 mm³); a piece
  pushed 0.3 mm into its neighbour is caught (95 mm³).
- 3D-printing check (FDM, PLA, general design rules) passes on all 14 pieces and the fit test;
  thinnest wall 1.05 mm, beside the slots.

## Limits

- The pieces are cut from the render meshes saved in the .3dm, so the corner fillets are faceted.
  Export each part from Rhino as a fine STL (or STEP) for smoother prints and rerun.
- Part 7's mesh had a small gap in its bottom face; it was closed by trimming 0.02 mm off the edge.
- The walls beside the slots are about 1 mm: strong enough to locate and hold the pieces, but
  slide the pieces together gently and in line, and glue them for a permanent shell.
- No strength check was run on the joints.
