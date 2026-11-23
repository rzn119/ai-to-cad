"""The parts of the suitcase, from the assembled (exploded) suitcase in the STEP: group index (see
build/assembled_groups.json, largest first) -> code, Chinese / English name, material, make or buy.
Names marked (待确认) are my reading of the model and need the designer's confirmation."""
TBC = "待确认 TBC"
ALLOY = "铝镁合金 Al-Mg ALLOY"
LEATHER = "皮革 LEATHER"

# code, groups, CN, EN, material
MAKE = [
    ("SC-101", [0], "行李箱外壳", "SUITCASE SHELL", TBC),
    ("SC-102", [1], "硬质内底板", "HARD INNER BASE PANEL", TBC),
    ("SC-103", [17], "外壳封边板", "SHELL EDGE PLATE", TBC),
    ("SC-201", [4], "行李箱框(带滑轨)", "FRAME WITH TRACK", ALLOY),
    ("SC-202", [5], "行李箱框", "FRAME", ALLOY),
    ("SC-203", [9], "框横档 A", "FRAME CROSS BAR A", ALLOY),
    ("SC-204", [10], "框横档 B", "FRAME CROSS BAR B", ALLOY),
    ("SC-205", [2], "折叠面板框", "FOLDING PANEL FRAME", ALLOY),
    ("SC-206", [7], "折叠框横档", "FOLDING FRAME CROSS BAR", ALLOY),
    ("SC-207", [11], "折叠框侧档 右", "FOLDING FRAME SIDE BAR R", ALLOY),
    ("SC-208", [12], "折叠框侧档 左", "FOLDING FRAME SIDE BAR L", ALLOY),
    ("SC-209", [6], "拉杆上横把", "HANDLE TOP BAR", ALLOY),
    ("SC-210", [8], "拉杆下横档", "HANDLE LOWER BAR", ALLOY),
    ("SC-211", [13], "拉杆管", "HANDLE TUBE", ALLOY),
    ("SC-212", [14], "顶部横档", "TOP RAIL", TBC),
    ("SC-213", [15], "内侧档 左", "INNER SIDE RAIL L", TBC),
    ("SC-214", [16], "内侧档 右", "INNER SIDE RAIL R", TBC),
    ("SC-215", [44], "滑轨块 34.8", "TRACK BLOCK 34.8", TBC),
    ("SC-216", [49], "滑轨块 18.1", "TRACK BLOCK 18.1", TBC),
    ("SC-217", [50], "滑轨块 17.9", "TRACK BLOCK 17.9", TBC),
    ("SC-218", [51], "滑轨块 13.1", "TRACK BLOCK 13.1", TBC),
    ("SC-219", [59], "滑轨挡块 A", "TRACK STOP A", TBC),
    ("SC-220", [60], "滑轨挡块 B", "TRACK STOP B", TBC),
    ("SC-221", [32], "框固定条 93", "FRAME FIXING STRIP 93", TBC),
    ("SC-222", [37], "框固定条 71.3", "FRAME FIXING STRIP 71.3", TBC),
    ("SC-223", [38], "框固定条 68.2", "FRAME FIXING STRIP 68.2", TBC),
    ("SC-224", [68], "固定片 A", "FIXING TAB A", TBC),
    ("SC-225", [70], "固定片 B", "FIXING TAB B", TBC),
    ("SC-231", [39], "框锁扣 A", "FRAME LATCH A", TBC),
    ("SC-232", [40], "框锁扣 B", "FRAME LATCH B", TBC),
    ("SC-233", [42], "框锁扣 C", "FRAME LATCH C", TBC),
    ("SC-234", [43], "框锁扣 D", "FRAME LATCH D", TBC),
    ("SC-235", [45], "连接杆", "JOINING ROD", TBC),
    ("SC-236", [63], "框连接片", "FRAME CONNECTOR PLATE", TBC),
    ("SC-301", [3], "皮革面板", "LEATHER PANEL", LEATHER),
    ("SC-302", [18], "面板边条 6", "PANEL EDGE STRIP 6", TBC),
    ("SC-303", [21], "面板边条 3", "PANEL EDGE STRIP 3", TBC),
    ("SC-304", [28, 29], "皮革窄条", "LEATHER NARROW STRIP", LEATHER),
    ("SC-401", [22], "轮座 左", "WHEEL HOUSING L", TBC),
    ("SC-402", [23], "轮座 右", "WHEEL HOUSING R", TBC),
    ("SC-403", [27], "把手底座", "HANDLE BASE", TBC),
]
# bought parts (外购件): code, groups, CN, EN, qty per suitcase
BUY = [
    ("BP-01", [19, 20, 25, 26, 30, 31, 33, 34, 35, 36], "万向轮", "SWIVEL CASTER", 4),
    ("BP-02", [24], "把手", "CARRY HANDLE", 2),
    ("BP-03", [46, 47, 48, 52, 53, 54, 56, 57, 64, 66, 67, 69], "阻尼铰链", "DAMPING HINGE", 4),
    ("BP-04", [41, 55, 58, 61, 62], "密码锁", "COMBINATION LOCK", 1),
]
SKIP = {65: "0.2 mm tolerance body (a modelling cutter, not a part)"}
