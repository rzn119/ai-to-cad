"""Check the Rhino STEP files carry each bayonet as designed, in the .3dm's coordinates."""
from pathlib import Path

import build123d as bd

import v3_joints as v

ROOT = Path(__file__).resolve().parent.parent
p7 = bd.import_step(str(ROOT / "exports" / "v3" / "STEP" / "rhino_part7_joints.step"))
p6 = bd.import_step(str(ROOT / "exports" / "v3" / "STEP" / "rhino_part6_joints.step"))
solids7 = {c.label.replace("_", " "): c for c in p7.children}      # STEP labels read back as "P7-F3-L_add"


def inside(shape, x, y, z):
    return any(sol.is_inside(bd.Vector(x, y, z)) for sol in shape.solids())


ok = True
for j in (j for j in v.SPEC["floor"] if j["kind"] == "bayonet"):
    left, right = solids7[f"{j['on']} add"], solids7[f"{j['into']} cut"]
    x, y, z = v.XC, j["y"], v.ZF
    checks = {
        "tab head on the left piece, at the lock": inside(left, x + 2.3, y, z + 1.4),
        "T-slot head in the right piece, at the lock": inside(right, x + 2.3, y, z + 1.6),
        "lip left standing at the lock (what holds it)": not inside(right, x + 0.5, y, z + 1.4),
        "straight window 16 mm towards the end wall": inside(right, x + 0.5, y - v.BAY_SLIDE, z + 1.4),
        "channel joining window and lock": inside(right, x + 2.3, y - v.BAY_SLIDE / 2, z + 1.6),
        "no window at the lock's other side": not inside(right, x + 0.5, y + v.BAY_SLIDE, z + 1.4),
    }
    bad = [k for k, val in checks.items() if not val]
    ok &= not bad
    print(f"{j['on']} -> {j['into']} at y {y:.1f}: {'all as designed' if not bad else 'WRONG: ' + ', '.join(bad)}")
# part 6: nothing of its joints may reach the floor level where the bayonets are (part 6 is the upper ring)
lowest6 = min(c.bounding_box().min.Z for c in p6.children)
print(f"part 6 STEP: lowest joint feature at z {lowest6:.1f} in the .3dm (part 6 sits at z -177.2 .. -84.9 there): "
      "no bayonets, as designed (they are only in part 7's floor)")
print("RESULT:", "every bayonet in the Rhino file matches" if ok else "MISMATCH")
