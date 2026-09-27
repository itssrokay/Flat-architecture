"""Interior-design checks: default load, option switching, camera kept, compare split, inspector specs.
Usage: python3 scripts/test_interiors.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/?lowq=1"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_interiors"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1600, "height": 950}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(BASE); await pg.wait_for_function("window.app && app.ready")
        st = await pg.evaluate("() => ({file: app.modelFile, cur: document.querySelector('#designPanel button.cur')?.dataset.file, notes: document.getElementById('designNotes').innerText.slice(0,80), y: viewer.camera.position.y, cats: [...app.byCat.keys()]})")
        check("opens directly in DEFAULT interior", st["file"] == "MyFlat_V1_1_Room1_DEFAULT.glb" and st["cur"] == st["file"], st["notes"])
        check("starts at eye level in Room 1", 1.3 < st["y"] < 1.9, f'y={st["y"]:.2f}')
        check("design categories present", all(c in st["cats"] for c in ["furniture", "wardrobe", "fenestration", "lighting", "ceiling"]), ",".join(st["cats"]))
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f"{OUT}/01_default_start.png")
        cam0 = await pg.evaluate("() => viewer.camera.position.toArray()")
        for key, f in [("A", "OPTION_A"), ("B", "OPTION_B"), ("C", "OPTION_C"), ("D", "OPTION_D"), ("DEF", "DEFAULT")]:
            await pg.click(f'#designPanel button[data-file="MyFlat_V1_1_Room1_{f}.glb"]')
            await pg.wait_for_function(f"app.ready && app.modelFile === 'MyFlat_V1_1_Room1_{f}.glb' && !document.getElementById('loading').checkVisibility()")
            await pg.wait_for_timeout(2500); await pg.screenshot(path=f"{OUT}/02_{f}_eye.png")
            n = await pg.evaluate("() => app.objects.filter(o => o.obj.userData.design_option).length")
            cam = await pg.evaluate("() => viewer.camera.position.toArray()")
            check(f"switch to {f}: loads, keeps camera", n > 40 and max(abs(a - b_) for a, b_ in zip(cam, cam0)) < 1e-3, f"{n} design objects")
        # Option D shows its budget with a total inside the Rs 1.5-2 lakh target
        await pg.click('#designPanel button[data-file="MyFlat_V1_1_Room1_OPTION_D.glb"]')
        await pg.wait_for_function("app.ready && app.modelFile === 'MyFlat_V1_1_Room1_OPTION_D.glb'")
        bud = await pg.evaluate("""() => { const n = app.designNotes.OPTION_D.budget; const sum = n.rows.reduce((s, r) => s + +r[2].replace(/[^0-9]/g, ''), 0);
            return { total: n.total, sum, shown: !!document.querySelector('#designNotes .budget tr.tot') }; }""")
        check("Option D: budget table shown, rows add up to the total, total within Rs 1.5-2 lakh",
              bud["shown"] and int(bud["total"].replace("₹", "").replace(",", "")) == bud["sum"] and 150000 <= bud["sum"] <= 200000, str(bud))
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f"{OUT}/02b_OPTION_D_budget.png")
        await pg.click('#designPanel button[data-file="MyFlat_V1_1_Room1_DEFAULT.glb"]')
        await pg.wait_for_function("app.ready && app.modelFile === 'MyFlat_V1_1_Room1_DEFAULT.glb'")
        # W1 placeholder replaced; architecture baseline has no design objects
        rep = await pg.evaluate("() => !viewer.scene.getObjectByName('WINDOW_W1_FRAME') && !!viewer.scene.getObjectByName('R1_DEF_W1_OUTER_FRAME')")
        check("generic W1 replaced by designed window", rep)
        # inspector on a design object
        await pg.evaluate("() => viewer.select(viewer.scene.getObjectByName('R1_DEF_BALCONY_DOOR_P2_FRAME'))")
        ins = await pg.evaluate("() => document.getElementById('inspector').innerText")
        check("inspector shows design spec", "Specification" in ins and "DESIGN" in ins.upper(), ins.replace("\n", " | ")[:200])
        # top cutaway of each option via roof off
        await pg.evaluate("viewer.setCat('roof', false); viewer.setCat('ceiling', false); viewer.goRoom('Room 1', 0)"); 
        await pg.evaluate("() => { const r = app.rooms.find(r=>r.name==='Room 1'); const vp = r.vps.find(v=>v.name.startsWith('From above')); viewer.camera.position.copy(vp.pos); viewer.controls.target.copy(vp.target); app.tween=null; }")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f"{OUT}/03_default_above.png")
        # compare split: DEFAULT vs V1 baseline, then DEFAULT vs C
        await pg.select_option("#compareSelect", "MyFlat_V1_Architecture.glb")
        await pg.wait_for_function("app.compare && app.compare.file === 'MyFlat_V1_Architecture.glb'")
        await pg.wait_for_timeout(3000); await pg.screenshot(path=f"{OUT}/04_compare_default_vs_v1.png")
        await pg.select_option("#compareSelect", "MyFlat_V1_1_Room1_OPTION_C.glb")
        await pg.wait_for_function("app.compare && app.compare.file.endsWith('OPTION_C.glb')")
        await pg.evaluate("viewer.setCat('roof', true); viewer.setCat('ceiling', true); viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween")
        await pg.wait_for_timeout(3000); await pg.screenshot(path=f"{OUT}/05_compare_default_vs_C_eye.png")
        cap = await pg.evaluate("() => document.getElementById('compareCaption').innerText")
        check("side-by-side compare works", "DEFAULT" in cap and "Option C" in cap, cap.replace("\n", " vs "))
        await pg.select_option("#compareSelect", ""); await pg.wait_for_function("!app.compare")
        check("compare off", True)
        await pg.evaluate("viewer.goRoom('Room 1', 3)"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(2500); await pg.screenshot(path=f"{OUT}/06_default_balcony.png")
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
