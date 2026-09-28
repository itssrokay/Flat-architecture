"""Immersive-feature checks: openable parts, balcony access, lights/night, dimensions, immersive mode.
Usage: python3 scripts/test_immersive.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/?lowq=1"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_immersive"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
WALK = """([open, yft]) => { const W = viewer.walk, V = app.center.constructor, FT = 0.3048;
  if (open) viewer.imm.setAll(true); else viewer.imm.setAll(false);
  for (let i = 0; i < 40; i++) viewer.imm.update(0.05);          // finish animations
  W.exit(); W.enter(new V(2.0 * FT, 1.6, -yft * FT), new V(-10, 1.6, -yft * FT));
  W.yaw = Math.PI / 2; W.keys.clear(); W.keys.add('KeyW');
  for (let i = 0; i < 120; i++) W.update(0.05);
  W.keys.clear(); const x = W.cam.position.x / FT; const info = document.getElementById('walkInfo').textContent; W.exit();
  return { x, info }; }"""
async def shot(pg, name, wait=2500):
    await pg.wait_for_timeout(wait); await pg.screenshot(path=f"{OUT}/{name}.png")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1600, "height": 950}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(BASE); await pg.wait_for_function("window.app && app.ready")
        n = await pg.evaluate("() => viewer.imm.groups.size"); check("openable parts found (DEFAULT)", n >= 8, f"{n} groups")
        for f, label, yft in [("DEFAULT", "DEFAULT", -3.0), ("OPTION_A", "A", -3.0), ("OPTION_B", "B", -4.0), ("OPTION_C", "C", -3.0), ("OPTION_D", "D", -6.0), ("OPTION_E", "E", -6.0)]:
            if f != "DEFAULT":
                await pg.evaluate(f"viewer.switchModel('MyFlat_V1_1_Room1_{f}.glb')"); await pg.wait_for_function(f"app.ready && app.modelFile.endsWith('{f}.glb') && viewer.imm.groups.size > 0")
            closed = await pg.evaluate(WALK, [False, yft]); opened = await pg.evaluate(WALK, [True, yft])
            ok = (closed["x"] > -0.3 or label == "C") and opened["x"] < -1.6      # C's bi-fold is shown folded open
            check(f"{label}: closed balcony door blocks, opened door lets you walk onto the balcony", ok, f"closed x={closed['x']:.2f} ft, open x={opened['x']:.2f} ft ({opened['info'][:40]})")
        await pg.evaluate("viewer.switchModel('MyFlat_V1_1_Room1_DEFAULT.glb')"); await pg.wait_for_function("app.ready && app.modelFile.endsWith('DEFAULT.glb') && viewer.imm.groups.size > 0")
        # wardrobe open
        await pg.evaluate("viewer.imm.setAll(false); viewer.goRoom('Room 1', 2)"); await pg.wait_for_function("!app.tween")
        await pg.evaluate("() => { const g = viewer.imm.groups; ['WARDROBE_DOOR_1','WARDROBE_DOOR_2','WARDROBE_DOOR_3','WARDROBE_LOFT_DOOR_2'].forEach(k => viewer.imm.toggle(g.get(k), true)); }")
        await pg.wait_for_timeout(1500)
        rot = await pg.evaluate("() => { const o = viewer.scene.getObjectByName('R1_DEF_WARDROBE_DOOR_1'); return new app.center.constructor(0,0,1).applyQuaternion(o.quaternion).toArray(); }")
        check("wardrobe door swings open", abs(rot[2]) < 0.5, f"door normal {[round(v,2) for v in rot]}")
        await shot(pg, "01_wardrobe_open")
        # balcony door open, sheer drawn back, view out
        await pg.evaluate("viewer.imm.setAll(true); viewer.goRoom('Room 1', 1)"); await pg.wait_for_function("!app.tween"); await shot(pg, "02_balcony_door_open")
        # night + lights
        await pg.evaluate("viewer.imm.setNight(true); viewer.imm.setLights(true); viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween")
        nl = await pg.evaluate("() => viewer.imm.lights.filter(l => l.isLight && l.visible).length"); check("night mode switches on fixture lights", nl >= 6, f"{nl} lights")
        await shot(pg, "03_night_lights_on", 4000)
        await pg.evaluate("viewer.imm.setLights(false)"); await shot(pg, "04_night_lights_off", 4000)
        off = await pg.evaluate("() => viewer.imm.lights.filter(l => l.isLight && l.visible).length"); check("lights off", off == 0)
        await pg.evaluate("viewer.imm.setNight(false); viewer.imm.setLights(true)")
        # dimensions
        await pg.evaluate("viewer.imm.setDims(true); viewer.select(viewer.scene.getObjectByName('R1_DEF_BED_BASE')); viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween")
        await pg.wait_for_timeout(3000)
        nd = await pg.evaluate("() => [...document.querySelectorAll('.lbl-dim')].filter(e => e.style.display !== 'none').length")
        sel = await pg.evaluate("() => [...document.querySelectorAll('.lbl-dim.sel')].map(e => e.textContent)")
        check("dimensions: labels + W/D/H of selected bed", nd > 10 and len(sel) == 3, f"{nd} labels; bed {sel}")
        await shot(pg, "05_dimensions", 500)
        await pg.evaluate("() => { const r = app.rooms.find(r=>r.name==='Room 1'); const vp = r.vps.find(v=>v.name.startsWith('From above')); viewer.setCat('roof', false); viewer.setCat('ceiling', false); viewer.camera.position.copy(vp.pos); viewer.controls.target.copy(vp.target); app.tween=null; }")
        await shot(pg, "06_dimensions_above")
        await pg.evaluate("viewer.imm.setDims(false); viewer.select(null); viewer.setCat('roof', true); viewer.setCat('ceiling', true)")
        # immersive
        await pg.evaluate("viewer.imm.setImmersive(true); viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween")
        imm = await pg.evaluate("() => ({cls: document.body.classList.contains('immersive'), bar: getComputedStyle(document.getElementById('immBar')).display, w: viewer.renderer.domElement.clientWidth})")
        check("immersive mode: panels hidden, toolbar shown, full-width view", imm["cls"] and imm["bar"] == "flex" and imm["w"] > 1500, str(imm))
        await pg.evaluate("viewer.startWalk()"); await pg.wait_for_timeout(4000)
        hint = await pg.evaluate("() => !document.getElementById('crosshair').classList.contains('hidden')")
        check("walk shows crosshair for E-interaction", hint)
        await shot(pg, "07_immersive_walk")
        await pg.evaluate("viewer.walk.exit(); viewer.imm.setImmersive(false)")
        notes = await pg.evaluate("() => document.querySelector('#designNotes .sched') ? document.querySelector('#designNotes .sched').innerText.length : 0")
        check("material & finish schedule shown", notes > 500, f"{notes} chars")
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
