import sys, rhino3dm as r
m = r.File3dm.Read(sys.argv[1])
s = m.Settings
print("units", s.ModelUnitSystem, "tol", s.ModelAbsoluteTolerance)
print("layers:")
for i, l in enumerate(m.Layers):
    print(" ", i, repr(l.FullPath), l.Visible)
print("objects:", len(m.Objects))
for o in m.Objects:
    g, a = o.Geometry, o.Attributes
    bb = g.GetBoundingBox()
    extra = ""
    if isinstance(g, r.Brep):
        extra = f"faces={len(g.Faces)} solid={g.IsSolid}"
    elif isinstance(g, r.Extrusion):
        extra = f"extrusion solid={g.IsSolid}"
    elif isinstance(g, r.Mesh):
        extra = f"verts={len(g.Vertices)}"
    print(f"{type(g).__name__:12s} layer={a.LayerIndex:2d} name={a.Name!r:22s} {extra:22s} "
          f"min=({bb.Min.X:.1f},{bb.Min.Y:.1f},{bb.Min.Z:.1f}) max=({bb.Max.X:.1f},{bb.Max.Y:.1f},{bb.Max.Z:.1f})")
print("blocks:", len(m.InstanceDefinitions))
for d in m.InstanceDefinitions: print(" ", d.Name)
