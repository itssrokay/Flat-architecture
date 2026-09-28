// Easy mode for phones (made for someone who has never used a 3D app):
//  - big labelled buttons: turn left / walk forward / turn right, look up / step back / look down
//  - tap the floor to walk there by itself; tap a door, window or wardrobe to open / close it
//  - "Places": a big list of spots to jump to (Room 1 views, the balcony, the ceiling, every room)
//  - "Whole house": the plan from above; tap any room to go inside
//  - "Straighten": level the view again
// Everything else (joystick, top-bar tools, side panels) is tucked away; "All controls" brings it back.
import * as THREE from 'three';

export function setupSimple(ctx) {
  const { app, $, walk, imm, ex, renderer, scene, CONFIG } = ctx;
  const body = document.body, el = renderer.domElement;
  const store = { get(k) { try { return localStorage.getItem('myflat.' + k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem('myflat.' + k, v); } catch (e) { } } };
  let lang = ctx.lang || 'en';
  const L = (en, hi) => (lang === 'hi' ? hi : en);
  const ROOM_HI = { 'Room 1': 'कमरा 1', 'Room 2': 'कमरा 2', 'Kitchen': 'रसोई', 'Bathroom 1': 'बाथरूम 1', 'Bathroom 2': 'बाथरूम 2', 'Passage': 'गलियारा', 'Hall': 'हॉल', 'Balcony': 'बालकनी', 'Stair': 'सीढ़ी', 'Open Square': 'खुला आँगन' };
  const roomName = (n) => (lang === 'hi' ? ROOM_HI[n] || n : n);

  // ------------------------------------------------ UI
  const ui = document.createElement('div'); ui.id = 'simpleUI'; ui.className = 'hidden';
  $('viewport').appendChild(ui);
  const sheet = document.createElement('div'); sheet.id = 'placesSheet'; sheet.className = 'hidden'; $('viewport').appendChild(sheet);
  const help = document.createElement('div'); help.id = 'simpleHelp'; help.className = 'hidden'; $('viewport').appendChild(help);
  function build() {
    ui.innerHTML = `
      <div class="s-top">
        <div class="s-row">
          <button class="s-btn" data-a="places"><b>📍</b>${L('Places', 'जगहें')}</button>
          <button class="s-btn" data-a="house"><b>🏠</b>${L('Whole house', 'पूरा घर')}</button>
          <button class="s-btn" data-a="level"><b>↺</b>${L('Straighten', 'सीधा करें')}</button>
          <button class="s-btn" data-a="help"><b>?</b>${L('Help', 'मदद')}</button>
        </div>
        <div class="s-where" id="sWhere">📍</div>
      </div>
      <div class="s-tip" id="sTip"></div>
      <div class="s-pad" id="sPad">
        <button data-h="turnL"><b>↰</b><span>${L('Turn left', 'बाएँ मुड़ें')}</span></button>
        <button data-h="fwd" class="s-main"><b>▲</b><span>${L('Walk', 'आगे चलें')}</span></button>
        <button data-h="turnR"><b>↱</b><span>${L('Turn right', 'दाएँ मुड़ें')}</span></button>
        <button data-h="up"><b>⤒</b><span>${L('Look up', 'ऊपर देखें')}</span></button>
        <button data-h="back"><b>▼</b><span>${L('Step back', 'पीछे')}</span></button>
        <button data-h="down"><b>⤓</b><span>${L('Look down', 'नीचे देखें')}</span></button>
      </div>`;
    ui.querySelectorAll('.s-btn').forEach(b => b.onclick = () => action(b.dataset.a));
    ui.querySelectorAll('.s-pad button').forEach(b => {
      const on = (e) => { e.preventDefault(); e.stopPropagation(); try { b.setPointerCapture(e.pointerId); } catch (x) { } hold(b.dataset.h, true); b.classList.add('down'); };
      const off = () => { hold(b.dataset.h, false); b.classList.remove('down'); };
      b.addEventListener('pointerdown', on); b.addEventListener('pointerup', off); b.addEventListener('pointercancel', off); b.addEventListener('lostpointercapture', off);
      b.addEventListener('contextmenu', (e) => e.preventDefault());
    });
    help.innerHTML = `<div class="h-card"><h3>${L('How to look around your flat', 'अपना फ़्लैट कैसे देखें')}</h3>
      <div class="h-row"><b>▲ ▼ ↰ ↱</b><span>${L('Press and hold the big buttons at the bottom to walk and turn.', 'नीचे के बड़े बटन दबाकर रखें — चलने और मुड़ने के लिए।')}</span></div>
      <div class="h-row"><b>👆</b><span>${L('Tap the floor anywhere — you will walk there by yourself.', 'फ़र्श पर कहीं भी टैप करें — आप अपने आप वहाँ चले जाएँगे।')}</span></div>
      <div class="h-row"><b>🚪</b><span>${L('Tap a door, window or wardrobe to open it. Tap again to close.', 'दरवाज़े, खिड़की या अलमारी को टैप करें — खुल जाएगी। दोबारा टैप करें — बंद।')}</span></div>
      <div class="h-row"><b>☝️</b><span>${L('Slide one finger on the screen to look around.', 'स्क्रीन पर एक उँगली सरकाएँ — चारों ओर देखें।')}</span></div>
      <div class="h-row"><b>📍</b><span>${L('Places: jump straight to the balcony, the wardrobe, the ceiling or any room.', 'जगहें: सीधे बालकनी, अलमारी, छत या किसी भी कमरे में पहुँचें।')}</span></div>
      <div class="h-row"><b>↺</b><span>${L('Lost? Press Straighten, or Places → Room 1.', 'भटक गए? "सीधा करें" दबाएँ, या जगहें → कमरा 1।')}</span></div>
      <button class="s-btn h-ok">${L('OK, got it', 'ठीक है, समझ गया')}</button></div>`;
    help.querySelector('.h-ok').onclick = () => { help.classList.add('hidden'); store.set('simpleHelpSeen', 1); };
    $('simpleBtn').textContent = on ? L('⚙ All controls', '⚙ सारे कंट्रोल') : L('👍 Easy mode', '👍 आसान मोड');
    tipText();
  }
  function tipText() {
    const t = $('sTip'); if (!t) return;
    t.textContent = walk.active ? L('Tap the floor to walk there · tap a door or wardrobe to open it', 'फ़र्श पर टैप करें — वहाँ चलें · दरवाज़े या अलमारी पर टैप करें — खुलेगी')
                                : L('Tap any room to go inside', 'अंदर जाने के लिए किसी भी कमरे पर टैप करें');
  }

  // ------------------------------------------------ hold buttons
  function hold(h, down) {
    const v = down ? 1 : 0;
    if (h === 'fwd') walk.joy.y = down ? -0.8 : 0;
    if (h === 'back') walk.joy.y = down ? 0.6 : 0;
    if (h === 'turnL') walk.turn = down ? -1 : 0;
    if (h === 'turnR') walk.turn = down ? 1 : 0;
    if (h === 'up') walk.look = v;
    if (h === 'down') walk.look = -v;
    if (down) walk.auto = null;
  }

  // ------------------------------------------------ places
  function places() {
    const rooms = app.rooms || []; const r1 = rooms.find(r => r.name === 'Room 1');
    const items = [];
    const vpName = { 'Design view (from balcony door)': ['🛏 Room 1 — whole room', '🛏 कमरा 1 — पूरा कमरा'], 'Towards balcony (from door side)': ['🌇 Room 1 — towards the balcony', '🌇 कमरा 1 — बालकनी की ओर'],
      'Wardrobe & thick wall': ['🚪 Wardrobe & study table', '🚪 अलमारी और स्टडी टेबल'], 'Balcony (outside, looking south)': ['🌿 Balcony', '🌿 बालकनी'] };
    if (r1) r1.vps.forEach((vp, i) => { if (vpName[vp.name]) items.push({ t: L(...vpName[vp.name]), go: () => ctx.goRoomVp(r1, vp) }); });
    if (r1) items.push({ t: L('⤒ Room 1 — look at the ceiling', '⤒ कमरा 1 — छत देखें'), go: () => { ctx.goRoomVp(r1, r1.vps[0]); pendingCeiling = true; } });
    for (const r of rooms) if (r.name !== 'Room 1' && r.vps[0]) items.push({ t: '🏠 ' + roomName(r.name), go: () => ctx.goRoomVp(r, r.vps.find(v => v.name === 'Centre') || r.vps[0]) });
    items.push({ t: L('🗺 Whole house from above', '🗺 ऊपर से पूरा घर'), go: () => action('house') });
    sheet.innerHTML = `<div class="p-head"><b>📍 ${L('Where do you want to go?', 'कहाँ जाना है?')}</b><button class="s-btn" data-x>✕</button></div>` +
      `<div class="p-list">${items.map((it, i) => `<button class="p-item" data-i="${i}">${it.t}</button>`).join('')}</div>`;
    sheet.querySelector('[data-x]').onclick = () => sheet.classList.add('hidden');
    sheet.querySelectorAll('.p-item').forEach(b => b.onclick = () => { sheet.classList.add('hidden'); ex.lookAtCeiling && walk.active && ex.lookAtCeiling(false); items[+b.dataset.i].go(); });
    sheet.classList.remove('hidden');
  }
  let pendingCeiling = false;
  function action(a) {
    if (a === 'places') places();
    else if (a === 'house') {
      walk.auto = null; $('tapInfo').classList.add('hidden'); ctx.overview(); setTimeout(() => { ctx.presetView('top'); }, 50);
    } else if (a === 'level') { walk.pitch = 0; walk.eyeOffset = 0; ex.setFov(60); walk.auto = null; }
    else if (a === 'help') help.classList.remove('hidden');
  }

  // ------------------------------------------------ taps: floor = walk there / go inside; door = open (immersive handles that)
  const marker = new THREE.Mesh(new THREE.RingGeometry(0.16, 0.24, 32), new THREE.MeshBasicMaterial({ color: 0x2b8cff, transparent: true, depthTest: false }));
  marker.rotation.x = -Math.PI / 2; marker.renderOrder = 998; marker.visible = false; marker.raycast = () => { }; scene.add(marker);
  let down = null;
  el.addEventListener('pointerdown', (e) => { if (on) down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
  el.addEventListener('pointerup', (e) => {
    if (!on || !down) return;
    const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y), dur = performance.now() - down.t; down = null;
    if (moved > 12 || dur > 600) return;
    const r = el.getBoundingClientRect(); const ndc = new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    if (imm.interactiveHit(ndc, walk.active ? 6 : Infinity)) return;         // a door / window / wardrobe: it opens (handled elsewhere)
    let p = imm.floorHit(ndc), near = false;
    if (!p && walk.active) { p = nearHit(ndc); near = !!p; }                                  // tapped a bed / sofa / table: walk up to it
    if (!p) return;
    if (walk.active) {
      if (p.distanceTo(walk.cam.position) > 12) return;
      if (!near) $('tapInfo').classList.add('hidden');                        // walking on the floor / a rug: no info card
      walk.auto = { x: p.x, z: p.z }; marker.position.set(p.x, p.y + 0.03, p.z); marker.visible = true; marker.material.opacity = 1;
    } else { $('tapInfo').classList.add('hidden'); ctx.goToPoint(p); }                                                 // from the whole-house view: go inside there
  });
  walk.onAutoStop = () => { marker.visible = false; };
  const ray = new THREE.Raycaster();
  function nearHit(ndc) {
    ray.setFromCamera(ndc, walk.cam); ray.far = 8;
    const cands = app.meshes.filter(m => { for (let q = m; q; q = q.parent) if (!q.visible) return false; return true; });
    for (const h of ray.intersectObjects(cands, false)) {
      let cat = null; for (let q = h.object; q && !cat; q = q.parent) cat = q.userData?.category || null;
      if (['furniture', 'soft_furnishing', 'decor', 'plants', 'lighting', 'appliances', 'fixtures'].includes(cat) && h.point.y < walk.cam.position.y - 0.3) {
        // aim a little short of it, on your side
        const d = new THREE.Vector3(h.point.x - walk.cam.position.x, 0, h.point.z - walk.cam.position.z); const L = d.length();
        if (L < 0.6) return null;
        return new THREE.Vector3(walk.cam.position.x, h.point.y, walk.cam.position.z).addScaledVector(d.normalize(), L - 0.5).setY(walk.cam.position.y - 1.5);
      }
      return null;
    }
    return null;
  }

  // ------------------------------------------------ mode on / off
  let on = false;
  function setOn(v) {
    on = v; body.classList.toggle('simple', on); if (on) body.classList.remove('m-left', 'm-right'); ui.classList.toggle('hidden', !on);
    walk.lookK = on ? 0.7 : 1; store.set('simple', on ? 1 : 0);
    if (!on) { sheet.classList.add('hidden'); help.classList.add('hidden'); marker.visible = false; }
    build(); sync();
    if (on && !store.get('simpleHelpSeen')) help.classList.remove('hidden');
    ctx.resize && ctx.resize();
  }
  $('simpleBtn').onclick = () => setOn(!on);
  function sync() {
    const pad = $('sPad'); if (pad) pad.classList.toggle('hidden', !walk.active);
    tipText();
  }
  function where() {
    const t = (app.walkInfoRaw || '').replace(/ · .*$/, ''), m = t.match(/^In (.+)$/);
    if (m) return lang === 'hi' ? roomName(m[1]) + ' में' : 'In ' + m[1];
    return t.startsWith('On ') ? L('Walking', 'चल रहे हैं') : $('walkInfoMini').textContent || '';
  }
  let t0 = 0;
  function update(dt) {
    if (!on) return;
    if (marker.visible) marker.material.opacity = 0.55 + 0.45 * Math.sin(performance.now() / 180);
    const now = performance.now(); if (now - t0 < 250) return; t0 = now;
    const w = $('sWhere'); if (w) w.textContent = walk.active ? '📍 ' + where() : '🗺 ' + L('Whole house — tap a room', 'पूरा घर — किसी कमरे पर टैप करें');
    if (pendingCeiling && walk.active && !app.tween) { pendingCeiling = false; ex.lookAtCeiling(true); }
  }
  function onWalkChange() { sync(); if (!walk.active) marker.visible = false; }
  // phones start in easy mode (unless "All controls" was chosen before)
  const saved = store.get('simple');
  setOn(ctx.force === '1' ? true : ctx.force === '0' ? false : saved ? saved === '1' : !!ctx.TOUCH);
  return { setOn, isOn: () => on, update, onWalkChange, setLang: (l) => { lang = l; build(); sync(); }, action };
}
