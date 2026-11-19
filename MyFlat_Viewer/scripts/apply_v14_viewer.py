# V1.4 viewer declutter: short top bar + "More" menu, plans first, folded side panels, controls tucked away.
# Run from the MyFlat folder:  python3 MyFlat_Viewer/scripts/apply_v14_viewer.py
# Safe to re-run (each step checks whether it is already applied).
import json, collections, os, sys
OD = collections.OrderedDict
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")
V = "MyFlat_Viewer/"

def patch(path, pairs):
    s = open(V + path, encoding="utf-8").read()
    for a, b in pairs:
        if b in s: continue                         # already applied
        assert s.count(a) == 1, (path, a[:80], s.count(a))
        s = s.replace(a, b)
    open(V + path, "w", encoding="utf-8").write(s)

# ------------------------------------------------------------ 1. index.html
TOP_OLD_START = '<header id="topbar">'
TOP_OLD_END = '</header>'
NEW_TOP = '''<header id="topbar">
  <div class="brand desk-only">MyFlat</div>
  <select id="modelSelect" title="Choose a plan"></select>
  <button id="walkBtn" class="toggle accent" title="Stand inside at eye level">Walk</button>
  <button id="overviewBtn" title="Step outside and see the whole flat (orbit)">Overview</button>
  <button id="lightsBtn" class="toggle on" title="Light fittings on/off (L)">Lights ON</button>
  <button id="nightBtn" class="toggle" title="Day / night (N)">Day</button>
  <button id="editBtn" class="toggle hidden" title="Change wardrobe, mirror, desk, window, colours: the 3D and budget update">✏️ Customise</button>
  <div class="spacer"></div>
  <button id="simpleBtn" class="simpleToggle" title="Easy mode: big buttons for walking around">👍 Easy mode</button>
  <button id="learnBtn" class="toggle learn" title="Beginner's guide: what everything is made of, how homes are built, dictionary (G)">📘 Learn</button>
  <button id="chatBtn" class="toggle chatb" title="Ask anything about your flat, the designs, materials and budget">💬 Ask</button>
  <button id="langBtn" class="lang" title="हिंदी में देखें">हिंदी</button>
  <button id="moreBtn" class="toggle" aria-expanded="false" title="More views, measuring and tools">More ▾</button>
</header>
<div id="moreMenu" class="hidden">
  <div class="mg"><h5>View</h5>
    <div class="mrow group" id="viewButtons">
      <button data-view="top" title="Plan view (hides the roof)">Top</button>
      <button data-view="north">N</button><button data-view="south">S</button><button data-view="east">E</button><button data-view="west">W</button>
      <button data-view="iso">Iso</button>
    </div>
    <div class="mrow">
      <button id="projBtn" class="toggle" title="Perspective / orthographic">Persp</button>
      <button id="roofBtn" class="toggle on">Roof ON</button>
      <button id="labelsBtn" class="toggle on">Labels</button>
      <button id="edgesBtn" class="toggle on" title="Outline edges">Edges</button>
      <button id="immBtn" class="accent" title="Full-screen immersive mode (F)">⛶ Immersive</button>
    </div>
  </div>
  <div class="mg"><h5>Measure</h5>
    <div class="mrow">
      <button id="roomDimsBtn" class="toggle" title="Wall-by-wall size of the room you are in (M)">Room size</button>
      <button id="dimsBtn" class="toggle" title="Show dimensions of parts; select an object for W/D/H lines">Dimensions</button>
      <button id="hoverBtn" class="toggle" title="Point at anything to see what it is (I)">Hover info</button>
    </div>
  </div>
  <div class="mg"><h5>Tools</h5>
    <div class="mrow">
      <button id="statusBtn" class="toggle">Status</button>
      <button id="planBtn" class="toggle">Plan compare</button>
      <button id="debugBtn" class="toggle">Debug</button>
      <button id="resetBtn" title="Reset camera and visibility">Reset</button>
    </div>
  </div>
</div>'''

LEFT_OLD = '''<aside id="left">
  <h3>Interior design</h3>
  <div id="designPanel"></div>
  <div class="cmp"><span>Compare side by side with</span><select id="compareSelect"></select></div>
  <h3 style="margin-top:14px">Rooms</h3>
  <div id="roomList"></div>
  <div class="hint">Click a room for an eye-level view. Arrows show extra viewpoints.</div>
  <button id="copyViewBtn" class="small">Copy current view</button>
</aside>'''
LEFT_NEW = '''<aside id="left">
  <h3>Plans</h3>
  <div id="designPanel"></div>
  <h3 style="margin-top:14px">Rooms</h3>
  <div id="roomList"></div>
  <details class="tools"><summary>More tools</summary>
    <div class="cmp"><span>Compare side by side with</span><select id="compareSelect"></select></div>
    <button id="copyViewBtn" class="small">Copy current view</button>
  </details>
</aside>'''

p = V + "index.html"; s = open(p, encoding="utf-8").read()
if 'id="moreMenu"' not in s:
    a = s.index(TOP_OLD_START); b = s.index(TOP_OLD_END, a) + len(TOP_OLD_END)
    s = s[:a] + NEW_TOP + s[b:]
if LEFT_OLD in s: s = s.replace(LEFT_OLD, LEFT_NEW)
s = s.replace('<button id="dockToggle" class="small">Hide controls ▾</button>\n  <div id="dock">', '<button id="dockToggle" class="small">Controls ▴</button>\n  <div id="dock" class="collapsed">')
if "declutter.js" not in s:
    s = s.replace('<script type="module" src="./src/main.js?v=19"></script>', '<script type="module" src="./src/main.js?v=19"></script>\n<script type="module" src="./src/declutter.js?v=19"></script>')
s = s.replace("?v=19", "?v=20")
open(p, "w", encoding="utf-8").write(s)

# ------------------------------------------------------------ 2. More menu behaviour
open(V + "src/declutter.js", "w", encoding="utf-8").write('''// V1.4: the "More" menu in the top bar (views, measuring, tools). Buttons keep their ids, so main.js still drives them.
const btn = document.getElementById('moreBtn'), menu = document.getElementById('moreMenu');
function place() {
  const r = btn.getBoundingClientRect();
  menu.style.top = (r.bottom + 6) + 'px';
  menu.style.right = Math.max(8, innerWidth - r.right) + 'px';
}
function set(open) {
  menu.classList.toggle('hidden', !open); btn.classList.toggle('on', open); btn.setAttribute('aria-expanded', String(open));
  if (open) place();
}
btn.addEventListener('click', (e) => { e.stopPropagation(); set(menu.classList.contains('hidden')); });
document.addEventListener('pointerdown', (e) => {
  if (!menu.classList.contains('hidden') && !menu.contains(e.target) && !btn.contains(e.target)) set(false);
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
menu.addEventListener('click', (e) => { if (e.target.closest('#viewButtons button, #resetBtn, #immBtn')) set(false); });
addEventListener('resize', () => { if (!menu.classList.contains('hidden')) place(); });
''')

# ------------------------------------------------------------ 3. styles
css = V + "src/styles.css"; c = open(css, encoding="utf-8").read()
if "#moreMenu" not in c:
    c += '''
/* ---- V1.4 declutter ---- */
#moreMenu { position: fixed; z-index: 60; background: #fff; border: 1px solid var(--line); border-radius: 12px;
  box-shadow: 0 12px 32px rgba(20,20,30,.16); padding: 10px 12px 12px; display: grid; gap: 10px; width: 300px; max-width: calc(100vw - 16px); }
#moreMenu.hidden { display: none; }
#moreMenu h5 { margin: 0 0 5px; font-size: 10.5px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 700; }
#moreMenu .mrow { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
#moreMenu button { padding: 5px 9px; font-size: 12.5px; border-radius: 7px; }
#moreMenu #viewButtons button { min-width: 34px; }
#topbar #moreBtn { font-weight: 600; }
#topbar select#modelSelect { max-width: 340px; font-weight: 600; }
body.immersive #moreMenu { display: none !important; }
#designPanel details.grpd { grid-column: 1 / 3; margin-top: 6px; }
#designPanel details.grpd > summary { cursor: pointer; font-size: 10.5px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; user-select: none; }
#designPanel .grpw { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-top: 4px; }
#designPanel button small { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
#left details.tools { margin-top: 14px; font-size: 12px; }
#left details.tools > summary { cursor: pointer; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 6px; }
#left details.tools .cmp { margin-bottom: 6px; }
#designNotes .verdict { background: #fff; border-left: 3px solid #6d3fa8; border-radius: 6px; padding: 6px 8px; margin: 2px 0 8px; }
'''
    open(css, "w", encoding="utf-8").write(c)

# ------------------------------------------------------------ 4. main.js: plans first, folded groups, short notes
patch("src/main.js", [
 ("const BUILD = '19';", "const BUILD = '20';"),
 ("""  const groups = [['interior', 'Room 1 interior'], ['version', 'Layout versions'], ['architecture', 'Architecture only']];
  for (const [g, title] of groups) {
    const items = list.models.filter(m => (m.group || 'architecture') === g);
    if (!items.length) continue;
    const h = document.createElement('div'); h.className = 'grp'; h.textContent = title; p.appendChild(h);""",
  """  const groups = [['version', 'Flat plans'], ['interior', 'Room 1 interior'], ['architecture', 'Architecture only']];
  const cur = new URLSearchParams(location.search).get('model') || app.modelFile || list.default;
  for (const [g, title] of groups) {
    const items = list.models.filter(m => (m.group || 'architecture') === g);
    if (!items.length) continue;
    let host = p;
    if (g === 'version') { /* shown first, no sub-heading: the panel heading already says Plans */ }
    else {   // less-used groups are folded away until opened
      const d = document.createElement('details'); d.className = 'grpd'; d.open = items.some(m => m.file === cur);
      const sm = document.createElement('summary'); sm.textContent = title; d.appendChild(sm);
      host = document.createElement('div'); host.className = 'grpw'; d.appendChild(host); p.appendChild(d);
    }"""),
 ("""      b.innerHTML = `${m.short || m.label}<small>${g === 'interior' ? sub : (m.label || '')}</small>`;
      b.onclick = () => switchModel(m.file);
      p.appendChild(b);""",
  """      b.innerHTML = `${m.short || m.label}<small>${g === 'interior' ? sub : (note?.budget ? note.budget.total.replace(/\\d[\\d,]*/g, x => (parseInt(x.replace(/,/g, '')) / 1e5).toFixed(2)) + ' L' : '')}</small>`;
      b.title = m.label || m.file;
      b.onclick = () => switchModel(m.file);
      host.appendChild(b);"""),
 ("""  for (const m of list.models) { const o = document.createElement('option'); o.value = m.file; o.textContent = m.label || m.file; o.dataset.manifest = m.manifest || ''; sel.appendChild(o); }""",
  """  const og = {}; const GT = { version: 'Flat plans', interior: 'Room 1 interior', architecture: 'Architecture only' };
  for (const g of ['version', 'interior', 'architecture']) { const e = document.createElement('optgroup'); e.label = GT[g]; og[g] = e; }
  for (const m of list.models) { const o = document.createElement('option'); o.value = m.file; o.textContent = m.label || m.file; o.dataset.manifest = m.manifest || ''; (og[m.group || 'architecture'] || og.architecture).appendChild(o); }
  for (const g of ['version', 'interior', 'architecture']) if (og[g].children.length) sel.appendChild(og[g]);"""),
 ("""  el.innerHTML = `<div class="t">${n.title}</div><div class="tag">${n.tagline}</div>` +""",
  """  const vk = Object.keys(n.sections || {}).find(k => k === 'Verdict' || k === 'फ़ैसला');
  el.innerHTML = `<div class="t">${n.title}</div><div class="tag">${n.tagline}</div>` + (vk ? `<div class="verdict"><b>${vk}:</b> ${n.sections[vk]}</div>` : '') +"""),
 ("""    (n.budget ? `<details class="budget" open><summary>""", """    (n.budget ? `<details class="budget"><summary>"""),
 ("""    Object.entries(n.sections).map(([k, v]) =>""", """    Object.entries(n.sections || {}).filter(([k]) => k !== vk).map(([k, v]) =>"""),
])

# ------------------------------------------------------------ 5. walk help box: shown for a few seconds, then folds to one line
patch("src/extras.js", [
 ("""  setHudMin(store.get('hudMin') ? store.get('hudMin') === '1' : !!ctx.TOUCH);   // phones start minimised""",
  """  if (store.get('hudMin')) setHudMin(store.get('hudMin') === '1');
  else {   // first visit: show the help, fold it to one line once you start walking around
    hud.classList.toggle('min', !!ctx.TOUCH);
    let t = null; new MutationObserver(() => { if (!hud.classList.contains('hidden') && !t) t = setTimeout(() => hud.classList.add('min'), 7000); }).observe(hud, { attributes: true, attributeFilter: ['class'] });
  }"""),
])

# ------------------------------------------------------------ 6. Hindi for the new words
patch("src/i18n.js", [
 ("""  // left panel\n""", """  // left panel\n  'More ▾': 'और ▾', 'View': 'देखें', 'Measure': 'नाप', 'Tools': 'टूल', 'Plans': 'प्लान', 'Flat plans': 'घर के प्लान', 'More tools': 'और टूल',
  '★ Recommended': '★ सुझाया गया', 'Budget plain': 'कम बजट, सादा', 'Long-lasting': 'सबसे टिकाऊ', 'Marble classic': 'मार्बल क्लासिक', 'Panelled hall': 'पैनल वाला हॉल',
  'Room 2 bath (V1.2)': 'कमरा 2 बाथ (V1.2)', 'Dining & window': 'डाइनिंग और खिड़की', 'TV wall (from the sofa)': 'TV दीवार (सोफ़े से)',
  'Main door (just inside)': 'मुख्य दरवाज़ा (अंदर से)', 'Whole hall (from the south-east corner)': 'पूरा हॉल (दक्षिण-पूर्व कोने से)',\n"""),
])

# ------------------------------------------------------------ 7. Hall viewpoint for the dining corner
patch("src/config.js", [
 ("""      { name: 'Whole hall (from the south-east corner)', pos: [5.79, 1.65, 13.41], target: [2.44, 0.9, 6.1] },\n""",
  """      { name: 'Whole hall (from the south-east corner)', pos: [5.79, 1.65, 13.41], target: [2.44, 0.9, 6.1] },
      { name: 'Dining & window', pos: [3.96, 1.6, 9.0], target: [2.9, 0.9, 13.1] },\n"""),
])

# ------------------------------------------------------------ 8. models.json: plans first, short names, open on the Recommended plan
P = V + "models/models.json"
d = json.load(open(P, encoding="utf-8"), object_pairs_hook=OD)
SHORT = {"MyFlat_V1_3_Hall_Recommended.glb": "★ Recommended", "MyFlat_V1_3_Hall_Budget.glb": "Budget plain", "MyFlat_V1_3_Hall_LongLasting.glb": "Long-lasting",
         "MyFlat_V1_3_Hall_Marble.glb": "Marble classic", "MyFlat_V1_3_Hall_Panelled.glb": "Panelled hall", "MyFlat_V1_2_Room2_Ensuite.glb": "Room 2 bath (V1.2)"}
for m in d["models"]:
    if m["file"] in SHORT: m["short"] = SHORT[m["file"]]
order = list(SHORT)
d["models"].sort(key=lambda m: (0, order.index(m["file"])) if m["file"] in order else (1, 0))
d["default"] = "MyFlat_V1_3_Hall_Recommended.glb"
json.dump(d, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("viewer updated (v1.4 declutter)")
