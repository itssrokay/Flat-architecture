# One-shot: build the model, embed scripts + assumptions as text blocks, save
# MyFlat_Trial_V0.blend and render preview images. Run from Blender's Text Editor.
import bpy, os
D = os.path.join(os.path.expanduser("~"), "Documents", "MyFlat")
g = {"__name__": "flatbuild"}
exec(open(os.path.join(D, "build_MyFlat_Trial_V0.py")).read(), g)
g["run"]()
for fn, tn in (("build_MyFlat_Trial_V0.py", "build_MyFlat_Trial_V0.py"),
               ("render_views.py", "render_views.py"),
               ("TRIAL_ASSUMPTIONS.txt", "TRIAL_ASSUMPTIONS")):
    t = bpy.data.texts.get(tn) or bpy.data.texts.new(tn)
    t.clear(); t.write(open(os.path.join(D, fn)).read())
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "MyFlat_Trial_V0.blend"))
r = {"__name__": "rv"}
exec(open(os.path.join(D, "render_views.py")).read(), r)
r["render_views"]()
bpy.ops.wm.save_mainfile()
