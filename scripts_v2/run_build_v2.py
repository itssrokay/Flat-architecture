# Run with: Blender --background --factory-startup --python scripts_v2/run_build_v2.py
import bpy, json, runpy, mathutils
BASE = "/Users/shraj/Documents/MyFlat/"
src = BASE + "build_MyFlat_V2_Architecture.py"
code = open(src).read()
ns = runpy.run_path(src, run_name="myflat_v2")
d = ns['run']()
for t in list(bpy.data.texts): bpy.data.texts.remove(t)
bpy.data.texts.new("build_MyFlat_V2_Architecture.py").write(code)
for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras):
    for x in list(blk):
        if x.users == 0: blk.remove(x)
bpy.ops.wm.save_as_mainfile(filepath=BASE + "MyFlat_V2_Architecture.blend", compress=True)
o = bpy.data.objects
dg = bpy.context.evaluated_depsgraph_get()
def bb(n):
    ob = o[n]; f = 1/0.3048
    pts = [ob.matrix_world @ mathutils.Vector(c) for c in ob.bound_box]
    return [round(min(p.x for p in pts)*f,2), round(max(p.x for p in pts)*f,2), round(min(p.y for p in pts)*f,2), round(max(p.y for p in pts)*f,2)]
names = ["PILLAR_1","PILLAR_2","PILLAR_GATE_E","DOOR_MAIN_CUTTER","OPENING_HALL_GATE_CUTTER","DOOR_KITCHEN_CUTTER","DOOR_R2_EXIT1_CUTTER","DOOR_R2_EXIT2_CUTTER","DOOR_B2_CUTTER","COL_B2_E","WALL_INT_R2_TUB","WINDOW_W3_CUTTER","WINDOW_W4_CUTTER","WINDOW_W5_CUTTER","WINDOW_W6_CUTTER","WINDOW_HALL_W_CUTTER","WINDOW_W9_PASSAGE_HALL_CUTTER","COL_R2_E_TUB","COL_R2_E_MID","PILASTER_HALL_W_P2","PILASTER_HALL_W_P1","OPENING_HALLSTRIP_OPENSQ_CUTTER","WALL_INT_B1_W","WALL_EXT_W_HALL"]
bad = []
for w in o:
    if w.type == 'MESH' and w.modifiers:
        ev = w.evaluated_get(dg)
        if len(ev.data.vertices) == 0: bad.append(w.name)
keys = ['xK0','xK1','xB0','xB1','xR20','xR21N','xR21S','xH0','xH1','yH0','yP1','yR21','yB1n']
res = {"n_obj": len(o), "d": {k: round(d[k],3) for k in keys}, "bb": {n: bb(n) for n in names if n in o},
       "missing": [n for n in names if n not in o], "empty_after_boolean": bad}
json.dump(res, open(BASE + "scripts_v2/build_v2_report.json", "w"), indent=1)
