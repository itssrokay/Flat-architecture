"""Navigation checks: no going under the ground, no white screen inside walls, inside (walk) views,
drag-to-look, wheel / keyboard travel, eye height, overview, double-click-to-stand-here.
Usage: python3 scripts/test_navigation.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/?lowq=1"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_navigation"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1600, "height": 950}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(BASE); await pg.wait_for_function("window.app && app.ready")
        await pg.wait_for_timeout(1500)
        check("opens inside Room 1 (walk mode)", await pg.evaluate("() => viewer.walk.active"))

        sides = await pg.evaluate("""() => { const s = {}; viewer.scene.traverse(o => { if (!o.isMesh) return; let c = null; for (let p = o; p && !c; p = p.parent) c = p.userData?.category;
            (s[c] = s[c] || {front: 0, double: 0})[o.material.side === 0 ? 'front' : 'double']++; }); return s; }""")
        w = sides.get("walls", {}); c = sides.get("ceiling", {}) ; r = sides.get("roof", {})
        check("walls / ceiling / roof are one-sided (see through from inside, no white screen)",
              w.get("double", 1) == 0 and c.get("double", 0) == 0 and r.get("double", 0) == 0, json.dumps({k: sides[k] for k in sides if k in ("walls", "ceiling", "roof", "fenestration", "soft_furnishing")}))

        # overview button
        await pg.click("#overviewBtn"); await pg.wait_for_function("!app.tween")
        check("Overview button: steps outside to the whole-flat view", not await pg.evaluate("() => viewer.walk.active"))

        # orbit hard downwards: must stay above the ground
        box = await pg.evaluate("() => { const r = viewer.renderer.domElement.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; }")
        await pg.mouse.move(*box); await pg.mouse.down()
        for i in range(12): await pg.mouse.move(box[0], box[1] - 40 * (i + 1))
        await pg.mouse.up(); await pg.wait_for_timeout(1500)
        st = await pg.evaluate("() => ({cy: viewer.camera.position.y, ty: viewer.controls.target.y})")
        check("orbiting down never goes under the house", st["cy"] > st["ty"] and st["cy"] > 0, str(st))

        # keyboard travel in the overview
        t0 = await pg.evaluate("() => viewer.controls.target.toArray()")
        await pg.keyboard.down("KeyW"); await pg.wait_for_timeout(1500); await pg.keyboard.up("KeyW")
        t1 = await pg.evaluate("() => viewer.controls.target.toArray()")
        d = sum((a - b_) ** 2 for a, b_ in zip(t0, t1)) ** 0.5
        check("overview: W slides the view forward (camera + pivot)", d > 0.3, f"moved {d:.2f} m")

        # double-click a floor -> stand there
        await pg.click("#dockToggle")            # the controls panel covers the lower part of the view
        await pg.evaluate("viewer.presetView('top')"); await pg.wait_for_function("!app.tween")
        xy = await pg.evaluate("""() => { const r = app.rooms.find(r => r.name === 'Hall'); const c = r.center.clone(); c.project(viewer.camera);
            const b = viewer.renderer.domElement.getBoundingClientRect(); return [b.left + (c.x+1)/2*b.width, b.top + (1-c.y)/2*b.height]; }""")
        await pg.mouse.dblclick(xy[0], xy[1]); await pg.wait_for_timeout(500); await pg.wait_for_function("!app.tween")
        await pg.wait_for_timeout(300)
        wk = await pg.evaluate("() => ({on: viewer.walk.active, info: document.getElementById('walkInfo').textContent})")
        check("double-click a floor in the overview: you stand there", wk["on"], wk["info"])
        await pg.screenshot(path=f"{OUT}/01_stand_in_hall.png")
        await pg.click("#dockToggle")

        # room viewpoint -> inside
        await pg.evaluate("viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(300)
        check("room viewpoint puts you inside (walk)", await pg.evaluate("() => viewer.walk.active"))

        # drag up = look up at the ceiling
        p0 = await pg.evaluate("() => viewer.walk.pitch")
        await pg.mouse.move(*box); await pg.mouse.down()
        for i in range(10): await pg.mouse.move(box[0], box[1] + 25 * (i + 1))
        await pg.mouse.up(); await pg.wait_for_timeout(600)
        p1 = await pg.evaluate("() => viewer.walk.pitch")
        check("inside: drag looks around (up at the ceiling)", p1 > p0 + 0.5, f"pitch {p0:.2f} -> {p1:.2f}")
        await pg.screenshot(path=f"{OUT}/02_look_up_ceiling.png")

        # R raises eye height
        e0 = await pg.evaluate("() => viewer.camera.position.y")
        await pg.keyboard.down("KeyR"); await pg.wait_for_timeout(3500); await pg.keyboard.up("KeyR")
        e1 = await pg.evaluate("() => viewer.camera.position.y")
        check("inside: R raises the eye (closer look at the ceiling)", e1 > e0 + 0.2, f"{e0:.2f} -> {e1:.2f} m")
        await pg.screenshot(path=f"{OUT}/03_eye_raised.png")

        # wheel steps forward
        await pg.evaluate("() => { viewer.walk.pitch = 0; viewer.walk.eyeOffset = 0; }")
        q0 = await pg.evaluate("() => viewer.camera.position.toArray()")
        await pg.mouse.move(*box)
        for _ in range(3): await pg.mouse.wheel(0, -120); await pg.wait_for_timeout(100)
        await pg.wait_for_timeout(2500)
        q1 = await pg.evaluate("() => viewer.camera.position.toArray()")
        d = ((q0[0] - q1[0]) ** 2 + (q0[2] - q1[2]) ** 2) ** 0.5
        check("inside: mouse wheel steps forward", d > 0.2, f"moved {d:.2f} m")

        # camera never inside the ceiling: eye stays below the ceiling at max raise
        await pg.evaluate("() => { viewer.walk.eyeOffset = 1.15; }"); await pg.wait_for_timeout(3000)
        cy = await pg.evaluate("""() => { const W = viewer.walk, V = app.center.constructor; W.ray.set(viewer.camera.position.clone(), new V(0, 1, 0)); W.ray.far = 5;
            const h = W.ray.intersectObjects(W.visibleIn(['ceiling','roof','beams']), false);
            return { eye: +viewer.camera.position.y.toFixed(2), ceil: h.length ? +h[0].point.y.toFixed(2) : null }; }""")
        check("highest eye position stays under the ceiling", cy["ceil"] is None or cy["eye"] < cy["ceil"] - 0.1, str(cy))
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
