"""Move the whole right half of part 7 through the bayonet assembly against the whole left half,
using the final pieces: push in at the windows (16 mm towards the end wall), slide 16 mm towards
the open end, then try to pull apart. usage: v3_check_bayonet_path.py build/v3/assembled"""
import sys, trimesh
d = sys.argv[1]
names = ["B", "S1", "S2", "C", "F2", "F3"]
L = [trimesh.load(f"{d}/P7-{n}-L.stl") for n in names]
R = [trimesh.load(f"{d}/P7-{n}-R.stl") for n in names]
def overlap(dx, dy):
    t = 0.0
    for r in R:
        m = r.copy(); m.apply_translation([dx, dy, 0])
        for l in L:
            i = trimesh.boolean.intersection([m, l], engine="manifold"); t += float(i.volume) if len(i.faces) else 0.0
    return t
GAP = 0.05      # the two bottom-wall halves touch face to face on the centre plane; test just clear of it
push = max(overlap(dx, 16.0) for dx in (10, 5, 3, 2, 1, 0.5, GAP))
slide = max(overlap(GAP, dy) for dy in (16, 12, 8, 4, 2, 1, 0.5, 0.0))
caught = overlap(0.3, 0.0)
blocked = overlap(1.5, 0.0)
print(f"push in at the windows: largest overlap {push:.3f} mm3")
print(f"slide 16 mm:            largest overlap {slide:.3f} mm3")
print(f"locked, pulled 0.3 mm:  {caught:.1f} mm3 (caught)")
print(f"straight in, no offset: {blocked:.1f} mm3 (blocked)")
ok = push < 0.01 and slide < 0.01 and caught > 1 and blocked > 1
print("RESULT:", "the bayonets work as designed" if ok else "PROBLEM"); sys.exit(0 if ok else 1)
