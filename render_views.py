# Renders preview images for MyFlat_Trial_V0 into ~/Documents/MyFlat/renders
import bpy, os
OUT = os.path.join(os.path.expanduser("~"), "Documents", "MyFlat", "renders")
os.makedirs(OUT, exist_ok=True)

def render_views(names=None):
    sc = bpy.context.scene
    vl = bpy.context.view_layer.layer_collection
    arch = vl.children["01_ARCHITECTURE"]
    ceil = bpy.data.collections["Ceilings"]
    labels = bpy.data.collections["Labels"]
    ph = bpy.data.collections["07_PLACEHOLDERS"]
    plan = bpy.data.objects.get("PLAN_REFERENCE")
    plan_mat = bpy.data.materials.get("PlanImage")
    cams = {
        "TOP_VIEW": dict(ceil=False, labels=True, plan=False),
        "TOP_VIEW_COMPARE": dict(ceil=False, labels=True, plan=True),
        "PERSP_Aerial_SE": dict(ceil=False, labels=False, plan=False),
        "PERSP_Aerial_NW": dict(ceil=False, labels=False, plan=False),
        "PERSP_Hall_Interior": dict(ceil=True, labels=False, plan=False),
        "PERSP_Room2_Interior": dict(ceil=True, labels=False, plan=False),
    }
    sh = sc.display.shading
    out = []
    for n, s in cams.items():
        if names and n not in names: continue
        cam = bpy.data.objects[n]
        sc.camera = cam
        r = cam.get("res", (1600, 1000)); sc.render.resolution_x, sc.render.resolution_y = int(r[0]), int(r[1])
        sc.render.resolution_percentage = 100
        ceil.hide_render = not s["ceil"]
        labels.hide_render = not s["labels"]; ph.hide_render = not s["labels"]
        if plan: plan.hide_render = not s["plan"]
        # plan image needs texture colour in workbench
        sh.color_type = 'TEXTURE' if s["plan"] else 'MATERIAL'
        top = n.startswith("TOP")
        sh.show_shadows = not top           # shadows smear the plan view
        sh.shadow_intensity = 0.35
        sh.light = 'FLAT' if top else 'STUDIO'
        sc.render.filepath = os.path.join(OUT, n + ".png")
        bpy.ops.render.render(write_still=True)
        out.append(sc.render.filepath)
    ceil.hide_render = False; labels.hide_render = False; ph.hide_render = False
    sh.color_type = 'MATERIAL'; sc.camera = bpy.data.objects["TOP_VIEW"]
    return out
