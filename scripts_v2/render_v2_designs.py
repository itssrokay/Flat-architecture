import bpy
from mathutils import Vector
BASE = "/Users/shraj/Documents/MyFlat/"; FT = 0.3048
bpy.ops.wm.open_mainfile(filepath=BASE + "MyFlat_V2_Designs.blend")
sc = bpy.context.scene
bpy.data.objects["SLAB_ROOF"].hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("LBL_"): o.hide_render = True
    if o.name.startswith("HBB_GYPSUM") : pass
def cam(nm, loc, look, lens=16, res=(1600, 1000)):
    cd = bpy.data.cameras.new(nm); o = bpy.data.objects.new(nm, cd); sc.collection.objects.link(o)
    o.location = Vector([v * FT for v in loc]); cd.clip_start = 0.05; cd.clip_end = 500; cd.lens = lens
    o.rotation_euler = (Vector([v * FT for v in look]) - o.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o; sc.render.resolution_x, sc.render.resolution_y = res
def shot(fn):
    sc.render.filepath = BASE + "renders_v2/" + fn; bpy.ops.render.render(write_still=True)
sc.display.shading.color_type = 'TEXTURE'
top = bpy.data.objects["CAM_TOP_ORTHO"]; sc.camera = top; sc.render.resolution_x = sc.render.resolution_y = 1400
hide = [o for o in bpy.data.objects if o.name.startswith(("BEAM_", "HBB_GYPSUM", "HBB_COVE", "HBB_DOWNLIGHT", "HBB_FAN"))]
for o in hide: o.hide_render = True
shot("D1_TOP.png")
for o in hide: o.hide_render = False
cam("C1", (17.5, -30.1, 5.2), (6.5, -30.1, 4.2)); shot("D2_TV_WALL.png")
cam("C2", (26.0, -44.0, 5.4), (9.0, -22.0, 3.5)); shot("D3_HALL_SE.png")
cam("C3", (8.0, -16.5, 5.4), (20.0, -40.0, 3.0)); shot("D4_HALL_NW.png")
cam("C4", (29.2, -5.4, 5.2), (39.5, -1.0, 2.5)); shot("D5_TUB.png")
cam("C7", (37.5, -4.6, 5.0), (31.0, -6.0, 3.2)); shot("D7_VANITY.png")
cam("C8", (30.0, -21.5, 5.4), (36.5, -8.5, 2.2)); shot("D8_R2_BED.png")
cam("C9", (37.0, -9.0, 5.4), (30.0, -20.0, 3.0)); shot("D9_R2_WARDROBE.png")
cam("C5", (29.5, -22.5, 5.2), (33.0, -6.5, 4.0)); shot("D6_BEDROOM.png")
