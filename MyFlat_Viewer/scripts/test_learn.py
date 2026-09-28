"""Learn-guide checks: drawer opens, every design's surface cards resolve to real objects,
'Show me' selects and explains, dictionary search works, hover/inspector say it in simple words.
Usage: python3 scripts/test_learn.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/?lowq=1"
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_learn"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1500, "height": 950}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(BASE); await pg.wait_for_function("window.app && app.ready && viewer.learn")
        await pg.click("#learnBtn"); await pg.wait_for_timeout(800)
        n = await pg.evaluate("document.querySelectorAll('#learn .lcard').length")
        check("Learn opens on 'Your room' with surface cards", n >= 6, f"{n} cards")
        await pg.screenshot(path=f"{OUT}/01_your_room.png")
        for f in ["DEFAULT", "OPTION_A", "OPTION_B", "OPTION_C", "OPTION_D"]:
            await pg.evaluate(f"viewer.switchModel('MyFlat_V1_1_Room1_{f}.glb')"); await pg.wait_for_function(f"app.ready && app.modelFile.endsWith('{f}.glb')")
            miss = await pg.evaluate("""async () => { const g = await fetch('./models/learn_guide.json').then(r => r.json()); const k = '%s';
              return g.designs[k].filter(c => c.show.length && !c.show.some(p => app.objects.some(o => new RegExp(p).test(o.name.replace(/^R1_(DEF|OPA|OPB|OPC|OPD)_/, '')) || new RegExp(p).test(o.name)))).map(c => c.title); }""" % f)
            check(f"{f}: every surface card points at a real object", not miss, str(miss))
        await pg.click("#learn .showme >> nth=0"); await pg.wait_for_timeout(300); await pg.wait_for_function("!app.tween")
        ins = await pg.evaluate("document.getElementById('inspector').innerText")
        check("Show me selects the part and the inspector explains it in simple words", "In simple words" in ins, ins.replace("\n", " | ")[:200])
        await pg.click("#learn .ltabs button[data-t=basics]"); await pg.wait_for_timeout(400)
        await pg.click("#learn .showme2[data-p='WALL_R1_S_RAISED']"); await pg.wait_for_timeout(300); await pg.wait_for_function("!app.tween")
        sel = await pg.evaluate("app.selected && app.selected.name")
        check("Basics: 'Show me the thick wall' finds the raised wall", sel == "WALL_R1_S_RAISED", str(sel))
        await pg.screenshot(path=f"{OUT}/02_basics.png")
        await pg.click("#learn .ltabs button[data-t=dict]"); await pg.fill("#dictSearch", "putty"); await pg.wait_for_timeout(300)
        terms = await pg.evaluate("[...document.querySelectorAll('#learn .dterm b')].map(b => b.textContent)")
        check("Dictionary search finds 'Wall putty'", "Wall putty" in terms, ", ".join(terms))
        await pg.click("#learn .ltabs button[data-t=compare]"); await pg.wait_for_timeout(300)
        cols = await pg.evaluate("document.querySelectorAll('#learn .ctable th').length")
        check("Compare table shows all 5 designs", cols == 6, f"{cols - 1} designs")
        await pg.click("#learn .ltabs button[data-t=steps]"); await pg.wait_for_timeout(300)
        steps = await pg.evaluate("document.querySelectorAll('#learn ol.steps li').length")
        check("Step-by-step order of work", steps >= 10, f"{steps} steps")
        ex = await pg.evaluate("viewer.learn.explain(viewer.scene.getObjectByName('R1_OPD_WARDROBE_CARCASS')).map(t => t.term)")
        check("explain(): wardrobe carcass gets plain-language terms", len(ex) > 0, str(ex))
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
