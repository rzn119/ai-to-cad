# Suitcase body: printable pieces with hidden joints (Bambu A1 mini)

**Current version: `exports/v3/`**, made from the updated `part_6_and_7.3dm` (the pieces split in
Rhino to fit the 180 × 180 × 180 mm plate). Part 6 is the upper ring, part 7 the lower tray with the
floor; part 6's bottom edges sit on part 7's top edges. Every piece is joined to its neighbours, every
joint is inside the faces that meet (nothing shows inside or out), and every clearance is **0.2 mm**.
(The files directly in `exports/STL`, `exports/STEP` are the earlier kit for the earlier model.)

## The joints

| Where | Joint | Size | Clearance |
| --- | --- | --- | --- |
| **Part 6, between its pieces** (all 8 seams) | **Sliding T-rail** in the cut face: one piece's rail runs in the next piece's T-slot. The pieces slide together vertically | rail: 1.2 mm neck for 1.2 mm, 2.0 mm head to 3.0 mm out; slot 1.6 / 2.4 mm | 0.2 mm all round; pulled apart, it catches after 0.25 mm |
| **Part 7, between its wall pieces** (the 6 side-wall seams) | **2 tabs per seam** in the cut face, standing out along the wall | tab 1.6 × 12 mm, 3.0 mm out; pocket 2.0 × 12.4 × 3.4 mm | 0.2 mm all round, 0.4 mm at the end |
| **Part 7 top edge ↔ part 6 bottom edge** | **41 keys** on part 7's top edge into pockets in part 6's bottom edge. Your seams in the two parts are 18 mm apart, so each part 6 piece bridges a part 7 seam: brick-fashion, this ties both parts together | key 10 × 1.6 × 4.0 mm; pocket 10.4 × 2.0 × 4.4 mm | 0.2 mm, 0.4 mm at the bottom |
| **Part 7 floor seams across the length**, bottom wall → floor, end wall → floor | **16 floor keys** in the middle of the 5.7 mm floor | tab 12 × 2.0 mm, 3.0 mm out; pocket 12.4 × 2.4 × 3.4 mm | 0.2 mm |
| **Part 7 centre seam** (left ↔ right half) | **7 bayonet T-locks** in the floor and the bottom wall: push together at a window, slide 16 mm, locked | T-tab 1.6 / 3.2 mm | 0.2 mm; catches after 0.2 mm |
| Floor panels ↔ walls | panels kept **0.2 mm clear of the walls all round** so they drop in | — | 0.2 mm |

Part 7's centre seam in the end wall and the bottom wall has no extra joint: the halves slide 16 mm
past each other to lock the bayonets, and a 4.5 mm wall has no room for a 16 mm slot. Those halves
are held by the bayonets (the bottom wall has its own) and each end-wall half is keyed to its floor
panel.

**Fixed in this version:** in the previous one each part 7 corner (C) had keys into its floor panel
from the end wall (along y) and from the side wall (along x). A piece can only be pushed one way, so
the corners could not have gone together. Every key within a half of part 7 now points along the
side wall, and the side wall → panel keys are gone.

## Assembly order (each step checked: the piece moves in without touching anything)

**Part 7, each half** (all pushes along the side wall, towards the open end):
1. P7-B (bottom wall, wheels).
2. P7-S1 pushed onto P7-B (wall tabs and floor keys).
3. P7-F2 floor panel pushed onto P7-S1's floor.
4. P7-S2 pushed onto P7-S1 (wall tabs).
5. P7-F3 floor panel pushed onto P7-F2.
6. P7-C corner pushed onto P7-S2 (wall tabs) and P7-F3 (end-wall keys).

**Join the halves:** set the right half 16 mm further towards the end wall than the left, push them
together so the T-tabs enter their windows, slide the right half 16 mm towards the open end.

**Part 6**, each piece lowered from above onto part 7's keys and down its neighbours' T-rails, in
this order: P6-C-R, P6-C-L, P6-S2-L, P6-S2-R, P6-B-L, P6-B-R, P6-S1-L, P6-S1-R. (The end-wall centre
slot is open at the top and the bottom-wall centre and B|S1 slots at the bottom, which sets the order
of those pieces; the other seams slide either way.)

Optional: glue in the slots and pockets for a permanent body. Without it the pieces cannot be pulled
apart sideways; part 6 is held down by its weight and whatever closes the top (the frame).

## What I changed in your model, and why

- **Floor seam between P7-S1 and P7-F2 moved 5 mm, y −644.23 → −639.23.** The middle floor panels
  were exactly 180.0 × 156 mm, the whole plate, too wide to turn. They are now 175 mm.
- **Floor panels (and the 5 mm of floor S1 took over) kept 0.2 mm clear of the walls.**
- **The frame lock strips are joined to the part 6 wall pieces they sit on.**
- **Mesh repairs:** gaps in 11 saved display meshes closed; P7-B-L and P6-C-R rebuilt as mirrors
  of P7-B-R and P6-C-L (as they are in your model, volumes within 0.5 %).

## Pieces (20)

| Piece | What | On the plate (mm) | Print |
| --- | --- | --- | --- |
| P6-B-L / R | part 6 bottom wall (wheels) | 164 / 161 × 46 × 92 | upside down |
| P6-S1-L / R | part 6 side wall, open-end piece | 12 × 120 × 92 | upside down |
| P6-S2-L / R | part 6 side wall, middle (R has the handle) | 132 × 132 × 92, turned 45° | upside down |
| P6-C-L / R | part 6 corner, half the end wall | 164 / 161 × 160 × 92 | upside down |
| P7-B-L / R | part 7 bottom wall (wheels) | 164 / 161 × 46 × 96 | as it stands |
| P7-S1-L / R | part 7 side wall with the floor at the open end | 164 / 161 × 143 × 96 | as it stands |
| P7-S2-L / R | part 7 side wall, middle (R has the handle) | 132 × 132 × 96, turned 45° | as it stands |
| P7-C-L / R | part 7 corner, half the end wall | 161 × 142 × 96 | as it stands |
| P7-F2-L / R | floor panel, middle | 159 / 156 × 175 × 5.7 | flat |
| P7-F3-L / R | floor panel, end-wall side | 159 / 156 × 140 × 5.7 | flat |

Part 6 prints upside down (top edge on the bed): about a tenth of the support it would need upright.
Supports are needed under the handle recesses and wheel housings (most: P6-S2-R and P7-S2-R, about
70–80 cm³ each).

## Files

- `exports/v3/STL/` – the 20 pieces in print orientation, ready for Bambu Studio.
- `exports/v3/STEP/rhino_part6_joints.step`, `rhino_part7_joints.step` – for Rhino, placed on your
  pieces where they are in the .3dm: union `<piece> add`, BooleanDifference `<piece> cut`.
- `exports/v3/pieces_report.json` – size, volume, fit and the overlap check for every piece.
- `tools/v3_prepare.py` – reads the .3dm, repairs, stacks, moves the floor seam, places every joint
  (ring keys tested against the real wall outlines); writes `build/v3/joints.json`.
- `src/v3_joints.py` – every joint's shape and clearance; `src/check_v3.py` checks them;
  `src/v3_build.py` writes each piece's joint geometry and the Rhino STEPs.
- `tools/v3_make_pieces.py` – applies the joints, lays out the pieces, checks overlaps;
  `tools/v3_preview.py` – renders. `viewer/bayonet.html` – the 3D bayonet demo.

```bash
python tools/v3_prepare.py part_6_and_7.3dm build/v3
cad run src/v3_build.py
cad run src/check_v3.py
python tools/v3_make_pieces.py build/v3 exports/v3
```
(Python tools: `pip install rhino3dm trimesh manifold3d pymeshfix mapbox_earcut shapely`.)

## Checks run

- Clearances measured on the solids: part 6 T-rail, part 7 seam tab, ring key, floor key and
  bayonet all 0.200 mm; a tab 0.3 mm too large is caught.
- Assembly: every piece moved along its way in, in the order above, touches nothing (largest
  0.007 mm³, face contact).
- Pull-apart: a part 6 seam catches after 0.25 mm on its T-rail alone; with the keys from part 7,
  every piece is held within 0.3 mm.
- All 20 pieces closed and on the 180 mm plate with at least 2 mm to spare each side.
- Assembled, no two pieces overlap beyond face contact at your seams (≤ 0.002 mm thick).
- 3D-printing check (FDM, PLA): 19 of 20 pass, thinnest wall 0.99 mm beside a T-slot. P7-C-R has a
  0.02 mm sliver in your model where the end-wall recess meets the top edge; a slicer skips it.

## Limits

- About 1 mm of wall beside the T-slots in the 4.46 mm walls: slide the part 6 pieces in gently and
  in line.
- Part 6 is not locked down against lifting off part 7.
- Curves are slightly faceted (from the .3dm's saved display meshes); a fine STL or STEP export from
  Rhino gives smoother prints.
- No strength check was run on the joints.
