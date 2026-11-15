# Suitcase joint studies

Nail-free joint options for the multipurpose suitcase, modelled as sample pieces
(text-to-cad / build123d). Every model holds two copies: assembled, and "opened like a book"
so both mating faces point the same way.

| Code | Joint | Form |
| --- | --- | --- |
| 1A | Perimeter groove + frame lip | Suitcase: frame to body |
| 1B | Keyhole slots + mushroom studs | Suitcase: frame to body |
| 1C | Hidden magnets + tapered locating pins | Suitcase: frame to body |
| 1D | Over-centre draw latch | Suitcase: frame to body |
| 2-1 | Keyhole ladder | Shelf: box height on the legs |
| 2-2 | Spring plunger in a C-channel | Shelf: box height on the legs |
| 2-3 | Sawtooth rack + gravity pawl | Shelf: box height on the legs |
| 2-4 | T-slot + cam-lever clamp | Shelf: box height on the legs |

- `exports/STEP/` – open in Rhino (File › Import). Parts are named and coloured.
- `exports/GLB/` – the same models for web/3D viewers.
- `renders/` – an opened view and a section/detail view of each joint.
- `src/` – the parametric models. Rebuild with `cad run src/frame_joints.py` and
  `cad run src/height_joints.py`, then `./render_all.sh` and `python3 crop_renders.py`.
- `viewer/joint-viewer.html` – the interactive page (needs `models.js` beside it).

Sample sizes are placeholders: 15 mm body walls, 30 × 14 mm frame bars, 30 × 18 mm leg rails.
