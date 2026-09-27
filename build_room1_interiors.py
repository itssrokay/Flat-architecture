# Room 1 interior design options for MyFlat V1.1 (architecture frozen).
# Run with MyFlat_V1_1_Architecture.blend open; adds collections
#   13_ROOM1_DEFAULT, 14_ROOM1_OPTION_A, 15_ROOM1_OPTION_B, 16_ROOM1_OPTION_C
# Every object: design_category, design_option, status=DESIGN, spec.
# Units: feet. Room 1 frame: x=0 west inner face (balcony opening), x=12.583 east inner face,
# y=0 north inner face, y=-11.167 face of raised south wall (x 0..7.25), y=-14.5 south wall (x 7.25..12.583).
import bpy, bmesh, math
from mathutils import Vector

FT = 0.3048; IN = 1 / 12
RW, XSTEP, YW, YS = 12 + 7 * IN, 7.25, -(11 + 2 * IN), -14.5
OPN_Y0, OPN_Y1, OPN_H = YW, -0.75, 7.0          # balcony structural opening (x -1.25..0)
W1_X0, W1_X1, W1_Z0, W1_Z1 = 3.4, 7.4, 3.0, 7.0  # W1 structural opening in north wall (y 0..0.75)
DOOR_Y0, DOOR_Y1 = -12.333, -9.667                # Room 1 exit (east wall)
BAL_X0, BAL_X1, BAL_Y0, BAL_Y1, BAL_Z = -4.35, -1.25, -13.9, 0.7, -2 * IN   # usable balcony floor
H = 10.0

def m(v): return v * FT
OPT = None; COL = None; MATS = {}
TAG = {'DEFAULT': 'DEF', 'OPTION_A': 'OPA', 'OPTION_B': 'OPB', 'OPTION_C': 'OPC'}

def mat(name, rgb, rough=0.6, metal=0.0, alpha=1.0, emit=0.0):
    key = f"{OPT}_{name}"
    if key in MATS: return MATS[key]
    mt = bpy.data.materials.new(key); mt.use_nodes = True
    b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try: mt.surface_render_method = 'BLENDED'
        except Exception: pass
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    mt.diffuse_color = (*rgb, alpha); MATS[key] = mt; return mt

def _obj(name, me, mt, cat, spec, loc=(0, 0, 0), rot=0.0):
    o = bpy.data.objects.new(f"R1_{TAG[OPT]}_{name}", me); o.location = Vector([m(v) for v in loc]); o.rotation_euler.z = rot
    if mt: o.data.materials.append(mt)
    COL.objects.link(o)
    o["design_category"] = cat; o["design_option"] = OPT; o["status"] = "DESIGN"
    if spec: o["spec"] = spec
    return o

def _bm_box(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new((m(a), m(b), m(c))) for a, b, c in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])

def boxes(name, bxs, mt, cat, spec="", origin=(0, 0, 0), rot=0.0, pivot=None, interact=None):
    """several boxes in ONE object. Default: coords are local to origin.
    pivot=(px,py): coords are WORLD, object origin placed at the pivot (hinge / slide reference).
    interact: dict of viewer interaction props, e.g. {"interact":"hinge","open_deg":100,"group":"X"}"""
    if pivot is not None:
        px, py = pivot; bxs = [(a - px, b - px, c - py, d - py, e, f) for (a, b, c, d, e, f) in bxs]; origin = (px, py, 0)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for b in bxs: _bm_box(bm, *b)
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec, origin, rot)
    for k, v in (interact or {}).items(): o[k] = v
    return o

def box(name, x0, x1, y0, y1, z0, z1, mt, cat, spec="", interact=None):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return boxes(name, [(x0-cx, x1-cx, y0-cy, y1-cy, 0, z1-z0)], mt, cat, spec, (cx, cy, z0), interact=interact)

def HINGE(group, deg, label="Open / close"): return {"interact": "hinge", "open_deg": float(deg), "group": group, "label": label}
def SLIDE(group, dx=0.0, dy=0.0, label="Slide open / closed"): return {"interact": "slide", "slide_ft": [float(dx), float(dy), 0.0], "group": group, "label": label}
def TOGGLE(group, label="Draw / open"): return {"interact": "toggle", "group": group, "label": label}

def cyl(name, cx, cy, r, z0, z1, mt, cat, spec="", n=24):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=m(r), radius2=m(r), depth=m(z1 - z0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, m(z1 - z0) / 2)); bm.to_mesh(me); bm.free()
    return _obj(name, me, mt, cat, spec, (cx, cy, z0))

def blob(name, cx, cy, cz, r, mt, cat, spec="", sz=1.0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=m(r))
    for v in bm.verts: v.co.z *= sz
    bm.to_mesh(me); bm.free(); return _obj(name, me, mt, cat, spec, (cx, cy, cz))

def curtain(name, p0, p1, z0, z1, mt, cat, spec="", amp=0.07, waves=None, interact=None):
    """pleated curtain surface from p0 to p1 (x,y) - thin wavy sheet"""
    a, b = Vector(p0), Vector(p1); L = (b - a).length; d = (b - a).normalized(); nrm = Vector((-d.y, d.x))
    n = max(8, int(L / 0.18)); waves = waves or max(2, int(L / 0.45))
    me = bpy.data.meshes.new(name); bm = bmesh.new(); cols = []
    for i in range(n + 1):
        t = i / n; off = amp * math.sin(t * waves * 2 * math.pi)
        p = a + d * (t * L) + nrm * off
        cols.append((bm.verts.new((m(p.x), m(p.y), m(z0))), bm.verts.new((m(p.x), m(p.y), m(z1)))))
    for i in range(n): bm.faces.new((cols[i][0], cols[i+1][0], cols[i+1][1], cols[i][1]))
    bm.to_mesh(me); bm.free(); o = _obj(name, me, mt, cat, spec)
    for k, v in (interact or {}).items(): o[k] = v
    return o

def plant(name, cx, cy, z, pot_r, pot_h, leaf_r, pot_mt, spec="", tall=1.0):
    cyl(name + "_POT", cx, cy, pot_r, z, z + pot_h, pot_mt, "plants", spec)
    blob(name + "_LEAVES", cx, cy, z + pot_h + leaf_r * tall * 0.9, leaf_r, mat("Foliage", (0.22, 0.42, 0.2), 0.8), "plants", spec, sz=tall)

# ---------------------------------------------------------------- composite builders
def bed(ox, oy, ang_deg, w, L, s):
    """head at (ox,oy) on wall; u axis points from head to foot (ang)."""
    a = math.radians(ang_deg); hw = w / 2
    hb = s.get("hb_w", w + 0.5) / 2
    boxes("BED_HEADBOARD", [(0, s.get("hb_t", 0.25), -hb, hb, s.get("hb_z0", 0.3), s["hb_h"])], s["hb_mat"], "furniture", s["hb_spec"], (ox, oy, 0), a)
    bz0, bz1 = s.get("base_z", (0.3, 1.15))
    boxes("BED_BASE", [(0.25, L + 0.35, -hw - 0.08, hw + 0.08, bz0, bz1)], s["base_mat"], "furniture", s["base_spec"], (ox, oy, 0), a)
    if bz0 > 0.05:
        boxes("BED_PLINTH", [(0.45, L + 0.15, -hw + 0.2, hw - 0.2, 0, bz0)], mat("Plinth", (0.12, 0.12, 0.12), 0.7), "furniture", "recessed plinth / legs", (ox, oy, 0), a)
    t = bz1 + 0.62
    boxes("BED_MATTRESS", [(0.3, L + 0.3, -hw, hw, bz1, t)], mat("Mattress", (0.95, 0.94, 0.92), 0.9), "soft_furnishing", "Queen mattress 60\" x 78\", 8\" pocket-spring", (ox, oy, 0), a)
    boxes("BED_DUVET", [(1.7, L + 0.36, -hw - 0.05, hw + 0.05, t - 0.1, t + 0.08)], s["duvet"], "soft_furnishing", s.get("duvet_spec", "cotton duvet"), (ox, oy, 0), a)
    boxes("BED_THROW", [(L - 0.9, L + 0.38, -hw - 0.07, hw + 0.07, t + 0.02, t + 0.12)], s["throw"], "soft_furnishing", "throw / bed runner", (ox, oy, 0), a)
    boxes("BED_PILLOWS", [(0.45, 1.45, -hw + 0.15, -0.08, t, t + 0.42), (0.45, 1.45, 0.08, hw - 0.15, t, t + 0.42)], mat("Pillow", (0.97, 0.96, 0.94), 0.9), "soft_furnishing", "2 pillows", (ox, oy, 0), a)
    boxes("BED_CUSHIONS", [(1.3, 1.75, -hw + 0.6, hw - 0.6, t, t + 0.9)], s["cushion"], "soft_furnishing", "accent cushions", (ox, oy, 0), a)

def wardrobe_alcove(style):
    """wardrobe filling the south-east alcove, 2' deep, front faces north. Hollow carcass with
    real internals; each shutter is its own object (hinged or sliding) so it can be opened."""
    x0, x1, yb, yf = XSTEP + 0.05, RW - 0.05, YS + 0.05, YS + 2.0
    top = style.get("top", 7.5); t = 0.06; fz = yf - 0.14; zb = 0.33
    body = style["body"]; inner = mat("Wardrobe_Interior", (0.9, 0.89, 0.86), 0.6)
    boxes("WARDROBE_CARCASS", [(x0, x0 + t, yb, fz, zb, top), (x1 - t, x1, yb, fz, zb, top), (x0, x1, yb, yb + t, zb, top),
                                (x0, x1, yb, fz, top - t, top), (x0, x1, yb, fz, zb, zb + t)], body, "wardrobe", style["spec"])
    box("WARDROBE_PLINTH", x0 + 0.05, x1 - 0.05, yb, fz - 0.1, 0, zb, mat("Plinth", (0.12, 0.12, 0.12), 0.7), "wardrobe", "4\" recessed plinth (mopping clearance)")
    n = style["doors"]; W = x1 - x0; sec = 3 if n >= 3 else 2
    ints = []; rods = []; cloth = []
    for i in range(1, sec):
        x = x0 + i * W / sec; ints.append((x - t / 2, x + t / 2, yb + t, fz, zb + t, top - t))
    xs = [(x0 + i * W / sec + t, x0 + (i + 1) * W / sec - t) for i in range(sec)]
    # section 1: hanging (shirts) over 2 drawers
    a, b = xs[0]; ints += [(a, b, yb + t, fz, 1.6, 1.66), (a, b, yb + t, fz, 6.2, 6.26)]
    ints += [(a + 0.05, b - 0.05, fz - 0.05, fz, zb + 0.1, 0.95), (a + 0.05, b - 0.05, fz - 0.05, fz, 0.97, 1.55)]
    rods.append((a, b, (yb + fz) / 2 - 0.02, (yb + fz) / 2 + 0.02, 5.9, 5.94))
    cloth += [(a + 0.1 + k * 0.18, a + 0.16 + k * 0.18, yb + 0.35, fz - 0.3, 3.3, 5.85) for k in range(int((b - a - 0.2) / 0.18))]
    # section 2: shelves with folded stacks
    a, b = xs[1]
    for z in (1.4, 2.6, 3.8, 5.0, 6.2): ints.append((a, b, yb + t, fz, z, z + 0.06))
    for z in (1.46, 2.66, 3.86, 5.06): cloth.append((a + 0.15, b - 0.15, yb + 0.3, fz - 0.25, z, z + 0.5))
    if sec == 3:   # section 3: long hanging (sarees / dresses) + top shelf
        a, b = xs[2]; ints.append((a, b, yb + t, fz, 6.2, 6.26))
        rods.append((a, b, (yb + fz) / 2 - 0.02, (yb + fz) / 2 + 0.02, 5.9, 5.94))
        cloth += [(a + 0.1 + k * 0.2, a + 0.17 + k * 0.2, yb + 0.35, fz - 0.3, 1.2, 5.85) for k in range(int((b - a - 0.2) / 0.2))]
    boxes("WARDROBE_INTERNALS", ints, inner, "wardrobe", "internals: 18 mm HDHMR shelves, partition, 2 soft-close drawers, frosty-white laminate")
    boxes("WARDROBE_HANGING_RODS", rods, mat("Chrome", (0.8, 0.8, 0.82), 0.2, 1.0), "wardrobe", "oval SS hanging rods with LED profile above")
    boxes("WARDROBE_CONTENTS", cloth, mat("Clothes", (0.5, 0.55, 0.62), 0.9), "decor", "clothes (for scale)")
    if style.get("light"):
        boxes("WARDROBE_LED", [(x0 + t, x1 - t, fz - 0.06, fz - 0.03, top - 0.12, top - 0.09)], style["light"], "lighting", "sensor-operated LED strip inside wardrobe")
    sh, hd, ins = style["shutter"], style["handle"], style.get("inset")
    if style.get("sliding"):
        half = W / 2
        p1 = [(x0, x0 + half + 0.05, yf - 0.06, yf, zb, top)]
        p2 = [(x0 + half - 0.05, x1, yf - 0.13, yf - 0.07, zb, top)]
        boxes("WARDROBE_SLIDER_1", p1, sh, "wardrobe", style["shutter_spec"], pivot=(x0 + half / 2, yf), interact=SLIDE("WARDROBE_SLIDER_1", dx=half - 0.15, label="Slide wardrobe door"))
        if style.get("mirror"):
            boxes("WARDROBE_SLIDER_1_MIRROR", [(x0 + 0.2, x0 + half - 0.2, yf, yf + 0.03, 0.8, top - 0.6)], style["mirror"], "wardrobe", "full-height mirror", pivot=(x0 + half / 2, yf), interact=SLIDE("WARDROBE_SLIDER_1", dx=half - 0.15))
        boxes("WARDROBE_SLIDER_2", p2, sh, "wardrobe", style["shutter_spec"], pivot=(x1 - half / 2, yf), interact=SLIDE("WARDROBE_SLIDER_2", dx=-(half - 0.15), label="Slide wardrobe door"))
    else:
        g = 0.012
        for i in range(n):
            xa, xb = x0 + i * W / n + g, x0 + (i + 1) * W / n - g
            left = (i % 2 == 0); hx = xa if left else xb
            bx = [(xa, xb, yf - 0.06, yf, zb, top)]
            hb = [((xb - 0.12, xb - 0.08) if left else (xa + 0.08, xa + 0.12)) + (yf, yf + 0.06, 3.0, 5.2)]
            it = HINGE(f"WARDROBE_DOOR_{i+1}", 100 if left else -100, "Open / close wardrobe door")
            boxes(f"WARDROBE_DOOR_{i+1}", bx, sh, "wardrobe", style["shutter_spec"], pivot=(hx, yf), interact=it)
            boxes(f"WARDROBE_DOOR_{i+1}_HANDLE", hb, hd, "wardrobe", style["handle_spec"], pivot=(hx, yf), interact=it)
            if ins:
                boxes(f"WARDROBE_DOOR_{i+1}_INSET", [(xa + 0.22, xb - 0.22, yf, yf + 0.015, 1.2, top - 0.9)], ins, "wardrobe", style["inset_spec"], pivot=(hx, yf), interact=it)
    if style.get("loft"):
        boxes("WARDROBE_LOFT", [(x0, x1, yb, fz, top + 0.05, top + 0.11), (x0, x1, yb, fz, 9.89, 9.95), (x0, x1, yb, yb + t, top + 0.05, 9.95),
                                (x0, x0 + t, yb, fz, top + 0.05, 9.95), (x1 - t, x1, yb, fz, top + 0.05, 9.95)], body, "wardrobe", "loft storage for suitcases / quilts")
        boxes("WARDROBE_LOFT_CONTENTS", [(x0 + 0.3, x0 + 2.2, yb + 0.2, fz - 0.2, top + 0.11, top + 1.6), (x0 + 2.5, x1 - 0.4, yb + 0.2, fz - 0.3, top + 0.11, top + 1.0)], mat("Suitcase", (0.25, 0.3, 0.4), 0.6), "decor", "suitcases (for scale)")
        for i in range(n):
            xa, xb = x0 + i * W / n + 0.012, x0 + (i + 1) * W / n - 0.012; left = (i % 2 == 0)
            boxes(f"WARDROBE_LOFT_DOOR_{i+1}", [(xa, xb, yf - 0.06, yf, top + 0.07, 9.93)], sh, "wardrobe", "loft shutter, push-to-open",
                  pivot=(xa if left else xb, yf), interact=HINGE(f"WARDROBE_LOFT_DOOR_{i+1}", 95 if left else -95, "Open / close loft"))

def floor_finish(mt, spec):
    boxes("FLOOR_FINISH", [(0, RW, YW, 0, 0, 0.02), (XSTEP, RW, YS, YW, 0, 0.02)], mt, "finishes", spec)

def skirting(mt):
    k = 0.33; t = 0.04
    boxes("SKIRTING", [(0, W1_X0 - 0.3, -t, 0, 0.02, k), (W1_X0 - 0.3, RW, -t, 0, 0.02, k), (RW - t, RW, DOOR_Y1, 0, 0.02, k),
                       (RW - t, RW, YS, DOOR_Y0, 0.02, k), (XSTEP, RW, YS, YS + t, 0.02, k), (XSTEP, XSTEP + t, YS, YW, 0.02, k),
                       (0, XSTEP, YW, YW + t, 0.02, k)], mt, "finishes", "4\" skirting")

def ceiling_band(mt, drop, band, spec, cove_mt=None, pelmet=True):
    """perimeter false-ceiling band (gypsum) with optional cove LED; raft stays at slab."""
    z0 = H - drop; bx = [(0, RW, -band, 0, z0, H), (0, RW, YW, YW + band, z0, H), (0, band + (0.5 if pelmet else 0), YW, 0, z0, H), (RW - band, RW, YW, 0, z0, H)]
    boxes("FALSE_CEILING_BAND", bx, mt, "ceiling", spec)
    box("FALSE_CEILING_ALCOVE", XSTEP, RW, YS + 2.05, YW, z0, H, mt, "ceiling", "flat gypsum strip in front of wardrobe loft")
    if cove_mt:
        c = 0.06; zc = z0 - 0.02
        bx = [(band, RW - band, -band - c, -band, zc, z0), (band, RW - band, YW + band, YW + band + c, zc, z0),
              (band + (0.5 if pelmet else 0), band + (0.5 if pelmet else 0) + c, YW + band, -band, zc, z0), (RW - band - c, RW - band, YW + band, -band, zc, z0)]
        boxes("COVE_LED", bx, cove_mt, "lighting", "2700K warm-white LED cove strip, 10 W/m, dimmable")
    return z0

def downlights(pts, z, mt, spec="6 W COB downlight, 3000K, 36 deg"):
    for i, (x, y) in enumerate(pts):
        cyl(f"DOWNLIGHT_{i+1}", x, y, 0.16, z - 0.03, z, mt, "lighting", spec, 16)

def track_curtains(prefix, p0, p1, ztop, sheer_mt, heavy_mt, stack=1.3, spec_sheer="", spec_heavy="", rod_mt=None, side=None):
    a, b = Vector(p0), Vector(p1); d = (b - a).normalized()
    curtain(prefix + "_SHEER", p0, p1, 0.08, ztop - 0.1, sheer_mt, "soft_furnishing", spec_sheer, amp=0.05, interact=TOGGLE(prefix + "_SHEER", "Draw / open sheer"))
    off = Vector((-d.y, d.x)) * (-0.18 if side is None else side)
    s0a, s0b = a + off, a + off + d * stack; s1a, s1b = b + off - d * stack, b + off
    curtain(prefix + "_DRAPE_L", tuple(s0a), tuple(s0b), 0.05, ztop - 0.1, heavy_mt, "soft_furnishing", spec_heavy, amp=0.12, waves=4)
    curtain(prefix + "_DRAPE_R", tuple(s1a), tuple(s1b), 0.05, ztop - 0.1, heavy_mt, "soft_furnishing", spec_heavy, amp=0.12, waves=4)
    rm = rod_mt or mat("Track", (0.85, 0.85, 0.85), 0.4, 0.5)
    lo, hi = a + off * 0.5, b + off * 0.5
    boxes(prefix + "_TRACK", [(min(lo.x, hi.x) - 0.03, max(lo.x, hi.x) + 0.03, min(lo.y, hi.y) - 0.03, max(lo.y, hi.y) + 0.03, ztop - 0.08, ztop)], rm, "soft_furnishing", "ceiling-mounted double curtain track")

# ---- window W1 (north wall, y 0 inner .. 0.75 outer) ------------------------------
def w1_frame(frame_mt, spec, depth=(0.2, 0.55), fw=0.17):
    y0, y1 = depth; x0, x1, z0, z1 = W1_X0, W1_X1, W1_Z0, W1_Z1
    boxes("W1_OUTER_FRAME", [(x0, x0 + fw, y0, y1, z0, z1), (x1 - fw, x1, y0, y1, z0, z1), (x0, x1, y0, y1, z0, z0 + fw), (x0, x1, y0, y1, z1 - fw, z1)], frame_mt, "fenestration", spec)

def sash(name, x0, x1, z0, z1, y0, y1, fr_mt, gl_mt, cat_spec, fw=0.14, mid=None, hinge=None, slide=None):
    """hinge=('L'|'R', 'out'|'in', deg) rotates about the left/right jamb; slide=dx (ft)."""
    bx = [(x0, x0 + fw, y0, y1, z0, z1), (x1 - fw, x1, y0, y1, z0, z1), (x0, x1, y0, y1, z0, z0 + fw), (x0, x1, y0, y1, z1 - fw, z1)]
    if mid: bx.append((x0, x1, y0, y1, mid - fw / 2, mid + fw / 2))
    yc = (y0 + y1) / 2
    gl = [(x0 + fw, x1 - fw, yc - 0.015, yc + 0.015, z0 + fw, z1 - fw)]
    piv, it = None, None
    if hinge:
        side, way, deg = hinge; piv = (x0 if side == 'L' else x1, yc)
        sign = (1 if way == 'out' else -1) * (1 if side == 'L' else -1)   # +y = outside (north)
        it = HINGE(name, sign * deg, "Open / close window")
    elif slide:
        piv = ((x0 + x1) / 2, yc); it = SLIDE(name, dx=slide, label="Slide window open / closed")
    if piv:
        boxes(name + "_SASH", bx, fr_mt, "fenestration", cat_spec, pivot=piv, interact=it)
        boxes(name + "_GLASS", gl, gl_mt, "fenestration", cat_spec, pivot=piv, interact=it)
    else:
        boxes(name + "_SASH", bx, fr_mt, "fenestration", cat_spec)
        box(name + "_GLASS", *gl[0], gl_mt, "fenestration", cat_spec)

def w1_sill(mt, spec, proj=0.3):
    box("W1_SILL", W1_X0 - 0.15, W1_X1 + 0.15, -proj, 0.2, W1_Z0 - 0.08, W1_Z0, mt, "fenestration", spec)
    box("W1_DRIP_SILL", W1_X0 - 0.1, W1_X1 + 0.1, 0.55, 0.95, W1_Z0 - 0.1, W1_Z0 - 0.02, mt, "fenestration", "external sill with drip groove, slopes out")

def w1_grill(mt, spec, pitch=0.42, y=0.64):
    bx = [(x, x + 0.05, y, y + 0.05, W1_Z0 + 0.05, W1_Z1 - 0.05) for x in [W1_X0 + 0.2 + i * pitch for i in range(int((W1_X1 - W1_X0 - 0.3) / pitch) + 1)]]
    bx += [(W1_X0 + 0.1, W1_X1 - 0.1, y, y + 0.05, z, z + 0.05) for z in (W1_Z0 + 1.3, W1_Z1 - 1.3)]
    boxes("W1_SAFETY_GRILL", bx, mt, "fenestration", spec)

# ---- balcony opening (west wall x -1.25..0, y OPN_Y0..OPN_Y1, z 0..7) ----------------
def bd_frame(mt, spec, x0=-0.9, x1=-0.35, fw=0.2):
    y0, y1, z1 = OPN_Y0, OPN_Y1, OPN_H
    boxes("BALCONY_DOOR_FRAME", [(x0, x1, y0, y0 + fw, 0, z1), (x0, x1, y1 - fw, y1, 0, z1), (x0, x1, y0, y1, z1 - fw, z1), (x0, x1, y0, y1, -0.02, 0.06)], mt, "fenestration", spec)

def bd_panel(name, xc, ya, yb, fr_mt, gl_mt, spec, fw=0.2, th=0.12, z0=0.06, z1=OPN_H - 0.2, mid=None, slide_dy=None, extra=None):
    """balcony door leaf; slide_dy (ft, along the wall, - = south) makes it a sliding leaf in the viewer.
    extra = list of (name, boxes, material) that move with the leaf (e.g. its handle)."""
    bx = [(xc - th, xc + th, ya, ya + fw, z0, z1), (xc - th, xc + th, yb - fw, yb, z0, z1), (xc - th, xc + th, ya, yb, z0, z0 + fw + 0.15), (xc - th, xc + th, ya, yb, z1 - fw, z1)]
    if mid: bx.append((xc - th, xc + th, ya, yb, mid - 0.07, mid + 0.07))
    gl = [(xc - 0.02, xc + 0.02, ya + fw, yb - fw, z0 + fw + 0.15, z1 - fw)]
    it = SLIDE(name, dy=slide_dy, label="Slide door open / closed") if slide_dy else None
    piv = (xc, (ya + yb) / 2)
    boxes(name + "_FRAME", bx, fr_mt, "fenestration", spec, pivot=piv, interact=it)
    boxes(name + "_GLASS", gl, gl_mt, "fenestration", spec, pivot=piv, interact=it)
    for (en, eb, em) in (extra or []):
        boxes(en, eb, em, "fenestration", spec, pivot=piv, interact=it)

def handle_v(name, x, y, mt, spec, z=3.4, L=1.0):
    box(name, x - 0.04, x + 0.04, y - 0.04, y + 0.04, z, z + L, mt, "fenestration", spec)

def threshold(mt, spec):
    box("BALCONY_THRESHOLD", -1.25, 0.0, OPN_Y0, OPN_Y1, -0.06, 0.0, mt, "fenestration", spec)
    box("BALCONY_THRESHOLD_NOSING", -1.45, -1.25, OPN_Y0, OPN_Y1, -0.2, -0.04, mt, "fenestration", "sloped nosing to balcony (1:50 fall) - water check")

def balcony_floor(mt, spec):
    box("BALCONY_FLOOR_FINISH", BAL_X0, BAL_X1, BAL_Y0, BAL_Y1, BAL_Z, BAL_Z + 0.03, mt, "balcony", spec)

def outdoor_light(mt, spec, y=-12.4, z=6.6):
    box("BALCONY_WALL_LIGHT", -1.45, -1.25, y - 0.25, y + 0.25, z, z + 0.5, mt, "lighting", spec)

# ================================================================ OPTIONS
def build_default():
    oak = mat("Oak_Laminate", (0.62, 0.45, 0.3), 0.55); off = mat("OffWhite_Matt", (0.93, 0.91, 0.87), 0.6)
    sage = mat("Sage_Fabric", (0.55, 0.6, 0.5), 0.9); rust = mat("Rust_Fabric", (0.66, 0.34, 0.22), 0.9)
    charcoal = mat("Charcoal_Alu", (0.18, 0.19, 0.2), 0.35, 0.6); glass = mat("Clear_Glass", (0.75, 0.88, 0.95), 0.05, alpha=0.25)
    mesh = mat("Mesh", (0.2, 0.2, 0.22), 0.8, alpha=0.55); granite = mat("Granite_Black", (0.1, 0.1, 0.11), 0.25)
    light = mat("LED", (1.0, 0.86, 0.66), 0.5, emit=6.0); gyp = mat("Gypsum_White", (0.97, 0.97, 0.95), 0.9)
    brass = mat("Brass", (0.78, 0.6, 0.3), 0.3, 0.9)
    floor_finish(mat("Tile_Greige", (0.8, 0.76, 0.7), 0.5), "Matte vitrified tile 800x1600 mm, warm greige (Kajaria/Somany class)")
    skirting(mat("Skirting", (0.7, 0.66, 0.6), 0.5))
    # accent wall behind bed: fluted laminate panel
    fl = [(RW - 0.08, RW, y, y + 0.14, 0, 8.0) for y in [-8.3 + i * 0.2 for i in range(int(7.6 / 0.2))]]
    boxes("HEADBOARD_WALL_FLUTED", fl + [(RW - 0.05, RW, -8.35, -0.7, 0, 8.0)], oak, "finishes", "fluted oak laminate panel on 12 mm ply, 8' high, behind bed")
    box("ACCENT_BAND_HEADBOARD", RW - 0.1, RW - 0.08, -8.35, -0.7, 8.0, 8.05, brass, "finishes", "brass-finish trim")
    bed(RW - 0.1, -4.5, 180, 5.0, 6.5, dict(hb_h=3.8, hb_mat=sage, hb_spec="upholstered sage headboard, 3'10\" high",
        base_mat=oak, base_spec="Queen bed, oak laminate, hydraulic storage", duvet=off, throw=rust, cushion=rust))
    for tag, y0 in (("N", -0.35), ("S", -7.15)):
        box(f"BEDSIDE_{tag}", RW - 1.55, RW - 0.12, y0 - 1.5, y0, 0.3, 1.9, oak, "furniture", "bedside table 18\"x17\", 2 drawers, wall-hung look")
        box(f"BEDSIDE_{tag}_PLINTH", RW - 1.45, RW - 0.2, y0 - 1.4, y0 - 0.1, 0, 0.3, charcoal, "furniture", "")
        box(f"WALL_LAMP_{tag}", RW - 0.45, RW - 0.12, y0 - 0.9, y0 - 0.6, 4.4, 4.9, light, "lighting", "adjustable reading wall light, 2700K")
    wardrobe_alcove(dict(doors=3, body=off, shutter=off, spec="3-door hinged wardrobe 5'3\" x 2' x 7'6\", BWP ply carcass",
                         shutter_spec="off-white matt laminate shutters, soft-close hinges", handle=charcoal, handle_spec="12\" black profile handles",
                         inset=oak, inset_spec="oak laminate vertical inset strip", loft=True, light=light))
    # study / dresser on the raised wall face
    box("STUDY_DESK_TOP", 1.2, 5.2, YW, YW + 1.75, 2.35, 2.5, oak, "furniture", "study-cum-dresser 4' x 1'9\", 30\" high")
    box("STUDY_DESK_DRAWERS", 3.7, 5.2, YW, YW + 1.6, 0.3, 2.35, off, "furniture", "2-drawer pedestal")
    box("STUDY_WALL_SHELF", 1.2, 5.2, YW, YW + 0.8, 5.2, 5.3, oak, "furniture", "floating shelf")
    box("STUDY_MIRROR", 1.8, 3.2, YW, YW + 0.05, 3.2, 5.0, mat("Mirror", (0.85, 0.9, 0.92), 0.02, 1.0), "furniture", "vanity mirror, frameless")
    boxes("STUDY_CHAIR", [(0, 1.5, 0, 1.5, 1.4, 1.55), (0, 1.5, 0, 0.12, 1.55, 2.9), (0.6, 0.9, 0.6, 0.9, 0, 1.4)], sage, "furniture", "upholstered study chair", (2.1, YW + 1.9, 0))
    # accent chair + floor lamp near north wall
    boxes("ACCENT_CHAIR", [(0, 2.2, -1.55, 0, 0.5, 1.4), (0, 2.2, -0.3, 0, 1.4, 2.7), (0, 0.25, -1.55, 0, 1.4, 1.9), (1.95, 2.2, -1.55, 0, 1.4, 1.9)], rust, "furniture", "compact lounge chair 26\" wide", (8.1, -0.3, 0))
    cyl("FLOOR_LAMP", 10.55, -0.9, 0.35, 0, 0.05, charcoal, "lighting", "")
    cyl("FLOOR_LAMP_POLE", 10.55, -0.9, 0.03, 0.05, 4.8, charcoal, "lighting", "")
    cyl("FLOOR_LAMP_SHADE", 10.55, -0.9, 0.45, 4.8, 5.5, mat("Linen_Shade", (0.95, 0.9, 0.8), 0.9, emit=1.5), "lighting", "linen shade floor lamp")
    box("RUG", 3.8, 10.8, -7.6, -1.4, 0.02, 0.05, mat("Rug_Wool", (0.78, 0.72, 0.62), 1.0), "soft_furnishing", "flat-weave wool rug 5'x7'")
    box("ARTWORK", 1.2, 5.2, YW + 0.02, YW + 0.07, 6.0, 7.8, mat("Art", (0.75, 0.55, 0.4), 0.8), "decor", "framed art print 4'x1'10\"")
    # ceiling & lighting
    z0 = ceiling_band(gyp, 0.5, 1.6, "gypsum perimeter band 1'7\" wide, 6\" drop, curtain pelmet on balcony side", light)
    downlights([(1.05, -3.0), (1.05, -8.0), (11.8, -2.6), (11.8, -9.3), (6.3, -0.8), (4.0, YW + 0.8), (10.0, -11.9)], z0, light)
    # W1: 3-track aluminium slider (2 glass + 1 mesh) + safety grill
    w1_frame(charcoal, "W1: 3-track aluminium sliding window, charcoal powder-coat, 5 mm clear toughened glass, EPDM gaskets")
    sash("W1_SASH_1", W1_X0 + 0.15, 5.55, W1_Z0 + 0.15, W1_Z1 - 0.15, 0.24, 0.32, charcoal, glass, "sliding glass shutter (track 1)")
    sash("W1_SASH_2", 5.25, W1_X1 - 0.15, W1_Z0 + 0.15, W1_Z1 - 0.15, 0.33, 0.41, charcoal, glass, "sliding glass shutter (track 2)", slide=-1.85)
    sash("W1_MESH", 5.25, W1_X1 - 0.15, W1_Z0 + 0.15, W1_Z1 - 0.15, 0.43, 0.5, charcoal, mesh, "SS-304 mosquito mesh shutter (track 3)")
    w1_grill(charcoal, "flat-bar MS safety grill, 5\" pitch, powder-coated to match frame (outside the glass)")
    w1_sill(granite, "Black granite sill, 4\" projection, rounded edge")
    track_curtains("W1_CURTAIN", (W1_X0 - 0.9, -0.35), (W1_X1 + 0.9, -0.35), z0, mat("Sheer", (0.97, 0.96, 0.93), 0.9, alpha=0.4), sage,
                   1.0, "linen-look sheer, 2x fullness", "sage blackout drape, ripple-fold", side=-0.15)
    # Balcony door: 3-track, 3-panel aluminium slider
    bd_frame(charcoal, "Balcony door: 3-track aluminium sliding system (Jindal/Fenesta class), charcoal, 10'5\" x 7'")
    Wd = OPN_Y1 - OPN_Y0 - 0.4; p = (Wd + 0.4) / 3
    ys = [OPN_Y0 + 0.2, OPN_Y0 + 0.2 + p - 0.2, OPN_Y0 + 0.2 + 2 * p - 0.4]
    for i, (xc, y) in enumerate(zip([-0.78, -0.63, -0.48], ys)):
        hx = [(-0.36, -0.28, ys[2] + 0.26, ys[2] + 0.34, 3.4, 4.4)] if i == 2 else []
        bd_panel(f"BALCONY_DOOR_P{i+1}", xc, y, y + p + 0.2, charcoal, glass, th=0.06, spec=f"panel {i+1}: 8 mm clear toughened glass, interlocking profile" + (" (fixed)" if i == 0 else " (sliding)"),
                 slide_dy=(None, -(p - 0.1), -(2 * p - 0.3))[i], extra=[("BALCONY_DOOR_HANDLE", hx, charcoal)] if hx else None)
    box("BALCONY_PLEATED_MESH", -0.3, -0.22, OPN_Y1 - 0.45, OPN_Y1 - 0.2, 0.06, OPN_H - 0.2, mesh, "fenestration", "retractable pleated mosquito mesh (stacked)")
    threshold(granite, "black granite threshold with low-profile track, 2\" step down to balcony, sloped outward")
    track_curtains("BALCONY_CURTAIN", (0.35, OPN_Y0 + 0.05), (0.35, OPN_Y1 + 0.3), z0, mat("Sheer", (0.97, 0.96, 0.93), 0.9, alpha=0.4), sage,
                   1.6, "linen-look sheer, full width", "sage blackout drapes stacked at both ends", side=-0.15)
    # Balcony
    balcony_floor(mat("Outdoor_Tile", (0.55, 0.5, 0.45), 0.8), "anti-skid matte outdoor tile 600x600, R11")
    teak = mat("Teak_Outdoor", (0.5, 0.33, 0.18), 0.6)
    box("BALCONY_BENCH", -2.6, -1.3, -13.75, -11.35, 0, 1.45, teak, "balcony", "built-in teak/WPC bench 2'4\" x 1'4\", storage under seat")
    box("BALCONY_BENCH_CUSHION", -2.55, -1.35, -13.7, -11.4, 1.45, 1.75, sage, "balcony", "outdoor fabric cushion")
    box("BALCONY_BACK_CUSHION", -1.55, -1.3, -13.6, -11.5, 1.75, 2.9, rust, "balcony", "back cushion")
    cyl("BALCONY_SIDE_TABLE_TOP", -3.25, -12.55, 0.6, 1.7, 1.8, teak, "balcony", "18\" round teak side table")
    cyl("BALCONY_SIDE_TABLE_LEG", -3.25, -12.55, 0.07, 0, 1.7, charcoal, "balcony", "")
    box("BALCONY_GREEN_WALL", -1.33, -1.26, -13.8, -11.3, 3.2, 6.2, mat("Foliage", (0.22, 0.42, 0.2), 0.8), "plants", "modular vertical-garden panel with drip irrigation")
    plant("BALCONY_PLANT_1", -3.6, -0.2, BAL_Z, 0.55, 1.4, 0.75, mat("Planter_Grey", (0.45, 0.45, 0.45), 0.7), "areca palm in fibre planter", 1.6)
    plant("BALCONY_PLANT_2", -2.2, 0.1, BAL_Z, 0.4, 1.0, 0.55, mat("Planter_Grey", (0.45, 0.45, 0.45), 0.7), "snake plant")
    for i, y in enumerate((-2.5, -5.5, -8.5)):
        box(f"RAILING_PLANTER_{i+1}", -4.3, -3.85, y - 1.0, y + 1.0, 2.6, 3.1, charcoal, "plants", "railing planter box 2' (herbs / flowers)")
        blob(f"RAILING_PLANTER_{i+1}_LEAVES", -4.07, y, 3.2, 0.5, mat("Foliage", (0.22, 0.42, 0.2), 0.8), "plants", "", sz=0.5)
    outdoor_light(charcoal, "IP65 outdoor wall light, warm white, up-down beam")

def build_A():  # Japandi calm - bed faces north, desk under window
    ash = mat("Light_Ash", (0.8, 0.68, 0.52), 0.6); white = mat("Warm_White", (0.95, 0.94, 0.9), 0.7)
    linen = mat("Linen", (0.86, 0.8, 0.7), 0.95); moss = mat("Moss_Green", (0.42, 0.47, 0.35), 0.9); black = mat("Matt_Black", (0.08, 0.08, 0.08), 0.5)
    upvc = mat("uPVC_White", (0.96, 0.96, 0.95), 0.4); glass = mat("Clear_Glass", (0.75, 0.88, 0.95), 0.05, alpha=0.25)
    mesh = mat("Mesh", (0.3, 0.3, 0.3), 0.8, alpha=0.5); light = mat("LED", (1.0, 0.84, 0.62), 0.5, emit=5.0)
    bamboo = mat("Bamboo", (0.72, 0.6, 0.38), 0.8)
    floor_finish(mat("Tile_WoodLook", (0.75, 0.62, 0.47), 0.55), "wood-look vitrified plank tile 200x1200, light oak")
    skirting(ash)
    sl = [(x, x + 0.12, YW, YW + 0.1, 0, 8.5) for x in [0.3 + i * 0.25 for i in range(int(6.8 / 0.25))]]
    boxes("HEADBOARD_SLAT_WALL", sl + [(0.2, 7.2, YW, YW + 0.03, 0, 8.5)], ash, "finishes", "vertical ash slat wall (1.5\" slats, 3\" c/c) on raised south wall")
    bed(4.1, YW + 0.1, 90, 5.0, 6.5, dict(hb_h=1.9, hb_t=0.2, hb_mat=ash, hb_spec="low ash headboard rail", base_z=(0.0, 0.9), hb_z0=0.0,
        base_mat=ash, base_spec="Japanese-style low platform bed, solid ash, 11\" high", duvet=linen, throw=moss, cushion=moss, hb_w=6.2))
    box("BEDSIDE_E", 6.75, 7.2, YW + 0.1, YW + 1.4, 0, 1.6, ash, "furniture", "slim ash bedside, open shelf")
    cyl("BEDSIDE_W_STOOL", 0.75, YW + 0.8, 0.5, 0, 1.5, ash, "furniture", "round wooden stool as bedside (keeps balcony path clear)")
    for x in (0.75, 6.95):
        blob(f"PAPER_LAMP_{x:.0f}", x, YW + 0.8, 5.6, 0.45, mat("Rice_Paper", (0.98, 0.94, 0.85), 0.9, emit=2.5), "lighting", "rice-paper pendant lamp")
    # desk under window
    box("DESK_TOP", W1_X0 - 0.2, W1_X1 + 0.2, -1.9, 0, 2.35, 2.48, ash, "furniture", "4'4\" solid-ash desk under the window (daylight from front)")
    boxes("DESK_LEGS", [(W1_X0 - 0.15, W1_X0 - 0.05, -1.8, -0.1, 0, 2.35), (W1_X1 + 0.05, W1_X1 + 0.15, -1.8, -0.1, 0, 2.35)], ash, "furniture", "")
    boxes("DESK_CHAIR", [(0, 1.45, 0, 1.45, 1.4, 1.52), (0, 1.45, -0.1, 0.02, 1.52, 2.7), (0.1, 0.2, 0.1, 1.3, 0, 1.4), (1.25, 1.35, 0.1, 1.3, 0, 1.4)], ash, "furniture", "wooden chair with woven seat", (4.7, -2.75, 0))
    # east-wall low bookcase + reading pouf
    box("LOW_BOOKCASE", RW - 1.25, RW - 0.05, -7.0, -1.2, 0, 2.6, ash, "furniture", "low open bookcase 5'10\" long, 15\" deep")
    cyl("READING_POUF", RW - 2.4, -3.3, 0.9, 0, 1.2, linen, "furniture", "jute/linen floor pouf")
    plant("INDOOR_PLANT", RW - 0.8, -8.6, 0, 0.6, 1.3, 0.8, mat("Terracotta", (0.66, 0.4, 0.28), 0.8), "fiddle-leaf fig in ceramic pot", 1.8)
    box("RUG", 0.8, 7.0, YW + 3.0, -2.2, 0.02, 0.04, mat("Jute", (0.72, 0.62, 0.45), 1.0), "soft_furnishing", "jute rug 6'x8'")
    wardrobe_alcove(dict(doors=2, sliding=True, top=8.4, body=white, shutter=ash, spec="2-door sliding wardrobe 5'3\" x 2' x 8'5\" (no swing space needed)",
                         shutter_spec="ash veneer sliding shutters with grooved lines", handle=black, handle_spec="recessed finger pulls", loft=False))
    box("WARDROBE_TOP_NICHE", XSTEP + 0.05, RW - 0.05, YS + 0.05, YS + 1.9, 8.45, 9.95, white, "wardrobe", "open top niche for baskets")
    # ceiling: no false ceiling; timber slat raft over bed + surface lights
    sl = [(x, x + 0.14, YW + 0.3, YW + 6.8, 9.65, 9.8) for x in [0.8 + i * 0.3 for i in range(int(6.0 / 0.3))]]
    boxes("CEILING_SLAT_RAFT", sl, ash, "ceiling", "suspended ash slat raft over bed zone (6' x 6'6\"), no gypsum false ceiling")
    blob("CEILING_PAPER_PENDANT", 6.3, -5.0, 8.2, 0.9, mat("Rice_Paper", (0.98, 0.94, 0.85), 0.9, emit=2.5), "lighting", "large rice-paper pendant (Akari style)", sz=0.8)
    downlights([(2.0, -2.0), (10.5, -2.0), (10.5, -9.0), (10.0, -11.9)], H, light, "surface-mounted round downlight, 2700K")
    # W1: uPVC white casement x2 (outward) + internal roller mesh; laminated glass instead of grill
    w1_frame(upvc, "W1: uPVC casement window (white), multi-chamber, 6.38 mm laminated safety glass - no grill needed")
    sash("W1_CASEMENT_L", W1_X0 + 0.17, 5.4, W1_Z0 + 0.17, W1_Z1 - 0.17, 0.35, 0.47, upvc, glass, "outward-opening casement with friction stay", hinge=('L', 'out', 75))
    sash("W1_CASEMENT_R", 5.4, W1_X1 - 0.17, W1_Z0 + 0.17, W1_Z1 - 0.17, 0.35, 0.47, upvc, glass, "outward-opening casement with friction stay", hinge=('R', 'out', 75))
    box("W1_ROLLER_MESH_CASSETTE", W1_X0 + 0.1, W1_X1 - 0.1, 0.18, 0.28, W1_Z1 - 0.3, W1_Z1 - 0.1, upvc, "fenestration", "vertical roller mosquito mesh (inside)")
    w1_sill(mat("Teak_Sill", (0.5, 0.33, 0.18), 0.5), "solid wood sill board, 5\" deep (display ledge)", proj=0.4)
    box("W1_ROMAN_BLIND", W1_X0 - 0.2, W1_X1 + 0.2, -0.2, -0.12, 5.8, 7.4, bamboo, "soft_furnishing", "bamboo roman blind, light-filtering")
    # Balcony door: uPVC 2-track 4-panel slider (fixed-slide-slide-fixed)
    bd_frame(upvc, "Balcony door: uPVC 3-track 4-panel slider, white, 10'5\" x 7' - 2 fixed (south) + 2 sliding (north); opens the north half, away from the bed")
    q = (OPN_Y1 - OPN_Y0 - 0.4) / 4
    for i in range(4):
        y = OPN_Y0 + 0.2 + i * q; xc = (-0.74, -0.74, -0.6, -0.46)[i]
        bd_panel(f"BALCONY_DOOR_P{i+1}", xc, y - (0.1 if i else 0), y + q + (0.1 if i < 3 else 0), upvc, glass, "5 mm toughened glass" + (" (sliding)" if i >= 2 else " (fixed)"), th=0.06, mid=3.4,
                 slide_dy={2: -(2 * q - 0.2), 3: -(2 * q - 0.2)}.get(i))
    box("BALCONY_ROLLER_MESH", -0.35, -0.25, OPN_Y0 + 0.2, OPN_Y1 - 0.2, OPN_H - 0.4, OPN_H - 0.2, upvc, "fenestration", "horizontal roller insect screen cassette")
    threshold(mat("Kota_Stone", (0.55, 0.55, 0.48), 0.5), "Kota stone threshold, 2\" step down")
    curtain("BALCONY_LINEN_CURTAIN_N", (0.3, OPN_Y1 + 0.2), (0.3, OPN_Y1 - 1.8), 0.1, 8.0, linen, "soft_furnishing", "natural linen curtain on wooden rod", amp=0.1)
    curtain("BALCONY_LINEN_CURTAIN_S", (0.3, OPN_Y0 + 1.8), (0.3, OPN_Y0 - 0.1), 0.1, 8.0, linen, "soft_furnishing", "natural linen curtain on wooden rod", amp=0.1)
    cyl("BALCONY_CURTAIN_ROD", 0.3, (OPN_Y0 + OPN_Y1) / 2, 0.04, 8.05, 8.12, ash, "soft_furnishing", "wooden curtain rod (visual only - horizontal)")
    # Balcony: deck tiles, floor seating, bamboo privacy screen
    balcony_floor(mat("Deck_Tile", (0.55, 0.38, 0.24), 0.7), "WPC interlocking deck tiles 300x300")
    box("BALCONY_FLOOR_CUSHION_1", -2.9, -1.5, -13.6, -12.0, 0, 0.45, moss, "balcony", "outdoor floor cushion")
    box("BALCONY_FLOOR_CUSHION_2", -2.9, -1.5, -11.8, -10.2, 0, 0.45, linen, "balcony", "outdoor floor cushion")
    box("BALCONY_LOW_TABLE", -3.9, -3.0, -13.0, -11.0, 0, 1.1, ash, "balcony", "low tea table (chabudai style)")
    bx = [(-4.33, -4.29, y, y + 0.06, 0.4, 5.0) for y in [BAL_Y0 + 0.1 + i * 0.1 for i in range(int((BAL_Y1 - BAL_Y0 - 0.2) / 0.1))]]
    boxes("BALCONY_BAMBOO_SCREEN", bx, bamboo, "balcony", "bamboo privacy screen fixed to railing, 5' high")
    for i, y in enumerate((0.1, -1.0, -8.0)):
        plant(f"BALCONY_PLANT_{i+1}", -3.4 + 0.6 * (i % 2), y, BAL_Z, 0.5, 1.2, 0.7, mat("Terracotta", (0.66, 0.4, 0.28), 0.8), "bamboo palm / monstera in terracotta", 1.5)
    blob("BALCONY_LANTERN", -1.6, -13.3, 6.8, 0.35, mat("Lantern", (1.0, 0.85, 0.6), 0.6, emit=3.0), "lighting", "hanging solar paper-lantern", sz=1.3)

def build_B():  # Minimal monochrome - bed head on north wall, media/dresser wall on raised wall
    white = mat("Pure_White_Matt", (0.95, 0.95, 0.94), 0.5); grey = mat("Warm_Grey", (0.6, 0.58, 0.55), 0.7)
    walnut = mat("Walnut", (0.35, 0.22, 0.14), 0.5); black = mat("Black_Alu", (0.05, 0.05, 0.06), 0.35, 0.6)
    glass = mat("Clear_Glass", (0.75, 0.88, 0.95), 0.05, alpha=0.22); light = mat("LED", (1.0, 0.92, 0.8), 0.5, emit=6.0)
    gyp = mat("Gypsum_White", (0.97, 0.97, 0.96), 0.9); boucle = mat("Boucle", (0.9, 0.88, 0.84), 1.0)
    floor_finish(mat("Tile_LightGrey", (0.78, 0.78, 0.76), 0.35), "large-format 1200x1200 light-grey matte porcelain, 1 mm joints")
    skirting(mat("Shadow_Gap", (0.2, 0.2, 0.2), 0.5))
    box("HEADBOARD_PANEL_WALL", 7.45, RW, -0.08, 0, 0, 8.3, grey, "finishes", "full-height fabric-wrapped acoustic panel wall, warm grey")
    box("HEADBOARD_LED_LINE", 7.4, RW - 0.05, -0.1, -0.08, 4.3, 4.35, light, "lighting", "hidden LED line in panel reveal")
    bed((7.5 + RW) / 2, -0.1, -90, 5.0, 6.5, dict(hb_h=3.2, hb_mat=grey, hb_spec="integrated padded headboard", base_z=(0.35, 1.1),
        base_mat=walnut, base_spec="floating platform bed, walnut veneer, hidden plinth", duvet=white, throw=grey, cushion=mat("Charcoal_Fabric", (0.2, 0.2, 0.22), 0.9), hb_w=5.0))
    box("BEDSIDE_FLOATING_W", 6.1, 7.4, -1.5, -0.05, 1.3, 1.75, walnut, "furniture", "floating bedside drawer (below window sill)")
    box("BEDSIDE_SHELF_E", RW - 0.08, RW, -2.0, -0.6, 2.2, 2.3, walnut, "furniture", "wall shelf (no room for table on this side)")
    cyl("PENDANT_W", 6.75, -0.8, 0.25, 4.4, 4.9, mat("Opal", (1.0, 0.95, 0.88), 0.4, emit=3.0), "lighting", "opal glass mini pendant")
    # media + dresser wall on the raised wall
    box("MEDIA_WALL_UNIT", 0.5, 7.2, YW, YW + 1.35, 0.6, 1.9, walnut, "furniture", "floating walnut console 6'8\" x 16\"")
    box("MEDIA_WALL_TALL", 5.9, 7.2, YW, YW + 1.35, 0, 8.5, white, "furniture", "tall handleless storage column")
    box("TV_55", 1.4, 5.2, YW + 0.05, YW + 0.15, 3.3, 5.45, black, "furniture", "55\" TV, wall-mounted, viewed from bed")
    box("MEDIA_WALL_PANEL", 0.3, 5.9, YW, YW + 0.05, 0, 8.5, grey, "finishes", "microcement-look panel behind TV")
    # lounge corner by balcony
    boxes("LOUNGE_CHAIR", [(0, 2.3, -2.3, 0, 0.4, 1.35), (0, 2.3, -0.35, 0, 1.35, 2.9), (0, 0.3, -2.3, 0, 1.35, 2.0), (2.0, 2.3, -2.3, 0, 1.35, 2.0)], boucle, "furniture", "boucle lounge chair in the NW corner, facing the balcony", (1.0, -0.15, 0))
    cyl("LOUNGE_SIDE_TABLE", 3.75, -1.0, 0.45, 0, 1.7, black, "furniture", "black metal side table")
    cyl("ARC_LAMP_BASE", 0.55, -0.55, 0.35, 0, 0.1, black, "lighting", "")
    cyl("ARC_LAMP_POLE", 0.55, -0.55, 0.04, 0.1, 6.0, black, "lighting", "arc floor lamp")
    blob("ARC_LAMP_SHADE", 2.0, -1.4, 5.3, 0.45, mat("Opal", (1.0, 0.95, 0.88), 0.4, emit=3.0), "lighting", "", sz=0.6)
    box("RUG", 2.0, 11.0, -9.4, -3.8, 0.02, 0.04, mat("Rug_Charcoal", (0.3, 0.3, 0.3), 1.0), "soft_furnishing", "low-pile charcoal rug 6'x9'")
    box("EAST_CONSOLE", RW - 1.0, RW - 0.05, -9.4, -7.2, 1.4, 2.6, walnut, "furniture", "slim floating console / dresser")
    wardrobe_alcove(dict(doors=2, sliding=True, top=9.35, body=white, shutter=white, mirror=mat("Mirror", (0.85, 0.9, 0.92), 0.02, 1.0), light=light, spec="floor-to-ceiling sliding wardrobe, handleless, 5'3\" x 2' x 9'4\" (to false ceiling)",
                         shutter_spec="matt white lacquered glass sliding shutters", handle=black, handle_spec="", loft=False))
    # ceiling: flush gypsum + curtain pocket + linear lights
    box("FALSE_CEILING_FLUSH", 0, RW, YW, 0, 9.4, H, gyp, "ceiling", "flush gypsum ceiling at 9'5\" with 6\" recessed blind pocket along balcony side")
    box("FALSE_CEILING_ALCOVE", XSTEP, RW, YS + 2.05, YW, 9.4, H, gyp, "ceiling", "")
    for i, y in enumerate((-3.0, -8.0)):
        box(f"LINEAR_LIGHT_{i+1}", 1.5, 11.0, y - 0.06, y + 0.06, 9.37, 9.4, light, "lighting", "recessed linear LED profile 1\" wide, 3000K")
    box("BLIND_POCKET_SHADOW", 0.0, 0.55, YW, OPN_Y1, 9.38, 9.4, mat("Shadow_Gap", (0.2, 0.2, 0.2), 0.5), "ceiling", "blind pocket")
    # W1: slim black aluminium fixed + casement, invisible grill
    w1_frame(black, "W1: slim-profile black aluminium, left fixed + right inward tilt-and-turn sash, 6 mm low-E glass")
    sash("W1_FIXED", W1_X0 + 0.17, 5.4, W1_Z0 + 0.17, W1_Z1 - 0.17, 0.35, 0.45, black, glass, "fixed pane")
    sash("W1_CASEMENT", 5.4, W1_X1 - 0.17, W1_Z0 + 0.17, W1_Z1 - 0.17, 0.35, 0.45, black, glass, "tilt-and-turn sash (opens INWARD, so the external cable grill stays clear)", hinge=('R', 'in', 80))
    bx = [(W1_X0 + 0.1, W1_X1 - 0.1, 0.66, 0.67, z, z + 0.01) for z in [W1_Z0 + 0.2 + i * 0.25 for i in range(15)]]
    boxes("W1_INVISIBLE_GRILL", bx, mat("Steel_Wire", (0.7, 0.7, 0.72), 0.3, 1.0), "fenestration", "invisible grill: 2 mm SS-316 cables at 3\" c/c")
    w1_sill(mat("Quartz_White", (0.92, 0.92, 0.9), 0.3), "flush white quartz sill")
    box("W1_ROLLER_BLIND", W1_X0 - 0.1, W1_X1 + 0.1, -0.2, -0.15, 6.0, 7.2, grey, "soft_furnishing", "sunscreen roller blind (5% openness)")
    # Balcony door: black slim lift-and-slide, 2 large panels
    bd_frame(black, "Balcony door: slim black aluminium lift-and-slide, 2 panels (1 fixed + 1 sliding), 20 mm sightlines")
    half = (OPN_Y1 - OPN_Y0) / 2
    bd_panel("BALCONY_DOOR_FIXED", -0.75, OPN_Y0 + 0.2, OPN_Y0 + half + 0.1, black, glass, "fixed 10 mm toughened low-E glass", fw=0.12)
    bd_panel("BALCONY_DOOR_SLIDER", -0.5, OPN_Y0 + half - 0.1, OPN_Y1 - 0.2, black, glass, "lift-and-slide sash, 10 mm toughened low-E", fw=0.12,
             slide_dy=-(half - 0.5), extra=[("BALCONY_DOOR_HANDLE", [(-0.37, -0.29, OPN_Y0 + half + 0.11, OPN_Y0 + half + 0.19, 3.4, 4.8)], black)])
    box("BALCONY_PLEATED_MESH", -0.28, -0.22, OPN_Y1 - 0.4, OPN_Y1 - 0.2, 0.06, OPN_H - 0.2, black, "fenestration", "retractable pleated mesh")
    threshold(mat("Quartz_Grey", (0.5, 0.5, 0.5), 0.3), "flush quartz threshold, concealed drainage channel")
    box("BALCONY_BLIND_BLACKOUT", 0.15, 0.2, OPN_Y0, OPN_Y1, 3.5, 9.4, grey, "soft_furnishing", "motorised blackout roller blind (half-lowered)")
    box("BALCONY_BLIND_SHEER", 0.3, 0.33, OPN_Y0, OPN_Y1, 6.0, 9.4, mat("Sheer", (0.97, 0.96, 0.93), 0.9, alpha=0.4), "soft_furnishing", "motorised sunscreen blind")
    # Balcony
    balcony_floor(mat("Porcelain_Grey", (0.5, 0.5, 0.5), 0.6), "grey outdoor porcelain 600x1200, anti-skid")
    boxes("BALCONY_FOLD_TABLE", [(0, 0.9, -1.1, 1.1, 2.4, 2.5)], black, "balcony", "fold-down railing table 2'x11\"", (-4.3, -12.4, 0))
    for i, y in enumerate((-13.3, -11.5)):
        boxes(f"BALCONY_CHAIR_{i+1}", [(0, 1.3, 0, 1.3, 1.45, 1.55), (1.2, 1.3, 0, 1.3, 1.55, 2.8), (0.05, 0.12, 0.05, 1.25, 0, 1.45), (1.15, 1.22, 0.05, 1.25, 0, 1.45)], black, "balcony", "slim powder-coated metal chair", (-3.4, y - 0.65, 0))
    for i, y in enumerate((0.1, -9.8)):
        plant(f"BALCONY_PLANT_{i+1}", -2.3, y, BAL_Z, 0.5, 2.2, 0.65, mat("Concrete_Planter", (0.6, 0.6, 0.58), 0.8), "tall concrete-look planter, olive tree", 1.4)
    box("BALCONY_LINEAR_LIGHT", -1.3, -1.25, -13.8, -11.3, 7.2, 7.3, light, "lighting", "outdoor IP65 linear wall light")

def build_C():  # Indian modern heritage - premium, bi-fold door, diwan, cane
    teak = mat("Teak", (0.45, 0.28, 0.15), 0.45); cane = mat("Cane", (0.8, 0.65, 0.42), 0.8); teal = mat("Deep_Teal", (0.1, 0.32, 0.34), 0.8)
    terracotta = mat("Terracotta_Fabric", (0.72, 0.38, 0.25), 0.9); ivory = mat("Ivory", (0.94, 0.9, 0.82), 0.7); brass = mat("Brass", (0.78, 0.6, 0.3), 0.3, 0.9)
    glass = mat("Clear_Glass", (0.75, 0.88, 0.95), 0.05, alpha=0.25); light = mat("LED", (1.0, 0.82, 0.58), 0.5, emit=5.0); gyp = mat("Gypsum_White", (0.97, 0.96, 0.93), 0.9)
    floor_finish(mat("Terrazzo", (0.85, 0.82, 0.76), 0.4), "terrazzo-look tile 600x600 with brass-coloured strip border")
    box("FLOOR_BORDER", 0.3, RW - 0.3, YW + 0.3, -0.3, 0.02, 0.025, brass, "finishes", "brass inlay strip (1'from walls) - visual")
    skirting(teak)
    box("ACCENT_WALL_TEAL", RW - 0.03, RW, -9.4, 0, 0, 10, teal, "finishes", "deep teal limewash accent wall (east)")
    box("HEADBOARD_CANE_PANEL", RW - 0.3, RW - 0.03, -8.0, -1.0, 0.3, 4.8, cane, "furniture", "full-width cane headboard in teak frame 7' x 4'6\"")
    boxes("HEADBOARD_TEAK_FRAME", [(RW - 0.35, RW - 0.03, -8.1, -7.9, 0.3, 4.9), (RW - 0.35, RW - 0.03, -1.1, -0.9, 0.3, 4.9), (RW - 0.35, RW - 0.03, -8.1, -0.9, 4.75, 4.95)], teak, "furniture", "teak frame")
    bed(RW - 0.3, -4.5, 180, 5.0, 6.5, dict(hb_h=0.4, hb_mat=teak, hb_spec="(headboard is the cane wall panel)", base_mat=teak, base_spec="teak bed with turned legs, under-bed drawers",
        duvet=ivory, throw=terracotta, cushion=teal))
    for tag, y0 in (("N", -0.2), ("S", -7.1)):
        boxes(f"BEDSIDE_{tag}", [(RW - 1.7, RW - 0.35, y0 - 1.4, y0, 1.5, 2.0), (RW - 1.65, RW - 0.4, y0 - 1.35, y0 - 0.05, 0, 1.5)], teak, "furniture", "teak bedside with cane drawer front")
        cyl(f"PENDANT_{tag}", RW - 1.0, y0 - 0.7, 0.35, 4.6, 5.2, brass, "lighting", "brass dome pendant, 2700K")
    # diwan (daybed) on the raised wall, facing the balcony corner
    box("DIWAN_BASE", 0.6, 6.9, YW, YW + 2.3, 0, 1.25, teak, "furniture", "built-in diwan / daybed 6'4\" x 2'7\" with storage drawers")
    box("DIWAN_MATTRESS", 0.65, 6.85, YW + 0.05, YW + 2.25, 1.25, 1.65, terracotta, "soft_furnishing", "block-print mattress")
    boxes("DIWAN_BOLSTERS", [(0.7, 1.3, YW + 0.3, YW + 2.1, 1.65, 2.25), (6.2, 6.8, YW + 0.3, YW + 2.1, 1.65, 2.25)], teal, "soft_furnishing", "round bolsters (gol takiya)")
    box("DIWAN_BACK_CUSHIONS", 0.7, 6.8, YW + 0.05, YW + 0.6, 1.65, 3.2, ivory, "soft_furnishing", "back cushions")
    box("JAALI_PANEL", 0.8, 6.8, YW, YW + 0.06, 3.6, 7.6, cane, "finishes", "CNC teak jaali wall panel above diwan")
    box("BRASS_URLI_TABLE", 1.2, 2.8, YW + 3.3, YW + 4.6, 0, 1.3, brass, "decor", "low brass-top coffee table")
    wardrobe_alcove(dict(doors=3, body=ivory, shutter=teak, spec="3-door hinged wardrobe, teak veneer frame + cane-mesh insets (ventilated for humidity)",
                         shutter_spec="teak veneer shutters, cane insets", handle=brass, handle_spec="brass bar handles",
                         inset=cane, inset_spec="woven cane mesh inset panels", loft=True, light=light))
    box("RUG", 5.0, 10.8, -8.4, -0.8, 0.03, 0.05, mat("Dhurrie", (0.7, 0.45, 0.35), 1.0), "soft_furnishing", "hand-woven cotton dhurrie 6'x8'")
    # ceiling: single-step tray with cove + teak strip
    z0 = ceiling_band(gyp, 0.75, 2.2, "single-step tray ceiling: 2'2\" gypsum band at 9'3\", cove LED, curtain pelmet", light)
    boxes("CEILING_TEAK_STRIP", [(2.2, RW - 2.2, -2.3, -2.2, z0 - 0.02, z0), (2.2, RW - 2.2, YW + 2.2, YW + 2.3, z0 - 0.02, z0)], teak, "ceiling", "teak veneer edge strip")
    downlights([(1.1, -1.1), (1.1, -10.0), (11.4, -1.1), (11.4, -10.0), (10.0, -11.9)], z0, light, "brass-trim downlight 7 W, 2700K")
    blob("CEILING_CANE_PENDANT", 6.3, -5.5, 8.0, 0.8, cane, "lighting", "large cane pendant over room centre", sz=0.7)
    # W1: teak-finish aluminium casement + top fixed light, decorative jaali grill
    w1_frame(teak, "W1: aluminium casement with teak woodgrain finish, 2 inward casements + fixed top light, 6 mm toughened")
    sash("W1_TOPLIGHT", W1_X0 + 0.17, W1_X1 - 0.17, 5.9, W1_Z1 - 0.17, 0.35, 0.45, teak, glass, "fixed top light")
    sash("W1_CASEMENT_L", W1_X0 + 0.17, 5.4, W1_Z0 + 0.17, 5.9, 0.28, 0.38, teak, glass, "inward-opening casement (grill is outside), brass handle", hinge=('L', 'in', 85))
    sash("W1_CASEMENT_R", 5.4, W1_X1 - 0.17, W1_Z0 + 0.17, 5.9, 0.28, 0.38, teak, glass, "inward-opening casement (grill is outside), brass handle", hinge=('R', 'in', 85))
    bx = []
    for i in range(6):
        for j in range(6):
            cx = W1_X0 + 0.35 + i * 0.66; cz = W1_Z0 + 0.35 + j * 0.66
            bx += [(cx - 0.3, cx + 0.3, 0.64, 0.68, cz - 0.02, cz + 0.02), (cx - 0.02, cx + 0.02, 0.64, 0.68, cz - 0.3, cz + 0.3)]
    boxes("W1_JAALI_GRILL", bx, mat("Iron_Black", (0.1, 0.1, 0.1), 0.5, 0.4), "fenestration", "decorative MS jaali-pattern safety grill (outside)")
    w1_sill(mat("Kota_Stone", (0.5, 0.55, 0.48), 0.5), "Kota stone sill, polished")
    track_curtains("W1_CURTAIN", (W1_X0 - 0.9, -0.35), (W1_X1 + 0.9, -0.35), z0, mat("Sheer", (0.97, 0.95, 0.9), 0.9, alpha=0.4), terracotta,
                   1.0, "cotton voile sheer", "block-print cotton drape, lined", rod_mt=brass, side=-0.15)
    # Balcony door: 4-panel aluminium bi-fold, shown folded open to the north
    bd_frame(teak, "Balcony door: 4-panel aluminium bi-fold (teak finish), full 10'5\" opening, bottom-rolling")
    pw = (OPN_Y1 - OPN_Y0 - 0.4) / 4
    for i in range(4):
        y = OPN_Y1 - 0.35 - i * 0.18
        boxes(f"BIFOLD_P{i+1}_FRAME", [(-0.6 - pw, -0.6, y - 0.08, y + 0.08, 0.06, 0.3), (-0.6 - pw, -0.6, y - 0.08, y + 0.08, OPN_H - 0.4, OPN_H - 0.2),
                                        (-0.8, -0.6, y - 0.08, y + 0.08, 0.06, OPN_H - 0.2), (-0.6 - pw, -0.4 - pw, y - 0.08, y + 0.08, 0.06, OPN_H - 0.2)],
              teak, "fenestration", f"bi-fold leaf {i+1} (folded open onto balcony)")
        box(f"BIFOLD_P{i+1}_GLASS", -0.4 - pw, -0.8, y - 0.02, y + 0.02, 0.3, OPN_H - 0.4, glass, "fenestration", "8 mm toughened glass")
    box("BALCONY_PLEATED_MESH", -0.3, -0.22, OPN_Y0 + 0.2, OPN_Y0 + 0.5, 0.06, OPN_H - 0.2, teak, "fenestration", "pleated mesh, stacked at south jamb")
    threshold(mat("Kota_Stone", (0.5, 0.55, 0.48), 0.5), "Kota stone threshold with flush bottom track")
    track_curtains("BALCONY_CURTAIN", (0.35, OPN_Y0 + 0.05), (0.35, OPN_Y1 + 0.3), z0, mat("Sheer", (0.97, 0.95, 0.9), 0.9, alpha=0.4), terracotta,
                   1.6, "cotton voile sheer", "block-print drapes on brass rod", rod_mt=brass, side=-0.15)
    # Balcony
    balcony_floor(mat("Kota_Outdoor", (0.5, 0.55, 0.48), 0.7), "leather-finish Kota stone")
    boxes("BALCONY_RATTAN_CHAIR", [(0, 2.0, -2.0, 0, 0.4, 1.4), (0, 0.4, -2.0, 0, 1.4, 3.0), (0, 2.0, -0.3, 0, 1.4, 2.1), (0, 2.0, -2.0, -1.7, 1.4, 2.1)], cane, "balcony", "rattan armchair (outdoor-grade synthetic)", (-3.4, -11.3, 0))
    box("BALCONY_CHAIR_CUSHION", -3.3, -1.5, -13.2, -11.4, 1.4, 1.65, teal, "balcony", "")
    cyl("BALCONY_CANE_TABLE", -3.6, -10.3, 0.55, 0, 1.6, cane, "balcony", "cane side table")
    for i, (x, y) in enumerate(((-3.5, 0.2), (-2.1, 0.2), (-3.7, -6.0), (-1.9, -13.5))):
        plant(f"BALCONY_PLANT_{i+1}", x, y, BAL_Z, 0.45 + 0.1 * (i % 2), 1.0 + 0.3 * (i % 2), 0.6, mat("Terracotta", (0.66, 0.4, 0.28), 0.8), "terracotta planters: tulsi, jasmine, bougainvillea", 1.4)
    blob("BALCONY_BRASS_LANTERN", -1.6, -12.6, 6.5, 0.3, mat("Lantern", (1.0, 0.8, 0.5), 0.5, emit=3.5), "lighting", "pierced brass lantern (wall bracket)", sz=1.4)
    box("BALCONY_DHURRIE", -4.2, -1.5, -13.8, -9.5, BAL_Z + 0.03, BAL_Z + 0.05, mat("Dhurrie", (0.7, 0.45, 0.35), 1.0), "balcony", "outdoor jute dhurrie")

OPTIONS = [("DEFAULT", "13_ROOM1_DEFAULT", build_default), ("OPTION_A", "14_ROOM1_OPTION_A", build_A),
           ("OPTION_B", "15_ROOM1_OPTION_B", build_B), ("OPTION_C", "16_ROOM1_OPTION_C", build_C)]
REPLACES = "WINDOW_W1_FRAME,WINDOW_W1_GLASS"   # generic architecture placeholders replaced by the designed window

def run():
    global OPT, COL
    for _, cname, _ in OPTIONS:
        c = bpy.data.collections.get(cname)
        if c:
            for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
    for m_ in [x for x in bpy.data.materials if x.users == 0]: bpy.data.materials.remove(m_)
    MATS.clear(); counts = {}
    for key, cname, fn in OPTIONS:
        OPT = key; COL = bpy.data.collections.new(cname); bpy.context.scene.collection.children.link(COL)
        COL["design_option"] = key; COL["replaces"] = REPLACES
        fn()
        # suspension cords for pendant fittings (to the ceiling / false-ceiling underside)
        for o in list(COL.objects):
            if any(k in o.name for k in ("PENDANT", "PAPER_LAMP")) and "ARC" not in o.name:
                top_z = (o.location.z + max(v[2] for v in o.bound_box)) / FT
                x, y = o.location.x / FT, o.location.y / FT
                cyl(o.name.split("_", 2)[-1] + "_CORD", x, y, 0.015, top_z, H - 0.02, mat("Cord", (0.1, 0.1, 0.1), 0.6), "lighting", "suspension cord", 6)
        # light-emitting fittings -> metadata for the viewer's night / lights mode
        for o in COL.objects:
            n = o.name
            if o.get("design_category") != "lighting" or n.endswith("_CORD") or "POLE" in n or "BASE" in n or n.endswith("FLOOR_LAMP"): continue
            kind = "spot" if "DOWNLIGHT" in n else ("strip" if any(k in n for k in ("COVE", "LINEAR", "LED")) else "point")
            o["light"] = kind; o["lumens"] = {"spot": 450, "strip": 900, "point": 300}[kind]
        counts[key] = len(COL.objects)
    # show DEFAULT, hide others in viewport
    for key, cname, _ in OPTIONS:
        lc = bpy.context.view_layer.layer_collection.children[cname]; lc.hide_viewport = key != "DEFAULT"
        bpy.data.collections[cname].hide_render = key != "DEFAULT"
    for n in REPLACES.split(","):
        o = bpy.data.objects.get(n)
        if o: o.hide_set(True); o.hide_render = True
    return counts
