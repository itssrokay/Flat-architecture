// MyFlat Viewer - displays the architecture GLB exported from Blender.
// Nothing here re-creates architecture: every wall/door/room comes from the model.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { CONFIG } from './config.js?v=9';
import { Walkthrough } from './walk.js?v=9';
import { setupImmersive } from './immersive.js?v=9';
import { setupExtras } from './extras.js?v=9';
import { setupLearn } from './learn.js?v=9';
// bump together with the ?v= in index.html and the imports above whenever the viewer or models change,
// so browsers never mix a new page with old cached scripts or models
const BUILD = '9';

const $ = (id) => document.getElementById(id);
const FT = 0.3048;

// ------------------------------------------------------------------ formatting
export function fmtFt(ft) {
  if (ft == null || isNaN(ft)) return '–';
  const neg = ft < 0; ft = Math.abs(ft);
  let whole = Math.floor(ft), inch = Math.round((ft - whole) * 12 * 2) / 2;
  if (inch >= 12) { whole += 1; inch -= 12; }
  const s = whole ? (inch ? `${whole}' ${inch}"` : `${whole}'`) : `${inch}"`;
  return (neg ? '-' : '') + s;
}
const fmtM = (m) => `${(m / FT).toFixed(2)} ft`;

// ------------------------------------------------------------------ app state
const app = {
  model: null, modelFile: null, manifest: null,
  objects: [], edges: [], // {obj, name, cat, status}
  meshes: [],             // selectable/visible meshes
  byCat: new Map(),       // cat -> [object3D]
  catVisible: {},
  rooms: [],              // {name, floor, box, floorY, center, vps}
  materials: new Map(),   // original material -> {opacity, transparent}
  planObj: null, planMat: null,
  bbox: new THREE.Box3(), center: new THREE.Vector3(), size: 1, wallTop: 3.05,
  statusMode: false, debugMode: false, labelsOn: true, planMode: false, edgesOn: true,
  selected: null, ortho: false,
  sectionPlane: new THREE.Plane(new THREE.Vector3(0, -1, 0), 1e6),
  tween: null,
};
window.app = app; // handy for debugging in the browser console

// ------------------------------------------------------------------ renderer / scene
const host = $('canvasHost');
const LOWQ = new URLSearchParams(location.search).has('lowq');   // ?lowq=1 -> no shadows (slow/old GPUs)
const renderer = new THREE.WebGLRenderer({ antialias: !LOWQ, preserveDrawingBuffer: true });
renderer.setPixelRatio(LOWQ ? 1 : Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = !LOWQ;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.localClippingEnabled = true;
host.appendChild(renderer.domElement);
const labelRenderer = new CSS2DRenderer();
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.inset = '0';
labelRenderer.domElement.style.pointerEvents = 'none';
host.appendChild(labelRenderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#e9ecef');
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.45;
const hemi = new THREE.HemisphereLight('#ffffff', '#b9b3a8', 1.1); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffffff', 1.6);
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);

const persp = new THREE.PerspectiveCamera(60, 1, 0.1, 500);
const orthoCam = new THREE.OrthographicCamera(-10, 10, 10, -10, -200, 500);
let camera = persp;
const controls = new OrbitControls(persp, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.09; controls.screenSpacePanning = true;
// never orbit under the ground (that is where the "all white" views came from); keep a small gap to the pivot
controls.maxPolarAngle = Math.PI * 0.495; controls.minDistance = 0.3; controls.maxDistance = 120;
controls.zoomToCursor = true;           // the wheel zooms towards what is under the mouse, so you can travel with it
controls.rotateSpeed = 0.7;

// Solid objects are drawn one-sided. If the camera ends up inside a wall, slab or ceiling you simply see
// through it instead of a white screen. Thin / soft / see-through things stay two-sided.
const _sz = new THREE.Vector3();
function fixSides(meshes, register) {
  const need = new Map();   // material -> [meshes that need two-sided]
  const solid = new Map();  // material -> [meshes that can be one-sided]
  for (const o of meshes) {
    const cat = catOf(o), mat = o.material; if (!mat || Array.isArray(mat)) continue;
    if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
    o.geometry.boundingBox.getSize(_sz).multiply(o.getWorldScale(new THREE.Vector3()));
    const thin = Math.min(Math.abs(_sz.x), Math.abs(_sz.y), Math.abs(_sz.z)) < 0.03;
    const dbl = thin || mat.transparent || mat.opacity < 1 || ['soft_furnishing', 'plan_reference', 'context', 'plants'].includes(cat);
    const m = dbl ? need : solid; if (!m.has(mat)) m.set(mat, []); m.get(mat).push(o);
  }
  for (const [mat, list] of solid) { mat.side = THREE.FrontSide; mat.needsUpdate = true; }
  for (const [mat, list] of need) {
    let use = mat;
    if (solid.has(mat)) { use = mat.clone(); use.clippingPlanes = mat.clippingPlanes; register && register(use, mat); }
    use.side = THREE.DoubleSide; use.needsUpdate = true;
    for (const o of list) { o.material = use; o.userData._origMat = use; o.userData._dbl = true; }
  }
}

const labelsGroup = new THREE.Group(); scene.add(labelsGroup);
const debugGroup = new THREE.Group(); debugGroup.visible = false; scene.add(debugGroup);
const selBox = new THREE.Box3Helper(new THREE.Box3(), 0xff2d55); selBox.visible = false; scene.add(selBox);
const edgeMat = new THREE.LineBasicMaterial({ color: '#2b3036', transparent: true, opacity: 0.55, clippingPlanes: [app.sectionPlane] });

const walk = new Walkthrough({ app, persp, renderer, controls, CONFIG, onInfo: (t) => { $('walkInfo').textContent = t; } });

function resize() {
  const w = host.clientWidth, h = host.clientHeight;
  renderer.setSize(w, h, false); labelRenderer.setSize(w, h);
  persp.aspect = w / h; persp.updateProjectionMatrix();
  setOrthoFrustum(orthoCam.userData.halfH || 10);
}
function setOrthoFrustum(halfH) {
  const a = host.clientWidth / Math.max(1, host.clientHeight);
  orthoCam.userData.halfH = halfH;
  orthoCam.left = -halfH * a; orthoCam.right = halfH * a; orthoCam.top = halfH; orthoCam.bottom = -halfH;
  orthoCam.updateProjectionMatrix();
}
window.addEventListener('resize', resize);

// ------------------------------------------------------------------ camera helpers
function useCamera(ortho) {
  if (app.ortho === ortho && camera === (ortho ? orthoCam : persp)) return;
  const from = camera, to = ortho ? orthoCam : persp;
  to.position.copy(from.position); to.quaternion.copy(from.quaternion);
  if (ortho) {
    const d = from.position.distanceTo(controls.target);
    setOrthoFrustum(Math.max(2, d * Math.tan(THREE.MathUtils.degToRad(persp.fov / 2))));
    orthoCam.zoom = 1; orthoCam.updateProjectionMatrix();
  }
  camera = to; app.ortho = ortho; controls.object = to; controls.update();
  $('projBtn').textContent = ortho ? 'Ortho' : 'Persp';
  $('projBtn').classList.toggle('on', ortho);
}

// smooth fly-to. view = {pos:Vector3, target:Vector3, ortho?:bool, halfH?:number}
function flyTo(view, dur = 0.9) {
  if (walk.active) walk.exit();
  app.pendingWalk = null;
  useCamera(!!view.ortho);
  if (view.ortho && view.halfH) { setOrthoFrustum(view.halfH); orthoCam.zoom = 1; orthoCam.updateProjectionMatrix(); }
  app.tween = { start: performance.now(), dur, p0: camera.position.clone(), t0: controls.target.clone(), p1: view.pos.clone(), t1: view.target.clone() };
}
function stepTween(dt) {
  const tw = app.tween; if (!tw) return;
  tw.t = Math.min(1, (performance.now() - tw.start) / 1000 / tw.dur);
  const e = tw.t < .5 ? 4 * tw.t ** 3 : 1 - (-2 * tw.t + 2) ** 3 / 2;
  camera.position.lerpVectors(tw.p0, tw.p1, e); controls.target.lerpVectors(tw.t0, tw.t1, e);
  if (tw.t >= 1) {
    app.tween = null;
    if (app.pendingWalk) { const pw = app.pendingWalk; app.pendingWalk = null; walk.enter(pw.pos.clone(), pw.target.clone()); }
  }
}

function presetView(name) {
  const c = app.center, D = app.size * 1.6, halfH = app.size * 0.62, y = app.bbox.min.y + 1.5;
  const views = {
    top:   { pos: new THREE.Vector3(c.x, c.y + D * 2, c.z + 0.001), target: c.clone(), ortho: true, halfH },
    north: { pos: new THREE.Vector3(c.x, y, c.z - D), target: new THREE.Vector3(c.x, y, c.z), ortho: app.ortho, halfH: halfH * 0.7 },
    south: { pos: new THREE.Vector3(c.x, y, c.z + D), target: new THREE.Vector3(c.x, y, c.z), ortho: app.ortho, halfH: halfH * 0.7 },
    east:  { pos: new THREE.Vector3(c.x + D, y, c.z), target: new THREE.Vector3(c.x, y, c.z), ortho: app.ortho, halfH: halfH * 0.7 },
    west:  { pos: new THREE.Vector3(c.x - D, y, c.z), target: new THREE.Vector3(c.x, y, c.z), ortho: app.ortho, halfH: halfH * 0.7 },
    iso:   { pos: new THREE.Vector3(c.x - app.size * 0.85, c.y + app.size * 0.9, c.z + app.size * 1.05), target: c.clone(), ortho: false },
  };
  const v = views[name]; if (!v) return;
  if (name === 'top') setCat('roof', false);   // a plan view is only useful without the roof
  flyTo(v);
  document.querySelectorAll('#viewButtons button').forEach(b => b.classList.toggle('active', b.dataset.view === name));
}

// ------------------------------------------------------------------ model loading
async function loadModelList() {
  let list = { default: CONFIG.defaultModel, models: [{ file: CONFIG.defaultModel, label: CONFIG.defaultModel }] };
  try { const r = await fetch(CONFIG.modelsIndex, { cache: 'no-store' }); if (r.ok) list = await r.json(); } catch (e) { /* use default */ }
  app.modelList = list;
  try { if (list.designNotes) { const r = await fetch(CONFIG.modelDir + list.designNotes, { cache: 'no-store' }); if (r.ok) app.designNotes = await r.json(); } } catch (e) { }
  buildDesignPanel(list);
  const sel = $('modelSelect'); sel.innerHTML = '';
  for (const m of list.models) { const o = document.createElement('option'); o.value = m.file; o.textContent = m.label || m.file; o.dataset.manifest = m.manifest || ''; sel.appendChild(o); }
  const urlModel = new URLSearchParams(location.search).get('model');
  const file = urlModel || list.default || list.models[0]?.file;
  if (urlModel && ![...sel.options].some(o => o.value === urlModel)) { const o = document.createElement('option'); o.value = urlModel; o.textContent = urlModel; sel.appendChild(o); }
  sel.value = file;
  sel.onchange = () => { const u = new URL(location); u.searchParams.set('model', sel.value); history.replaceState(null, '', u); loadModel(sel.value); };
  return file;
}

function modelEntry(file) { return (app.modelList?.models || []).find(m => m.file === file) || { file }; }
function buildDesignPanel(list) {
  const p = $('designPanel'); p.innerHTML = '';
  const groups = [['interior', 'Room 1 interior'], ['architecture', 'Architecture only']];
  for (const [g, title] of groups) {
    const items = list.models.filter(m => (m.group || 'architecture') === g);
    if (!items.length) continue;
    const h = document.createElement('div'); h.className = 'grp'; h.textContent = title; p.appendChild(h);
    for (const m of items) {
      const b = document.createElement('button'); b.dataset.file = m.file;
      const note = m.design && app.designNotes?.[m.design];
      const sub = (note ? note.title.split('·')[1]?.trim() || '' : (m.label || '').replace(/\(.*\)/, '')) + (note?.budget ? ` · ${note.budget.total}` : '');
      b.innerHTML = `${m.short || m.label}<small>${g === 'interior' ? sub : (m.label || '')}</small>`;
      b.onclick = () => switchModel(m.file);
      p.appendChild(b);
    }
  }
  const cs = $('compareSelect'); cs.innerHTML = '<option value="">— off —</option>';
  for (const m of list.models) { const o = document.createElement('option'); o.value = m.file; o.textContent = m.label || m.file; cs.appendChild(o); }
  cs.onchange = () => setCompare(cs.value);
}
function switchModel(file) {
  const u = new URL(location); u.searchParams.set('model', file); history.replaceState(null, '', u);
  $('modelSelect').value = file; loadModel(file);
}
function updateDesignUI() {
  document.querySelectorAll('#designPanel button').forEach(b => b.classList.toggle('cur', b.dataset.file === app.modelFile));
  const m = modelEntry(app.modelFile); const n = m.design && app.designNotes?.[m.design]; const el = $('designNotes');
  if (!n) { el.classList.add('hidden'); return; }
  el.classList.remove('hidden');
  el.innerHTML = `<div class="t">${n.title}</div><div class="tag">${n.tagline}</div>` +
    `<details ${m.design === 'DEFAULT' ? 'open' : ''}><summary>${m.design === 'DEFAULT' ? 'Why this is the default' : 'Concept'}</summary><div class="why">${n.why}</div></details>` +
    (n.budget ? `<details class="budget" open><summary>Budget · ${n.budget.total}</summary><table>` +
      n.budget.rows.map(r => `<tr><td>${r[0]}<div class="bd">${r[1]}</div></td><td class="amt">${r[2]}</td></tr>`).join('') +
      `<tr class="tot"><td>Total</td><td class="amt">${n.budget.total}</td></tr></table>` +
      (n.budget.note ? `<div class="bnote">${n.budget.note}</div>` : '') + (n.budget.savings ? `<div class="bnote"><b>If it runs over:</b> ${n.budget.savings.replace(/^If it runs over:\s*/, '')}</div>` : '') + `</details>` : '') +
    Object.entries(n.sections).map(([k, v]) => `<details><summary>${k}</summary><div>${v}</div></details>`).join('') +
    (n.schedule ? `<details class="sched" open><summary>Material & finish schedule</summary>` + n.schedule.map(g =>
      `<div class="sg">${g.area}</div><table>${g.items.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('')}</table>`).join('') + `</details>` : '');
}

function disposeModel() {
  if (!app.model) return;
  scene.remove(app.model);
  app.model.traverse(o => { if (o.isMesh) { o.geometry.dispose(); } });
  labelsGroup.clear(); debugGroup.clear();
  app.edges.forEach(e => e.geometry.dispose());
  Object.assign(app, { objects: [], edges: [], meshes: [], byCat: new Map(), rooms: [], materials: new Map(), planObj: null, selected: null });
  selBox.visible = false;
}

function catOf(o) { for (let p = o; p; p = p.parent) if (p.userData && p.userData.category) return p.userData.category; return 'other'; }
function statusOf(o) { for (let p = o; p; p = p.parent) if (p.userData && p.userData.status) return p.userData.status; return null; }

async function loadModel(file) {
  $('loading').classList.remove('hidden'); $('loading').textContent = `Loading ${file}…`;
  app.ready = false;
  const keep = app.model ? { pos: camera.position.clone(), target: controls.target.clone(), ortho: app.ortho, zoom: orthoCam.zoom, halfH: orthoCam.userData.halfH, sel: app.selected?.name } : null;
  disposeModel();
  app.modelFile = file;
  const url = CONFIG.modelDir + file;
  let gltf;
  try { gltf = await new GLTFLoader().loadAsync(url + '?v=' + BUILD); }
  catch (e) { $('loading').textContent = `Could not load ${url}. Is the local server running from the MyFlat_Viewer folder? (${e.message || e})`; return; }
  const manifestFile = modelEntry(file).manifest || file.replace(/\.glb$/i, '.manifest.json');
  app.manifest = null;
  try { const r = await fetch(CONFIG.modelDir + manifestFile, { cache: 'no-store' }); if (r.ok) app.manifest = await r.json(); } catch (e) { }

  const root = gltf.scene; root.name = file; app.model = root; scene.add(root);
  root.updateMatrixWorld(true);

  root.traverse(o => {
    if (o === root) return;
    const cat = catOf(o);
    const own = !!(o.userData && o.userData.category);
    if (own) app.objects.push({ obj: o, name: o.name, cat, status: o.userData.status || null });
    if (own) { if (!app.byCat.has(cat)) app.byCat.set(cat, []); app.byCat.get(cat).push(o); }
    if (o.isMesh) {
      if (!app.materials.has(o.material)) app.materials.set(o.material, { opacity: o.material.opacity, transparent: o.material.transparent });
      o.userData._origMat = o.material;
      o.material.clippingPlanes = [app.sectionPlane];
      o.castShadow = !['plan_reference', 'context'].includes(cat) && !o.material.transparent;
      o.receiveShadow = true;
      if (cat !== CONFIG.planCategory) app.meshes.push(o);
      if (![CONFIG.planCategory, 'context'].includes(cat)) {
        const e = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 28), edgeMat);
        e.name = o.name + '__edges'; e.raycast = () => {}; e.userData.isEdge = true; o.add(e); app.edges.push(e);
      }
    }
  });

  fixSides(app.meshes, (clone, src) => app.materials.set(clone, app.materials.get(src)));

  // plan overlay (the reference plane saved in Blender, already aligned to the model)
  app.planObj = root.getObjectByName(CONFIG.planOverlayName) || (app.byCat.get(CONFIG.planCategory) || [])[0] || null;
  if (app.planObj) {
    const src = app.planObj.material;
    app.planMat = new THREE.MeshBasicMaterial({ map: src.map, transparent: true, opacity: +$('planOpacity').value, side: THREE.DoubleSide, depthWrite: false });
    if (app.planMat.map) app.planMat.map.colorSpace = THREE.SRGBColorSpace;
    app.planObj.traverse(o => { if (o.isMesh) { o.material = app.planMat; o.renderOrder = 10; o.castShadow = false; o.receiveShadow = false; } });
    app.planObj.userData._baseY = app.planObj.position.y;
    app.planObj.visible = false;
  }

  // bounds of the architecture (excluding ground + plan)
  app.bbox.makeEmpty();
  for (const m of app.meshes) { const c = catOf(m); if (c !== 'context') app.bbox.expandByObject(m); }
  app.bbox.getCenter(app.center); const s = new THREE.Vector3(); app.bbox.getSize(s); app.size = Math.max(s.x, s.z);
  const walls = app.byCat.get('walls') || [];
  const wb = new THREE.Box3(); walls.forEach(w => wb.expandByObject(w)); app.wallTop = wb.isEmpty() ? app.bbox.max.y : wb.max.y;
  sun.position.set(app.center.x - 12, app.center.y + 25, app.center.z + 18); sun.target.position.copy(app.center);
  const sc = sun.shadow.camera; const r = app.size * 0.75; sc.left = -r; sc.right = r; sc.top = r; sc.bottom = -r; sc.near = 1; sc.far = 80; sc.updateProjectionMatrix();
  controls.maxDistance = app.size * 6; persp.far = app.size * 20; persp.updateProjectionMatrix();

  buildRooms(); buildCategoryToggles(); buildRoomList(); buildDebug(); buildLegend(); updateObjList();
  applyVisibility(); applyMaterials(); setSection(); setPlan();
  $('sectionRange').max = (app.bbox.max.y + 0.3).toFixed(2);

  // integrity check against the export manifest
  let check = '';
  if (app.manifest) {
    const names = new Set(); root.traverse(o => names.add(o.name));
    const missing = app.manifest.objects.filter(o => !names.has(o.name));
    check = missing.length ? ` · ⚠ ${missing.length} objects in manifest missing: ${missing.slice(0, 4).map(m => m.name).join(', ')}` : ` · ${app.manifest.object_count}/${app.manifest.object_count} exported objects present ✓`;
    app.missing = missing;
  }
  app.statusText = `${file} · ${app.objects.length} named objects${check}` + (app.manifest ? ` · exported ${app.manifest.exported} from ${app.manifest.source_blend}` : '');
  $('loading').classList.add('hidden');
  resize();
  if (keep) {            // switching models: keep the exact same camera so designs can be compared
    useCamera(keep.ortho); camera.position.copy(keep.pos); controls.target.copy(keep.target);
    if (keep.ortho) { setOrthoFrustum(keep.halfH); orthoCam.zoom = keep.zoom; orthoCam.updateProjectionMatrix(); }
    controls.update();
    if (keep.sel) { const o = root.getObjectByName(keep.sel); if (o) select(o); }
  } else {
    presetView('iso'); camera.position.copy(app.tween.p1); controls.target.copy(app.tween.t1); app.tween = null;
    const sv = modelEntry(file).startView;
    if (sv) { const [rn, i] = sv.split(':'); const r = app.rooms.find(x => x.name === rn); const vp = r && r.vps[+i || 0];
      if (vp) { useCamera(false); camera.position.copy(vp.pos); controls.target.copy(vp.target); controls.update();
        if (!vp.roofOff && !CONFIG.startInOverview) walk.enter(vp.pos.clone(), vp.target.clone()); } }
  }
  imm.onModel(root); ex.onModel(root);
  if (learnApi) learnApi.onModel();
  updateDesignUI();
  if (app.compare) $('capL').innerHTML = `<b>${modelEntry(file).label || file}</b>`;
  app.ready = true;
}

// ------------------------------------------------------------------ rooms & viewpoints
const _ray = new THREE.Raycaster();
function hitsObject(obj, x, z, yFrom) {
  _ray.set(new THREE.Vector3(x, yFrom, z), new THREE.Vector3(0, -1, 0)); _ray.far = 10;
  return _ray.intersectObject(obj, true).length > 0;
}
function buildRooms() {
  const roomObjs = app.objects.filter(o => o.obj.userData.room);
  for (const r of roomObjs) {
    const box = new THREE.Box3().setFromObject(r.obj);
    const floorY = box.max.y; const c = box.getCenter(new THREE.Vector3());
    const room = { name: r.obj.userData.room, floor: r.obj, box, floorY, center: new THREE.Vector3(c.x, floorY, c.z), vps: [] };
    // label: prefer the room centre if it lies on the floor, else a point that does
    let lx = c.x, lz = c.z;
    if (!hitsObject(r.obj, lx, lz, floorY + 1)) {
      outer: for (let fx = 0.3; fx <= 0.7; fx += 0.1) for (let fz = 0.3; fz <= 0.7; fz += 0.1) {
        const x = box.min.x + (box.max.x - box.min.x) * fx, z = box.min.z + (box.max.z - box.min.z) * fz;
        if (hitsObject(r.obj, x, z, floorY + 1)) { lx = x; lz = z; break outer; }
      }
    }
    room.labelPos = new THREE.Vector3(lx, floorY + 1.1, lz);
    const div = document.createElement('div'); div.className = 'lbl-room'; div.textContent = room.name.toUpperCase();
    const l = new CSS2DObject(div); l.position.copy(room.labelPos); l.visible = app.labelsOn; labelsGroup.add(l);
    room.vps = makeViewpoints(room);
    app.rooms.push(room);
  }
  const order = CONFIG.roomOrder;
  app.rooms.sort((a, b) => (order.indexOf(a.name) + 1 || 99) - (order.indexOf(b.name) + 1 || 99));
}

function makeViewpoints(room) {
  const b = room.box, eye = room.floorY + CONFIG.eyeHeight;
  const w = b.max.x - b.min.x, d = b.max.z - b.min.z;
  const ins = Math.min(0.45, w * 0.18, d * 0.18);
  const vps = [];
  for (const v of (CONFIG.viewpoints[room.name] || []))
    vps.push({ name: v.name, pos: new THREE.Vector3(...v.pos), target: new THREE.Vector3(...v.target) });
  // corners (north = -Z, east = +X); only if the corner is really inside this room
  const corners = { SW: [b.min.x + ins, b.max.z - ins], NE: [b.max.x - ins, b.min.z + ins], NW: [b.min.x + ins, b.min.z + ins], SE: [b.max.x - ins, b.max.z - ins] };
  const opp = { SW: 'NE', NE: 'SW', NW: 'SE', SE: 'NW' };
  for (const k of ['SW', 'NE', 'SE', 'NW']) {
    const [x, z] = corners[k];
    if (!hitsObject(room.floor, x, z, room.floorY + 1)) continue;
    const [tx, tz] = corners[opp[k]];
    vps.push({ name: `From ${k} corner`, pos: new THREE.Vector3(x, eye, z), target: new THREE.Vector3(tx, eye - 0.25, tz) });
  }
  const c = room.center;
  if (hitsObject(room.floor, c.x, c.z, room.floorY + 1)) {
    const along = w >= d ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 0, -1);
    vps.push({ name: 'Centre', pos: new THREE.Vector3(c.x, eye, c.z).addScaledVector(along, -0.3), target: new THREE.Vector3(c.x, eye - 0.2, c.z).addScaledVector(along, 3) });
  }
  const s = Math.max(w, d);
  vps.push({ name: 'From above (roof off)', pos: new THREE.Vector3(c.x, room.floorY + Math.max(6, s * 1.4), c.z + s * 0.8), target: c.clone(), roofOff: true });
  return vps;
}

// Room viewpoints at eye level put you *inside* (walk mode: drag to look, WASD / wheel to move).
// "From above" viewpoints stay in the overview (orbit) camera.
function goRoomVp(room, vp, inside = true) {
  if (vp.roofOff) setCat('roof', false);
  flyTo({ pos: vp.pos, target: vp.target, ortho: false });
  app.pendingWalk = (inside && !vp.roofOff) ? { pos: vp.pos, target: vp.target } : null;
  if (app.pendingWalk && app.catVisible.roof === false) setCat('roof', true);   // inside you want a ceiling over your head
  app.lastRoom = room.name;
}
// double-click on a floor in the overview: go and stand there, looking the way the camera was looking
function goToPoint(p) {
  const look = new THREE.Vector3().subVectors(p, camera.position).setY(0);
  if (look.lengthSq() < 1e-4) look.set(0, 0, -1);
  look.normalize();
  const pos = new THREE.Vector3(p.x, p.y + CONFIG.eyeHeight, p.z);
  const target = pos.clone().addScaledVector(look, 3);
  // back off so the flight ends looking at the spot, then step in
  flyTo({ pos, target, ortho: false }, 0.8);
  app.pendingWalk = { pos, target };
  if (app.catVisible.roof === false) setCat('roof', true);
}
function overview() {
  app.pendingWalk = null;
  if (walk.active) walk.exit();
  presetView('iso');
}

function buildRoomList() {
  const list = $('roomList'); list.innerHTML = '';
  for (const room of app.rooms) {
    const el = document.createElement('div'); el.className = 'room';
    el.innerHTML = `<div class="room-head"><button class="go">${room.name}</button><button class="more" title="More viewpoints">▸</button></div><div class="vps"></div>`;
    const vps = el.querySelector('.vps');
    room.vps.forEach(vp => { const b = document.createElement('button'); b.textContent = vp.name; b.onclick = () => goRoomVp(room, vp); vps.appendChild(b); });
    el.querySelector('.go').onclick = () => { goRoomVp(room, room.vps[0]); el.classList.add('open'); el.querySelector('.more').textContent = '▾'; };
    el.querySelector('.more').onclick = () => { el.classList.toggle('open'); el.querySelector('.more').textContent = el.classList.contains('open') ? '▾' : '▸'; };
    list.appendChild(el);
  }
  if (!app.rooms.length) list.innerHTML = '<div class="hint">This model has no objects tagged with a room.</div>';
}

// ------------------------------------------------------------------ visibility
function allCats() {
  const known = CONFIG.categories.map(c => c.key);
  const extra = [...app.byCat.keys()].filter(k => !known.includes(k) && k !== CONFIG.planCategory);
  return [...CONFIG.categories.filter(c => app.byCat.has(c.key)), ...extra.map(k => ({ key: k, label: k.replace(/_/g, ' ') }))];
}
function buildCategoryToggles() {
  const box = $('catToggles'); box.innerHTML = '';
  for (const c of allCats()) {
    if (!(c.key in app.catVisible)) app.catVisible[c.key] = true;
    const n = (app.byCat.get(c.key) || []).filter(o => !o.parent || !o.parent.userData.category).length;
    const chip = document.createElement('span'); chip.className = 'chip'; chip.dataset.cat = c.key;
    chip.innerHTML = `${c.label}<span class="n">${n}</span>`;
    chip.onclick = () => setCat(c.key, !app.catVisible[c.key]);
    box.appendChild(chip);
  }
}
function setCat(key, on) { app.catVisible[key] = on; applyVisibility(); }
function applyVisibility() {
  for (const [cat, objs] of app.byCat) {
    if (cat === CONFIG.planCategory) continue;
    const on = app.catVisible[cat] !== false;
    for (const o of objs) {
      // an object is shown if its own category is on; children with their own category decide for themselves
      o.visible = on;
    }
  }
  if (app.compare) for (const [cat, objs] of app.compare.byCat) for (const o of objs) o.visible = cat !== CONFIG.planCategory && app.catVisible[cat] !== false;
  document.querySelectorAll('#catToggles .chip').forEach(ch => ch.classList.toggle('on', app.catVisible[ch.dataset.cat] !== false));
  const roofOn = app.catVisible.roof !== false;
  $('roofBtn').classList.toggle('on', roofOn); $('roofBtn').textContent = roofOn ? 'Roof ON' : 'Roof OFF';
  updateDebugLabels();
}

// ------------------------------------------------------------------ materials: status / opacity / selection
const statusMats = {};
function statusMat(st, dbl) {
  const key = (st || '_none') + (dbl ? '_2' : '');
  if (!statusMats[key]) {
    const col = (CONFIG.status[st] || CONFIG.noStatus).color;
    statusMats[key] = new THREE.MeshStandardMaterial({ color: col, roughness: 0.8, metalness: 0, side: dbl ? THREE.DoubleSide : THREE.FrontSide, clippingPlanes: [app.sectionPlane] });
  }
  return statusMats[key];
}
function applyMaterials() {
  const op = +$('modelOpacity').value;
  for (const m of app.meshes) {
    const mat = app.statusMode ? statusMat(statusOf(m), m.userData._dbl) : m.userData._origMat;
    m.material = mat;
  }
  const mats = [...app.materials.keys(), ...Object.values(statusMats)];
  for (const mat of mats) {
    const orig = app.materials.get(mat) || { opacity: 1, transparent: false };
    mat.opacity = orig.opacity * op; mat.transparent = orig.transparent || op < 0.999; mat.depthWrite = !(orig.transparent) ; mat.needsUpdate = true;
  }
  $('statusBtn').classList.toggle('on', app.statusMode); $('legend').classList.toggle('hidden', !app.statusMode);
}
function buildLegend() {
  const counts = {};
  for (const o of app.objects) { const k = o.status || '_none'; counts[k] = (counts[k] || 0) + 1; }
  let html = '<b>Status (from Blender)</b>';
  for (const [k, v] of Object.entries(CONFIG.status)) if (counts[k]) html += `<div class="li"><span class="sw" style="background:${v.color}"></span>${v.label}<span class="n">${counts[k]}</span></div>`;
  for (const k of Object.keys(counts)) if (k !== '_none' && !CONFIG.status[k]) html += `<div class="li"><span class="sw" style="background:${CONFIG.noStatus.color}"></span>${k}<span class="n">${counts[k]}</span></div>`;
  if (counts._none) html += `<div class="li"><span class="sw" style="background:${CONFIG.noStatus.color}"></span>${CONFIG.noStatus.label}<span class="n">${counts._none}</span></div>`;
  $('legend').innerHTML = html;
}

// ------------------------------------------------------------------ section & plan
function setSection() {
  const on = $('sectionChk').checked, h = +$('sectionRange').value;
  app.sectionPlane.constant = on ? h : 1e6;
  $('sectionVal').textContent = on ? `Cut at ${fmtFt(h / FT)} (${h.toFixed(2)} m) above floor level` : 'Off – drag to set height, tick to cut';
}
function setPlan() {
  if (!app.planObj) { $('planBtn').disabled = true; $('planBtn').title = 'No plan reference in this model'; return; }
  const show = app.planMode && $('planChk').checked;
  app.planObj.visible = show;
  app.planMat.opacity = +$('planOpacity').value;
  const above = document.querySelector('input[name=planPos]:checked').value === 'above';
  // "above" = just over the wall tops, drawn on top of everything. "floor" = on the floor, hidden by walls.
  const parentY = app.planObj.parent ? app.planObj.parent.getWorldPosition(new THREE.Vector3()).y : 0;
  app.planObj.position.y = (above ? app.wallTop + 0.05 : app.bbox.min.y + 0.35) - parentY;
  app.planMat.depthTest = !above; app.planMat.needsUpdate = true;
  app.planMat.clippingPlanes = null;
}
function togglePlanMode(on) {
  app.planMode = on;
  $('planBtn').classList.toggle('on', on); $('planSection').classList.toggle('hidden', !on);
  if (on) {
    app._prePlan = { roof: app.catVisible.roof, labels: app.labelsOn };
    setCat('roof', false); presetView('top');
  } else if (app._prePlan) {
    setCat('roof', app._prePlan.roof !== false);
  }
  setPlan();
}

// ------------------------------------------------------------------ labels & debug
function setEdges(on) { app.edgesOn = on; app.edges.forEach(e => e.visible = on); (app.compare?.edges || []).forEach(e => e.visible = on); $('edgesBtn').classList.toggle('on', on); }
function setLabels(on) { app.labelsOn = on; labelsGroup.visible = on; labelsGroup.children.forEach(l => l.visible = on); app._occT = 0; $('labelsBtn').classList.toggle('on', on); }
function buildDebug() {
  debugGroup.clear();
  for (const o of app.objects) {
    if (o.obj.parent && o.obj.parent.userData && o.obj.parent.userData.category) continue; // assemblies: label the parent only
    if ([CONFIG.planCategory, 'context'].includes(o.cat)) continue;
    const b = new THREE.Box3().setFromObject(o.obj); if (b.isEmpty()) continue;
    const c = b.getCenter(new THREE.Vector3());
    const ud = o.obj.userData, st = CONFIG.status[o.status];
    const dims = ud.dims_ft ? ud.dims_ft.map(fmtFt).join(' × ') : (ud.width_ft ? `${fmtFt(ud.width_ft)} wide` : '');
    const div = document.createElement('div'); div.className = 'lbl-debug';
    div.innerHTML = `<b>${o.name}</b><br><span style="color:${st ? st.color : '#888'}">${o.status || 'no status'}</span>${dims ? ' · ' + dims : ''}`;
    const l = new CSS2DObject(div); l.position.set(c.x, Math.min(b.max.y, app.wallTop) + 0.1, c.z); l.userData.src = o.obj; debugGroup.add(l);
  }
}
function updateDebugLabels() {
  for (const l of debugGroup.children) {
    let vis = true; for (let p = l.userData.src; p; p = p.parent) if (p.visible === false) { vis = false; break; }
    l.visible = vis && app.debugMode;
  }
}
function setDebug(on) {
  app.debugMode = on; debugGroup.visible = on;
  $('debugBtn').classList.toggle('on', on); $('debugPanel').classList.toggle('hidden', !on);
  updateDebugLabels();
}
function updateObjList() {
  const q = $('objSearch').value.trim().toLowerCase();
  const list = $('objList'); list.innerHTML = '';
  for (const o of app.objects) {
    const s = `${o.name} ${o.cat} ${o.status || ''} ${o.obj.userData.subtype || ''}`.toLowerCase();
    if (q && !s.includes(q)) continue;
    const it = document.createElement('div'); it.className = 'it' + (app.selected === o.obj ? ' sel' : '');
    const col = (CONFIG.status[o.status] || CONFIG.noStatus).color;
    it.innerHTML = `<span class="dot" style="background:${col}"></span><span>${o.name}</span><span class="cat">${o.cat}</span>`;
    it.onclick = () => { select(o.obj); focusObject(o.obj); };
    list.appendChild(it);
  }
}

// ------------------------------------------------------------------ selection & inspector
const raycaster = new THREE.Raycaster();
function pick(ev) {
  const r = renderer.domElement.getBoundingClientRect();
  let x = ev.clientX - r.left, w = r.width, pool = app.meshes;
  if (app.compare) { const hw = r.width / 2; if (x > hw) { x -= hw; pool = app.compare.meshes; } w = hw; }
  const ndc = new THREE.Vector2((x / w) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
  const cands = pool.filter(m => { for (let p = m; p; p = p.parent) if (!p.visible) return false; return catOf(m) !== 'context' && catOf(m) !== CONFIG.planCategory; });
  const hits = raycaster.intersectObjects(cands, false).filter(h => !app.sectionPlane || h.point.y <= app.sectionPlane.constant + 1e-3);
  select(hits.length ? hits[0].object : null);
}
function namedOf(o) { for (let p = o; p; p = p.parent) if (p.userData && p.userData.category) return p; return o; }
function select(o) {
  app.selected = o ? namedOf(o) : null;
  if (!app.selected) { selBox.visible = false; renderInspector(null); updateObjList(); imm.onSelect(null); return; }
  selBox.box.setFromObject(app.selected); selBox.visible = !(app.compare && app.compare.root.getObjectById(app.selected.id));
  renderInspector(app.selected); updateObjList(); imm.onSelect(app.selected);
}
function focusObject(o) {
  const b = new THREE.Box3().setFromObject(o); const c = b.getCenter(new THREE.Vector3()); const s = b.getSize(new THREE.Vector3()).length();
  const dir = camera.position.clone().sub(controls.target).normalize();
  flyTo({ pos: c.clone().addScaledVector(dir, Math.max(3, s * 1.8)), target: c, ortho: app.ortho, halfH: Math.max(2, s) });
}
const CAT_LABEL = Object.fromEntries(CONFIG.categories.map(c => [c.key, c.label]));
function renderInspector(o) {
  const el = $('inspector');
  if (!o) { el.className = 'empty'; el.textContent = 'Click any wall, door, window, pillar, beam, step or piece of furniture.'; return; }
  el.className = '';
  const ud = o.userData; const st = ud.status; const sc = CONFIG.status[st];
  const rows = [];
  const add = (k, v) => { if (v !== undefined && v !== null && v !== '') rows.push(`<div class="k">${k}</div><div class="v">${v}</div>`); };
  add('Category', (CAT_LABEL[ud.category] || ud.category) + (ud.subtype ? ` (${ud.subtype})` : ''));
  add('Status', st ? `<span class="badge" style="background:${sc ? sc.color : '#999'}">${sc ? sc.label.toUpperCase() : st}</span>` : '<i>none in model</i>');
  add('Basis', ud.basis);
  if (ud.design_option) add('Design option', ud.design_option);
  add('Specification', ud.spec);
  if (learnApi) add('In simple words', learnApi.explainHTML(o));
  add('Room', ud.room);
  if (ud.dims_ft) {
    const [x, y, z] = ud.dims_ft;
    add('Size', `${fmtFt(x)} × ${fmtFt(y)} × ${fmtFt(z)} <span style="color:#888">(local X × Y × height)</span>`);
    if (ud.category === 'walls' || ud.category === 'pillars' || ud.category === 'beams') add(ud.category === 'walls' ? 'Thickness' : 'Section', ud.category === 'walls' ? fmtFt(Math.min(x, y)) : `${fmtFt(Math.min(x, y))} × ${fmtFt(Math.max(x, y))}`);
  }
  if (ud.width_ft) add('Opening width', fmtFt(ud.width_ft));
  if (ud.height_ft) add('Opening height', fmtFt(ud.height_ft));
  if (ud.sill_ft !== undefined) add('Sill', fmtFt(ud.sill_ft));
  if (ud.top_ft !== undefined) add('Head', fmtFt(ud.top_ft));
  if (ud.swing) add('Swing', ud.swing);
  add('Collection', ud.collection);
  if (o.parent && o.parent.userData && o.parent.userData.category) add('Part of', `<a href="#" id="selParent">${o.parent.name}</a>`);
  const kids = o.children.filter(c => c.userData && c.userData.category).map(c => c.name);
  if (kids.length) add('Parts', kids.join('<br>'));
  const b = new THREE.Box3().setFromObject(o); const p = b.getCenter(new THREE.Vector3());
  add('Centre', `x ${fmtM(p.x)}, z ${fmtM(p.z)} <span style="color:#888">(model axes)</span>`);
  el.innerHTML = `<div class="objname">${o.name}</div><div class="kv">${rows.join('')}</div>
    <div class="row">${imm.isInteractive(o) ? '<button class="small" id="interactBtn">Open / close</button>' : ''}<button class="small" id="focusBtn">Focus</button><button class="small" id="isoBtn">Isolate category</button><button class="small" id="clearSelBtn">Clear</button></div>`;
  $('focusBtn').onclick = () => focusObject(o);
  if ($('interactBtn')) $('interactBtn').onclick = () => imm.toggleFor(o);
  $('clearSelBtn').onclick = () => select(null);
  $('isoBtn').onclick = () => { for (const k of Object.keys(app.catVisible)) app.catVisible[k] = (k === ud.category); app.catVisible.floors = true; applyVisibility(); };
  const sp = $('selParent'); if (sp) sp.onclick = (e) => { e.preventDefault(); select(o.parent); };
}

// ------------------------------------------------------------------ UI wiring
document.querySelectorAll('#viewButtons button').forEach(b => b.onclick = () => presetView(b.dataset.view));
$('projBtn').onclick = () => { if (walk.active) return; useCamera(!app.ortho); };
$('roofBtn').onclick = () => setCat('roof', app.catVisible.roof === false);
$('labelsBtn').onclick = () => setLabels(!app.labelsOn);
$('edgesBtn').onclick = () => setEdges(!app.edgesOn);
$('dockToggle').onclick = () => { $('dock').classList.toggle('collapsed'); $('dockToggle').textContent = $('dock').classList.contains('collapsed') ? 'Controls ▴' : 'Hide controls ▾'; };
$('statusBtn').onclick = () => { app.statusMode = !app.statusMode; applyMaterials(); };
$('planBtn').onclick = () => togglePlanMode(!app.planMode);
$('debugBtn').onclick = () => setDebug(!app.debugMode);
$('walkBtn').onclick = () => walk.active ? overview() : startWalk();
$('overviewBtn').onclick = overview;
$('exitWalkBtn').onclick = overview;
$('resetBtn').onclick = () => { resetVisibility(); $('sectionChk').checked = false; setSection(); $('modelOpacity').value = 1; app.statusMode = false; applyMaterials(); if (app.planMode) togglePlanMode(false); select(null); presetView('iso'); };
$('showAllBtn').onclick = () => { for (const k of Object.keys(app.catVisible)) app.catVisible[k] = true; applyVisibility(); };
$('hideAllBtn').onclick = () => { for (const k of Object.keys(app.catVisible)) app.catVisible[k] = false; applyVisibility(); };
$('resetVisBtn').onclick = resetVisibility;
function resetVisibility() { for (const k of Object.keys(app.catVisible)) app.catVisible[k] = true; applyVisibility(); }
$('sectionChk').onchange = setSection; $('sectionRange').oninput = () => { $('sectionChk').checked = true; setSection(); };
$('modelOpacity').oninput = applyMaterials;
$('planChk').onchange = setPlan; $('planOpacity').oninput = setPlan;
document.querySelectorAll('input[name=planPos]').forEach(r => r.onchange = setPlan);
$('objSearch').oninput = updateObjList;
$('copyViewBtn').onclick = async () => {
  const f = (v) => [+v.x.toFixed(3), +v.y.toFixed(3), +v.z.toFixed(3)];
  const txt = JSON.stringify({ name: 'My view', pos: f(camera.position), target: f(controls.target) });
  try { await navigator.clipboard.writeText(txt); $('copyViewBtn').textContent = 'Copied ✓'; } catch (e) { prompt('Copy this into CONFIG.viewpoints:', txt); }
  setTimeout(() => $('copyViewBtn').textContent = 'Copy current view', 1500);
};
function startWalk() {
  useCamera(false);
  const ok = walk.enter(camera.position.clone(), controls.target.clone());
  if (ok) return;
  // from the overview: stand where the view is pointing if that is a floor, else in the last room, else the hall
  const t = controls.target.clone(), dir = t.clone().sub(camera.position).setY(0);
  if (dir.lengthSq() < 1e-6) dir.set(0, 0, -1);
  const at = new THREE.Vector3(t.x, t.y + 1.2, t.z);
  if (walk.enter(at, at.clone().add(dir.normalize()))) return;
  const r = app.rooms.find(x => x.name === app.lastRoom) || app.rooms.find(x => x.name === 'Room 1') || app.rooms.find(x => x.name === 'Hall') || app.rooms[0];
  if (r) walk.enter(r.vps[0].pos.clone(), r.vps[0].target.clone());
}
walk.onChange = (on) => { $('walkBtn').classList.toggle('on', on); $('walkHud').classList.toggle('hidden', !on); };

let down = null;
renderer.domElement.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
renderer.domElement.addEventListener('pointerup', e => {
  if (!down) return;          // a click (not a drag) selects, in the overview and inside
  if (Math.hypot(e.clientX - down.x, e.clientY - down.y) < 5) pick(e);
  down = null;
});
controls.addEventListener('start', () => { app.tween = null; app.pendingWalk = null; });

// labels: when you stand inside the building, hide labels of rooms behind walls
function visibleChain(m) { for (let p = m; p; p = p.parent) if (!p.visible) return false; return true; }
const _lray = new THREE.Raycaster();
function updateLabelOcclusion() {
  if (!app.labelsOn || !app.model) return;
  const cp = camera.position;
  const inside = !app.ortho && cp.y < app.wallTop && cp.x > app.bbox.min.x && cp.x < app.bbox.max.x && cp.z > app.bbox.min.z && cp.z < app.bbox.max.z;
  if (!inside) { labelsGroup.children.forEach(l => l.visible = true); return; }
  const occ = app.meshes.filter(m => ['walls', 'roof', 'doors'].includes(catOf(m)) && visibleChain(m));
  for (const l of labelsGroup.children) {
    const dir = l.position.clone().sub(cp); const dist = dir.length(); dir.normalize();
    _lray.set(cp, dir); _lray.far = Math.max(0.01, dist - 0.2);
    l.visible = dist > 3.2 && _lray.intersectObjects(occ, false).length === 0;
  }
}

// ------------------------------------------------------------------ side-by-side compare
const scene2 = new THREE.Scene();
scene2.background = scene.background; scene2.environment = scene.environment; scene2.environmentIntensity = scene.environmentIntensity;
scene2.add(new THREE.HemisphereLight('#ffffff', '#b9b3a8', 1.1));
const sun2 = new THREE.DirectionalLight('#ffffff', 1.6); sun2.castShadow = !LOWQ; sun2.shadow.mapSize.set(2048, 2048); sun2.shadow.bias = -0.0004; sun2.shadow.normalBias = 0.02;
scene2.add(sun2, sun2.target);
let _aspect = 0;
function setAspect(a) {
  if (Math.abs(a - _aspect) < 1e-4) return; _aspect = a;
  persp.aspect = a; persp.updateProjectionMatrix();
  const hh = orthoCam.userData.halfH || 10; orthoCam.left = -hh * a; orthoCam.right = hh * a; orthoCam.updateProjectionMatrix();
}
async function setCompare(file) {
  if (app.compare) { scene2.remove(app.compare.root); app.compare = null; }
  $('compareSelect').value = file || '';
  if (!file) { $('compareCaption').classList.add('hidden'); labelRenderer.domElement.style.display = ''; _aspect = 0; return; }
  const gltf = await new GLTFLoader().loadAsync(CONFIG.modelDir + file + '?v=' + BUILD);
  const root = gltf.scene; const byCat = new Map(), meshes = [], edges = [];
  root.traverse(o => {
    const cat = catOf(o);
    if (o.userData?.category) { if (!byCat.has(cat)) byCat.set(cat, []); byCat.get(cat).push(o); }
    if (o.isMesh) {
      o.userData._origMat = o.material; o.material.clippingPlanes = [app.sectionPlane];
      o.castShadow = !['plan_reference', 'context'].includes(cat) && !o.material.transparent; o.receiveShadow = true;
      if (cat !== CONFIG.planCategory) meshes.push(o);
      if (![CONFIG.planCategory, 'context'].includes(cat)) { const e = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 28), edgeMat); e.raycast = () => {}; e.visible = app.edgesOn; o.add(e); edges.push(e); }
    }
  });
  fixSides(meshes);
  sun2.position.copy(sun.position); sun2.target.position.copy(sun.target.position);
  const sc = sun2.shadow.camera; Object.assign(sc, { left: sun.shadow.camera.left, right: sun.shadow.camera.right, top: sun.shadow.camera.top, bottom: sun.shadow.camera.bottom, near: 1, far: 80 }); sc.updateProjectionMatrix();
  scene2.add(root); app.compare = { root, byCat, meshes, edges, file };
  applyVisibility();
  labelRenderer.domElement.style.display = 'none';
  $('capL').innerHTML = `<b>${modelEntry(app.modelFile).label || app.modelFile}</b>`; $('capR').innerHTML = `<b>${modelEntry(file).label || file}</b>`;
  $('compareCaption').classList.remove('hidden');
}

// ------------------------------------------------------------------ overview: keyboard travel
// WASD / arrows slide the view (camera + pivot together) over the floor; Q / E or PageUp / PageDown go up / down.
const okeys = new Set();
document.addEventListener('keydown', (e) => {
  if (walk.active || /INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName)) return;
  if (/^(Key[WASDQE]|Arrow|Page|Shift)/.test(e.code)) { okeys.add(e.code); if (/^(Arrow|Page)/.test(e.code)) e.preventDefault(); }
});
document.addEventListener('keyup', (e) => okeys.delete(e.code));
window.addEventListener('blur', () => okeys.clear());
function orbitKeys(dt) {
  if (!okeys.size || app.tween) return;
  const k = okeys; let f = 0, s = 0, u = 0;
  if (k.has('KeyW') || k.has('ArrowUp')) f += 1; if (k.has('KeyS') || k.has('ArrowDown')) f -= 1;
  if (k.has('KeyD') || k.has('ArrowRight')) s += 1; if (k.has('KeyA') || k.has('ArrowLeft')) s -= 1;
  if (k.has('KeyE') || k.has('PageUp')) u += 1; if (k.has('KeyQ') || k.has('PageDown')) u -= 1;
  if (!f && !s && !u) return;
  const dist = camera.position.distanceTo(controls.target);
  const speed = Math.max(1.2, Math.min(6, dist * 0.5)) * ((k.has('ShiftLeft') || k.has('ShiftRight')) ? 2.5 : 1);
  const fwd = new THREE.Vector3().subVectors(controls.target, camera.position).setY(0);
  if (fwd.lengthSq() < 1e-6) camera.getWorldDirection(fwd).setY(0);
  if (fwd.lengthSq() < 1e-6) fwd.set(0, 0, -1);
  fwd.normalize(); const right = new THREE.Vector3(-fwd.z, 0, fwd.x);
  const mv = fwd.multiplyScalar(f).add(right.multiplyScalar(s)); mv.y = u;
  mv.normalize().multiplyScalar(speed * dt);
  if (camera.position.y + mv.y < 0.25) mv.y = 0;       // never below the ground
  camera.position.add(mv); controls.target.add(mv);
}

// ------------------------------------------------------------------ loop
const clock = new THREE.Clock();
function loop() {
  const dt = Math.min(0.25, clock.getDelta());
  if (walk.active) walk.update(dt); else { stepTween(dt); orbitKeys(dt); controls.update(); }
  imm.update(dt); ex.update(dt);
  if (selBox.visible && app.selected) selBox.box.setFromObject(app.selected);
  const now = performance.now(); if (now - (app._occT || 0) > 200) { app._occT = now; updateLabelOcclusion(); }
  const camName = walk.active ? 'Walkthrough' : (app.ortho ? 'Orthographic' : 'Perspective');
  $('statusbar').textContent = `${app.statusText || ''} · ${camName}`;
  const W = host.clientWidth, Hh = host.clientHeight;
  if (app.compare) {
    const hw = Math.floor(W / 2); setAspect(hw / Hh);
    renderer.setScissorTest(true);
    renderer.setViewport(0, 0, hw, Hh); renderer.setScissor(0, 0, hw, Hh); renderer.render(scene, camera);
    renderer.setViewport(hw, 0, W - hw, Hh); renderer.setScissor(hw, 0, W - hw, Hh); renderer.render(scene2, camera);
    renderer.setScissorTest(false); renderer.setViewport(0, 0, W, Hh);
  } else {
    setAspect(W / Hh); renderer.render(scene, camera); labelRenderer.render(scene, camera);
  }
  requestAnimationFrame(loop);
}

// ------------------------------------------------------------------ immersive features
const imm = setupImmersive({ app, scene, renderer, controls, walk, hemi, sun, $, fmtFt, getCamera: () => camera, resize: () => { _aspect = 0; resize(); },
  onBlocked: (what, by) => ex && ex.toast(`${what[0].toUpperCase() + what.slice(1)} can't open further: it hits the ${by}`),
  startWalk: () => startWalk(), overview, goToPoint, goRoom: (n, i) => { const r = app.rooms.find(x => x.name === n); if (r && r.vps[i]) goRoomVp(r, r.vps[i]); } });
let learnApi = null;
const ex = setupExtras({ app, scene, renderer, controls, walk, persp, $, fmtFt, CONFIG, getCamera: () => camera, explain: (o) => learnApi ? learnApi.explain(o) : [],
  resize: () => { _aspect = 0; resize(); }, isInteractive: (o) => imm.isInteractive(o) });
new ResizeObserver(() => { _aspect = 0; resize(); }).observe(host);
setupLearn({ app, $, select, focusObject, scene, build: BUILD, modelEntry }).then(a => { learnApi = a; window.viewer.learn = a; });
walk.onChange = (on) => {
  $('walkBtn').classList.toggle('on', on); $('walkHud').classList.toggle('hidden', !on); document.querySelector('#immBar [data-act=walk]')?.classList.toggle('on', on);
  ex.onWalkChange(on);
  // inside: tuck the controls panel away so you see the room; bring it back in the overview
  const d = $('dock');
  if (on && !app._inWalk) { app._dockWas = d.classList.contains('collapsed'); d.classList.add('collapsed'); }
  else if (!on && app._inWalk && app._dockWas === false) d.classList.remove('collapsed');
  app._inWalk = on;
  $('dockToggle').textContent = d.classList.contains('collapsed') ? 'Controls ▴' : 'Hide controls ▾';
};

// ------------------------------------------------------------------ start
(async function start() {
  resize(); setLabels(true);
  const file = await loadModelList();
  await loadModel(file);
  loop();
})();

// exposed for automated checks
window.viewer = { imm, ex, setCompare, switchModel, presetView, setCat, setEdges, updateLabelOcclusion, applyVisibility, togglePlanMode, setDebug, setLabels, select, loadModel, startWalk, walk, overview, goToPoint, goRoomVp,
  get camera() { return camera; }, controls, scene, renderer, CONFIG, fmtFt,
  setStatus: (on) => { app.statusMode = on; applyMaterials(); }, goRoom: (name, i = 0) => { const r = app.rooms.find(r => r.name === name); goRoomVp(r, r.vps[i]); },
  pickAt: (x, y) => pick({ clientX: x, clientY: y }), setSection: (on, h) => { $('sectionChk').checked = on; if (h) $('sectionRange').value = h; setSection(); } };
