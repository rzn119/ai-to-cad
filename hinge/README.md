# Hinge that holds an angle (from `hinge.3dm`)

Your hinge is a print-in-place cone pivot. Cone bosses on the channel walls run in cone sockets in the
knuckle, 0.2 mm apart. The arm swings from −5° (it meets the floor edge) to 180° (folded back into
the channel). All three options keep your box, knuckle, arm and end piece and the same pivot axis
(x along the axis, y = −397.146, z = −162.16). Rebuilt to within 0.002 mm of your file
(95th percentile).

**Note:** your connector has a cone boss only on the right wall, but the knuckle has a socket on both
sides. I added the matching left boss (in the original and in A and B).

| | A · Click detent | B · Ratchet | C · Clamp knob |
| --- | --- | --- | --- |
| How it holds | V-nub on a spring bridge in the floor clicks into 13 V-notches on the knuckle | Pawl in the floor engages 7 saw-tooth notches. Going up it clicks; going down it meets a square face | M4 bolt through walls and knuckle. Slit walls (ears) clamp the knuckle when the knob is tightened |
| Angles | every 15°, 0–180° | every 30°, 0–180° (15° teeth are too small on a 6.2 mm knuckle) | any |
| To move | push the arm | lift freely; to lower, press the pawl's front end down (about 3 mm) | loosen the knob |
| Holds | light loads (panel weight) | positively, against loads pushing the arm down | strongest, about 1 N·m hand-tight (estimate) |
| Hardware | none | none | M4 × 25 bolt, M4 nut (in the knob) |
| Printing | in place, upright (floor on the plate) | in place, upright; support under the pawl from the plate | 3 parts: box upright, arm on its side, knob flat |

## Files
- `exports/hinge_A.step`, `hinge_B.step`, `hinge_C.step`: for Rhino, in your file's coordinates. Each holds the connector, arm, end piece (and C's knob and bolt).
- `exports/print/A|B|C/*.stl`: on the plate, ready for Bambu Studio. For A and B, load both STLs as one object (print in place).
- `renders/`: views at 60° and the section drawing. `viewer/index.html`: the 3D page.
- `src/hinge_options.py`: all geometry (`cad run src/hinge_options.py`). `tools/check_hinges.py`: the checks.

## Checks run
- The arm, swept 0–180° in 5° steps, touches nothing except the spring tooth (A, B), which is analysed separately.
- Gap to the spring tooth at every stop: 0.20 mm. Most the spring gives: 0.57 mm (A) and 1.0 mm (B). Peak strain is about 1.1 % in both (PLA yields around 2.5 %).
- B, lowering from each stop: the tooth would have to drop 1.0 mm through a vertical face, so it is locked.
- 3D-print check (FDM, PLA, 180 mm plate): all parts pass, with warnings only (the knuckle underside and A's 24.5 mm bridge).

## Limits
- Play of about ±2.5° (A) and ±1.5° (B) at each stop, from the 0.2 mm print-in-place clearance.
- Holding strength is estimated, not load-tested. PETG springs last longer than PLA ones for frequent use.
- As in your original, the knuckle prints over a 0.9 mm gap above the floor, so its underside will sag slightly.
