# Blender --background --factory-startup --python scripts_v2/build_v2_designs.py
# V2 architecture + Room 1 designs (appended from the V1.3 file; Room 1 did not move) + Room 2 en-suite V2 + hall designs V2.
import bpy, json, runpy, mathutils
BASE = "/Users/shraj/Documents/MyFlat/"
bpy.ops.wm.open_mainfile(filepath=BASE + "MyFlat_V2_Architecture.blend")
sc = bpy.context.scene
src = BASE + "MyFlat_V1_3_Hall_Designs.blend"
with bpy.data.libraries.load(src, link=False) as (df, dt):
    names = sorted(n for n in df.collections if n[:3] in ("13_", "14_", "15_", "16_", "17_", "18_"))
    dt.collections = names
r1 = []
for c in dt.collections:
    sc.collection.children.link(c); r1.append((c.name, len(c.all_objects), c.get("design_option"), c.get("replaces")))
rep = {"room1": r1}
rep["ensuite"] = runpy.run_path(BASE + "build_room2_ensuite_v2.py", run_name="r2")["run"]()
rep["hall"] = runpy.run_path(BASE + "build_hall_designs_v2.py", run_name="hall")["run"]("HALL_BEST")
rep["room2_bedroom"] = runpy.run_path(BASE + "build_room2_bedroom_v2.py", run_name="r2br")["run"]()
vl = bpy.context.view_layer
for n, *_ in r1:
    hide = not n.startswith("13_")
    vl.layer_collection.children[n].hide_viewport = hide; bpy.data.collections[n].hide_render = hide
for t in list(bpy.data.texts): bpy.data.texts.remove(t)
for f in ("build_MyFlat_V2_Architecture.py", "build_room2_ensuite_v2.py", "build_hall_designs_v2.py", "build_room2_bedroom_v2.py"):
    bpy.data.texts.new(f).write(open(BASE + f).read())
sc["myflat_version"] = "V2_Designs"
bpy.ops.wm.save_as_mainfile(filepath=BASE + "MyFlat_V2_Designs.blend", compress=True)
rep["n_obj"] = len(bpy.data.objects)
rep["hall"] = {k: (v if not isinstance(v, (list, tuple)) else list(v)) for k, v in rep["hall"].items()}
json.dump(rep, open(BASE + "scripts_v2/build_v2_designs_report.json", "w"), indent=1, default=str)
