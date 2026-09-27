"""Automated smoke test for the viewer (headless Chromium + WebGL).
Usage:  python3 scripts/test_viewer.py [base_url] [out_dir]
"""
import sys, os, json, asyncio
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/?lowq=1"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots"
os.makedirs(OUT, exist_ok=True)
results = []
def check(name, ok, info=""):
    results.append((name, bool(ok), info)); print(("PASS " if ok else "FAIL ") + name, info)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": 1600, "height": 950}); pg.set_default_timeout(90000)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
        await pg.goto(BASE)
        await pg.wait_for_function("window.app && window.app.ready === true", timeout=60000)
        await pg.wait_for_timeout(800)
        info = await pg.evaluate("""() => ({n: app.objects.length, rooms: app.rooms.map(r=>r.name), cats:[...app.byCat.keys()],
            missing: (app.missing||[]).length, manifest: app.manifest && app.manifest.object_count, status: document.getElementById('statusbar').textContent})""")
        check("1 model loads", info["n"] > 100, f'{info["n"]} named objects')
        check("19 no exported objects missing", info["missing"] == 0 and info["manifest"], f'manifest {info["manifest"]}')
        check("rooms found", len(info["rooms"]) == 10, ", ".join(info["rooms"]))
        await pg.screenshot(path=f"{OUT}/01_iso.png")

        # orientation: north wall must be at -Z, east (Room 2) at +X
        o = await pg.evaluate("""() => { const T=window.viewer; const s=T.scene; const g=(n)=>{const o=s.getObjectByName(n); const b=new (o.geometry?o.geometry.boundingBox.constructor:Object)(); return null};
            const c=(n)=>{const o=s.getObjectByName(n); const THREEBox=app.bbox.constructor; const b=new THREEBox().setFromObject(o); const v=b.getCenter(b.min.clone()); return [v.x,v.y,v.z]};
            return {n:c('WALL_EXT_N_R1'), s:c('WALL_EXT_S_HALL'), r1:c('FLOOR_R1'), r2:c('FLOOR_R2'), bal:c('BALCONY_FLOOR'), p1:c('PILLAR_1'), p2:c('PILLAR_2')} }""")
        check("2 orientation N=-Z", o["n"][2] < o["s"][2], f'north wall z={o["n"][2]:.2f}, south wall z={o["s"][2]:.2f}')
        check("2 orientation E=+X", o["r2"][0] > o["r1"][0] and o["bal"][0] < o["r1"][0], "Room2 east of Room1, balcony west")
        check("Pillar 2 north of Pillar 1", o["p2"][2] < o["p1"][2])

        async def shot(name, js, wait=1300):
            await pg.evaluate(js); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"{OUT}/{name}.png")
        await shot("02_top", "viewer.presetView('top')")
        cam = await pg.evaluate("() => { const c=viewer.camera; return {ortho: c.isOrthographicCamera, y: c.position.y, t: viewer.controls.target.y} }")
        check("3 top view is orthographic from above", cam["ortho"] and cam["y"] > cam["t"] + 5)
        for v in ["north", "south", "east", "west"]:
            await shot(f"03_{v}", f"viewer.presetView('{v}')")
        check("4 N/S/E/W views run", True)
        # orbit / pan / zoom with the real mouse
        await pg.evaluate("viewer.presetView('iso')"); await pg.wait_for_timeout(1100)
        before = await pg.evaluate("() => viewer.camera.position.toArray()")
        cx, cy = 210 + (1600-210-290)//2, 46 + 400
        await pg.mouse.move(cx, cy); await pg.mouse.down(); await pg.mouse.move(cx+180, cy+40, steps=8); await pg.mouse.up(); await pg.wait_for_timeout(600)
        after = await pg.evaluate("() => viewer.camera.position.toArray()")
        check("5 orbit (left drag) moves camera", sum(abs(a-b) for a, b in zip(before, after)) > 0.5)
        t0 = await pg.evaluate("() => viewer.controls.target.toArray()")
        await pg.mouse.move(cx, cy); await pg.mouse.down(button="right"); await pg.mouse.move(cx+120, cy+60, steps=8); await pg.mouse.up(button="right"); await pg.wait_for_timeout(600)
        t1 = await pg.evaluate("() => viewer.controls.target.toArray()")
        check("6 pan (right drag) moves target", sum(abs(a-b) for a, b in zip(t0, t1)) > 0.2)
        d0 = await pg.evaluate("() => viewer.camera.position.distanceTo(viewer.controls.target)")
        await pg.mouse.move(cx, cy); await pg.mouse.wheel(0, -800); await pg.wait_for_timeout(700)
        d1 = await pg.evaluate("() => viewer.camera.position.distanceTo(viewer.controls.target)")
        check("7 zoom (wheel) changes distance", d1 < d0 - 0.3, f"{d0:.1f} -> {d1:.1f} m")

        # rooms
        for rn, fname in [("Hall", "05_hall"), ("Room 1", "06_room1"), ("Room 2", "07_room2"), ("Open Square", "08_stair_opensq")]:
            idx = 0
            if rn == "Open Square":
                idx = await pg.evaluate("() => app.rooms.find(r=>r.name==='Open Square').vps.findIndex(v=>v.name.includes('SE'))")
                idx = max(0, idx)
            await shot(fname, f"viewer.goRoom('{rn}', {idx})", 1400)
        eye = await pg.evaluate("() => viewer.camera.position.y")
        check("8 room navigation at eye level", 1.3 < eye < 1.9, f"camera y={eye:.2f} m")
        vps = await pg.evaluate("() => app.rooms.map(r => r.name + ':' + r.vps.map(v=>v.name).join('|'))")
        print("   viewpoints:", vps)

        # walkthrough
        await pg.evaluate("viewer.goRoom('Hall', 0)"); await pg.wait_for_function("!app.tween")
        await pg.evaluate("viewer.startWalk()")
        await pg.keyboard.down("KeyW"); await pg.wait_for_timeout(200)
        keyok = await pg.evaluate("() => viewer.walk.keys.has('KeyW')"); await pg.keyboard.up("KeyW")
        # movement is simulated with fixed time steps so the result does not depend on the (software) frame rate
        sim = await pg.evaluate("""() => { const W = viewer.walk, V = app.center.constructor, out = {};
            const run = (yaw, secs) => { W.yaw = yaw; W.keys.clear(); W.keys.add('KeyW'); for (let i=0;i<secs/0.05;i++) W.update(0.05); W.keys.clear(); };
            const p0 = W.cam.position.clone(); run(W.yaw, 1.5); out.walked = W.cam.position.distanceTo(p0);
            run(Math.PI/2, 20); out.x = W.cam.position.x;
            const o = viewer.scene.getObjectByName('WALL_EXT_W_HALL'); out.wall = new app.bbox.constructor().setFromObject(o).max.x;
            const st = app.rooms.find(r=>r.name==='Stair'); const b = st.box; const xe=(b.min.x+b.max.x)/2+(b.max.x-b.min.x)*0.25, xw=(b.min.x+b.max.x)/2-(b.max.x-b.min.x)*0.25;
            W.exit(); W.enter(new V(xe, 1.6, b.min.z+0.35), new V(xe, 1.6, b.max.z)); out.f0 = W.feet;
            run(Math.PI, 6); out.landing = W.feet; W.cam.position.x = xw; W.update(0.05); run(0, 7); out.top = W.feet; out.info = document.getElementById('walkInfo').textContent;
            return out; }""")
        check("9 walkthrough: keys register + W moves", keyok and sim["walked"] > 1.5, f'{sim["walked"]:.2f} m in 1.5 s')
        check("9 collision: stays inside hall west wall", sim["x"] > sim["wall"], f'cam x={sim["x"]:.2f}, wall inner x={sim["wall"]:.2f}')
        check("walkthrough climbs stair to landing and roof level", sim["landing"] > 1.4 and sim["top"] > 3.0, f'feet {sim["f0"]:.2f} -> landing {sim["landing"]:.2f} -> top {sim["top"]:.2f} m')
        await pg.screenshot(path=f"{OUT}/09_walk.png")
        await pg.evaluate("viewer.walk.exit()")
        check("9 exit walkthrough", not await pg.evaluate("() => viewer.walk.active"))

        # roof, visibility
        await pg.evaluate("viewer.presetView('iso')"); await pg.wait_for_timeout(1000)
        await pg.evaluate("viewer.setCat('roof', true)"); await pg.click("#roofBtn"); await pg.wait_for_timeout(300)
        rv = await pg.evaluate("() => viewer.scene.getObjectByName('SLAB_ROOF').visible")
        check("10 roof OFF hides SLAB_ROOF", rv is False)
        await pg.screenshot(path=f"{OUT}/11_roof_off.png")
        await pg.click("#hideAllBtn"); hid = await pg.evaluate("() => app.objects.filter(o=>o.cat!=='plan_reference' && (!o.obj.parent||!o.obj.parent.userData.category)).every(o=>!o.obj.visible)")
        await pg.click("#showAllBtn"); shown = await pg.evaluate("() => app.objects.filter(o=>o.cat!=='plan_reference').every(o=>o.obj.visible)")
        await pg.click('#catToggles .chip[data-cat="walls"]'); wv = await pg.evaluate("() => viewer.scene.getObjectByName('WALL_INT_R2_W').visible")
        await pg.screenshot(path=f"{OUT}/12_no_walls.png")
        await pg.click("#resetVisBtn")
        check("11 visibility toggles / show all / hide all", hid and shown and wv is False)
        # section
        await pg.evaluate("viewer.setSection(true, 1.2)"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"{OUT}/13_section.png")
        await pg.evaluate("viewer.setSection(false)")
        # labels
        n_lbl = await pg.evaluate("() => document.querySelectorAll('.lbl-room').length")
        await pg.click("#labelsBtn"); await pg.wait_for_timeout(3000); off = await pg.evaluate("() => [...document.querySelectorAll('.lbl-room')].every(e=>e.style.display==='none')")
        await pg.click("#labelsBtn")
        check("12 labels show/hide", n_lbl == 10 and off, f"{n_lbl} room labels")
        # status
        await pg.click("#statusBtn"); await pg.wait_for_timeout(300)
        st = await pg.evaluate("() => ({mat: viewer.scene.getObjectByName('PILLAR_1').material.color.getHexString(), legend: document.getElementById('legend').innerText})")
        check("13 status mode colours by Blender status", st["mat"] == "f26b0f", st["legend"].replace("\n", " | "))
        await pg.evaluate("viewer.presetView('top')"); await pg.wait_for_timeout(1300); await pg.screenshot(path=f"{OUT}/14_status_top.png")
        await pg.click("#statusBtn")
        # selection: project PILLAR_2 to screen and click it
        await pg.evaluate("viewer.goRoom('Hall', 0)"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(300)
        xy = await pg.evaluate("""() => { const o=viewer.scene.getObjectByName('PILLAR_2'); const b=new app.bbox.constructor().setFromObject(o); const c=b.getCenter(b.min.clone()); c.y=1.2;
            c.project(viewer.camera); const r=viewer.renderer.domElement.getBoundingClientRect(); return [r.left+(c.x+1)/2*r.width, r.top+(1-c.y)/2*r.height] }""")
        await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(300)
        ins = await pg.evaluate("() => document.getElementById('inspector').innerText")
        check("14/15 click selects + inspector shows metadata", "PILLAR_2" in ins and "PROVISIONAL" in ins, ins.replace("\n", " | ")[:260])
        await pg.screenshot(path=f"{OUT}/15_selected.png")
        # door assembly inspector
        await pg.evaluate("() => viewer.select(viewer.scene.getObjectByName('DOOR_B1_LEAF'))")
        ins2 = await pg.evaluate("() => document.getElementById('inspector').innerText")
        print("   door:", ins2.replace("\n", " | ")[:300])
        # plan compare
        await pg.click("#planBtn"); await pg.wait_for_timeout(1500)
        pv = await pg.evaluate("() => ({vis: app.planObj.visible, ortho: viewer.camera.isOrthographicCamera, roof: viewer.scene.getObjectByName('SLAB_ROOF').visible})")
        await pg.screenshot(path=f"{OUT}/16_plan_compare.png")
        await pg.evaluate("() => { document.getElementById('planOpacity').value = 0.9; document.getElementById('planOpacity').dispatchEvent(new Event('input')); }")
        await pg.wait_for_timeout(200); await pg.screenshot(path=f"{OUT}/17_plan_compare_90.png")
        check("16 plan compare: plan shown, top ortho, roof off", pv["vis"] and pv["ortho"] and not pv["roof"])
        # alignment: plan overlay centre vs model centre in XZ
        al = await pg.evaluate("""() => { const B=app.bbox.constructor; const pb=new B().setFromObject(app.planObj); return {plan:[pb.min.x,pb.max.x,pb.min.z,pb.max.z], model:[app.bbox.min.x,app.bbox.max.x,app.bbox.min.z,app.bbox.max.z]} }""")
        print("   plan extents", [round(v, 2) for v in al["plan"]], "model extents", [round(v, 2) for v in al["model"]])
        check("17 plan overlay covers model footprint", al["plan"][0] < al["model"][0] and al["plan"][1] > al["model"][1] and al["plan"][2] < al["model"][2] and al["plan"][3] > al["model"][3])
        await pg.click("#planBtn")
        # debug
        await pg.click("#debugBtn"); await pg.evaluate("viewer.presetView('top')"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(3500)
        nd = await pg.evaluate("() => document.querySelectorAll('.lbl-debug').length")
        await pg.screenshot(path=f"{OUT}/18_debug.png")
        await pg.click("#debugBtn")
        check("debug labels + object list", nd > 50, f"{nd} debug labels")
        # swap model via URL param (same file, proves the mechanism)
        await pg.goto(BASE.split("?")[0] + "?lowq=1&model=MyFlat_V1_Architecture.glb")
        await pg.wait_for_function("window.app && window.app.ready === true", timeout=60000)
        check("18 model can be chosen by ?model= / models.json", await pg.evaluate("() => app.modelFile") == "MyFlat_V1_Architecture.glb")
        check("no JS errors", not errors, "; ".join(errors[:3]))
        await b.close()
    with open(f"{OUT}/results.json", "w") as f: json.dump(results, f, indent=1)
    print(f"\n{sum(r[1] for r in results)}/{len(results)} checks passed")

asyncio.run(main())
