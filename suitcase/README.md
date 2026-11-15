# Suitcase panel joints

Three nail-free joints that fix each panel to the body in **both** forms of the convertible
suitcase, modelled on `ai_to_cad_suitcase_demo.3dm` in that file's own coordinates (mm, Z up).

| | Option | Suitcase form | Shelf form (height) |
| --- | --- | --- | --- |
| A | Drop-in T-blocks | blocks drop through windows in the slot lips, slide 20 mm down, detent clicks | link shoe on 2 blocks, 11 heights at 40 mm |
| B | Spring index pins | 2 spring pins per rail snap into holes in the slot floor | captive shoe + spring pin, 17 heights at 30 mm |
| C | Quarter-turn twist locks | 3 hammer-head locks per rail turn behind the lips | 2 T-bolts with thumb knobs, any height (clamped) |

All three widen the ring's T-slot chamber from 10 to 14 mm (3 mm lips instead of 1 mm), replace the
panels' continuous T-tongue (its 10.5 mm head does not fit the 10 mm chamber, and the slot is closed
at both ends) and replace the drawn links/pins with a new link and a ball-lock pin per corner.

## Into Rhino

1. Delete what the joints replace: the front and back frame rings and the 8 panel T-tongues
   (layer `frame track`), all 24 objects on `screws/nails`, and the four 2.4 mm hinge plates on
   `foldable surface`.
2. `File > Import` `exports/STEP/<a|b|c>_shelf.step` (panels as drawn) or `<a|b|c>_suitcase.step`
   (panels closed). It lands in place. Parts are named by corner: FL, FR, BL, BR.
3. Or keep your own rings/panels and BooleanDifference the cut tools in `exports/STEP/<a|b|c>_cuts.step`
   (`cut_ring_slot` from each ring, `cut_panel` from each panel as drawn).

Closed pose of a panel = the drawn panel rotated +23° about X, then moved (0, 254.68, −962.44) mm.

## Files

- `src/base.py` – dimensions measured from the .3dm, the rebuilt ring, link and ball-lock pin.
- `src/options.py` – the three options: `<opt>_suitcase`, `<opt>_suitcase_pulled`, `<opt>_shelf`,
  `<opt>_cuts`, and short `<opt>_detail_*` pieces for sections.
- `src/exports.py` – writes every STEP and GLB (`cad run src/exports.py`).
- `tools/` – reading the .3dm (`rhino_to_meshes.py`, `closed_pose.py`, `inspect_3dm.py`; need
  `pip install rhino3dm trimesh scipy shapely`), `compose.py` to merge a joint GLB with the Rhino
  meshes, `render_all.sh` for the images in `renders/`.
- `viewer/index.html` + `models.js` – the comparison page.
