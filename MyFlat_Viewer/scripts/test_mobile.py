"""Phone checks (emulated touch phone, 390x844): layout, slide-over panels, joystick walking, pinch lens,
tap to open AND close, double-tap to go inside, pinch zoom in the overview, tap info, minimisable HUD.
Also a desktop check that an opened sliding window can be clicked closed again.
Usage: python3 scripts/test_mobile.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_mobile"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
BASE_NOQ = BASE.split("?")[0]

async def touch(cdp, kind, pts):
    await cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)]})

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        # ------------------------------------------------ desktop: open a sliding window, then click it closed
        pg = await b.new_page(viewport={"width": 1500, "height": 900}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(BASE_NOQ + "?lowq=1"); await pg.wait_for_function("window.app && app.ready")
        await pg.evaluate("viewer.overview(); viewer.setCat('soft_furnishing', false)"); await pg.wait_for_function("!app.tween")
        async def click_on(name, off=(0.3, 0.2, 2.6)):
            xy = await pg.evaluate("""([n, off]) => { const o = viewer.scene.getObjectByName(n); const c = new app.bbox.constructor().setFromObject(o).getCenter(new app.center.constructor());
                viewer.controls.target.copy(c); viewer.camera.position.set(c.x + off[0], c.y + off[1], c.z + off[2]); viewer.controls.update(); app.tween = null; viewer.camera.updateMatrixWorld();
                c.project(viewer.camera); const r = viewer.renderer.domElement.getBoundingClientRect(); return [r.left + (c.x+1)/2*r.width, r.top + (1-c.y)/2*r.height]; }""", [name, list(off)])
            await pg.wait_for_timeout(600)
            return xy
        settle = lambda k: pg.wait_for_function(f"(() => {{ const g = viewer.imm.groups.get('{k}'); return g.t === (g.open ? 1 : 0); }})()")
        xy = await click_on("R1_DEF_W1_SASH_2_GLASS")
        await pg.mouse.dblclick(xy[0], xy[1]); await pg.wait_for_timeout(300); await settle("W1_SASH_2")
        o1 = await pg.evaluate("viewer.imm.groups.get('W1_SASH_2').open")
        xy = await click_on("R1_DEF_W1_SASH_1_GLASS")          # the opened sash now sits behind this fixed one
        await pg.mouse.dblclick(xy[0], xy[1]); await pg.wait_for_timeout(300); await settle("W1_SASH_2")
        o2 = await pg.evaluate("viewer.imm.groups.get('W1_SASH_2').open")
        check("desktop: an opened sliding window can be clicked closed again", o1 is True and o2 is False, f"after open: {o1}, after second click: {o2}")
        # balcony door: panels slide behind the fixed one
        xy = await click_on("R1_DEF_BALCONY_DOOR_P3_GLASS", (2.6, 0.2, 0.3)); await pg.mouse.dblclick(xy[0], xy[1]); await pg.wait_for_timeout(300); await settle("BALCONY_DOOR_P3")
        d1 = await pg.evaluate("viewer.imm.groups.get('BALCONY_DOOR_P3').open")
        xy = await click_on("R1_DEF_BALCONY_DOOR_P1_GLASS", (2.6, 0.2, 0.3)); await pg.mouse.dblclick(xy[0], xy[1]); await pg.wait_for_timeout(300); await settle("BALCONY_DOOR_P3"); await settle("BALCONY_DOOR_P2")
        d2 = await pg.evaluate("[...viewer.imm.groups].filter(([k, g]) => k.startsWith('BALCONY_DOOR') && g.open).map(([k]) => k)")
        check("desktop: an opened balcony door panel can be clicked closed from the fixed panel", d1 is True and "BALCONY_DOOR_P3" not in d2, f"open after: {d2}")
        # HUD minimise (desktop)
        await pg.evaluate("viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(300)
        await pg.click("#hudMin"); m1 = await pg.evaluate("document.getElementById('walkHud').classList.contains('min')")
        await pg.click("#walkHud .hudMini"); m2 = await pg.evaluate("document.getElementById('walkHud').classList.contains('min')")
        check("desktop: the 'Inside' box (with Look at ceiling) minimises and comes back", m1 and not m2)
        check("desktop: no JS errors", not errs, "; ".join(errs[:3]))
        await pg.close()

        # ------------------------------------------------ phone
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True,
                                  user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148")
        pg = await ctx.new_page(); pg.set_default_timeout(120000); cdp = await ctx.new_cdp_session(pg)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(BASE_NOQ + "?touch=1"); await pg.wait_for_function("window.app && app.ready"); await pg.wait_for_timeout(1500)
        lay = await pg.evaluate("""() => ({ w: viewer.renderer.domElement.clientWidth, left: getComputedStyle(document.getElementById('left')).display,
            touch: document.body.classList.contains('touch'), status: getComputedStyle(document.getElementById('statusBtn')).display,
            pad: !document.getElementById('touchPad').classList.contains('hidden'), hudMin: document.getElementById('walkHud').classList.contains('min'),
            dock: document.getElementById('dock').classList.contains('collapsed') })""")
        check("phone: full-width 3D view, side panels tucked away, desktop-only buttons hidden", lay["w"] >= 380 and lay["left"] == "none" and lay["status"] == "none", str(lay))
        check("phone: opens inside with joystick, small HUD and controls tucked away", lay["touch"] and lay["pad"] and lay["hudMin"] and lay["dock"], str(lay))
        await pg.screenshot(path=f"{OUT}/01_phone_inside.png")
        # joystick: push up for ~2.5 s
        jb = await pg.evaluate("() => { const r = document.getElementById('joy').getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; }")
        p0 = await pg.evaluate("viewer.camera.position.toArray()")
        await touch(cdp, "touchStart", [jb]); await touch(cdp, "touchMove", [(jb[0], jb[1] - 45)])
        await pg.wait_for_timeout(4000); await touch(cdp, "touchEnd", [])
        await pg.wait_for_timeout(500)
        p1 = await pg.evaluate("viewer.camera.position.toArray()")
        mv = ((p0[0] - p1[0]) ** 2 + (p0[2] - p1[2]) ** 2) ** 0.5
        check("phone: joystick walks you forward", mv > 0.3, f"moved {mv:.2f} m")
        # drag to look
        y0 = await pg.evaluate("viewer.walk.yaw")
        await touch(cdp, "touchStart", [(250, 400)]);
        for i in range(8): await touch(cdp, "touchMove", [(250 - 12 * (i + 1), 400)])
        await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(400)
        y1 = await pg.evaluate("viewer.walk.yaw")
        check("phone: one-finger drag looks around", abs(y1 - y0) > 0.2, f"yaw {y0:.2f} -> {y1:.2f}")
        # pinch for lens
        f0 = await pg.evaluate("viewer.camera.fov")
        await touch(cdp, "touchStart", [(170, 420), (220, 420)])
        for i in range(6): await touch(cdp, "touchMove", [(170 + 6 * i, 420), (220 - 6 * i, 420)])
        await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(500)
        f1 = await pg.evaluate("viewer.camera.fov")
        check("phone: pinch (fingers together) widens the lens inside", f1 > f0 + 5, f"fov {f0:.0f} -> {f1:.0f}")
        await pg.evaluate("viewer.ex.setFov(60)")
        # eye-up button
        e0 = await pg.evaluate("viewer.camera.position.y")
        ub = await pg.evaluate("() => { const r = document.querySelector('#touchBtns [data-t=up]').getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; }")
        await touch(cdp, "touchStart", [ub]); await pg.wait_for_timeout(2000); await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(400)
        e1 = await pg.evaluate("viewer.camera.position.y")
        check("phone: ⬆ button raises your eyes", e1 > e0 + 0.15, f"{e0:.2f} -> {e1:.2f}")
        # tap a wardrobe door to open, tap again to close
        await pg.evaluate("viewer.goRoom('Room 1', 2)"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(800)
        async def tap_obj(name):
            xy = await pg.evaluate("""(n) => { const o = viewer.scene.getObjectByName(n); const c = new app.bbox.constructor().setFromObject(o).getCenter(new app.center.constructor());
                c.project(viewer.camera); const r = viewer.renderer.domElement.getBoundingClientRect(); return [r.left + (c.x+1)/2*r.width, r.top + (1-c.y)/2*r.height]; }""", name)
            await touch(cdp, "touchStart", [xy]); await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(400)
            await pg.wait_for_function("(() => { const g = viewer.imm.groups.get('WARDROBE_DOOR_2'); return g.t === (g.open ? 1 : 0); })()")
            return xy
        await tap_obj("R1_DEF_WARDROBE_DOOR_2"); t1 = await pg.evaluate("viewer.imm.groups.get('WARDROBE_DOOR_2').open")
        await tap_obj("R1_DEF_WARDROBE_DOOR_2"); t2 = await pg.evaluate("viewer.imm.groups.get('WARDROBE_DOOR_2').open")
        check("phone: tap opens a wardrobe door and a second tap closes it", t1 is True and t2 is False, f"{t1} -> {t2}")
        await pg.screenshot(path=f"{OUT}/02_phone_wardrobe.png")
        # overview: pinch zoom with two fingers
        await pg.evaluate("viewer.overview()"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(500)
        d0 = await pg.evaluate("viewer.camera.position.distanceTo(viewer.controls.target)")
        await touch(cdp, "touchStart", [(150, 420), (240, 420)])
        for i in range(10): await touch(cdp, "touchMove", [(150 - 8 * i, 420), (240 + 8 * i, 420)]); await pg.wait_for_timeout(60)
        await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(1200)
        d1 = await pg.evaluate("viewer.camera.position.distanceTo(viewer.controls.target)")
        check("phone: pinch zooms the overview", d1 < d0 * 0.85, f"{d0:.1f} -> {d1:.1f} m")
        # tap an object -> info card
        await pg.evaluate("viewer.presetView('top')"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(600)
        xy = await pg.evaluate("""() => { const b = viewer.renderer.domElement.getBoundingClientRect(); const R = new (viewer.walk.ray.constructor)();
            for (let fy = 0.35; fy < 0.7; fy += 0.05) for (let fx = 0.3; fx < 0.75; fx += 0.05) {       // find a visible floor spot
              R.setFromCamera({ x: fx * 2 - 1, y: -(fy * 2 - 1) }, viewer.camera);
              const h = R.intersectObjects(app.meshes.filter(m => { for (let p = m; p; p = p.parent) if (!p.visible) return false; return true; }), false)[0];
              if (h && /^FLOOR_/.test(h.object.name)) return [b.left + fx * b.width, b.top + fy * b.height]; }
            return [b.left + b.width / 2, b.top + b.height / 2]; }""")
        await touch(cdp, "touchStart", [xy]); await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(900)
        card = await pg.evaluate("() => ({ on: !document.getElementById('tapInfo').classList.contains('hidden'), t: document.getElementById('tapInfo').innerText.slice(0, 120) })")
        check("phone: tapping something shows an info card", card["on"], card["t"].replace("\n", " | "))
        await pg.screenshot(path=f"{OUT}/03_phone_tapinfo.png")
        # double-tap the floor -> inside
        await pg.evaluate("window._tl=[]; ['pointerdown','pointerup','dblclick'].forEach(t => viewer.renderer.domElement.addEventListener(t, e => _tl.push([t, Math.round(performance.now())]), true))")
        # (the headless renderer is too slow for real-time taps, so the two taps are sent as instant pointer events)
        await pg.evaluate("""(p) => { const el = viewer.renderer.domElement; const ev = (t, id) => el.dispatchEvent(new PointerEvent(t, { pointerId: id, pointerType: 'touch', clientX: p[0], clientY: p[1], bubbles: true, isPrimary: true }));
            ev('pointerdown', 71); ev('pointerup', 71); ev('pointerdown', 72); ev('pointerup', 72); }""", xy)
        await pg.wait_for_timeout(800); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(500)
        inside = await pg.evaluate("viewer.walk.active")
        if not inside: print("   events:", await pg.evaluate("_tl"), xy)
        check("phone: double-tap a floor to go inside", inside)
        # slide-over panel
        await pg.evaluate("viewer.overview()"); await pg.wait_for_function("!app.tween")
        await pg.tap("#leftTab"); await pg.wait_for_timeout(400)
        lp = await pg.evaluate("() => ({ d: getComputedStyle(document.getElementById('left')).display, pos: getComputedStyle(document.getElementById('left')).position })")
        await pg.screenshot(path=f"{OUT}/04_phone_left_panel.png")
        await pg.tap("#designPanel button[data-file='MyFlat_V1_1_Room1_OPTION_D.glb']")
        await pg.wait_for_function("app.ready && app.modelFile.endsWith('OPTION_D.glb')")
        await touch(cdp, "touchStart", [(375, 500)]); await touch(cdp, "touchEnd", []); await pg.wait_for_timeout(400)
        lc = await pg.evaluate("getComputedStyle(document.getElementById('left')).display")
        check("phone: left panel slides over, lets you switch designs, and closes when you tap the view", lp["d"] == "block" and lp["pos"] == "fixed" and lc == "none", f"{lp} then {lc}")
        await pg.tap("#learnBtn"); await pg.wait_for_timeout(600)
        lw = await pg.evaluate("document.getElementById('learn').getBoundingClientRect().width")
        check("phone: Learn guide fills the screen width", lw >= 380, f"{lw:.0f}px")
        await pg.screenshot(path=f"{OUT}/05_phone_learn.png")
        errs = [e for e in errs if "setPointerCapture" not in e]    # from the synthetic test taps only
        check("phone: no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
