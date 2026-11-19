# MyFlat V2 - Room 2 bedroom furnishing (19 Nov 2026). Run after build_room2_ensuite_v2.py on the V2 file.
# Coordinates are V2 feet (no shift). Room 2 bedroom: x 27.917 (west inner face) .. east wall (tapers 40.5 -> 38.42),
# y -6.683 (cross wall south face) .. -23.583 (south wall). Doors: passage y -7.5..-10.5 and hall y -20.25..-23.25 (west wall),
# bathroom doorway x 27.92..30.92 in the cross wall. Windows W5 y -6.86..-11.13, W6 y -14.1..-18.37 (east wall).
# Layout (checked against clearances, see compare.json "checks"):
#   queen bed with its head on the cross wall, x 32.2..37.2 -> 695 mm walk on the west, 646 mm on the east;
#   sliding wardrobe on the west wall between the two doors (front clearance 695 mm to the bed);
#   desk under W6 on the east wall, chest of drawers + mirror on the south wall, split AC above it (not over the bed);
#   bedside tables level with the mattress, wall reading lights, ceiling fan between the bed foot and the desk.
import bpy, bmesh, math
from mathutils import Vector

FT = 0.3048; H = 10.0
XW, YN, YS = 27.917, -6.683, -23.583
def m(v): return v * FT
def xin(y): return 40.5 - 2.083 * (-y / 23.583)
COLL_NAME = "26_ROOM2_BEDROOM"; COL = None; MATS = {}

def mat(name, rgb, rough=0.6, metal=0.0, emit=0.0):
    key = "R2BR_" + name
    if key in MATS: return MATS[key]
    mt = bpy.data.materials.get(key) or bpy.data.materials.new(key); mt.use_nodes = True
    b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    mt.diffuse_color = (*rgb, 1); MATS[key] = mt; return mt

def _obj(name, me, mt, cat, spec, loc):
    o = bpy.data.objects.new("R2BR_" + name, me); o.location = Vector([m(v) for v in loc])
    if mt: o.data.materials.append(mt)
    COL.objects.link(o); o["design_category"] = cat; o["status"] = "DESIGN"; o["version"] = "V2"
    if spec: o["spec"] = spec
    return o
def _bm_box(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new((m(a), m(b), m(c))) for a, b, c in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])
def boxes(name, bxs, mt, cat, spec="", props=None, soft=0.0):
    cx, cy = (bxs[0][0] + bxs[0][1]) / 2, (bxs[0][2] + bxs[0][3]) / 2
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for (a, b, c, d, e, f) in bxs: _bm_box(bm, a - cx, b - cx, c - cy, d - cy, e, f)
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (cx, cy, 0))
    for k, v in (props or {}).items(): o[k] = v
    if soft:
        md = o.modifiers.new("Soft", 'BEVEL'); md.width = m(soft / 12); md.segments = 3; md.limit_method = 'ANGLE'; md.use_clamp_overlap = True
        for p in o.data.polygons: p.use_smooth = True
    return o
def box(name, x0, x1, y0, y1, z0, z1, mt, cat, spec="", props=None, soft=0.0): return boxes(name, [(x0, x1, y0, y1, z0, z1)], mt, cat, spec, props, soft)
def cyl(name, cx, cy, r, z0, z1, mt, cat, spec="", n=24, props=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=m(r), radius2=m(r), depth=m(z1 - z0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, m(z1 - z0) / 2)); bm.to_mesh(me); bm.free()
    o = _obj(name, me, mt, cat, spec, (cx, cy, z0))
    for k, v in (props or {}).items(): o[k] = v
    return o
def seg_box(name, p0, p1, w, z0, z1, mt, cat, spec=""):
    """box along the segment p0 -> p1 (plan, feet), w wide"""
    (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy * w / 2, ux * w / 2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
    v = [bm.verts.new((m(a - cx), m(b - cy), m(z))) for z in (z0, z1) for a, b in pts]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return _obj(name, me, mt, cat, spec, (cx, cy, 0))
def wavy_along(name, p0, p1, amp, waves, z0, z1, mt, cat, spec=""):
    (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    n = max(8, int(waves * 8)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    me = bpy.data.meshes.new(name); bm = bmesh.new(); cols = []
    for i in range(n + 1):
        t = i / n; d = amp * math.sin(t * waves * 2 * math.pi); x = x0 + (x1 - x0) * t - uy * d; y = y0 + (y1 - y0) * t + ux * d
        cols.append((bm.verts.new((m(x - cx), m(y - cy), m(z0))), bm.verts.new((m(x - cx), m(y - cy), m(z1)))))
    for i in range(n): bm.faces.new((cols[i][0], cols[i + 1][0], cols[i + 1][1], cols[i][1]))
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (cx, cy, 0))
    for p in o.data.polygons: p.use_smooth = True
    mod = o.modifiers.new("Thick", 'SOLIDIFY'); mod.thickness = m(0.04)
    return o

def build():
    wood = mat("Oak", (0.62, 0.48, 0.33), 0.55); walnut = mat("Walnut", (0.38, 0.27, 0.18), 0.5)
    lam = mat("Laminate_White", (0.90, 0.89, 0.86), 0.45); fabric = mat("Headboard_Fabric", (0.55, 0.60, 0.55), 0.95)
    sheet = mat("Sheet_White", (0.95, 0.94, 0.92), 0.9); duvet = mat("Duvet_Rust", (0.70, 0.45, 0.33), 0.9); pillow = mat("Pillow", (0.93, 0.91, 0.86), 0.9)
    metal = mat("Metal_Black", (0.08, 0.08, 0.08), 0.35, 0.9); glass = mat("Mirror", (0.8, 0.85, 0.88), 0.03, 1.0)
    led = mat("LED_Warm", (1.0, 0.88, 0.68), 0.4, 0, 3.0); curt = mat("Curtain_Linen", (0.86, 0.82, 0.74), 0.95)
    rug = mat("Rug", (0.78, 0.72, 0.62), 0.95); white = mat("AC_White", (0.95, 0.95, 0.94), 0.4); leaf = mat("Foliage", (0.22, 0.42, 0.2), 0.8)
    # --- bed: head on the cross wall
    BX0, BX1, BY0, BY1 = 32.2, 37.2, -13.5, -7.0
    box("BED_HEADBOARD", BX0 - 0.1, BX1 + 0.1, BY1, BY1 + 0.27, 0.0, 3.8, fabric, "furniture", "upholstered headboard 5'2\" wide, fixed to the cross wall", soft=1.0)
    box("BED_BASE", BX0, BX1, BY0, BY1, 0.3, 1.3, walnut, "furniture", "queen bed 5 × 6½ ft with hydraulic box storage, sheesham or BWP ply", soft=0.6)
    box("BED_PLINTH", BX0 + 0.2, BX1 - 0.2, BY0 + 0.2, BY1 - 0.2, 0.0, 0.3, metal, "furniture", "recessed plinth so the bed looks lighter")
    box("BED_MATTRESS", BX0 + 0.08, BX1 - 0.08, BY0 + 0.08, BY1 - 0.05, 1.3, 1.85, sheet, "soft_furnishing", "queen mattress 6 inch, HR foam or latex hybrid (cooler than memory foam)", soft=1.5)
    box("BED_DUVET", BX0 + 0.02, BX1 - 0.02, BY0 + 0.02, -9.6, 1.6, 1.95, duvet, "soft_furnishing", "cotton dohar / duvet", soft=1.5)
    boxes("BED_PILLOWS", [(BX0 + 0.35, 34.55, -8.05, -7.15, 1.85, 2.3), (34.85, BX1 - 0.35, -8.05, -7.15, 1.85, 2.3)], pillow, "soft_furnishing", "two pillows", soft=2.0)
    # --- bedside tables (top level with the mattress) + wall reading lights
    for side, (x0, x1) in (("W", (30.95, 32.1)), ("E", (37.35, 38.6))):
        box(f"BEDSIDE_{side}", x0, x1, -8.3, -6.83, 0.0, 1.9, wood, "furniture", "bedside table with a drawer, top level with the mattress", soft=0.4)
        xc = (x0 + x1) / 2
        boxes(f"WALL_LAMP_{side}", [(xc - 0.12, xc + 0.12, -6.83, -6.75, 4.1, 4.5), (xc - 0.03, xc + 0.03, -7.5, -6.83, 4.4, 4.46), (xc - 0.2, xc + 0.2, -7.75, -7.35, 3.95, 4.4)],
              metal, "lighting", "swing-arm reading light with its own switch, 3000K", props={"light": "spot", "lumens": 300})
    # --- sliding wardrobe on the west wall between the two doors
    WY0, WY1, WD = -17.0, -11.0, 2.0
    box("WARDROBE_CARCASS", XW, XW + WD, WY0, WY1, 0.3, 9.5, lam, "wardrobe", "sliding wardrobe 6 × 2 ft to the loft, BWP ply carcase, laminate outside")
    box("WARDROBE_PLINTH", XW, XW + WD - 0.1, WY0, WY1, 0.0, 0.3, walnut, "wardrobe", "")
    boxes("WARDROBE_SLIDER", [(XW + WD, XW + WD + 0.06, WY0, (WY0 + WY1) / 2 + 0.05, 0.35, 7.45), (XW + WD + 0.06, XW + WD + 0.12, (WY0 + WY1) / 2 - 0.05, WY1, 0.35, 7.45)],
          lam, "wardrobe", "two sliding shutters (no swing space needed), soft-close track")
    box("WARDROBE_LOFT_DOOR", XW + WD, XW + WD + 0.05, WY0, WY1, 7.55, 9.45, lam, "wardrobe", "loft shutters")
    boxes("WARDROBE_SLIDER_PULL", [(XW + WD + 0.06, XW + WD + 0.1, -14.3, -14.2, 3.0, 5.0), (XW + WD + 0.12, XW + WD + 0.16, -13.8, -13.7, 3.0, 5.0)], metal, "wardrobe", "slim black pulls")
    # --- desk under W6 + chair
    DY0, DY1 = -18.8, -15.2; dx1 = min(xin(DY0), xin(DY1)) - 0.08; dx0 = dx1 - 1.95
    box("STUDY_DESK_TOP", dx0, dx1, DY0, DY1, 2.33, 2.45, wood, "furniture", "study desk 3'7\" × 2' at 29 inch, matt laminate top", soft=0.3)
    boxes("STUDY_DESK_LEGS", [(dx0 + 0.05, dx0 + 0.15, DY0 + 0.05, DY0 + 0.15, 0, 2.33), (dx0 + 0.05, dx0 + 0.15, DY1 - 0.15, DY1 - 0.05, 0, 2.33),
                              (dx1 - 0.15, dx1 - 0.05, DY0 + 0.05, DY0 + 0.15, 0, 2.33), (dx1 - 0.15, dx1 - 0.05, DY1 - 0.15, DY1 - 0.05, 0, 2.33)], metal, "furniture", "")
    cx_ = dx0 - 0.9; cy_ = (DY0 + DY1) / 2
    boxes("STUDY_CHAIR", [(cx_ - 0.75, cx_ + 0.75, cy_ - 0.75, cy_ + 0.75, 1.45, 1.6), (cx_ - 0.85, cx_ - 0.75, cy_ - 0.7, cy_ + 0.7, 1.6, 3.6),
                          (cx_ - 0.05, cx_ + 0.05, cy_ - 0.05, cy_ + 0.05, 0.2, 1.45), (cx_ - 0.6, cx_ + 0.6, cy_ - 0.05, cy_ + 0.05, 0.1, 0.2), (cx_ - 0.05, cx_ + 0.05, cy_ - 0.6, cy_ + 0.6, 0.1, 0.2)],
          mat("Chair_Mesh", (0.2, 0.2, 0.22), 0.7), "furniture", "ergonomic mesh chair with lumbar support")
    # --- chest of drawers + mirror on the south wall, split AC high above it
    box("CHEST_OF_DRAWERS", 32.0, 36.0, YS, YS + 1.5, 0.0, 2.7, walnut, "furniture", "chest of drawers 4 ft, 4 drawers", soft=0.4)
    boxes("CHEST_GROOVES", [(32.05, 35.95, YS + 1.5, YS + 1.52, z, z + 0.03) for z in (0.7, 1.35, 2.0)], metal, "furniture", "")
    box("DRESSER_MIRROR", 32.8, 35.2, YS, YS + 0.05, 3.5, 6.2, glass, "decor", "wall mirror 2'5\" × 2'8\" above the chest")
    box("SPLIT_AC", 32.4, 35.6, YS, YS + 0.75, 7.2, 8.2, white, "fixtures", "1.5 ton 5-star inverter split AC on the south wall: blows along the room, not onto the bed", soft=0.5)
    # --- curtains on W5 and W6 (east wall), ceiling fan, downlights, rug, plant
    for w, (y0, y1) in (("W5", (-6.86, -11.13)), ("W6", (-14.1, -18.37))):
        a, b = y0 + 0.5 if y0 + 0.5 < -6.75 else -6.78, y1 - 0.5
        p0, p1 = (xin(a) - 0.3, a), (xin(b) - 0.3, b)
        seg_box(f"{w}_CURTAIN_ROD", p0, p1, 0.08, 7.6, 7.68, metal, "soft_furnishing", "curtain rod, matt black")
        for side, (s0, s1) in (("A", (a, a - 1.1)), ("B", (b + 1.1, b))):
            wavy_along(f"{w}_CURTAIN_{side}", (xin(s0) - 0.22, s0), (xin(s1) - 0.22, s1), 0.07, 4, 0.1, 7.55, curt, "soft_furnishing", "linen-look blackout curtains, stacked open beside the window")
    cyl("FAN_ROD", 34.5, -15.0, 0.05, 8.9, H, white, "fixtures", "", 8)
    cyl("FAN_HUB", 34.5, -15.0, 0.35, 8.6, 8.9, white, "fixtures", "BLDC ceiling fan 1200 mm")
    bl = []
    for kk in range(3):
        ang = kk * 2 * math.pi / 3; ux, uy = math.cos(ang), math.sin(ang)
        for s in range(6):
            r0 = 0.4 + s * 0.27; bl.append((34.5 + ux * r0 - 0.14, 34.5 + ux * r0 + 0.14, -15.0 + uy * r0 - 0.14, -15.0 + uy * r0 + 0.14, 8.68, 8.74))
    boxes("FAN_BLADES", bl, white, "fixtures", "fan blades")
    for i, (x, y) in enumerate(((30.4, -9.8), (30.4, -19.5), (35.6, -19.8), (34.7, -11.0))):
        cyl(f"DOWNLIGHT_{i+1}", x, y, 0.28, H - 0.05, H, led, "lighting", "10 W LED downlight 3000K", 20, {"light": "spot", "lumens": 800})
    box("RUG", 31.5, 37.9, -15.0, -9.5, 0.0, 0.03, rug, "soft_furnishing", "cotton dhurrie 6 × 6½ ft under the lower part of the bed")
    cyl("PLANT_POT", 38.0, -21.6, 0.45, 0.0, 1.3, mat("Pot", (0.82, 0.8, 0.76), 0.6), "plants", "planter, 14 inch")
    cyl("PLANT_LEAVES", 38.0, -21.6, 0.7, 1.3, 3.6, leaf, "plants", "rubber plant / snake plant", 12)

def run():
    global COL
    c = bpy.data.collections.get(COLL_NAME)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
    COL = bpy.data.collections.new(COLL_NAME); bpy.context.scene.collection.children.link(COL)
    COL["version"] = "V2"; COL["note"] = "Room 2 bedroom furnishing (all plans)"; MATS.clear()
    build()
    return {"objects": len(COL.objects)}
