#!/bin/bash
# Re-render every joint and re-export its STEP/GLB. Run from joints/ after `cad run src/*.py`.
set -e
CAD=${CAD:-cad}
# label id clip_x section_camera opened_camera
while read -r L ID CX SCAM OCAM; do
  [ -z "$L" ] && continue
  $CAD model snapshot "$ID" "renders/${L}_opened.png" --camera "$OCAM" --preview \
    --display "{\"isolated\":[\"$L/opened\"]}" --width 1200 --height 900
  if [ "$CX" = "none" ]; then
    $CAD model snapshot "$ID" "renders/${L}_detail.png" --camera "$SCAM" --preview \
      --display "{\"isolated\":[\"$L/assembled\"]}" --width 1200 --height 900
  else
    $CAD model snapshot "$ID" "renders/${L}_detail.png" --camera "$SCAM" --preview \
      --display "{\"isolated\":[\"$L/assembled\"],\"clip\":{\"enabled\":true,\"axis\":\"x\",\"at\":$CX,\"invert\":false}}" \
      --width 1000 --height 1400
  fi
  $CAD model export "$ID" "exports/STEP/${L}.step" "exports/GLB/${L}.glb"
done <<'LIST'
1A_groove_and_lip 87726e8d-7b20-568f-9e72-93cfed2e5188 80 65:12 150:25
1B_keyhole_slots 22f29ab9-3a26-5d94-a919-911f1d853ac7 24 65:12 150:25
1C_magnets_and_pins 6e06a2e7-05b2-5d2b-ab9d-ec2f73d7797b 7.5 65:12 150:25
1D_draw_latch 24c50a98-74d5-5acd-93db-da03819838b7 none 240:20 150:25
2-1_keyhole_ladder c67a1bb6-aa2e-5c55-9f46-73f84f9cf623 15 65:12 30:20
2-2_spring_plunger 67cef488-3362-5ffd-a8e6-e200fe36f53e 15 65:12 30:20
2-3_rack_and_pawl 386cc8cb-70e6-5ad5-9077-20dfe6fac922 15 65:12 30:20
2-4_cam_clamp 050a9e00-de5a-58b8-8033-f20f00efa000 15 65:12 30:20
LIST
