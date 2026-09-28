// "Learn" guide for people who have never done up a home (English / Hindi):
//   Your room      - every surface of the current design, what it is made of (layer by layer), which paint, where
//   How homes are built - pillars, beams, slab, brick walls; your Room 1 plan explained
//   Floor & paint  - what the floor is made of (tile vs marble vs cement) and exactly which paint, with prices and colours
//   Step by step   - the order the work happens in, and who does it
//   Compare        - the 5 designs side by side in simple words
//   Dictionary     - every term used in the viewer, with "See pictures" and "Read more" links
// Content: models/learn_guide.json (English) and models/learn_guide_hi.json (Hindi).
// Hover info, tap cards and the inspector also use it ("In simple words").

const esc = (t) => String(t ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const LAYER_COLORS = ['#8d8d8d', '#b9a88f', '#e9e4da', '#f5f1ea', '#d9c9ad', '#c9a27e', '#9c7a5a'];

export async function setupLearn(ctx) {
  const { app, $, select, focusObject, build } = ctx;
  let guide = null, G = [], lang = ctx.lang || 'en';
  const U = (k) => guide?.pages?.ui?.[k] ?? k;
  async function load(l) {
    lang = l;
    const f = l === 'hi' ? 'learn_guide_hi.json' : 'learn_guide.json';
    try { guide = await (await fetch(`./models/${f}?v=${build}`, { cache: 'no-store' })).json(); }
    catch (e) { guide = { glossary: [], designs: {}, pages: { ui: {}, svg: {}, basics: [], floorpaint: [], steps: [], compare: null } }; }
    G = guide.glossary.map(t => ({ ...t, re: t.match ? new RegExp(t.match, 'i') : null }));
    buildShell(); render();
  }

  // ---- small pictures
  function stack(layers) {
    const L = [...layers].reverse();
    return `<div class="stackh">` + L.map((t, i) => {
      const bottom = i === L.length - 1;
      const col = i === 0 ? '#e9d5b7' : bottom ? '#a3a3a3' : LAYER_COLORS[(i + 1) % LAYER_COLORS.length];
      return `<div class="layer${i === 0 ? ' top' : ''}${bottom ? ' base' : ''}" style="background:${col}">${esc(t)}${i === 0 ? `<span class="yousee">${esc(U('yousee'))}</span>` : ''}${bottom ? `<span class="yousee dark">${esc(U('structure'))}</span>` : ''}</div>`;
    }).join('') + `</div>`;
  }
  const S = (k) => esc(guide.pages.svg[k] || k);
  function frameSVG() {
    return `<svg viewBox="0 0 420 250" class="diagram" role="img" aria-label="RCC frame">
    <rect x="10" y="30" width="400" height="18" fill="#9a9a9a"/><text x="150" y="24" font-size="12">${S('slab')}</text>
    <rect x="30" y="48" width="360" height="22" fill="#b3b3b3"/><text x="140" y="64" font-size="11.5">${S('beam')}</text>
    <rect x="30" y="48" width="30" height="170" fill="#7d7d7d"/><rect x="360" y="48" width="30" height="170" fill="#7d7d7d"/>
    <text x="2" y="150" font-size="11.5" transform="rotate(-90 12 150)">${S('pillar')}</text>
    <defs><clipPath id="wallclip"><rect x="60" y="70" width="270" height="148"/></clipPath></defs>
    <g fill="#c0664a" stroke="#f2e3d7" stroke-width="1.5" clip-path="url(#wallclip)">${Array.from({ length: 6 }, (_, r) => Array.from({ length: 10 }, (_, c) =>
      `<rect x="${60 + c * 30 + (r % 2 ? 15 : 0)}" y="${70 + r * 24}" width="30" height="24"/>`).join('')).join('')}</g>
    <rect x="330" y="70" width="30" height="148" fill="#e9e4da" opacity=".9"/>
    <text x="200" y="210" font-size="11" fill="#fff">${S('brick')}</text><text x="190" y="100" font-size="11" fill="#fff">${S('filler')}</text>
    <text x="30" y="244" font-size="11">${S('wallcap')}</text><rect x="10" y="218" width="400" height="10" fill="#9a9a9a"/></svg>`;
  }
  function room1SVG() {
    const k = 18, ox = 90, oy = 20, X = (x) => ox + x * k, Y = (y) => oy - y * k;
    const RW = 12.583, XS = 7.25, YW = -11.167, YS = -14.5;
    const room = `${X(0)},${Y(0)} ${X(RW)},${Y(0)} ${X(RW)},${Y(YS)} ${X(XS)},${Y(YS)} ${X(XS)},${Y(YW)} ${X(0)},${Y(YW)}`;
    return `<svg viewBox="0 0 420 320" class="diagram plan" role="img" aria-label="Room 1 plan">
    <rect x="${X(-4.35)}" y="${Y(0.7)}" width="${3.1 * k}" height="${14.6 * k}" fill="#dfe9d8" stroke="#8aa37a"/>
    <text x="${X(-4.1)}" y="${Y(-6)}" font-size="11" transform="rotate(-90 ${X(-3.4)} ${Y(-6)})">${S('balcony')}</text>
    <polygon points="${room}" fill="#f6f1e7" stroke="#333" stroke-width="3"/>
    <rect x="${X(0)}" y="${Y(YW)}" width="${XS * k}" height="${3.333 * k}" fill="#c9b8a2" stroke="#333"/>
    <text x="${X(0.4)}" y="${Y(YW - 1.4)}" font-size="11" font-weight="700">${S('thick')}</text><text x="${X(0.4)}" y="${Y(YW - 2.5)}" font-size="10.5">${S('thick2')}</text>
    <rect x="${X(XS)}" y="${Y(YS + 2)}" width="${(RW - XS) * k}" height="${2 * k}" fill="#e7dcf4" stroke="#6d3fa8"/>
    <text x="${X(XS + 0.3)}" y="${Y(YS + 1.25)}" font-size="10.5">${S('alcove')}</text><text x="${X(XS + 0.3)}" y="${Y(YS + 0.45)}" font-size="10">${S('alcove2')}</text>
    <rect x="${X(0)}" y="${Y(0)}" width="${0.75 * k}" height="${0.75 * k}" fill="#7d7d7d"/><text x="${X(0.3)}" y="${Y(-1.7)}" font-size="10.5">${S('pillar9')}</text>
    <rect x="${X(3.4)}" y="${Y(0) - 5}" width="${4 * k}" height="10" fill="#8ec5e8" stroke="#333"/><text x="${X(3.6)}" y="${Y(0) - 8}" font-size="10.5">${S('window')}</text>
    <rect x="${X(0) - 5}" y="${Y(-0.75)}" width="10" height="${10.417 * k}" fill="#8ec5e8" stroke="#333"/>
    <text x="${X(0.35)}" y="${Y(-3.4)}" font-size="10.5">${S('opening')}</text>
    <rect x="${X(RW) - 5}" y="${Y(-9.667)}" width="10" height="${2.667 * k}" fill="#d9a066" stroke="#333"/><text x="${X(RW) - 80}" y="${Y(-10.4)}" font-size="10.5">${S('door')}</text>
    <text x="${X(4.2)}" y="${Y(-5)}" font-size="12" font-weight="700">${S('room')}</text>
    <text x="${X(3.3)}" y="${Y(-6.2)}" font-size="10.5">${S('size')}</text>
    <text x="${X(RW) + 6}" y="${Y(-0.5)}" font-size="11">${S('north')}</text></svg>`;
  }
  const linkBtns = (imgUrl, wikiUrl) => (imgUrl ? `<a class="small lbtn" href="${esc(imgUrl)}" target="_blank" rel="noopener">${esc(U('pics'))}</a>` : '') +
    (wikiUrl ? `<a class="small lbtn" href="${esc(wikiUrl)}" target="_blank" rel="noopener">${esc(U('wiki'))}</a>` : '');

  // ---- drawer
  const box = document.createElement('div'); box.id = 'learn'; box.className = 'hidden';
  $('viewport').appendChild(box);
  let tab = 'room', open = false, q = '';
  function buildShell() {
    box.innerHTML = `<div class="lhead"><b>📘 ${esc(U('title'))}</b><span class="lsub">${esc(U('sub'))}</span><button class="small" id="learnClose" title="G">✕</button></div>
      <div class="ltabs">${(U('tabs') || []).map(([k, t]) => `<button data-t="${k}">${esc(t)}</button>`).join('')}</div>
      <div class="lbody" id="learnBody"></div>`;
    box.querySelectorAll('.ltabs button').forEach(b => b.onclick = () => { tab = b.dataset.t; render(); });
    $('learnClose').onclick = () => setOpen(false);
  }
  function setOpen(on) {
    open = on; box.classList.toggle('hidden', !on); $('learnBtn').classList.toggle('on', on);
    document.querySelector('#immBar [data-act=learn]')?.classList.toggle('on', on);
    if (on) render();
  }
  $('learnBtn').onclick = () => setOpen(!open);
  $('immBar').addEventListener('click', (e) => { if (e.target.closest('button')?.dataset.act === 'learn') setOpen(!open); });
  document.addEventListener('keydown', (e) => { if (e.code === 'KeyG' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName)) setOpen(!open); });

  // ---- "show me"
  function findObjs(patterns) {
    const out = [];
    for (const p of patterns || []) {
      const re = new RegExp(p);
      for (const o of app.objects) { const n = o.name.replace(/^R1_(DEF|OPA|OPB|OPC|OPD|OPE)_/, ''); if (re.test(n) || re.test(o.name)) out.push(o.obj); }
      if (out.length) break;
    }
    return out;
  }
  function showMe(patterns) {
    const objs = findObjs(patterns); if (!objs.length) return false;
    select(objs[0]); focusObject(objs[0]);
    if (window.innerWidth <= 900) setOpen(false);          // on a phone, get the guide out of the way to see it
    return true;
  }
  const designKey = () => (ctx.modelEntry(app.modelFile) || {}).design || null;
  const designTitle = () => { const k = designKey(); return (k && app.designNotes?.[k]?.title) || (ctx.modelEntry(app.modelFile) || {}).label || app.modelFile; };

  // ---- tabs
  function renderRoom() {
    const k = designKey(), cards = guide.designs[k];
    if (!cards) return `<p>${esc(U('bare'))}</p>`;
    let h = `<p class="lead">${U('lead').replace('{d}', esc(designTitle()))}</p>`;
    cards.forEach((c, i) => {
      h += `<div class="lcard"><h4>${esc(c.title)}</h4><p><b>${esc(U('see'))}</b> ${esc(c.see)}</p>${stack(c.layers)}`;
      if (c.simple) h += `<p><b>${esc(U('simple'))}</b> ${esc(c.simple)}</p>`;
      if (c.paint) h += `<p class="paint"><b>${esc(U('paint'))}</b> ${esc(c.paint)}</p>`;
      if (c.where) h += `<p class="where"><b>${esc(U('where'))}</b> ${esc(c.where)}</p>`;
      h += `<div class="lrow">${c.show?.length ? `<button class="small showme" data-i="${i}">${esc(U('showme'))}</button>` : ''}${linkBtns(c.img)}</div></div>`;
    });
    return h;
  }
  function renderBasics() {
    return guide.pages.basics.map(b => `<div class="lcard"><h4>${esc(b.h)}</h4>` +
      (b.svg === 'frame' ? frameSVG() : b.svg === 'room1' ? room1SVG() : '') +
      (b.p || []).map(p => `<p>${p}</p>`).join('') +
      (b.ul ? `<ul>${b.ul.map(x => `<li>${x}</li>`).join('')}</ul>` : '') +
      (b.stacks || []).map(([t, L]) => `<p><b>${esc(t)}</b>:</p>${stack(L)}`).join('') +
      (b.notes || []).map(n => `<p class="where">${n}</p>`).join('') +
      (b.buttons ? `<div class="lrow">${b.buttons.map(([p, t]) => `<button class="small showme2" data-p="${esc(p)}">${esc(t)}</button>`).join('')}</div>` : '') + `</div>`).join('');
  }
  function renderFloorPaint() {
    return guide.pages.floorpaint.map(b => `<div class="lcard"><h4>${esc(b.h)}</h4>` + b.p.map(p => `<p>${p}</p>`).join('') +
      `<div class="ctable"><table class="ftable">${b.table.map((r, i) => `<tr>${r.map(c => i === 0 ? `<th>${esc(c)}</th>` : `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>` +
      (b.swatches ? `<div class="swatches">${b.swatches.map(([c, n]) => `<span class="sw" style="--c:${c}"><i></i>${esc(n)}</span>`).join('')}</div>` : '') +
      (b.notes || []).map(n => `<p class="where">${n}</p>`).join('') +
      `<div class="lrow">${b.links.map(([u, t]) => `<a class="small lbtn" href="${esc(u)}" target="_blank" rel="noopener">🖼 ${esc(t)}</a>`).join('')}</div></div>`).join('');
  }
  function renderSteps() {
    return `<p class="lead">${esc(U('stepslead'))}</p><ol class="steps">` +
      guide.pages.steps.map(([a, who, t]) => `<li><b>${esc(a)}</b> <span class="who">${esc(who)}</span><div>${esc(t)}</div></li>`).join('') +
      `</ol><p class="where">${esc(U('stepsnote'))}</p>`;
  }
  function renderCompare() {
    const c = guide.pages.compare; if (!c) return '';
    const name = { DEFAULT: 'DEFAULT', OPTION_A: 'A', OPTION_B: 'B', OPTION_C: 'C', OPTION_D: 'D', OPTION_E: 'E' }, cur = designKey();
    return `<p class="lead">${esc(U('comparelead'))}</p><div class="ctable"><table><tr><th></th>${c.cols.map(k => `<th class="${k === cur ? 'cur' : ''}">${name[k] || k}</th>`).join('')}</tr>` +
      c.rows.map((r, i) => `<tr><td class="rh">${esc(r)}</td>${c.cols.map(k => `<td class="${k === cur ? 'cur' : ''}">${esc(c.cells[k][i])}</td>`).join('')}</tr>`).join('') + `</table></div>`;
  }
  function renderDict() {
    const groups = {};
    for (const t of G) {
      const hay = (t.term + ' ' + t.aka.join(' ') + ' ' + t.plain).toLowerCase();
      if (q && !hay.includes(q.toLowerCase())) continue;
      (groups[t.groupLabel] = groups[t.groupLabel] || []).push(t);
    }
    let h = `<input id="dictSearch" placeholder="${esc(U('search'))}" value="${esc(q)}">`;
    for (const [g, list] of Object.entries(groups)) {
      h += `<div class="dgroup">${esc(g)}</div>`;
      for (const t of list) {
        const inScene = t.re && app.objects.some(o => t.re.test(o.name) || t.re.test(o.obj.userData?.spec || ''));
        h += `<div class="dterm"><b>${esc(t.term)}</b>${t.aka.length ? ` <span class="aka">(${esc(t.aka.join(', '))})</span>` : ''}<div>${esc(t.plain)}</div>` +
          `<div class="lrow">${inScene ? `<button class="small showterm" data-term="${esc(t.term)}">${esc(U('showme'))}</button>` : ''}${linkBtns(t.img, t.wiki)}</div></div>`;
      }
    }
    return Object.keys(groups).length ? h : h + `<p>${esc(U('nomatch'))}</p>`;
  }
  function render() {
    if (!open || !guide) return;
    box.querySelectorAll('.ltabs button').forEach(b => b.classList.toggle('on', b.dataset.t === tab));
    const body = $('learnBody');
    body.innerHTML = ({ room: renderRoom, basics: renderBasics, floorpaint: renderFloorPaint, steps: renderSteps, compare: renderCompare, dict: renderDict }[tab] || renderRoom)();
    body.querySelectorAll('.showme').forEach(b => b.onclick = () => { const c = guide.designs[designKey()][+b.dataset.i]; if (!showMe(c.show)) b.textContent = U('notin'); });
    body.querySelectorAll('.showme2').forEach(b => b.onclick = () => { if (!showMe(b.dataset.p.split('|'))) b.textContent = U('notin'); });
    body.querySelectorAll('.showterm').forEach(b => b.onclick = () => {
      const t = G.find(x => x.term === b.dataset.term); const o = app.objects.find(o => t.re.test(o.name) || t.re.test(o.obj.userData?.spec || ''));
      if (o) { select(o.obj); focusObject(o.obj); if (window.innerWidth <= 900) setOpen(false); }
    });
    const s = $('dictSearch'); if (s) { s.oninput = () => { q = s.value; const pos = s.selectionStart; render(); const n = $('dictSearch'); n.focus(); n.setSelectionRange(pos, pos); }; }
  }

  // ---- plain-language explanation of any object (hover info, tap card, inspector)
  function explain(o) {
    if (!o) return [];
    const u = o.userData || {}, text = `${o.name} ${u.spec || ''}`;
    const hits = [];
    for (const t of G) { if (t.re && t.re.test(text)) { hits.push(t); if (hits.length === 2) break; } }
    return hits.map(t => ({ term: t.term, plain: t.plain, img: t.img }));
  }
  function explainHTML(o) {
    const h = explain(o); if (!h.length) return '';
    return h.map(t => `<b>${esc(t.term)}:</b> ${esc(t.plain)}${t.img ? ` <a href="${esc(t.img)}" target="_blank" rel="noopener">${esc(U('pics'))}</a>` : ''}`).join('<br>');
  }
  await load(lang);
  return { onModel: () => render(), setOpen, explain, explainHTML, showMe, isOpen: () => open, setTab: (t) => { tab = t; render(); },
           setLang: (l) => load(l), U };
}
