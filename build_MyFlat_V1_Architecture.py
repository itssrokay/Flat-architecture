# MyFlat_V1_Architecture - parametric architectural base model (Blender 4.2+ / 5.x)
# ---------------------------------------------------------------------------------
# All dimensions are in FEET in table P. Edit a value, then run this script
# (Text Editor > Run Script) to rebuild. Openings (doors/windows/vents) are EMPTIES:
# move/rotate an empty and its cutter, frame, leaf and glass follow, and the wall
# hole updates live (non-destructive Boolean modifiers).
#
# Every object has custom properties:
#   status = CONFIRMED | PLAN | DERIVED | PROVISIONAL
#   basis  = where the value came from
# Viewport tip: Solid shading > Color: Object  -> status map
#   green = CONFIRMED, blue = PLAN, yellow = DERIVED, orange = PROVISIONAL
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

FT = 0.3048
IN = 1 / 12
HOME_DIR = os.path.join(os.path.expanduser("~"), "Documents", "MyFlat")
PLAN_IMAGE = os.path.join(HOME_DIR, "floorplan_reference.png")

P = dict(
    # ---- structure (PROVISIONAL unless noted) ----
    T_EXT=9 * IN, T_INT=5 * IN,
    T_BAL=15 * IN,            # CONFIRMED Room1<->balcony wall
    CEIL_H=10.0,              # floor finish -> slab underside
    SLAB=5 * IN, FLOOR_SLAB=6 * IN, FINISH=3 * IN,
    DOOR_H=7.0,
    BATH_DROP=1 * IN, BAL_DROP=2 * IN, OPEN_DROP=3 * IN,
    # ---- north row ----
    R1_W=12 + 7 * IN,         # CONFIRMED Room1 livable width
    K_D=7 + 1 * IN,           # PLAN
    PAS_W=5.0,                # PLAN
    KG_W=3.0,                 # PROVISIONAL kitchen gate
    K_EXTRA=4.0,              # CONFIRMED kitchen = gate + 4'
    B2_W=4 + 5 * IN,          # CONFIRMED (approx)
    R2_WN=12 + 7 * IN,        # PLAN
    R2_WS=10.5,               # PLAN (narrowing CONFIRMED)
    R2_D=23 + 7 * IN,         # CONFIRMED total
    # ---- hall block ----
    HALL_W=21.0, HALL_D=32.0,  # PLAN
    BUMP_W=3.5,               # PROVISIONAL
    STAIR_D=10 + 5 * IN,      # PROVISIONAL
    B1_W=4.0, B1_D=8.5,       # PLAN (orientation PROVISIONAL)
    # ---- balcony ----
    BAL_D=3.5, BAL_L=14 + 8 * IN,  # PLAN
    RAIL_H=3.25,              # PROVISIONAL
    # ---- open square ----
    PARAPET_H=3.0, OS_RAIL_H=1.5,  # PROVISIONAL (site video: low wall + grill)
    # ---- openings ----
    WIN=4.0, SILL=3.0,        # CONFIRMED 4x4 opening; sill PROVISIONAL
    R1EXIT_FROM_S=2 + 2 * IN, R1EXIT_W=2 + 8 * IN,
    BAL_OPEN_FROM_S=19 * IN, BAL_OPEN_W=6.0,
    HALLGATE_W=5 + 8 * IN, HALLGATE_X0=1.9,
    ROOM_DOOR_W=3.0, BATH_DOOR_W=2.5,
    DOOR_OPEN_DEG=90.0,       # leaves shown open so swing is visible
    # ---- pillars / beams ----
    PIL_EW=9 * IN, PIL_NS=15 * IN,   # PROVISIONAL rectangular
    P2_FROM_N=7.5, P1_FROM_N=16.5,
    BEAM_W=9 * IN, BEAM_DROP=12 * IN,
    # ---- stair ----
    N_RISERS=16, TREAD=10 * IN, STAIR_WAIST=5 * IN, NOSING=1 * IN,
    # ---- vents ----
    VENT=6 * IN, VENT_Z=8.75,
)
STATUS_COL = {"CONFIRMED": (0.2, 0.75, 0.3, 1), "PLAN": (0.25, 0.5, 0.95, 1),
              "DERIVED": (0.95, 0.8, 0.15, 1), "PROVISIONAL": (1.0, 0.45, 0.05, 1),
              "REFERENCE": (0.6, 0.6, 0.6, 1)}

def m(v): return v * FT
def V(x, y, z=0): return Vector((m(x), m(y), m(z)))

# ------------------------------------------------------------------ geometry derivation
def derive(p):
    TE, TI = p['T_EXT'], p['T_INT']
    d = {}
    d['xW'] = -p['T_BAL']; d['yN'] = TE
    d['xR1E'] = p['R1_W']; d['xK0'] = d['xR1E'] + TI
    d['xK1'] = d['xK0'] + p['KG_W'] + p['K_EXTRA']
    d['xB0'] = d['xK1'] + TI; d['xB1'] = d['xB0'] + p['B2_W']; d['xR20'] = d['xB1'] + TI
    d['xR21N'] = d['xR20'] + p['R2_WN']; d['xR21S'] = d['xR20'] + p['R2_WS']
    d['yK1'] = -p['K_D']; d['yP0'] = d['yK1'] - TI; d['yP1'] = d['yP0'] - p['PAS_W']
    d['yH0'] = d['yP1'] - TE; d['yH1'] = d['yH0'] - p['HALL_D']; d['ySo'] = d['yH1'] - TE
    d['xH1'] = d['xB1']; d['xH0'] = d['xH1'] - p['HALL_W']
    d['yR21'] = -p['R2_D']; d['yR2w'] = d['yR21'] - TI
    d['xSw0'] = d['xH1'] + p['BUMP_W']; d['xSt0'] = d['xSw0'] + TI; d['xSt1'] = d['xR21S']
    d['ySt1'] = d['yR2w'] - p['STAIR_D']; d['yBump'] = d['ySt1'] + TI
    d['yB1n'] = d['yH1'] + p['B1_D']; d['xB1_0'] = d['xH1'] - p['B1_W']
    d['xE1'] = d['xR21S'] + TE
    return d

# ------------------------------------------------------------------ helpers
COLL = {}
def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent.children if parent else bpy.context.scene.collection.children).link(c)
    COLL[name] = c; return c

MATS = {}
def mat(name, rgba, rough=0.8, metal=0.0):
    if name in MATS: return MATS[name]
    mt = bpy.data.materials.new(name); mt.use_nodes = True
    b = mt.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = rgba
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        if rgba[3] < 1:
            b.inputs["Alpha"].default_value = rgba[3]
            try: mt.surface_render_method = 'BLENDED'
            except Exception: pass
    mt.diffuse_color = rgba
    MATS[name] = mt; return mt

def tag(o, status, basis=""):
    o["status"] = status
    if basis: o["basis"] = basis
    o.color = STATUS_COL.get(status, (0.7, 0.7, 0.7, 1))
    return o

def link(o, c):
    for uc in list(o.users_collection): uc.objects.unlink(o)
    c.objects.link(o)

def bm_box(bm, x0, x1, y0, y1, z0, z1):
    """add axis-aligned box (metres) to bmesh"""
    vs = [bm.verts.new(v) for v in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                                    (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        bm.faces.new([vs[i] for i in f])

def mesh_obj(name, boxes_ft, c, mt, status, basis, origin=(0, 0, 0)):
    """object from list of boxes in FEET, relative to origin (ft)"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    ox, oy, oz = origin
    for (x0, x1, y0, y1, z0, z1) in boxes_ft:
        bm_box(bm, m(x0-ox), m(x1-ox), m(y0-oy), m(y1-oy), m(z0-oz), m(z1-oz))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = V(*origin)
    if mt: o.data.materials.append(mt)
    c.objects.link(o); return tag(o, status, basis)

def box(name, x0, x1, y0, y1, z0, z1, c, mt, status, basis=""):
    org = ((x0+x1)/2, (y0+y1)/2, z0)
    return mesh_obj(name, [(x0, x1, y0, y1, z0, z1)], c, mt, status, basis, org)

def prism(name, pts, z0, z1, c, mt, status, basis=""):
    cx = sum(q[0] for q in pts)/len(pts); cy = sum(q[1] for q in pts)/len(pts)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bot = [bm.verts.new((m(x-cx), m(y-cy), 0)) for x, y in pts]
    f = bm.faces.new(bot); f.normal_update()
    if f.normal.z > 0: f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in r['geom']:
        if isinstance(v, bmesh.types.BMVert): v.co.z = m(z1 - z0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = V(cx, cy, z0)
    if mt: o.data.materials.append(mt)
    c.objects.link(o); return tag(o, status, basis)

def bar_between(name, p0, p1, w, h, c, mt, status, basis=""):
    """square-section bar from p0 to p1 (ft tuples)"""
    a, b = V(*p0), V(*p1); L = (b - a).length
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bm_box(bm, 0, L, -m(w)/2, m(w)/2, -m(h)/2, m(h)/2); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = a
    o.rotation_euler = (b - a).to_track_quat('X', 'Z').to_euler()
    if mt: o.data.materials.append(mt)
    c.objects.link(o); return tag(o, status, basis)

def empty(name, loc_ft, rot_z, c, status, basis=""):
    e = bpy.data.objects.new(name, None); e.empty_display_type = 'ARROWS'
    e.empty_display_size = 0.25; e.location = V(*loc_ft); e.rotation_euler.z = rot_z
    c.objects.link(e); return tag(e, status, basis)

def child(o, parent):
    o.parent = parent  # local geometry was built in parent space: no inverse needed
    return o

def railing_mesh(name, p0, p1, z0, h, c, mt, status, basis, spacing=4 * IN, post=4.0):
    """steel railing along p0->p1 (ft): posts, top rail, mid rail, balusters. Built in local
    space (x along run) and placed with an object transform."""
    a, b = Vector(p0), Vector(p1); L = (b - a).length
    boxes = []
    n_bal = max(1, int(L / spacing))
    for i in range(n_bal + 1):
        x = min(L - 0.03, i * L / n_bal); boxes.append((x-0.03, x+0.03, -0.03, 0.03, 0, h))
    n_post = max(1, int(round(L / post)))
    for i in range(n_post + 1):
        x = min(L - 0.08, max(0.0, i * L / n_post - 0.08)); boxes.append((x, x+0.16, -0.08, 0.08, 0, h))
    boxes.append((0, L, -0.1, 0.1, h - 0.12, h))          # top rail
    boxes.append((0, L, -0.04, 0.04, 0.35, 0.45))         # bottom rail
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for bx in boxes: bm_box(bm, *[m(v) for v in bx])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = V(a.x, a.y, z0); o.rotation_euler.z = math.atan2(b.y - a.y, b.x - a.x)
    o.data.materials.append(mt); c.objects.link(o); return tag(o, status, basis)

def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras):
        for x in list(blk):
            if x.users == 0: blk.remove(x)
    for t in list(bpy.data.texts):
        pass

# ------------------------------------------------------------------ build
def run():
    clear(); MATS.clear(); COLL.clear()
    p = P; d = derive(p); g = d.__getitem__
    TE, TI, H = p['T_EXT'], p['T_INT'], p['CEIL_H']
    ZB = -p['FINISH']                    # top of structural floor slab
    sc = bpy.context.scene
    sc.unit_settings.system = 'IMPERIAL'; sc.unit_settings.length_unit = 'ADAPTIVE'

    C_W = coll("01_WALLS"); C_WE = coll("WALLS_EXTERNAL", C_W); C_WI = coll("WALLS_INTERNAL", C_W)
    C_CUT = coll("_OPENING_CUTTERS", C_W); C_VCUT = coll("_VENT_CUTTERS", C_W)
    C_F = coll("02_FLOORS"); C_C = coll("03_CEILING_SLAB"); C_D = coll("04_DOORS"); C_WN = coll("05_WINDOWS")
    C_P = coll("06_PILLARS"); C_B = coll("07_BEAMS"); C_S = coll("08_STAIRS"); C_BA = coll("09_BALCONY")
    C_OS = coll("10_OPEN_SQUARE"); C_R = coll("11_REFERENCE"); C_L = coll("LABELS", C_R); C_CAM = coll("CAMERAS", C_R)
    C_PR = coll("12_PROVISIONAL")

    M = dict(
        wall=mat("Plaster_White", (0.9, 0.89, 0.86, 1)), conc=mat("Concrete", (0.62, 0.62, 0.6, 1)),
        slab=mat("Slab_Concrete", (0.72, 0.72, 0.7, 1)), frame=mat("Frame_Wood", (0.42, 0.27, 0.15, 1)),
        leaf=mat("Door_Leaf", (0.62, 0.43, 0.25, 1)), wframe=mat("Window_Frame_Steel", (0.22, 0.24, 0.26, 1), 0.4, 0.6),
        glass=mat("Glass", (0.6, 0.8, 0.95, 0.3), 0.05), steel=mat("Railing_Steel", (0.15, 0.15, 0.16, 1), 0.4, 0.7),
        stair=mat("Stair_Concrete", (0.78, 0.74, 0.66, 1)), thr=mat("Threshold_Stone", (0.85, 0.85, 0.82, 1), 0.3),
        cut=mat("Cutter", (1, 0, 0, 0.25)), lab=mat("Label", (0.05, 0.05, 0.05, 1)),
        ground=mat("Ground", (0.62, 0.66, 0.58, 1)), vent=mat("Vent_Frame", (0.35, 0.35, 0.35, 1)))
    floor_col = {"R1": (0.93, 0.85, 0.7, 1), "KIT": (0.8, 0.9, 0.72, 1), "B2": (0.72, 0.84, 0.95, 1),
                 "PAS": (0.9, 0.88, 0.8, 1), "R2": (0.95, 0.8, 0.72, 1), "HALL": (0.93, 0.9, 0.82, 1),
                 "B1": (0.72, 0.84, 0.95, 1), "STAIR": (0.85, 0.8, 0.9, 1), "OPENSQ": (0.6, 0.6, 0.6, 1)}

    xW, yN = g('xW'), g('yN'); xR1E, xK0, xK1, xB0, xB1, xR20 = [g(k) for k in ('xR1E','xK0','xK1','xB0','xB1','xR20')]
    xR21N, xR21S, yK1, yP0, yP1 = [g(k) for k in ('xR21N','xR21S','yK1','yP0','yP1')]
    yH0, yH1, ySo, xH0, xH1 = [g(k) for k in ('yH0','yH1','ySo','xH0','xH1')]
    yR21, yR2w, xSw0, xSt0, xSt1, ySt1, yBump = [g(k) for k in ('yR21','yR2w','xSw0','xSt0','xSt1','ySt1','yBump')]
    yB1n, xB1_0, xE1 = g('yB1n'), g('xB1_0'), g('xE1')

    # ============ FLOORS ============
    foot = [(xW, yN), (xR21N+TE, yN), (xE1, yR2w), (xE1, ySo), (xH0-TE, ySo), (xH0-TE, yH0), (xW, yH0)]
    prism("SLAB_FLOOR_STRUCTURAL", foot, ZB - p['FLOOR_SLAB'], ZB, C_F, M['slab'], "PROVISIONAL", "6in slab + 3in finish zone assumed")
    rooms = {
        "R1": ([(0,0),(xR1E,0),(xR1E,yP1),(0,yP1)], 0, "DERIVED", "12'7\" CONFIRMED x 12'6\" DERIVED (south wall aligned with passage)"),
        "KIT": ([(xK0,0),(xK1,0),(xK1,yK1),(xK0,yK1)], 0, "DERIVED", "width = gate(3' prov) + 4' ; depth 7'1\" PLAN"),
        "B2": ([(xB0,0),(xB1,0),(xB1,yK1),(xB0,yK1)], -p['BATH_DROP'], "DERIVED", "4'5\" CONFIRMED x 7'1\" (=kitchen) ; sunk 1\" PROVISIONAL"),
        "PAS": ([(xK0,yP0),(xB1,yP0),(xB1,yP1),(xK0,yP1)], 0, "PLAN", "5' PLAN"),
        "R2": ([(xR20,0),(xR21N,0),(xR21S,yR21),(xR20,yR21)], 0, "PLAN", "23'7\" CONFIRMED, 12'7\"->10'6\" PLAN, taper side PROVISIONAL"),
        "HALL": ([(xH0,yH0),(xH1,yH0),(xH1,yR2w),(xSw0,yR2w),(xSw0,yBump),(xH1,yBump),(xH1,yB1n+TI),(xB1_0-TI,yB1n+TI),(xB1_0-TI,yH1),(xH0,yH1)], 0, "PLAN", "21' x 32' PLAN"),
        "B1": ([(xB1_0,yB1n),(xH1,yB1n),(xH1,yH1),(xB1_0,yH1)], -p['BATH_DROP'], "PLAN", "4' x 8'6\" PLAN, orientation PROVISIONAL"),
        "STAIR": ([(xSt0,yR2w),(xSt1,yR2w),(xSt1,ySt1),(xSt0,ySt1)], 0, "PROVISIONAL", "size/position PROVISIONAL"),
    }
    for n, (pts, top, st, basis) in rooms.items():
        prism(f"FLOOR_{n}", pts, ZB, top, C_F, mat(f"Floor_{n}", floor_col[n]), st, basis)
    os_pts = [(xR20,ySt1),(xSt1,ySt1),(xSt1,yH1),(xR20,yH1)]
    prism("FLOOR_OPENSQ", os_pts, ZB, -p['OPEN_DROP'], C_OS, mat("Floor_OPENSQ", floor_col["OPENSQ"]), "PROVISIONAL", "open to sky; 3\" lower PROVISIONAL")
    g_ = box("GROUND_CONTEXT", -45, 85, -95, 45, ZB - p['FLOOR_SLAB'] - 0.1, ZB - p['FLOOR_SLAB'] - 0.05, C_R, M['ground'], "REFERENCE"); g_.hide_select = True

    # ============ WALLS ============
    WALLS = []
    def wall(name, x0, x1, y0, y1, ext, status, basis, h=None):
        o = box(name, x0, x1, y0, y1, ZB, h if h is not None else H, C_WE if ext else C_WI, M['wall'], status, basis)
        WALLS.append(o); return o
    SE, SI = "PROVISIONAL", "PROVISIONAL"
    tb = "thickness 9in PROVISIONAL"; ti = "thickness 5in PROVISIONAL"
    # north external wall, split per room
    wall("WALL_EXT_N_R1", xW, xR1E + TI/2, 0, yN, True, "PLAN", "line PLAN; " + tb)
    wall("WALL_EXT_N_KIT", xR1E + TI/2, xK1 + TI/2, 0, yN, True, "PLAN", tb)
    wall("WALL_EXT_N_B2", xK1 + TI/2, xB1 + TI/2, 0, yN, True, "PLAN", tb)
    wall("WALL_EXT_N_R2", xB1 + TI/2, xR21N + TE, 0, yN, True, "PLAN", tb)
    wall("WALL_EXT_W_R1_BALCONY", xW, 0, yH0, yN, True, "CONFIRMED", "15in thick CONFIRMED")
    wall("WALL_EXT_S_R1", xW, xH0, yH0, yP1, True, "DERIVED", "Room1 south, outside part; aligned with passage (your answer)")
    wall("WALL_INT_R1_S_HALL", xH0, xK0, yH0, yP1, False, "DERIVED", "Room1 south / hall north; " + tb)
    wall("WALL_INT_PAS_S_HALL", xK0, xB1, yH0, yP1, False, "PROVISIONAL", "passage/hall; 9in to align with Room1 south")
    wall("WALL_INT_R1_E", xR1E, xK0, yP1, 0, False, "PLAN", ti)
    wall("WALL_INT_KIT_B2_S", xK0, xB1, yP0, yK1, False, "PLAN", ti)
    wall("WALL_INT_KIT_B2", xK1, xB0, yK1, 0, False, "DERIVED", "kitchen width = gate + 4'")
    wall("WALL_INT_R2_W", xB1, xR20, yR2w, 0, False, "PLAN", ti)
    wall("WALL_INT_R2_S", xR20, xR21S + 0.3, yR2w, yR21, False, "CONFIRMED", "Room2 length 23'7\" CONFIRMED")
    o = prism("WALL_EXT_E_R2_TAPERED", [(xR21N, yN), (xR21N+TE, yN), (xE1, yR2w), (xR21S, yR2w)], ZB, H, C_WE, M['wall'],
              "PROVISIONAL", "narrowing CONFIRMED; taper on east wall PROVISIONAL"); WALLS.append(o)
    wall("WALL_EXT_E_STAIR", xR21S, xE1, ySt1, yR2w, True, "PROVISIONAL", tb)
    wall("WALL_EXT_W_HALL", xH0 - TE, xH0, ySo, yH0, True, "PLAN", "position from hall 21' PLAN")
    wall("WALL_EXT_S_HALL", xH0 - TE, xR20, ySo, yH1, True, "PLAN", tb)
    wall("WALL_INT_STAIR_W", xSw0, xSt0, ySt1, yR2w, False, "PROVISIONAL", "stair moved west (your answer); size PROVISIONAL")
    wall("WALL_INT_HALLSTRIP_S", xH1, xSt0, ySt1, yBump, False, "PROVISIONAL", "")
    wall("WALL_INT_OPENSQ_W", xH1, xR20, yH1, ySt1, False, "DERIVED", "Bath1 east = open square west")
    wall("WALL_INT_B1_N", xB1_0 - TI, xH1, yB1n, yB1n + TI, False, "PLAN", ti)
    wall("WALL_INT_B1_W", xB1_0 - TI, xB1_0, yH1, yB1n + TI, False, "DERIVED", "from 4' bath width")
    # open square parapets (open to sky)
    pS = box("PARAPET_OPENSQ_S", xR20, xE1, ySo, yH1, ZB, p['PARAPET_H'], C_OS, M['wall'], "PROVISIONAL", "low wall per site video")
    pE = box("PARAPET_OPENSQ_E", xR21S, xE1, yH1, ySt1, ZB, p['PARAPET_H'], C_OS, M['wall'], "PROVISIONAL", "low wall per site video")
    railing_mesh("RAILING_OPENSQ_S", (xR20 + 0.1, (ySo+yH1)/2), (xE1 - 0.1, (ySo+yH1)/2), p['PARAPET_H'], p['OS_RAIL_H'], C_OS, M['steel'], "PROVISIONAL", "grill on parapet per site video")
    railing_mesh("RAILING_OPENSQ_E", ((xR21S+xE1)/2, yH1), ((xR21S+xE1)/2, ySt1 - 0.1), p['PARAPET_H'], p['OS_RAIL_H'], C_OS, M['steel'], "PROVISIONAL", "")
    box("MARKER_OPENSQ_OPEN_TO_SKY", xR20 + 0.5, xSt1 - 0.5, yH1 + 0.5, ySt1 - 0.5, H + 2, H + 2.02, C_OS, mat("SkyMarker", (0.4, 0.7, 1, 0.15)), "CONFIRMED", "open to sky CONFIRMED - marker only, hidden in renders").hide_render = True

    # ============ OPENINGS ============
    E = 0.3
    FW, FD = 3 * IN, 5 * IN          # frame member width / depth

    def opening_door(name, center, rot, t, w, h, swing, status, basis, leaf=True, frame=True):
        """center = (x,y) on wall centre-line (ft); rot = wall direction (rad), local x along wall,
        local y across wall. swing = +1 opens to local +y, -1 to local -y."""
        e = empty(name, (center[0], center[1], 0), rot, C_D, status, basis)
        e["width_ft"] = w; e["height_ft"] = h
        c = mesh_obj(name + "_CUTTER", [(-w/2, w/2, -t/2 - E, t/2 + E, -0.01, h)], C_CUT, M['cut'], status, basis)
        c.display_type = 'WIRE'; c.hide_render = True; child(c, e)
        if frame:
            fr = mesh_obj(name + "_FRAME", [(-w/2, -w/2 + FW, -FD/2, FD/2, 0, h), (w/2 - FW, w/2, -FD/2, FD/2, 0, h),
                                            (-w/2, w/2, -FD/2, FD/2, h - FW, h)], C_D, M['frame'], status, basis)
            child(fr, e)
        if leaf:
            L = w - 2 * FW; lt = 1.5 * IN
            ly = (-lt, 0) if swing > 0 else (0, lt)       # closed leaf sits inside the frame
            lf = mesh_obj(name + "_LEAF", [(0, L, ly[0], ly[1], 0, h - FW - 0.02)],
                          C_D, M['leaf'], "PROVISIONAL", "leaf size/swing PROVISIONAL unless noted")
            child(lf, e)
            lf.location = V(-w/2 + FW, FD/2 if swing > 0 else -FD/2, 0.0)
            lf.rotation_euler.z = math.radians(p['DOOR_OPEN_DEG']) * (1 if swing > 0 else -1)
            lf["swing"] = "local +Y" if swing > 0 else "local -Y"
        return e

    def opening_window(name, center, rot, t, w, sill, top, status, basis, coll_=None, cutc=None, mullion=True):
        cl = coll_ or C_WN
        e = empty(name, (center[0], center[1], 0), rot, cl, status, basis)
        e["width_ft"] = w; e["sill_ft"] = sill; e["top_ft"] = top
        c = mesh_obj(name + "_CUTTER", [(-w/2, w/2, -t/2 - E, t/2 + E, sill, top)], cutc or C_CUT, M['cut'], status, basis)
        c.display_type = 'WIRE'; c.hide_render = True; child(c, e)
        f = 2.5 * IN if w > 1 else 1.5 * IN
        bx = [(-w/2, -w/2 + f, -FD/2, FD/2, sill, top), (w/2 - f, w/2, -FD/2, FD/2, sill, top),
              (-w/2, w/2, -FD/2, FD/2, sill, sill + f), (-w/2, w/2, -FD/2, FD/2, top - f, top)]
        if mullion and w >= 3: bx.append((-f/2, f/2, -FD/2, FD/2, sill, top))
        fr = mesh_obj(name + "_FRAME", bx, cl, M['wframe'] if w > 1 else M['vent'], status, basis); child(fr, e)
        if w > 1:
            gl = mesh_obj(name + "_GLASS", [(-w/2 + f, w/2 - f, -0.02, 0.02, sill + f, top - f)], cl, M['glass'], status, basis)
            child(gl, e)
        return e

    RX, RY = 0.0, math.pi / 2           # wall along X (E-W) / along Y (N-S)
    # For RY walls, local +y points WEST. For RX walls, local +y points NORTH.
    def cy(y0, y1): return (y0 + y1) / 2
    y_ex = yP1 + p['R1EXIT_FROM_S'] + p['R1EXIT_W']/2
    opening_door("DOOR_R1_EXIT", ((xR1E+xK0)/2, y_ex), RY, TI, p['R1EXIT_W'], p['DOOR_H'], -1, "CONFIRMED",
                 "2'2\" from passage-south line CONFIRMED; width 2'8\" PROVISIONAL; opens east into passage")
    opening_door("DOOR_KITCHEN", (xK0 + p['KG_W']/2, cy(yP0, yK1)), RX, TI, p['KG_W'], p['DOOR_H'], +1, "CONFIRMED",
                 "at west end of kitchen south wall CONFIRMED; width 3' PROVISIONAL")
    hg = xK0 + p['HALLGATE_X0'] + p['HALLGATE_W']/2
    opening_door("OPENING_HALL_GATE", (hg, cy(yH0, yP1)), RX, TE, p['HALLGATE_W'], p['DOOR_H'], 0, "CONFIRMED",
                 "5'8\" PLAN, open - no door CONFIRMED; position PROVISIONAL", leaf=False)
    opening_door("DOOR_B2", ((xB1+xR20)/2, -3.0), RY, TI, p['BATH_DOOR_W'], p['DOOR_H'], +1, "PLAN",
                 "on Bath2 east wall PLAN; size/position PROVISIONAL; swings into bathroom")
    opening_door("DOOR_R2_EXIT2", ((xB1+xR20)/2, cy(yP0, yP1)), RY, TI, p['ROOM_DOOR_W'], p['DOOR_H'], -1, "PLAN",
                 "Room2 -> passage PLAN; size PROVISIONAL; swings into Room 2")
    p2y = yH0 - p['P2_FROM_N']
    opening_door("DOOR_R2_EXIT1", ((xB1+xR20)/2, p2y), RY, TI, p['ROOM_DOOR_W'], p['DOOR_H'], -1, "PLAN",
                 "Room2 -> hall PLAN; aligned with Pillar 2 PROVISIONAL")
    opening_door("DOOR_B1", ((xB1_0 + xH1)/2, yB1n + TI/2), RX, TI, p['BATH_DOOR_W'], p['DOOR_H'], -1, "PLAN",
                 "Bath1 north wall PLAN; swings into bathroom PROVISIONAL")
    opening_door("DOOR_STAIR", ((xSw0+xSt0)/2, yR2w - 2.0), RY, TI, p['ROOM_DOOR_W'], p['DOOR_H'], -1, "PLAN",
                 "stair door faces west PLAN; position PROVISIONAL; external access route")
    bo = yP1 + p['BAL_OPEN_FROM_S'] + p['BAL_OPEN_W']/2
    opening_door("OPENING_BALCONY", (xW/2, bo), RY, p['T_BAL'], p['BAL_OPEN_W'], p['DOOR_H'], 0, "CONFIRMED",
                 "opening only, no door yet CONFIRMED; 19\" from south CONFIRMED; width 6' PROVISIONAL", leaf=False)
    # thresholds where floor level changes
    for n, (x0, x1, y0, y1) in {"THRESHOLD_B2": (xB1, xR20, -3.0 - 1.25, -3.0 + 1.25),
                                "THRESHOLD_B1": ((xB1_0+xH1)/2 - 1.25, (xB1_0+xH1)/2 + 1.25, yB1n, yB1n + TI),
                                "THRESHOLD_BALCONY": (xW, 0, bo - 3, bo + 3)}.items():
        box(n, x0, x1, y0, y1, ZB, 0.5 * IN, C_F, M['thr'], "PROVISIONAL", "marks floor-level change")

    # windows
    S_, T_ = p['SILL'], p['SILL'] + p['WIN']; WB = "4'x4' opening CONFIRMED; sill 3' + position PROVISIONAL"
    opening_window("WINDOW_W1", (5.4, yN/2), RX, TE, p['WIN'], S_, T_, "CONFIRMED", WB)
    opening_window("WINDOW_W2", ((xK0+xK1)/2, yN/2), RX, TE, p['WIN'], S_, T_, "CONFIRMED", WB)
    opening_window("WINDOW_W3", ((xB0+xB1)/2, yN/2), RX, TE, 2.0, 5.0, 7.0, "PROVISIONAL", "bathroom 2'x2' PROVISIONAL")
    opening_window("WINDOW_W4", (xR20 + 0.46 * p['R2_WN'], yN/2), RX, TE, p['WIN'], S_, T_, "CONFIRMED", WB)
    opening_window("WINDOW_W7", (xH0 + 6.1, cy(ySo, yH1)), RX, TE, p['WIN'], S_, T_, "CONFIRMED", WB)
    opening_window("WINDOW_W9_PASSAGE_HALL", (xB1 - 2.05, cy(yH0, yP1)), RX, TE, 2.5, 3.5, 7.0, "CONFIRMED",
                   "internal hall<->passage window CONFIRMED; size PROVISIONAL")
    # W5/W6 on tapered east wall
    a = Vector((m(xR21S - xR21N), m(yR21 - 0), 0)).normalized()
    ang = math.atan2(a.y, a.x); nrm = Vector((-a.y, a.x, 0))   # -a.y>0 -> east
    if nrm.x < 0: nrm = -nrm
    for n, yc in (("WINDOW_W5", -7.4), ("WINDOW_W6", -16.2)):
        t = yc / yR21; xin = xR21N + (xR21S - xR21N) * t
        cx = xin + nrm.x * TE / 2 / FT * FT; cy_ = yc + nrm.y * TE / 2
        opening_window(n, (cx, cy_), ang, TE, p['WIN'], S_, T_, "CONFIRMED", WB)
    # W8: plan shows a window on the open-square south wall; wall is now a parapet (site video)
    note = box("NOTE_W8_REPLACED_BY_PARAPET", xR20 + 3, xR20 + 7, ySo, yH1, p['PARAPET_H'], p['PARAPET_H'] + 0.05, C_PR, M['cut'], "PROVISIONAL",
               "Plan W8 is on the open-square south wall; modelled as parapet+grill per site video. Confirm.")
    note.display_type = 'WIRE'; note.hide_render = True

    # vents (provisional, high level)
    vents = [("VENT_R1_N_1", (2.0, yN/2), RX, TE), ("VENT_R1_N_2", (9.5, yN/2), RX, TE),
             ("VENT_KIT_N", (xK0 + 0.9, yN/2), RX, TE), ("VENT_B2_N", (xB0 + 0.6, yN/2), RX, TE),
             ("VENT_R2_N_1", (xR20 + 2.0, yN/2), RX, TE), ("VENT_R2_N_2", (xR20 + 10.5, yN/2), RX, TE),
             ("VENT_HALL_S_1", (xH0 + 2.0, cy(ySo, yH1)), RX, TE), ("VENT_HALL_S_2", (xH0 + 11.0, cy(ySo, yH1)), RX, TE),
             ("VENT_HALL_S_3", (xH0 + 15.5, cy(ySo, yH1)), RX, TE), ("VENT_B1_W", (xB1_0 - TI/2, yH1 + 4.25), RY, TI)]
    for n, cen, r, t in vents:
        opening_window(n, cen, r, t, p['VENT'], p['VENT_Z'], p['VENT_Z'] + p['VENT'], "PROVISIONAL",
                       "high-level vent seen in site video; exact location PROVISIONAL", coll_=C_PR, cutc=C_VCUT, mullion=False)

    for w in WALLS:
        for nm, cc in (("Openings", C_CUT), ("Vents", C_VCUT)):
            md = w.modifiers.new(nm, 'BOOLEAN'); md.operation = 'DIFFERENCE'
            md.operand_type = 'COLLECTION'; md.collection = cc; md.solver = 'EXACT'

    # ============ PILLARS & BEAMS ============
    px = xK0 + p['HALLGATE_X0'] + p['HALLGATE_W']      # line of hall-gate east edge (your answer)
    p1y = yH0 - p['P1_FROM_N']
    for n, yy in (("PILLAR_2", p2y), ("PILLAR_1", p1y)):
        box(n, px - p['PIL_EW']/2, px + p['PIL_EW']/2, yy - p['PIL_NS']/2, yy + p['PIL_NS']/2, ZB, H, C_P, M['conc'],
            "PROVISIONAL", "rectangular per site video; on hall-gate east-edge line CONFIRMED; size & N-S position PROVISIONAL")
    zb0, zb1 = H - p['BEAM_DROP'], H
    bw = p['BEAM_W']
    box("BEAM_HALL_01_NS", px - bw/2, px + bw/2, yH1, yH0, zb0, zb1, C_B, M['conc'], "PROVISIONAL", "N-S beam over pillars; size PROVISIONAL")
    box("BEAM_HALL_02_EW_P2", xH0, xH1, p2y - bw/2, p2y + bw/2, zb0, zb1, C_B, M['conc'], "PROVISIONAL", "E-W beam through Pillar 2")
    box("BEAM_HALL_03_EW_P1", xH0, xSw0, p1y - bw/2, p1y + bw/2, zb0, zb1, C_B, M['conc'], "PROVISIONAL", "E-W beam through Pillar 1")

    # ============ CEILING SLAB ============
    roof = prism("SLAB_ROOF", foot, H, H + p['SLAB'], C_C, M['slab'], "PROVISIONAL", "10' ceiling + 5\" slab PROVISIONAL")
    cs = box("SLAB_CUT_OPENSQ_SKY", xR20 - 0.01, xE1 + 0.5, ySo - 0.5, ySt1, H - 0.5, H + 1.5, C_C, M['cut'], "CONFIRMED", "open to sky CONFIRMED")
    cw = box("SLAB_CUT_STAIRWELL", xSt0, xSt1, yR2w, ySt1, H - 0.5, H + 1.5, C_C, M['cut'], "PROVISIONAL", "stair opening; mumty above not modelled")
    for c in (cs, cw):
        c.display_type = 'WIRE'; c.hide_render = True
        md = roof.modifiers.new(c.name, 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = c; md.solver = 'EXACT'

    # ============ STAIR (dog-leg, provisional) ============
    n = p['N_RISERS']; half = n // 2; rise = (H + p['SLAB']) / n; tr = p['TREAD']
    xm = (xSt0 + xSt1) / 2
    st = empty("STAIR_01", (xSt0, yR2w, 0), 0, C_S, "PROVISIONAL",
               f"{n} risers x {rise*12:.1f}\", treads {tr*12:.0f}\", dog-leg, goes UP (direction PROVISIONAL)")
    y_top = yR2w
    # flight 1: east half, starts at north wall, rises southward
    for i in range(half):
        ya, yb = y_top - (i + 1) * tr, y_top - i * tr
        s = box(f"STAIR_01_F1_STEP_{i+1:02d}", xm + 0.05, xSt1, ya - p['NOSING'], yb, ZB if i == 0 else (i) * rise - 0.5, (i + 1) * rise, C_S, M['stair'], "PROVISIONAL")
    yl = y_top - half * tr
    land_z = half * rise
    box("STAIR_01_LANDING", xSt0, xSt1, ySt1 + 0.05, yl, land_z - p['STAIR_WAIST'] - 0.2, land_z, C_S, M['stair'], "PROVISIONAL", "landing")
    # flight 2: west half, from landing rising northward
    for j in range(half):
        ya, yb = yl + j * tr, yl + (j + 1) * tr
        zt = land_z + (j + 1) * rise
        box(f"STAIR_01_F2_STEP_{j+1:02d}", xSt0, xm - 0.05, ya, yb + p['NOSING'], zt - rise, zt, C_S, M['stair'], "PROVISIONAL")
    # waist slabs (inclined) under flights
    bar_between("STAIR_01_F1_WAIST", (xm + 0.05 + (xSt1 - xm)/2, y_top, 0.2), ((xm + xSt1)/2 + 0.02, yl, land_z - 0.5), xSt1 - xm - 0.05, p['STAIR_WAIST'], C_S, M['stair'], "PROVISIONAL")
    bar_between("STAIR_01_F2_WAIST", ((xSt0 + xm)/2, yl, land_z - 0.6), ((xSt0 + xm)/2, y_top, H - 0.4), xm - xSt0 - 0.05, p['STAIR_WAIST'], C_S, M['stair'], "PROVISIONAL")
    # mid wall between flights + handrails
    box("STAIR_01_MID_WALL", xm - 0.2, xm + 0.2, yl, y_top, ZB, 3.0, C_S, M['wall'], "PROVISIONAL", "low divider between flights")
    hr = 3.0
    bar_between("STAIR_01_HANDRAIL_F1", (xm + 0.1, y_top, hr + rise), (xm + 0.1, yl, land_z + hr), 0.12, 0.12, C_S, M['steel'], "PROVISIONAL")
    bar_between("STAIR_01_HANDRAIL_F2", (xm - 0.1, yl, land_z + hr), (xm - 0.1, y_top, H + p['SLAB'] + hr), 0.12, 0.12, C_S, M['steel'], "PROVISIONAL")
    bpy.context.view_layer.update()
    for o in list(C_S.objects):
        if o is not st and o.parent is None:
            o.parent = st; o.matrix_parent_inverse = st.matrix_world.inverted()

    # ============ BALCONY ============
    bx0 = xW - p['BAL_D']; by1 = yN; by0 = yN - p['BAL_L']
    box("BALCONY_FLOOR", bx0, xW, by0, by1, ZB - p['FLOOR_SLAB'], -p['BAL_DROP'], C_BA, mat("Floor_BALCONY", (0.8, 0.62, 0.42, 1)),
        "PLAN", "3'6\" x 14'8\" PLAN; aligned to north face PROVISIONAL; 2\" drop PROVISIONAL")
    box("BALCONY_EDGE_CURB", bx0, bx0 + 0.4, by0, by1, -p['BAL_DROP'], 0.35, C_BA, M['wall'], "PROVISIONAL", "small upstand")
    rz = 0.35; rh = p['RAIL_H'] - rz
    railing_mesh("BALCONY_RAILING_W", (bx0 + 0.2, by0 + 0.1), (bx0 + 0.2, by1 - 0.1), rz, rh, C_BA, M['steel'], "CONFIRMED", "railing CONFIRMED; height PROVISIONAL")
    railing_mesh("BALCONY_RAILING_N", (bx0 + 0.2, by1 - 0.1), (xW - 0.05, by1 - 0.1), -p['BAL_DROP'], p['RAIL_H'], C_BA, M['steel'], "CONFIRMED", "")
    railing_mesh("BALCONY_RAILING_S", (bx0 + 0.2, by0 + 0.1), (xW - 0.05, by0 + 0.1), -p['BAL_DROP'], p['RAIL_H'], C_BA, M['steel'], "CONFIRMED", "")

    # ============ LABELS ============
    def label(txt, x, y, size=1.0):
        cu = bpy.data.curves.new("LBL", 'FONT'); cu.body = txt; cu.size = m(size); cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        o = bpy.data.objects.new("LBL_" + txt.split("\n")[0].replace(" ", "_"), cu); o.location = V(x, y, H + 2.5)
        o.data.materials.append(M['lab']); C_L.objects.link(o); return o
    def cen(pts): return sum(q[0] for q in pts)/len(pts), sum(q[1] for q in pts)/len(pts)
    for k, t, s in (("R1", "ROOM 1\n12'7\" x 12'6\"", 1.0), ("KIT", "KITCHEN\n7' x 7'1\"", 0.8), ("B2", "BATH 2\n4'5\" x 7'1\"", 0.7),
                    ("PAS", "PASSAGE 5'", 0.8), ("R2", "ROOM 2\n12'7\"-10'6\" x 23'7\"", 1.0), ("B1", "BATH 1\n4' x 8'6\"", 0.7),
                    ("STAIR", "STAIR", 0.9)):
        label(t, *cen(rooms[k][0]), s)
    label("HALL\n21' x 32'", xH0 + 6, yH0 - 22, 1.3)
    label("OPEN SQUARE\n(open to sky)", *cen(os_pts), 0.9)
    label("BALCONY", (bx0 + xW)/2, -6, 0.6).rotation_euler.z = math.pi/2
    label("N", 17, 4.5, 2.2)

    # ============ REFERENCE IMAGE ============
    sx, sy = 24.833/930, 45.25/1035; k = 2000/2470
    if os.path.exists(PLAN_IMAGE):
        img = bpy.data.images.load(PLAN_IMAGE, check_existing=True)
        if not img.packed_file: img.pack()
        Wp, Hp = img.size; wft, hft = Wp*k*sx, Hp*k*sy
        cx0 = -390*sx + wft/2; cy0 = 130*sy - hft/2
        pm = bpy.data.materials.get("PlanImage") or bpy.data.materials.new("PlanImage"); pm.use_nodes = True; nt = pm.node_tree
        tex = next((nd for nd in nt.nodes if nd.type == 'TEX_IMAGE'), None) or nt.nodes.new("ShaderNodeTexImage"); tex.image = img
        bsdf = nt.nodes.get("Principled BSDF"); nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        for nm, off, z, hide in (("PLAN_REFERENCE", 60.0, 0.02, False), ("PLAN_REFERENCE_OVERLAY", 0.0, H + 2.4, True)):
            me = bpy.data.meshes.new(nm)
            me.from_pydata([(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0)], [], [(0, 1, 2, 3)])
            uvl = me.uv_layers.new()
            for i, uvc in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uvl.data[i].uv = uvc
            o = bpy.data.objects.new(nm, me); o.location = V(cx0 + off, cy0, z); o.scale = (m(wft), m(hft), 1)
            o.data.materials.append(pm); C_R.objects.link(o); tag(o, "REFERENCE", "original plan - NOT to scale")
            o.hide_viewport = hide; o.hide_render = hide

    # ============ CAMERAS ============
    def cam(nm, loc, look, lens=35, ortho=None, res=(1600, 1000), top=False):
        cd = bpy.data.cameras.new(nm); o = bpy.data.objects.new(nm, cd); C_CAM.objects.link(o)
        o.location = V(*loc); cd.clip_end = 500; cd.clip_start = 0.05
        if top: o.rotation_euler = (0, 0, 0)
        else: o.rotation_euler = (V(*look) - o.location).to_track_quat('-Z', 'Y').to_euler()
        if ortho: cd.type = 'ORTHO'; cd.ortho_scale = m(ortho)
        else: cd.lens = lens
        o["res"] = res; return o
    cxm, cym = (xW - p['BAL_D'] + xE1)/2, (yN + ySo)/2
    cam("CAM_TOP_ORTHO", (cxm, cym, 150), None, ortho=54, res=(1400, 1400), top=True)
    cam("CAM_TOP_COMPARE", (cxm + 30, cym, 150), None, ortho=116, res=(2400, 1150), top=True)
    cam("CAM_EXTERIOR", (-38, -88, 42), (17, -22, 3), 30)
    cam("CAM_HALL", (4.6, -44.5, 5.2), (21, -16, 5.0), 16)
    cam("CAM_ROOM1", (11.9, -11.8, 5.2), (1.5, -3.0, 4.5), 16)
    cam("CAM_ROOM2", (26.0, -23.0, 5.2), (34, -1, 5.0), 16)
    cam("CAM_STAIR_OPENSQ", (34.6, -44.6, 5.4), (29.5, -26, 6.0), 16)
    sc.camera = bpy.data.objects["CAM_TOP_ORTHO"]

    # ============ LOOK ============
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
    sh.show_shadows = True; sh.shadow_intensity = 0.35; sh.show_cavity = True; sh.cavity_type = 'WORLD'
    scr = bpy.context.screen
    if scr:
        for ar in scr.areas:
            if ar.type == 'VIEW_3D':
                s3 = ar.spaces.active; s3.shading.type = 'SOLID'; s3.shading.color_type = 'MATERIAL'; s3.clip_end = 1000
    lc = bpy.context.view_layer.layer_collection.children["01_WALLS"]
    lc.children["_OPENING_CUTTERS"].hide_viewport = True; lc.children["_VENT_CUTTERS"].hide_viewport = True
    return d

if __name__ == "__main__":
    run()
