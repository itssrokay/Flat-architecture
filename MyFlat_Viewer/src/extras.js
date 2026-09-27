// Comfort features:
//  - collapsible side panels and control sections
//  - "image-style" zoom: the wheel zooms towards the exact point under the cursor
//  - wide lens + "Look at ceiling" when you are inside
//  - hover info: point at anything to read what it is
//  - room size: focused wall-by-wall dimensions of the room you are in
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const FT = 0.3048;
const store = {
  get(k) { try { return localStorage.getItem('myflat.' + k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem('myflat.' + k, v); } catch (e) { } },
};
function pretty(n) { return (n || '').replace(/^R1_(DEF|OPA|OPB|OPC|A|B|C)_/, '').replace(/\.\d+$/, '').replace(/_/g, ' ').toLowerCase().replace(/^\w/, c => c.toUpperCase()); }

export function setupExtras(ctx) {
  const { app, scene, renderer, controls, walk, persp, $, fmtFt, CONFIG } = ctx;
  const cam = () => ctx.getCamera();
  const el = renderer.domElement;
  const visible = (o) => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };
  const catOf = (o) => { for (let p = o; p; p = p.parent) if (p.userData?.category) return p.userData.category; return null; };
  const ownerOf = (o) => { for (let p = o; p; p = p.parent) if (p.userData?.category) return p; return o; };
  const ray = new THREE.Raycaster();
  const ndc = (ev) => { const r = el.getBoundingClientRect(); return new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1); };
  function pickAll(v, skip = []) {
    ray.setFromCamera(v, cam()); ray.far = Infinity;
    const c = app.meshes.filter(m => visible(m) && !skip.includes(catOf(m)));
    return ray.intersectObjects(c, false);
  }

  // =================================================================== 1. panels
  const body = document.body;
  function setLeft(hide) { body.classList.toggle('no-left', hide); $('leftTab').textContent = hide ? '›' : '‹'; $('leftTab').title = hide ? 'Show left panel ( [ )' : 'Hide left panel ( [ )'; store.set('noLeft', hide ? 1 : 0); ctx.resize(); }
  function setRight(hide) { body.classList.toggle('no-right', hide); $('rightTab').textContent = hide ? '‹' : '›'; $('rightTab').title = hide ? 'Show right panel ( ] )' : 'Hide right panel ( ] )'; store.set('noRight', hide ? 1 : 0); ctx.resize(); }
  $('leftTab').onclick = () => setLeft(!body.classList.contains('no-left'));
  $('rightTab').onclick = () => setRight(!body.classList.contains('no-right'));
  setLeft(store.get('noLeft') === '1'); setRight(store.get('noRight') === '1');
  document.querySelectorAll('#dock section').forEach((sec, i) => {
    const h = sec.querySelector('h4'); if (!h) return;
    const key = 'sec.' + (sec.id || h.textContent.trim());
    h.classList.add('sec-head'); h.title = 'Minimise / expand';
    h.onclick = () => { sec.classList.toggle('min'); store.set(key, sec.classList.contains('min') ? 1 : 0); };
    if (store.get(key) === '1') sec.classList.add('min');
  });
  // right panel blocks (design notes, inspector …) fold too
  document.querySelectorAll('#right > h3, #left > h3').forEach(h => {
    const key = 'blk.' + h.textContent.trim();
    h.classList.add('blk-head'); h.title = 'Minimise / expand';
    const fold = (min) => { let n = h.nextElementSibling; while (n && n.tagName !== 'H3') { n.classList.toggle('folded', min); n = n.nextElementSibling; } h.classList.toggle('min', min); };
    h.onclick = () => { const m = !h.classList.contains('min'); fold(m); store.set(key, m ? 1 : 0); };
    if (store.get(key) === '1') fold(true);
  });

  // =================================================================== 2. image-style zoom
  // Every wheel notch scales the whole view about the point under the cursor, exactly like zooming a
  // photo: that point stays under the mouse, so you can zoom straight into a corner of the balcony.
  let zoom = null;          // { P, log }  pending zoom, applied smoothly over a few frames
  const _v = new THREE.Vector3();
  function zoomPoint(v) {
    const hits = pickAll(v, [CONFIG.planCategory]);
    if (hits.length) return hits[0].point.clone();
    // nothing under the cursor: use the pivot's depth
    ray.setFromCamera(v, cam());
    const n = cam().getWorldDirection(new THREE.Vector3());
    const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(n, controls.target);
    return ray.ray.intersectPlane(plane, new THREE.Vector3()) || controls.target.clone();
  }
  el.addEventListener('wheel', (e) => {
    if (walk.active) {                         // inside: pinch / Ctrl+wheel = lens (field of view)
      if (e.ctrlKey || e.altKey) { e.preventDefault(); e.stopImmediatePropagation(); setFov(walkFov + e.deltaY * (e.ctrlKey ? 0.35 : 0.06)); }
      return;
    }
    if (cam().isOrthographicCamera) return;    // orthographic views keep OrbitControls' zoom-to-cursor
    e.preventDefault();
    let d = e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 400 : 1);
    const k = e.ctrlKey ? 0.012 : 0.0018;      // trackpad pinch sends small ctrl+wheel deltas
    const log = THREE.MathUtils.clamp(d * k, -0.7, 0.7);
    const P = zoomPoint(ndc(e));
    if (zoom && zoom.P.distanceTo(P) < 0.5) zoom.log += log; else zoom = { P, log };
    app.tween = null; app.pendingWalk = null;
  }, { passive: false, capture: true });
  function stepZoom(dt) {
    if (!zoom) return;
    const c = cam(), part = zoom.log * Math.min(1, dt * 14);
    let s = Math.exp(part);
    const dist = c.position.distanceTo(zoom.P);
    if (dist * s < 0.25) s = 0.25 / dist;                                   // don't pass through the point
    if (c.position.distanceTo(app.center) * s > Math.max(80, app.size * 6) && s > 1) s = 1;   // don't fly away
    c.position.sub(zoom.P).multiplyScalar(s).add(zoom.P);
    controls.target.sub(zoom.P).multiplyScalar(s).add(zoom.P);
    if (c.position.y < 0.3) { const dy = 0.3 - c.position.y; c.position.y += dy; controls.target.y += dy; }
    zoom.log -= part; if (Math.abs(zoom.log) < 1e-3 || s === 1) zoom = null;
  }

  // =================================================================== 3. lens + ceiling (inside)
  let walkFov = 60, ceilingMode = null;
  function setFov(f) {
    walkFov = THREE.MathUtils.clamp(f, 35, 110);
    if (walk.active) { persp.fov = walkFov; persp.updateProjectionMatrix(); }
    $('fovRange').value = walkFov; $('fovVal').textContent = Math.round(walkFov) + '°';
  }
  $('fovRange').oninput = () => setFov(+$('fovRange').value);
  function roomUnderYou() { for (let o = walk._ground?.object; o; o = o.parent) if (o.userData?.room) return o.userData.room; return null; }
  function lookAtCeiling(on = !ceilingMode) {
    if (!walk.active) return;
    if (on) {
      ceilingMode = { fov: walkFov, pitch: walk.pitch, eye: walk.eyeOffset, pos: walk.cam.position.clone() };
      // stand in the middle of the room, eyes low, look straight up through a wide lens
      const rn = roomUnderYou(); const room = app.rooms.find(r => r.name === rn);
      if (room) { const p = room.labelPos || room.center; walk.cam.position.x = p.x; walk.cam.position.z = p.z; }
      walk.yaw = Math.round(walk.yaw / (Math.PI / 2)) * (Math.PI / 2);   // square to the walls
      walk.pitch = 1.45; walk.eyeOffset = -0.55; setFov(100);
    } else {
      const m = ceilingMode; ceilingMode = null;
      walk.pitch = 0; walk.eyeOffset = 0; setFov(m ? m.fov : 60);
    }
    $('ceilBtn').classList.toggle('on', !!ceilingMode);
  }
  $('ceilBtn').onclick = () => lookAtCeiling();
  document.addEventListener('keydown', (e) => {
    if (/INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName)) return;
    if (e.code === 'BracketLeft') setLeft(!body.classList.contains('no-left'));
    if (e.code === 'BracketRight') setRight(!body.classList.contains('no-right'));
    if (e.code === 'KeyI') setHover(!hoverOn);
    if (e.code === 'KeyM') setRoomDims(!roomDimsOn);
    if (!walk.active) return;
    if (e.code === 'KeyC') lookAtCeiling();
    if (e.code === 'Minus' || e.code === 'NumpadSubtract') setFov(walkFov + 8);
    if (e.code === 'Equal' || e.code === 'NumpadAdd') setFov(walkFov - 8);
  });
  function onWalkChange(on) {
    if (on) { persp.fov = walkFov; } else { persp.fov = 60; ceilingMode = null; $('ceilBtn').classList.remove('on'); }
    persp.updateProjectionMatrix();
  }

  // =================================================================== 4. hover info
  let hoverOn = false, hoverObj = null, hoverT = 0, lastEv = null;
  const hoverBox = new THREE.Box3Helper(new THREE.Box3(), 0x2b8cff); hoverBox.visible = false; hoverBox.raycast = () => { }; scene.add(hoverBox);
  function setHover(on) {
    hoverOn = on; $('hoverBtn').classList.toggle('on', on);
    document.querySelector('#immBar [data-act=hover]')?.classList.toggle('on', on);
    if (!on) { $('hoverTip').classList.add('hidden'); hoverBox.visible = false; hoverObj = null; }
  }
  $('hoverBtn').onclick = () => setHover(!hoverOn);
  el.addEventListener('pointermove', (e) => { lastEv = e; });
  el.addEventListener('pointerleave', () => { lastEv = null; if (hoverOn) { $('hoverTip').classList.add('hidden'); hoverBox.visible = false; } });
  function sizeText(o) {
    const d = o.userData?.dims_ft;
    if (Array.isArray(d) && d.length === 3) return `${fmtFt(Math.max(d[0], d[1]))} wide × ${fmtFt(Math.min(d[0], d[1]))} deep × ${fmtFt(d[2])} high`;
    const s = new THREE.Box3().setFromObject(o).getSize(new THREE.Vector3());
    return `${fmtFt(Math.max(s.x, s.z) / FT)} × ${fmtFt(Math.min(s.x, s.z) / FT)} × ${fmtFt(s.y / FT)} high <span class="dim">(outer box)</span>`;
  }
  const catLabel = (c) => (CONFIG.categories.find(x => x.key === c) || {}).label || c;
  const esc = (t) => String(t ?? '').replace(/[&<>]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch]));
  function updateHover() {
    if (!hoverOn) return;
    const now = performance.now(); if (now - hoverT < 70) return; hoverT = now;
    const tip = $('hoverTip');
    if (!lastEv) return;
    // inside with the mouse still, use the crosshair
    const v = ndc(lastEv);
    const hits = pickAll(v, [CONFIG.planCategory, 'context']);
    const h = hits[0];
    if (!h) { tip.classList.add('hidden'); hoverBox.visible = false; hoverObj = null; return; }
    const o = ownerOf(h.object);
    if (o !== hoverObj) {
      hoverObj = o; const u = o.userData || {};
      const st = u.status ? (CONFIG.status[u.status]?.label || u.status) : null;
      const rows = [
        ['Type', esc(catLabel(u.category))],
        ['Size', sizeText(o)],
        u.spec ? ['Spec', esc(u.spec)] : null,
        u.room ? ['Room', esc(u.room)] : null,
        u.design_option ? ['Design', esc(u.design_option)] : null,
        st ? ['Status', esc(st)] : null,
        u.basis ? ['Basis', esc(u.basis)] : null,
        ctx.isInteractive(o) ? ['', '<i>double-click (or click inside) to open / close</i>'] : null,
      ].filter(Boolean);
      tip.innerHTML = `<b>${esc(u.label || pretty(o.name))}</b><table>${rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('')}</table>`;
      hoverBox.box.setFromObject(o); hoverBox.visible = true;
    } else hoverBox.box.setFromObject(o);
    const r = el.getBoundingClientRect(), vp = $('viewport').getBoundingClientRect();
    let x = lastEv.clientX - vp.left + 16, y = lastEv.clientY - vp.top + 16;
    tip.classList.remove('hidden');
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    if (x + tw > vp.width - 8) x = lastEv.clientX - vp.left - tw - 12;
    if (y + th > vp.height - 30) y = Math.max(8, lastEv.clientY - vp.top - th - 12);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }

  // =================================================================== 5. room size (focused)
  let roomDimsOn = false, roomDimsFor = null, rdT = 0;
  const rdGroup = new THREE.Group(); rdGroup.visible = false; scene.add(rdGroup);
  const rdMat = new THREE.LineBasicMaterial({ color: 0xd6336c, depthTest: false, transparent: true });
  const rdMatSoft = new THREE.LineBasicMaterial({ color: 0xd6336c, depthTest: false, transparent: true, opacity: 0.45 });
  function setRoomDims(on) {
    roomDimsOn = on; rdGroup.visible = on; $('roomDimsBtn').classList.toggle('on', on);
    document.querySelector('#immBar [data-act=roomdims]')?.classList.toggle('on', on);
    rdGroup.traverse(o => { if (o.isCSS2DObject) o.visible = on; });
    if (on) { roomDimsFor = null; refreshRoomDims(true); }
  }
  $('roomDimsBtn').onclick = () => setRoomDims(!roomDimsOn);
  function focusRoom() {
    if (walk.active) { const r = roomUnderYou(); if (r) return r; }
    for (let o = app.selected; o; o = o.parent) if (o.userData?.room) return o.userData.room;
    return app.lastRoom || (app.rooms.find(r => r.name === 'Room 1') || app.rooms[0])?.name;
  }
  // outline of a floor: boundary edges of its upward-facing triangles, chained into loops
  function floorOutline(obj) {
    const key = (x, z) => `${Math.round(x * 200)},${Math.round(z * 200)}`;
    const edges = new Map(), pts = new Map(); let top = -Infinity;
    const tris = [];
    obj.updateMatrixWorld(true);
    obj.traverse(m => {
      if (!m.isMesh) return;
      const g = m.geometry, pos = g.attributes.position, idx = g.index;
      const n = idx ? idx.count : pos.count;
      const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), nrm = new THREE.Vector3();
      for (let i = 0; i < n; i += 3) {
        const ia = idx ? idx.getX(i) : i, ib = idx ? idx.getX(i + 1) : i + 1, ic = idx ? idx.getX(i + 2) : i + 2;
        a.fromBufferAttribute(pos, ia).applyMatrix4(m.matrixWorld); b.fromBufferAttribute(pos, ib).applyMatrix4(m.matrixWorld); c.fromBufferAttribute(pos, ic).applyMatrix4(m.matrixWorld);
        nrm.subVectors(c, b).cross(new THREE.Vector3().subVectors(a, b)).normalize();
        if (nrm.y < 0.95) continue;
        tris.push([a.clone(), b.clone(), c.clone()]); top = Math.max(top, a.y, b.y, c.y);
      }
    });
    for (const t of tris) {
      if (Math.abs(t[0].y - top) > 0.01) continue;
      for (let i = 0; i < 3; i++) {
        const p = t[i], q = t[(i + 1) % 3];
        const kp = key(p.x, p.z), kq = key(q.x, q.z); pts.set(kp, p); pts.set(kq, q);
        const k = kp < kq ? kp + '|' + kq : kq + '|' + kp;
        edges.set(k, (edges.get(k) || 0) + 1);
      }
    }
    const adj = new Map();
    for (const [k, n] of edges) if (n === 1) { const [p, q] = k.split('|'); (adj.get(p) || adj.set(p, []).get(p)).push(q); (adj.get(q) || adj.set(q, []).get(q)).push(p); }
    const loops = [], used = new Set();
    for (const start of adj.keys()) {
      if (used.has(start)) continue;
      const loop = [start]; used.add(start); let prev = null, cur = start;
      for (let guard = 0; guard < 2000; guard++) {
        const nx = (adj.get(cur) || []).find(q => q !== prev && (!used.has(q) || (q === start && loop.length > 2)));
        if (!nx || nx === start) break;
        loop.push(nx); used.add(nx); prev = cur; cur = nx;
      }
      if (loop.length > 2) loops.push(loop.map(k => pts.get(k)));
    }
    // simplify: drop points on straight runs
    const simp = loops.map(L => L.filter((p, i) => {
      const a = L[(i - 1 + L.length) % L.length], c = L[(i + 1) % L.length];
      const ux = p.x - a.x, uz = p.z - a.z, vx = c.x - p.x, vz = c.z - p.z;
      return Math.abs(ux * vz - uz * vx) > 1e-4 * Math.hypot(ux, uz) * Math.hypot(vx, vz) + 1e-7;
    }));
    const area = L => { let s = 0; for (let i = 0; i < L.length; i++) { const p = L[i], q = L[(i + 1) % L.length]; s += p.x * q.z - q.x * p.z; } return s / 2; };
    simp.sort((A, B) => Math.abs(area(B)) - Math.abs(area(A)));
    return { loop: simp[0] || [], top, area: simp.length ? Math.abs(area(simp[0])) - simp.slice(1).reduce((s, L) => s + Math.abs(area(L)), 0) : 0, signed: simp.length ? area(simp[0]) : 0 };
  }
  function label(text, pos, cls = '') {
    const d = document.createElement('div'); d.className = 'lbl-roomdim ' + cls; d.innerHTML = text;
    const o = new CSS2DObject(d); o.position.copy(pos); o.visible = roomDimsOn; rdGroup.add(o); return o;
  }
  function line(a, b, mat = rdMat) { const g = new THREE.BufferGeometry().setFromPoints([a, b]); const l = new THREE.Line(g, mat); l.renderOrder = 999; l.raycast = () => { }; rdGroup.add(l); return l; }
  function clearRD() { rdGroup.traverse(o => { if (o.isCSS2DObject) o.element.remove(); }); rdGroup.clear(); }
  function refreshRoomDims(force) {
    const name = focusRoom(); if (!force && name === roomDimsFor) return;
    roomDimsFor = name; clearRD();
    const room = app.rooms.find(r => r.name === name); if (!room) return;
    const { loop, top, area, signed } = floorOutline(room.floor);
    if (loop.length < 3) return;
    const y = top + 0.03, inward = signed > 0 ? 1 : -1;   // polygon winding decides which side is inside
    const bb = new THREE.Box2(); loop.forEach(p => bb.expandByPoint(new THREE.Vector2(p.x, p.z)));
    for (let i = 0; i < loop.length; i++) {
      const p = loop[i], q = loop[(i + 1) % loop.length];
      const len = Math.hypot(q.x - p.x, q.z - p.z); if (len < 0.05) continue;
      const dx = (q.x - p.x) / len, dz = (q.z - p.z) / len;
      // inward normal of the edge (left of p->q for CCW in x/z)
      const nx = -dz * inward, nz = dx * inward;
      const off = 0.18;
      const a = new THREE.Vector3(p.x + nx * off, y, p.z + nz * off), b = new THREE.Vector3(q.x + nx * off, y, q.z + nz * off);
      line(a, b);
      line(new THREE.Vector3(p.x, y, p.z), a, rdMatSoft); line(new THREE.Vector3(q.x, y, q.z), b, rdMatSoft);
      const mid = a.clone().add(b).multiplyScalar(0.5); mid.x += nx * 0.12; mid.z += nz * 0.12;
      label(fmtFt(len / FT), mid, len < 0.45 ? 'small' : '');
    }
    // ceiling height, measured straight up from the room's middle
    const c = room.labelPos || room.center;
    ray.set(new THREE.Vector3(c.x, top + 0.1, c.z), new THREE.Vector3(0, 1, 0)); ray.far = 6;
    const up = ray.intersectObjects(app.meshes.filter(m => visible(m) && ['ceiling', 'roof', 'beams'].includes(catOf(m))), false)[0];
    const ch = up ? up.point.y - top : null;
    const w = bb.max.x - bb.min.x, d = bb.max.y - bb.min.y;
    label(`<b>${name}</b><br>${fmtFt(w / FT)} × ${fmtFt(d / FT)} overall · ${(area / FT / FT).toFixed(0)} sq ft` + (ch ? `<br>floor to ceiling ${fmtFt(ch / FT)}` : ''), new THREE.Vector3(c.x, top + 0.9, c.z), 'title');
    if (ch) {
      // vertical line in the first corner
      const p = loop[0], q = loop[1], r2 = loop[loop.length - 1];
      const v1 = new THREE.Vector2(q.x - p.x, q.z - p.z).normalize(), v2 = new THREE.Vector2(r2.x - p.x, r2.z - p.z).normalize();
      const cx = p.x + (v1.x + v2.x) * 0.3, cz = p.z + (v1.y + v2.y) * 0.3;
      line(new THREE.Vector3(cx, top, cz), new THREE.Vector3(cx, top + ch, cz));
      label(fmtFt(ch / FT), new THREE.Vector3(cx, top + ch / 2, cz), 'vert');
    }
    $('roomDimsInfo') && ($('roomDimsInfo').textContent = `Room size: ${name}`);
  }

  $('immBar').addEventListener('click', (e) => {
    const a = e.target.closest('button')?.dataset.act;
    if (a === 'hover') setHover(!hoverOn); else if (a === 'roomdims') setRoomDims(!roomDimsOn);
  });

  // =================================================================== toast
  let toastT = 0;
  function toast(msg) { const t = $('toast'); t.textContent = msg; t.classList.remove('hidden'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.add('hidden'), 3200); }

  function update(dt) {
    controls.enableZoom = !!cam().isOrthographicCamera;
    if (!walk.active) stepZoom(dt); else zoom = null;
    updateHover();
    if (roomDimsOn) { const now = performance.now(); if (now - rdT > 400) { rdT = now; refreshRoomDims(false); } }
  }
  function onModel() { hoverObj = null; hoverBox.visible = false; if (roomDimsOn) { roomDimsFor = null; refreshRoomDims(true); } }
  return { update, onModel, onWalkChange, setLeft, setRight, setHover, setRoomDims, lookAtCeiling, setFov, toast, floorOutline,
    state: () => ({ hoverOn, roomDimsOn, roomDimsFor, walkFov, ceiling: !!ceilingMode, zooming: !!zoom }),
    roomDimLabels: () => rdGroup.children.filter(o => o.isCSS2DObject).map(o => o.element.innerText || o.element.textContent) };
}
