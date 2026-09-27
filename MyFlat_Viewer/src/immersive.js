// Immersive features: openable parts, dimensions, lights on/off + night, full-screen mode.
// Everything is driven by metadata exported from Blender:
//   interact = hinge | slide | toggle, group, open_deg, slide_ft, label   (openable parts)
//   light    = spot | point | strip, lumens                               (light fittings)
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { OBB } from 'three/addons/math/OBB.js';

const FT = 0.3048;
const YAXIS = new THREE.Vector3(0, 1, 0);
// things a swinging sash / door / sliding panel can bump into
const OBSTACLE_CATS = ['furniture', 'decor', 'lighting', 'plants'];
export function prettyName(n) {
  return (n || '').replace(/^R1_(DEF|OPA|OPB|OPC|A|B|C)_/, '').replace(/\.\d+$/, '').replace(/_/g, ' ').toLowerCase();
}

export function setupImmersive(ctx) {
  const { app, scene, renderer, controls, walk, hemi, sun, $, fmtFt } = ctx;
  const cam = () => ctx.getCamera();
  const groups = new Map();          // group -> { objs:[{o,pos,quat}], meta, open, t }
  const lights = [];                 // created three lights
  const emissive = new Map();        // material -> original emissiveIntensity
  const dimsGroup = new THREE.Group(); dimsGroup.visible = false; scene.add(dimsGroup);
  const selDims = new THREE.Group(); scene.add(selDims);
  const st = { lightsOn: true, night: false, dims: false, immersive: false };
  const ray = new THREE.Raycaster();
  const day = { bg: scene.background.clone(), hemi: hemi.intensity, sun: sun.intensity, env: scene.environmentIntensity };

  // ---------------------------------------------------------------- model hook
  function onModel(root) {
    groups.clear(); emissive.clear();
    lights.forEach(l => { l.parent && l.parent.remove(l); l.dispose?.(); }); lights.length = 0;
    dimsGroup.clear(); selDims.clear();
    root.traverse(o => {
      const u = o.userData || {};
      if (u.interact && u.group) {
        if (!groups.has(u.group)) groups.set(u.group, { objs: [], meta: u, open: false, t: 0 });
        groups.get(u.group).objs.push({ o, pos: o.position.clone(), quat: o.quaternion.clone() });
      }
      if (o.isMesh && o.material?.emissive && o.material.emissiveIntensity > 0 && (o.material.emissive.r + o.material.emissive.g + o.material.emissive.b) > 0)
        if (!emissive.has(o.material)) emissive.set(o.material, o.material.emissiveIntensity);
    });
    buildLights(root); buildDimLabels(root); buildObstacles(root);
    applyLighting();
    $('openAllBtn').disabled = $('closeAllBtn').disabled = groups.size === 0;
    $('interactInfo').textContent = groups.size ? `${groups.size} openable parts in this model` : 'No openable parts in this model';
  }

  // ---------------------------------------------------------------- open / close
  function groupOf(o) { for (let p = o; p; p = p.parent) if (p.userData?.interact && p.userData.group) return groups.get(p.userData.group); return null; }
  function toggle(g, force) { if (!g) return; g.open = force === undefined ? !g.open : force; g.blockedT = null; }

  // ---- collisions: an opening part stops when it touches furniture, a lamp, a plant … (like a real one)
  let obstacles = [];
  function catOfO(o) { for (let p = o; p; p = p.parent) if (p.userData?.category) return p.userData.category; return null; }
  function visibleO(o) { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; }
  function obbOf(m, shrink = 0) {
    if (!m.geometry.boundingBox) m.geometry.computeBoundingBox();
    const b = m.geometry.boundingBox.clone();
    if (shrink) { const s = new THREE.Vector3(); b.getSize(s); b.expandByVector(new THREE.Vector3(-Math.min(shrink, s.x * 0.3), -Math.min(shrink, s.y * 0.3), -Math.min(shrink, s.z * 0.3))); }
    // (OBB.applyMatrix4 doesn't rotate the box centre, so build it from the decomposed world matrix)
    const pos = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
    m.matrixWorld.decompose(pos, q, sc);
    const hs = b.getSize(new THREE.Vector3()).multiplyScalar(0.5).multiply(new THREE.Vector3(Math.abs(sc.x), Math.abs(sc.y), Math.abs(sc.z)));
    return new OBB(b.getCenter(new THREE.Vector3()).applyMatrix4(m.matrixWorld), hs, new THREE.Matrix3().setFromMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(q)));
  }
  function buildObstacles(root) {
    root.updateMatrixWorld(true); obstacles = [];
    // wardrobe internals (LED, loft contents …) sit behind their own doors: not obstacles
    root.traverse(o => { if (o.isMesh && OBSTACLE_CATS.includes(catOfO(o)) && !groupOf(o) && !/WARDROBE/i.test(o.name)) obstacles.push({ m: o, obb: obbOf(o, 0.004), c: new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3()) }); });
    for (const g of groups.values()) {
      g.meshes = []; for (const it of g.objs) it.o.traverse(o => { if (o.isMesh) g.meshes.push(o); });
      const c = new THREE.Box3(); g.meshes.forEach(m => c.expandByObject(m)); g.center = c.getCenter(new THREE.Vector3());
      g.near = obstacles.filter(ob => ob.c.distanceTo(g.center) < 3.5);
      // anything already touching when closed is not a collision
      g.ignore = new Set(g.near.filter(ob => collideList(g, [ob])));
    }
  }
  function collideList(g, list) {
    for (const m of g.meshes) {
      if (!visibleO(m)) continue;
      const a = obbOf(m, 0.004);
      for (const ob of list) if (visibleO(ob.m) && a.intersectsOBB(ob.obb)) return ob;
    }
    return null;
  }
  function collides(g) { return g.near?.length ? collideList(g, g.near.filter(ob => !g.ignore.has(ob))) : null; }
  function pose(g, t) {
    const e = t * t * (3 - 2 * t), m = g.meta;
    for (const it of g.objs) {
      if (m.interact === 'hinge') {
        it.o.quaternion.copy(it.quat).multiply(new THREE.Quaternion().setFromAxisAngle(YAXIS, THREE.MathUtils.degToRad(m.open_deg) * e));
      } else if (m.interact === 'slide') {
        const s = m.slide_ft || [0, 0, 0];     // Blender (x, y) ft -> three (x, -z) m
        it.o.position.copy(it.pos).add(new THREE.Vector3(s[0] * FT * e, s[2] * FT * e, -s[1] * FT * e));
      } else if (m.interact === 'toggle') {
        it.o.visible = t < 0.5;
      }
      it.o.updateMatrixWorld(true);        // keep collisions / raycasts exact within the same frame
    }
  }
  function setAll(open) { for (const g of groups.values()) toggle(g, open); }
  function animate(dt) {
    for (const g of groups.values()) {
      const target = g.open ? 1 : 0; if (g.t === target || (g.open && g.blockedT === g.t)) continue;
      const prev = g.t;
      g.t = target > g.t ? Math.min(1, g.t + dt / 0.6) : Math.max(0, g.t - dt / 0.6);
      pose(g, g.t);
      if (target === 1 && g.meta.interact !== 'toggle') {
        const hit = collides(g);
        if (hit) {           // back off in small steps to the last free position, then stop there
          let t = prev; pose(g, t);
          for (let k = 1; k <= 6; k++) { const tt = prev + (g.t - prev) * k / 6; pose(g, tt); if (collides(g)) { pose(g, t); break; } t = tt; }
          g.t = t; g.blockedT = t; g.blockedBy = hit.m.name;
          ctx.onBlocked && ctx.onBlocked(prettyName([...groups].find(([k, v]) => v === g)?.[0] || g.objs[0].o.name), prettyName(hit.m.name));
        }
      }
    }
  }
  function interactiveHit(ndc, maxDist = Infinity) {
    ray.setFromCamera(ndc, cam()); ray.far = maxDist;
    const cands = app.meshes.filter(m => { for (let p = m; p; p = p.parent) if (!p.visible) return false; return true; });
    const hits = ray.intersectObjects(cands, false);
    for (const h of hits) {
      const g = groupOf(h.object); if (g) return { g, hit: h };
      const cat = h.object.userData?.category || h.object.parent?.userData?.category;
      if (!['soft_furnishing', 'lighting'].includes(cat)) return null;   // something solid is in front
    }
    return null;
  }
  function ndcFromEvent(ev) {
    const r = renderer.domElement.getBoundingClientRect();
    return new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  }
  // first solid thing under the cursor; returns the point if it is a floor / stair / balcony floor you can stand on
  function floorHit(ndc) {
    ray.setFromCamera(ndc, cam()); ray.far = Infinity;
    const cands = app.meshes.filter(m => { for (let p = m; p; p = p.parent) if (!p.visible) return false; return true; });
    for (const h of ray.intersectObjects(cands, false)) {
      let cat = null; for (let p = h.object; p && !cat; p = p.parent) cat = p.userData?.category || null;
      if (['soft_furnishing', 'lighting', 'plan_reference', 'roof', 'ceiling', 'beams', 'vents', 'decor'].includes(cat)) continue;   // look through the lid
      const n = h.face ? h.face.normal.clone().transformDirection(h.object.matrixWorld) : null;
      if (['floors', 'stairs'].includes(cat) && n && n.y > 0.7) return h.point.clone();
      return null;
    }
    return null;
  }
  renderer.domElement.addEventListener('dblclick', (ev) => {
    if (walk.active || app.compare) return;
    const ndc = ndcFromEvent(ev); const h = interactiveHit(ndc);
    if (h) { toggle(h.g); return; }
    const p = floorHit(ndc); if (p && ctx.goToPoint) ctx.goToPoint(p);
  });
  // walk mode: a click (not a drag) on a door / sash / wardrobe within reach opens or closes it
  renderer.domElement.addEventListener('pointerup', (ev) => {
    if (!walk.active || walk.dragMoved > 5 || (ev.pointerType === 'mouse' && ev.button !== 0)) return;
    const h = interactiveHit(ndcFromEvent(ev), 3.5); if (h) toggle(h.g);
  });
  let hoverT = 0;
  renderer.domElement.addEventListener('pointermove', (ev) => {
    if (walk.active || app.compare) return; const now = performance.now(); if (now - hoverT < 90) return; hoverT = now;
    const ndc = ndcFromEvent(ev); const h = interactiveHit(ndc);
    const f = h ? null : floorHit(ndc);
    renderer.domElement.style.cursor = h ? 'pointer' : (f ? 'cell' : '');
    renderer.domElement.title = h ? `${h.g.meta.label || 'Open / close'} (double-click)` : (f ? 'Double-click to stand here' : '');
  });
  // walkthrough: look at a part and press E (or click while the mouse is captured)
  const center = new THREE.Vector2(0, 0);
  function useCenter() { if (!walk.active) return false; const h = interactiveHit(center, 3.2); if (h) { toggle(h.g); return true; } return false; }
  document.addEventListener('keydown', (e) => {
    if (/INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName)) return;
    if (e.code === 'KeyE') useCenter();
    if (e.code === 'KeyL') setLights(!st.lightsOn);
    if (e.code === 'KeyN') setNight(!st.night);
    if (e.code === 'KeyF' && !walk.active) setImmersive(!st.immersive);
  });
  let hintT = 0;
  function updateHint() {
    const now = performance.now(); if (now - hintT < 120) return; hintT = now;
    const hint = $('interactHint'); $('crosshair').classList.toggle('hidden', !walk.active);
    if (!walk.active) { hint.classList.add('hidden'); return; }
    const h = interactiveHit(center, 3.2);
    if (h) { hint.textContent = `E · ${h.g.open ? 'Close' : (h.g.meta.label || 'Open')}`; hint.classList.remove('hidden'); } else hint.classList.add('hidden');
  }

  // ---------------------------------------------------------------- lights & night
  function buildLights(root) {
    const fixtures = []; root.traverse(o => { if (o.userData?.light) fixtures.push(o); });
    const warm = new THREE.Color('#ffd7a8');
    let budget = 18;
    for (const f of fixtures) {
      if (budget <= 0) break;
      const b = new THREE.Box3().setFromObject(f); const c = b.getCenter(new THREE.Vector3()); const s = b.getSize(new THREE.Vector3());
      const lm = f.userData.lumens || 300; const kind = f.userData.light;
      if (kind === 'spot') {
        const l = new THREE.SpotLight(warm, lm / 45, 7, 0.8, 0.7, 2); l.position.set(c.x, b.min.y - 0.02, c.z);
        l.target.position.set(c.x, 0, c.z); scene.add(l, l.target); lights.push(l, l.target); budget--;
      } else if (kind === 'strip') {
        const long = s.x > s.z ? 'x' : 'z'; const L = Math.max(s.x, s.z); const n = Math.min(budget, L > 2.5 ? 2 : 1);
        for (let i = 0; i < n; i++) {
          const l = new THREE.PointLight(warm, lm / (35 * n), 5, 2); const p = c.clone(); if (n > 1) p[long] = b.min[long] + L * (i + 0.5) / n;
          p.y = b.min.y - 0.08; l.position.copy(p); scene.add(l); lights.push(l); budget--;
        }
      } else {
        const l = new THREE.PointLight(warm, lm / 40, 4, 2); l.position.set(c.x, b.min.y - 0.05, c.z); scene.add(l); lights.push(l); budget--;
      }
    }
  }
  function applyLighting() {
    const on = st.lightsOn;
    for (const [m, v] of emissive) { m.emissiveIntensity = on ? v * (st.night ? 0.8 : 1) : 0; m.needsUpdate = true; }
    for (const l of lights) if (l.isLight) l.visible = on && st.night;   // fixtures add real light at night
    if (st.night) {
      scene.background = new THREE.Color('#0d1322'); hemi.intensity = 0.05; sun.intensity = 0.04; scene.environmentIntensity = 0.04;
      renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.95;
    } else {
      scene.background = day.bg.clone(); hemi.intensity = day.hemi; sun.intensity = day.sun; scene.environmentIntensity = day.env;
      renderer.toneMapping = THREE.NoToneMapping;
    }
    $('lightsBtn').classList.toggle('on', on); $('lightsBtn').textContent = on ? 'Lights ON' : 'Lights OFF';
    $('nightBtn').classList.toggle('on', st.night); $('nightBtn').textContent = st.night ? 'Night' : 'Day';
    syncImmBar();
  }
  function setLights(on) { st.lightsOn = on; applyLighting(); }
  function setNight(on) { st.night = on; applyLighting(); }

  // ---------------------------------------------------------------- dimensions
  const SKIP = /PILLOW|CUSHION|DUVET|THROW|MATTRESS|PLINTH|LEAVES|_POT$|CORD|TRACK|DRAPE|SHEER|GLASS|HANDLE|INSET|CONTENTS|RODS|INTERNALS|SKIRTING|LED$|COVE|DOWNLIGHT|__edges|FLOOR_FINISH|FLOOR_BORDER|NOSING|MESH|POLE|LAMP_BASE|SHADE|LANTERN|BAND$/;
  const SHOW = ['furniture', 'wardrobe', 'fenestration', 'balcony', 'finishes', 'ceiling', 'decor', 'plants', 'doors', 'windows', 'pillars', 'beams'];
  function sizeText(o) {
    const b = new THREE.Box3().setFromObject(o); const s = b.getSize(new THREE.Vector3());
    return { b, txt: `${fmtFt(s.x / FT)} × ${fmtFt(s.z / FT)} × ${fmtFt(s.y / FT)}` };
  }
  function buildDimLabels(root) {
    dimsGroup.clear();
    const seen = new Set();
    root.traverse(o => {
      const u = o.userData || {}; if (!u.category || !SHOW.includes(u.category)) return;
      if (SKIP.test(o.name) || seen.has(o.name)) return;
      if (u.group && seen.has('g:' + u.group)) return;
      if (['doors', 'windows'].includes(u.category) && (o.isMesh || !u.width_ft)) return;   // architecture openings: the empty carries width/height
      seen.add(o.name); if (u.group) seen.add('g:' + u.group);
      let txt, pos;
      if (u.width_ft) {  // architectural opening
        const b = new THREE.Box3().setFromObject(o); pos = b.getCenter(new THREE.Vector3());
        txt = `${o.name.replace(/^(DOOR|WINDOW|OPENING)_/, '')}: ${fmtFt(u.width_ft)} × ${fmtFt(u.height_ft || (u.top_ft - u.sill_ft))}` + (u.sill_ft !== undefined ? ` · sill ${fmtFt(u.sill_ft)}` : '');
      } else {
        const r = sizeText(o); if (r.b.isEmpty()) return; pos = r.b.getCenter(new THREE.Vector3()); pos.y = r.b.max.y + 0.05;
        const nice = o.name.replace(/^R1_[A-Z]+_/, '').replace(/_/g, ' ').toLowerCase();
        txt = `${nice}: ${r.txt}`;
      }
      const d = document.createElement('div'); d.className = 'lbl-dim'; d.textContent = txt;
      const l = new CSS2DObject(d); l.position.copy(pos); l.userData.src = o; dimsGroup.add(l);
    });
    for (const r of app.rooms) {   // room sizes
      const s = r.box.getSize(new THREE.Vector3());
      const d = document.createElement('div'); d.className = 'lbl-dim room'; d.textContent = `${r.name}: ${fmtFt(s.x / FT)} × ${fmtFt(s.z / FT)} (overall)`;
      const l = new CSS2DObject(d); l.position.copy(r.labelPos).setY(r.floorY + 0.05); dimsGroup.add(l);
    }
  }
  function showSelDims(o) {
    selDims.clear(); if (!o || !st.dims) return;
    const b = new THREE.Box3().setFromObject(o); if (b.isEmpty()) return;
    const mat = new THREE.LineBasicMaterial({ color: 0xd6336c, depthTest: false });
    const { min: a, max: z } = b; const off = 0.08;
    const segs = [
      [new THREE.Vector3(a.x, a.y, z.z + off), new THREE.Vector3(z.x, a.y, z.z + off), 'W', (z.x - a.x)],
      [new THREE.Vector3(z.x + off, a.y, a.z), new THREE.Vector3(z.x + off, a.y, z.z), 'D', (z.z - a.z)],
      [new THREE.Vector3(z.x + off, a.y, z.z + off), new THREE.Vector3(z.x + off, z.y, z.z + off), 'H', (z.y - a.y)],
    ];
    for (const [p, q, k, len] of segs) {
      const g = new THREE.BufferGeometry().setFromPoints([p, q]); const line = new THREE.Line(g, mat); line.renderOrder = 20; selDims.add(line);
      const d = document.createElement('div'); d.className = 'lbl-dim sel'; d.textContent = `${k} ${fmtFt(len / FT)}`;
      const l = new CSS2DObject(d); l.position.copy(p).add(q).multiplyScalar(0.5); selDims.add(l);
    }
  }
  function setDims(on) {
    st.dims = on; dimsGroup.visible = on; dimsGroup.children.forEach(l => l.visible = on && visibleSrc(l));
    $('dimsBtn').classList.toggle('on', on); showSelDims(app.selected); syncImmBar();
  }
  function visibleSrc(l) { for (let p = l.userData.src; p; p = p.parent) if (!p.visible) return false; return true; }

  // ---------------------------------------------------------------- immersive / full screen
  function setImmersive(on) {
    st.immersive = on;
    document.body.classList.toggle('immersive', on);
    if (on && !document.fullscreenElement) document.documentElement.requestFullscreen?.().catch(() => {});
    if (!on && document.fullscreenElement) document.exitFullscreen?.().catch(() => {});
    setTimeout(() => ctx.resize(), 60); syncImmBar();
  }
  document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && st.immersive) { st.immersive = false; document.body.classList.remove('immersive'); setTimeout(() => ctx.resize(), 60); } });
  function syncImmBar() {
    const b = $('immBar'); if (!b) return;
    b.querySelector('[data-act=lights]').classList.toggle('on', st.lightsOn);
    b.querySelector('[data-act=night]').classList.toggle('on', st.night);
    b.querySelector('[data-act=dims]').classList.toggle('on', st.dims);
    b.querySelector('[data-act=walk]').classList.toggle('on', walk.active);
  }
  $('immBtn').onclick = () => setImmersive(!st.immersive);
  $('lightsBtn').onclick = () => setLights(!st.lightsOn);
  $('nightBtn').onclick = () => setNight(!st.night);
  $('dimsBtn').onclick = () => setDims(!st.dims);
  $('openAllBtn').onclick = () => setAll(true);
  $('closeAllBtn').onclick = () => setAll(false);
  $('immBar').addEventListener('click', (e) => {
    const a = e.target.closest('button')?.dataset.act; if (!a) return;
    if (a === 'exit') setImmersive(false);
    else if (a === 'walk') { walk.active ? ctx.overview() : ctx.startWalk(); }
    else if (a === 'overview') ctx.overview();
    else if (a === 'lights') setLights(!st.lightsOn);
    else if (a === 'night') setNight(!st.night);
    else if (a === 'dims') setDims(!st.dims);
    else if (a === 'open') setAll(true);
    else if (a === 'close') setAll(false);
    else if (a === 'room1') ctx.goRoom('Room 1', 0);
    else if (a === 'balcony') ctx.goRoom('Room 1', 3);
    syncImmBar();
  });

  let dimT = 0;
  function update(dt) {
    animate(dt); updateHint();
    const now = performance.now();
    if (st.dims && now - dimT > 300) {   // show only the ~28 nearest labels, so the view never drowns in text
      dimT = now; const cp = cam().position;
      const camera = cam(); camera.updateMatrixWorld(); const v = new THREE.Vector3();
      const inView = (l) => { v.copy(l.position).project(camera); return v.z < 1 && Math.abs(v.x) < 0.95 && Math.abs(v.y) < 0.95; };
      const c = dimsGroup.children.map(l => ({ l, d: l.position.distanceTo(cp), ok: visibleSrc(l) && inView(l) })).filter(x => x.ok && x.d < 9).sort((a, b) => a.d - b.d);
      const occ = app.meshes.filter(m => { let cat = null; for (let p = m; p; p = p.parent) { if (!p.visible) return false; cat = cat || p.userData?.category; } return ['walls', 'roof', 'ceiling'].includes(cat); });
      const seen = (l) => {   // line of sight from the camera to the label (walls / ceilings block it)
        const dir = l.position.clone().sub(cp); const dist = dir.length(); ray.set(cp, dir.normalize()); ray.far = Math.max(0.01, dist - 0.25);
        return ray.intersectObjects(occ, false).length === 0; };
      dimsGroup.children.forEach(l => l.visible = false);
      let k = 0; for (const x of c) { if (k >= 28) break; if (seen(x.l)) { x.l.visible = true; k++; } }
    }
  }
  return { onModel, update, onSelect: showSelDims, toggle, toggleFor: (o) => toggle(groupOf(o)), isInteractive: (o) => !!groupOf(o),
           setAll, setLights, setNight, setDims, setImmersive, groups, state: st, lights, floorHit, interactiveHit, collides, obstacles: () => obstacles };
}
