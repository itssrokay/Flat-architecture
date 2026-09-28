"""Option E 'Customise' panel: variants show/hide, budget recomputes, rules, presets, colours, link, Hindi.
Usage: python3 scripts/test_edit.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/").split("?")[0]
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_edit"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
VIS = """(n) => { const o = viewer.scene.getObjectByName('R1_OPE_' + n); if (!o) return null; for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; }"""
TOT = "() => app.editBudget('OPTION_E', app.designNotes.OPTION_E.budget)._sum"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1500, "height": 950}); pg.set_default_timeout(150000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(BASE + "?lowq=1&model=MyFlat_V1_1_Room1_OPTION_E.glb"); await pg.wait_for_function("window.app && app.ready")
        await pg.evaluate("localStorage.removeItem('myflat.edit.OPTION_E')"); await pg.reload(); await pg.wait_for_function("window.app && app.ready && !app.tween")
        vis = lambda n: pg.evaluate(VIS, n)
        st = await pg.evaluate("() => ({ btn: !document.getElementById('editBtn').classList.contains('hidden'), panel: !document.getElementById('editPanel').classList.contains('hidden') })")
        check("E: ✏️ Customise button and panel shown", st["btn"] and st["panel"], str(st))
        d = {n: await vis(n) for n in ["WARDROBE_SLIDER_1", "WARDROBE_SLIDER_1_MIRROR", "WARDROBE_DOOR_1", "PEGBOARD", "MIRROR_CABINET_DOOR", "FULL_LENGTH_MIRROR", "STANDING_DESK_TOP", "FOLD_DESK_TOP", "W1_SASH_1_SASH", "W1TT_L_SASH", "BALCONY_BISTRO_TABLE"]}
        check("recommended: sliding wardrobe + mirror on it + pegboard, standing desk, builder's window; alternatives hidden",
              d["WARDROBE_SLIDER_1"] and d["WARDROBE_SLIDER_1_MIRROR"] and d["PEGBOARD"] and d["STANDING_DESK_TOP"] and d["W1_SASH_1_SASH"] and not any(d[k] for k in ["WARDROBE_DOOR_1", "MIRROR_CABINET_DOOR", "FULL_LENGTH_MIRROR", "FOLD_DESK_TOP", "W1TT_L_SASH", "BALCONY_BISTRO_TABLE"]), str(d))
        t0 = await pg.evaluate(TOT); shown = await pg.evaluate("document.querySelector('#designNotes .budget tr.tot .amt').textContent")
        check("recommended total Rs 1,47,900 and the notes' budget table shows it", t0 == 147900 and shown == "₹1,47,900", f"{t0} / {shown}")
        await pg.screenshot(path=f"{OUT}/01_recommended.png")
        # hinged doors: mirror rule falls back to the cabinet
        await pg.click('#editPanel [data-g=wardrobe][data-o=hinged]'); await pg.wait_for_timeout(400)
        s = await pg.evaluate("viewer.edit.state()")
        d = {n: await vis(n) for n in ["WARDROBE_DOOR_1", "WARDROBE_SLIDER_1", "MIRROR_CABINET_DOOR", "PEGBOARD"]}
        t1 = await pg.evaluate(TOT)
        check("hinged: 3 hinged doors appear, sliders go, mirror moves to the cabinet (rule), budget changes", s["mirror"] == "cabinet" and d["WARDROBE_DOOR_1"] and not d["WARDROBE_SLIDER_1"] and d["MIRROR_CABINET_DOOR"] and not d["PEGBOARD"] and t1 == 147900 - 9000 - 4500 + 6500, f"{s} {d} {t1}")
        n = await pg.evaluate("viewer.imm.groups.has('MIRROR_CABINET_DOOR') && viewer.imm.groups.has('WARDROBE_DOOR_1')")
        check("the mirror cabinet door and hinged doors open (openable parts rebuilt)", n)
        await pg.evaluate("viewer.goRoom('Room 1', 2)"); await pg.wait_for_function("!app.tween && viewer.walk.active"); await pg.wait_for_timeout(300)
        await pg.evaluate("viewer.imm.toggle(viewer.imm.groups.get('MIRROR_CABINET_DOOR'), true); viewer.imm.toggle(viewer.imm.groups.get('WARDROBE_DOOR_1'), true)")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f"{OUT}/02_hinged_cabinet_open.png")
        # picking the mirror-on-slider brings the sliders back
        await pg.click('#editPanel [data-g=mirror][data-o=wardrobe]'); await pg.wait_for_timeout(400)
        s = await pg.evaluate("viewer.edit.state()")
        check("mirror on the slider switches the wardrobe back to sliding (rule)", s["wardrobe"] == "sliding" and s["mirror"] == "wardrobe", str(s))
        # presets
        await pg.click('#editPanel [data-p=budget]'); await pg.wait_for_timeout(400)
        t2 = await pg.evaluate(TOT); loft = await vis("WARDROBE_LOFT")
        check("'Within Rs 1.3 lakh' preset: Rs 1,28,400, loft hidden", t2 == 128400 and loft is False, f"{t2} loft={loft}")
        await pg.click('#editPanel [data-p=tight]'); await pg.wait_for_timeout(400)
        t3 = await pg.evaluate(TOT); fd = await vis("FOLD_DESK_TOP"); sd = await vis("STANDING_DESK_TOP")
        check("'Tightest' preset: Rs 1,13,900 with the fold-down desk", t3 == 113900 and fd and not sd, f"{t3}")
        # budget-only choice + window upgrade
        await pg.click('#editPanel [data-g=walls][data-o=bare]'); await pg.click('#editPanel [data-g=window][data-o=tt]'); await pg.wait_for_timeout(400)
        t4 = await pg.evaluate(TOT); tt = await vis("W1TT_L_SASH")
        rows = await pg.evaluate("[...document.querySelectorAll('#designNotes .budget tr')].map(r => r.cells[0].firstChild.textContent)")
        check("bare walls (+5k) and tilt-and-turn window (+48k): model and budget rows update", t4 == 113900 + 5000 + 48000 and tt and "Window W1" in rows, f"{t4} {rows}")
        # colours
        await pg.click('#editPanel [data-c=c_bedwall][data-o=terracotta]'); await pg.click('#editPanel [data-c=c_wood][data-o=walnut]'); await pg.wait_for_timeout(400)
        col = await pg.evaluate("() => { const o = viewer.scene.getObjectByName('R1_OPE_BED_WALL_PALE_SAGE'); const w = viewer.scene.getObjectByName('R1_OPE_BED_BASE'); return [o.material.color.toArray().map(v => +v.toFixed(2)), w.material.color.toArray().map(v => +v.toFixed(2))]; }")
        check("colours: bed wall -> terracotta, wood -> walnut", col[0] == [0.72, 0.42, 0.3] and col[1] == [0.42, 0.28, 0.18], str(col))
        await pg.evaluate("viewer.overview()"); await pg.wait_for_function("!app.tween"); await pg.wait_for_timeout(1500)
        await pg.evaluate("viewer.goRoom('Room 1', 0)"); await pg.wait_for_function("!app.tween && viewer.walk.active"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f"{OUT}/03_custom_colours.png")
        # link + reload keeps choices
        await pg.click('#editPanel [data-copy]'); await pg.wait_for_timeout(300)
        url = pg.url
        check("copy link puts the choices in the address", "e=" in url and "wardrobe%3Ahinged" in url.replace(":", "%3A"), url)
        pg2 = await b.new_page(viewport={"width": 1200, "height": 800}); pg2.set_default_timeout(150000)
        await pg2.goto(BASE + "?lowq=1&model=MyFlat_V1_1_Room1_OPTION_E.glb&e=desk:fold,c_curtains:navy"); await pg2.wait_for_function("window.app && app.ready")
        s2 = await pg2.evaluate("viewer.edit.state()")
        check("a shared link opens with its choices", s2["desk"] == "fold" and s2["c_curtains"] == "navy", str(s2))
        await pg2.close()
        await pg.reload(); await pg.wait_for_function("window.app && app.ready")
        s3 = await pg.evaluate("viewer.edit.state()")
        check("choices are remembered after reload", s3["wood" if "wood" in s3 else "c_wood"] == "walnut" and s3["window"] == "tt", str(s3))
        # Hindi
        await pg.click("#langBtn"); await pg.wait_for_timeout(2000)
        h = await pg.evaluate("document.querySelector('#editPanel .e-head b').textContent")
        check("Hindi panel", "विकल्प" in h, h)
        await pg.click("#langBtn"); await pg.wait_for_timeout(1000)
        # other designs: no Customise button
        await pg.evaluate("viewer.switchModel('MyFlat_V1_1_Room1_OPTION_D.glb')"); await pg.wait_for_function("app.ready && app.modelFile.endsWith('OPTION_D.glb')")
        hid = await pg.evaluate("document.getElementById('editBtn').classList.contains('hidden') && document.getElementById('editPanel').classList.contains('hidden')")
        check("other designs have no Customise button", hid)
        await pg.evaluate("localStorage.removeItem('myflat.edit.OPTION_E')")
        check("no JS errors", not errs, "; ".join(errs[:3]))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
