import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from load import solids, ROOT
S = solids()
G = json.load(open(ROOT / "build" / "assembled_groups.json"))
n = len(G); cols = 9; rows = -(-n // cols)
fig = plt.figure(figsize=(cols * 2.6, rows * 2.6))
for gi, g in enumerate(G):
    s = S[g["items"][0][0]]
    V, F = [], []
    for fc in s.faces():
        try:
            vv, ff = fc.tessellate(0.5, 0.5)
        except Exception:
            continue
        b = len(V); V += [(p.X, p.Y, p.Z) for p in vv]; F += [(a + b, c + b, d + b) for a, c, d in ff]
    v, f = np.array(V), np.array(F)
    ax = fig.add_subplot(rows, cols, gi + 1, projection="3d")
    ax.add_collection3d(Poly3DCollection(v[f], facecolor="#9db8d6", edgecolor="#33475b", linewidths=0.05))
    c = (v.max(0) + v.min(0)) / 2; r = (v.max(0) - v.min(0)).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.axis("off"); ax.view_init(25, -60)
    d = g["sig"][1]
    ax.set_title(f"G{gi} x{len(g['items'])}  {d[2]}x{d[1]}x{d[0]}\n{(g['items'][0][2] or '')[:28]}", fontsize=7)
plt.tight_layout(); plt.savefig(ROOT / "build" / "contact.png", dpi=55)
