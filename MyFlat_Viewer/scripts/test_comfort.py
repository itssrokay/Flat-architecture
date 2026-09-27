"""Comfort-feature checks: collapsible panels, image-style zoom, lens / ceiling view, hover info,
opening parts that stop at furniture, and focused room dimensions.
Usage: python3 scripts/test_comfort.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/?lowq=1"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_comfort"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
SEP = "?" if "?" not in BASE else "&"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1600, "height": 950}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(BASE); await pg.wait_for_function("window.app && app.ready"); await pg.wait_for_timeout(1000)

        # ---- panels
        w0 = await pg.evaluate("() => viewer.renderer.domElement.clientWidth")
        await pg.click("#leftTab"); await pg.click("#rightTab"); await pg.wait_for_timeout(800)
        st = await pg.evaluate("() => ({l: getComputedStyle(document.getElementById('left')).display, r: getComputedStyle(document.getElementById('right')).display, w: viewer.renderer.domElement.clientWidth})")
        check("left and right panels hide (view gets wider)", st["l"] == "none" and st["r"] == "none" and st["w"] > w0 + 400, f"{w0} -> {st['w']} px")
        await pg.screenshot(path=f"{OUT}/01_panels_hidden.png")
        await pg.click("#leftTab"); await pg.click("#rightTab"); await pg.wait_for_timeout(500)
        await pg.evaluate("viewer.overview()"); await pg.wait_for_function("!app.tween")
        await pg.click("#dock section h4.sec-head >> nth=0")
        mn = await pg.evaluate("() => ({min: document.querySelector('#dock section').classList.contains('min'), chips: getComputedStyle(document.getElementById('catToggles')).display})")
        check("dock section (Visibility) minimises to its title", mn["min"] and mn["chips"] == "none", str(mn))
        await pg.click("#dock section h4.sec-head >> nth=0")

        # ---- image-style zoom towards the balcony
        await pg.evaluate("viewer.presetView('iso')"); await pg.wait_for_function("!app.tween")
        xy = await pg.evaluate("""() => { const o = viewer.scene.getObjectByName('BALCONY_FLOOR'); const c = new app.bbox.constructor().setFromObject(o).getCenter(new app.center.constructor());
            window._P = c.clone(); c.project(viewer.camera); const r = viewer.renderer.domElement.getBoundingClientRect(); return [r.left + (c.x+1)/2*r.width, r.top + (1-c.y)/2*r.height]; }""")
        d0 = await pg.evaluate("() => viewer.camera.position.distanceTo(window._P)")
        await pg.mouse.move(xy[0], xy[1])
        for _ in range(6): await pg.mouse.wheel(0, -200); await pg.wait_for_timeout(120)
        await pg.wait_for_timeout(3000)
        z = await pg.evaluate("""() => { const c = window._P.clone(); const d = viewer.camera.position.distanceTo(c); c.project(viewer.camera); const r = viewer.renderer.domElement.getBoundingClientRect();
            return { d, x: r.left + (c.x+1)/2*r.width, y: r.top + (1-c.y)/2*r.height }; }""")
        drift = ((z["x"] - xy[0]) ** 2 + (z["y"] - xy[1]) ** 2) ** 0.5
        check("wheel zooms straight towards the point under the cursor (balcony stays under the mouse)", z["d"] < d0 * 0.5 and drift < 40,
              f"distance {d0:.1f} -> {z['d']:.1f} m, point drifted {drift:.0f} px")
        await pg.screenshot(path=f"{OUT}/02_zoomed_to_balcony.png")

        # ---- inside: ceiling view + lens
        await pg.evaluate("viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(500)
        await pg.click("#ceilBtn"); await pg.wait_for_timeout(2500)
        c = await pg.evaluate("() => ({pitch: viewer.walk.pitch, fov: viewer.camera.fov, walk: viewer.walk.active})")
        check("Look at ceiling: straight up with a wide lens", c["walk"] and c["pitch"] > 1.3 and c["fov"] >= 95, str(c))
        await pg.screenshot(path=f"{OUT}/03_ceiling_view.png")
        await pg.click("#ceilBtn"); await pg.wait_for_timeout(800)
        box = await pg.evaluate("() => { const r = viewer.renderer.domElement.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; }")
        await pg.mouse.move(*box); await pg.keyboard.down("Control")
        for _ in range(4): await pg.mouse.wheel(0, 60); await pg.wait_for_timeout(100)
        await pg.keyboard.up("Control"); await pg.wait_for_timeout(600)
        f = await pg.evaluate("() => viewer.camera.fov")
        check("inside: pinch / Ctrl+wheel widens the lens", f > 65, f"fov {f:.0f}°")

        # ---- hover info
        await pg.evaluate("viewer.ex.setFov(60); viewer.walk.pitch = -0.25")
        await pg.click("#hoverBtn"); await pg.wait_for_timeout(2500)
        xy = await pg.evaluate("() => { const r = viewer.renderer.domElement.getBoundingClientRect(); return [r.left + r.width * 0.55, r.top + r.height * 0.62]; }")
        await pg.mouse.move(xy[0] - 5, xy[1]); await pg.mouse.move(xy[0], xy[1]); await pg.wait_for_timeout(2500)
        tip = await pg.evaluate("() => ({hidden: document.getElementById('hoverTip').classList.contains('hidden'), txt: document.getElementById('hoverTip').innerText})")
        check("hover info: pointing at an object shows what it is", not tip["hidden"] and "Size" in tip["txt"], tip["txt"].replace("\n", " | ")[:200])
        await pg.screenshot(path=f"{OUT}/04_hover_info.png")
        await pg.click("#hoverBtn")

        # ---- room size
        await pg.evaluate("viewer.ex.setRoomDims(true)"); await pg.wait_for_timeout(1500)
        labels = await pg.evaluate("() => viewer.ex.roomDimLabels().map(t => t.replace(/\\n/g, ' | '))")
        check("room size: wall lengths, area and ceiling height of the room you are in",
              any("12' 7\"" in l for l in labels) and any("14' 6\"" in l for l in labels) and any("sq ft" in l for l in labels), "; ".join(labels))
        await pg.evaluate("viewer.overview()"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"{OUT}/05_room_size_overview.png")
        await pg.evaluate("viewer.ex.setRoomDims(false)")

        # ---- opening parts stop at furniture (put a lamp back in the window's path, as the old design had it)
        await pg.evaluate("viewer.switchModel('MyFlat_V1_1_Room1_OPTION_B.glb')"); await pg.wait_for_function("app.ready && app.modelFile.endsWith('OPTION_B.glb') && viewer.imm.groups.size > 0")
        free = await pg.evaluate("() => { const I = viewer.imm; const g = I.groups.get('W1_CASEMENT'); I.toggle(g, true); for (let i=0;i<40;i++) I.update(0.05); const t = g.t; I.toggle(g, false); for (let i=0;i<40;i++) I.update(0.05); return t; }")
        check("Option B: window now opens fully (reading light moved clear of the sash)", free == 1, f"t={free}")
        blk = await pg.evaluate("""() => { const I = viewer.imm; const lamp = viewer.scene.getObjectByName('R1_OPB_READING_LIGHT_W');
            lamp.position.set(2.057, 1.417, 0.244); lamp.updateMatrixWorld(true); I.onModel(app.model);
            const g = I.groups.get('W1_CASEMENT'); I.toggle(g, true); for (let i=0;i<40;i++) I.update(0.05);
            return { t: g.t, by: g.blockedBy, toast: document.getElementById('toast').innerText }; }""")
        check("a sash that meets a lamp stops there instead of passing through it", 0.2 < blk["t"] < 1 and "READING_LIGHT" in (blk["by"] or ""), str(blk))
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
