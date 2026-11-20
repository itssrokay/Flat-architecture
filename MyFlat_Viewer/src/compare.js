// Compare view (19 Nov 2026): side-by-side tables for products (budget / mid / premium picks + what owners say),
// paints and wall prep, and a placement check of the design against standard clearances. Data: models/compare.json.
const $ = (id) => document.getElementById(id);
const hi = () => (document.documentElement.lang === 'hi' ? 1 : 0);
const T = (p) => (Array.isArray(p) ? p[hi()] || p[0] : p == null ? '' : p);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const L = {
  title: ['Compare', 'तुलना'], products: ['🛒 Products', '🛒 सामान'], paints: ['🎨 Paints & walls', '🎨 पेंट और दीवार'], checks: ['📐 Placement check', '📐 जगह की जाँच'],
  item: ['Item', 'चीज़'], budget: ['Budget', 'बजट'], mid: ['Mid-range', 'मिड-रेंज'], prem: ['Premium', 'प्रीमियम'], like: ['Owners like', 'मालिकों को पसंद'], bad: ['Owners complain', 'मालिकों की शिकायत'],
  tip: ['Tip', 'सुझाव'], all: ['All', 'सब'], search: ['Search…', 'खोजें…'], open: ['Open', 'खोलें'], close: ['Close', 'बंद करें'], amazon: ['Amazon', 'Amazon'],
  product: ['Product', 'प्रोडक्ट'], tier: ['Tier', 'श्रेणी'], finish: ['Finish', 'फ़िनिश'], wash: ['Washability', 'धुलाई'], price: ['Price', 'दाम'], cov: ['Coverage', 'कवरेज'], war: ['Warranty', 'वारंटी'], say: ['People say', 'लोग कहते हैं'],
  interior: ['Interior walls', 'अंदर की दीवारें'], exterior: ['Outside walls', 'बाहर की दीवारें'], prep: ['Putty, primer, damp-proofing', 'पुट्टी, प्राइमर, सीलन-रोधी'], colours: ['Colour scheme (Asian Paints codes)', 'रंग योजना (Asian Paints कोड)'],
  cost: ['Cost', 'ख़र्च'], mist: ['Painting mistakes to avoid', 'पेंट की ग़लतियाँ जिनसे बचें'], plan: ['Suggested system', 'सुझाई गई व्यवस्था'], screen: ['Screen colours are approximate: check the shade card and a test patch.', 'स्क्रीन का रंग अनुमानित है: शेड कार्ड और दीवार पर टेस्ट देखें।'],
  room: ['Room', 'कमरा'], rule: ['Guideline', 'नियम'], ours: ['This design', 'यह डिज़ाइन'], ok: ['OK', 'ठीक'], warn: ['Check', 'देखें'], checkNote: ['Measured from the V2 designs after the 19 Nov placement fixes. Sources: NKBA, NBC (via Indian guides), SMPTE/THX, ADA (reference only).', 'V2 डिज़ाइन से नापा (19 नवंबर के सुधार के बाद)। स्रोत: NKBA, NBC (भारतीय गाइड से), SMPTE/THX, ADA (सिर्फ़ संदर्भ)।'],
  inPlan: ['In this plan only', 'सिर्फ़ इस प्लान का'], ceil: ['🏠 Ceilings', '🏠 छत'], option: ['Option', 'विकल्प'], rate: ['Rate (₹/sq ft, installed)', 'दाम (₹/वर्ग फ़ुट, लगवाकर)'], forUs: ['For our flat', 'हमारे फ़्लैट के लिए'],
  height: ['Height', 'ऊँचाई'], life: ['Lasts', 'चलेगा'], score: ['My rating /10', 'मेरी रेटिंग /10'], sHall: ['Hall', 'हॉल'], sBed: ['Bedroom', 'बेडरूम'], sWet: ['Bath', 'बाथ'], why: ['Why', 'क्यों'], prosC: ['Pros', 'फ़ायदे'], consC: ['Cons', 'नुक़सान'], myPlan: ['My choice, room by room', 'मेरा चुनाव, कमरे के हिसाब से'], pick: ['Pick', 'चुनाव'], tipsC: ['Before you start', 'शुरू करने से पहले'], srcC: ['Sources', 'स्रोत'], details: ['Details', 'विवरण'],
};
let CEIL = null;
fetch('./models/ceilings.json?v=34').then((r) => r.json()).then((d) => { CEIL = d; }).catch((e) => console.warn('ceilings', e));
let DATA = null, SHOP = null, modal = null, state = { tab: 'products', room: 'all', q: '', onlyPlan: false };
Promise.all([fetch('./models/compare.json?v=32').then((r) => r.json()), fetch('./models/shop.json?v=32').then((r) => r.json())])
  .then(([c, s]) => { DATA = c; SHOP = s; addButtons(); }).catch((e) => console.warn('compare.js', e));

function addButtons() {
  const mk = (cls) => { const b = document.createElement('button'); b.className = cls; b.textContent = '📊 ' + T(L.title); b.onclick = () => openCompare(); return b; };
  const tryAdd = () => {
    const row = document.querySelector('.insideRow'); if (!row) return setTimeout(tryAdd, 400);
    if (!row.querySelector('.cmpBtn')) { const b = mk('small cmpBtn'); row.appendChild(b); }
    const tools = document.querySelector('#moreMenu .mg:last-child .mrow'); if (tools && !tools.querySelector('.cmpBtn')) tools.prepend(mk('cmpBtn'));
  };
  tryAdd();
  new MutationObserver(() => { document.querySelectorAll('.cmpBtn').forEach((b) => b.textContent = '📊 ' + T(L.title)); if (modal && !modal.classList.contains('hidden')) render(); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
}
function ensure() {
  if (modal) return;
  modal = document.createElement('div'); modal.id = 'cmpModal'; modal.className = 'hidden';
  modal.innerHTML = `<div class="cm-box"><div class="cm-h"><b class="cm-t"></b><div class="cm-tabs"></div><button class="cm-x"></button></div><div class="cm-bar"></div><div class="cm-body"></div></div>`;
  document.body.appendChild(modal);
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  modal.querySelector('.cm-x').onclick = close;
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !modal.classList.contains('hidden')) close(); });
}
function close() { modal.classList.add('hidden'); }
export function openCompare(tab, key) {
  if (!DATA) return; ensure(); if (tab) state.tab = tab; if (key) { state.q = ''; state.focus = key; } else state.focus = null;
  modal.classList.remove('hidden'); render();
}
const link = (u, t) => u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>` : esc(t);
function pickCell(list) {
  if (!list || !list.length) return '<span class="cm-na">—</span>';
  return list.map((p) => `<div class="cm-pick">${link(p.url, p.n)}<span class="cm-pr">${esc(p.price)}</span></div>`).join('');
}
const li = (a) => (a && a.length ? `<ul>${a.map((x) => `<li>${esc(T(x))}</li>`).join('')}</ul>` : '<span class="cm-na">—</span>');
function present(it) { const names = (window.app?.objects || []).map((o) => o.name); return it.match && names.some((n) => new RegExp(it.match, 'i').test(n)); }

function render() {
  const tabs = [['products', L.products], ['paints', L.paints], ['checks', L.checks], ['ceil', L.ceil]];
  modal.querySelector('.cm-t').textContent = '📊 ' + T(L.title);
  modal.querySelector('.cm-x').textContent = T(L.close);
  modal.querySelector('.cm-tabs').innerHTML = tabs.map(([k, l]) => `<button class="${k === state.tab ? 'on' : ''}" data-t="${k}">${T(l)}</button>`).join('');
  modal.querySelectorAll('.cm-tabs button').forEach((b) => b.onclick = () => { state.tab = b.dataset.t; state.focus = null; render(); });
  const bar = modal.querySelector('.cm-bar'), body = modal.querySelector('.cm-body');
  if (state.tab === 'products') {
    const rooms = Object.entries(SHOP.rooms || {});
    bar.innerHTML = `<div class="cm-chips">${[['all', L.all], ...rooms].map(([k, l]) => `<button class="${state.room === k ? 'on' : ''}" data-r="${k}">${esc(T(l))}</button>`).join('')}</div>
      <label class="cm-only"><input type="checkbox" ${state.onlyPlan ? 'checked' : ''}> ${T(L.inPlan)}</label>
      <input class="cm-q" type="search" placeholder="${T(L.search)}" value="${esc(state.q)}">`;
    bar.querySelectorAll('[data-r]').forEach((b) => b.onclick = () => { state.room = b.dataset.r; state.focus = null; render(); });
    bar.querySelector('.cm-only input').onchange = (e) => { state.onlyPlan = e.target.checked; render(); };
    const q = bar.querySelector('.cm-q'); q.oninput = () => { state.q = q.value; state.focus = null; drawProducts(body); }; 
    drawProducts(body);
  } else if (state.tab === 'paints') { bar.innerHTML = `<div class="cm-note">${esc(T(DATA.paintNotes.plan))}</div>`; drawPaints(body); }
  else if (state.tab === 'ceil') { bar.innerHTML = `<div class="cm-note"><b>${esc(T(CEIL?.summary || ''))}</b></div>`; drawCeil(body); }
  else { bar.innerHTML = `<div class="cm-note">${esc(T(L.checkNote))}</div>`; drawChecks(body); }
}
function drawProducts(body) {
  const q = state.q.trim().toLowerCase();
  let items = SHOP.items.filter((it) => (state.room === 'all' || (it.room || 'all') === state.room));
  if (state.onlyPlan) items = items.filter(present);
  if (q) items = items.filter((it) => (T(it.n) + ' ' + it.n[0] + ' ' + JSON.stringify(DATA.picks[it.k] || {})).toLowerCase().includes(q));
  if (state.focus) items = items.filter((it) => it.k === state.focus);
  const rows = items.map((it) => {
    const d = DATA.picks[it.k] || {}; const by = (t) => (d.picks || []).filter((p) => p.t === t);
    const fallback = (b) => `<div class="cm-pick">${link(it[b].url, T(L.amazon) + ' ' + it[b].band)}</div>`;
    const like = d.like && d.like.length ? d.like : it.pros; const bad = d.bad && d.bad.length ? d.bad : it.cons;
    return `<tr><td class="cm-item"><span class="cm-th" data-k="${it.k}"></span><b>${esc(T(it.n))}</b><div class="cm-sz">${esc(T(it.size))}</div><button class="small cm-open" data-k="${it.k}">${T(L.details)} ›</button></td>
      <td>${by('b').length ? pickCell(by('b')) : fallback('budget')}</td><td>${by('m').length ? pickCell(by('m')) : fallback('mid')}</td><td>${pickCell(by('p'))}</td>
      <td class="cm-like">${li(like)}</td><td class="cm-bad">${li(bad)}</td><td class="cm-tip">${esc(T(d.tip || it.tip || ''))}</td></tr>`;
  }).join('');
  body.innerHTML = `<div class="cm-note">${esc(T(DATA.note))}</div><div class="cm-scroll"><table class="cm-table"><thead><tr><th>${T(L.item)}</th><th>${T(L.budget)}</th><th>${T(L.mid)}</th><th>${T(L.prem)}</th><th>${T(L.like)}</th><th>${T(L.bad)}</th><th>${T(L.tip)}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  body.querySelectorAll('.cm-open').forEach((b) => b.onclick = () => { const it = SHOP.items.find((x) => x.k === b.dataset.k); close(); window.inside?.openProduct(it, 'why'); });
  fillThumbs(body);
}
const ICONS = { mesh: '🦟', downlight: '💡', cove: '〰️', ac: '❄️', generic: '🛒' };
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
function drawPaints(body) {
  const tbl = (rows) => `<div class="cm-scroll"><table class="cm-table cm-paint"><thead><tr><th>${T(L.product)}</th><th>${T(L.tier)}</th><th>${T(L.finish)}</th><th>${T(L.wash)}</th><th>${T(L.price)}</th><th>${T(L.cov)}</th><th>${T(L.war)}</th><th>${T(L.say)}</th></tr></thead><tbody>
    ${rows.map((r) => `<tr class="${/★/.test(r.tier) ? 'star' : ''}"><td>${link(r.url, r.n)}</td><td>${esc(r.tier)}</td><td>${esc(r.fin)}</td><td>${esc(r.wash)}</td><td class="nw">${esc(r.price)}</td><td>${esc(r.cov)}</td><td class="nw">${esc(r.war)}</td><td>${esc(T(r.say))}</td></tr>`).join('')}</tbody></table></div>`;
  const P = DATA.paints, N = DATA.paintNotes;
  body.innerHTML = `<h4>${T(L.interior)}</h4>${tbl(P.interior)}<h4>${T(L.exterior)}</h4>${tbl(P.exterior)}<h4>${T(L.prep)}</h4>${tbl(P.prep)}
    <h4>${T(L.colours)}</h4><div class="cm-sw">${DATA.colours.map((c) => `<div class="sw"><span style="background:${c.hex}"></span><b>${esc(c.n)}</b> <code>${esc(c.code)}</code><div>${esc(T(c.use))}</div></div>`).join('')}</div><div class="cm-note">${T(L.screen)}</div>
    <h4>${T(L.cost)}</h4><div class="cm-note">${esc(T(N.cost))}</div><h4>⚠ ${T(L.mist)}</h4><ol class="cm-ol">${N.mistakes.map((m) => `<li>${esc(T(m))}</li>`).join('')}</ol>`;
}
function drawChecks(body) {
  const rows = DATA.checks.map((c) => `<tr class="${c.ok === true ? 'ok' : 'warn'}"><td>${esc(T(DATA.rooms[c.room] || c.room))}</td><td><b>${esc(T(c.item))}</b>${c.note ? `<div class="cm-sz">${esc(T(c.note))}</div>` : ''}</td><td>${esc(c.rule)}</td><td>${esc(c.ours)}</td><td class="st">${c.ok === true ? '✓ ' + T(L.ok) : '⚠ ' + T(L.warn)}</td></tr>`).join('');
  body.innerHTML = `<div class="cm-scroll"><table class="cm-table cm-chk"><thead><tr><th>${T(L.room)}</th><th>${T(L.item)}</th><th>${T(L.rule)}</th><th>${T(L.ours)}</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`;
}
function drawCeil(body) {
  if (!CEIL) { body.innerHTML = '…'; return; }
  const ul = (a) => `<ul>${a.map((x) => `<li>${esc(T(x))}</li>`).join('')}</ul>`;
  const sc = (v) => `<span class="cm-sc s${v >= 8 ? 'g' : v >= 5 ? 'm' : 'l'}">${v}</span>`;
  const name = (k) => T((CEIL.opts.find((o) => o.k === k) || {}).n || k);
  const plan = CEIL.plan.map((r) => `<tr class="star"><td><b>${esc(T(r.room))}</b></td><td><b>${esc(name(r.pick))}</b></td><td class="nw">${esc(r.cost)}</td><td>${esc(T(r.why))}</td></tr>`).join('');
  const rows = CEIL.opts.map((o) => `<tr><td class="cm-item"><b>${esc(T(o.n))}</b><div class="cm-sz">${esc(o.src)}</div></td><td>${esc(o.rate)}</td><td>${esc(o.hall)}</td><td>${esc(T(o.height))}</td><td>${esc(T(o.life))}</td>
    <td class="cm-like">${ul(o.pros)}</td><td class="cm-bad">${ul(o.cons)}</td><td class="nw">${T(L.sHall)} ${sc(o.rate10.hall)}<br>${T(L.sBed)} ${sc(o.rate10.bed)}<br>${T(L.sWet)} ${sc(o.rate10.wet)}</td></tr>`).join('');
  body.innerHTML = `<h4>✅ ${T(L.myPlan)}</h4><div class="cm-scroll"><table class="cm-table"><thead><tr><th>${T(L.room)}</th><th>${T(L.pick)}</th><th>${T(L.cost)}</th><th>${T(L.why)}</th></tr></thead><tbody>${plan}</tbody></table></div>
    <h4>${T(L.ceil)}</h4><div class="cm-scroll"><table class="cm-table"><thead><tr><th>${T(L.option)}</th><th>${T(L.rate)}</th><th>${T(L.forUs)}</th><th>${T(L.height)}</th><th>${T(L.life)}</th><th>${T(L.prosC)}</th><th>${T(L.consC)}</th><th>${T(L.score)}</th></tr></thead><tbody>${rows}</tbody></table></div>
    <h4>${T(L.tipsC)}</h4><ol class="cm-ol">${CEIL.tips.map((t) => `<li>${esc(T(t))}</li>`).join('')}</ol>
    <div class="cm-note">${T(L.srcC)}: ${CEIL.sources.map(([n, u]) => `<a href="${u}" target="_blank" rel="noopener">${esc(n)}</a>`).join(' · ')}</div>`;
}
window.compare = { openCompare };
