"""One mesh per 3dm object (npz) plus an index with layer, bbox and role."""
import sys, json, numpy as np, rhino3dm as r
src, out = sys.argv[1], sys.argv[2]
m = r.File3dm.Read(src)
layers = [l.FullPath for l in m.Layers]
index = []
for i, o in enumerate(m.Objects):
    g = o.Geometry
    if isinstance(g, r.Extrusion):
        mm = g.GetMesh(r.MeshType.Any); parts = [mm] if mm else []
        if not parts: g = g.ToBrep(False)
    if isinstance(g, r.Brep):
        parts = [f.GetMesh(r.MeshType.Any) for f in g.Faces]; parts = [p for p in parts if p]
    elif not isinstance(g, r.Extrusion):
        parts = []
    if not parts: continue
    V, F = [], []
    for p in parts:
        p.Faces.ConvertQuadsToTriangles(); b = len(V)
        V += [(p.Vertices[k].X, p.Vertices[k].Y, p.Vertices[k].Z) for k in range(len(p.Vertices))]
        F += [(p.Faces[k][0] + b, p.Faces[k][1] + b, p.Faces[k][2] + b) for k in range(len(p.Faces))]
    V, F = np.array(V), np.array(F)
    np.savez(f"{out}/o{i}.npz", v=V, f=F)
    bb = g.GetBoundingBox()
    index.append({"i": i, "layer": layers[o.Attributes.LayerIndex], "min": [bb.Min.X, bb.Min.Y, bb.Min.Z], "max": [bb.Max.X, bb.Max.Y, bb.Max.Z]})
json.dump(index, open(f"{out}/index.json", "w"), indent=0)
print(len(index), "objects")
