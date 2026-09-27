# Validation renders for MyFlat_V1_Architecture -> ~/Documents/MyFlat/renders_v1
import bpy, os
OUT = os.path.join(os.path.expanduser("~"), "Documents", "MyFlat", "renders_v1")

def render_views(names=None):
    os.makedirs(OUT, exist_ok=True)
    sc = bpy.context.scene; sh = sc.display.shading
    C = bpy.data.collections
    roof, labels, prov = C["03_CEILING_SLAB"], C["LABELS"], C["12_PROVISIONAL"]
    plan = bpy.data.objects.get("PLAN_REFERENCE")
    views = {  # camera, roof, labels, plan, colour mode, output name
        "01_TOP_ORTHO":        ("CAM_TOP_ORTHO", False, True, False, 'MATERIAL'),
        "02_TOP_STATUS_MAP":   ("CAM_TOP_ORTHO", False, True, False, 'OBJECT'),
        "03_TOP_COMPARE_PLAN": ("CAM_TOP_COMPARE", False, True, True, 'TEXTURE'),
        "04_EXTERIOR":         ("CAM_EXTERIOR", True, False, False, 'MATERIAL'),
        "05_HALL":             ("CAM_HALL", True, False, False, 'MATERIAL'),
        "06_ROOM1":            ("CAM_ROOM1", True, False, False, 'MATERIAL'),
        "07_ROOM2":            ("CAM_ROOM2", True, False, False, 'MATERIAL'),
        "08_STAIR_OPENSQ":     ("CAM_STAIR_OPENSQ", True, False, False, 'MATERIAL'),
    }
    out = []
    for n, (cam, r, lab, pl, col) in views.items():
        if names and n not in names: continue
        c = bpy.data.objects[cam]; sc.camera = c
        res = c.get("res", (1600, 1000)); sc.render.resolution_x, sc.render.resolution_y = int(res[0]), int(res[1])
        sc.render.resolution_percentage = 100
        roof.hide_render = not r; labels.hide_render = not lab
        if plan: plan.hide_render = not pl
        top = n.startswith("0") and "TOP" in n
        sh.light = 'FLAT' if top else 'STUDIO'; sh.show_shadows = not top; sh.color_type = col
        sc.render.filepath = os.path.join(OUT, n + ".png")
        bpy.ops.render.render(write_still=True); out.append(sc.render.filepath)
    roof.hide_render = False; labels.hide_render = False
    sh.color_type = 'MATERIAL'; sh.light = 'STUDIO'; sh.show_shadows = True
    sc.camera = bpy.data.objects["CAM_TOP_ORTHO"]
    return out
