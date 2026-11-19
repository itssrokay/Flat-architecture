# V1.5/V1.6 viewer: "What's inside" layers, real-paint walls, shopping list. Expects src/inside.js, src/inside.css.part,
# models/layers.json and models/shop.json to be in place already. Run from the MyFlat folder. Safe to re-run.
import os, sys
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")
V = "MyFlat_Viewer/"
css = open(V + "src/inside.css.part", encoding="utf-8").read()
p = V + "src/styles.css"; s = open(p, encoding="utf-8").read()
if "V1.5 what's inside" not in s: s += css
elif "V1.6 reasons" not in s and "V1.6 reasons" in css: s += css[css.index("/* ---- V1.6 reasons"):]
open(p, "w", encoding="utf-8").write(s)
p = V + "index.html"; s = open(p, encoding="utf-8").read()
if "inside.js" not in s:
    s = s.replace('<script type="module" src="./src/declutter.js?v=21"></script>', '<script type="module" src="./src/declutter.js?v=21"></script>\n<script type="module" src="./src/inside.js?v=21"></script>')
assert "inside.js" in s
s = s.replace("?v=21", "?v=23").replace("?v=22", "?v=23")
open(p, "w", encoding="utf-8").write(s)
p = V + "src/main.js"; s = open(p, encoding="utf-8").read().replace("BUILD = '21'", "BUILD = '23'").replace("BUILD = '22'", "BUILD = '23'")
open(p, "w", encoding="utf-8").write(s)
print("viewer updated (v1.5 what's inside)")
