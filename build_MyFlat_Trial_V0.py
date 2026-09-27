# MyFlat_Trial_V0 - parametric build script (Blender 4.x/5.x)
# All dimensions are in FEET in the P table below. Edit a value and re-run this
# script (Text Editor > Run Script) to rebuild the whole model.
# Sources: PLAN = written on the floor plan, ANSWER = your checklist answers,
#          ASSUMED = provisional value chosen for the trial (see TRIAL_ASSUMPTIONS).
import bpy, bmesh, math, os
from mathutils import Vector

FT = 0.3048
PLAN_IMAGE = os.path.join(os.path.expanduser("~"), "Documents", "MyFlat", "floorplan_reference.png")

P = dict(
    # --- walls / heights ---
    T_EXT=9/12,        # ASSUMED external wall
    T_INT=5/12,        # ASSUMED internal wall
    T_BAL=15/12,       # ANSWER  Room1<->balcony wall = 15"
    CEIL_H=10.0,       # ASSUMED floor-to-ceiling
    SLAB=5/12,         # ASSUMED roof slab thickness
    DOOR_H=7.0,        # ASSUMED
    # --- north row ---
    R1_W=12+7/12,      # PLAN/ANSWER Room 1 clear E-W ("livable")
    K_D=7+1/12,        # PLAN kitchen N-S
    PAS_W=5.0,         # PLAN passage N-S
    KG_W=3.0,          # ASSUMED kitchen gate width
    K_EXTRA=4.0,       # ANSWER kitchen width = gate + 4'
    B2_W=4+5/12,       # ANSWER bathroom 2 width ~4'5"
    R2_WN=12+7/12,     # PLAN Room 2 width at north
    R2_WS=10.5,        # PLAN Room 2 width at south (narrows - ANSWER)
    R2_D=23+7/12,      # ANSWER Room 2 N-S total 23'7"
    # --- hall block ---
    HALL_W=21.0,       # PLAN
    HALL_D=32.0,       # PLAN
    BUMP_W=3.5,        # ASSUMED hall strip east of Room2-west-wall line leading to stair door
    STAIR_D=10+5/12,   # ASSUMED stair room N-S (incl. to openway)
    B1_W=4.0,          # PLAN bath1 E-W (orientation ASSUMED)
    B1_D=8.5,          # PLAN bath1 N-S
    # --- balcony ---
    BAL_D=3.5,         # PLAN 3'6"
    BAL_L=14+8/12,     # PLAN 14'8" (aligned to north face - ASSUMED)
    RAIL_H=3.25,       # ASSUMED railing height
    # --- openings ---
    WIN=4.0, SILL=3.0,                 # ANSWER all room windows 4'x4'; sill ASSUMED
    R1EXIT_FROM_S=2+2/12, R1EXIT_W=2+8/12,  # ANSWER 2'2" from passage-south line; width ASSUMED
    BAL_OPEN_FROM_S=19/12, BAL_OPEN_W=6.0,  # ANSWER 19" ; width ASSUMED
    HALLGATE_W=5+8/12,                 # PLAN/ANSWER open, no door
    HALLGATE_X0=1.9,                   # ASSUMED gate west edge offset from passage west end
    ROOM_DOOR_W=3.0, BATH_DOOR_W=2.5,  # ASSUMED
    PILLAR_D=15/12,                    # ASSUMED round pillars
    P2_FROM_N=7.5, P1_FROM_N=16.5,     # ASSUMED distances from hall north face
)
def build():
    p = P
    TE, TI = p['T_EXT'], p['T_INT']
    H = p['CEIL_H']
    # ---------- derived plan coordinates (ft). x=0 Room1 west inner face, y=0 north inner face
    xR1E = p['R1_W']; xK0 = xR1E + TI; K_W = p['KG_W'] + p['K_EXTRA']; xK1 = xK0 + K_W
    xB0 = xK1 + TI; xB1 = xB0 + p['B2_W']; xR20 = xB1 + TI
    xR21N = xR20 + p['R2_WN']; xR21S = xR20 + p['R2_WS']
    yK1 = -p['K_D']; yP0 = yK1 - TI; yP1 = yP0 - p['PAS_W']
    yH0 = yP1 - TE; yH1 = yH0 - p['HALL_D']; ySo = yH1 - TE
    xH1 = xB1; xH0 = xH1 - p['HALL_W']
    yR21 = -p['R2_D']; yR2w = yR21 - TI
    xSw0 = xH1 + p['BUMP_W']; xSt0 = xSw0 + TI; xSt1 = xR21S
    ySt1 = yR2w - p['STAIR_D']; yBump = ySt1 + TI
    yB1n = yH1 + p['B1_D']; xB1_0 = xH1 - p['B1_W']
    xE1 = xR21S + TE
    D = dict(locals()); D.pop('p')
    return D

def m(v): return v * FT

def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(blk):
            if d.users == 0: blk.remove(d)

COLL = {}
def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent.children if parent else bpy.context.scene.collection.children).link(c)
    COLL[name] = c; return c

MATS = {}
def mat(name, rgba, rough=0.8):
    if name in MATS: return MATS[name]
    mt = bpy.data.materials.new(name); mt.use_nodes = True
    b = mt.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = rgba
        b.inputs["Roughness"].default_value = rough
        if rgba[3] < 1: b.inputs["Alpha"].default_value = rgba[3]
    mt.diffuse_color = rgba
    MATS[name] = mt; return mt

def tag(o, src, note=""):
    o["source"] = src
    if note: o["note"] = note

def prism(name, pts, z0, z1, c, mt, src="PLAN", note=""):
    """pts in ft (2D), z in ft. Object origin at footprint centre."""
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
    o = bpy.data.objects.new(name, me); o.location = (m(cx), m(cy), m(z0))
    o.data.materials.append(mt); c.objects.link(o); tag(o, src, note); return o

def box(name, x0, x1, y0, y1, z0, z1, c, mt, src="PLAN", note=""):
    return prism(name, [(x0,y0),(x1,y0),(x1,y1),(x0,y1)], z0, z1, c, mt, src, note)

def run():
    clear()
    d = build(); p = P; g = d.get
    TE, TI, H = p['T_EXT'], p['T_INT'], p['CEIL_H']
    sc = bpy.context.scene
    sc.unit_settings.system = 'IMPERIAL'; sc.unit_settings.length_unit = 'ADAPTIVE'

    A = coll("01_ARCHITECTURE"); Wc = coll("Walls", A); Fc = coll("Floors", A); Cc = coll("Ceilings", A)
    Bc = coll("Balcony", A); CUT = coll("OPENING_CUTTERS", A)
    DO = coll("02_DOORS"); WI = coll("03_WINDOWS"); PI = coll("04_PILLARS"); ST = coll("05_STAIRS")
    RF = coll("06_REFERENCE"); LB = coll("Labels", RF); CAM = coll("Cameras", RF); PH = coll("07_PLACEHOLDERS")

    wall_m = mat("Wall_White", (0.92, 0.91, 0.88, 1)); slab_m = mat("Slab_Grey", (0.55, 0.55, 0.55, 1))
    ceil_m = mat("Ceiling", (0.97, 0.97, 0.97, 1)); door_m = mat("Door_Wood", (0.55, 0.36, 0.2, 1))
    glass_m = mat("Glass", (0.55, 0.78, 0.95, 0.35), 0.1); pil_m = mat("Pillar", (0.3, 0.33, 0.38, 1))
    stair_m = mat("Stair_PLACEHOLDER", (0.95, 0.6, 0.2, 1)); rail_m = mat("Railing", (0.2, 0.2, 0.22, 1))
    cut_m = mat("Cutter", (1, 0, 0, 0.3)); lab_m = mat("Label", (0.05, 0.05, 0.05, 1))
    ground_m = mat("Ground", (0.62, 0.66, 0.58, 1))
    room_cols = {"Room1": (0.93, 0.85, 0.7, 1), "Kitchen": (0.8, 0.9, 0.72, 1), "Bathroom2": (0.72, 0.84, 0.95, 1),
                 "Passage": (0.9, 0.88, 0.8, 1), "Room2": (0.95, 0.8, 0.72, 1), "Hall": (0.93, 0.9, 0.82, 1),
                 "Bathroom1": (0.72, 0.84, 0.95, 1), "Stair": (0.85, 0.8, 0.9, 1), "OpenSquare": (0.6, 0.6, 0.6, 1),
                 "Balcony": (0.8, 0.62, 0.42, 1)}

    xR1E, xK0, xK1, xB0, xB1, xR20 = g('xR1E'), g('xK0'), g('xK1'), g('xB0'), g('xB1'), g('xR20')
    xR21N, xR21S, yK1, yP0, yP1, yH0, yH1, ySo = g('xR21N'), g('xR21S'), g('yK1'), g('yP0'), g('yP1'), g('yH0'), g('yH1'), g('ySo')
    xH0, xH1, yR21, yR2w, xSw0, xSt0, xSt1 = g('xH0'), g('xH1'), g('yR21'), g('yR2w'), g('xSw0'), g('xSt0'), g('xSt1')
    ySt1, yBump, yB1n, xB1_0, xE1 = g('ySt1'), g('yBump'), g('yB1n'), g('xB1_0'), g('xE1')
    xW = -p['T_BAL']; yN = TE

    # ---------------- rooms (clear floor polygons) ----------------
    rooms = {
        "Room1": [(0,0),(xR1E,0),(xR1E,yP1),(0,yP1)],
        "Kitchen": [(xK0,0),(xK1,0),(xK1,yK1),(xK0,yK1)],
        "Bathroom2": [(xB0,0),(xB1,0),(xB1,yK1),(xB0,yK1)],
        "Passage": [(xK0,yP0),(xB1,yP0),(xB1,yP1),(xK0,yP1)],
        "Room2": [(xR20,0),(xR21N,0),(xR21S,yR21),(xR20,yR21)],
        "Hall": [(xH0,yH0),(xH1,yH0),(xH1,yR2w),(xSw0,yR2w),(xSw0,yBump),(xH1,yBump),(xH1,yB1n+TI),(xB1_0-TI,yB1n+TI),(xB1_0-TI,yH1),(xH0,yH1)],
        "Bathroom1": [(xB1_0,yB1n),(xH1,yB1n),(xH1,yH1),(xB1_0,yH1)],
        "Stair": [(xSt0,yR2w),(xSt1,yR2w),(xSt1,ySt1),(xSt0,ySt1)],
        "OpenSquare": [(xR20,ySt1),(xSt1,ySt1),(xSt1,yH1),(xR20,yH1)],
    }
    for n, pts in rooms.items():
        src = "ASSUMED" if n in ("Stair", "OpenSquare", "Kitchen") else "PLAN"
        prism(f"FLOOR_{n}", pts, 0, 0.02, Fc, mat(f"Floor_{n}", room_cols[n]), src)
        if n not in ("OpenSquare", "Stair"):   # open square = open to sky; stairwell left open
            prism(f"CEIL_{n}", pts, H, H + p['SLAB'], Cc, ceil_m, "ASSUMED", "ceiling height assumed")
    prism("SLAB_Base", [(xW,yN),(xR21N+TE,yN),(xE1,yR2w),(xE1,ySo),(xH0-TE,ySo),(xH0-TE,yH0),(xW,yH0)], -1.0, 0, A, slab_m, "ASSUMED")
    ground = box("GROUND_Context", -40, 80, -90, 40, -1.05, -1.0, RF, ground_m, "REFERENCE"); ground.hide_select = True

    # ---------------- walls ----------------
    W = []
    def wall(n, x0, x1, y0, y1, src="PLAN", note=""):
        o = box("WALL_" + n, x0, x1, y0, y1, 0, H, Wc, wall_m, src, note); W.append(o); return o
    wall("North_Ext", xW, xR21N + TE, 0, yN, "ASSUMED", "thickness 9in assumed")
    wall("Room1_West_Balcony_15in", xW, 0, yH0, yN, "ANSWER", "15in wall confirmed")
    wall("Room1_South_Ext", xW, xK0, yH0, yP1, "ASSUMED", "aligned with passage south wall (ANSWER G3)")
    wall("Passage_South", xK0, xB1, yH0, yP1, "ASSUMED", "thickness 9in assumed to align with Room1 south")
    wall("Room1_East", xR1E, xK0, yP1, 0)
    wall("Kitchen_Bath2_South", xK0, xB1, yP0, yK1)
    wall("Kitchen_Bath2_Partition", xK1, xB0, yK1, 0, "ASSUMED")
    wall("Room2_West", xB1, xR20, yR2w, 0)
    wall("Room2_South", xR20, xR21S + 0.3, yR2w, yR21)
    o = prism("WALL_East_Room2_Tapered", [(xR21N,0),(xR21N+TE,0),(xR21N+TE,yN),(xR21N,yN)][:0] or
              [(xR21N,yN),(xR21N+TE,yN),(xE1,yR2w),(xR21S,yR2w)], 0, H, Wc, wall_m, "ASSUMED",
              "Room2 narrows 12'7\" -> 10'6\" (ANSWER G1); taper on east wall ASSUMED"); W.append(o)
    wall("East_Ext_Lower", xR21S, xE1, ySo, yR2w, "ASSUMED")
    wall("Hall_West_Ext", xH0 - TE, xH0, ySo, yH0, "PLAN", "position from HALL_W=21ft")
    wall("South_Ext", xH0 - TE, xE1, ySo, yH1)
    wall("Stair_West", xSw0, xSt0, ySt1, yR2w, "ASSUMED", "stair moved west (ANSWER G7)")
    wall("HallStrip_South", xH1, xSt0, ySt1, yBump, "ASSUMED")
    wall("OpenSquare_West", xH1, xR20, yH1, ySt1)
    wall("Bath1_North", xB1_0 - TI, xH1, yB1n, yB1n + TI)
    wall("Bath1_West", xB1_0 - TI, xB1_0, yH1, yB1n + TI)

    # ---------------- openings: cutters + leaves/glass ----------------
    E = 0.25
    def cutter(n, x0, x1, y0, y1, z0, z1, src, note=""):
        o = box("CUT_" + n, x0, x1, y0, y1, z0, z1, CUT, cut_m, src, note)
        o.display_type = 'WIRE'; o.hide_render = True; return o

    def door(n, axis, a0, a1, wx0, wx1, swing, src="ASSUMED", note="", leaf=True, z1=None):
        z1 = z1 or p['DOOR_H']; w = a1 - a0
        if axis == 'Y':   # wall runs N-S, wall spans x wx0..wx1, opening along y a0..a1
            cutter(n, wx0 - E, wx1 + E, a0, a1, 0, z1, src, note)
            if leaf:
                x0, x1 = (wx1, wx1 + w) if swing == 'E' else (wx0 - w, wx0)
                box("DOOR_" + n, x0, x1, a0, a0 + 0.13, 0, z1 - 0.05, DO, door_m, "ASSUMED", "leaf/swing assumed")
        else:             # wall runs E-W, spans y wx0..wx1, opening along x
            cutter(n, a0, a1, wx0 - E, wx1 + E, 0, z1, src, note)
            if leaf:
                y0, y1 = (wx1, wx1 + w) if swing == 'N' else (wx0 - w, wx0)
                box("DOOR_" + n, a0, a0 + 0.13, y0, y1, 0, z1 - 0.05, DO, door_m, "ASSUMED", "leaf/swing assumed")

    def window(n, axis, a0, a1, wx0, wx1, sill, top, src="ANSWER", note=""):
        if axis == 'Y':
            cutter(n, wx0 - E, wx1 + E, a0, a1, sill, top, src, note)
            mid = (wx0 + wx1) / 2; box("WIN_" + n, mid - 0.04, mid + 0.04, a0, a1, sill, top, WI, glass_m, src, note)
        else:
            cutter(n, a0, a1, wx0 - E, wx1 + E, sill, top, src, note)
            mid = (wx0 + wx1) / 2; box("WIN_" + n, a0, a1, mid - 0.04, mid + 0.04, sill, top, WI, glass_m, src, note)

    y_ex0 = yP1 + p['R1EXIT_FROM_S']
    door("Room1_Exit", 'Y', y_ex0, y_ex0 + p['R1EXIT_W'], xR1E, xK0, 'E', "ANSWER", "2'2\" from passage south wall; width assumed")
    door("Kitchen_Gate", 'X', xK0, xK0 + p['KG_W'], yP0, yK1, 'N', "ANSWER", "at west end of kitchen south wall")
    hg0 = xK0 + p['HALLGATE_X0']
    door("Hall_Gate_OPEN", 'X', hg0, hg0 + p['HALLGATE_W'], yH0, yP1, 'S', "PLAN", "open, no door", leaf=False)
    door("Bath2", 'Y', -4.25, -4.25 + p['BATH_DOOR_W'], xB1, xR20, 'W', "ASSUMED", "on Bath2 east wall, into Room2")
    door("Room2_Exit2_Passage", 'Y', -11.5, -11.5 + p['ROOM_DOOR_W'], xB1, xR20, 'E', "ASSUMED")
    pil2_y = yH0 - p['P2_FROM_N']
    door("Room2_Exit1_Hall", 'Y', pil2_y - 1.5, pil2_y + 1.5, xB1, xR20, 'E', "ASSUMED", "aligned with Pillar 2")
    bd0 = (xB1_0 + xH1) / 2 - p['BATH_DOOR_W'] / 2
    door("Bath1", 'X', bd0, bd0 + p['BATH_DOOR_W'], yB1n, yB1n + TI, 'S', "ASSUMED", "north wall, opens to hall")
    door("Stair_Door", 'Y', yR2w - 3.5, yR2w - 0.5, xSw0, xSt0, 'E', "ASSUMED", "west wall of stair room")
    bo0 = yP1 + p['BAL_OPEN_FROM_S']
    door("Balcony_OPEN", 'Y', bo0, bo0 + p['BAL_OPEN_W'], xW, 0, 'W', "ANSWER", "opening only for now", leaf=False)

    S, T = p['SILL'], p['SILL'] + p['WIN']
    window("W1_Room1", 'X', 3.4, 3.4 + p['WIN'], 0, yN, S, T)
    kc = (xK0 + xK1) / 2; window("W2_Kitchen", 'X', kc - 2, kc + 2, 0, yN, S, T)
    bc = (xB0 + xB1) / 2; window("W3_Bath2_ASSUMED_2x2", 'X', bc - 1, bc + 1, 0, yN, 5.0, 7.0, "ASSUMED", "bath vent 2x2 assumed")
    rc = xR20 + 0.46 * p['R2_WN']; window("W4_Room2", 'X', rc - 2, rc + 2, 0, yN, S, T)
    window("W7_Hall", 'X', xH0 + 4.1, xH0 + 8.1, yH1 - TE, yH1, S, T)
    oc = (xR20 + xSt1) / 2; window("W8_OpenSquare", 'X', oc - 2, oc + 2, yH1 - TE, yH1, S, T)
    window("W9_Passage_Hall_internal", 'X', xB1 - 3.3, xB1 - 0.8, yH0, yP1, 3.5, 7.0, "ANSWER", "white diamond = window between hall and passage; size assumed")
    # W5/W6 on tapered east wall -> rotated cutters
    ang = math.atan2(yR2w - yN, xE1 - (xR21N + TE))
    for n, yc in (("W5_Room2", -7.4), ("W6_Room2", -16.2)):
        t = (yc - 0) / (yR21 - 0); xin = xR21N + (xR21S - xR21N) * t
        cx = xin + TE / 2
        c = box("CUT_" + n, -0.9, 0.9, -p['WIN']/2, p['WIN']/2, S, T, CUT, cut_m, "ANSWER"); c.display_type = 'WIRE'; c.hide_render = True
        c.location.x += m(cx); c.location.y += m(yc); c.rotation_euler.z = ang - math.radians(-90)
        gl = box("WIN_" + n, -0.04, 0.04, -p['WIN']/2, p['WIN']/2, S, T, WI, glass_m, "ANSWER")
        gl.location.x += m(cx); gl.location.y += m(yc); gl.rotation_euler.z = ang - math.radians(-90)
    for o in W:
        md = o.modifiers.new("Openings", 'BOOLEAN'); md.operation = 'DIFFERENCE'
        md.operand_type = 'COLLECTION'; md.collection = CUT; md.solver = 'EXACT'

    # ---------------- pillars ----------------
    px = hg0 + p['HALLGATE_W']
    for n, yy in (("Pillar2_North", pil2_y), ("Pillar1_South", yH0 - p['P1_FROM_N'])):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=m(p['PILLAR_D']/2), depth=m(H), location=(m(px), m(yy), m(H/2)))
        o = bpy.context.active_object; o.name = n
        for c in o.users_collection: c.objects.unlink(o)
        PI.objects.link(o); o.data.materials.append(pil_m)
        tag(o, "ASSUMED", "on line of Hall Gate east edge (ANSWER); size & N-S position assumed")

    # ---------------- stairs (placeholder dog-leg, 16 risers) ----------------
    n_r = 8; rise = H / (2 * n_r); tread = 10/12
    xm = (xSt0 + xSt1) / 2
    for i in range(n_r):
        box(f"STAIR_F1_Step{i+1:02d}_ASSUMED", xm, xSt1, yR2w - (i+1)*tread, yR2w - i*tread, 0, (i+1)*rise, ST, stair_m, "ASSUMED")
    yl0 = yR2w - n_r*tread
    box("STAIR_Landing_ASSUMED", xSt0, xSt1, yl0 - 3.0, yl0, n_r*rise - 0.5, n_r*rise, ST, stair_m, "ASSUMED")
    for j in range(n_r):
        zt = n_r*rise + (j+1)*rise
        box(f"STAIR_F2_Step{j+1:02d}_ASSUMED", xSt0, xm, yl0 + j*tread, yl0 + (j+1)*tread, zt - 0.5, zt, ST, stair_m, "ASSUMED")

    # ---------------- balcony ----------------
    bx0 = xW - p['BAL_D']; by1 = yN; by0 = yN - p['BAL_L']
    box("BALCONY_Floor", bx0, xW, by0, by1, -0.25, 0.0, Bc, mat("Floor_Balcony", room_cols["Balcony"]), "PLAN", "3'6\" x 14'8\"")
    box("BALCONY_Railing_West", bx0, bx0 + 0.15, by0, by1, 0, p['RAIL_H'], Bc, rail_m, "ASSUMED", "railing height assumed")
    box("BALCONY_Railing_North", bx0, xW, by1 - 0.15, by1, 0, p['RAIL_H'], Bc, rail_m, "ASSUMED")
    box("BALCONY_Railing_South", bx0, xW, by0, by0 + 0.15, 0, p['RAIL_H'], Bc, rail_m, "ASSUMED")

    # ---------------- labels ----------------
    def label(txt, x, y, size=1.1, c=LB):
        cu = bpy.data.curves.new("LBL_" + txt[:12], 'FONT'); cu.body = txt; cu.size = m(size)
        cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        o = bpy.data.objects.new("LBL_" + txt.split("\n")[0], cu); o.location = (m(x), m(y), m(H + 0.6))
        o.data.materials.append(lab_m); c.objects.link(o); return o
    def cen(pts): return sum(q[0] for q in pts)/len(pts), sum(q[1] for q in pts)/len(pts)
    names = {"Room1": "ROOM 1\n12'7\" x 12'6\"", "Kitchen": "KITCHEN\n7' x 7'1\"", "Bathroom2": "BATH 2\n4'5\" x 7'1\"",
             "Passage": "PASSAGE\n5'", "Room2": "ROOM 2\n12'7\"/10'6\" x 23'7\"", "Bathroom1": "BATH 1\n4' x 8'6\"",
             "Stair": "STAIR", "OpenSquare": "OPEN SQUARE\n(open to sky)"}
    for n, t in names.items():
        cx, cy = cen(rooms[n]); label(t, cx, cy, 0.9 if n in ("Bathroom1", "Bathroom2", "Kitchen") else 1.1)
    label("HALL\n21' x 32'", xH0 + 6, yH0 - 22, 1.3)
    label("BALCONY", (bx0 + xW)/2, -6, 0.7).rotation_euler.z = math.radians(90)
    lN = label("N  ^", 17, 5, 2.0)
    # assumption tags (orange) in placeholders
    am = mat("Assumption_Tag", (1.0, 0.45, 0.0, 1))
    for t, x, y in (("A-stair", xm, yR2w - 5), ("A-taper", xR21S + 0.5, yR21 + 3), ("A-pillars", px + 2, pil2_y),
                    ("A-hallW", xH0 + 2, yH0 - 2), ("A-kitchenW", xK0 + 3.5, -2)):
        o = label(t, x, y, 0.6, PH); o.data.materials[0] = am; o.location.z = m(H + 0.8)

    # ---------------- reference image ----------------
    sx, sy = 24.833/930, 45.25/1035          # ft per px, measured on the 2000-px-wide version
    k = 2000/2470                            # file is 2470 px wide
    if os.path.exists(PLAN_IMAGE):
        img = bpy.data.images.load(PLAN_IMAGE, check_existing=True); img.pack()
        W_px, H_px = img.size
        wft, hft = W_px*k*sx, H_px*k*sy
        cx0 = -390*sx + wft/2; cy0 = 130*sy - hft/2
        pm = bpy.data.materials.new("PlanImage"); pm.use_nodes = True; nt = pm.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
        bsdf = nt.nodes.get("Principled BSDF"); nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        em = bsdf.inputs.get("Emission Color")
        if em: nt.links.new(tex.outputs["Color"], em); bsdf.inputs["Emission Strength"].default_value = 1.0
        for nm, off, hide in (("PLAN_REFERENCE", 60.0, False), ("PLAN_REFERENCE_Overlay", 0.0, True)):
            bpy.ops.mesh.primitive_plane_add(size=1, location=(m(cx0 + off), m(cy0), m(-0.9 if hide else 0.02)))
            o = bpy.context.active_object; o.name = nm; o.scale = (m(wft), m(hft), 1)
            for c in o.users_collection: c.objects.unlink(o)
            RF.objects.link(o); o.data.materials.append(pm); o.hide_viewport = hide; o.hide_render = hide
            tag(o, "REFERENCE", "original plan, NOT to scale; stretched to match model extents")

    # ---------------- cameras ----------------
    def cam(n, loc, look, lens=35, ortho=None, res=(1600, 1000)):
        cd = bpy.data.cameras.new(n); o = bpy.data.objects.new(n, cd); CAM.objects.link(o)
        o.location = Vector([m(v) for v in loc])
        dvec = Vector([m(v) for v in look]) - o.location
        o.rotation_euler = dvec.to_track_quat('-Z', 'Y').to_euler()
        if ortho: cd.type = 'ORTHO'; cd.ortho_scale = m(ortho)
        else: cd.lens = lens
        cd.clip_end = 500; o["res"] = res; return o
    cx, cy = (xW - p['BAL_D'] + xE1)/2, (yN + ySo)/2
    t = cam("TOP_VIEW", (cx, cy, 150), (cx, cy + 0.001, 0), ortho=54, res=(1400, 1400))
    t.rotation_euler = (0, 0, 0)
    t2 = cam("TOP_VIEW_COMPARE", (cx + 30, cy, 150), (cx + 30, cy, 0), ortho=116, res=(2400, 1150))
    t2.rotation_euler = (0, 0, 0)
    cam("PERSP_Aerial_SE", (62, -80, 55), (18, -22, 0), 30)
    cam("PERSP_Aerial_NW", (-32, 38, 50), (18, -22, 0), 30)
    cam("PERSP_Hall_Interior", (4.8, -44.3, 5.2), (21, -16, 4.2), 18)
    cam("PERSP_Room2_Interior", (26.2, -22.8, 5.2), (34, 0, 4.5), 18)
    sc.camera = t

    # ---------------- look ----------------
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
    sh.show_shadows = True; sh.show_cavity = True; sh.cavity_type = 'WORLD'
    for a in bpy.context.screen.areas if bpy.context.screen else []:
        if a.type == 'VIEW_3D':
            s = a.spaces.active; s.shading.type = 'SOLID'; s.shading.color_type = 'MATERIAL'; s.clip_end = 1000
    bpy.context.view_layer.layer_collection.children["01_ARCHITECTURE"].children["OPENING_CUTTERS"].hide_viewport = True
    return d

if __name__ == "__main__":
    run()
