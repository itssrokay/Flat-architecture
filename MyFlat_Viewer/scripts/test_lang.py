"""Hindi / English switch + phone top bar checks.
Usage: python3 scripts/test_lang.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/").split("?")[0]
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_lang"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1500, "height": 950}); pg.set_default_timeout(120000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(BASE + "?lowq=1&model=MyFlat_V1_1_Room1_OPTION_D.glb"); await pg.wait_for_function("window.app && app.ready && viewer.learn")
        await pg.evaluate("localStorage.removeItem('myflat.lang')")
        await pg.click("#langBtn"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""() => ({ lights: document.getElementById('lightsBtn').textContent, room: document.querySelector('#roomList .go').textContent,
            notes: document.getElementById('designNotes').innerText, info: document.getElementById('walkInfo').textContent, lang: document.documentElement.lang })""")
        check("Hindi: buttons, rooms, walk info and design notes switch to Hindi", r["lights"] == "लाइट चालू" and r["room"] == "कमरा 1" and "स्मार्ट बजट" in r["notes"] and "आँखें" in r["info"] and r["lang"] == "hi", str({k: v[:40] for k, v in r.items()}))
        await pg.click("#learnBtn"); await pg.wait_for_timeout(800)
        t = await pg.evaluate("document.querySelector('#learn .ltabs').innerText")
        check("Hindi: the Learn guide is in Hindi", "शब्दकोश" in t and "आपका कमरा" in t, t.replace("\n", " | "))
        await pg.click("#learn .ltabs button[data-t=floorpaint]"); await pg.wait_for_timeout(400)
        fp = await pg.evaluate("document.getElementById('learnBody').innerText")
        check("Floor & paint page: vitrified vs marble, paint grades with prices", "विट्रिफ़ाइड" in fp and "मार्बल" in fp and "₹212" in fp and "₹764" in fp, fp[:120].replace("\n", " "))
        await pg.screenshot(path=f"{OUT}/01_hindi_floor_paint.png")
        await pg.click("#learn .ltabs button[data-t=dict]"); await pg.fill("#dictSearch", "टेराकोटा"); await pg.wait_for_timeout(300)
        links = await pg.evaluate("[...document.querySelectorAll('#learn .dterm a')].map(a => a.href)")
        check("Dictionary: terracotta has 'see pictures' and 'read more' links", any("google.com/search" in l for l in links) and any("wikipedia" in l for l in links), str(links[:3]))
        await pg.click("#langBtn"); await pg.wait_for_timeout(1500)
        r2 = await pg.evaluate("""() => ({ lights: document.getElementById('lightsBtn').textContent, room: document.querySelector('#roomList .go').textContent, tabs: document.querySelector('#learn .ltabs').innerText, notes: document.getElementById('designNotes').innerText.slice(0, 30) })""")
        check("English again: everything switches back exactly", r2["lights"] == "Lights ON" and r2["room"] == "Room 1" and "Dictionary" in r2["tabs"] and r2["notes"].startswith("Option D"), str(r2))
        check("desktop: no JS errors", not errs, "; ".join(errs[:3]))
        await pg.close()
        # phone top bar
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.set_default_timeout(120000)
        await pg.goto(BASE + "?touch=1&easy=0"); await pg.wait_for_function("window.app && app.ready")
        vis = await pg.evaluate("""() => [...document.querySelectorAll('#topbar > *')].filter(e => getComputedStyle(e).display !== 'none').map(e => e.id || e.className || e.tagName)""")
        hidden = await pg.evaluate("""() => ['viewButtons','projBtn','roofBtn','labelsBtn','edgesBtn','statusBtn','planBtn','debugBtn'].every(id => getComputedStyle(document.getElementById(id)).display === 'none')""")
        check("phone: top bar keeps only the useful buttons", hidden and "learnBtn" in vis and "langBtn" in vis and "walkBtn" in vis, ", ".join(vis))
        await pg.screenshot(path=f"{OUT}/02_phone_topbar.png")
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
