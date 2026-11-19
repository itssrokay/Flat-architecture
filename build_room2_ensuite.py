# MyFlat V1.2 - Room 2 en-suite: tub room + Bath 2 joined, ONE door into Room 2 (27 Oct 2026).
# Run with MyFlat_V1_1_Room1_Interiors.blend open, then save as MyFlat_V1_2_Room2_Ensuite.blend:
#   exec(open(".../build_room2_ensuite.py").read()); run()
# Re-running is safe: it rebuilds collection 19_ROOM2_ENSUITE and re-applies the edits below.
#
# Layout (feet; Room 2 frame: x=25.25 west inner face, y=0 north inner face, east wall tapers 37.833 -> 35.75):
#   * new 5" partition across Room 2, north face 4'11" from the north wall (south face 5'4").
#     It cannot go deeper: east window W5 starts 5'5" from the north wall.
#   * tub room (12'7"->12'2" x 4'11"): 5' x 2'6" built-in tub in the NE corner on a 4" plinth,
#     wall-hung vanity + mirror on the partition, geyser, exhaust fan in the existing high vent,
#     W4 glass frosted, tiles to 7'.
#   * Bath 2 (existing WC room, 4'5" x 7'1") keeps its doorway; the leaf is removed so WC and tub room
#     are one bathroom. Bath 2 gets a WC and a small basin.
#   * the only way in/out is the new 2'6" door in the partition (opens into the bathroom).
#   * FLOOR_R2 is trimmed to the new partition; the tub room gets its own floor (room = "Room 2 Bath").
import bpy, bmesh, math
from mathutils import Vector

FT = 0.3048; IN = 1 / 12; H = 10.0
XW = 25.25                       # Room 2 west inner face
YPN, YPS = -(4 + 11 * IN), -(5 + 4 * IN)   # partition north / south face
DX0, DX1 = 26.0, 28.5            # door opening in partition
TILE = 0.04; DADO = 7.0
COLL_NAME = "19_ROOM2_ENSUITE"
def m(v): return v * FT
def xE(y): return 37.833 + (35.75 - 37.833) * (-y / 23.583)   # east wall inner face at y

COL = None; MATS = {}
def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0, emit=0.0):
    key = "R2B_" + name
    if key in MATS: return MATS[key]
    mt = bpy.data.materials.get(key) or bpy.data.materials.new(key); mt.use_nodes = True
    b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal; b.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        try: mt.surface_render_method = 'BLENDED'
        except Exception: pass
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    mt.diffuse_color = (*rgb, alpha); MATS[key] = mt; return mt

def _obj(name, me, mt, cat, spec, loc=(0, 0, 0)):
    o = bpy.data.objects.new("R2B_" + name, me); o.location = Vector([m(v) for v in loc])
    if mt: o.data.materials.append(mt)
    COL.objects.link(o)
    o["design_category"] = cat; o["status"] = "DESIGN"; o["version"] = "V1.2"
    if spec: o["spec"] = spec
    return o

def _bm_box(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new((m(a), m(b), m(c))) for a, b, c in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])

def boxes(name, bxs, mt, cat, spec="", pivot=None, props=None):
    """boxes given in WORLD feet; object origin at pivot (x, y) or at the first box's min corner"""
    px, py = pivot if pivot else (bxs[0][0], bxs[0][2])
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for (a, b, c, d, e, f) in bxs: _bm_box(bm, a - px, b - px, c - py, d - py, e, f)
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (px, py, 0))
    for k, v in (props or {}).items(): o[k] = v
    return o
def box(name, x0, x1, y0, y1, z0, z1, mt, cat, spec="", props=None):
    return boxes(name, [(x0, x1, y0, y1, z0, z1)], mt, cat, spec, ((x0 + x1) / 2, (y0 + y1) / 2), props)

def prism(name, pts, z0, z1, mt, cat, spec="", props=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    lo = [bm.verts.new((m(x), m(y), m(z0))) for x, y in pts]; hi = [bm.verts.new((m(x), m(y), m(z1))) for x, y in pts]
    bm.faces.new(list(reversed(lo))); bm.faces.new(hi)
    for i in range(len(pts)): j = (i + 1) % len(pts); bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)      # outward normals whatever the point order (viewer is one-sided)
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec)
    for k, v in (props or {}).items(): o[k] = v
    return o

def cyl(name, cx, cy, r, z0, z1, mt, cat, spec="", n=24, sy=1.0, props=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=m(r), radius2=m(r), depth=m(z1 - z0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, m(z1 - z0) / 2))
    for v in bm.verts: v.co.y *= sy
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (cx, cy, z0))
    for k, v in (props or {}).items(): o[k] = v
    return o

def hcyl(name, x0, x1, y, z, r, mt, cat, spec=""):   # horizontal rod along X
    o = cyl(name, 0, 0, r, 0, x1 - x0, mt, cat, spec, 12)
    o.rotation_euler.y = math.pi / 2; o.location = Vector((m(x0), m(y), m(z))); return o

def curtain(name, x0, x1, y, z0, z1, mt, cat, spec="", amp=0.09, waves=6):
    n = 40; me = bpy.data.meshes.new(name); bm = bmesh.new(); cols = []
    for i in range(n + 1):
        t = i / n; x = x0 + (x1 - x0) * t; yy = y + amp * math.sin(t * waves * 2 * math.pi)
        cols.append((bm.verts.new((m(x), m(yy), m(z0))), bm.verts.new((m(x), m(yy), m(z1)))))
    for i in range(n): bm.faces.new((cols[i][0], cols[i+1][0], cols[i+1][1], cols[i][1]))
    bm.to_mesh(me); bm.free(); return _obj(name, me, mt, cat, spec)

# ---------------------------------------------------------------- architecture edits
def edit_architecture():
    notes = []
    # 1. Room 2 floor ends at the partition
    f = bpy.data.objects.get("FLOOR_R2")
    if f:
        mw, inv = f.matrix_world, f.matrix_world.inverted()
        for v in f.data.vertices:
            w = mw @ v.co
            if w.y / FT > YPS + 0.01:                       # north edge -> partition south face
                east = w.x / FT > 30
                w.y = m(YPS); w.x = m(xE(YPS) if east else XW); v.co = inv @ w
        f.data.update(); f["basis"] = "V1.2: trimmed to the en-suite partition (north 5'4\" is now the tub room)"
        notes.append("FLOOR_R2 trimmed")
    # 2. Bath 2 doorway becomes an open link (leaf removed)
    leaf = bpy.data.objects.get("DOOR_B2_LEAF")
    if leaf: bpy.data.objects.remove(leaf, do_unlink=True); notes.append("DOOR_B2_LEAF removed")
    b2 = bpy.data.objects.get("DOOR_B2")
    if b2: b2["basis"] = "V1.2: open doorway between Bath 2 (WC) and the tub room - no leaf"
    # 3. W4 is now a bathroom window: frosted glass (own mesh copy so other windows keep clear glass)
    g = bpy.data.objects.get("WINDOW_W4_GLASS")
    if g:
        if g.data.users > 1: g.data = g.data.copy()
        fm = mat("Glass_Frosted", (0.88, 0.9, 0.92), 0.85, 0, 0.82)
        if g.material_slots: g.material_slots[0].material = fm
        else: g.data.materials.append(fm)
        g["spec"] = "Frosted film / obscure glass - W4 now lights the tub room"; notes.append("W4 frosted")
    # 4. labels
    lb = bpy.data.objects.get("LBL_R2")
    if lb and lb.type == 'FONT': lb.data.body = "ROOM 2\n12'1\"-10'6\" x 18'3\""
    return notes

# ---------------------------------------------------------------- en-suite
def build():
    M = {
        "wall": bpy.data.materials.get("Plaster_White") or mat("Plaster", (0.93, 0.92, 0.9), 0.9),
        "wood": bpy.data.materials.get("Frame_Wood") or mat("Frame_Wood", (0.55, 0.4, 0.26), 0.6),
        "leaf": mat("Door_WPC", (0.86, 0.83, 0.78), 0.5),
        "thr": bpy.data.materials.get("Threshold_Stone") or mat("Granite", (0.25, 0.25, 0.27), 0.3),
        "floor": mat("Floor_AntiSkid", (0.72, 0.71, 0.68), 0.8),
        "tile": mat("Wall_Tile_Matte", (0.86, 0.85, 0.82), 0.45),
        "accent": mat("Wall_Tile_Sage", (0.62, 0.69, 0.62), 0.4),
        "acrylic": mat("Acrylic_White", (0.97, 0.97, 0.96), 0.12),
        "ceramic": mat("Ceramic_White", (0.96, 0.96, 0.95), 0.15),
        "chrome": mat("Chrome", (0.85, 0.86, 0.88), 0.12, 1.0),
        "vanity": mat("Vanity_Oak", (0.62, 0.48, 0.33), 0.55),
        "quartz": mat("Quartz_Top", (0.9, 0.89, 0.86), 0.25),
        "mirror": mat("Mirror", (0.8, 0.85, 0.88), 0.03, 1.0),
        "led": mat("LED_Warm", (1.0, 0.86, 0.66), 0.4, 0, 1, 4.0),
        "fitting": mat("Fitting_White", (0.95, 0.95, 0.95), 0.4),
        "curtain": mat("Shower_Curtain", (0.9, 0.93, 0.92), 0.7, 0, 0.88),
        "mat": mat("Bath_Mat", (0.45, 0.55, 0.5), 0.95),
        "towel": mat("Towel", (0.93, 0.9, 0.84), 0.95),
        "plant": mat("Foliage", (0.22, 0.42, 0.2), 0.8),
        "pot": mat("Pot", (0.82, 0.8, 0.76), 0.6),
    }
    # --- partition wall + door (walls/doors categories so the viewer collides with them)
    W = dict(spec="5\" brick/AAC partition, plastered both sides, to slab; waterproofed 1' up on the bath side")
    boxes("PARTITION_WALL", [(XW, DX0, YPS, YPN, 0, H), (DX1, xE(YPS) + 0.2, YPS, YPN, 0, H), (DX0, DX1, YPS, YPN, 7.0, H)],
          M["wall"], "walls", W["spec"], props={"subtype": "internal"})
    boxes("DOOR_FRAME", [(DX0, DX0 + 0.25, YPS, YPN, 0, 7.0), (DX1 - 0.25, DX1, YPS, YPN, 0, 7.0), (DX0, DX1, YPS, YPN, 6.75, 7.0)],
          M["wood"], "doors", "WPC door frame 2'6\" x 7' (waterproof, termite-proof)")
    px, py = DX1 - 0.25, -5.06                        # hinge on the east jamb, bath side
    boxes("DOOR_LEAF", [(DX0 + 0.25, px, py - 0.125, py, 0.04, 6.73),
                        (px - 1.85, px - 1.65, py - 0.3, py - 0.125, 3.3, 3.42), (px - 1.85, px - 1.65, py, py + 0.17, 3.3, 3.42)],
          M["leaf"], "doors", "WPC flush door 2' leaf, 30 mm, matt laminate; privacy lock; opens INTO the bathroom",
          pivot=(px, py), props={"interact": "hinge", "open_deg": -95.0, "group": "R2B_BATH_DOOR", "label": "Bathroom door"})
    box("THRESHOLD", DX0, DX1, YPS, YPN, -0.25, 0.042, M["thr"], "floors", "granite threshold; bath floor is 1/2\" lower", {"subtype": "threshold"})
    # --- tub-room floor (own room for the viewer)
    prism("FLOOR", [(XW, 0), (37.833, 0), (xE(YPS), YPS), (XW, YPS)], -0.25, -0.042, M["floor"], "floors",
          "anti-skid matt vitrified 600x600, laid to fall towards the floor trap by the tub; PU waterproofing below",
          {"room": "Room 2 Bath", "status": "DESIGN"})
    # --- wall tiles to 7' (dado), paint above
    T = "matt ceramic wall tile 300x600 to 7'; washable paint above"
    box("TILE_N_1", XW, 29.0, -TILE, 0, 0, DADO, M["tile"], "finishes", T)
    box("TILE_N_2", 29.0, 33.08, -TILE, 0, 0, 3.0, M["tile"], "finishes", T + " (below W4)")
    box("TILE_N_TUB", 33.08, xE(-TILE) - 0.01, -TILE, 0, 0, DADO, M["accent"], "finishes", "sage feature tile behind the tub")
    box("TILE_W_1", XW, XW + TILE, -1.75, 0, 0, DADO, M["tile"], "finishes", T)
    box("TILE_W_2", XW, XW + TILE, YPN, -4.25, 0, DADO, M["tile"], "finishes", T)
    box("TILE_S_1", XW, DX0, YPN, YPN + TILE, 0, DADO, M["tile"], "finishes", T)
    box("TILE_S_2", DX1, xE(YPN) - 0.01, YPN, YPN + TILE, 0, DADO, M["tile"], "finishes", T)
    prism("TILE_E", [(xE(0), 0), (xE(YPN), YPN), (xE(YPN) - TILE, YPN), (xE(0) - TILE, 0)], 0, DADO, M["accent"], "finishes", "sage feature tile (tub end)")
    # --- bathtub: 5' x 2'6" acrylic drop-in on a 4" masonry plinth, tiled apron
    TX0, TX1, TY0, TY1 = 32.5, 37.45, -2.54, -TILE
    boxes("TUB_APRON", [(TX0, TX1, TY0, TY0 + 0.16, 0, 1.75), (TX0, TX0 + 0.16, TY0 + 0.16, TY1, 0, 1.75)],
          M["accent"], "sanitaryware", "tiled masonry apron with a removable service panel; 4\" plinth for the waste fall")
    bx0, bx1, by0, by1 = TX0 + 0.4, TX1 - 0.4, TY0 + 0.38, TY1 - 0.38
    boxes("BATHTUB", [(TX0, TX1, TY0, by0, 1.72, 1.84), (TX0, TX1, by1, TY1, 1.72, 1.84),
                      (TX0, bx0, by0, by1, 1.72, 1.84), (bx1, TX1, by0, by1, 1.72, 1.84),
                      (bx0, bx1, by0, by1, 0.55, 0.62),
                      (bx0, bx1, by0, by0 + 0.05, 0.62, 1.72), (bx0, bx1, by1 - 0.05, by1, 0.62, 1.72),
                      (bx0, bx0 + 0.05, by0, by1, 0.62, 1.72), (bx1 - 0.05, bx1, by0, by1, 0.62, 1.72)],
          M["acrylic"], "sanitaryware", "1500 x 750 mm acrylic soaking tub (drop-in), ~180 L; pop-up waste to Bath 2 stack")
    box("TUB_SPOUT", 34.75, 35.15, -0.6, -TILE, 2.15, 2.3, M["chrome"], "sanitaryware", "wall-mounted bath spout + diverter")
    cyl("TUB_MIXER", 34.95, -0.1, 0.12, 2.5, 2.62, M["chrome"], "sanitaryware", "concealed thermostatic mixer (hot/cold)")
    cyl("HAND_SHOWER_RAIL", 36.6, -0.12, 0.035, 2.4, 5.6, M["chrome"], "sanitaryware", "slide rail + hand shower 100 mm", 10)
    box("HAND_SHOWER", 36.52, 36.68, -0.3, -0.12, 5.0, 5.55, M["chrome"], "sanitaryware", "hand shower head")
    hcyl("CURTAIN_ROD", TX0, TX1, TY0 - 0.02, 6.95, 0.03, M["chrome"], "sanitaryware", "ceiling-to-wall curtain rod")
    curtain("SHOWER_CURTAIN", 36.2, 37.4, TY0 - 0.02, 1.9, 6.9, M["curtain"], "soft_furnishing", "waterproof PEVA curtain - drawn along the tub when showering", 0.08, 5)
    box("BATH_MAT", 33.4, 35.6, -3.35, -2.65, -0.042, -0.01, M["mat"], "soft_furnishing", "cotton bath mat")
    # --- vanity on the partition (bath side)
    VX0, VX1, VY0 = 28.9, 31.4, YPN + TILE
    box("VANITY_CABINET", VX0, VX1, VY0, VY0 + 1.55, 1.15, 2.62, M["vanity"], "furniture", "wall-hung vanity 750 x 450 mm, WPC carcass, oak laminate, 2 drawers")
    box("VANITY_TOP", VX0, VX1, VY0, VY0 + 1.6, 2.62, 2.72, M["quartz"], "furniture", "20 mm quartz top")
    cyl("VANITY_BASIN", 30.15, VY0 + 0.85, 0.5, 2.72, 3.05, M["ceramic"], "sanitaryware", "counter-top ceramic basin 400 mm", 28, 0.8)
    cyl("VANITY_TAP", 30.15, VY0 + 0.18, 0.05, 2.72, 3.55, M["chrome"], "sanitaryware", "tall pillar tap", 10)
    box("VANITY_MIRROR", 29.05, 31.25, VY0, VY0 + 0.04, 3.7, 6.2, M["mirror"], "decor", "frameless mirror 650 x 750 mm with demister")
    box("MIRROR_LIGHT", 29.3, 31.0, VY0, VY0 + 0.12, 6.3, 6.4, M["led"], "lighting", "IP44 LED mirror light 3000K", {"light": "strip", "lumens": 600})
    box("TOWEL_RAIL", 32.0, 34.0, VY0, VY0 + 0.25, 4.2, 4.28, M["chrome"], "decor", "towel rail 600 mm")
    box("TOWEL", 32.3, 33.6, VY0 + 0.12, VY0 + 0.25, 3.0, 4.25, M["towel"], "soft_furnishing", "bath towel")
    # --- services
    box("GEYSER", XW + TILE, XW + 1.1, -1.55, -0.3, 7.3, 8.9, M["fitting"], "fixtures", "15 L storage geyser, 5-star, on its own 16 A point")
    box("EXHAUST_FAN", 35.4, 36.1, -0.12, -TILE, 8.4, 9.1, M["fitting"], "fixtures", "150 mm exhaust fan in the existing high vent")
    for i, (x, y) in enumerate(((29.7, -2.5), (35.0, -1.3))):
        cyl(f"DOWNLIGHT_{i+1}", x, y, 0.28, H - 0.06, H, M["led"], "lighting", "IP44 6 W downlight 3000K", 20, 1.0, {"light": "spot", "lumens": 450})
    cyl("PLANT_POT", 26.0, -0.6, 0.35, 0, 0.9, M["pot"], "plants", "pothos - likes the humidity")
    o = cyl("PLANT_LEAVES", 26.0, -0.6, 0.55, 0.9, 1.9, M["plant"], "plants", "pothos", 12)
    # --- Bath 2 (existing WC room): WC + small basin
    BZ = -1 * IN
    box("WC_CISTERN", 22.05, 23.15, -7.083 + TILE, -6.55, 1.35, 2.55, M["ceramic"], "sanitaryware", "close-coupled EWC, dual flush (Bath 2)")
    cyl("WC_BOWL", 22.6, -5.95, 0.58, BZ, 1.32, M["ceramic"], "sanitaryware", "EWC bowl, floor mounted, S-trap to the existing stack", 28, 1.25)
    box("WC_SEAT", 22.05, 23.15, -6.55, -5.3, 1.32, 1.38, M["ceramic"], "sanitaryware", "soft-close seat")
    cyl("HEALTH_FAUCET", 20.55, -5.6, 0.06, 2.0, 2.4, M["chrome"], "sanitaryware", "health faucet", 10)
    box("WC_BASIN", 21.85, 23.35, -1.3, 0, 2.5, 2.8, M["ceramic"], "sanitaryware", "wall-hung hand-wash basin 450 mm (Bath 2)")
    box("WC_MIRROR", 22.0, 23.2, -0.04, 0, 3.3, 4.8, M["mirror"], "decor", "small mirror below W3")
    cyl("WC_DOWNLIGHT", 22.6, -3.6, 0.28, H - 0.06, H, M["led"], "lighting", "IP44 6 W downlight", 20, 1.0, {"light": "spot", "lumens": 450})

def run():
    global COL
    c = bpy.data.collections.get(COLL_NAME)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
    COL = bpy.data.collections.new(COLL_NAME); bpy.context.scene.collection.children.link(COL)
    COL["version"] = "V1.2"; COL["note"] = "Room 2 en-suite: tub room + Bath 2, one door into Room 2"
    MATS.clear()
    notes = edit_architecture()
    build()
    return {"objects": len(COL.objects), "notes": notes}
