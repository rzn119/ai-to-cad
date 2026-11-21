# Suitcase body: printable pieces with hidden joints (Bambu A1 mini)

**Current version: `exports/v3/`**, made from the updated `part_6_and_7.3dm` (the pieces split in
Rhino). Part 6 is the upper ring, part 7 the lower tray with the floor; part 6's bottom edges sit
on part 7's top edges. Every joint is inside the faces that meet; nothing shows inside or out. All
clearances are **0.2 mm**. (The files directly in `exports/STL`, `exports/STEP` are the earlier
kit for the earlier model.)

## The joints

| Where | Joint | Size | Clearance |
| --- | --- | --- | --- |
| Part 6 bottom edge ↔ part 7 top edge, all round | **41 keys** on part 7's top edge into pockets in part 6's bottom edge. Your seams in part 6 and part 7 are 18 mm apart along the side walls, so each part 6 piece rests on two part 7 pieces and a key either side of the part 7 seam ties them together, brick-fashion | key 12 × 1.6 × 4.0 mm (top edges chamfered 0.4); pocket 12.4 × 2.0 × 4.4 mm | 0.2 mm all round, 0.4 mm at the bottom |
| Part 7 floor seams across the length; bottom wall → floor; walls → floor panels | **24 floor keys** in the middle of the 5.7 mm floor | tab 12 × 2.0 mm, 3.0 mm out; pocket 12.4 × 2.4 × 3.4 mm | 0.2 mm all round |
| Part 7 centre floor seam (left ↔ right half) | **7 bayonet T-locks**: a T-tab (1.6 mm neck, 3.2 mm head, 3.0 mm out) runs in a T-slot; a window 16 mm along the seam lets it in | — | 0.2 mm all round; locked, it catches after 0.2 mm of pull |
| Floor panels ↔ walls | the panels are kept **0.2 mm clear of the walls all round**, corners included, so they drop in between the walls | — | 0.2 mm |

## What I changed in your model, and why

- **Floor seam between P7-S1 and P7-F2 moved 5 mm, from y −644.23 to −639.23.** The middle floor
  panels were exactly 180.0 × 156 mm: the full A1 mini plate, which a panel that wide cannot be
  turned to fit. They are now 175 mm (2.5 mm clear each side on the plate); P7-S1 carries 5 mm
  more floor. The wall seams are unchanged.
- **Floor panels trimmed 0.2 mm where they meet the walls** (above).
- **The frame lock strips are joined to the part 6 wall pieces they sit on.**
- **Mesh repairs** (the .3dm's saved display meshes were not closed on 11 objects): gaps closed;
  P7-B-L and P6-C-R rebuilt as mirror images of P7-B-R and P6-C-L, which they are in your model
  (volumes agree within 0.5 %), because their repaired meshes were not clean.

## Pieces (20)

| Piece | What | On the plate | Print |
| --- | --- | --- | --- |
| P6-B-L / R | part 6 bottom wall (wheels), halves | 161 × 43 × 92 | upside down |
| P6-S1-L / R | part 6 side wall, open-end piece | 12 × 117 × 92 | upside down |
| P6-S2-L / R | part 6 side wall, middle (R has the handle) | 131 × 131 × 92, turned 45° | upside down |
| P6-C-L / R | part 6 corner with half the end wall | 161 × 160 × 92 | upside down |
| P7-B-L / R | part 7 bottom wall (wheels), halves | 164 × 46 × 96 | as it stands |
| P7-S1-L / R | part 7 side wall with the floor at the open end | 164 × 143 × 96 | as it stands |
| P7-S2-L / R | part 7 side wall, middle (R has the handle) | 130 × 130 × 96, turned 45° | as it stands |
| P7-C-L / R | part 7 corner with half the end wall | 161 × 142 × 96 | as it stands |
| P7-F2-L / R | floor panel, middle | 159 × 175 × 5.7 | flat |
| P7-F3-L / R | floor panel, end-wall side | 159 × 140 × 5.7 | flat |

Part 6 prints **upside down** (top edge on the bed, key pockets opening upwards): that needs about a
tenth of the support it would need upright (P6-B: 14 against 510 cm³). Part 7 prints as it stands
(floor down, keys up). Supports are needed under the handle recesses and the wheel housings (most:
P6-S2-R and P7-S2-R, about 70–80 cm³ each). Material: about 2.4 litres of part.

## Assemble

1. **Part 7, left half:** lay P7-F2-L and P7-F3-L between P7-S1-L, P7-S2-L and P7-C-L, keys into
   pockets (the walls' floor keys go into the panels' edges), and P7-B-L against P7-S1-L's floor.
2. **Part 7, right half:** the same.
3. **Join the halves:** set the right half 16 mm further towards the end wall than the left, push
   the two together so the T-tabs on the left floor enter the windows in the right floor, then slide
   the right half 16 mm towards the open end. The T-locks hold the halves together.
4. **Part 6:** lower each piece onto part 7's top edge, its pockets over the keys. Each part 6 piece
   bridges a part 7 seam and locks the two pieces under it together.
5. Optional: glue in the pockets for a permanent body; without it, part 6 is held down by its own
   weight and whatever closes the top (the frame).

## Files

- `exports/v3/STL/` – the 20 pieces, in print orientation, ready for Bambu Studio.
- `exports/v3/STEP/rhino_part6_joints.step`, `rhino_part7_joints.step` – for Rhino, placed on your
  pieces where they are in the .3dm: union `<piece> add`, BooleanDifference `<piece> cut`.
- `exports/v3/pieces_report.json` – size, volume, fit and the overlap check for every piece.
- `tools/v3_prepare.py` – reads the .3dm, repairs, stacks, moves the floor seam, traces the walls and
  places every key (each one tested against the real wall outline); writes `build/v3/joints.json`.
- `src/v3_joints.py` – every joint's shape and clearance; `src/check_v3.py` checks them;
  `src/v3_build.py` writes each piece's joint geometry and the Rhino STEPs.
- `tools/v3_make_pieces.py` – applies the joints, lays out the pieces, checks overlaps;
  `tools/v3_preview.py` – renders.

```bash
python tools/v3_prepare.py part_6_and_7.3dm build/v3
cad run src/v3_build.py
cad run src/check_v3.py
python tools/v3_make_pieces.py build/v3 exports/v3
```
(Python tools: `pip install rhino3dm trimesh manifold3d pymeshfix mapbox_earcut shapely`.)

## Checks run

- Clearances measured on the solids: ring key 0.200 mm, floor key 0.200 mm, bayonet 0.200 mm;
  a tab 0.3 mm too large is caught.
- Bayonet: the tab passes the window and the 16 mm slide with 0.2 mm to spare all the way, and
  once locked it catches when pulled 1 mm out.
- Every ring key tested against the traced walls of both pieces (at least 1 mm of wall beside a
  pocket, at least 2 mm between a pocket and a seam).
- All 20 pieces closed and on the 180 mm plate with at least 2 mm to spare each side.
- Assembled, no two pieces overlap: what remains is face-to-face contact at your seams, 0.002 mm
  or less (the largest, 1.1 mm³ over the whole bottom-wall seam).
- 3D-printing check (FDM, PLA): 19 of 20 pass, thinnest wall 1.02 mm beside a pocket. P7-C-R has a
  0.02 mm sliver in your model where the end-wall recess curve meets the top edge, which a slicer
  skips; it is not from a joint.

## Limits

- The pieces come from the display meshes saved in the .3dm, so curves are slightly faceted; export
  a fine STL or STEP from Rhino and rerun for smoother prints.
- Part 6 is not locked down onto part 7 against lifting (the keys stop it sliding, not lifting).
- No strength check was run on the joints.
