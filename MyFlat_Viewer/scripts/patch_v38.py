# Build 38 (21 Nov 2026): paint name on wall click, hide-all-doors toggle, Learn highlights what we used (click = go there),
# picture beside each item in Compare. Run from MyFlat_Viewer: python3 scripts/patch_v38.py   (safe to re-run)
import json, re

def patch(path, marker, pairs):
    s = open(path).read()
    if marker in s: print(path, 'already'); return
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:80]); s = s.replace(a, b)
    open(path, 'w').write(s); print(path, 'patched')

# ---- A. colours.js: which paint is on this wall point?
patch('src/colours.js', 'colourAt', [
 ("window.wallColours = { applyScheme, update, state: () => state, data: () => DATA };",
  """// Same rule as the shader: the face shows the paint of the room it faces; the accent side gets the accent shade.
function colourAt(p, n) {
  const app = window.app; if (!app || !app.rooms || !DATA || !state.on || !p || !n) return null;
  if (Math.abs(n.y) >= 0.5) { const s = SH[state.ceil] || SH.L145; return s ? { shade: s, part: 'ceiling' } : null; }
  const len = Math.hypot(n.x, n.z) || 1, wx = p.x + (n.x / len) * 0.12, wz = p.z + (n.z / len) * 0.12;
  const order = ['Bathroom 1', 'Bathroom 2', 'Room 2 Bath', 'Kitchen', 'Passage', 'Room 1', 'Room 2', 'Stair', 'Balcony', 'Open Square', 'Hall'];
  for (const name of order) {
    const r = app.rooms.find((x) => x.name === name); if (!r) continue;
    const b = r.box || (r.obj && new THREE.Box3().setFromObject(r.obj)); if (!b) continue;
    if (wx < b.min.x - 0.03 || wx > b.max.x + 0.03 || wz < b.min.z - 0.03 || wz > b.max.z + 0.03) continue;
    const grp = DATA.rooms.find((g) => g.rooms.includes(name)); if (!grp) return { shade: null, room: name };
    const st = state.rooms[grp.k] || {}; const d = st.acc && st.side ? DIR[st.side] : null;
    const acc = !!(d && (n.x / len) * d[0] + (n.z / len) * d[1] > 0.8);
    return { shade: SH[acc ? st.acc : st.base] || null, accent: acc, room: name, group: grp };
  }
  return null;
}
window.wallColours = { applyScheme, update, state: () => state, data: () => DATA, colourAt };"""),
])

# ---- B. inside.js: show the paint name on the tap card
patch('src/inside.js', 'pc-paint', [
 ("breakdown: ['🔍 Break it down', '🔍 परतें खोलें'],",
  "breakdown: ['🔍 Break it down', '🔍 परतें खोलें'], paintIs: ['Paint', 'पेंट'], accentW: ['accent wall', 'एक्सेंट दीवार'], ceilingW: ['ceiling', 'छत'], shadeCard: ['Asian Paints shade', 'Asian Paints शेड'],"),
 ("  const title = it ? T(it.n) : T(d.title);",
  """  const title = it ? T(it.n) : T(d.title);
  let paint = '';
  if (window.wallColours?.colourAt && ['walls', 'pillars', 'beams', 'ceiling', 'roof'].includes(catOfO(o))) {
    const cam = window.viewer?.camera, cv = window.viewer?.renderer?.domElement;
    if (cam && cv) {
      const r = cv.getBoundingClientRect(), rc = new THREE.Raycaster();
      rc.setFromCamera(new THREE.Vector2(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1), cam);
      const hit = rc.intersectObject(o, true)[0];
      if (hit && hit.face) {
        const nrm = hit.face.normal.clone().transformDirection(hit.object.matrixWorld);
        if (nrm.dot(rc.ray.direction) > 0) nrm.negate();
        const c = window.wallColours.colourAt(hit.point, nrm);
        if (c && c.shade) paint = `<div class="pc-paint"><span class="sw" style="background:${c.shade.hex}"></span><div><b>${T(L10N.paintIs)}: ${esc(c.shade.n)}</b> <span class="code">${esc(c.shade.code)}</span>
          <div class="sub">${c.part === 'ceiling' ? T(L10N.ceilingW) : esc(T(c.group?.n || c.room || ''))}${c.accent ? ' · ' + T(L10N.accentW) : ''} · <a href="${esc(c.shade.url)}" target="_blank" rel="noopener">${T(L10N.shadeCard)} ↗</a></div></div></div>`;
      }
    }
  }"""),
 ("    ${it ? imgFor(it, 'pc-img') : ''}\n", "    ${it ? imgFor(it, 'pc-img') : ''}${paint}\n"),
 ("function showCard(o, x, y) {", "const catOfO = (o) => { for (let p = o; p; p = p.parent) if (p.userData && p.userData.category) return p.userData.category; return ''; };\nfunction showCard(o, x, y) {"),
])

# ---- C. tidy.js: hide / show all doors (More menu + walk box)
patch('src/tidy.js', 'doorsBtn', [
 ("// 2. Lights / day-night", """// 1b. One switch to hide every door (frames and leaves): walk through openings, see rooms joined up.
function doorsOn() { return window.app?.catVisible?.doors !== false; }
function doorLabel(b) { b.textContent = doorsOn() ? (hi() ? '🚪 सब दरवाज़े हटाएँ' : '🚪 Hide all doors') : (hi() ? '🚪 दरवाज़े वापस' : '🚪 Show doors'); b.classList.toggle('on', !doorsOn()); }
function toggleDoors() { window.viewer?.setCat?.('doors', !doorsOn()); document.querySelectorAll('.doorsBtn').forEach(doorLabel); }
(function addDoors() {
  const row = document.querySelector('#moreMenu #viewButtons')?.parentElement?.querySelectorAll('.mrow')[1];
  if (!row || !window.viewer?.setCat) return setTimeout(addDoors, 400);
  const mk = (cls) => { const b = document.createElement('button'); b.className = 'toggle doorsBtn ' + cls; b.type = 'button'; b.onclick = toggleDoors; doorLabel(b); return b; };
  if (!row.querySelector('.doorsBtn')) row.prepend(mk(''));
  const hudRow = document.querySelector('#walkHud .hudRow'); if (hudRow && !hudRow.querySelector('.doorsBtn')) hudRow.append(mk('small'));
  const ins = document.querySelector('.insideRow'); if (ins && !ins.querySelector('.doorsBtn')) ins.append(mk('small'));
  setInterval(() => document.querySelectorAll('.doorsBtn').forEach(doorLabel), 1500);   // stays right after the Controls panel or a plan switch
})();
document.addEventListener('keydown', (e) => { if (e.key === 'h' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || '')) toggleDoors(); });

// 2. Lights / day-night"""),
])

# ---- D. compare.js: picture beside each item name
patch('src/compare.js', 'cm-th', [
 ("    return `<tr><td class=\"cm-item\"><b>${esc(T(it.n))}</b>",
  "    return `<tr><td class=\"cm-item\"><span class=\"cm-th\" data-k=\"${it.k}\"></span><b>${esc(T(it.n))}</b>"),
 ("  body.querySelectorAll('.cm-open').forEach((b) => b.onclick = () => { const it = SHOP.items.find((x) => x.k === b.dataset.k); close(); window.inside?.openProduct(it, 'why'); });",
  """  body.querySelectorAll('.cm-open').forEach((b) => b.onclick = () => { const it = SHOP.items.find((x) => x.k === b.dataset.k); close(); window.inside?.openProduct(it, 'why'); });
  fillThumbs(body);"""),
 ("function drawPaints(body) {", """const ICONS = { mesh: '🦟', downlight: '💡', cove: '〰️', ac: '❄️', generic: '🛒' };
function fillThumbs(body) {
  // pictures are rendered from the 3D model one at a time so the table opens instantly
  const todo = [...body.querySelectorAll('.cm-th:not(.done)')];
  const step = () => {
    const el = todo.shift(); if (!el || !el.isConnected) return;
    el.classList.add('done'); const k = el.dataset.k; let u = null;
    try { u = ICONS[k] ? null : window.inside?.thumb?.(k, 200, 150); } catch (e) { u = null; }
    const it = SHOP.items.find((x) => x.k === k); const link = it && (it.ex?.[0]?.url || it.mid?.url);
    el.innerHTML = u ? `<img src="${u}" alt="">` : `<i>${ICONS[k] || '🛒'}</i>`;
    if (link) { el.title = 'Amazon ↗'; el.onclick = () => window.open(link, '_blank', 'noopener'); }
    setTimeout(step, 0);
  };
  step();
}
function drawPaints(body) {"""),
])

# ---- E. learn.js: rows we used are highlighted; click = go there. Dictionary terms in the plan get a tick.
patch('src/learn.js', 'data-go', [
 ("      (b.table ? `<div class=\"ctable\"><table class=\"ftable\">${b.table.map((r, i) => `<tr>${r.map(c => i === 0 ? `<th>${esc(c)}</th>` : `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>` : '') +",
  "      (b.table ? `<div class=\"ctable\"><table class=\"ftable\">${b.table.map((r, i) => { const go = i && b.go && b.go[i]; return `<tr${go ? ` class=\"used\" data-go=\"${esc(go.join('|'))}\" title=\"${esc(U('usedGo'))}\"` : ''}>${r.map((c, j) => i === 0 ? `<th>${esc(c)}</th>` : `<td>${go && j === 0 ? '✓ ' : ''}${esc(c)}${go && j === r.length - 1 ? ' <span class=\"gobtn\">👁</span>' : ''}</td>`).join('')}</tr>`; }).join('')}</table></div>${b.go ? `<p class=\"usedhint\">${esc(U('usedHint'))}</p>` : ''}` : '') +"),
 ("    wireCalc(body);", "    wireCalc(body);\n    body.querySelectorAll('tr[data-go]').forEach(tr => tr.onclick = () => { if (!showMe(tr.dataset.go.split('|'))) { tr.classList.add('miss'); tr.title = U('notin'); } });"),
 ("        h += `<div class=\"dterm\"><b>${esc(t.term)}</b>", "        h += `<div class=\"dterm${inScene ? ' used' : ''}\">${inScene ? '<span class=\"tick\">✓</span> ' : ''}<b>${esc(t.term)}</b>"),
])

# ---- data: which rows are 'used', and where to go
GO_TILES_CHOSEN = {1: ['_FLOOR_HALL_FINISH', 'FLOOR_HALL'], 2: ['_FLOOR_R2_FINISH', 'R1_DEF_FLOOR_FINISH', '_FLOOR_KIT_FINISH', 'FLOOR_R2'], 3: ['_FLOOR_B1_FINISH', 'R2B_FLOOR', 'FLOOR_B1'],
                   4: ['R2B_TILE_N_1', 'R2B_TILE', 'ENTRY_DADO'], 5: ['_FLOOR_KIT_FINISH', 'FLOOR_KIT'], 6: ['R2B_THRESHOLD', 'THRESHOLD_MAIN', '_W1_SILL', 'STAIR_01_F1_STEP_01'],
                   7: ['BALCONY_FLOOR_FINISH', 'BALCONY_FLOOR', 'FLOOR_OPENSQ'], 8: ['_SKIRTING']}
GO_TILES_WORDS = {3: ['_FLOOR_HALL_FINISH', 'FLOOR_HALL'], 7: ['_FLOOR_B1_FINISH', 'R2B_FLOOR', 'FLOOR_B1'], 8: ['R2B_THRESHOLD', 'THRESHOLD_MAIN', '_W1_SILL'], 9: ['BALCONY_FLOOR_FINISH', 'BALCONY_FLOOR', 'FLOOR_OPENSQ']}
GO_TILES_RATE = {1: ['_FLOOR_HALL_FINISH', 'FLOOR_HALL']}
GO_GRANITE = {1: ['R2B_THRESHOLD', 'THRESHOLD_MAIN', '_W1_SILL', 'STAIR_01_F1_STEP_01']}
GO_CEIL_WORDS = {2: ['_GYPSUM_BORDER$', 'GYPSUM_BORDER', 'FALSE_CEILING_BAND'], 3: ['_COVE_LED_1', 'COVE_LED'], 4: ['DOWNLIGHT'], 7: ['_GYPSUM_BORDER$', 'GYPSUM_BORDER', 'FALSE_CEILING_BAND']}
GO_CEIL_OPTS = {2: ['_GYPSUM_BORDER$', 'GYPSUM_BORDER', 'FALSE_CEILING_BAND']}
UI = [dict(usedHint="✓ = used in your plan · click a highlighted row to see it in 3D", usedGo="Show it in the 3D model"),
      dict(usedHint="✓ = आपके प्लान में इस्तेमाल · हाइलाइट लाइन दबाएँ, 3D में दिखेगा", usedGo="3D मॉडल में दिखाएँ")]
for li, path in enumerate(['models/learn_guide.json', 'models/learn_guide_hi.json']):
    g = json.load(open(path)); P = g['pages']; P['ui'].update(UI[li])
    t = P.get('tiles') or []
    if len(t) >= 4:
        t[0]['go'] = GO_TILES_WORDS; t[1]['go'] = GO_TILES_CHOSEN; t[2]['go'] = GO_TILES_RATE; t[3]['go'] = GO_GRANITE
        r = t[1]['table'][3]   # bathroom floor: the plan model uses 600×600 anti-skid
        r[1] = r[1].replace('300×600', '600×600 (or 300×600)') if '(or' not in r[1] else r[1]
    c = P.get('ceiling') or []
    if len(c) >= 3: c[0]['go'] = GO_CEIL_WORDS; c[2]['go'] = GO_CEIL_OPTS
    # JSON keys must be strings
    for card in t + c:
        if 'go' in card: card['go'] = {str(k): v for k, v in card['go'].items()}
    json.dump(g, open(path, 'w'), ensure_ascii=False, indent=1); print(path, 'go rows added')

# ---- F. CSS
c = 'src/styles.css'; css = open(c).read()
if '.pc-paint' not in css:
    css += """
/* ---- build 38 (21 Nov 2026) ---- */
#pickCard .pc-paint { display: flex; gap: 8px; align-items: flex-start; background: #faf7f1; border: 1px solid #eadfcb; border-radius: 8px; padding: 6px 8px; margin: 4px 0 6px; }
#pickCard .pc-paint .sw { width: 26px; height: 26px; border-radius: 6px; border: 1px solid rgba(0,0,0,.18); flex: none; }
#pickCard .pc-paint .code { color: #666; font-size: 11.5px; }
#pickCard .pc-paint .sub { color: #555; font-size: 11.5px; }
#cmpModal .cm-th { display: block; width: 120px; height: 90px; margin-bottom: 4px; border-radius: 8px; overflow: hidden; background: #f3f1ec; cursor: pointer; }
#cmpModal .cm-th img { width: 100%; height: 100%; object-fit: cover; display: block; }
#cmpModal .cm-th i { display: flex; width: 100%; height: 100%; align-items: center; justify-content: center; font-size: 30px; font-style: normal; }
#learn tr.used td { background: #eef8f1; cursor: pointer; }
#learn tr.used:hover td { background: #dff1e5; }
#learn tr.used td:first-child { font-weight: 700; color: #1f6f54; }
#learn tr.used.miss td { background: #f6f1e7; cursor: default; }
#learn .gobtn { float: right; opacity: .7; }
#learn .usedhint { font-size: 11.5px; color: #1f6f54; margin: 2px 0 6px; }
#learn .dterm.used { border-left: 3px solid #1f8a5b; padding-left: 7px; background: #f3faf5; }
#learn .dterm .tick { color: #1f8a5b; font-weight: 700; }
.doorsBtn.on { background: #1f2328 !important; color: #fff !important; }
"""
    open(c, 'w').write(css); print('css added')
