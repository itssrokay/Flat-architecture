"""💬 Ask chat: UI, knowledge + state sent, markdown, Apply action, Hindi, easy mode.
Needs a chat backend: run scripts/serve.py with OPENAI_API_KEY (and optionally OPENAI_BASE_URL pointing to a mock).
Usage: python3 scripts/test_chat.py [base_url] [out_dir]"""
import sys, os, asyncio, json
from playwright.async_api import async_playwright
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8766/").split("?")[0]
OUT = sys.argv[2] if len(sys.argv) > 2 else "test_shots_chat"; os.makedirs(OUT, exist_ok=True)
res = []
def check(n, ok, info=""): res.append((n, bool(ok), info)); print(("PASS " if ok else "FAIL ") + n, info)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1400, "height": 900}); pg.set_default_timeout(150000)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(BASE + "?lowq=1&model=MyFlat_V1_1_Room1_OPTION_E.glb"); await pg.wait_for_function("window.app && app.ready && !app.tween")
        await pg.evaluate("localStorage.removeItem('myflat.edit.OPTION_E'); sessionStorage.removeItem('myflat.chat')"); await pg.reload(); await pg.wait_for_function("window.app && app.ready && !app.tween")
        await pg.click("#chatBtn"); await pg.wait_for_timeout(300)
        n = await pg.evaluate("document.querySelectorAll('#chat .c-chip').length")
        check("💬 Ask opens with suggestion chips", n >= 3, f"{n} chips")
        k = await pg.evaluate("viewer.chat.knowledge().then(k => ({ len: k.length, e: k.includes('OPTION_E'), d: k.includes('DICTIONARY'), f: k.includes('FIXED FACTS'), rooms: k.includes('ROOM FLOOR SIZES') }))")
        check("knowledge pack has all designs, facts, room sizes and the dictionary", k["e"] and k["d"] and k["f"] and k["rooms"] and k["len"] > 30000, str(k))
        await pg.fill("#chatIn", "Should I make the wardrobe hinged?"); await pg.press("#chatIn", "Enter")
        await pg.wait_for_function("viewer.chat.messages().some(m => m.role === 'assistant')", timeout=30000)
        sent = json.load(open('/tmp/claude-0/last_openai.json'))
        st = sent["messages"][1]["content"]
        check("state sent: design, live budget, customise choices", "OPTION_E" in st and "budgetTotal" in st and '"wardrobe": "sliding"' in st.replace('":"', '": "'), st[:200])
        html = await pg.evaluate("document.querySelector('#chat .c-msg.a').innerHTML")
        check("reply rendered with bold, bullets and a table; ACTION line hidden", "<b>Mock</b>" in html and "<li>" in html and "<table>" in html and "ACTION" not in html, html[:160])
        await pg.screenshot(path=f"{OUT}/01_chat.png")
        await pg.click("#chat .c-apply"); await pg.wait_for_timeout(500)
        s = await pg.evaluate("viewer.edit.state()"); v = await pg.evaluate("(() => { const o = viewer.scene.getObjectByName('R1_OPE_WARDROBE_DOOR_1'); for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; })()")
        check("'Apply' button changes the Customise choice and the 3D", s["wardrobe"] == "hinged" and v, str(s["wardrobe"]))
        # 'W' typed in the box must not walk
        p0 = await pg.evaluate("viewer.camera.position.toArray()")
        await pg.click("#chatIn"); await pg.keyboard.type("wwww"); await pg.wait_for_timeout(800)
        p1 = await pg.evaluate("viewer.camera.position.toArray()")
        check("typing in the chat box doesn't move the camera", p0 == p1)
        # select an object -> suggestion about it; state carries it
        await pg.evaluate("viewer.select(viewer.scene.getObjectByName('R1_OPE_CEILING_FAN_MOTOR'))"); await pg.fill("#chatIn", ""); await pg.click("#chat [data-clear]")
        chip = await pg.evaluate("document.querySelector('#chat .c-chip').textContent")
        check("selected object gets its own suggested question", "ceiling fan motor" in chip, chip)
        # Hindi
        await pg.click("#langBtn"); await pg.wait_for_timeout(1500)
        t = await pg.evaluate("[document.getElementById('chatBtn').textContent, document.querySelector('#chat .c-head b').textContent]")
        check("Hindi labels", "पूछें" in t[0] and "फ़्लैट" in t[1], str(t))
        await pg.click("#langBtn"); await pg.wait_for_timeout(800)
        check("no JS errors", not errs, "; ".join(errs[:3]))
        # phone easy mode: button visible
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg2 = await ctx.new_page(); pg2.set_default_timeout(150000)
        await pg2.goto(BASE + "?touch=1"); await pg2.wait_for_function("window.app && app.ready")
        vis = await pg2.evaluate("getComputedStyle(document.getElementById('chatBtn')).display !== 'none'")
        await pg2.click("#simpleHelp .h-ok"); await pg2.click("#chatBtn"); await pg2.wait_for_timeout(400)
        await pg2.screenshot(path=f"{OUT}/02_phone.png")
        check("phone easy mode keeps the 💬 Ask button; chat opens as a bottom sheet", vis and await pg2.evaluate("!document.getElementById('chat').classList.contains('hidden')"))
        await b.close()
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1); print(f"\n{sum(r[1] for r in res)}/{len(res)} checks passed")
asyncio.run(main())
