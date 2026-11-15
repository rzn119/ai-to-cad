#!/bin/bash
# Render every option: composites with the Rhino model (needs the per-object meshes in $OBJS and
# the venv in $PY) and capped sections of the detail models. Run from suitcase/.
set -e
CAD=${CAD:-cad}
mkdir -p renders tmp
declare -A DS=( [a]=43ceb9e2-eacb-5574-807f-78ac3678e584 [b]=f842a25f-642c-54ad-9452-91bd7f529373 [c]=da7826ec-0d07-5040-bda0-d7949018a804 )
declare -A DH=( [a]=82d78091-b562-5342-8b0d-402866b914d9 [b]=67b45740-0385-5788-97e4-ceb5aa42e805 [c]=cf476fb5-7483-537d-8f1d-c1776a76c406 )
for o in a b c; do
  $PY -I tools/compose.py $OBJS exports/GLB/${o}_shelf.glb shelf tmp/${o}_shelf.glb >/dev/null
  $PY -I tools/compose.py $OBJS exports/GLB/${o}_suitcase.glb suitcase tmp/${o}_closed.glb >/dev/null
  $PY -I tools/compose.py $OBJS exports/GLB/${o}_suitcase_pulled.glb suitcase tmp/${o}_pulled_c.glb --explode 120 --crop 10880,3000,-150 10990,3200,140 >/dev/null
  $PY -I tools/compose.py $OBJS exports/GLB/${o}_shelf.glb shelf tmp/${o}_shelf_c.glb --crop 10880,3080,-140 10990,3200,30 >/dev/null
  $CAD glb snapshot tmp/${o}_shelf.glb renders/${o}_shelf.png --camera iso --preview --width 1100 --height 1100
  $CAD glb snapshot tmp/${o}_closed.glb renders/${o}_suitcase.png --camera iso --preview --width 1100 --height 1100
  $CAD glb snapshot tmp/${o}_pulled_c.glb renders/${o}_suitcase_corner.png --camera 290:20 --preview --width 900 --height 1000
  $CAD glb snapshot tmp/${o}_shelf_c.glb renders/${o}_shelf_corner.png --camera 240:25 --preview --width 900 --height 1000
  $CAD model snapshot ${DS[$o]} renders/${o}_section_suitcase.png --camera 70:12 --preview \
    --display '{"clip":{"enabled":true,"axis":"x","at":10936.5,"invert":false}}' --width 900 --height 1000
  $CAD model snapshot ${DH[$o]} renders/${o}_section_shelf.png --camera 70:12 --preview \
    --display '{"clip":{"enabled":true,"axis":"x","at":10936.5,"invert":false}}' --width 900 --height 1000
done
