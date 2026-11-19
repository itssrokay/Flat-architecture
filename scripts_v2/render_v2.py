import bpy
BASE = "/Users/shraj/Documents/MyFlat/"
bpy.ops.wm.open_mainfile(filepath=BASE + "MyFlat_V2_Architecture.blend")
sc = bpy.context.scene
for n in ("SLAB_ROOF",): bpy.data.objects[n].hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("LBL_") or o.name.startswith("BEAM_"): o.hide_render = False
sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
for cam, fn, hide_beams in (("CAM_TOP_ORTHO", "01_TOP_ORTHO.png", True), ("CAM_HALL", "02_HALL.png", False),
                            ("CAM_ROOM2", "03_ROOM2.png", False), ("CAM_EXTERIOR", "04_EXTERIOR.png", False)):
    sc.camera = bpy.data.objects[cam]
    r = sc.camera.get("res", (1600, 1000)); sc.render.resolution_x, sc.render.resolution_y = int(r[0]), int(r[1])
    for o in bpy.data.objects:
        if o.name.startswith("BEAM_"): o.hide_render = hide_beams
    bpy.data.objects["SLAB_ROOF"].hide_render = cam != "CAM_EXTERIOR" and True
    sc.render.filepath = BASE + "renders_v2/" + fn
    bpy.ops.render.render(write_still=True)
