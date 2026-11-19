# MyFlat V2 - hall designs on the site-measured layout (14 Nov 2026).
# Hall: x 6.5 (west wall) .. 27.5, pillars x 18.67-19.92 at y -19.9 and -36.0, main door on the west wall y -24.61..-21.07,
# west-wall window y -41.2..-37.1, hall arch x 13.0-18.67. The TV wall moved to the west wall SOUTH of the main door.
# Was: MyFlat V1.3 - hall designs + flat-wide floor finishes (5 Nov 2026; main door + 4 options added the same day).
# Run with MyFlat_V1_2_Room2_Ensuite.blend open, then save as MyFlat_V1_3_Hall_Designs.blend:
#   exec(open(".../build_hall_designs.py").read()); run()
# Two options, each a collection with design_option set (exported together with a Room 1 design):
#   20_HALL_RECOMMENDED  (HALL_REC)    matt GVT 600x1200 floors, WPC fluted TV wall with metal frame + LED,
#                                      steel corner guards on pillars, downlights, sofa/dining layout
#   21_HALL_BUDGET       (HALL_BUDGET) double-charge 600x600 floors, plain painted walls, TV on wall + laminate shelf,
#                                      LED battens, simpler furniture
# Both: 4" tile skirting in the hall, anti-skid tiles in Bath 1 / Bath 2, Kota stone in the open square.
# Units: feet. Hall: x 3.83 (west wall inner face) .. 24.83, y -13.25/-15.25 (north) .. -45.25 (south), ceiling 10 ft,
# beams bottom at 9 ft (E-W beams at y -20.75 and -29.75), pillars at x 20.19-20.94.
import bpy, bmesh, math
import numpy as np
from mathutils import Vector

FT = 0.3048; H = 10.0
def m(v): return v * FT
OPT = None; COL = None; MATS = {}; TAG = {"HALL_REC": "HR", "HALL_BUDGET": "HB"}

# ---------------------------------------------------------------- textures (generated, packed into the .blend)
def _up(a, h, w):
    ys = np.linspace(0, a.shape[0] - 1, h); xs = np.linspace(0, a.shape[1] - 1, w)
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
    y1 = np.minimum(y0 + 1, a.shape[0] - 1); x1 = np.minimum(x0 + 1, a.shape[1] - 1)
    fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    return (a[y0][:, x0] * (1 - fy) * (1 - fx) + a[y1][:, x0] * fy * (1 - fx) + a[y0][:, x1] * (1 - fy) * fx + a[y1][:, x1] * fy * fx)

def tile_image(name, w, h, base, var=0.04, grout=(0.6, 0.58, 0.55), gpx=3, speck=0.0, veins=False, seed=1):
    old = bpy.data.images.get(name)
    if old: bpy.data.images.remove(old)
    rng = np.random.default_rng(seed)
    n = sum(_up(rng.random((max(2, h // s), max(2, w // s))), h, w) * (0.5 ** i) for i, s in enumerate((128, 48, 16)))
    n = (n - n.mean()) / (n.std() + 1e-6)
    rgb = np.ones((h, w, 3)) * np.array(base)[None, None, :] + n[..., None] * var
    if veins:
        yy, xx = np.mgrid[0:h, 0:w]
        for k in range(3):
            a, b, c = rng.uniform(-0.6, 0.6), rng.uniform(0, w), rng.uniform(20, 60)
            d = np.abs(yy - (a * (xx - b) + h * rng.uniform(0.2, 0.8) + 10 * np.sin(xx / c)))
            rgb -= (np.exp(-(d / 2.5) ** 2) * 0.045)[..., None]
    if speck:
        s = rng.random((h, w)) < speck
        rgb[s] *= rng.uniform(0.6, 0.85)
    rgb[:gpx, :, :] = grout; rgb[-gpx:, :, :] = grout; rgb[:, :gpx, :] = grout; rgb[:, -gpx:, :] = grout
    rgb = np.clip(rgb, 0, 1)
    rgba = np.concatenate([rgb, np.ones((h, w, 1))], axis=2).astype(np.float32)
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.pixels.foreach_set(rgba.ravel()); img.update(); img.pack()
    return img

def tex_mat(name, img, rough, swatch):
    key = f"{OPT}_{name}"
    if key in MATS: return MATS[key]
    mt = bpy.data.materials.new(key); mt.use_nodes = True
    nt = mt.node_tree; b = nt.nodes["Principled BSDF"]
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img
    nt.links.new(tn.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    mt.diffuse_color = (*swatch, 1)
    MATS[key] = mt; return mt

def mat(name, rgb, rough=0.6, metal=0.0, emit=0.0):
    key = f"{OPT}_{name}"
    if key in MATS: return MATS[key]
    mt = bpy.data.materials.new(key); mt.use_nodes = True
    b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    mt.diffuse_color = (*rgb, 1); MATS[key] = mt; return mt

# ---------------------------------------------------------------- geometry helpers
def _obj(name, me, mt, cat, spec, loc=(0, 0, 0)):
    o = bpy.data.objects.new(f"{TAG[OPT]}_{name}", me); o.location = Vector([m(v) for v in loc])
    if mt: o.data.materials.append(mt)
    COL.objects.link(o)
    o["design_category"] = cat; o["design_option"] = OPT; o["status"] = "DESIGN"
    if spec: o["spec"] = spec
    return o

def _bm_box(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new((m(a), m(b), m(c))) for a, b, c in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])

def boxes(name, bxs, mt, cat, spec="", props=None):
    """boxes in WORLD feet; object origin at the centre of the first box's base"""
    cx, cy = (bxs[0][0] + bxs[0][1]) / 2, (bxs[0][2] + bxs[0][3]) / 2
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for (a, b, c, d, e, f) in bxs: _bm_box(bm, a - cx, b - cx, c - cy, d - cy, e, f)
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (cx, cy, 0))
    for k, v in (props or {}).items(): o[k] = v
    return o
def box(name, x0, x1, y0, y1, z0, z1, mt, cat, spec="", props=None): return boxes(name, [(x0, x1, y0, y1, z0, z1)], mt, cat, spec, props)

def cyl(name, cx, cy, r, z0, z1, mt, cat, spec="", n=24, props=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=m(r), radius2=m(r), depth=m(z1 - z0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, m(z1 - z0) / 2)); bm.to_mesh(me); bm.free()
    o = _obj(name, me, mt, cat, spec, (cx, cy, z0))
    for k, v in (props or {}).items(): o[k] = v
    return o

def floor_overlay(name, src_name, mt, tile_u, tile_v, along_y, spec):
    """thin finish on the top face of an architecture floor, UV-mapped in world feet so the tile texture repeats"""
    src = bpy.data.objects.get(src_name)
    if not src: return None
    bm = bmesh.new(); bm.from_mesh(src.data); bm.transform(src.matrix_world)
    bm.normal_update()
    top = max(v.co.z for v in bm.verts)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if abs(f.normal.z) < 0.9 or abs(f.calc_center_median().z - top) > 1e-4], context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm, geom=loose, context='VERTS')
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    for v in bm.verts: v.co.z = top + m(0.006)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            x, y = l.vert.co.x / FT, l.vert.co.y / FT
            l[uv].uv = (y / tile_u, x / tile_v) if along_y else (x / tile_u, y / tile_v)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return _obj(name, me, mt, "finishes", spec)

def skirting(mt, spec):
    S = 0.33; T = 0.04
    runs = [(X, X + T, -45.25, MAIN_Y0), (X, X + T, MAIN_Y1, -15.25), (X, B1X, -45.25, -45.25 + T), (X, 13.0, -15.25 - T, -15.25),
            (PX1, XE_, -13.25 - T, -13.25),
            (XE_ - T, XE_, R2D_Y1, -13.25), (XE_ - T, XE_, -24.0, R2D_Y0)]
    return boxes("SKIRTING", [(a, b, c, d, 0.0, S) for a, b, c, d in runs], mt, "finishes", spec)

def ceiling_fan(z_hub=8.6, cx=12.67, cy=-30.1):
    M = mat("Fan_White", (0.92, 0.92, 0.9), 0.4)
    cyl("FAN_ROD", cx, cy, 0.05, z_hub + 0.3, H, M, "fixtures", "", 8)
    cyl("FAN_HUB", cx, cy, 0.35, z_hub, z_hub + 0.3, M, "fixtures", "BLDC ceiling fan 1200 mm (5-star, ~30 W)")
    bl = []
    for k in range(3):
        a = k * 2 * math.pi / 3; ux, uy = math.cos(a), math.sin(a)
        for s in range(6):
            r0 = 0.4 + s * 0.27
            bl.append((cx + ux * r0 - 0.14, cx + ux * r0 + 0.14, cy + uy * r0 - 0.14, cy + uy * r0 + 0.14, z_hub + 0.08, z_hub + 0.14))
    boxes("FAN_BLADES", bl, M, "fixtures", "fan blades")

def soften(o, w=0.6, seg=3):
    """rounded edges (w in inches); the GLB exporter applies modifiers"""
    if not o: return o
    b = o.modifiers.new("Soft", 'BEVEL'); b.width = m(w / 12); b.segments = seg; b.limit_method = 'ANGLE'
    b.use_clamp_overlap = True
    try: b.harden_normals = True
    except Exception: pass
    for p in o.data.polygons: p.use_smooth = True
    return o
def sbox(*a, w=0.6, seg=3, **k): return soften(box(*a, **k), w, seg)
def sboxes(*a, w=0.6, seg=3, **k): return soften(boxes(*a, **k), w, seg)

def cone(name, cx, cy, r0, r1, z0, z1, mt, cat, spec="", n=28, props=None):
    """vertical frustum: r0 at z0 (bottom), r1 at z1 (top)"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=m(r0), radius2=m(r1), depth=m(z1 - z0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, m(z1 - z0) / 2)); bm.to_mesh(me); bm.free()
    o = _obj(name, me, mt, cat, spec, (cx, cy, z0))
    for p in o.data.polygons: p.use_smooth = len(p.vertices) == 4
    for k, v in (props or {}).items(): o[k] = v
    return o

def blobs(name, pts, mt, cat, spec=""):
    """several soft spheres in one object: pts = [(x, y, z, r, squash)] in world feet (stylised foliage, cushions)"""
    cx, cy = pts[0][0], pts[0][1]
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for (x, y, z, r, sq) in pts:
        g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=m(r))
        vs = g["verts"]; bmesh.ops.scale(bm, vec=(1, 1, sq), verts=vs)
        bmesh.ops.translate(bm, verts=vs, vec=(m(x - cx), m(y - cy), m(z)))
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (cx, cy, 0))
    for p in o.data.polygons: p.use_smooth = True
    return o

def wavy_panel(name, x0, x1, y, amp, waves, z0, z1, mt, cat, spec="", t=0.04):
    """pleated curtain: a corrugated sheet along x at wall-offset y, smooth shaded so the folds catch light"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    n = max(8, int(waves * 8)); cx = (x0 + x1) / 2
    front, back = [], []
    for i in range(n + 1):
        u = i / n; x = x0 + (x1 - x0) * u; dy = amp * math.sin(u * waves * 2 * math.pi)
        for lst, off in ((front, t), (back, 0.0)):
            lst.append((bm.verts.new((m(x - cx), m(y + dy + off), m(z0))), bm.verts.new((m(x - cx), m(y + dy + off), m(z1)))))
    for i in range(n):
        f = front; bm.faces.new((f[i][0], f[i + 1][0], f[i + 1][1], f[i][1]))
        b = back; bm.faces.new((b[i][1], b[i + 1][1], b[i + 1][0], b[i][0]))
    for lst_a, lst_b in ((front, back),):
        for i in (0, n): bm.faces.new((lst_a[i][0], lst_a[i][1], lst_b[i][1], lst_b[i][0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, (cx, 0, 0))
    for p_ in o.data.polygons: p_.use_smooth = True
    return o

def leaves(name, x, y, z, n, length, width, tilt, mt, seed=1, spec=""):
    """n long thin leaves radiating from (x, y, z), each tilted up by `tilt` degrees (stylised palm / snake / rubber plant)"""
    import random
    from mathutils import Matrix
    rnd = random.Random(seed)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for k in range(n):
        az = 2 * math.pi * k / n + rnd.uniform(-0.3, 0.3); tl = math.radians(tilt + rnd.uniform(-12, 12)); L = length * rnd.uniform(0.75, 1.1)
        g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0); vs = g["verts"]
        bmesh.ops.scale(bm, vec=(m(L / 2), m(width / 2), m(0.06)), verts=vs)
        bmesh.ops.translate(bm, verts=vs, vec=(m(L / 2), 0, 0))
        rot = Matrix.Rotation(az, 3, 'Z') @ Matrix.Rotation(-tl, 3, 'Y')
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=rot)
        bmesh.ops.translate(bm, verts=vs, vec=(0, 0, m(z + rnd.uniform(-0.15, 0.25))))
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, "plants", spec, (x, y, 0))
    for p_ in o.data.polygons: p_.use_smooth = True
    return o

def art_image(name, seed, palette):
    """simple abstract print (arches and a sun) generated as pixels, packed into the file"""
    import numpy as np
    W, Hh = 256, 320
    rng = np.random.default_rng(seed)
    a = np.ones((Hh, W, 4), np.float32); a[..., :3] = palette[0]
    yy, xx = np.mgrid[0:Hh, 0:W]
    for i, (cx, cy, r) in enumerate(((80, 0, 120), (180, 0, 90), (128, 0, 55))):
        msk = ((xx - cx) ** 2 + (yy - cy) ** 2 < r * r)
        a[msk, :3] = palette[1 + i % (len(palette) - 1)]
    msk = ((xx - 190) ** 2 + (yy - 240) ** 2 < 26 * 26); a[msk, :3] = palette[-1]
    a[..., :3] += rng.normal(0, 0.012, (Hh, W, 1)).astype(np.float32)
    img = bpy.data.images.new(name, W, Hh, alpha=False); img.pixels.foreach_set(np.clip(a, 0, 1).ravel()); img.pack()
    return img

def sofa(prefix, x0, y0, y1, fabric, wood, spec, accent=None, pillows=True):
    """3 ft deep sofa facing west (towards the TV): plinth, seat and back cushions, rounded arms, wooden legs, throw pillows"""
    A = 0.5                                   # arm width
    sboxes(prefix + "_FRAME", [(x0 + 0.05, x0 + 2.95, y0 + 0.05, y1 - 0.05, 0.35, 1.1), (x0 + 2.45, x0 + 3.0, y0, y1, 1.1, 2.45)],
           fabric, "furniture", spec, w=1.2)
    sboxes(prefix + "_ARMS", [(x0, x0 + 3.0, y0, y0 + A, 0.35, 2.05), (x0, x0 + 3.0, y1 - A, y1, 0.35, 2.05)], fabric, "furniture", "", w=2.0)
    n = 3 if (y1 - y0) >= 6.5 else 2
    span = (y1 - y0 - 2 * A) / n; seats, backs = [], []
    for i in range(n):
        a = y0 + A + i * span + 0.03; b = a + span - 0.06
        seats.append((x0 + 0.12, x0 + 2.45, a, b, 1.1, 1.55))
        backs.append((x0 + 1.95, x0 + 2.45, a, b, 1.55, 2.75))
    sboxes(prefix + "_SEAT_CUSHIONS", seats, fabric, "furniture", "foam seat cushions with removable covers", w=1.8, seg=4)
    sboxes(prefix + "_BACK_CUSHIONS", backs, fabric, "furniture", "", w=2.4, seg=4)
    for i, (lx, ly) in enumerate(((x0 + 0.25, y0 + 0.25), (x0 + 2.75, y0 + 0.25), (x0 + 0.25, y1 - 0.25), (x0 + 2.75, y1 - 0.25))):
        cone(f"{prefix}_LEG_{i+1}", lx, ly, 0.06, 0.09, 0.0, 0.35, wood, "furniture", "", 12)
    if pillows and accent:
        sboxes(prefix + "_PILLOWS", [(x0 + 1.65, x0 + 1.95, y0 + A + 0.15, y0 + A + 1.45, 1.55, 2.75), (x0 + 1.65, x0 + 1.95, y1 - A - 1.45, y1 - A - 0.15, 1.55, 2.75)],
               accent, "soft_furnishing", "throw pillows 18 inch", w=2.5, seg=4)

def coffee_table(x0, x1, y0, y1, wood, top=None, shelf=True):
    sbox("COFFEE_TABLE", x0, x1, y0, y1, 1.12, 1.3, top or wood, "furniture", "coffee table 4 x 2'6\" with a lower shelf", w=0.5)
    legs = [(x0 + 0.12, x0 + 0.27, y0 + 0.12, y0 + 0.27, 0, 1.12), (x1 - 0.27, x1 - 0.12, y0 + 0.12, y0 + 0.27, 0, 1.12),
            (x0 + 0.12, x0 + 0.27, y1 - 0.27, y1 - 0.12, 0, 1.12), (x1 - 0.27, x1 - 0.12, y1 - 0.27, y1 - 0.12, 0, 1.12)]
    if shelf: legs.append((x0 + 0.15, x1 - 0.15, y0 + 0.15, y1 - 0.15, 0.3, 0.38))
    sboxes("COFFEE_TABLE_BASE", legs, wood, "furniture", "", w=0.25, seg=2)
    # a tray, a bowl and two books on top
    sbox("COFFEE_TABLE_BOOKS", x0 + 0.4, x0 + 1.1, y0 + 0.5, y0 + 1.4, 1.3, 1.42, mat("Book_Sage", (0.48, 0.56, 0.48), 0.8), "decor", "", w=0.15, seg=2)
    cone("COFFEE_TABLE_BOWL", (x0 + x1) / 2 + 0.3, (y0 + y1) / 2 + 0.6, 0.18, 0.38, 1.3, 1.5, mat("Ceramic_White", (0.92, 0.91, 0.88), 0.3), "decor", "ceramic bowl")

def pendant(name, x, y, z_bottom, shade_mt, cord_mt, lumens=500):
    cyl(name + "_CORD", x, y, 0.015, z_bottom + 0.75, H, cord_mt, "lighting", "", 6)
    cone(name, x, y, 0.55, 0.12, z_bottom, z_bottom + 0.75, shade_mt, "lighting", "pendant light over the dining table, E27 9 W warm LED", 32)
    cyl(name + "_BULB", x, y, 0.1, z_bottom + 0.02, z_bottom + 0.2, mat("Bulb_Warm", (1.0, 0.86, 0.62), 0.3, 0, 4.0), "lighting", "warm LED bulb", 12,
        {"light": "point", "lumens": lumens})

def floor_lamp(x, y, metal, shade_mt):
    cyl("FLOOR_LAMP_BASE", x, y, 0.45, 0.0, 0.08, metal, "lighting", "", 24)
    cyl("FLOOR_LAMP_POLE", x, y, 0.035, 0.08, 4.9, metal, "lighting", "", 8)
    cone("FLOOR_LAMP_SHADE", x, y, 0.62, 0.55, 4.6, 5.6, shade_mt, "lighting", "linen drum floor lamp beside the sofa, warm LED", 32, {"light": "point", "lumens": 400})

def plant(name, x, y, pot_mt, size=1.0, kind="palm"):
    leaf = mat("Foliage", (0.20, 0.40, 0.19), 0.75); leaf2 = mat("Foliage_Light", (0.33, 0.52, 0.26), 0.75)
    cone(name + "_POT", x, y, 0.42 * size, 0.55 * size, 0.0, 1.4 * size, pot_mt, "plants", "", 24)
    s = size; stem = mat("Stem", (0.30, 0.36, 0.18), 0.8)
    if kind == "palm":                        # areca palm: a few stems with long arching fronds
        for i, (dx, dy, h) in enumerate(((0.0, 0.0, 4.6), (0.22, 0.12, 3.8), (-0.2, -0.1, 4.1))):
            cyl(f"{name}_STEM_{i+1}", x + dx * s, y + dy * s, 0.035 * s, 1.3 * s, h * s, stem, "plants", "", 6)
        leaves(name + "_LEAVES", x, y, 4.4 * s, 9, 2.0 * s, 0.32 * s, 20, leaf, 3, "areca palm (likes the bright corner near W7)")
        leaves(name + "_LEAVES2", x + 0.1 * s, y, 3.6 * s, 7, 1.6 * s, 0.30 * s, 35, leaf2, 5)
    else:                                     # snake plant: upright blades
        leaves(name + "_LEAVES", x, y, 1.35 * s, 10, 2.4 * s, 0.32 * s, 72, leaf, 7, "snake plant (easy care, low light)")
        leaves(name + "_LEAVES2", x, y, 1.35 * s, 6, 1.8 * s, 0.30 * s, 64, leaf2, 9)
    cyl(name + "_SOIL", x, y, 0.4 * size, 1.25 * size, 1.32 * size, mat("Soil", (0.18, 0.12, 0.08), 0.95), "plants", "", 16)

def curtains(fabric, rod_mt, sheer=True):
    """W7 on the south wall (x 10.6 .. 14.6): ceiling-high rod, two pleated panels stacked open at the sides"""
    Yw = -45.25; zt = 8.3
    cyl("CURTAIN_ROD_L", 9.27, Yw + 0.35, 0.05, zt + 0.05, zt + 0.15, rod_mt, "soft_furnishing", "", 8)
    box("CURTAIN_ROD", 9.17, 16.07, Yw + 0.32, Yw + 0.38, zt + 0.06, zt + 0.12, rod_mt, "soft_furnishing", "curtain rod, matt black, 7 ft wide, mounted high so the window looks taller")
    for side, (a, b) in (("L", (9.37, 10.87)), ("R", (14.37, 15.87))):
        wavy_panel(f"CURTAIN_{side}", a, b, Yw + 0.22, 0.09, 5, 0.08, zt, fabric, "soft_furnishing", "full-length cotton-linen curtains with blackout lining, stacked open beside W7")

def wall_art(x0, x1, z0, z1, seed, palette, frame_mt, y=-15.25):
    Wd = 0.08
    sboxes("WALL_ART_FRAME", [(x0, x1, y - Wd, y, z0, z0 + 0.12), (x0, x1, y - Wd, y, z1 - 0.12, z1), (x0, x0 + 0.12, y - Wd, y, z0, z1), (x1 - 0.12, x1, y - Wd, y, z0, z1)],
           frame_mt, "decor", "framed print 3 x 2'4\" above the panel line", w=0.2, seg=2)
    img = art_image(f"{OPT}_art", seed, palette)
    mt = tex_mat("Art_Print", img, 0.8, palette[0])
    me = bpy.data.meshes.new("WALL_ART"); bm = bmesh.new()
    v = [bm.verts.new((m(a), m(y - 0.03), m(c))) for a, c in ((x0 + 0.12, z0 + 0.12), (x1 - 0.12, z0 + 0.12), (x1 - 0.12, z1 - 0.12), (x0 + 0.12, z1 - 0.12))]
    f = bm.faces.new(v[::-1]); uv = bm.loops.layers.uv.new("UVMap")
    for l in f.loops: l[uv].uv = ((l.vert.co.x / FT - x0) / (x1 - x0), (l.vert.co.z / FT - z0) / (z1 - z0))
    bm.normal_update(); bm.to_mesh(me); bm.free(); _obj("WALL_ART", me, mt, "decor", "abstract print, matt paper")

def side_table(x, y, wood, metal):
    cyl("SIDE_TABLE_TOP", x, y, 0.7, 1.75, 1.85, wood, "furniture", "round side table 1'5\"", 32)
    cyl("SIDE_TABLE_STEM", x, y, 0.06, 0.06, 1.75, metal, "furniture", "", 8)
    cyl("SIDE_TABLE_FOOT", x, y, 0.45, 0.0, 0.06, metal, "furniture", "", 24)

def console_decor(top_z=1.6):
    cone("CONSOLE_VASE", X + 0.6, TV_YC - 2.5, 0.16, 0.26, top_z, top_z + 1.0, mat("Vase_Clay", (0.70, 0.50, 0.38), 0.7), "decor", "clay vase")
    sboxes("CONSOLE_BOOKS", [(X + 0.4, X + 1.0, TV_YC + 2.2, TV_YC + 2.32, top_z, top_z + 0.8), (X + 0.4, X + 1.0, TV_YC + 2.34, TV_YC + 2.46, top_z, top_z + 0.72),
                             (X + 0.4, X + 1.0, TV_YC + 2.48, TV_YC + 2.6, top_z, top_z + 0.85)], mat("Books", (0.55, 0.45, 0.35), 0.8), "decor", "", w=0.1, seg=1)
    sbox("SOUNDBAR", X + 0.35, X + 0.65, TV_YC - 1.4, TV_YC + 1.4, top_z, top_z + 0.22, mat("TV_Black", (0.03, 0.03, 0.035), 0.15), "furniture", "soundbar", w=0.3, seg=2)

def dining(prefix, x0, x1, y0, y1, chairs_y, top_mt, chair_mt, spec):
    sbox(prefix + "_TABLE_TOP", x0, x1, y0, y1, 2.35, 2.5, top_mt, "furniture", spec, w=0.5)
    sboxes(prefix + "_TABLE_LEGS", [(x0 + 0.2, x0 + 0.4, y0 + 0.2, y0 + 0.4, 0, 2.35), (x1 - 0.4, x1 - 0.2, y0 + 0.2, y0 + 0.4, 0, 2.35),
                                   (x0 + 0.2, x0 + 0.4, y1 - 0.4, y1 - 0.2, 0, 2.35), (x1 - 0.4, x1 - 0.2, y1 - 0.4, y1 - 0.2, 0, 2.35)], top_mt, "furniture", "", w=0.3, seg=2)
    ch = []
    for cy_ in chairs_y:
        for side in (-1, 1):
            xs = (x0 - 1.4, x0 - 0.1) if side < 0 else (x1 + 0.1, x1 + 1.4)
            ch.append((xs[0], xs[1], cy_ - 0.65, cy_ + 0.65, 1.4, 1.55))
            bx = (xs[0], xs[0] + 0.12) if side < 0 else (xs[1] - 0.12, xs[1])
            ch.append((bx[0], bx[1], cy_ - 0.65, cy_ + 0.65, 1.55, 3.0))
            for lx in (xs[0] + 0.1, xs[1] - 0.2):
                for ly in (cy_ - 0.55, cy_ + 0.45): ch.append((lx, lx + 0.1, ly, ly + 0.1, 0, 1.4))
    sboxes(prefix + "_CHAIRS", ch, chair_mt, "furniture", "dining chairs", w=0.35, seg=2)
    pads = [((x0 - 1.32, x0 - 0.18) if s_ < 0 else (x1 + 0.18, x1 + 1.32)) + (cy_ - 0.57, cy_ + 0.57, 1.55, 1.68) for cy_ in chairs_y for s_ in (-1, 1)]
    sboxes(prefix + "_SEAT_PADS", pads, mat("Seat_Pad", (0.80, 0.74, 0.64), 0.9), "soft_furnishing", "seat cushions", w=0.8, seg=3)

def common_wet_and_outside():
    anti = tex_mat("AntiSkid_Tile", tile_image(f"{OPT}_antiskid", 384, 384, (0.70, 0.72, 0.72), 0.03, (0.55, 0.56, 0.56), 3, speck=0.05, seed=7), 0.85, (0.70, 0.72, 0.72))
    for src in ("FLOOR_B1", "FLOOR_B2"):
        floor_overlay(src + "_FINISH", src, anti, 1.97, 1.97, False, "anti-skid matt vitrified 600x600, R11, epoxy grout")
    kota = tex_mat("Kota_Stone", tile_image(f"{OPT}_kota", 384, 384, (0.47, 0.55, 0.50), 0.06, (0.36, 0.40, 0.37), 2, seed=11), 0.75, (0.47, 0.55, 0.50))
    floor_overlay("OPENSQ_FINISH", "FLOOR_OPENSQ", kota, 1.97, 1.97, False, "Kota stone 2'x2', natural finish, sloped to drain")

# ---------------------------------------------------------------- architecture: main entrance (user, 5 Nov 2026)
MAIN_Y0, MAIN_Y1 = -24.61, -21.07          # V2: 108 cm main door (architecture), 25 cm south of Pillar 2's line
B1X, XE_ = 23.08, 27.5                     # Bath 1 west wall outer face / hall east wall
PX0, PX1 = 18.67, 19.92                    # pillar line (15 in E-W)
PIL_Y = ((-20.25, -19.5), (-36.33, -35.58))  # Pillar 2, Pillar 1 (9 in N-S)
R2D_Y0, R2D_Y1 = -23.25, -20.25            # Room 2 hall door
def main_door_v2():
    """V2: the main door is already architecture (DOOR_MAIN). Give its leaf a teak finish and make it openable."""
    l = bpy.data.objects.get('DOOR_MAIN_LEAF')
    if not l: return None
    teak = bpy.data.materials.get('Door_Main_Teak') or bpy.data.materials.new('Door_Main_Teak')
    teak.use_nodes = True; b = teak.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.36, 0.22, 0.12, 1); b.inputs['Roughness'].default_value = 0.45
    teak.diffuse_color = (0.36, 0.22, 0.12, 1)
    if l.data.users > 1: l.data = l.data.copy()
    l.data.materials.clear(); l.data.materials.append(teak)
    l['spec'] = "solid teak main door 3'6\" x 7', opens into the hall"; l['label'] = 'Main door'
    return l.name
def add_main_door():
    """main entrance in WALL_EXT_W_HALL: cutter (cuts the wall through its Openings boolean), frame, leaf, threshold"""
    for n in ("DOOR_MAIN", "DOOR_MAIN_CUTTER", "DOOR_MAIN_FRAME", "DOOR_MAIN_LEAF", "THRESHOLD_MAIN"):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    cut_c = bpy.data.collections.get("_OPENING_CUTTERS"); door_c = bpy.data.collections.get("04_DOORS"); fl_c = bpy.data.collections.get("02_FLOORS")
    def mk(name, bxs, mtname, coll, pivot=None):
        px, py = pivot if pivot else ((bxs[0][0] + bxs[0][1]) / 2, (bxs[0][2] + bxs[0][3]) / 2)
        me = bpy.data.meshes.new(name); bm = bmesh.new()
        for (a, b, c, d, e, f) in bxs: _bm_box(bm, a - px, b - px, c - py, d - py, e, f)
        bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); o.location = Vector((m(px), m(py), 0))
        mt = bpy.data.materials.get(mtname)
        if mt: o.data.materials.append(mt)
        coll.objects.link(o); return o
    basis = "user answer 5 Nov 2026: main entrance in the middle of the hall west wall, 3 ft; exact position PROVISIONAL"
    c = mk("DOOR_MAIN_CUTTER", [(2.8, 4.1, MAIN_Y0, MAIN_Y1, -0.01, 7.0)], "", cut_c); c.display_type = 'WIRE'; c.hide_render = True
    f = mk("DOOR_MAIN_FRAME", [(3.08, 3.83, MAIN_Y0, MAIN_Y0 + 0.2, 0, 7.0), (3.08, 3.83, MAIN_Y1 - 0.2, MAIN_Y1, 0, 7.0), (3.08, 3.83, MAIN_Y0, MAIN_Y1, 6.8, 7.0)], "Frame_Wood", door_c)
    teak = bpy.data.materials.get("Door_Main_Teak") or bpy.data.materials.new("Door_Main_Teak")
    teak.use_nodes = True; b = teak.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.36, 0.22, 0.12, 1); b.inputs["Roughness"].default_value = 0.45
    teak.diffuse_color = (0.36, 0.22, 0.12, 1)
    px, py = 3.70, MAIN_Y0 + 0.2
    l = mk("DOOR_MAIN_LEAF", [(3.55, 3.70, py, MAIN_Y1 - 0.2, 0.04, 6.8), (3.70, 3.78, py + 2.2, py + 2.3, 3.0, 3.8)], "Door_Main_Teak", door_c, pivot=(px, py))
    t = mk("THRESHOLD_MAIN", [(3.08, 3.83, MAIN_Y0, MAIN_Y1, -0.25, 0.042)], "Threshold_Stone", fl_c)
    for o in (c, f, l, t):
        o["status"] = "CONFIRMED"; o["basis"] = basis
    l["interact"] = "hinge"; l["open_deg"] = -95.0; l["group"] = "MAIN_DOOR"; l["label"] = "Main door"
    l["spec"] = "solid teak main door 2'7\" x 6'9\", opens into the hall"; f["spec"] = "main door frame"; t["spec"] = "granite threshold"
    return [c.name, f.name, l.name, t.name]

# ---------------------------------------------------------------- shared layout (TV on the west wall north of the main door)
X = 6.5
TV_Y0, TV_Y1, TV_YC = -34.1, -26.1, -30.1        # 8 ft panel on the west wall between the main door and Pillar 1's wall column
def tv_and_console(tv_mat, con_mat, depth=0.13, console=True):
    box("TV", X + depth, X + depth + 0.15, TV_YC - 2.15, TV_YC + 2.15, 2.45, 4.85, tv_mat, "furniture", "55 inch TV, wall-mounted, cables inside the wall finish")
    if console:
        sbox("TV_CONSOLE", X + depth, X + 1.57, TV_YC - 3.0, TV_YC + 3.0, 0.9, 1.6, con_mat, "furniture", "floating console 6 ft x 1'3\", push-to-open shutters", w=0.4)
        console_decor()
        boxes("TV_CONSOLE_GROOVES", [(X + 1.57, X + 1.59, TV_YC + k - 0.015, TV_YC + k + 0.015, 0.95, 1.55) for k in (-1.0, 1.0)], mat("Groove_Dark", (0.06, 0.05, 0.05), 0.6), "furniture", "")

STYLE = {   # soft furnishings per plan: pillow accent, curtain, rug field/border, art palette, metal
    "HALL_REC":    dict(acc=(0.62, 0.42, 0.30), cur=(0.86, 0.82, 0.74), rug=((0.80, 0.75, 0.66), (0.55, 0.46, 0.36)), art=[(0.93, 0.89, 0.82), (0.78, 0.55, 0.40), (0.55, 0.60, 0.50), (0.85, 0.72, 0.55), (0.70, 0.36, 0.25)], metal=(0.08, 0.08, 0.08)),
    "HALL_BUDGET": dict(acc=(0.30, 0.42, 0.55), cur=(0.80, 0.80, 0.78), rug=None, art=None, metal=(0.15, 0.15, 0.15)),
    "HALL_LONG":   dict(acc=(0.75, 0.62, 0.40), cur=(0.74, 0.73, 0.70), rug=((0.62, 0.62, 0.60), (0.30, 0.31, 0.33)), art=[(0.90, 0.90, 0.88), (0.35, 0.38, 0.42), (0.70, 0.66, 0.58), (0.55, 0.58, 0.60), (0.78, 0.62, 0.38)], metal=(0.72, 0.73, 0.74)),
    "HALL_MARBLE": dict(acc=(0.55, 0.20, 0.18), cur=(0.88, 0.80, 0.64), rug=((0.70, 0.30, 0.22), (0.20, 0.30, 0.25)), art=[(0.94, 0.90, 0.80), (0.20, 0.36, 0.28), (0.72, 0.30, 0.22), (0.86, 0.66, 0.32), (0.55, 0.20, 0.18)], metal=(0.75, 0.60, 0.30)),
    "HALL_BEST":   dict(acc=(0.66, 0.40, 0.28), cur=(0.86, 0.82, 0.74), rug=((0.82, 0.78, 0.70), (0.52, 0.56, 0.48)), art=[(0.94, 0.91, 0.85), (0.70, 0.46, 0.32), (0.55, 0.60, 0.50), (0.86, 0.76, 0.60), (0.62, 0.36, 0.26)], metal=(0.08, 0.08, 0.08)),
    "HALL_PANEL":  dict(acc=(0.45, 0.52, 0.42), cur=(0.88, 0.85, 0.78), rug=((0.84, 0.80, 0.72), (0.56, 0.62, 0.53)), art=[(0.94, 0.91, 0.85), (0.56, 0.62, 0.53), (0.78, 0.68, 0.50), (0.85, 0.80, 0.70), (0.62, 0.42, 0.30)], metal=(0.78, 0.68, 0.50)),
}
def living_and_dining(fabric, wood, chair, sofa_len=7.0, seats6=True, rug=True, table=(10.85, 12.8), decor=True):
    S = STYLE.get(OPT, STYLE["HALL_REC"])
    metal = mat("Metal_Accent", S["metal"], 0.35, 0.9)
    y0 = TV_YC - sofa_len / 2; y1 = TV_YC + sofa_len / 2
    sofa("SOFA", X + 7.47, y0, y1, fabric, wood, f"{'3-seater' if sofa_len >= 7 else 'ready-made'} sofa {sofa_len:.0f} ft, about 8 ft from the TV",
         accent=mat("Pillow_Accent", S["acc"], 0.9), pillows=decor)
    coffee_table(table[0], table[1], TV_YC - 1.25, TV_YC + 1.25, wood, shelf=decor)
    if rug and S["rug"]:
        box("RUG", 8.17, 16.47, TV_YC - 4.25, TV_YC + 4.25, 0.01, 0.035, mat("Rug_Border", S["rug"][1], 0.95), "soft_furnishing", "flat-weave cotton rug 8 x 8 ft (easy to wash)")
        box("RUG_FIELD", 8.57, 16.07, TV_YC - 3.85, TV_YC + 3.85, 0.035, 0.045, mat("Rug_Field", S["rug"][0], 0.95), "soft_furnishing", "")
    if seats6: dining("DINING", 10.67, 13.67, -43.0, -37.0, (-38.0, -40.0, -42.0), wood, chair, "6-seater dining table 6 x 3 ft near window W7")
    else: dining("DINING", 10.92, 13.42, -41.5, -37.5, (-38.6, -40.4), wood, chair, "4-seater dining table 4 x 2'6\"")
    curtains(mat("Curtain", S["cur"], 0.95), mat("Rod_Black", (0.08, 0.08, 0.08), 0.4, 0.8), sheer=decor)
    plant("PLANT_DINING", 7.67, -43.8, mat("Pot_Terracotta", (0.65, 0.38, 0.26), 0.8), 1.0, "palm")
    if not decor: return
    cy_ = -40.0 if seats6 else -39.5
    shade = mat("Pendant_Shade", S["metal"], 0.35, 0.85); cord = mat("Cord_Black", (0.05, 0.05, 0.05), 0.6)
    for i, dy in enumerate((-1.4, 1.4) if seats6 else (0.0,)):
        pendant(f"PENDANT_{i+1}", 12.17, cy_ + dy, 5.5, shade, cord)
    floor_lamp(X + 8.97, y1 + 0.9, metal, mat("Lamp_Linen", (0.95, 0.90, 0.80), 0.9, 0, 0.6))
    side_table(X + 8.97, y0 - 0.8, wood, metal)
    plant("PLANT_TV", X + 0.92, TV_Y0 - 0.75, mat("Pot_Stone", (0.82, 0.80, 0.76), 0.6), 0.8, "round")
    if S["art"]: wall_art(8.2, 11.2, 4.3, 6.7, 7, S["art"], mat("Frame", S["metal"], 0.4, 0.6))

def entry(cab_mat, mirror=True):
    box("SHOE_CABINET", X, X + 1.2, -19.3, -15.7, 0.4, 3.0, cab_mat, "furniture", "shoe cabinet 3'6\" x 1'2\" beside the main door")
    if mirror: box("ENTRY_MIRROR", X, X + 0.05, -18.9, -16.1, 3.6, 6.4, mat("Mirror", (0.8, 0.85, 0.88), 0.03, 1.0), "decor", "entry mirror")

def guards(height=4.0):
    g = []
    for (y0, y1) in PIL_Y:
        for xc in (PX0, PX1):
            for yc in (y0, y1): g.append((xc - 0.07, xc + 0.07, yc - 0.07, yc + 0.07, 0.0, height))
    boxes("PILLAR_CORNER_GUARDS", g, mat("Steel_304", (0.78, 0.79, 0.8), 0.25, 1.0), "wall_finish", f"304 stainless steel corner guards 1.5\" x 1.5\", {height:.0f} ft")

def downlights():
    led = mat("Downlight", (1.0, 0.92, 0.8), 0.4, 0, 3.0)
    for i, (x, y) in enumerate([(x, y) for x in (10.5, 15.8) for y in (-17.5, -25.0, -32.5, -40.5)]):
        cyl(f"DOWNLIGHT_{i+1}", x, y, 0.3, H - 0.05, H, led, "lighting", "12 W LED downlight 3000K", 20, {"light": "spot", "lumens": 900})

def floors(main_mat, main_spec, tile_u, tile_v, along_y, srcs=("FLOOR_HALL", "FLOOR_PAS", "FLOOR_R2", "FLOOR_KIT"), skirt=None):
    for src in srcs: floor_overlay(src + "_FINISH", src, main_mat, tile_u, tile_v, along_y, main_spec)
    skirting(skirt or mat("Skirting", (0.78, 0.75, 0.70), 0.5), "4 inch skirting cut from the floor tile")
    common_wet_and_outside()

def gvt_mat():
    return tex_mat("GVT_Matt_Greige", tile_image(f"{OPT}_gvt", 1024, 512, (0.80, 0.77, 0.72), 0.035, (0.66, 0.63, 0.59), 2, veins=True, seed=3), 0.55, (0.80, 0.77, 0.72))

def wall_slab(name, y0, y1, z0, z1, x0, x1, mt, slab_w, slab_h, spec):
    """vertical panel on the west wall with UVs in feet so a slab texture repeats"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); _bm_box(bm, x0, x1, y0, y1, z0, z1)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops: l[uv].uv = ((l.vert.co.y / FT - y0) / slab_w, (l.vert.co.z / FT - z0) / slab_h)
    bm.to_mesh(me); bm.free(); return _obj(name, me, mt, "wall_finish", spec)

# ---------------------------------------------------------------- options
def build_rec():
    floors(gvt_mat(), "matt/satin GVT 600x1200, light warm greige stone look, rectified, 2 mm joints", 3.94, 1.97, True, skirt=mat("Skirting_GVT", (0.78, 0.75, 0.70), 0.5))
    Z0, Z1 = 0.33, 8.75
    wpc = mat("WPC_Teak", (0.55, 0.40, 0.27), 0.5); metal = mat("Profile_Black", (0.08, 0.08, 0.08), 0.35, 0.8)
    box("TV_WALL_PANEL", X, X + 0.08, TV_Y0, TV_Y1, Z0, Z1, wpc, "wall_finish", "WPC fluted panel 8 ft x 8'5\", teak, glued on the wall; hides TV wiring")
    flutes = []; y = TV_Y0 + 0.12
    while y + 0.12 < TV_Y1: flutes.append((X + 0.08, X + 0.13, y, y + 0.12, Z0, Z1)); y += 0.25
    boxes("TV_WALL_FLUTES", flutes, wpc, "wall_finish", "fluted ridges")
    boxes("TV_WALL_FRAME", [(X, X + 0.16, TV_Y0 - 0.08, TV_Y0, Z0, Z1 + 0.08), (X, X + 0.16, TV_Y1, TV_Y1 + 0.08, Z0, Z1 + 0.08),
                            (X, X + 0.16, TV_Y0 - 0.08, TV_Y1 + 0.08, Z1, Z1 + 0.08)], metal, "wall_finish", "black anodised aluminium profile frame")
    box("TV_WALL_LED", X + 0.13, X + 0.16, TV_Y0 + 0.2, TV_Y1 - 0.2, Z1 - 0.12, Z1 - 0.06, mat("LED_Warm", (1.0, 0.85, 0.6), 0.4, 0, 3.0), "lighting",
        "warm LED strip behind the top profile", {"light": "strip", "lumens": 600})
    walnut = mat("Walnut", (0.36, 0.25, 0.17), 0.5)
    tv_and_console(mat("TV_Black", (0.03, 0.03, 0.035), 0.15), walnut)
    guards(); entry(walnut)
    living_and_dining(mat("Sofa_Oatmeal", (0.72, 0.66, 0.57), 0.9), walnut, mat("Chair_Cane", (0.66, 0.52, 0.34), 0.7))
    downlights(); ceiling_fan()

def build_budget():
    dc = tex_mat("DoubleCharge_Beige", tile_image(f"{OPT}_dc", 512, 512, (0.84, 0.80, 0.72), 0.02, (0.70, 0.66, 0.60), 3, speck=0.10, seed=5), 0.45, (0.84, 0.80, 0.72))
    floors(dc, "double-charge vitrified 600x600, beige speckled, polished", 1.97, 1.97, False, skirt=mat("Skirting_DC", (0.82, 0.78, 0.70), 0.45))
    lam = mat("Laminate_Oak", (0.66, 0.53, 0.38), 0.55)
    box("TV", X, X + 0.15, TV_YC - 2.15, TV_YC + 2.15, 2.45, 4.85, mat("TV_Black", (0.03, 0.03, 0.035), 0.15), "furniture", "43-55 inch TV on a wall bracket; cables in a PVC casing")
    box("TV_SHELF", X, X + 1.0, TV_YC - 1.75, TV_YC + 1.75, 1.6, 1.7, lam, "furniture", "laminated ply shelf 3'6\" on brackets")
    box("TV_UNIT", X, X + 1.3, TV_YC - 2.25, TV_YC + 2.25, 0.0, 1.4, lam, "furniture", "ready-made TV unit, engineered wood")
    box("SHOE_RACK", X, X + 1.0, -18.3, -15.7, 0.0, 2.6, lam, "furniture", "ready-made shoe rack beside the main door")
    living_and_dining(mat("Sofa_Grey", (0.55, 0.56, 0.57), 0.9), lam, mat("Chair_Black", (0.15, 0.15, 0.15), 0.6), sofa_len=6.0, seats6=False, rug=False, table=(11.1, 12.8), decor=False)
    bat = mat("LED_Batten", (1.0, 0.97, 0.9), 0.4, 0, 3.0)
    for i, (a, b, c, d) in enumerate([(7.17, 10.17, -45.25, -45.13), (16.17, 20.17, -45.25, -45.13), (X, X + 0.12, -33.0, -29.0)]):
        box(f"LED_BATTEN_{i+1}", a, b, c, d, 7.6, 7.75, bat, "lighting", "20 W LED batten, 4 ft", {"light": "strip", "lumens": 2000})
    ceiling_fan()

def build_long():
    fb = tex_mat("FullBody_Grey", tile_image(f"{OPT}_fb", 1024, 512, (0.74, 0.73, 0.70), 0.03, (0.62, 0.61, 0.58), 2, speck=0.02, seed=9), 0.5, (0.74, 0.73, 0.70))
    floors(fb, "full-body vitrified 600x1200, matt, light stone grey, rectified, 2 mm epoxy joints", 3.94, 1.97, True, skirt=mat("Skirting_FB", (0.72, 0.71, 0.68), 0.5))
    slab_img = tile_image(f"{OPT}_slab", 512, 1024, (0.93, 0.92, 0.90), 0.02, (0.80, 0.80, 0.79), 2, veins=True, seed=21)
    slab = tex_mat("Porcelain_Slab", slab_img, 0.25, (0.93, 0.92, 0.90))
    Z0, Z1 = 0.33, 8.75
    wall_slab("TV_WALL_SLABS", TV_Y0, TV_Y1, Z0, Z1, X, X + 0.04, slab, 2.62, 5.25, "porcelain slabs 800x1600 marble look, laid vertically, epoxy joints; waterproof, fade-proof")
    ss = mat("Steel_Brushed", (0.72, 0.73, 0.74), 0.3, 1.0)
    boxes("TV_WALL_PROFILE", [(X, X + 0.08, TV_Y0 - 0.05, TV_Y0, Z0, Z1 + 0.05), (X, X + 0.08, TV_Y1, TV_Y1 + 0.05, Z0, Z1 + 0.05),
                              (X, X + 0.08, TV_Y0 - 0.05, TV_Y1 + 0.05, Z1, Z1 + 0.05)], ss, "wall_finish", "304 brushed stainless steel edge profile")
    hpl = mat("HPL_Graphite", (0.22, 0.22, 0.23), 0.5)
    tv_and_console(mat("TV_Black", (0.03, 0.03, 0.035), 0.15), hpl, depth=0.04)
    box("TV_CONSOLE_TOP", X + 0.04, X + 1.62, TV_YC - 3.05, TV_YC + 3.05, 1.6, 1.68, mat("Granite_Black", (0.08, 0.08, 0.09), 0.2), "furniture", "granite top on the console")
    guards(height=5.0); entry(hpl)
    living_and_dining(mat("Sofa_Charcoal", (0.32, 0.33, 0.35), 0.85), mat("Teak_Solid", (0.45, 0.30, 0.18), 0.5), mat("Chair_Metal", (0.2, 0.2, 0.2), 0.4))
    downlights(); ceiling_fan()

def build_marble():
    mimg = tile_image(f"{OPT}_marble", 1024, 512, (0.94, 0.93, 0.91), 0.02, (0.86, 0.85, 0.83), 1, veins=True, seed=31)
    marble = tex_mat("Marble_White", mimg, 0.15, (0.94, 0.93, 0.91))
    for src in ("FLOOR_HALL", "FLOOR_PAS"):
        floor_overlay(src + "_FINISH", src, marble, 3.94, 1.97, True, "Indian white marble (Rajnagar / Makrana) 2x4 ft, ground and polished on site")
    for src in ("FLOOR_R2", "FLOOR_KIT"):
        floor_overlay(src + "_FINISH", src, gvt_mat(), 3.94, 1.97, True, "matt GVT 600x1200 (marble only in the hall and passage)")
    green = mat("Marble_Green", (0.16, 0.30, 0.22), 0.15)
    W = 0.5; z = 0.012
    boxes("FLOOR_BORDER", [(X + 1.0, X + 1.0 + W, -44.25, -16.25, 0, z), (PX0 - 1.0 - W, PX0 - 1.0, -44.25, -16.25, 0, z),
                           (X + 1.0, PX0 - 1.0, -44.25, -44.25 + W, 0, z), (X + 1.0, PX0 - 1.0, -16.25 - W, -16.25, 0, z)], green, "finishes",
          "6 inch green marble border inlay")
    skirting(mat("Skirting_Marble", (0.92, 0.91, 0.89), 0.2), "4 inch marble skirting")
    common_wet_and_outside()
    lime = mat("Limewash_Clay", (0.72, 0.60, 0.48), 0.95)
    box("TV_WALL_LIMEWASH", X, X + 0.02, TV_Y0, TV_Y1, 0.33, 9.0, lime, "wall_finish", "limewash feature wall in warm clay, 8 ft wide")
    teak = mat("Teak", (0.45, 0.30, 0.18), 0.45)
    boxes("TV_WALL_SHELVES", [(X + 0.02, X + 0.9, TV_Y0 + 0.3, TV_Y0 + 2.0, 4.0, 4.12), (X + 0.02, X + 0.9, TV_Y0 + 0.3, TV_Y0 + 2.0, 5.6, 5.72),
                              (X + 0.02, X + 0.9, TV_Y1 - 2.0, TV_Y1 - 0.3, 4.0, 4.12), (X + 0.02, X + 0.9, TV_Y1 - 2.0, TV_Y1 - 0.3, 5.6, 5.72)], teak, "furniture", "solid teak floating shelves")
    tv_and_console(mat("TV_Black", (0.03, 0.03, 0.035), 0.15), teak, depth=0.02)
    guards(); entry(teak)
    living_and_dining(mat("Sofa_Cane", (0.78, 0.68, 0.52), 0.8), teak, mat("Chair_Cane", (0.66, 0.52, 0.34), 0.7))
    downlights(); ceiling_fan()


def fluted(name, x0, x1, y0, y1, z0, z1, mt, face, spec, pitch=0.25, w=0.12, d=0.05):
    """ridges on one face of a panel: face 'x+' (wall at x0, ridges stick out in +x) or 'y+'/'y-' """
    r = []
    if face == "x+":
        y = y0 + 0.06
        while y + w < y1: r.append((x1, x1 + d, y, y + w, z0, z1)); y += pitch
    elif face in ("y+", "y-"):
        x = x0 + 0.06
        while x + w < x1:
            r.append((x, x + w, y1, y1 + d, z0, z1) if face == "y+" else (x, x + w, y0 - d, y0, z0, z1)); x += pitch
    elif face == "x-":
        y = y0 + 0.06
        while y + w < y1: r.append((x0 - d, x0, y, y + w, z0, z1)); y += pitch
    if r: boxes(name, r, mt, "wall_finish", spec)

def build_panel():
    floors(gvt_mat(), "matt/satin GVT 600x1200, light warm greige stone look, rectified, 2 mm joints", 3.94, 1.97, True, skirt=mat("Skirting_GVT", (0.78, 0.75, 0.70), 0.5))
    wpc = mat("WPC_Teak", (0.55, 0.40, 0.27), 0.5); black = mat("Profile_Black", (0.08, 0.08, 0.08), 0.35, 0.8)
    # 1. west wall panelled from the main door frame to Pillar 1's wall column, TV in the middle
    Y0, Y1, Z0, Z1 = -35.5, MAIN_Y0 - 0.15, 0.33, 8.75
    box("FEATURE_WALL_PANEL", X, X + 0.08, Y0, Y1, Z0, Z1, wpc, "wall_finish", "WPC fluted panelling, whole wall 11 ft x 8'5\", teak")
    fluted("FEATURE_WALL_FLUTES", X, X + 0.08, Y0, Y1, Z0, Z1, wpc, "x+", "fluted ridges")
    boxes("FEATURE_WALL_FRAME", [(X, X + 0.16, Y0 - 0.06, Y0, Z0, Z1 + 0.06), (X, X + 0.16, Y0 - 0.06, Y1, Z1, Z1 + 0.06)], black, "wall_finish", "black aluminium end and top profile")
    box("FEATURE_WALL_LED", X + 0.13, X + 0.16, Y0 + 0.2, Y1 - 0.2, Z1 - 0.12, Z1 - 0.06, mat("LED_Warm", (1.0, 0.85, 0.6), 0.4, 0, 3.0), "lighting",
        "warm LED strip along the top", {"light": "strip", "lumens": 900})
    walnut = mat("Walnut", (0.36, 0.25, 0.17), 0.5)
    tv_and_console(mat("TV_Black", (0.03, 0.03, 0.035), 0.15), walnut)
    # 2. 3 ft half-wall panelling (wainscot) on the other hall walls, champagne aluminium cap
    sage = mat("Wainscot_Sage", (0.56, 0.62, 0.53), 0.55); cap = mat("Profile_Champagne", (0.78, 0.68, 0.50), 0.3, 0.9)
    T, ZH = 0.06, 3.0
    runs = [("W_WINDOW_WALL", (X, X + T, -45.25, -36.4), "x"), ("W_NORTH_OF_DOOR", (X, X + T, -19.45, -15.25), "x"), ("S_WALL", (X, B1X, -45.25, -45.25 + T), "y"),
            ("R1_WALL", (X, 13.0, -15.25 - T, -15.25), "y"),
            ("PASSAGE_E", (PX1, XE_, -13.25 - T, -13.25), "y"), ("EAST_N", (XE_ - T, XE_, R2D_Y1, -13.25), "x"), ("EAST_S", (XE_ - T, XE_, -24.0, R2D_Y0), "x")]
    panels, caps, stiles = [], [], []
    for nm, (a, b, c, d), axis in runs:
        panels.append((a, b, c, d, 0.0, ZH))
        if axis == "x":
            xa, xb = (b, b + 0.05) if a < 10 else (a - 0.05, a)
            caps.append((xa - (0.02 if a > 10 else 0), xb + (0.02 if a < 10 else 0), c, d, ZH - 0.08, ZH + 0.02))
            y = c + 2.0
            while y < d - 0.5: stiles.append((xa, xb, y - 0.1, y + 0.1, 0.33, ZH - 0.08)); y += 2.0
            stiles.append((xa, xb, c, d, 0.33, 0.5))
        else:
            ya, yb = (d, d + 0.05) if c < -40 else (c - 0.05, c)
            caps.append((a, b, ya - (0.02 if c > -40 else 0), yb + (0.02 if c < -40 else 0), ZH - 0.08, ZH + 0.02))
            x = a + 2.0
            while x < b - 0.5: stiles.append((x - 0.1, x + 0.1, ya, yb, 0.33, ZH - 0.08)); x += 2.0
            stiles.append((a, b, ya, yb, 0.33, 0.5))
    boxes("WAINSCOT_PANELS", panels, sage, "wall_finish", "3 ft half-wall panelling: WPC / HDHMR panels in satin sage, glued on a dry wall")
    boxes("WAINSCOT_STILES", stiles, sage, "wall_finish", "panel moulding strips every 2 ft (picture-frame look)")
    boxes("WAINSCOT_CAP", caps, cap, "wall_finish", "champagne anodised aluminium cap profile")
    # 3. pillars wrapped full height in fluted WPC
    for i, (y0, y1) in enumerate(PIL_Y):
        x0, x1, e = PX0, PX1, 0.05
        boxes(f"PILLAR_WRAP_{i+1}", [(x0 - e, x1 + e, y0 - e, y1 + e, 0.0, 9.0)], wpc, "wall_finish", "pillar wrapped in fluted WPC, full height to the beam")
        fluted(f"PILLAR_FLUTES_{i+1}_E", x0 - e, x1 + e, y0 - e, y1 + e, 0.0, 9.0, wpc, "x+", "")
        fluted(f"PILLAR_FLUTES_{i+1}_W", x0 - e, x1 + e, y0 - e, y1 + e, 0.0, 9.0, wpc, "x-", "")
        fluted(f"PILLAR_FLUTES_{i+1}_N", x0 - e, x1 + e, y0 - e, y1 + e, 0.0, 9.0, wpc, "y+", "")
        fluted(f"PILLAR_FLUTES_{i+1}_S", x0 - e, x1 + e, y0 - e, y1 + e, 0.0, 9.0, wpc, "y-", "")
    entry(walnut)
    living_and_dining(mat("Sofa_Oatmeal", (0.72, 0.66, 0.57), 0.9), walnut, mat("Chair_Cane", (0.66, 0.52, 0.34), 0.7))
    downlights(); ceiling_fan()


# ---------------------------------------------------------------- V1.4 "Best of both": this guide + the Materials Field Guide (6 Nov 2026)
def upgrade_tub_geyser(litres=50):
    """the tub needs ~60 L of hot water: the V1.2 15 L geyser in the tub room becomes a 50 L one (same spot, bigger box)"""
    c = bpy.data.collections.get("19_ROOM2_ENSUITE")
    if not c: return None
    g = next((o for o in c.all_objects if "GEYSER" in o.name and o.type == 'MESH'), None)
    if not g: return None
    mw = g.matrix_world; inv = mw.inverted()
    ws = [mw @ v.co for v in g.data.vertices]
    x0, x1 = min(v.x for v in ws), max(v.x for v in ws); y0, y1 = min(v.y for v in ws), max(v.y for v in ws); z0, z1 = min(v.z for v in ws), max(v.z for v in ws)
    W, D, Hh = m(1.5), m(1.45), m(2.4)                # 50 L vertical storage geyser, about 1'6" x 1'5" x 2'5"
    yc = (y0 + y1) / 2
    nx0, nx1, ny0, ny1, nz0, nz1 = x0, x0 + D, yc - W / 2, yc + W / 2, z1 - Hh, z1
    f = lambda a, lo, hi, nlo, nhi: nlo + (a - lo) / (hi - lo) * (nhi - nlo) if hi > lo else nlo
    for v, w in zip(g.data.vertices, ws):
        v.co = inv @ Vector((f(w.x, x0, x1, nx0, nx1), f(w.y, y0, y1, ny0, ny1), f(w.z, z0, z1, nz0, nz1)))
    g["spec"] = f"{litres} L storage geyser, 5-star, on its own 16 A point (enough hot water to half-fill the 1500 x 750 tub; a 15 L one is not)"
    return g.name

def gypsum_border(mt, led):
    """2 ft gypsum border on GI framing round the main hall, dropped just below the beams, warm cove light on the inner edge, downlights in the band"""
    z0, z1 = 8.95, H - 0.02
    xa, xb, ya, yb, B = X, PX0, -45.25, -15.25, 2.0
    bands = [(xa, xa + B, ya, yb, z0, z1), (xb - B, xb, ya, yb, z0, z1), (xa + B, xb - B, ya, ya + B, z0, z1), (xa + B, xb - B, yb - B, yb, z0, z1)]
    sbox("GYPSUM_BORDER", *bands[0][:6], mt, "ceiling", "2 ft gypsum border on GI framing, 12.5 mm board, taped joints; drops to just below the beams", w=0.3, seg=1)
    for i, bx in enumerate(bands[1:]):
        sbox(f"GYPSUM_BORDER_{i+2}", *bx, mt, "ceiling", "", w=0.3, seg=1)
    t = 0.04
    coves = [(xa + B, xa + B + t, ya + B, yb - B), (xb - B - t, xb - B, ya + B, yb - B)]
    for i, (a, b, c, d) in enumerate(coves):
        box(f"COVE_LED_{i+1}", a, b, c, d, z0 + 0.08, z0 + 0.14, led, "lighting", "warm 3000K cove LED strip in an aluminium channel, on a dimmer", {"light": "strip", "lumens": 1200})
    for i, (x, y) in enumerate([(x, y) for x in (xa + B / 2, xb - B / 2) for y in (-18.5, -25.0, -34.0, -41.5)]):
        cyl(f"DOWNLIGHT_{i+1}", x, y, 0.28, z0 - 0.03, z0 + 0.01, mat("Downlight", (1.0, 0.92, 0.8), 0.4, 0, 3.0), "lighting", "10 W LED downlight 3000K in the border", 20, {"light": "spot", "lumens": 800})

def build_best():
    # floors: 2 x 4 ft GVT only where it shows (hall + passage), easy 2 x 2 ft elsewhere; same shade everywhere
    skirt = mat("Skirting_GVT", (0.78, 0.75, 0.70), 0.5)
    floors(gvt_mat(), "smooth matt / satin GVT 600x1200 (hall and passage only, laid with levelling clips by a mason who has done 2x4 before); warm greige", 3.94, 1.97, True,
           srcs=("FLOOR_HALL", "FLOOR_PAS"), skirt=skirt)
    gvt2 = tex_mat("GVT_Matt_Greige_2x2", tile_image(f"{OPT}_gvt2", 512, 512, (0.80, 0.77, 0.72), 0.035, (0.66, 0.63, 0.59), 2, veins=True, seed=4), 0.55, (0.80, 0.77, 0.72))
    for src in ("FLOOR_R2", "FLOOR_KIT"):
        floor_overlay(src + "_FINISH", src, gvt2, 1.97, 1.97, False, "smooth matt / satin GVT 600x600, same shade as the hall: easier to lay and cut in rooms")
    # TV wall: one flat matt laminate rectangle on BWP ply, low closed cabinet, warm LED along the top
    lam = mat("HPL_LightOak", (0.70, 0.58, 0.44), 0.6); black = mat("Profile_Black", (0.08, 0.08, 0.08), 0.35, 0.8)
    Y0, Y1, Z0, Z1, T = TV_YC - 3.5, TV_YC + 3.5, 0.33, 7.33, 0.07
    sbox("TV_PANEL", X, X + T, Y0, Y1, Z0, Z1, lam, "wall_finish", "flat matt HPL laminate (light oak) on 18 mm BWP plywood, 7 x 7 ft; cables in a conduit behind, access flap at the socket", w=0.15, seg=1)
    boxes("TV_PANEL_JOINT", [(X + T, X + T + 0.005, TV_YC - 0.01, TV_YC + 0.01, Z0, Z1)], mat("Groove_Dark", (0.06, 0.05, 0.05), 0.6), "wall_finish", "")
    boxes("TV_PANEL_PROFILE", [(X, X + T + 0.05, Y0, Y1, Z1, Z1 + 0.05)], black, "wall_finish", "slim black aluminium top profile hiding the LED")
    box("TV_PANEL_LED", X + T, X + T + 0.03, Y0 + 0.2, Y1 - 0.2, Z1 - 0.06, Z1, mat("LED_Warm", (1.0, 0.85, 0.6), 0.4, 0, 3.0), "lighting", "warm LED strip washing down the panel, dimmable", {"light": "strip", "lumens": 600})
    oak = mat("Oak", (0.62, 0.48, 0.33), 0.55)
    tv_and_console(mat("TV_Black", (0.03, 0.03, 0.035), 0.15), oak, depth=T, console=False)
    sbox("TV_CABINET", X + T, X + 1.5, TV_YC - 3.0, TV_YC + 3.0, 0.4, 1.75, oak, "furniture", "closed low TV cabinet 6 ft, floor-standing on legs (no wall load), vents at the back", w=0.4)
    boxes("TV_CABINET_GROOVES", [(X + 1.5, X + 1.52, TV_YC + k - 0.015, TV_YC + k + 0.015, 0.45, 1.7) for k in (-1.0, 1.0)], mat("Groove_Dark", (0.06, 0.05, 0.05), 0.6), "furniture", "")
    for i, (yy) in enumerate((TV_YC - 2.8, TV_YC + 2.8)):
        for xx in (X + 0.3, X + 1.3):
            cone(f"TV_CABINET_LEG_{i+1}_{int(xx*10)}", xx, yy, 0.05, 0.07, 0.0, 0.4, black, "furniture", "", 10)
    console_decor(top_z=1.75)
    # entry: 3'6" tile band where shoes and bags brush the wall, aluminium top trim; mirror above
    wt = tex_mat("Wall_Tile_Matt", tile_image(f"{OPT}_walltile", 512, 256, (0.86, 0.84, 0.80), 0.02, (0.74, 0.72, 0.68), 2, seed=6), 0.5, (0.86, 0.84, 0.80))
    wall_slab("ENTRY_DADO", -19.45, -15.25, 0.0, 3.5, X, X + 0.05, wt, 1.97, 0.98, "3'6\" wall-tile band (300 x 600 matt, light stone) on the entry wall (north of the main door) only, tile adhesive, matching grout")
    box("ENTRY_DADO_TRIM", X, X + 0.08, -19.45, -15.25, 3.5, 3.56, mat("Profile_Alu", (0.75, 0.75, 0.76), 0.3, 0.9), "wall_finish", "anodised aluminium top trim on the tile band")
    guards(4.0); entry(oak)
    gypsum_border(mat("Gypsum_White", (0.95, 0.95, 0.93), 0.8), mat("LED_Cove", (1.0, 0.86, 0.62), 0.4, 0, 2.5))
    living_and_dining(mat("Sofa_Oatmeal", (0.72, 0.66, 0.57), 0.9), oak, mat("Chair_Cane", (0.66, 0.52, 0.34), 0.7))
    ceiling_fan()

OPTIONS = [("HALL_REC", "20_HALL_RECOMMENDED", build_rec), ("HALL_BUDGET", "21_HALL_BUDGET", build_budget),
           ("HALL_LONG", "22_HALL_LONG_LASTING", build_long), ("HALL_MARBLE", "23_HALL_MARBLE", build_marble),
           ("HALL_PANEL", "24_HALL_PANELLED", build_panel), ("HALL_BEST", "25_HALL_BEST_OF_BOTH", build_best)]
TAG.update({"HALL_LONG": "HL", "HALL_MARBLE": "HM", "HALL_PANEL": "HP", "HALL_BEST": "HBB"})

def run(show="HALL_REC"):
    global OPT, COL
    door = main_door_v2()
    geyser = upgrade_tub_geyser()
    for _, cname, _ in OPTIONS:
        c = bpy.data.collections.get(cname)
        if c:
            for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
    for x in [x for x in bpy.data.meshes if x.users == 0]: bpy.data.meshes.remove(x)
    for x in [x for x in bpy.data.materials if x.users == 0]: bpy.data.materials.remove(x)
    for x in [x for x in bpy.data.images if x.users == 0]: bpy.data.images.remove(x)
    MATS.clear(); counts = {"door": door, "geyser": geyser}
    for key, cname, fn in OPTIONS:
        OPT = key; COL = bpy.data.collections.new(cname); bpy.context.scene.collection.children.link(COL)
        COL["design_option"] = key
        fn(); counts[key] = len(COL.objects)
    for key, cname, _ in OPTIONS:
        bpy.context.view_layer.layer_collection.children[cname].hide_viewport = key != show
        bpy.data.collections[cname].hide_render = key != show
    return counts
