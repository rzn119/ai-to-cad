"""Two short floor pieces with one bayonet T-lock, for the interactive demo.
Local frame: the seam at x = 0, the locked tab centred at y = 0, the floor's mid-plane at z = 0.
The right piece starts 16 mm along +y (window over the tab), pushes in along -x, slides 16 mm along -y."""
import build123d as bd
from cad import model

import v3_joints as v

J = next(j for j in v.SPEC["floor"] if j["kind"] == "bayonet" and j["on"] == "P7-F2-L")
TO_LOCAL = bd.Pos(-v.XC, -J["y"], -v.ZF)
Y0, Y1 = J["y"] - 42, J["y"] + 18
FZ0, FZ1 = -177.24, -171.55


@model
def demo_left():
    block = v.box(v.XC - 28, v.XC, Y0, Y1, FZ0, FZ1)
    block.label, block.color = "left_floor", "#efe9dc"
    tab = v.bayonet_tab(J) & v.box(v.XC - 1, v.XC + 10, Y0, Y1, FZ0, FZ1)
    tab.label, tab.color = "t_tab", "#c0392b"
    return bd.Compound(children=[TO_LOCAL * block, TO_LOCAL * tab], label="left_piece")


@model
def demo_right():
    block = v.box(v.XC, v.XC + 28, Y0, Y1, FZ0, FZ1) - v.bayonet_slot(J)
    block.label, block.color = "right_floor", "#8fa3b8"
    return bd.Compound(children=[TO_LOCAL * block], label="right_piece")


if __name__ == "__main__":
    demo_left()
    demo_right()
