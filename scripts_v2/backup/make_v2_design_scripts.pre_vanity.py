# Generates build_room2_ensuite_v2.py and build_hall_designs_v2.py from the V1.x scripts (run with plain python3).
import os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def patcher(src):
    s = [open(os.path.join(B, src)).read()]
    def rp(a, b, n=1):
        c = s[0].count(a)
        assert c == n, (c, n, a[:90])
        s[0] = s[0].replace(a, b)
    return s, rp

# ============================================================ Room 2 en-suite on V2
s, rp = patcher("build_room2_ensuite.py")
rp("# MyFlat V1.2 - Room 2 en-suite", "# MyFlat V2 - Room 2 en-suite on the site-measured layout (14 Nov 2026). Numbers below stay in the V1 frame;\n"
   "# SX moves everything 2'8\" east (V2 kitchen is 9'8\"). The cross wall is now REAL architecture (WALL_INT_R2_TUB,\n"
   "# 191 cm from the north wall, doorway at its west end), so this script only adds the door, finishes and fittings.\n# Was: MyFlat V1.2 - Room 2 en-suite")
rp("FT = 0.3048; IN = 1 / 12; H = 10.0", "FT = 0.3048; IN = 1 / 12; H = 10.0\nSX = 2 + 8 * IN                  # V2 east shift")
rp("YPN, YPS = -(4 + 11 * IN), -(5 + 4 * IN)   # partition north / south face", "YPN = -191 / 30.48; YPS = YPN - 5 * IN     # cross wall north / south face (measured 191 cm)")
rp("DX0, DX1 = 26.0, 28.5            # door opening in partition", "DX0, DX1 = 25.25, 28.25          # doorway at the west end of the cross wall (3 ft)")
rp('o = bpy.data.objects.new("R2B_" + name, me); o.location = Vector([m(v) for v in loc])',
   'o = bpy.data.objects.new("R2B_" + name, me); o.location = Vector((m(loc[0] + SX), m(loc[1]), m(loc[2])))')
rp('o["status"] = "DESIGN"; o["version"] = "V1.2"', 'o["status"] = "DESIGN"; o["version"] = "V2"')
rp("lo = [bm.verts.new((m(x), m(y), m(z0))) for x, y in pts]; hi = [bm.verts.new((m(x), m(y), m(z1))) for x, y in pts]",
   "lo = [bm.verts.new((m(x + SX), m(y), m(z0))) for x, y in pts]; hi = [bm.verts.new((m(x + SX), m(y), m(z1))) for x, y in pts]")
rp("o.rotation_euler.y = math.pi / 2; o.location = Vector((m(x0), m(y), m(z))); return o",
   "o.rotation_euler.y = math.pi / 2; o.location = Vector((m(x0 + SX), m(y), m(z))); return o")
rp("cols.append((bm.verts.new((m(x), m(yy), m(z0))), bm.verts.new((m(x), m(yy), m(z1)))))",
   "cols.append((bm.verts.new((m(x + SX), m(yy), m(z0))), bm.verts.new((m(x + SX), m(yy), m(z1)))))")
rp("east = w.x / FT > 30\n                w.y = m(YPS); w.x = m(xE(YPS) if east else XW); v.co = inv @ w",
   "east = w.x / FT > 30 + SX\n                w.y = m(YPS); w.x = m((xE(YPS) if east else XW) + SX); v.co = inv @ w")
rp("""f["basis"] = "V1.2: trimmed to the en-suite partition (north 5'4\\" is now the tub room)\"""",
   """f["basis"] = "V2: trimmed to the cross wall (north 6'3\\" is the bath + tub side)\"""")
rp('''    boxes("PARTITION_WALL", [(XW, DX0, YPS, YPN, 0, H), (DX1, xE(YPS) + 0.2, YPS, YPN, 0, H), (DX0, DX1, YPS, YPN, 7.0, H)],
          M["wall"], "walls", W["spec"], props={"subtype": "internal"})''',
   '''    boxes("DOOR_HEAD_WALL", [(DX0, DX1, YPS, YPN, 7.0, H)], M["wall"], "walls", "lintel + wall above the bathroom door", props={"subtype": "internal"})
    boxes("JAMB_INFILL", [(XW - 5 * IN, XW, -7.083, YPN, 0, H)], M["wall"], "walls",
          "10 inch brick infill at the south end of Bath 2's open side, so the bathroom is closed off from the bedroom", props={"subtype": "internal"})''')
rp("px, py = DX1 - 0.25, -5.06 ", "px, py = DX1 - 0.25, YPN - 0.143 ")
rp('    box("TILE_N_1", XW, 29.0, -TILE, 0, 0, DADO, M["tile"], "finishes", T)\n    box("TILE_N_2", 29.0, 33.08, -TILE, 0, 0, 3.0, M["tile"], "finishes", T + " (below W4)")\n    box("TILE_N_TUB", 33.08,',
   '    box("TILE_N_1", XW, 29.14, -TILE, 0, 0, DADO, M["tile"], "finishes", T)\n    box("TILE_N_2", 29.14, 33.3, -TILE, 0, 0, 3.0, M["tile"], "finishes", T + " (below W4)")\n    box("TILE_N_TUB", 33.3,')
rp('    box("TILE_W_1", XW, XW + TILE, -1.75, 0, 0, DADO, M["tile"], "finishes", T)\n    box("TILE_W_2", XW, XW + TILE, YPN, -4.25, 0, DADO, M["tile"], "finishes", T)\n    box("TILE_S_1", XW, DX0, YPN, YPN + TILE, 0, DADO, M["tile"], "finishes", T)\n',
   '    box("TILE_W_1", XW, XW + TILE, -2.2, 0, 0, DADO, M["tile"], "finishes", T)\n')
rp('COL["version"] = "V1.2"; COL["note"] = "Room 2 en-suite: tub room + Bath 2, one door into Room 2"',
   'COL["version"] = "V2"; COL["note"] = "Room 2 en-suite on the site-measured layout: tub side + Bath 2 behind the real cross wall"')
rp('"WPC flush door 2\' leaf, 30 mm, matt laminate; privacy lock; opens INTO the bathroom"', '"WPC flush door 2\'6\\" leaf, 30 mm, matt laminate; privacy lock; opens INTO the bathroom"')
rp('"WPC door frame 2\'6\\" x 7\' (waterproof, termite-proof)"', '"WPC door frame 3\' x 7\' (waterproof, termite-proof)"')
rp('box("VANITY_CABINET", VX0, VX1, VY0, VY0 + 1.55, 1.15, 2.62,', 'box("VANITY_CABINET", VX0, VX1, VY0, VY0 + 1.55, 0.85, 2.28,')
rp('box("VANITY_TOP", VX0, VX1, VY0, VY0 + 1.6, 2.62, 2.72,', 'box("VANITY_TOP", VX0, VX1, VY0, VY0 + 1.6, 2.28, 2.38,')
rp('cyl("VANITY_BASIN", 30.15, VY0 + 0.85, 0.5, 2.72, 3.05,', 'cyl("VANITY_BASIN", 30.15, VY0 + 0.85, 0.5, 2.38, 2.8,')
rp('cyl("VANITY_TAP", 30.15, VY0 + 0.18, 0.05, 2.72, 3.55,', 'cyl("VANITY_TAP", 30.15, VY0 + 0.18, 0.05, 2.38, 3.45,')
rp('box("VANITY_MIRROR", 29.05, 31.25, VY0, VY0 + 0.04, 3.7, 6.2,', 'box("VANITY_MIRROR", 29.05, 31.25, VY0, VY0 + 0.04, 3.35, 6.15,')
rp('box("MIRROR_LIGHT", 29.3, 31.0, VY0, VY0 + 0.12, 6.3, 6.4,', 'box("MIRROR_LIGHT", 29.3, 31.0, VY0, VY0 + 0.12, 6.25, 6.35,')
rp('hcyl("CURTAIN_ROD", TX0, TX1, TY0 - 0.02, 6.95,', 'hcyl("CURTAIN_ROD", TX0, TX1, TY0 + 0.25, 6.45,')
rp('curtain("SHOWER_CURTAIN", 36.2, 37.4, TY0 - 0.02, 1.9, 6.9,', 'curtain("SHOWER_CURTAIN", 36.2, 37.4, TY0 + 0.25, 1.95, 6.4,')
open(os.path.join(B, "build_room2_ensuite_v2.py"), "w").write(s[0])

# ============================================================ hall designs on V2
s, rp = patcher("build_hall_designs.py")
rp("# MyFlat V1.3 - hall designs", "# MyFlat V2 - hall designs on the site-measured layout (14 Nov 2026).\n"
   "# Hall: x 6.5 (west wall) .. 27.5, pillars x 18.67-19.92 at y -19.9 and -36.0, main door on the west wall y -24.61..-21.07,\n"
   "# west-wall window y -41.2..-37.1, hall arch x 13.0-18.67. The TV wall moved to the west wall SOUTH of the main door.\n# Was: MyFlat V1.3 - hall designs")
rp('''    runs = [(3.83, 3.83 + T, -45.25, -31.75), (3.83, 3.83 + T, -28.75, -15.25), (3.83, 20.42, -45.25, -45.25 + T), (3.83, 13.0, -15.25 - T, -15.25),
            (13.0, 14.9, -13.25 - T, -13.25), (20.57, 24.83, -13.25 - T, -13.25),
            (24.83 - T, 24.83, -19.25, -13.25), (24.83 - T, 24.83, -24.0, -22.25)]''',
   '''    runs = [(X, X + T, -45.25, MAIN_Y0), (X, X + T, MAIN_Y1, -15.25), (X, B1X, -45.25, -45.25 + T), (X, 13.0, -15.25 - T, -15.25),
            (PX1, XE_, -13.25 - T, -13.25),
            (XE_ - T, XE_, R2D_Y1, -13.25), (XE_ - T, XE_, -24.0, R2D_Y0)]''')
rp("def ceiling_fan(z_hub=8.6, cx=12.0, cy=-30.6):", "def ceiling_fan(z_hub=8.6, cx=12.67, cy=-30.1):")
rp("ceiling_fan(cx=10.0, cy=-25.2)", "ceiling_fan()", 6)
rp('''    """W7 on the south wall (x 7.93 .. 11.93): ceiling-high rod, two pleated panels stacked open at the sides"""
    Yw = -45.25; zt = 8.3
    cyl("CURTAIN_ROD_L", 6.6, Yw + 0.35,''', '''    """W7 on the south wall (x 10.6 .. 14.6): ceiling-high rod, two pleated panels stacked open at the sides"""
    Yw = -45.25; zt = 8.3
    cyl("CURTAIN_ROD_L", 9.27, Yw + 0.35,''')
rp('box("CURTAIN_ROD", 6.5, 13.4, Yw + 0.32', 'box("CURTAIN_ROD", 9.17, 16.07, Yw + 0.32')
rp('for side, (a, b) in (("L", (6.7, 8.2)), ("R", (11.7, 13.2))):', 'for side, (a, b) in (("L", (9.37, 10.87)), ("R", (14.37, 15.87))):')
rp("MAIN_Y0, MAIN_Y1 = -31.75, -28.75          # 3 ft opening, middle of the hall's west wall (wall x 3.08 .. 3.83)",
   "MAIN_Y0, MAIN_Y1 = -24.61, -21.07          # V2: 108 cm main door (architecture), 25 cm south of Pillar 2's line\n"
   "B1X, XE_ = 23.08, 27.5                     # Bath 1 west wall outer face / hall east wall\n"
   "PX0, PX1 = 18.67, 19.92                    # pillar line (15 in E-W)\n"
   "PIL_Y = ((-20.25, -19.5), (-36.33, -35.58))  # Pillar 2, Pillar 1 (9 in N-S)\n"
   "R2D_Y0, R2D_Y1 = -23.25, -20.25            # Room 2 hall door\n"
   "def main_door_v2():\n"
   "    \"\"\"V2: the main door is already architecture (DOOR_MAIN). Give its leaf a teak finish and make it openable.\"\"\"\n"
   "    l = bpy.data.objects.get('DOOR_MAIN_LEAF')\n"
   "    if not l: return None\n"
   "    teak = bpy.data.materials.get('Door_Main_Teak') or bpy.data.materials.new('Door_Main_Teak')\n"
   "    teak.use_nodes = True; b = teak.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.36, 0.22, 0.12, 1); b.inputs['Roughness'].default_value = 0.45\n"
   "    teak.diffuse_color = (0.36, 0.22, 0.12, 1)\n"
   "    if l.data.users > 1: l.data = l.data.copy()\n"
   "    l.data.materials.clear(); l.data.materials.append(teak)\n"
   "    l['spec'] = \"solid teak main door 3'6\\\" x 7', opens into the hall\"; l['label'] = 'Main door'\n"
   "    return l.name")
rp("TV_Y0, TV_Y1, TV_YC = -24.75, -16.75, -20.75      # 8 ft panel centred under the north E-W beam\nX = 3.83",
   "X = 6.5\nTV_Y0, TV_Y1, TV_YC = -34.1, -26.1, -30.1        # 8 ft panel on the west wall between the main door and Pillar 1's wall column")
# X must exist before skirting() is called - it is a module global, fine. MAIN_* now defined before TV_* too.
rp('sbox("TV_CONSOLE", X + depth, 5.4, TV_YC', 'sbox("TV_CONSOLE", X + depth, X + 1.57, TV_YC')
rp('boxes("TV_CONSOLE_GROOVES", [(5.4, 5.42, TV_YC', 'boxes("TV_CONSOLE_GROOVES", [(X + 1.57, X + 1.59, TV_YC')
rp("def living_and_dining(fabric, wood, chair, sofa_len=7.0, seats6=True, rug=True, table=(7.5, 10.0), decor=True):",
   "def living_and_dining(fabric, wood, chair, sofa_len=7.0, seats6=True, rug=True, table=(10.85, 12.8), decor=True):")
rp('sofa("SOFA", 11.8, y0, y1,', 'sofa("SOFA", X + 7.47, y0, y1,')
rp('box("RUG", 6.0, 14.3,', 'box("RUG", 8.17, 16.47,'); rp('box("RUG_FIELD", 6.4, 13.9,', 'box("RUG_FIELD", 8.57, 16.07,')
rp('dining("DINING", 8.0, 11.0, -42.0, -36.0, (-37.0, -39.0, -41.0),', 'dining("DINING", 10.67, 13.67, -43.0, -37.0, (-38.0, -40.0, -42.0),')
rp('dining("DINING", 8.25, 10.75, -40.0, -36.0, (-37.1, -38.9),', 'dining("DINING", 10.92, 13.42, -41.5, -37.5, (-38.6, -40.4),')
rp('plant("PLANT_DINING", 5.0, -43.8,', 'plant("PLANT_DINING", 7.67, -43.8,')
rp("cy_ = -39.0 if seats6 else -38.0", "cy_ = -40.0 if seats6 else -39.5")
rp('pendant(f"PENDANT_{i+1}", 9.5, cy_ + dy,', 'pendant(f"PENDANT_{i+1}", 12.17, cy_ + dy,')
rp("floor_lamp(13.3, -16.35, metal,", "floor_lamp(X + 8.97, y1 + 0.9, metal,")
rp("side_table(13.3, -25.05, wood, metal)", "side_table(X + 8.97, y0 - 0.8, wood, metal)")
rp('plant("PLANT_TV", 4.75, -26.1,', 'plant("PLANT_TV", X + 0.92, TV_Y0 - 0.75,')
rp("wall_art(6.4, 9.4, 4.3, 6.7,", "wall_art(8.2, 11.2, 4.3, 6.7,")
rp('''    box("SHOE_CABINET", X, X + 1.2, -36.0, -32.4, 0.4, 3.0,''', '''    box("SHOE_CABINET", X, X + 1.2, -19.3, -15.7, 0.4, 3.0,''')
rp('box("ENTRY_MIRROR", X, X + 0.05, -35.6, -32.8,', 'box("ENTRY_MIRROR", X, X + 0.05, -18.9, -16.1,')
rp('''    for (y0, y1) in ((-21.38, -20.13), (-30.37, -29.12)):
        for xc in (20.19, 20.94):''', '''    for (y0, y1) in PIL_Y:
        for xc in (PX0, PX1):''')
rp("for x in (8.0, 15.5) for y in (-17.5, -24.5, -33.5, -40.5)])", "for x in (10.5, 15.8) for y in (-17.5, -25.0, -32.5, -40.5)])")
rp('box("SHOE_RACK", X, X + 1.0, -35.0, -32.4,', 'box("SHOE_RACK", X, X + 1.0, -18.3, -15.7,')
rp("table=(8.0, 10.0), decor=False)", "table=(11.1, 12.8), decor=False)")
rp("[(4.5, 7.5, -45.25, -45.13), (13.5, 17.5, -45.25, -45.13), (X, X + 0.12, -42.0, -38.0)]", "[(7.17, 10.17, -45.25, -45.13), (16.17, 20.17, -45.25, -45.13), (X, X + 0.12, -33.0, -29.0)]")
rp('box("TV_CONSOLE_TOP", X + 0.04, 5.45,', 'box("TV_CONSOLE_TOP", X + 0.04, X + 1.62,')
rp('''[(3.83 + 1.0, 3.83 + 1.0 + W, -44.25, -16.25, 0, z), (20.42 - 1.5 - W, 20.42 - 1.5, -44.25, -16.25, 0, z),
                           (3.83 + 1.0, 20.42 - 1.5, -44.25, -44.25 + W, 0, z), (3.83 + 1.0, 20.42 - 1.5, -16.25 - W, -16.25, 0, z)]''',
   '''[(X + 1.0, X + 1.0 + W, -44.25, -16.25, 0, z), (PX0 - 1.0 - W, PX0 - 1.0, -44.25, -16.25, 0, z),
                           (X + 1.0, PX0 - 1.0, -44.25, -44.25 + W, 0, z), (X + 1.0, PX0 - 1.0, -16.25 - W, -16.25, 0, z)]''')
rp("    # 1. whole north part of the west wall panelled (door frame to Room 1 wall), TV in the middle\n    Y0, Y1, Z0, Z1 = -28.55, -15.3, 0.33, 8.75",
   "    # 1. west wall panelled from the main door frame to Pillar 1's wall column, TV in the middle\n    Y0, Y1, Z0, Z1 = -35.5, MAIN_Y0 - 0.15, 0.33, 8.75")
rp('"WPC fluted panelling, whole wall 13 ft x 8\'5\\", teak"', '"WPC fluted panelling, whole wall 11 ft x 8\'5\\", teak"')
rp('''    runs = [("W_SOUTH_OF_DOOR", (X, X + T, -45.25, -31.95), "x"), ("S_WALL", (3.83, 20.42, -45.25, -45.25 + T), "y"),
            ("R1_WALL", (3.83, 13.0, -15.25 - T, -15.25), "y"), ("PASSAGE_W", (13.0, 14.9, -13.25 - T, -13.25), "y"),
            ("PASSAGE_E", (20.57, 24.83, -13.25 - T, -13.25), "y"), ("EAST_N", (24.83 - T, 24.83, -19.25, -13.25), "x"), ("EAST_S", (24.83 - T, 24.83, -24.0, -22.25), "x")]''',
   '''    runs = [("W_WINDOW_WALL", (X, X + T, -45.25, -36.4), "x"), ("W_NORTH_OF_DOOR", (X, X + T, -19.45, -15.25), "x"), ("S_WALL", (X, B1X, -45.25, -45.25 + T), "y"),
            ("R1_WALL", (X, 13.0, -15.25 - T, -15.25), "y"),
            ("PASSAGE_E", (PX1, XE_, -13.25 - T, -13.25), "y"), ("EAST_N", (XE_ - T, XE_, R2D_Y1, -13.25), "x"), ("EAST_S", (XE_ - T, XE_, -24.0, R2D_Y0), "x")]''')
rp('''    for i, (y0, y1) in enumerate(((-21.38, -20.13), (-30.37, -29.12))):
        x0, x1, e = 20.19, 20.94, 0.05''', '''    for i, (y0, y1) in enumerate(PIL_Y):
        x0, x1, e = PX0, PX1, 0.05''')
rp("xa, xb, ya, yb, B = 3.83, 20.19, -45.25, -15.25, 2.0", "xa, xb, ya, yb, B = X, PX0, -45.25, -15.25, 2.0")
rp('wall_slab("ENTRY_DADO", -45.25, -31.95, 0.0, 3.5,', 'wall_slab("ENTRY_DADO", -19.45, -15.25, 0.0, 3.5,')
rp('box("ENTRY_DADO_TRIM", X, X + 0.08, -45.25, -31.95, 3.5, 3.56,', 'box("ENTRY_DADO_TRIM", X, X + 0.08, -19.45, -15.25, 3.5, 3.56,')
rp('on the entry wall only, tile adhesive', 'on the entry wall (north of the main door) only, tile adhesive')
rp("    door = add_main_door()", "    door = main_door_v2()")
rp('box("TV", X + depth, X + depth + 0.15, TV_YC - 2.15, TV_YC + 2.15, 2.9, 5.3, tv_mat,', 'box("TV", X + depth, X + depth + 0.15, TV_YC - 2.15, TV_YC + 2.15, 2.45, 4.85, tv_mat,')
rp('box("TV", X, X + 0.15, TV_YC - 2.15, TV_YC + 2.15, 2.9, 5.3, mat("TV_Black"', 'box("TV", X, X + 0.15, TV_YC - 2.15, TV_YC + 2.15, 2.45, 4.85, mat("TV_Black"')
rp('pendant(f"PENDANT_{i+1}", 12.17, cy_ + dy, 6.1,', 'pendant(f"PENDANT_{i+1}", 12.17, cy_ + dy, 5.5,')

t = s[0]
# skirting() and guards() use names defined later in the module: fine at call time.
open(os.path.join(B, "build_hall_designs_v2.py"), "w").write(t)
print("ok")
