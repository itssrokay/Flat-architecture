// 🎨 Wall colours (19 Nov 2026): try real Asian Paints shades on the walls of each room, live in 3D.
// Every wall face is coloured by the room it faces (the shader steps a few cm into the room and looks the point up in the
// room floor boxes), so both sides of a wall can have different colours. One wall per room can be an accent.
// Data: models/colours.json (scripts/colours_data.py). Choice is remembered in this browser (localStorage).
import * as THREE from 'three';
const $ = (id) => document.getElementById(id);
const hi = () => (document.documentElement.lang === 'hi' ? 1 : 0);
const T = (p) => (Array.isArray(p) ? p[hi()] || p[0] : p == null ? '' : p);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const L = {
  btn: ['🎨 Wall colours', '🎨 दीवार के रंग'], title: ['Wall colours', 'दीवार के रंग'], schemes: ['Ready-made colour schemes', 'तैयार रंग योजनाएँ'],
  rooms: ['Room by room', 'कमरे के हिसाब से'], walls: ['Walls', 'दीवारें'], accent: ['Accent wall', 'एक्सेंट दीवार'], none: ['none', 'नहीं'],
  side: { N: ['North', 'उत्तर'], E: ['East', 'पूर्व'], S: ['South', 'दक्षिण'], W: ['West', 'पश्चिम'] }, which: ['Accent on', 'एक्सेंट'],
  on: ['Colours on', 'रंग चालू'], off: ['Show plain', 'सादा देखें'], painter: ['For the painter / dealer', 'पेंटर / डीलर के लिए'], copy: ['📋 Copy list', '📋 सूची कॉपी करें'],
  copied: ['Copied ✓', 'कॉपी हो गई ✓'], tips: ['Before you buy', 'ख़रीदने से पहले'], pick: ['Pick a colour', 'रंग चुनें'], close: ['Close', 'बंद करें'],
  sources: ['Sources', 'स्रोत'], all: ['All', 'सभी'], voices: ['What people say', 'लोग क्या कहते हैं'], voicesNote: ['Paraphrased from Indian homeowners and designers online.', 'ऑनलाइन भारतीय घर-मालिकों और डिज़ाइनरों की बातें, अपने शब्दों में।'], look: ['👁 Look at it', '👁 देखें'], kept: ['Kitchen and stair walls stay as they are.', 'रसोई और सीढ़ी की दीवारें जैसी हैं वैसी रहेंगी।'],
  custom: ['My own mix', 'मेरी अपनी पसंद'], ceil: ['Ceiling', 'छत'], floor: ['Floor tiles tone', 'फ़र्श की टाइल का रंग'], floorNote: ['The plan\'s tile is a warm greige (grey-beige) matt GVT. Choose a warmer or lighter tone if grey feels dull; ask the dealer for the same finish in that shade.', 'प्लान की टाइल गर्म ग्रेज (ग्रे-बेज) मैट GVT है। ग्रे फीका लगे तो गर्म या हल्का टोन चुनें; डीलर से उसी फ़िनिश में वह शेड माँगें।'],
};
const N = 12;
const U = {
  uWcOn: { value: 0 },
  uWcBox: { value: Array.from({ length: N }, () => new THREE.Vector4(0, 0, -1, -1)) },
  uWcBase: { value: Array.from({ length: N }, () => new THREE.Color(1, 1, 1)) },
  uWcAcc: { value: Array.from({ length: N }, () => new THREE.Color(1, 1, 1)) },
  uWcDir: { value: Array.from({ length: N }, () => new THREE.Vector2(0, 0)) },
  uWcUse: { value: new Array(N).fill(0) },             // 0 unused, 1 paint, 2 keep as is (kitchen, stair...)
};
const DIR = { N: [0, 1], S: [0, -1], E: [-1, 0], W: [1, 0] };   // inner-face normal of that wall (north = -Z)
let DATA = null, SH = {}, panel = null, pop = null;
let state = { scheme: 'peach', on: true, rooms: {}, ceil: 'L145', floor: 'ivory' };
// floor tones: multiply the tile texture (base is a warm greige 0.80/0.77/0.72); values above 1 lighten it
const FLOORS = { plan: { n: ['Greige (plan)', 'ग्रेज (प्लान)'], t: [1, 1, 1], sw: '#CCC4B8' }, ivory: { n: ['Ivory', 'आइवरी'], t: [1.2, 1.2, 1.12], sw: '#F2E8D4' },
  beige: { n: ['Warm beige', 'गर्म बेज'], t: [1.18, 1.1, 0.95], sw: '#EBD7BA' }, white: { n: ['Marble white', 'मार्बल सफ़ेद'], t: [1.24, 1.27, 1.3], sw: '#F5F3F0' },
  sand: { n: ['Sandy gold', 'रेतीला सुनहरा'], t: [1.2, 1.08, 0.82], sw: '#EFD2A6' } };
try { const s = JSON.parse(localStorage.getItem('myflat.colours') || 'null'); if (s && s.rooms) state = Object.assign(state, s); } catch (e) { /* private window */ }
const save = () => { try { localStorage.setItem('myflat.colours', JSON.stringify(state)); } catch (e) { /* ignore */ } };

fetch('./models/colours.json?v=33').then((r) => r.json()).then((d) => {
  DATA = d; SH = Object.fromEntries(d.shades.map((s) => [s.code, s]));
  if (!Object.keys(state.rooms).length) applyScheme(state.scheme, false);
  addButtons(); loop();
}).catch((e) => console.warn('colours.js', e));

function applyScheme(k, rerender = true) {
  const s = DATA.schemes.find((x) => x.k === k); if (!s) return;
  state.scheme = k; state.on = true;
  for (const r of DATA.rooms) { const [b, a] = s.rooms[r.k]; state.rooms[r.k] = { base: b, acc: a, side: a ? (state.rooms[r.k]?.side || r.acc) : '' }; }
  save(); update(); if (rerender) render();
}

// ------------------------------------------------------------------ shader
function patch(mat) {
  if (!mat || mat.userData._wc) return; mat.userData._wc = true;
  const prev = mat.onBeforeCompile;
  mat.onBeforeCompile = (sh, r) => {
    if (prev) prev.call(mat, sh, r);
    Object.assign(sh.uniforms, U);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWcPos;\nvarying vec3 vWcNor;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvWcPos = (modelMatrix * vec4(transformed, 1.0)).xyz;\nvWcNor = normalize(mat3(modelMatrix) * objectNormal);');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vWcPos; varying vec3 vWcNor; uniform float uWcOn; uniform vec4 uWcBox[${N}]; uniform vec3 uWcBase[${N}]; uniform vec3 uWcAcc[${N}]; uniform vec2 uWcDir[${N}]; uniform float uWcUse[${N}];`)
      .replace('vec4 diffuseColor = vec4( diffuse, opacity );', `vec4 diffuseColor = vec4( diffuse, opacity );
if (uWcOn > 0.5) { vec3 wn = normalize(vWcNor); if (abs(wn.y) < 0.5) { vec2 wp = vWcPos.xz + normalize(wn.xz) * 0.12;
  for (int i = 0; i < ${N}; i++) { if (uWcUse[i] > 0.5 && wp.x > uWcBox[i].x && wp.x < uWcBox[i].z && wp.y > uWcBox[i].y && wp.y < uWcBox[i].w) {
    if (uWcUse[i] < 1.5) diffuseColor.rgb = dot(normalize(wn.xz), uWcDir[i]) > 0.8 ? uWcAcc[i] : uWcBase[i]; break; } } } }`);
  };
  mat.customProgramCacheKey = () => 'myflat-wallcolours-1';
  mat.needsUpdate = true;
}
const catOf = (o) => { for (let p = o; p; p = p.parent) if (p.userData && p.userData.category) return p.userData.category; return ''; };
let lastModel = null, lastRooms = null;
function loop() {
  const app = window.app;
  if (app && app.model && app.ready !== false && (app.model !== lastModel || app.rooms !== lastRooms)) {
    lastModel = app.model; lastRooms = app.rooms;
    setTimeout(() => { app.model.traverse((o) => { if (o.isMesh && ['walls', 'pillars'].includes(catOf(o)) && !Array.isArray(o.material)) patch(o.material); }); update(); }, 600);
  }
  // inside.js swaps in its painted clones after load: keep patching new wall materials
  if (app && app.model) app.model.traverse((o) => { if (o.isMesh && !Array.isArray(o.material) && o.material && !o.material.userData._wc && ['walls', 'pillars'].includes(catOf(o))) patch(o.material); });
  setTimeout(loop, 700);
}
function update() {
  const app = window.app; if (!app || !app.rooms || !DATA) return;
  const order = ['Bathroom 1', 'Bathroom 2', 'Room 2 Bath', 'Kitchen', 'Passage', 'Room 1', 'Room 2', 'Stair', 'Balcony', 'Open Square', 'Hall'];
  U.uWcUse.value.fill(0);
  order.forEach((name, i) => {
    if (i >= N) return; const r = app.rooms.find((x) => x.name === name); if (!r) return;
    const b = r.box || (r.obj && new THREE.Box3().setFromObject(r.obj)); if (!b) return;
    U.uWcBox.value[i].set(b.min.x - 0.03, b.min.z - 0.03, b.max.x + 0.03, b.max.z + 0.03);
    const grp = DATA.rooms.find((g) => g.rooms.includes(name));
    if (!grp) { U.uWcUse.value[i] = 2; return; }
    const st = state.rooms[grp.k] || {}; const base = SH[st.base], acc = SH[st.acc] || base;
    if (!base) { U.uWcUse.value[i] = 2; return; }
    U.uWcBase.value[i].set(base.hex); U.uWcAcc.value[i].set(acc.hex);
    const d = st.acc && st.side ? DIR[st.side] : [0, 0]; U.uWcDir.value[i].set(d[0], d[1]);
    U.uWcUse.value[i] = 1;
  });
  U.uWcOn.value = state.on ? 1 : 0;
  extras();
}
// ceilings face away from the lights and render grey: give them their paint colour plus a soft 'bounce light' glow.
// Stainless steel guards have nothing to reflect and look dark grey: make them read as brushed steel.
function extras() {
  const app = window.app; if (!app || !app.model || !DATA) return;
  const ceil = new THREE.Color((SH[state.ceil] || SH.L145 || { hex: '#F7F0E6' }).hex);
  const ft = FLOORS[state.on ? state.floor : 'plan'] || FLOORS.plan;
  const seen = new Set();
  app.model.traverse((o) => {
    if (!o.isMesh || Array.isArray(o.material) || !o.material) return; const m = o.material; if (seen.has(m)) return; seen.add(m);
    const c = catOf(o), ud = m.userData;
    if (c === 'roof' || c === 'ceiling' || c === 'beams') {
      if (!ud._wcCol) ud._wcCol = m.color.clone();
      m.color.copy(state.on ? ceil : ud._wcCol);
      if (m.emissive) { m.emissive.copy(m.color).multiplyScalar(0.3); }
    } else if (/Steel_304|Steel_Brushed/i.test(m.name || '')) {
      if (ud._wcMet === undefined) ud._wcMet = [m.metalness, m.roughness];
      m.metalness = 0.35; m.roughness = 0.35;
    } else if (c === 'finishes' && /FLOOR/.test(o.name) && m.map && !/AntiSkid|Kota/i.test(m.name || '')) {
      if (!ud._wcCol) ud._wcCol = m.color.clone();
      m.color.setRGB(ud._wcCol.r * ft.t[0], ud._wcCol.g * ft.t[1], ud._wcCol.b * ft.t[2]);
    }
  });
}

// ------------------------------------------------------------------ UI
function addButtons() {
  const mk = (cls) => { const b = document.createElement('button'); b.className = cls; b.textContent = T(L.btn); b.onclick = toggle; return b; };
  const tryAdd = () => {
    const learn = $('learnBtn'); if (learn && !document.querySelector('#topbar .wcBtn')) learn.before(mk('toggle wcBtn'));
    const row = document.querySelector('.insideRow'); if (!row) return setTimeout(tryAdd, 400);
    if (!row.querySelector('.wcBtn')) row.appendChild(mk('small wcBtn'));
  };
  tryAdd();
  new MutationObserver(() => { document.querySelectorAll('.wcBtn').forEach((b) => b.textContent = T(L.btn)); if (panel && !panel.classList.contains('hidden')) render(); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  if (/[?&]colours=1/.test(location.search)) toggle();
}
function toggle() {
  if (!panel) { panel = document.createElement('div'); panel.id = 'wcPanel'; panel.className = 'hidden'; $('viewport').appendChild(panel); panel.addEventListener('pointerdown', (e) => e.stopPropagation()); }
  panel.classList.toggle('hidden'); document.querySelectorAll('.wcBtn').forEach((b) => b.classList.toggle('on', !panel.classList.contains('hidden')));
  if (!panel.classList.contains('hidden')) { if (!state.on) { state.on = true; update(); } render(); }
}
const sw = (code, cls = '') => { const s = SH[code]; return s ? `<span class="wc-sw ${cls}" style="background:${s.hex}" title="${esc(s.n)} ${s.code}"></span>` : '<span class="wc-sw none">—</span>'; };
const lbl = (code) => { const s = SH[code]; return s ? `<a href="${s.url}" target="_blank" rel="noopener">${esc(s.n)}</a> <span class="wc-code">${s.code}</span>` : `<span class="wc-code">${T(L.none)}</span>`; };
function render() {
  if (!panel || !DATA) return;
  const scheme = DATA.schemes.find((s) => s.k === state.scheme);
  let TAG = window.__wcTag || '';
  const tagRow = DATA.tagn ? `<div class="wc-chips wc-tags">${[['', L.all], ...Object.entries(DATA.tagn)].map(([k, n]) => `<button class="wc-chip ${TAG === k ? 'on' : ''}" data-tag="${k}">${esc(T(n))}</button>`).join('')}</div>` : '';
  const cards = DATA.schemes.filter((s) => !TAG || (s.tags || []).includes(TAG) || s.k === state.scheme).map((s) => `<button class="wc-card ${s.k === state.scheme ? 'on' : ''}" data-s="${s.k}"><b>${esc(T(s.n))}</b><span class="wc-mood">${esc(T(s.mood))}</span>${(s.tags || []).length && DATA.tagn ? `<span class="wc-tg">${s.tags.map((t) => esc(T(DATA.tagn[t]))).join(' · ')}</span>` : ''}
    <span class="wc-strip">${['hall', 'room1', 'room2'].map((r) => sw(s.rooms[r][0]) + (s.rooms[r][1] ? sw(s.rooms[r][1], 'acc') : '')).join('')}</span></button>`).join('');
  const rows = DATA.rooms.map((g) => { const st = state.rooms[g.k] || {};
    const sides = ['', 'N', 'E', 'S', 'W'].map((d) => `<option value="${d}" ${st.side === d ? 'selected' : ''}>${d ? T(L.side[d]) + (d === g.acc ? ' ★' : '') : T(L.none)}</option>`).join('');
    return `<div class="wc-room"><div class="wc-rn">${esc(T(g.n))}</div>
      <div class="wc-pair"><button class="wc-pick" data-r="${g.k}" data-w="base">${sw(st.base)}<span>${T(L.walls)}<br>${lbl(st.base)}</span></button>
      ${g.acc !== '' || st.acc ? `<button class="wc-pick" data-r="${g.k}" data-w="acc">${sw(st.acc, 'acc')}<span>${T(L.accent)}<br>${lbl(st.acc)}</span></button>` : ''}</div>
      ${g.acc !== '' || st.acc ? `<label class="wc-side">${T(L.which)}: <select data-side="${g.k}">${sides}</select> <i>★ ${esc(T(g.accN))}</i></label>` : ''}</div>`; }).join('');
  const list = DATA.rooms.map((g) => { const st = state.rooms[g.k] || {}; const b = SH[st.base], a = SH[st.acc];
    return `<li><b>${esc(T(g.n))}:</b> ${b ? `${esc(b.n)} ${b.code}` : '—'}${a && st.side ? ` · ${T(L.accent)} (${T(L.side[st.side])}): ${esc(a.n)} ${a.code}` : ''}</li>`; }).join('');
  panel.innerHTML = `<div class="wc-h"><b>🎨 ${T(L.title)}</b><button class="wc-onoff ${state.on ? '' : 'off'}">${state.on ? T(L.off) : T(L.on)}</button><button class="wc-x">✕</button></div>
    <div class="wc-body"><h5>${T(L.schemes)}</h5>${tagRow}<div class="wc-cards">${cards}</div>
    ${scheme ? `<div class="wc-why">${esc(T(scheme.why))}</div>` : ''}
    <h5>${T(L.rooms)}${!scheme ? ` · ${T(L.custom)}` : ''}</h5>${rows}
    <div class="wc-room"><div class="wc-rn">${T(L.ceil)}</div><div class="wc-chips">${DATA.shades.filter((x) => x.fam === 'white').map((x) => `<button class="wc-chip ${state.ceil === x.code ? 'on' : ''}" data-ceil="${x.code}"><span class="wc-sw" style="background:${x.hex}"></span>${esc(x.n)} <span class="wc-code">${x.code}</span></button>`).join('')}</div></div>
    <div class="wc-room"><div class="wc-rn">${T(L.floor)}</div><div class="wc-chips">${Object.entries(FLOORS).map(([k, f]) => `<button class="wc-chip ${state.floor === k ? 'on' : ''}" data-floor="${k}"><span class="wc-sw" style="background:${f.sw}"></span>${esc(T(f.n))}</button>`).join('')}</div><div class="wc-kept">${T(L.floorNote)}</div></div>
    <div class="wc-kept">${T(L.kept)}</div>
    <h5>${T(L.painter)}</h5><ul class="wc-list">${list}<li>${T(L.ceil)}: ${esc((SH[state.ceil] || {}).n || 'White Cameo')} ${state.ceil}</li><li>${T(L.floor)}: ${esc(T((FLOORS[state.floor] || FLOORS.plan).n))} (matt GVT)</li></ul><button class="small wc-copy">${T(L.copy)}</button>
    ${DATA.voices ? `<h5>${T(L.voices)}</h5><div class="wc-kept">${T(L.voicesNote)}</div><ul class="wc-tips">${DATA.voices.map((t) => `<li>${esc(T(t))}</li>`).join('')}</ul>` : ''}
    <h5>${T(L.tips)}</h5><ul class="wc-tips">${DATA.tips.map((t) => `<li>${esc(T(t))}</li>`).join('')}</ul>
    <div class="wc-src">${T(L.sources)}: ${DATA.sources.map(([n, u]) => `<a href="${u}" target="_blank" rel="noopener">${esc(n)}</a>`).join(' · ')}</div></div>`;
  panel.querySelector('.wc-x').onclick = toggle;
  panel.querySelector('.wc-onoff').onclick = () => { state.on = !state.on; save(); update(); render(); };
  panel.querySelectorAll('[data-tag]').forEach((b) => b.onclick = () => { window.__wcTag = b.dataset.tag; render(); });
  panel.querySelectorAll('.wc-card').forEach((b) => b.onclick = () => applyScheme(b.dataset.s));
  panel.querySelectorAll('[data-ceil]').forEach((b) => b.onclick = () => { state.ceil = b.dataset.ceil; save(); update(); render(); });
  panel.querySelectorAll('[data-floor]').forEach((b) => b.onclick = () => { state.floor = b.dataset.floor; state.on = true; save(); update(); render(); });
  panel.querySelectorAll('.wc-pick').forEach((b) => b.onclick = (e) => openPicker(b.dataset.r, b.dataset.w, b));
  panel.querySelectorAll('[data-side]').forEach((s) => s.onchange = () => { const st = state.rooms[s.dataset.side]; st.side = s.value; if (st.side && !st.acc) st.acc = st.base; state.scheme = null; save(); update(); render(); });
  panel.querySelector('.wc-copy').onclick = async (e) => {
    const txt = [...panel.querySelectorAll('.wc-list li')].map((li) => li.textContent).join('\n') + '\nAsian Paints shade codes. Please tint by code.';
    try { await navigator.clipboard.writeText(txt); e.target.textContent = T(L.copied); } catch (err) { prompt('Copy:', txt); }
  };
}
function openPicker(room, which, anchor) {
  if (pop) pop.remove();
  pop = document.createElement('div'); pop.className = 'wc-pop';
  pop.innerHTML = `<div class="wc-h"><b>${T(L.pick)}</b><button class="wc-x">✕</button></div>` + DATA.families.map(([f, n]) => {
    const list = DATA.shades.filter((s) => s.fam === f); if (!list.length) return '';
    return `<div class="wc-fam"><i>${esc(T(n))}</i><div>${list.map((s) => `<button class="wc-sw big" data-c="${s.code}" style="background:${s.hex}" title="${esc(s.n)} ${s.code}"></button>`).join('')}</div></div>`; }).join('')
    + (which === 'acc' ? `<button class="small wc-noacc">${T(L.none)}</button>` : '');
  panel.appendChild(pop);
  pop.querySelector('.wc-x').onclick = () => pop.remove();
  pop.querySelectorAll('[data-c]').forEach((b) => {
    b.onmouseenter = () => { const s = SH[b.dataset.c]; b.title = `${s.n} ${s.code}`; };
    b.onclick = () => { const st = state.rooms[room]; st[which] = b.dataset.c; if (which === 'acc' && !st.side) st.side = DATA.rooms.find((g) => g.k === room).acc || 'N'; state.scheme = null; state.on = true; save(); update(); pop.remove(); render(); };
  });
  const na = pop.querySelector('.wc-noacc'); if (na) na.onclick = () => { const st = state.rooms[room]; st.acc = null; st.side = ''; state.scheme = null; save(); update(); pop.remove(); render(); };
}
window.wallColours = { applyScheme, update, state: () => state, data: () => DATA };
