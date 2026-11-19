# Run from any Python that can launch Blender: builds nothing, exports every V2 model to MyFlat_Viewer/models.
import subprocess, sys, json
BL = sys.argv[1] if len(sys.argv) > 1 else "/Applications/Blender.app/Contents/MacOS/Blender"
BASE = "/Users/shraj/Documents/MyFlat/"
COMBOS = [("MyFlat_V2_Hall_BestOfBoth", ["DEFAULT", "HALL_BEST"]), ("MyFlat_V2_Hall_Recommended", ["DEFAULT", "HALL_REC"]),
          ("MyFlat_V2_Hall_Budget", ["OPTION_D", "HALL_BUDGET"]), ("MyFlat_V2_Hall_LongLasting", ["DEFAULT", "HALL_LONG"]),
          ("MyFlat_V2_Hall_Marble", ["OPTION_C", "HALL_MARBLE"]), ("MyFlat_V2_Hall_Panelled", ["DEFAULT", "HALL_PANEL"]),
          ("MyFlat_V2_Room2_Ensuite", ["DEFAULT", "HALL_BEST"])] + \
         [("MyFlat_V2_Room1_" + o, [o, "HALL_BEST"]) for o in ("DEFAULT", "OPTION_A", "OPTION_B", "OPTION_C", "OPTION_D", "OPTION_E")]
out = []
for name, designs in COMBOS:
    expr = f"DESIGNS={designs!r}; OUT_NAME={name!r}; exec(open({BASE + 'MyFlat_Viewer/scripts/export_glb.py'!r}).read())"
    r = subprocess.run([BL, "--background", "--factory-startup", BASE + "MyFlat_V2_Designs.blend", "--python-expr", expr], capture_output=True, text=True, timeout=900)
    line = [l for l in r.stdout.splitlines() if l.startswith("EXPORT")]
    out.append((name, r.returncode, line[-1][:160] if line else r.stderr[-300:]))
json.dump(out, open(BASE + "scripts_v2/export_v2_report.json", "w"), indent=1)
