// "Inside" mode: you stand in the flat at eye level.
//  - drag (mouse or one finger) to look around, including up at the ceiling
//  - WASD / arrows to move, Shift to run, mouse wheel to step forward / back
//  - R / PageUp raises your eye height, V / PageDown lowers it (to study ceilings)
//  - walls, furniture, closed glass doors etc. block you; floors and stairs carry you
import * as THREE from 'three';

export class Walkthrough {
  constructor({ app, persp, renderer, controls, CONFIG, onInfo }) {
    Object.assign(this, { app, cam: persp, renderer, controls, C: CONFIG, onInfo });
    this.active = false; this.keys = new Set(); this.yaw = 0; this.pitch = 0; this.feet = 0;
    this.eyeOffset = 0; this.nudge = 0; this.joy = { x: 0, y: 0 };   // joy: on-screen joystick (touch), -1..1
    this.turn = 0; this.look = 0; this.auto = null; this.lookK = 1;   // simple mode: turn / look buttons, tap-to-walk target
    this.ray = new THREE.Raycaster(); this.onChange = null; this.drag = null; this.dragMoved = 0;
    const el = renderer.domElement;
    document.addEventListener('keydown', (e) => {
      if (!this.active || /INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName)) return;
      this.keys.add(e.code);
      if (e.code.startsWith('Arrow') || e.code === 'Space' || e.code.startsWith('Page')) e.preventDefault();
    });
    document.addEventListener('keyup', (e) => this.keys.delete(e.code));
    window.addEventListener('blur', () => this.keys.clear());
    el.addEventListener('pointerdown', (e) => {
      if (!this.active || (e.pointerType === 'mouse' && e.button !== 0)) return;
      this.drag = { x: e.clientX, y: e.clientY, id: e.pointerId }; this.dragMoved = 0;
    });
    window.addEventListener('pointermove', (e) => {
      if (!this.active || !this.drag || e.pointerId !== this.drag.id) return;
      const dx = e.clientX - this.drag.x, dy = e.clientY - this.drag.y; this.drag.x = e.clientX; this.drag.y = e.clientY;
      this.dragMoved += Math.abs(dx) + Math.abs(dy);
      const k = (e.pointerType === 'touch' ? 0.006 : 0.0045) * this.lookK;
      this.yaw += dx * k; this.pitch += dy * k;      // "grab the view": drag left = turn right, drag down = look up
      this.pitch = Math.max(-1.45, Math.min(1.45, this.pitch));
    });
    window.addEventListener('pointerup', (e) => { if (this.drag && e.pointerId === this.drag.id) this.drag = null; });
    el.addEventListener('wheel', (e) => { if (!this.active) return; e.preventDefault(); this.nudge += -Math.sign(e.deltaY) * Math.min(0.6, Math.abs(e.deltaY) * 0.004); }, { passive: false });
  }

  visibleIn(cats) {
    return this.app.meshes.filter(m => {
      let cat = null, vis = true;
      for (let p = m; p; p = p.parent) { if (!p.visible) { vis = false; break; } if (!cat && p.userData?.category) cat = p.userData.category; }
      return vis && cats.includes(cat);
    });
  }

  groundAt(x, z, fromY, cats = this.C.groundCategories, far = 4) {
    this.ray.set(new THREE.Vector3(x, fromY, z), new THREE.Vector3(0, -1, 0)); this.ray.far = far;
    const h = this.ray.intersectObjects(this.visibleIn(cats), false);
    return h.length ? h[0] : null;
  }

  enter(pos, target) {
    // only start if we are inside the building: a floor below and within ~3 m
    const g = this.groundAt(pos.x, pos.z, pos.y + 0.2, ['floors', 'stairs'], 3.2);
    if (!g) return false;
    this.feet = g.point.y; this.eyeOffset = 0; this.nudge = 0;
    this.cam.position.set(pos.x, this.feet + this.C.eyeHeight, pos.z);
    const d = target.clone().sub(this.cam.position);
    this.yaw = Math.atan2(-d.x, -d.z);
    this.pitch = Math.max(-0.6, Math.min(0.6, Math.atan2(d.y, Math.hypot(d.x, d.z))));
    this.cam.rotation.set(this.pitch, this.yaw, 0, 'YXZ');
    this.active = true; this.controls.enabled = false; this.app.tween = null;
    this.onChange && this.onChange(true);
    return true;
  }

  exit() {
    if (!this.active) return;
    this.active = false; this.keys.clear(); this.drag = null;
    if (document.pointerLockElement) document.exitPointerLock();
    // pivot slightly below eye level straight ahead, so the overview camera keeps the same view without a jump
    const look = new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
    this.controls.target.copy(this.cam.position).addScaledVector(look, 2); this.controls.target.y -= 0.3;
    this.controls.enabled = true; this.controls.update();
    this.onChange && this.onChange(false);
  }

  blocked(from, dir, dist) {
    if (dist <= 0) return false;
    const walls = this._walls;
    for (const hgt of [0.45, 1.2, 1.7]) {
      const o = new THREE.Vector3(from.x, this.feet + hgt, from.z);
      this.ray.set(o, dir); this.ray.far = dist + this.C.bodyRadius;
      if (this.ray.intersectObjects(walls, false).length) return true;
    }
    return false;
  }

  update(dt) {
    const k = this.keys, C = this.C;
    let f = 0, s = 0;
    if (k.has('KeyW') || k.has('ArrowUp')) f += 1;
    if (k.has('KeyS') || k.has('ArrowDown')) f -= 1;
    if (k.has('KeyD') || k.has('ArrowRight')) s += 1;
    if (k.has('KeyA') || k.has('ArrowLeft')) s -= 1;
    f -= this.joy.y; s += this.joy.x;
    if (this.turn) this.yaw -= this.turn * dt * 1.3;                       // ↰ / ↱ buttons
    if (this.look) this.pitch = Math.max(-1.2, Math.min(1.45, this.pitch + this.look * dt * 0.9));
    if (this.auto) {                                                        // tap-to-walk: turn towards the spot, then walk to it
      const dx = this.auto.x - this.cam.position.x, dz = this.auto.z - this.cam.position.z, dist = Math.hypot(dx, dz);
      if (dist < 0.25 || f || s || this.turn) { this.auto = null; this.onAutoStop && this.onAutoStop(dist < 0.25); }
      else {
        const want = Math.atan2(-dx, -dz); let d = want - this.yaw; d = Math.atan2(Math.sin(d), Math.cos(d));
        this.yaw += Math.sign(d) * Math.min(Math.abs(d), dt * 2.4);
        this.auto.trying = Math.abs(d) < 0.7; if (this.auto.trying) f = Math.min(1, dist * 1.2);
        this.pitch += (0 - this.pitch) * Math.min(1, dt * 2);               // level the view while walking
        this.auto.t = (this.auto.t || 0) + dt;
      }
    }
    if (k.has('KeyR') || k.has('PageUp')) this.eyeOffset = Math.min(1.15, this.eyeOffset + dt * 0.9);
    if (k.has('KeyV') || k.has('PageDown')) this.eyeOffset = Math.max(-1.0, this.eyeOffset - dt * 0.9);
    const speed = C.walkSpeed * ((k.has('ShiftLeft') || k.has('ShiftRight')) ? C.runMultiplier : 1);
    const fwd = new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
    const right = new THREE.Vector3(Math.cos(this.yaw), 0, -Math.sin(this.yaw));
    const mv = fwd.clone().multiplyScalar(f).add(right.multiplyScalar(s));
    if (mv.lengthSq() > 0) mv.normalize().multiplyScalar(speed * dt * Math.min(1, Math.hypot(f, s)));
    if (this.nudge) {   // mouse wheel: step forward / back smoothly
      const step = Math.sign(this.nudge) * Math.min(Math.abs(this.nudge), dt * 3.0);
      mv.addScaledVector(fwd, step); this.nudge -= step; if (Math.abs(this.nudge) < 1e-3) this.nudge = 0;
    }
    this._walls = this.visibleIn(C.collideCategories);
    const p = this.cam.position.clone();
    // axis-separated moves so you slide along walls
    for (const axis of ['x', 'z']) {
      const d = mv[axis]; if (!d) continue;
      const dir = new THREE.Vector3(axis === 'x' ? Math.sign(d) : 0, 0, axis === 'z' ? Math.sign(d) : 0);
      if (this.blocked(p, dir, Math.abs(d))) { if (this.nudge) this.nudge = 0; continue; }
      const np = p.clone(); np[axis] += d;
      const g = this.groundAt(np.x, np.z, this.feet + C.maxStepUp + 0.02);
      if (!g) continue;                                   // no floor there (edge / outside) -> stay
      if (this.feet - g.point.y > 1.0) continue;          // big drop -> stay
      p.copy(np); this._ground = g;
    }
    const g = this.groundAt(p.x, p.z, this.feet + C.maxStepUp + 0.02);
    if (g) { this._ground = g; const ty = g.point.y; this.feet += (ty - this.feet) * Math.min(1, dt * 14); }
    let eyeY = this.feet + C.eyeHeight + this.eyeOffset;
    if (this.eyeOffset > 0) {   // never push your head into the ceiling / a beam / a false ceiling
      this.ray.set(new THREE.Vector3(p.x, this.feet + 1.0, p.z), new THREE.Vector3(0, 1, 0)); this.ray.far = 4;
      const h = this.ray.intersectObjects(this.visibleIn(['ceiling', 'roof', 'beams', 'lighting']), false);
      if (h.length) { const maxY = h[0].point.y - 0.25; if (eyeY > maxY) { eyeY = Math.max(this.feet + 1.0, maxY); this.eyeOffset = eyeY - this.feet - C.eyeHeight; } }
    }
    if (this.auto) {   // stuck against something? stop trying
      const moved = Math.hypot(p.x - this.cam.position.x, p.z - this.cam.position.z);
      this.auto.still = moved < 0.002 && this.auto.trying ? (this.auto.still || 0) + dt : 0;
      if (this.auto.still > 0.5) { this.auto = null; this.onAutoStop && this.onAutoStop(false); }
    }
    this.cam.position.set(p.x, eyeY, p.z);
    this.cam.rotation.set(this.pitch, this.yaw, 0, 'YXZ');
    // info line
    let room = null;
    for (let o = this._ground?.object; o; o = o.parent) if (o.userData?.room) { room = o.userData.room; break; }
    const FT = 0.3048;
    this.onInfo && this.onInfo(`${room ? 'In ' + room : (this._ground ? 'On ' + this._ground.object.name : '')} · eye ${((this.C.eyeHeight + this.eyeOffset) / FT).toFixed(1)} ft above floor`);
  }
}
