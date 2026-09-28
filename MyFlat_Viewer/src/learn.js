// "Learn" guide for people who have never done up a home:
//   Your room  - every surface of the current design, what it is made of (layer by layer), in plain words
//   Basics     - how the flat is built (pillars, beams, slab, brick walls), your Room 1 plan explained
//   Step by step - the order the work happens in, and who does it
//   Compare    - the 5 designs side by side in simple words
//   Dictionary - every term used in the viewer (putty, HDHMR, domal, 2700K ...)
// Content lives in models/learn_guide.json. Hover info and the inspector also use it ("In simple words").

const esc = (t) => String(t ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// ------------------------------------------------------------------ small SVG diagrams
const LAYER_COLORS = ['#8d8d8d', '#b9a88f', '#e9e4da', '#f5f1ea', '#d9c9ad', '#c9a27e', '#9c7a5a'];
function stackSVG(layers) {
  // drawn like a cut through the surface: what you see on top, the structure at the bottom
  const L = [...layers].reverse();
  return `<div class="stackh">` + L.map((t, i) => {
    const bottom = i === L.length - 1;
    const col = i === 0 ? '#e9d5b7' : bottom ? '#a3a3a3' : LAYER_COLORS[(i + 1) % LAYER_COLORS.length];
    return `<div class="layer${i === 0 ? ' top' : ''}${bottom ? ' base' : ''}" style="background:${col}">${esc(t)}${i === 0 ? '<span class="yousee">you see this</span>' : ''}${bottom ? '<span class="yousee dark">structure</span>' : ''}</div>`;
  }).join('') + `</div>`;
}
const FRAME_SVG = `<svg viewBox="0 0 420 250" class="diagram" role="img" aria-label="RCC frame">
  <rect x="10" y="30" width="400" height="18" fill="#9a9a9a"/><text x="160" y="24" font-size="12">SLAB (RCC) = your ceiling</text>
  <rect x="30" y="48" width="360" height="22" fill="#b3b3b3"/><text x="150" y="64" font-size="11.5">BEAM (RCC) under the slab</text>
  <rect x="30" y="48" width="30" height="170" fill="#7d7d7d"/><rect x="360" y="48" width="30" height="170" fill="#7d7d7d"/>
  <text x="2" y="150" font-size="11.5" transform="rotate(-90 12 150)">PILLAR</text>
  <defs><clipPath id="wallclip"><rect x="60" y="70" width="270" height="148"/></clipPath></defs><g fill="#c0664a" stroke="#f2e3d7" stroke-width="1.5" clip-path="url(#wallclip)">${Array.from({ length: 6 }, (_, r) => Array.from({ length: 10 }, (_, c) =>
    `<rect x="${60 + c * 30 + (r % 2 ? 15 : 0)}" y="${70 + r * 24}" width="30" height="24"/>`).join('')).join('')}</g>
  <rect x="60" y="70" width="300" height="148" fill="none" stroke="#333" stroke-dasharray="4 3"/>
  <rect x="330" y="70" width="30" height="148" fill="#e9e4da" opacity=".9"/><text x="250" y="210" font-size="11" fill="#fff">brick / block wall</text>
  <text x="228" y="100" font-size="11" fill="#fff">(filler between pillars)</text>
  <text x="30" y="244" font-size="11">the wall: bricks, then plaster + putty + paint on the room side</text>
  <rect x="10" y="218" width="400" height="10" fill="#9a9a9a"/></svg>`;
function room1SVG() {
  // Room 1 plan, 18 px per foot. North up, balcony on the left (west).
  const k = 18, ox = 90, oy = 20, X = (x) => ox + x * k, Y = (y) => oy - y * k;
  const RW = 12.583, XS = 7.25, YW = -11.167, YS = -14.5;
  const room = `${X(0)},${Y(0)} ${X(RW)},${Y(0)} ${X(RW)},${Y(YS)} ${X(XS)},${Y(YS)} ${X(XS)},${Y(YW)} ${X(0)},${Y(YW)}`;
  return `<svg viewBox="0 0 420 320" class="diagram plan" role="img" aria-label="Room 1 plan">
  <rect x="${X(-4.35)}" y="${Y(0.7)}" width="${3.1 * k}" height="${14.6 * k}" fill="#dfe9d8" stroke="#8aa37a"/>
  <text x="${X(-4.1)}" y="${Y(-6)}" font-size="11" transform="rotate(-90 ${X(-3.4)} ${Y(-6)})">BALCONY (outside)</text>
  <polygon points="${room}" fill="#f6f1e7" stroke="#333" stroke-width="3"/>
  <rect x="${X(0)}" y="${Y(YW)}" width="${XS * k}" height="${3.333 * k}" fill="#c9b8a2" stroke="#333"/>
  <text x="${X(0.4)}" y="${Y(YW - 1.4)}" font-size="11" font-weight="700">THICK ("raised") WALL</text><text x="${X(0.4)}" y="${Y(YW - 2.5)}" font-size="10.5">solid · 7'3" × 3'4"</text>
  <rect x="${X(XS)}" y="${Y(YS + 2)}" width="${(RW - XS) * k}" height="${2 * k}" fill="#e7dcf4" stroke="#6d3fa8"/>
  <text x="${X(XS + 0.3)}" y="${Y(YS + 1.25)}" font-size="10.5">ALCOVE</text><text x="${X(XS + 0.3)}" y="${Y(YS + 0.45)}" font-size="10">(wardrobe here)</text>
  <rect x="${X(0)}" y="${Y(0)}" width="${0.75 * k}" height="${0.75 * k}" fill="#7d7d7d"/><text x="${X(0.3)}" y="${Y(-1.7)}" font-size="10.5">↖ 9" pillar</text>
  <rect x="${X(3.4)}" y="${Y(0) - 5}" width="${4 * k}" height="10" fill="#8ec5e8" stroke="#333"/><text x="${X(3.6)}" y="${Y(0) - 8}" font-size="10.5">WINDOW W1 (4')</text>
  <rect x="${X(0) - 5}" y="${Y(-0.75)}" width="10" height="${10.417 * k}" fill="#8ec5e8" stroke="#333"/>
  <text x="${X(0.35)}" y="${Y(-3.4)}" font-size="10.5">← balcony opening 10'5"</text>
  <rect x="${X(RW) - 5}" y="${Y(-9.667)}" width="10" height="${2.667 * k}" fill="#d9a066" stroke="#333"/><text x="${X(RW) - 70}" y="${Y(-10.4)}" font-size="10.5">door →</text>
  <text x="${X(4.2)}" y="${Y(-5)}" font-size="12" font-weight="700">ROOM 1</text>
  <text x="${X(3.6)}" y="${Y(-6.2)}" font-size="10.5">12'7" wide × 14'6" deep</text>
  <text x="${X(RW) + 6}" y="${Y(-0.5)}" font-size="11">N ↑</text></svg>`;
}
const STEPS = [
  ['Measure & decide', 'You + designer / Claude', 'Fix the layout, the finishes and the budget first. Changes later cost double.'],
  ['Civil work (only if needed)', 'Mason', 'Breaking / building walls, making openings. Never touch pillars, beams or the slab without an engineer.'],
  ['Window & door frames', 'Aluminium / uPVC fabricator', 'Frames go in before the final putty so the edges can be finished neatly.'],
  ['Electrical & AC piping', 'Electrician', 'Wires in pipes (conduits) cut into the brick walls: switch boards, light points, AC point. Done before putty and flooring.'],
  ['False ceiling frame (if any)', 'Gypsum / POP contractor', 'Steel channels + gypsum boards, with holes for downlights and a groove for the cove LED.'],
  ['Flooring (if new)', 'Tile mason', 'Tiles laid on a cement bed; left to set 2–3 days; skirting fixed. Cover it with sheets afterwards.'],
  ['Putty & primer', 'Painter', 'Walls and ceiling: 2 coats of putty, sanding, primer. Dusty work, so before carpentry is finished.'],
  ['Carpentry', 'Carpenter', 'Wardrobe, loft, study wall, pelmet. Usually 1–2 weeks for one room.'],
  ['Final paint coats', 'Painter', '2 coats of colour after the carpentry dust is gone. Touch-ups at the very end.'],
  ['Fittings', 'Electrician', 'Lights, switches, fan, LED strips and drivers.'],
  ['Glass, curtains, furniture', 'You / vendors', 'Window glass & mesh shutters, curtain rods, bed, mattress, rugs, plants.'],
  ['Deep clean', 'Cleaning service', 'Acid-free cleaning of tiles, remove paint spots, then move in.'],
];

export async function setupLearn(ctx) {
  const { app, $, select, focusObject, scene, build } = ctx;
  let guide = null;
  try { guide = await (await fetch('./models/learn_guide.json?v=' + build, { cache: 'no-store' })).json(); } catch (e) { guide = { glossary: [], designs: {}, compare: null }; }
  const G = guide.glossary.map(t => ({ ...t, re: t.match ? new RegExp(t.match, 'i') : null }));

  // ---- drawer
  const box = document.createElement('div'); box.id = 'learn'; box.className = 'hidden';
  box.innerHTML = `<div class="lhead"><b>📘 Learn</b><span class="lsub">home-making, explained simply</span><button class="small" id="learnClose" title="Close (G)">✕</button></div>
    <div class="ltabs"><button data-t="room" class="on">Your room</button><button data-t="basics">How homes are built</button><button data-t="steps">Step by step</button><button data-t="compare">Compare designs</button><button data-t="dict">Dictionary</button></div>
    <div class="lbody" id="learnBody"></div>`;
  $('viewport').appendChild(box);
  let tab = 'room', open = false;
  box.querySelectorAll('.ltabs button').forEach(b => b.onclick = () => { tab = b.dataset.t; render(); });
  $('learnClose').onclick = () => setOpen(false);
  function setOpen(on) {
    open = on; box.classList.toggle('hidden', !on); $('learnBtn').classList.toggle('on', on);
    document.querySelector('#immBar [data-act=learn]')?.classList.toggle('on', on);
    if (on) render();
  }
  $('learnBtn').onclick = () => setOpen(!open);
  $('immBar').addEventListener('click', (e) => { if (e.target.closest('button')?.dataset.act === 'learn') setOpen(!open); });
  document.addEventListener('keydown', (e) => { if (e.code === 'KeyG' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName)) setOpen(!open); });

  // ---- "show me": find the object(s) in the current model and fly to them
  function findObjs(patterns) {
    const out = [];
    for (const p of patterns || []) {
      const re = new RegExp(p);
      for (const o of app.objects) { const n = o.name.replace(/^R1_(DEF|OPA|OPB|OPC|OPD)_/, ''); if (re.test(n) || re.test(o.name)) out.push(o.obj); }
      if (out.length) break;
    }
    return out;
  }
  function showMe(patterns) {
    const objs = findObjs(patterns); if (!objs.length) return false;
    // everything a beginner needs to see it: roof off when the part is on the ceiling, otherwise keep things as they are
    select(objs[0]); focusObject(objs[0]); return true;
  }
  const designKey = () => { const m = (ctx.modelEntry(app.modelFile) || {}); return m.design || null; };
  const designTitle = () => { const k = designKey(); return (k && app.designNotes?.[k]?.title) || (ctx.modelEntry(app.modelFile) || {}).label || app.modelFile; };

  // ---- tabs
  function renderRoom() {
    const k = designKey(), cards = guide.designs[k];
    if (!cards) return `<p>This model is the bare architecture (no interior design), so there are no finishes to explain. Pick <b>DEFAULT, A, B, C or D</b> under <i>Interior design</i>, or open <b>How homes are built</b>.</p>`;
    let h = `<p class="lead">You're looking at <b>${esc(designTitle())}</b>. Each card says what you'll see, what it's made of (the layers from the structure up to what you touch), and where it goes. Click <b>Show me</b> to fly to it.</p>`;
    cards.forEach((c, i) => {
      h += `<div class="lcard"><h4>${esc(c.title)}</h4><p><b>What you see:</b> ${esc(c.see)}</p>${stackSVG(c.layers)}`;
      if (c.simple) h += `<p><b>In simple words:</b> ${esc(c.simple)}</p>`;
      if (c.where) h += `<p class="where"><b>Where exactly:</b> ${esc(c.where)}</p>`;
      if (c.show?.length) h += `<button class="small showme" data-i="${i}">👁 Show me</button>`;
      h += `</div>`;
    });
    return h;
  }
  function renderBasics() {
    return `<div class="lcard"><h4>1 · The skeleton: pillars, beams, slab</h4>${FRAME_SVG}
      <p>Your building stands on an <b>RCC frame</b> (concrete with steel bars): <b>pillars</b> (columns) go up, <b>beams</b> run between them under the ceiling, and a flat <b>slab</b> sits on top, which is your ceiling and the next flat's floor.</p>
      <p>The walls between the pillars are <b>brick or block</b> "filler" walls. They don't hold the building up, which is why you can cut small grooves in them for wires, but <b>never</b> in pillars, beams or the slab.</p>
      <button class="small showme2" data-p="PILLAR_R1_NW|PILLAR_1">👁 Show me a pillar</button> <button class="small showme2" data-p="BEAM_">👁 a beam</button></div>
    <div class="lcard"><h4>2 · Your Room 1, explained</h4>${room1SVG()}
      <ul><li><b>Thick ("raised") wall</b>: on the south side, one 7'3" part of the wall is 3'4" deep. It's solid, like a big block, not a cupboard. The designs put the study desk / dresser on its face. Ask the builder what's inside before drilling deep (often a pillar or a pipe/wire shaft).</li>
      <li><b>Alcove</b>: the 5'4" × 3'4" pocket next to it, perfect for a wardrobe, so the wardrobe takes no floor space from the room.</li>
      <li><b>Balcony opening</b>: the whole west side (10'5") opens to the balcony; there's no gate or frame yet, which is why every design adds a glass door.</li>
      <li><b>9" pillar</b> at the north-west corner where the opening ends.</li></ul>
      <button class="small showme2" data-p="WALL_R1_S_RAISED">👁 Show me the thick wall</button> <button class="small showme2" data-p="WARDROBE_CARCASS|WALL_R1_S_RAISED">👁 the alcove</button></div>
    <div class="lcard"><h4>3 · What's on a wall, a floor and a ceiling</h4>
      <p><b>Wall</b> (inside faces):</p>${stackSVG(['Brick / block', 'Cement plaster 12–15 mm', 'Wall putty, 2 thin coats', 'Primer', 'Paint, 2 coats'])}
      <p><b>Floor</b>:</p>${stackSVG(['RCC slab', 'Cement-sand bed ~40–50 mm', 'Tile (vitrified) or stone, grout in the joints'])}
      <p><b>Ceiling</b> (plain):</p>${stackSVG(['RCC slab', 'Thin plaster / POP punning', 'Putty', 'Primer', 'Ceiling-white paint'])}
      <p><b>Ceiling with a false ceiling</b>:</p>${stackSVG(['RCC slab', 'Steel channels hanging from it', 'Gypsum board 12.5 mm', 'Joint tape + putty', 'Primer + paint'])}
      <p class="where"><b>Which side gets putty and paint?</b> Only the <b>inside faces</b> of the room's walls and the <b>ceiling</b>. Outside faces of outer walls get exterior paint from the building (putty isn't waterproof, so it's never used outside). The balcony's walls get exterior-grade paint, no putty.</p>
      <p class="where"><b>Marble or tile?</b> None of the designs use marble. They use <b>vitrified tiles</b> (or keep your existing floor in Option D). Tiles are cheaper, don't stain, and don't need polishing; many are printed to look like marble, wood or terrazzo.</p></div>`;
  }
  function renderSteps() {
    return `<p class="lead">The usual order for doing up one room. Each step has to finish before the next, or work gets damaged and redone.</p><ol class="steps">` +
      STEPS.map(([a, who, t]) => `<li><b>${esc(a)}</b> <span class="who">${esc(who)}</span><div>${esc(t)}</div></li>`).join('') + `</ol>
      <p class="where">For Option D (budget), steps 2, 5 and 6 are skipped: no civil work, no false ceiling, no new floor.</p>`;
  }
  function renderCompare() {
    const c = guide.compare; if (!c) return '';
    const name = { DEFAULT: 'DEFAULT', OPTION_A: 'A', OPTION_B: 'B', OPTION_C: 'C', OPTION_D: 'D' };
    const cur = designKey();
    return `<p class="lead">The same room, five ways, in plain words.</p><div class="ctable"><table><tr><th></th>${c.cols.map(k => `<th class="${k === cur ? 'cur' : ''}">${name[k] || k}</th>`).join('')}</tr>` +
      c.rows.map((r, i) => `<tr><td class="rh">${esc(r)}</td>${c.cols.map(k => `<td class="${k === cur ? 'cur' : ''}">${esc(c.cells[k][i])}</td>`).join('')}</tr>`).join('') + `</table></div>`;
  }
  let q = '';
  function renderDict() {
    const groups = {};
    for (const t of G) {
      const hay = (t.term + ' ' + t.aka.join(' ') + ' ' + t.plain).toLowerCase();
      if (q && !hay.includes(q.toLowerCase())) continue;
      (groups[t.group] = groups[t.group] || []).push(t);
    }
    let h = `<input id="dictSearch" placeholder="Search: putty, HDHMR, domal, 2700K…" value="${esc(q)}">`;
    for (const [g, list] of Object.entries(groups)) {
      h += `<div class="dgroup">${esc(g)}</div>`;
      for (const t of list) {
        const inScene = t.re && app.objects.some(o => t.re.test(o.name) || t.re.test(o.obj.userData?.spec || ''));
        h += `<div class="dterm"><b>${esc(t.term)}</b>${t.aka.length ? ` <span class="aka">(${esc(t.aka.join(', '))})</span>` : ''}<div>${esc(t.plain)}</div>` +
          (inScene ? `<button class="small showterm" data-term="${esc(t.term)}">👁 Show me</button>` : '') + `</div>`;
      }
    }
    return h || '<p>No match.</p>';
  }
  function render() {
    if (!open) return;
    box.querySelectorAll('.ltabs button').forEach(b => b.classList.toggle('on', b.dataset.t === tab));
    const body = $('learnBody');
    body.innerHTML = { room: renderRoom, basics: renderBasics, steps: renderSteps, compare: renderCompare, dict: renderDict }[tab]();
    body.querySelectorAll('.showme').forEach(b => b.onclick = () => { const c = guide.designs[designKey()][+b.dataset.i]; if (!showMe(c.show)) b.textContent = 'Not in this model'; });
    body.querySelectorAll('.showme2').forEach(b => b.onclick = () => { if (!showMe(b.dataset.p.split('|'))) b.textContent = 'Not in this model'; });
    body.querySelectorAll('.showterm').forEach(b => b.onclick = () => {
      const t = G.find(x => x.term === b.dataset.term); const o = app.objects.find(o => t.re.test(o.name) || t.re.test(o.obj.userData?.spec || ''));
      if (o) { select(o.obj); focusObject(o.obj); }
    });
    const s = $('dictSearch'); if (s) { s.oninput = () => { q = s.value; const pos = s.selectionStart; render(); const n = $('dictSearch'); n.focus(); n.setSelectionRange(pos, pos); }; }
  }

  // ---- plain-language explanation of any object (hover info + inspector)
  function explain(o) {
    if (!o) return [];
    const u = o.userData || {}, text = `${o.name} ${u.spec || ''}`;
    const hits = [];
    for (const t of G) { if (t.re && t.re.test(text)) { hits.push(t); if (hits.length === 2) break; } }
    return hits.map(t => ({ term: t.term, plain: t.plain }));
  }
  function explainHTML(o) {
    const h = explain(o); if (!h.length) return '';
    return h.map(t => `<b>${esc(t.term)}:</b> ${esc(t.plain)}`).join('<br>');
  }
  return { onModel: () => render(), setOpen, explain, explainHTML, showMe, isOpen: () => open, setTab: (t) => { tab = t; render(); } };
}
