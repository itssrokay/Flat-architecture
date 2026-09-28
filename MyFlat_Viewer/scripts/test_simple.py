"""Easy mode (phone, 390x844, touch): the big-button mode meant for first-time users.
Usage: python3 scripts/test_simple.py [base_url] [out_dir]"""
import sys, os, asyncio, json, math
from playwright.async_api import async_playwright
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/").split("?")[0]
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_simple"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.set_default_timeout(150000)
        errs = []; pg.on("pageerror", lambda e: "setPointerCapture" in str(e) or errs.append(str(e)))   # synthetic test pointers only
        await pg.goto(BASE + "?touch=1"); await pg.wait_for_function("window.app && app.ready && viewer.walk.active && !app.tween"); await pg.wait_for_timeout(800)
        st = await pg.evaluate("""() => ({ simple: document.body.classList.contains('simple'), help: !document.getElementById('simpleHelp').classList.contains('hidden'),
            joy: getComputedStyle(document.getElementById('touchPad')).display, pad: !document.getElementById('sPad').classList.contains('hidden'),
            top: [...document.querySelectorAll('#topbar > *')].filter(e => getComputedStyle(e).display !== 'none').map(e => e.id || e.className) })""")
        check("phone opens in easy mode with the help card, big pad, no joystick", st["simple"] and st["help"] and st["pad"] and st["joy"] == "none", str(st))
        check("easy mode top bar: only Learn, Ask, language, design and the mode switch", set(x for x in st["top"] if x != "spacer") <= {"learnBtn", "chatBtn", "langBtn", "modelSelect", "simpleBtn"}, str(st["top"]))
        await pg.screenshot(path=f"{OUT}/01_help.png")
        await pg.click("#simpleHelp .h-ok")
        await pg.screenshot(path=f"{OUT}/02_easy_inside.png")
        box = lambda h: pg.evaluate(f"(() => {{ const r = document.querySelector('#sPad [data-h={h}]').getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; }})()")
        async def hold(h, ms):
            x, y = await box(h); await pg.mouse.move(x, y); await pg.mouse.down(); await pg.wait_for_timeout(ms); await pg.mouse.up(); await pg.wait_for_timeout(300)
        p0 = await pg.evaluate("viewer.camera.position.toArray()")
        await hold("fwd", 4000)
        p1 = await pg.evaluate("viewer.camera.position.toArray()")
        mv = math.hypot(p1[0] - p0[0], p1[2] - p0[2])
        check("holding 'Walk' moves forward, releasing stops", mv > 0.1 and await pg.evaluate("viewer.walk.joy.y === 0"), f"moved {mv:.2f} m")
        y0 = await pg.evaluate("viewer.walk.yaw"); await hold("turnL", 2500); y1 = await pg.evaluate("viewer.walk.yaw")
        await hold("turnR", 2500); y2 = await pg.evaluate("viewer.walk.yaw")
        check("turn left / turn right buttons turn", y1 - y0 > 0.1 and y1 - y2 > 0.1, f"{y0:.2f} -> {y1:.2f} -> {y2:.2f}")
        await hold("up", 4000); pu = await pg.evaluate("viewer.walk.pitch")
        await pg.click("[data-a=level]"); pl = await pg.evaluate("viewer.walk.pitch")
        check("look up, then Straighten levels the view", pu > 0.03 and abs(pl) < 1e-6, f"pitch {pu:.2f} -> {pl:.2f}")
        # tap the floor: walk there by itself
        await pg.evaluate("viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("viewer.walk.active && !app.tween"); await pg.wait_for_timeout(500)
        await pg.evaluate("viewer.walk.pitch = -0.45"); await pg.wait_for_timeout(1500)
        q0 = await pg.evaluate("viewer.camera.position.toArray()")
        await pg.evaluate("""() => { const el = viewer.renderer.domElement, r = el.getBoundingClientRect(); const cam = viewer.camera; cam.updateMatrixWorld();
            const f = new cam.position.constructor(); cam.getWorldDirection(f); f.y = 0; f.normalize();
            const P = cam.position.clone().addScaledVector(f, 1.3); P.y = cam.position.y - 1.55; P.project(cam);
            const x = r.left + (P.x+1)/2*r.width, y = r.top + (1-P.y)/2*r.height;
            const o = { clientX: x, clientY: y, pointerId: 7, pointerType: 'touch', bubbles: true, isPrimary: true };
            el.dispatchEvent(new PointerEvent('pointerdown', o)); el.dispatchEvent(new PointerEvent('pointerup', o)); }""")
        a = await pg.evaluate("viewer.walk.auto && [viewer.walk.auto.x, viewer.walk.auto.z]")
        check("tapping the floor sets a walk-to target", bool(a), str(a))
        if a:
            await pg.wait_for_function("!viewer.walk.auto", timeout=60000)
            q1 = await pg.evaluate("viewer.camera.position.toArray()")
            d = math.hypot(q1[0] - a[0], q1[2] - a[1])
            check("... and walks there by itself", d < 0.45 and math.hypot(q1[0]-q0[0], q1[2]-q0[2]) > 0.3, f"ended {d:.2f} m from target")
        # places -> balcony
        await pg.click("[data-a=places]"); await pg.wait_for_timeout(300)
        items = await pg.evaluate("[...document.querySelectorAll('#placesSheet .p-item')].map(b => b.textContent)")
        check("Places list has Room 1 views, balcony, ceiling, other rooms", len(items) >= 8 and any("Balcony" in t for t in items) and any("ceiling" in t for t in items), " | ".join(items))
        await pg.screenshot(path=f"{OUT}/03_places.png")
        i = next(k for k, t in enumerate(items) if "Balcony" in t)
        await pg.click(f"#placesSheet .p-item[data-i='{i}']"); await pg.wait_for_function("viewer.walk.active && !app.tween"); await pg.wait_for_timeout(400)
        d = await pg.evaluate("(() => { const v = app.rooms.find(r => r.name === 'Room 1').vps.find(v => v.name.startsWith('Balcony')); return viewer.camera.position.distanceTo(v.pos); })()")
        check("Places → Balcony takes you to the balcony", d < 0.3, f"{d:.2f} m from the balcony viewpoint")
        # whole house -> tap a room
        await pg.click("[data-a=house]"); await pg.wait_for_function("!viewer.walk.active && !app.tween && app.ortho"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=f"{OUT}/04_house.png")
        pad_hidden = await pg.evaluate("document.getElementById('sPad').classList.contains('hidden')")
        xy = await pg.evaluate("""() => { const r = app.rooms.find(r => r.name === 'Hall'); const c = r.vps[0].pos.clone(); c.y = 0.05; viewer.camera.updateMatrixWorld(); c.project(viewer.camera);
            const q = viewer.renderer.domElement.getBoundingClientRect(); return [q.left + (c.x+1)/2*q.width, q.top + (1-c.y)/2*q.height]; }""")
        await pg.evaluate("""([x, y]) => { const el = viewer.renderer.domElement; const o = { clientX: x, clientY: y, pointerId: 8, pointerType: 'touch', bubbles: true, isPrimary: true };
            el.dispatchEvent(new PointerEvent('pointerdown', o)); el.dispatchEvent(new PointerEvent('pointerup', o)); }""", xy)
        await pg.wait_for_function("viewer.walk.active && !app.tween", timeout=60000)
        await pg.wait_for_function("document.getElementById('sWhere').textContent.includes('Hall')", timeout=20000) if True else None
        w = await pg.evaluate("document.getElementById('sWhere').textContent")
        check("Whole house: pad hidden, tapping a room takes you inside it", pad_hidden and "Hall" in w, w)
        # Hindi
        await pg.click("#langBtn"); await pg.wait_for_timeout(2500)
        hi = await pg.evaluate("[document.querySelector('#sPad [data-h=fwd]').textContent, document.getElementById('simpleBtn').textContent, document.querySelector('[data-a=places]').textContent]")
        check("Hindi: big buttons are in Hindi", "में" in await pg.evaluate("document.getElementById('sWhere').textContent") and "आगे" in hi[0] and "कंट्रोल" in hi[1] and "जगहें" in hi[2], str(hi))
        await pg.screenshot(path=f"{OUT}/05_hindi.png")
        await pg.click("#langBtn"); await pg.wait_for_timeout(800)
        # all controls
        await pg.click("#simpleBtn"); await pg.wait_for_timeout(500)
        st = await pg.evaluate("""() => ({ simple: document.body.classList.contains('simple'), joy: getComputedStyle(document.getElementById('touchPad')).display, ui: document.getElementById('simpleUI').classList.contains('hidden') })""")
        check("'All controls' brings back the joystick and hides the big buttons", not st["simple"] and st["joy"] != "none" and st["ui"], str(st))
        await pg.reload(); await pg.wait_for_function("window.app && app.ready")
        check("the choice is remembered after reload", not await pg.evaluate("document.body.classList.contains('simple')"))
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
