"""Cut through the middle of the spring (x = XC): the knuckle and the nub / pawl tooth, at a stop
and half-way to the next, for A and B. Writes renders/sections.png."""
import json
from pathlib import Path
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "build" / "params.json").read_text())
XC, AY, AZ = P["XC"], P["AY"], P["AZ"]

def cut(path, deg=0):
    m = trimesh.load(path)
    if deg:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), [1, 0, 0], [XC, AY, AZ]))
    s = m.section(plane_origin=[XC, 0, 0], plane_normal=[1, 0, 0])
    return [s.vertices[e.points][:, 1:] for e in s.entities] if s is not None else []

cases = [("A", 30, "A click detent: at 30°"), ("A", 37.5, "A: between stops (spring drawn unbent:\nthe overlap, up to 0.57 mm, is how far the bridge gives)"),
         ("B", 60, "B ratchet: at 60°"), ("B", 75, "B: rising (pawl drawn unbent: the rim ramps it\ndown up to 1.0 mm; lowering meets the square face)")]
fig, axs = plt.subplots(2, 2, figsize=(13, 11))
for ax, (opt, deg, title) in zip(axs.flat, cases):
    for path, fc, ec, d in ((ROOT / "build" / opt / "connector.stl", "#8fb0d8", "#3d5f8a", 0),
                            (ROOT / "build" / opt / "moving.stl", "#efe9dc", "#6b6152", deg)):
        for loop in cut(path, d):
            if len(loop) < 4 or abs((loop[:-1, 0] * loop[1:, 1] - loop[1:, 0] * loop[:-1, 1]).sum()) / 2 < 0.05:
                continue
            ax.add_patch(MP(loop, closed=True, fc=fc, ec=ec, lw=0.8, alpha=0.9))
    ax.plot([AY], [AZ], "k+", ms=10)
    ax.set_xlim(AY - 16, AY + 14); ax.set_ylim(AZ - 10, AZ + 9); ax.set_aspect("equal")
    ax.set_title(title, fontsize=12); ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm)"); ax.grid(alpha=0.25)
fig.suptitle("Section through the middle of the hinge (x = %.2f)" % XC, fontsize=13)
plt.tight_layout(); (ROOT / "renders").mkdir(exist_ok=True); plt.savefig(ROOT / "renders" / "sections.png", dpi=90)
