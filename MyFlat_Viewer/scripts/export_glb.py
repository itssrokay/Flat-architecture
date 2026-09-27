"""
Export the currently open MyFlat architecture .blend to a web GLB + manifest.

The source .blend is NEVER saved: metadata is written to objects in memory only,
the GLB is exported, then the file is reverted.

Run inside Blender (Text Editor > Run Script) with the model open, or headless:
  /Applications/Blender.app/Contents/MacOS/Blender -b \
      ~/Documents/MyFlat/MyFlat_V2_Architecture.blend \
      --python ~/Documents/MyFlat/MyFlat_Viewer/scripts/export_glb.py

Output: MyFlat_Viewer/models/<blend name>.glb and <blend name>.manifest.json

Interior design files: set DESIGN = "DEFAULT" (or OPTION_A...) and OUT_NAME before running
to export the architecture + that one design option (objects with a design_option property).
"""
import bpy, os, json, datetime
from mathutils import Vector

FT = 0.3048
VIEWER = os.path.join(os.path.expanduser("~"), "Documents", "MyFlat", "MyFlat_Viewer")
OUT_DIR = os.path.join(VIEWER, "models")

# Object -> room name for floor objects (room navigation + labels in the viewer)
ROOM_FLOORS = {
    "FLOOR_R1": "Room 1", "FLOOR_KIT": "Kitchen", "FLOOR_B2": "Bathroom 2", "FLOOR_PAS": "Passage",
    "FLOOR_R2": "Room 2", "FLOOR_HALL": "Hall", "FLOOR_B1": "Bathroom 1", "FLOOR_STAIR": "Stair",
    "FLOOR_OPENSQ": "Open Square", "BALCONY_FLOOR": "Balcony",
}
SKIP_PREFIX = ("LBL_", "CAM_", "SLAB_CUT_", "NOTE_", "MARKER_")
SKIP_EXACT = {"PLAN_REFERENCE"}          # side-by-side copy; the aligned overlay is exported


def top_collection_map():
    m = {}
    def walk(c, top):
        for o in c.objects: m.setdefault(o.name, top)
        for ch in c.children: walk(ch, top)
    for c in bpy.context.scene.collection.children: walk(c, c.name)
    return m


def classify(o, top):
    n = o.name.upper()
    if "RAILING" in n or "HANDRAIL" in n: return "railings", ""
    if n.startswith("VENT_"): return "vents", ""
    if n.startswith("PLAN_REFERENCE"): return "plan_reference", ""
    if n.startswith("GROUND"): return "context", ""
    if n.startswith("PARAPET_") or n == "BALCONY_EDGE_CURB": return "walls", "parapet"
    if top == "01_WALLS": return "walls", "external" if "_EXT_" in n else "internal"
    if top == "02_FLOORS" or n in ROOM_FLOORS or n.startswith("FLOOR_"):
        return "floors", "threshold" if n.startswith("THRESHOLD") else ("structure" if "SLAB" in n else "")
    if top == "03_CEILING_SLAB": return "roof", ""
    if top == "04_DOORS": return "doors", "opening" if n.startswith("OPENING_") else ""
    if top == "05_WINDOWS": return "windows", ""
    if top == "06_PILLARS": return "pillars", ""
    if top == "07_BEAMS": return "beams", ""
    if top == "08_STAIRS": return "stairs", ""
    if top == "09_BALCONY": return "balcony", ""
    if top == "10_OPEN_SQUARE": return "open_square", ""
    return (top.split("_", 1)[-1].lower() if top else "other"), ""


def local_dims_ft(o, dg):
    if o.type != 'MESH': return None
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    if not me.vertices: ev.to_mesh_clear(); return None
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    s = o.matrix_world.to_scale()
    d = [(max(xs)-min(xs))*s.x/FT, (max(ys)-min(ys))*s.y/FT, (max(zs)-min(zs))*s.z/FT]
    ev.to_mesh_clear()
    return [round(v, 3) for v in d]


DESIGN = globals().get("DESIGN")        # None -> architecture (+ nothing tagged as design)
OUT_NAME = globals().get("OUT_NAME")


def export():
    src = bpy.data.filepath
    name = OUT_NAME or os.path.splitext(os.path.basename(src))[0] or "model"
    replaced = set()
    for c in bpy.data.collections:
        if DESIGN and c.get("design_option") == DESIGN and c.get("replaces"):
            replaced |= set(c["replaces"].split(","))
    os.makedirs(OUT_DIR, exist_ok=True)
    glb = os.path.join(OUT_DIR, name + ".glb")
    tops = top_collection_map(); dg = bpy.context.evaluated_depsgraph_get()
    vl = bpy.context.view_layer
    # make everything selectable (in memory only)
    def unhide(lc):
        lc.exclude = False; lc.hide_viewport = False
        for ch in lc.children: unhide(ch)
    unhide(vl.layer_collection)
    for o in bpy.data.objects: o.hide_viewport = False; o.hide_set(False); o.hide_select = False
    bpy.ops.object.select_all(action='DESELECT') if bpy.context.mode == 'OBJECT' else None
    rows = []
    for o in bpy.context.scene.objects:
        n = o.name
        if n.endswith("_CUTTER") or n.startswith(SKIP_PREFIX) or n in SKIP_EXACT: continue
        if o.type not in ('MESH', 'EMPTY'): continue
        opt = o.get("design_option")
        if opt and opt != DESIGN: continue
        if n in replaced: continue
        top = tops.get(n, "")
        cat, sub = classify(o, top)
        if o.get("design_category"): cat, sub = o["design_category"], ""
        o["category"] = cat
        if sub: o["subtype"] = sub
        o["collection"] = top
        if n in ROOM_FLOORS: o["room"] = ROOM_FLOORS[n]
        dims = local_dims_ft(o, dg)
        if dims: o["dims_ft"] = dims
        o.select_set(True)
        rows.append({"name": n, "type": o.type, "category": cat, "subtype": sub,
                     "status": o.get("status"), "parent": o.parent.name if o.parent else None})
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True, export_apply=True,
                              export_extras=True, export_yup=True, export_cameras=False, export_lights=False)
    counts = {}
    for r in rows: counts[r["category"]] = counts.get(r["category"], 0) + 1
    man = {"model": name + ".glb", "source_blend": os.path.basename(src),
           "exported": datetime.datetime.now().isoformat(timespec="seconds"),
           "blender": bpy.app.version_string, "units": "metres", "up": "+Y", "north": "-Z", "east": "+X",
           "object_count": len(rows), "counts": counts, "design_option": DESIGN, "replaced": sorted(replaced), "rooms": ROOM_FLOORS, "objects": rows}
    with open(os.path.join(OUT_DIR, name + ".manifest.json"), "w") as f: json.dump(man, f, indent=1)
    return glb, len(rows), counts


result = None
try:
    result = export()
finally:
    if bpy.data.filepath and bpy.data.is_dirty and not bpy.app.background:
        bpy.ops.wm.revert_mainfile()      # discard the in-memory metadata edits
print("EXPORT:", result)
