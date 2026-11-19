// V1.5 "What's inside": real-paint look for walls, layer-by-layer breakdown of every finish (3D, pull-apart),
// and a shopping list with Amazon links (budget / mid-range). Works on top of main.js through window.app / window.viewer.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const V = '35';
const $ = (id) => document.getElementById(id);
const hi = () => (document.documentElement.lang === 'hi' ? 1 : 0);
const T = (pair) => (Array.isArray(pair) ? pair[hi()] || pair[0] : pair);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
let DATA = null, SHOP = null;

Promise.all([
  fetch(`./models/layers.json?v=${V}`).then((r) => r.json()),
  fetch(`./models/shop.json?v=${V}`).then((r) => r.json()),
]).then(([l, s]) => { DATA = l; SHOP = s; addEntryPoints(); lastModel = null; }).catch((e) => console.warn('inside.js data', e));

// ------------------------------------------------------------------ textures (drawn once, shared)
function canvasTex(draw, w = 256, h = 256, repeat = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  t.anisotropy = 4; return t;
}
function noise(g, w, h, base, amp, seed = 1) {
  const img = g.createImageData(w, h); let s = seed * 9301 + 49297;
  const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280);
  for (let i = 0; i < w * h; i++) { const v = (rnd() - 0.5) * amp; img.data[i * 4] = base[0] + v; img.data[i * 4 + 1] = base[1] + v; img.data[i * 4 + 2] = base[2] + v; img.data[i * 4 + 3] = 255; }
  g.putImageData(img, 0, 0); return rnd;
}
const hexRGB = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
// paint: almost white so it keeps the material colour, with a soft roller stipple
const PAINT_MAP = canvasTex((g, w, h) => {
  const rnd = noise(g, w, h, [246, 245, 243], 7, 3);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '255,255,255' : '200,196,190'},0.05)`; g.beginPath(); g.arc(rnd() * w, rnd() * h, 1 + rnd() * 3, 0, 7); g.fill(); }
});
const PAINT_BUMP = canvasTex((g, w, h) => {
  const rnd = noise(g, w, h, [128, 128, 128], 40, 5);
  for (let i = 0; i < 1400; i++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '255,255,255' : '0,0,0'},0.10)`; g.beginPath(); g.arc(rnd() * w, rnd() * h, 0.8 + rnd() * 2.2, 0, 7); g.fill(); }
});
PAINT_BUMP.colorSpace = THREE.NoColorSpace;

const KIND_TEX = {};
function kindTex(kind, color) {
  const key = kind + (color || '');
  if (KIND_TEX[key]) return KIND_TEX[key];
  const C = color ? hexRGB(color) : null;
  const draw = {
    tile: (g, w, h) => { const b = C || [207, 198, 184]; const rnd = noise(g, w, h, b, 10, 7); for (let i = 0; i < 30; i++) { g.strokeStyle = 'rgba(150,140,128,0.25)'; g.beginPath(); g.moveTo(rnd() * w, rnd() * h); g.bezierCurveTo(rnd() * w, rnd() * h, rnd() * w, rnd() * h, rnd() * w, rnd() * h); g.stroke(); }
      g.fillStyle = 'rgba(110,104,96,0.9)'; for (let x = 0; x <= w; x += w / 2) g.fillRect(x - 1.5, 0, 3, h); for (let y = 0; y <= h; y += h / 2) g.fillRect(0, y - 1.5, w, 3); },
    paint: (g, w, h) => { noise(g, w, h, C || [238, 233, 224], 6, 2); },
    primer: (g, w, h) => { noise(g, w, h, C || [228, 234, 238], 5, 4); },
    putty: (g, w, h) => { noise(g, w, h, C || [250, 250, 246], 4, 6); },
    plaster: (g, w, h) => { const rnd = noise(g, w, h, C || [176, 170, 160], 30, 8); for (let i = 0; i < 600; i++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '90,85,78' : '230,226,218'},0.6)`; g.fillRect(rnd() * w, rnd() * h, 1.5, 1.5); } },
    brick: (g, w, h) => { g.fillStyle = '#c8c2b6'; g.fillRect(0, 0, w, h); const rnd = (() => { let s = 11; return () => ((s = (s * 9301 + 49297) % 233280) / 233280); })();
      const bh = h / 8, bw = w / 3; for (let r = 0; r < 8; r++) for (let c = -1; c < 4; c++) { const x = c * bw + (r % 2 ? bw / 2 : 0); const k = 150 + rnd() * 40; g.fillStyle = `rgb(${k},${k * 0.45},${k * 0.33})`; g.fillRect(x + 3, r * bh + 3, bw - 6, bh - 6); } },
    concrete: (g, w, h) => { const rnd = noise(g, w, h, C || [156, 156, 152], 26, 9); for (let i = 0; i < 160; i++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '110,108,104' : '190,188,182'},0.8)`; g.beginPath(); g.arc(rnd() * w, rnd() * h, 1 + rnd() * 3, 0, 7); g.fill(); } },
    screed: (g, w, h) => { noise(g, w, h, C || [169, 163, 152], 28, 10); },
    adhesive: (g, w, h) => { noise(g, w, h, C || [185, 188, 191], 14, 12); g.strokeStyle = 'rgba(120,124,128,0.7)'; g.lineWidth = 3; for (let y = 6; y < h; y += 14) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); } },
    membrane: (g, w, h) => { noise(g, w, h, C || [96, 132, 160], 10, 13); },
    laminate: (g, w, h) => { const b = C || [201, 165, 126]; const rnd = noise(g, w, h, b, 8, 14); for (let i = 0; i < 70; i++) { g.strokeStyle = `rgba(120,85,50,${0.08 + rnd() * 0.12})`; g.lineWidth = 1 + rnd() * 2; const y = rnd() * h; g.beginPath(); g.moveTo(0, y); g.bezierCurveTo(w * 0.3, y + rnd() * 8 - 4, w * 0.7, y + rnd() * 8 - 4, w, y + rnd() * 6 - 3); g.stroke(); } },
    ply: (g, w, h) => { const rnd = noise(g, w, h, C || [216, 185, 140], 10, 15); for (let i = 0; i < 40; i++) { g.strokeStyle = 'rgba(150,110,60,0.18)'; g.beginPath(); const y = rnd() * h; g.moveTo(0, y); g.lineTo(w, y + rnd() * 10 - 5); g.stroke(); } },
    wpc: (g, w, h) => { const b = C || [143, 106, 72]; g.fillStyle = `rgb(${b})`; g.fillRect(0, 0, w, h); for (let x = 0; x < w; x += 16) { g.fillStyle = 'rgba(40,25,10,0.35)'; g.fillRect(x, 0, 4, h); g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(x + 6, 0, 3, h); } },
    gypsum: (g, w, h) => { noise(g, w, h, C || [242, 241, 236], 5, 16); },
    tape: (g, w, h) => { noise(g, w, h, [250, 250, 250], 3, 17); g.fillStyle = 'rgba(200,200,200,0.6)'; g.fillRect(w / 2 - 12, 0, 24, h); },
    marble: (g, w, h) => { const rnd = noise(g, w, h, C || [240, 238, 234], 5, 18); for (let i = 0; i < 14; i++) { g.strokeStyle = `rgba(120,120,125,${0.15 + rnd() * 0.25})`; g.lineWidth = 0.6 + rnd() * 1.5; g.beginPath(); g.moveTo(rnd() * w, 0); g.bezierCurveTo(rnd() * w, h * 0.3, rnd() * w, h * 0.7, rnd() * w, h); g.stroke(); } },
    kota: (g, w, h) => { noise(g, w, h, C || [127, 154, 140], 24, 19); },
    lime: (g, w, h) => { const rnd = noise(g, w, h, C || [199, 169, 142], 10, 20); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '230,210,190' : '170,140,115'},0.12)`; g.beginPath(); g.arc(rnd() * w, rnd() * h, 10 + rnd() * 30, 0, 7); g.fill(); } },
    glue: (g, w, h) => { noise(g, w, h, [232, 217, 168], 6, 21); },
    metal: (g, w, h) => { noise(g, w, h, [190, 192, 196], 8, 22); },
  }[kind] || ((g, w, h) => noise(g, w, h, C || [200, 200, 200], 8, 23));
  KIND_TEX[key] = canvasTex(draw);
  return KIND_TEX[key];
}

// ------------------------------------------------------------------ 1. real-paint look on walls, pillars, beams and the ceiling
const PAINT_CATS = new Set(['walls', 'pillars', 'beams', 'ceiling', 'roof']);
const WALL_WHITE = new THREE.Color('#ebe6dd');
const CEIL_WHITE = new THREE.Color('#f2f0ea');
function catOf(o) { for (let p = o; p; p = p.parent) if (p.userData && p.userData.category) return p.userData.category; return 'other'; }
function boxUV(geom, mw, scale) {
  const pos = geom.attributes.position, nor = geom.attributes.normal; if (!pos || !nor) return false;
  const uv = new Float32Array(pos.count * 2), p = new THREE.Vector3(), n = new THREE.Vector3(), nm = new THREE.Matrix3().getNormalMatrix(mw);
  for (let i = 0; i < pos.count; i++) {
    p.fromBufferAttribute(pos, i).applyMatrix4(mw); n.fromBufferAttribute(nor, i).applyMatrix3(nm);
    const ax = Math.abs(n.x), ay = Math.abs(n.y), az = Math.abs(n.z);
    let u, v; if (ax >= ay && ax >= az) { u = p.z; v = p.y; } else if (ay >= az) { u = p.x; v = p.z; } else { u = p.x; v = p.y; }
    uv[i * 2] = u / scale; uv[i * 2 + 1] = v / scale;
  }
  geom.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); return true;
}
const painted = new Map();   // original material -> painted clone
function paintModel(root) {
  const app = window.app;
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (o.isMesh && !o.userData._lam && DATA && layerIdFor(o) === 'tv_laminate') woodLaminate(o);
    if (!o.isMesh || o.userData._painted) return;
    const cat = catOf(o); if (!PAINT_CATS.has(cat)) return;
    const orig = o.userData._origMat || o.material; if (!orig || Array.isArray(orig) || orig.map) return;
    if (cat === 'roof' && !/SLAB_ROOF/i.test(o.name)) return;
    if (!o.geometry.attributes.uv) { o.geometry = o.geometry.clone(); if (!boxUV(o.geometry, o.matrixWorld, 0.9)) return; }
    let m = painted.get(orig);
    if (!m) {
      m = orig.clone(); m.map = PAINT_MAP; m.bumpMap = PAINT_BUMP; m.bumpScale = 0.35; m.roughness = 0.94; m.metalness = 0;
      if (cat === 'pillars' || cat === 'beams') m.color.copy(WALL_WHITE);     // pillars and beams are plastered and painted like the walls
      if (cat === 'roof' || cat === 'ceiling') m.color.copy(CEIL_WHITE);
      m.clippingPlanes = orig.clippingPlanes; m.name = (orig.name || 'mat') + '_paint'; painted.set(orig, m);
      if (app.materials && app.materials.has(orig)) app.materials.set(m, app.materials.get(orig));
    }
    if (o.material === orig) o.material = m;
    o.userData._origMat = m; o.userData._painted = true;
  });
}
// the laminate TV panel gets a visible light-oak grain, so it reads as laminate and not as a painted board
let LAM = null;
function woodLaminate(o) {
  const app = window.app, orig = o.userData._origMat || o.material; if (!orig || Array.isArray(orig)) return;
  o.geometry = o.geometry.clone(); if (!boxUV(o.geometry, o.matrixWorld, 1.22)) return;      // one 4 ft sheet per texture repeat
  if (!LAM) { LAM = orig.clone(); LAM.map = kindTex('laminate', '#c9a57e'); LAM.color.set('#ffffff'); LAM.roughness = 0.7; LAM.metalness = 0; LAM.clippingPlanes = orig.clippingPlanes;
    LAM.map.rotation = Math.PI / 2; if (app.materials && app.materials.has(orig)) app.materials.set(LAM, app.materials.get(orig)); }
  if (o.material === orig) o.material = LAM; o.userData._origMat = LAM; o.userData._lam = true;
}
// wall seams drawn as black lines make painted walls look like panels: hide them when you are inside
const SEAM_CATS = new Set(['walls', 'pillars', 'beams', 'roof', 'ceiling']);
function updateSeams() {
  const app = window.app, walk = window.viewer && window.viewer.walk; if (!app || !app.edges) return;
  const inside = !!(walk && walk.active);
  for (const e of app.edges) { const c = e.parent ? catOf(e.parent) : ''; if (SEAM_CATS.has(c)) e.visible = app.edgesOn && !inside; }
}
let lastModel = null;
setInterval(() => {
  const app = window.app; if (!app || !app.model) return;
  if (app.model !== lastModel && app.ready !== false) { lastModel = app.model; paintModel(app.model); }
  if (app.compare && app.compare.root && !app.compare.root.userData._painted) { paintModel(app.compare.root); app.compare.root.userData._painted = true; }
  updateSeams();
}, 400);

// ------------------------------------------------------------------ 2. which build-up / shop item belongs to an object
function layerIdFor(o) {
  if (!DATA || !o) return null;
  const ud = o.userData || {}, name = o.name || '', spec = ud.spec || '', cat = ud.category || '', sub = ud.subtype || '';
  for (const r of DATA.rules) {
    if (r.name && !new RegExp(r.name, 'i').test(name)) continue;
    if (r.spec && !new RegExp(r.spec, 'i').test(spec)) continue;
    if (r.cat && r.cat !== cat) continue;
    if (r.sub && r.sub !== sub) continue;
    if (!r.name && !r.spec && !r.cat) continue;
    return r.id;
  }
  return null;
}
function shopFor(o) { if (!SHOP || !o) return null; return SHOP.items.find((it) => it.match && new RegExp(it.match, 'i').test(o.name || '')) || null; }
// anything else with a description still gets a card: its spec, size and an Amazon search built from the spec
const NO_GENERIC = new Set(['walls', 'floors', 'roof', 'pillars', 'beams', 'ceiling', 'stairs', 'context', 'plan_reference', 'vents', 'doors', 'windows', 'fenestration']);
function genericFor(o) {
  if (!o) return null; let p = o; while (p && !(p.userData && p.userData.spec) && p.parent) p = p.parent;
  const spec = (p && p.userData && p.userData.spec) || ''; const cat = catOf(o);
  if (!spec || NO_GENERIC.has(cat)) return null;
  const q = spec.split(/[;(:]|, /)[0].replace(/[0-9.]+\s*(ft|mm|inch|in|cm)\b/gi, '').trim().slice(0, 70);
  const az = (lo, hi) => `https://www.amazon.in/s?k=${encodeURIComponent(q)}` + (lo ? `&rh=p_36%3A${lo * 100}-${hi * 100}` : '');
  const nm = (o.name || '').replace(/^(DEF|OP[A-E]|H[RBLMP]|HBB|R2B)_/, '').replace(/^R1_(DEF|OP[A-E])_/, '').replace(/_\d+$/, '').replace(/_/g, ' ').toLowerCase();
  return { k: 'generic', generic: true, n: [nm.charAt(0).toUpperCase() + nm.slice(1), nm], size: [spec, spec], qty: 1, ex: [],
    budget: { band: '', url: az() }, mid: { band: '', url: az() }, why: [spec, spec] };
}
function productFor(o) { return shopFor(o) || genericFor(o); }

// ------------------------------------------------------------------ 3. inspector: "What's it made of?" + "Buy similar"
const L10N = {
  made: ["What's it made of?", 'यह किससे बना है?'], open3d: ['🔍 See the layers in 3D', '🔍 परतें 3D में देखें'], buy: ['🛒 Buy similar on Amazon', '🛒 Amazon पर ऐसा ही'],
  budget: ['Budget', 'बजट'], mid: ['Mid-range', 'मिड-रेंज'], examples: ['Examples', 'उदाहरण'], inside: ["🔍 What's inside", '🔍 अंदर क्या है'], shop: ['🛒 Shopping list', '🛒 ख़रीद की सूची'],
  pull: ['Pull apart', 'अलग करें'], feel: ['How it feels', 'छूने में कैसा'], drag: ['Drag to turn · scroll to zoom · tap a layer', 'घुमाने के लिए खींचें · ज़ूम के लिए स्क्रॉल · परत पर टैप करें'],
  pick: ['Choose a finish', 'फ़िनिश चुनें'], close: ['Close', 'बंद करें'], surface: ['outside / surface', 'बाहर / सतह'], structure: ['structure', 'ढाँचा'],
  inModel: ['In this plan', 'इस प्लान में'], also: ['Also needed', 'यह भी चाहिए'], qty: ['qty', 'संख्या'],
  tLayers: ['Layers', 'परतें'], tWhy: ['Why · pros · cons', 'क्यों · फ़ायदे · कमियाँ'], tMist: ['Mistakes · myths', 'ग़लतियाँ · भ्रम'],
  why: ['Why this', 'यही क्यों'], pros: ['Good', 'फ़ायदे'], cons: ['Watch out', 'ध्यान दें'], alt: ['Alternatives', 'दूसरे विकल्प'],
  mist: ['Common mistakes in small towns and villages', 'छोटे शहर और गाँव में आम ग़लतियाँ'], myths: ['Myth vs fact', 'भ्रम और सच'], myth: ['Myth', 'भ्रम'], fact: ['Fact', 'सच'],
  details: ['ℹ Details', 'ℹ विवरण'], prodWhy: ['👍 Why · pros · cons', '👍 क्यों · फ़ायदे · कमियाँ'], prodMist: ['⚠ Mistakes · options', '⚠ ग़लतियाँ · विकल्प'], search: ['🛒 Search on Amazon', '🛒 Amazon पर खोजें'], size: ['Size', 'साइज़'], room: ['Room', 'कमरा'], allItems: ['All items by room', 'कमरे के हिसाब से सब चीज़ें'], mistP: ['Mistakes people make', 'लोग कौन-सी ग़लतियाँ करते हैं'], breakdown: ['🔍 Break it down', '🔍 परतें खोलें'], openAmazon: ['Opens Amazon', 'Amazon खुलेगा'], tapImg: ['Tap a picture to open an example on Amazon', 'Amazon पर उदाहरण खोलने के लिए फ़ोटो दबाएँ'],
};
let lastSel = null;
const insp = $('inspector');
new MutationObserver(() => {
  const app = window.app; const o = app && app.selected;
  if (!o || insp.querySelector('.insideBox')) return;
  const id = layerIdFor(o), it = productFor(o); if (!id && !it) return;
  const box = document.createElement('div'); box.className = 'insideBox';
  let html = '';
  if (id) { const d = DATA.layers[id];
    html += `<div class="ib-t">${T(L10N.made)} <span>${esc(T(d.title))}</span></div><div class="ib-chain">${d.layers.map((l) => esc(T(l.n))).join(' <b>→</b> ')}</div>
      <button class="small accent" data-inside="${id}">${T(L10N.open3d)}</button>`; }
  if (it) html += `<div class="ib-t" style="margin-top:8px">${it.generic ? T(L10N.search) : T(L10N.buy)}</div>${pcHTML(it, 3)}<div class="ib-shop">${shopLinks(it)}</div>
      ${it.generic ? '' : `<button class="small accent" data-prod="why">${T(L10N.prodWhy)}</button> <button class="small" data-prod="mist">${T(L10N.prodMist)}</button>`}`;
  box.innerHTML = html; insp.appendChild(box);
  const b = box.querySelector('[data-inside]'); if (b) b.onclick = () => openLayers(b.dataset.inside, 'layers');
  box.querySelectorAll('[data-prod]').forEach((x) => x.onclick = () => openProduct(it, x.dataset.prod));
}).observe(insp, { childList: true });

function pcHTML(it, n = 2) {
  if (!it.pros && !it.cons) return '';
  const li = (a, cls) => (a || []).slice(0, n).map((x) => `<li class="${cls}">${esc(T(x))}</li>`).join('');
  return `<ul class="pc-pc">${li(it.pros, 'p')}${li(it.cons, 'c')}</ul>`;
}
function shopLinks(it) {
  if (it.generic) return `<a class="buy m" href="${it.mid.url}" target="_blank" rel="noopener">${T(L10N.search)}</a>`;
  const ex = it.ex.map((e) => `<a href="${e.url}" target="_blank" rel="noopener">${esc(e.t)}</a>`).join(' · ');
  return `<a class="buy b" href="${it.budget.url}" target="_blank" rel="noopener">${T(L10N.budget)} ${it.budget.band}</a>
    <a class="buy m" href="${it.mid.url}" target="_blank" rel="noopener">${T(L10N.mid)} ${it.mid.band}</a>
    ${ex ? `<div class="ex">${T(L10N.examples)}: ${ex}</div>` : ''}${it.note ? `<div class="ex">${esc(T(it.note))}</div>` : ''}`;
}

// ------------------------------------------------------------------ 4. entry points: left panel + More menu
function addEntryPoints() {
  const mk = (txt, fn, cls = 'small') => { const b = document.createElement('button'); b.className = cls; b.textContent = txt; b.onclick = fn; return b; };
  const row = document.createElement('div'); row.className = 'insideRow';
  row.append(mk(T(L10N.inside), () => openLayers(null)), mk(T(L10N.shop), openShop));
  const dp = $('designPanel'); if (dp) dp.after(row);
  const tools = document.querySelector('#moreMenu .mg:last-child .mrow');
  if (tools) { tools.prepend(mk(T(L10N.shop), openShop, '')); tools.prepend(mk(T(L10N.inside), () => openLayers(null), '')); }
  new MutationObserver(() => { const [a, b] = row.children; a.textContent = T(L10N.inside); b.textContent = T(L10N.shop); if (modal && !modal.classList.contains('hidden')) rerender(); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
}

// ------------------------------------------------------------------ 5. layers modal (its own little 3D scene)
let modal = null, three = null, curId = null, curMode = 'layers';
function ensureModal() {
  if (modal) return;
  modal = document.createElement('div'); modal.id = 'insideModal'; modal.className = 'hidden';
  modal.innerHTML = `<div class="im-card"><div class="im-head"><div class="im-title"></div><select class="im-pick"></select><button class="im-x small"></button></div>
    <div class="im-body"><div class="im-3d"><div class="im-canvas"></div><div class="im-ctl"><label><span class="im-pull"></span> <input type="range" min="0" max="1" step="0.01" value="0.8" class="im-range"></label><span class="im-hint"></span></div></div>
    <div class="im-side"></div></div></div>`;
  document.body.appendChild(modal);
  modal.addEventListener('pointerdown', (e) => { if (e.target === modal) close(); });
  modal.querySelector('.im-x').onclick = close;
  modal.querySelector('.im-pick').onchange = (e) => openLayers(e.target.value);
  modal.querySelector('.im-range').oninput = (e) => { if (three) { three.explode = +e.target.value; three.layout(); } };
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !modal.classList.contains('hidden')) close(); });
}
function close() { modal.classList.add('hidden'); if (three) three.running = false; }
function rerender() { if (curMode === 'shop') openShop(); else if (curMode === 'product') openProduct(curProd, modal.dataset.ptab || 'why'); else openLayers(curId); }

function openLayers(id, tab) {
  if (!DATA) return; ensureModal(); curMode = 'layers';
  if (tab) modal.dataset.tab = tab; else if (id && id !== curId) modal.dataset.tab = 'layers';
  id = id || curId || 'wall_int'; curId = id; const d = DATA.layers[id];
  modal.classList.remove('hidden', 'shop'); modal.querySelector('.im-3d').style.display = '';
  modal.querySelector('.im-title').textContent = T(d.title);
  const pick = modal.querySelector('.im-pick'); pick.style.display = '';
  pick.innerHTML = `<option disabled>${T(L10N.pick)}</option>` + DATA.order.map((k) => `<option value="${k}" ${k === id ? 'selected' : ''}>${esc(T(DATA.layers[k].title))}</option>`).join('');
  modal.querySelector('.im-x').textContent = T(L10N.close); modal.querySelector('.im-pull').textContent = T(L10N.pull); modal.querySelector('.im-hint').textContent = T(L10N.drag);
  const side = modal.querySelector('.im-side');
  const curTab = modal.dataset.tab || 'layers';
  const li = (arr) => `<ul>${(arr || []).map((x) => `<li>${esc(T(x))}</li>`).join('')}</ul>`;
  const whyHTML = `<div class="im-why"><b>${T(L10N.why)}:</b> ${esc(T(d.why || ''))}</div>
    <div class="im-pc"><div class="p"><h5>${T(L10N.pros)}</h5>${li(d.pros)}</div><div class="c"><h5>${T(L10N.cons)}</h5>${li(d.cons)}</div></div>
    ${d.alt ? `<h5>${T(L10N.alt)}</h5><p class="im-alt">${esc(T(d.alt))}</p>` : ''}`;
  const mistHTML = `<h5>⚠ ${T(L10N.mist)}</h5><ol class="im-mist">${(d.mistakes || []).map((x) => `<li>${esc(T(x))}</li>`).join('')}</ol>
    <h5>${T(L10N.myths)}</h5>${(d.myths || []).map(([m, f]) => `<div class="im-myth"><div class="m"><b>✗ ${T(L10N.myth)}:</b> ${esc(T(m))}</div><div class="f"><b>✓ ${T(L10N.fact)}:</b> ${esc(T(f))}</div></div>`).join('')}`;
  const tabs = `<div class="im-tabs">${[['layers', L10N.tLayers], ['why', L10N.tWhy], ['mist', L10N.tMist]].map(([k, l]) => `<button class="${k === curTab ? 'on' : ''}" data-tab="${k}">${T(l)}</button>`).join('')}</div>`;
  if (curTab !== 'layers') {
    side.innerHTML = tabs + (curTab === 'why' ? whyHTML : mistHTML);
    side.querySelectorAll('.im-tabs button').forEach((b) => b.onclick = () => { modal.dataset.tab = b.dataset.tab; openLayers(id); });
    if (!three) three = makeScene(modal.querySelector('.im-canvas'));
    three.build(d); three.explode = +modal.querySelector('.im-range').value; three.layout(true); three.start();
    return;
  }
  side.innerHTML = tabs + `<div class="im-feel"><b>${T(L10N.feel)}:</b> ${esc(T(d.feel))}</div>
    <div class="im-end">▲ ${T(L10N.surface)}</div>
    <ol class="im-list">${d.layers.map((l, i) => `<li data-i="${i}"><span class="sw" style="background:${swatch(l)}"></span><div><b>${i + 1}. ${esc(T(l.n))}</b>
      <span class="mm">${l.mm >= 1 ? l.mm + ' mm' : '< 1 mm'}</span><div class="w">${esc(T(l.what))}</div>${l.cost ? `<div class="c">${esc(l.cost)}</div>` : ''}</div></li>`).join('')}</ol>
    <div class="im-end">▼ ${T(L10N.structure)}</div>${d.note ? `<div class="im-note">${esc(T(d.note))}</div>` : ''}`;
  side.querySelectorAll('.im-tabs button').forEach((b) => b.onclick = () => { modal.dataset.tab = b.dataset.tab; openLayers(id); });
  side.querySelectorAll('.im-list li').forEach((li) => { li.onmouseenter = () => three && three.highlight(+li.dataset.i); li.onclick = () => three && three.highlight(+li.dataset.i, true); });
  if (!three) three = makeScene(modal.querySelector('.im-canvas'));
  three.build(d); three.explode = +modal.querySelector('.im-range').value; three.layout(true); three.start();
}
function swatch(l) {
  if (l.color) return l.color;
  return { tile: '#cfc6b8', paint: '#ebe6dd', primer: '#e2e9ee', putty: '#fafaf6', plaster: '#b0aa9f', brick: '#a2533e', concrete: '#9c9c98', screed: '#a9a398', adhesive: '#b9bcbf',
    membrane: '#6084a0', laminate: '#c9a57e', ply: '#d8b98c', wpc: '#8f6a48', frame: '#b7bcc2', gypsum: '#f2f1ec', tape: '#ffffff', marble: '#efede9', kota: '#7f9a8c', lime: '#c7a98e',
    glue: '#e8d9a8', metal: '#c0c0c0', pipe: '#dcdcdc', gap: 'transparent' }[l.kind] || '#ccc';
}

function makeScene(host) {
  const W = () => host.clientWidth || 520, H = () => host.clientHeight || 380;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1)); renderer.setSize(W(), H());
  host.appendChild(renderer.domElement);
  const labels = new CSS2DRenderer(); labels.setSize(W(), H()); labels.domElement.className = 'im-labels'; host.appendChild(labels.domElement);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(3, 5, 4); scene.add(sun);
  const under = new THREE.DirectionalLight(0xffffff, 0.35); under.position.set(2, -5, 3); scene.add(under);   // lights the ceiling build-up, seen from below
  const cam = new THREE.PerspectiveCamera(32, W() / H(), 0.05, 50);
  const ctl = new OrbitControls(cam, labels.domElement); ctl.enableDamping = true; ctl.enablePan = false; ctl.minDistance = 1.5; ctl.maxDistance = 9;
  const group = new THREE.Group(); scene.add(group);
  const ray = new THREE.Raycaster(); const ndc = new THREE.Vector2();
  const S = { renderer, scene, cam, ctl, group, items: [], explode: 0.8, axis: 'floor', running: false };
  const vt = (mm) => 0.035 + 0.075 * Math.log10(1 + mm);   // visual thickness: thin coats still visible, slabs not huge
  S.build = (d) => {
    group.traverse((o) => { if (o.isCSS2DObject && o.element) o.element.remove(); });   // drop old number tags from the label layer
    group.clear(); S.items = []; S.axis = d.axis; const n = d.layers.length;
    under.intensity = d.axis === 'ceiling' ? 1.4 : 0.35;
    d.layers.forEach((l, i) => {
      const t = vt(l.mm); const frac = 0.42 + 0.58 * (n > 1 ? i / (n - 1) : 1);   // outer layers cut back so the ones below show (stepped cutaway)
      const obj = new THREE.Group(); let mesh;
      if (l.kind === 'frame' || l.kind === 'pipe' || l.kind === 'gap') {
        const ghost = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0x9aa3ad, wireframe: true, transparent: true, opacity: 0.35 }));
        obj.add(ghost); mesh = ghost;
        if (l.kind !== 'gap') {
          const mat = new THREE.MeshStandardMaterial({ color: l.kind === 'pipe' ? 0xdedede : 0xb7bcc2, metalness: l.kind === 'frame' ? 0.7 : 0.1, roughness: 0.4 });
          for (let k = 0; k < 3; k++) { const bar = l.kind === 'pipe' ? new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 1, 16), mat) : new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), mat); bar.userData.bar = k; obj.add(bar); }
        }
      } else {
        const map = kindTex(l.kind, l.color);
        mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ map, roughness: l.kind === 'membrane' || l.kind === 'marble' ? 0.35 : 0.85, metalness: l.kind === 'metal' ? 0.8 : 0 }));
        obj.add(mesh);
      }
      const tag = document.createElement('div'); tag.className = 'im-tag'; tag.textContent = String(i + 1); const lab = new CSS2DObject(tag); obj.add(lab);
      group.add(obj); S.items.push({ obj, mesh, t, frac, layer: l, lab, i });
    });
  };
  S.layout = (resetCam) => {
    const n = S.items.length, gap = 0.04 + S.explode * 0.32, A = 1.7, B = 1.15;
    let off = 0; const total = S.items.reduce((s, it) => s + it.t, 0) + gap * (n - 1);
    // index 0 = surface; place from the structure end
    for (let k = n - 1; k >= 0; k--) {
      const it = S.items[k]; const len = A * it.frac; const c = off + it.t / 2;
      if (S.axis === 'wall') {                     // layers stacked along x, surface faces the viewer (+x)
        it.obj.position.set(c - total / 2, 0, (A - len) / 2); it.obj.children.forEach((ch) => setSize(ch, it.t, B, len, 'x'));
        it.lab.position.set(0, B / 2 + 0.08, len / 2 - 0.05);
      } else {                                     // floor: stacked up; ceiling: stacked down
        const y = S.axis === 'ceiling' ? total / 2 - c : c - total / 2;
        it.obj.position.set((A - len) / 2, y, 0); it.obj.children.forEach((ch) => setSize(ch, len, it.t, B, 'y'));
        it.lab.position.set(len / 2 + 0.07, 0, B / 2 - 0.05);
      }
      off += it.t + gap;
    }
    if (resetCam) {
      const r = 3.6 + total * 0.6;
      if (S.axis === 'wall') S.cam.position.set(r * 0.85, r * 0.35, r * 0.75);
      else if (S.axis === 'ceiling') S.cam.position.set(r * 0.7, -r * 0.55, r * 0.8);
      else S.cam.position.set(r * 0.7, r * 0.6, r * 0.8);
      S.ctl.target.set(0, 0, 0); S.ctl.update();
    }
  };
  function setSize(ch, x, y, z, axis) {
    if (ch.userData.bar !== undefined) {         // frame bars / pipes inside the ghost box
      const k = ch.userData.bar, f = (k - 1) * 0.33;
      if (ch.geometry.type === 'CylinderGeometry') { const d = Math.min(axis === 'x' ? x : y, 0.12); ch.scale.set(d, axis === 'x' ? y * 0.95 : z * 0.95, d); ch.rotation.set(axis === 'x' ? 0 : Math.PI / 2, 0, 0); ch.position.set(axis === 'x' ? 0 : f * x, 0, axis === 'x' ? f * z : 0); }
      else if (axis === 'x') { ch.scale.set(x * 0.9, y * 0.95, 0.05); ch.position.set(0, 0, f * z); }
      else { ch.scale.set(0.05, y * 0.9, z * 0.95); ch.position.set(f * x, 0, 0); }
      return;
    }
    if (ch.isMesh) { ch.scale.set(x, y, z); const m = ch.material.map; if (m) { m.repeat.set(1, 1); } }
  }
  S.highlight = (i, pin) => {
    S.items.forEach((it) => { const m = it.mesh.material; if (m.emissive) m.emissive.setHex(it.i === i ? 0x3a2a00 : 0x000000); it.lab.element.classList.toggle('on', it.i === i); });
    modal.querySelectorAll('.im-list li').forEach((li) => li.classList.toggle('on', +li.dataset.i === i));
    if (pin) { const li = modal.querySelector(`.im-list li[data-i="${i}"]`); if (li) li.scrollIntoView({ block: 'nearest' }); }
  };
  labels.domElement.addEventListener('pointerup', (e) => {
    const r = labels.domElement.getBoundingClientRect(); ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, S.cam); const hit = ray.intersectObjects(S.items.map((it) => it.mesh), false)[0];
    if (hit) { const it = S.items.find((x) => x.mesh === hit.object); if (it) S.highlight(it.i, true); }
  });
  S.start = () => {
    if (S.running) return; S.running = true;
    const tick = () => {
      if (!S.running) return;
      if (renderer.domElement.width !== Math.floor(W() * renderer.getPixelRatio())) { renderer.setSize(W(), H()); labels.setSize(W(), H()); S.cam.aspect = W() / H(); S.cam.updateProjectionMatrix(); }
      S.ctl.update(); renderer.render(scene, S.cam); labels.render(scene, S.cam); requestAnimationFrame(tick);
    };
    tick();
  };
  return S;
}

// ------------------------------------------------------------------ 6. shopping list
// ------------------------------------------------------------------ 6a. thumbnails of the furniture as it is in this 3D plan
const THUMBS = {}; let thumbR = null;
function partsFor(it) {
  const app = window.app; if (!app || !app.objects || !it.match) return [];
  const re = new RegExp(it.match, 'i');
  const hits = app.objects.filter((o) => re.test(o.name) && !(o.obj.parent && o.obj.parent.userData && re.test(o.obj.parent.name || '')));
  if (!hits.length) return [];
  const c0 = new THREE.Box3().setFromObject(hits[0].obj).getCenter(new THREE.Vector3());
  return hits.filter((h) => new THREE.Box3().setFromObject(h.obj).getCenter(new THREE.Vector3()).distanceTo(c0) < 1.7).map((h) => h.obj);   // first piece and its neighbours only
}
function thumb(k, w = 320, h = 240) {
  const it = SHOP && SHOP.items.find((x) => x.k === k); if (!it) return null;
  const key = k + '_' + (window.app && window.app.modelFile); if (THUMBS[key] !== undefined) return THUMBS[key];
  const parts = partsFor(it); if (!parts.length) { THUMBS[key] = null; return null; }
  if (!thumbR) { thumbR = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true }); thumbR.setPixelRatio(1); thumbR.toneMapping = THREE.ACESFilmicToneMapping; thumbR.toneMappingExposure = 1.05; }
  thumbR.setSize(w, h);
  const sc = new THREE.Scene(); sc.add(new THREE.HemisphereLight(0xffffff, 0xb9b2a6, 2.2));
  const d1 = new THREE.DirectionalLight(0xffffff, 2.2); d1.position.set(2, 4, 3); sc.add(d1);
  const d2 = new THREE.DirectionalLight(0xffffff, 0.8); d2.position.set(-3, 1, -2); sc.add(d2);
  const g = new THREE.Group(); sc.add(g);
  for (const p of parts) p.traverse((m) => { if (!m.isMesh) return; m.updateWorldMatrix(true, false); const c = new THREE.Mesh(m.geometry, m.userData._origMat || m.material); c.matrixAutoUpdate = false; c.matrix.copy(m.matrixWorld); g.add(c); });
  g.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(g); const ctr = box.getCenter(new THREE.Vector3()); const sz = box.getSize(new THREE.Vector3());
  // look from the middle of the room the piece stands in; flat things (art, panels) are seen square-on
  let room = null;
  for (const r of window.app.rooms || []) { const rb = r.box || (r.obj && new THREE.Box3().setFromObject(r.obj)); if (rb && ctr.x >= rb.min.x && ctr.x <= rb.max.x && ctr.z >= rb.min.z && ctr.z <= rb.max.z) { room = rb.getCenter(new THREE.Vector3()); break; } }
  if (!room) room = window.app.bbox ? window.app.bbox.getCenter(new THREE.Vector3()) : new THREE.Vector3();
  const dir = new THREE.Vector3(room.x - ctr.x, 0, room.z - ctr.z); if (dir.lengthSq() < 1e-3) dir.set(1, 0, 1); dir.normalize();
  const flat = Math.min(sz.x, sz.z) < 0.22 * Math.max(sz.x, sz.z);
  if (flat) { if (sz.x < sz.z) dir.set(Math.sign(dir.x) || 1, 0, 0); else dir.set(0, 0, Math.sign(dir.z) || 1); dir.applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.25); dir.y = 0.12; }
  else { dir.applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.6); dir.y = 0.45; }
  dir.normalize();
  const cam = new THREE.PerspectiveCamera(30, w / h, 0.01, 100); const rad = Math.max(0.25, sz.length() / 2);
  cam.position.copy(ctr).addScaledVector(dir, (rad / Math.sin((30 * Math.PI) / 360)) * 0.95); cam.lookAt(ctr);
  const clip = []; g.traverse((m) => { if (m.isMesh && m.material.clippingPlanes) { clip.push([m.material, m.material.clippingPlanes]); m.material.clippingPlanes = null; } });
  thumbR.render(sc, cam); const url = thumbR.domElement.toDataURL('image/png');
  for (const [m, c] of clip) m.clippingPlanes = c;
  THUMBS[key] = url; return url;
}
const ICON = { mesh: '🦟', downlight: '💡', cove: '〰️', generic: '🛒', ac: '❄️' };
function imgFor(it, cls = 'sh-img') {
  const u = ICON[it.k] ? null : thumb(it.k); const link = it.ex[0] ? it.ex[0].url : it.mid.url;
  return `<a class="${cls}" href="${link}" target="_blank" rel="noopener" title="${esc(T(L10N.openAmazon))}">${u ? `<img src="${u}" alt="${esc(T(it.n))}">` : `<span class="ph">${ICON[it.k] || '🛒'}</span>`}<span class="go">Amazon ↗</span></a>`;
}

function openShop() {
  if (!SHOP) return; ensureModal(); curMode = 'shop';
  modal.classList.remove('hidden'); modal.classList.add('shop'); if (three) three.running = false;
  modal.querySelector('.im-3d').style.display = 'none'; modal.querySelector('.im-pick').style.display = 'none';
  modal.querySelector('.im-title').textContent = T(L10N.shop).replace('🛒 ', '');
  modal.querySelector('.im-x').textContent = T(L10N.close);
  const names = (window.app?.objects || []).map((o) => o.name);
  const present = (it) => it.match && names.some((n) => new RegExp(it.match, 'i').test(n));
  const rows = (list) => list.map((it) => `<div class="sh-row">${imgFor(it)}<div class="sh-n"><b class="sh-open" data-k="${it.k}" title="${T(L10N.prodWhy)}">${esc(T(it.n))} ›</b>${it.qty > 1 ? ` <span class="q">× ${it.qty}</span>` : ''}<div class="sz">${esc(T(it.size))}</div>${it.why ? `<div class="sh-why">${esc(T(it.why))}</div>` : ''}${it.tip ? `<div class="sh-tip">⚠ ${esc(T(it.tip))}</div>` : ''}</div>
    <div class="sh-l">${shopLinks(it)}</div></div>`).join('');
  const a = SHOP.items.filter(present), b = SHOP.items.filter((it) => !present(it));
  const byRoom = (list) => Object.keys(SHOP.rooms || { all: ['', ''] }).map((r) => { const l = list.filter((it) => (it.room || 'all') === r); return l.length ? `<h5 class="sh-room">${esc(T((SHOP.rooms || {})[r] || ['', '']))}</h5>${rows(l)}` : ''; }).join('');
  modal.querySelector('.im-side').innerHTML = `<div class="im-note">${esc(T(SHOP.note))} ${esc(T(L10N.tapImg))}.</div>
    <h4>${T(L10N.inModel)}</h4>${byRoom(a)}${b.length ? `<h4>${T(L10N.also)}</h4>${rows(b)}` : ''}`;
  modal.querySelectorAll('.sh-open').forEach((el) => el.onclick = () => openProduct(SHOP.items.find((x) => x.k === el.dataset.k), 'why'));
}
let CMP = null; fetch(`./models/compare.json?v=${V}`).then((r) => r.json()).then((c) => { CMP = c; }).catch(() => {});
function optsHTML(it) {
  const d = CMP && CMP.picks && CMP.picks[it.k]; if (!d) return `<button class="small pr-cmp" style="margin-top:10px">📊 ${hi() ? 'तुलना तालिका' : 'Compare table'}</button>`;
  const tier = { b: [L10N.budget[0], L10N.budget[1]], m: [L10N.mid[0], L10N.mid[1]], p: ['Premium', 'प्रीमियम'] };
  const rows = (d.picks || []).map((p) => `<tr><td>${esc(T(tier[p.t]))}</td><td><a href="${p.url}" target="_blank" rel="noopener">${esc(p.n)}</a></td><td class="nw">${esc(p.price)}</td></tr>`).join('');
  const li2 = (a, c) => (a || []).map((x) => `<li class="${c}">${esc(T(x))}</li>`).join('');
  return `<h5 style="margin:12px 0 4px">${hi() ? 'लोग क्या ख़रीदते हैं (स्रोत लिंक)' : 'Options people buy (source links)'}</h5><table class="pr-opts">${rows}</table>
    ${(d.like || []).length || (d.bad || []).length ? `<h5 style="margin:10px 0 4px">${hi() ? 'मालिक क्या कहते हैं' : 'What owners say'}</h5><ul class="pc-pc">${li2(d.like, 'p')}${li2(d.bad, 'c')}</ul>` : ''}
    ${d.tip ? `<div class="im-why" style="margin-top:6px"><b>${hi() ? 'सुझाव' : 'Tip'}:</b> ${esc(T(d.tip))}</div>` : ''}
    <button class="small pr-cmp" style="margin-top:10px">📊 ${hi() ? 'तुलना तालिका में देखें' : 'See in the compare table'}</button>`;
}
// ------------------------------------------------------------------ 6b. one product: why, pros, cons, mistakes, alternatives, where to buy
let curProd = null;
function openProduct(it, tab = 'why') {
  if (!it) return; ensureModal(); curMode = 'product'; curProd = it;
  modal.classList.remove('hidden'); modal.classList.add('shop'); if (three) three.running = false;
  modal.querySelector('.im-3d').style.display = 'none'; modal.querySelector('.im-pick').style.display = 'none';
  modal.querySelector('.im-title').textContent = T(it.n); modal.querySelector('.im-x').textContent = T(L10N.close);
  modal.dataset.ptab = tab;
  const li = (arr) => `<ul>${(arr || []).map((x) => `<li>${esc(T(x))}</li>`).join('')}</ul>`;
  const tabs = `<div class="im-tabs">${[['why', L10N.tWhy], ['mist', ['Mistakes · options', 'ग़लतियाँ · विकल्प']]].map(([k, l]) => `<button class="${k === tab ? 'on' : ''}" data-ptab="${k}">${T(l)}</button>`).join('')}</div>`;
  const body = tab === 'why'
    ? `<div class="im-why"><b>${T(L10N.why)}:</b> ${esc(T(it.why || ''))}</div><div class="im-pc"><div class="p"><h5>${T(L10N.pros)}</h5>${li(it.pros)}</div><div class="c"><h5>${T(L10N.cons)}</h5>${li(it.cons)}</div></div>`
    : `<h5>⚠ ${T(L10N.mistP)}</h5><ol class="im-mist">${(it.mistakes || []).map((x) => `<li>${esc(T(x))}</li>`).join('')}</ol>${it.alt ? `<div class="im-why" style="margin-top:10px"><b>${T(L10N.alt)}:</b> ${esc(T(it.alt))}</div>` : ''}`;
  modal.querySelector('.im-side').innerHTML = `<div class="pr-top">${imgFor(it, 'sh-img pr-img')}<div><div class="sz"><b>${T(L10N.size)}:</b> ${esc(T(it.size))}${it.qty > 1 ? ` · × ${it.qty}` : ''}</div>
    ${SHOP.rooms && it.room ? `<div class="sz"><b>${T(L10N.room)}:</b> ${esc(T(SHOP.rooms[it.room]))}</div>` : ''}<div class="sh-l" style="margin-top:6px">${shopLinks(it)}</div></div></div>${tabs}${body}
    ${optsHTML(it)}<div class="im-note" style="margin-top:10px">${esc(T(SHOP.note))}</div>`;
  const cb = modal.querySelector('.pr-cmp'); if (cb) cb.onclick = () => { close(); window.compare?.openCompare('products', it.k); };
  modal.querySelectorAll('[data-ptab]').forEach((b) => b.onclick = () => openProduct(it, b.dataset.ptab));
}
// ------------------------------------------------------------------ 7. click card: walk around, click anything, choose what to see
let card = null, downAt = null;
function ensureCard() {
  if (card) return; card = document.createElement('div'); card.id = 'pickCard'; card.className = 'hidden'; document.getElementById('viewport').appendChild(card);
  card.addEventListener('pointerdown', (e) => e.stopPropagation());
}
function hideCard() { if (card) card.classList.add('hidden'); }
function showCard(o, x, y) {
  ensureCard();
  const it0 = shopFor(o), id = it0 ? null : layerIdFor(o), it = it0 || (id ? null : genericFor(o)), d = id ? DATA.layers[id] : null;
  if (!d && !it) { hideCard(); return; }
  const tip = document.getElementById('tapInfo'); if (tip) tip.classList.add('hidden');
  const title = it ? T(it.n) : T(d.title);
  card.innerHTML = `<div class="pc-h"><b>${esc(title)}</b><button class="x" title="${T(L10N.close)}">✕</button></div>
    ${it ? imgFor(it, 'pc-img') : ''}
    ${d ? `<div class="pc-chain">${d.layers.slice(0, 4).map((l) => esc(T(l.n).replace(/,.*$/, ''))).join(' → ')}${d.layers.length > 4 ? ' → …' : ''}</div>` : ''}
    ${d && d.why ? `<div class="pc-why">${esc(T(d.why))}</div>` : ''}
    ${!d && it && it.why ? `<div class="pc-why">${esc(T(it.why))}</div>` : ''}${it ? pcHTML(it, 2) : ''}${it && it.tip ? `<div class="pc-tip">⚠ ${esc(T(it.tip))}</div>` : ''}
    <div class="pc-b">${d ? `<button data-a="layers">${T(L10N.breakdown)}</button><button data-a="why">${T(L10N.tWhy)}</button><button data-a="mist">⚠ ${T(L10N.tMist)}</button>` : ''}
    ${it && !it.generic ? `<button data-p="why" class="accent">${T(L10N.prodWhy)}</button><button data-p="mist">${T(L10N.prodMist)}</button>` : ''}
    ${it ? (it.generic ? `<a class="buy m" href="${it.mid.url}" target="_blank" rel="noopener">${T(L10N.search)}</a>` : `<a class="buy b" href="${it.budget.url}" target="_blank" rel="noopener">🛒 ${T(L10N.budget)} ${it.budget.band}</a><a class="buy m" href="${it.mid.url}" target="_blank" rel="noopener">🛒 ${T(L10N.mid)} ${it.mid.band}</a>`) : ''}
    <button data-a="details">${T(L10N.details)}</button></div>`;
  card.querySelector('.x').onclick = hideCard;
  card.querySelectorAll('[data-p]').forEach((b) => b.onclick = () => { hideCard(); openProduct(it, b.dataset.p); });
  card.querySelectorAll('[data-a]').forEach((b) => b.onclick = () => {
    const a = b.dataset.a; hideCard();
    if (a === 'details') { if (document.body.classList.contains('no-right')) document.getElementById('rightTab')?.click(); document.getElementById('inspector')?.scrollIntoView({ block: 'nearest' }); }
    else openLayers(id, a);
  });
  const vp = document.getElementById('viewport').getBoundingClientRect();
  card.classList.remove('hidden');
  const cw = card.offsetWidth, ch = card.offsetHeight;
  card.style.left = Math.min(Math.max(8, x - vp.left + 14), vp.width - cw - 8) + 'px';
  card.style.top = Math.min(Math.max(8, y - vp.top + 14), vp.height - ch - 8) + 'px';
}
function hookCanvas() {
  const cv = window.viewer && window.viewer.renderer && window.viewer.renderer.domElement; if (!cv) return setTimeout(hookCanvas, 300);
  cv.addEventListener('pointerdown', (e) => { downAt = { x: e.clientX, y: e.clientY }; hideCard(); });
  cv.addEventListener('pointerup', (e) => {
    if (!downAt || Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y) > 6 || (e.pointerType === 'mouse' && e.button !== 0)) return;
    const walking = !!(window.viewer.walk && window.viewer.walk.active), sideHidden = document.body.classList.contains('no-right') || document.body.classList.contains('simple');
    setTimeout(() => {                                                          // main.js selects on the same click first
      const o = window.app && window.app.selected; if (!o) return hideCard();
      const imm = window.viewer.imm; if (imm && imm.isInteractive && imm.isInteractive(o)) return hideCard();   // doors and windows just open
      showCard(o, e.clientX, e.clientY);
    }, 30);
  });
}
hookCanvas();
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideCard(); });

window.inside = { openLayers, openShop, openProduct, layerIdFor, shopFor, productFor, thumb, showCard };
