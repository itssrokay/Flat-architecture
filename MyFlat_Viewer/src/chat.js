// 💬 Ask: a chat about the flat. The page builds a text "knowledge" pack (all design notes, budgets, schedules,
// Customise options, the Learn dictionary, room sizes, fixed facts about the flat) plus the current "state"
// (design, choices, live budget, where you are, what's selected) and sends it with your question to /api/chat
// (Vercel function api/chat.js, or scripts/serve.py locally). The OpenAI key never reaches the browser.
// If the answer asks to change a Customise choice, an "Apply" button does it in the 3D model.
export function setupChat(ctx) {
  const { app, $ } = ctx;
  const store = { get(k) { try { return localStorage.getItem('myflat.' + k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem('myflat.' + k, v); } catch (e) { } } };
  let lang = ctx.lang || 'en';
  const T = (en, hi) => (lang === 'hi' ? hi : en);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const FT = 0.3048, ft = (m) => { const f = m / FT; let w = Math.floor(f), i = Math.round((f - w) * 12); if (i === 12) { w++; i = 0; } return i ? `${w}'${i}"` : `${w}'`; };

  const FACTS = `FIXED FACTS ABOUT THE FLAT (from the Blender model; Room 1 is the room being designed)
- Single-floor flat. Rooms: Room 1, Kitchen, Bathroom 1, Bathroom 2, Passage, Hall, Room 2, Balcony, Stair, Open Square.
- Room 1 main area 12'7" (east-west) x 11'2" (north-south), plus a 5'4" x 3'4" alcove in the south-east corner where the wardrobe goes. Clear height 10'.
- Room 1 west wall is almost all opening: a 10'5" wide x 7' high sliding door to the balcony. North wall has window W1: 4' wide x 4' high, sill 3' above the floor, with a safety grill outside.
- East wall: 9'8" of solid wall (the bed wall), then the room's door (2'8" wide) which opens OUTWARDS into the passage.
- South side: a thick "raised" wall face (7'3" long) — existing structure, not a design feature; the desk/dresser goes against it.
- A 9" RCC pillar sits in the north-west corner. The ceiling is the underside of a 5" RCC roof slab, currently bare concrete.
- Floor: builder's floor (usually vitrified tile) unless the user says otherwise; if it's bare cement, new tiles cost about Rs 30-40k for Room 1.
- The bed can only go on the east wall (the only long solid wall). Walkways beside a queen bed here are about 2' each side; nothing should stand in them (that's why the DEFAULT lounge chair was removed).
- Money: prices are rounded 2026 Indian metro estimates; the user is a beginner on a budget (Option E target was Rs 1-1.3 lakh, Option D Rs 1.5-2 lakh).`;

  // ---------------------------------------------------------------- knowledge pack (cached per language)
  const kCache = {};
  async function knowledge() {
    if (kCache[lang]) return kCache[lang];
    let guide = null;
    try { guide = await fetch(`./models/${lang === 'hi' ? 'learn_guide_hi' : 'learn_guide'}.json?v=${ctx.build}`).then(r => r.json()); } catch (e) { }
    const out = [FACTS, '', 'DESIGNS FOR ROOM 1'];
    for (const [k, n] of Object.entries(app.designNotes || {})) {
      out.push(`\n## ${k}: ${n.title}\n${n.tagline}\nWhy: ${n.why}`);
      for (const [s, v] of Object.entries(n.sections || {})) out.push(`- ${s}: ${v}`);
      if (n.budget) {
        out.push(`Budget (as recommended) ${n.budget.total}:`); for (const r of n.budget.rows) out.push(`  - ${r[0]}: ${r[1]} = ${r[2]}`);
        if (n.budget.note) out.push(`  Note: ${n.budget.note}`); if (n.budget.savings) out.push(`  Savings: ${n.budget.savings}`);
      }
      for (const g of n.schedule || []) out.push(`  [${g.area}] ` + g.items.map(i => `${i[0]}: ${i[1]}`).join('; '));
      if (n.edit) {
        out.push(`Customise options for ${k} (key: optionId = label [budget rows it sets] - note):`);
        for (const g of n.edit.groups) out.push(`  ${g.key} (${g.label}; default ${g.default}): ` + g.options.map(o =>
          `${o.id} = ${o.label} [${Object.entries(o.rows).map(([rk, r]) => r ? `${r[0]} ${r[2]}` : `no ${rk}`).join(', ')}] - ${o.note}`).join(' | '));
        for (const c of n.edit.colours) out.push(`  ${c.key} (${c.label}, free): ` + c.options.map(o => `${o.id} = ${o.label}`).join(', '));
        out.push(`  Quick picks: ` + n.edit.presets.map(p => `${p.label} = ${JSON.stringify(p.choices)}`).join('; '));
      }
      const cards = guide?.designs?.[k];
      if (cards) out.push(`What each surface is made of (${k}): ` + cards.map(c => `${c.title}: ${c.see} Layers: ${c.layers.join(' > ')}. ${c.simple}${c.paint ? ' Paint: ' + c.paint : ''}`).join(' || '));
    }
    const rooms = (app.rooms || []).map(r => { const s = r.box.getSize(new app.center.constructor()); return `${r.name} ~${ft(s.x)} x ${ft(s.z)}`; });
    if (rooms.length) out.push('\nROOM FLOOR SIZES (bounding box, approx): ' + rooms.join('; '));
    if (guide) out.push('\nDICTIONARY\n' + guide.glossary.map(t => `- ${t.term}: ${t.plain}`).join('\n'));
    return (kCache[lang] = out.join('\n'));
  }
  function state() {
    const m = ctx.modelEntry(app.modelFile) || {}, d = m.design, n = d && app.designNotes?.[d];
    const s = { design: d || null, designTitle: n?.title || m.label || app.modelFile, view: ctx.walk.active ? 'inside at eye level: ' + (app.walkInfoRaw || '').replace(/ · eye.*/, '') : 'overview (outside, looking at the model)' };
    const o = app.selected;
    if (o) {
      const b = new app.bbox.constructor().setFromObject(o), sz = b.getSize(new app.center.constructor());
      s.selected = { name: (o.userData.label || o.name).replace(/^R1_[A-Z]+_/, '').replace(/_/g, ' ').toLowerCase(), category: o.userData.category, spec: o.userData.spec || '', size: `${ft(sz.x)} wide x ${ft(sz.z)} deep x ${ft(sz.y)} high` };
    }
    const cfg = n?.edit;
    if (cfg && ctx.edit) {
      const B = app.editBudget(d, n.budget);
      s.customise = { choices: ctx.edit.state(d), options: Object.fromEntries([...cfg.groups, ...cfg.colours].map(g => [g.key, g.options.map(x => x.id)])),
        budgetTotal: B.total, budgetRows: B.rows.map(r => `${r[0]}: ${r[2]}`) };
    }
    return s;
  }

  // ---------------------------------------------------------------- UI
  const box = document.createElement('div'); box.id = 'chat'; box.className = 'hidden'; $('viewport').appendChild(box);
  const btn = $('chatBtn');
  let msgs = []; try { msgs = JSON.parse(sessionStorage.getItem('myflat.chat') || '[]'); } catch (e) { }
  let busy = false, needPass = false;
  function save() { try { sessionStorage.setItem('myflat.chat', JSON.stringify(msgs.slice(-30))); } catch (e) { } }
  function suggestions() {
    const s = state(), out = [];
    if (s.selected) out.push(T(`What is the ${s.selected.name}? Any cheaper alternative?`, `यह ${s.selected.name} क्या है? कोई सस्ता विकल्प?`));
    if (s.design === 'OPTION_E') out.push(T('Sliding or hinged wardrobe for my room?', 'मेरे कमरे के लिए स्लाइडिंग या कब्ज़े वाली अलमारी?'), T('How do I get this under ₹1.3 lakh?', 'इसे ₹1.3 लाख के अंदर कैसे लाएँ?'));
    out.push(T('What does my bare concrete ceiling need?', 'मेरी सादी कंक्रीट छत पर क्या करवाना होगा?'), T('Compare Option D and E', 'विकल्प D और E की तुलना करें'), T('Which paint should I buy?', 'कौन-सा पेंट लूँ?'));
    return out.slice(0, 4);
  }
  function md(text) {        // tiny, safe markdown: escape first, then tables / bullets / bold
    const lines = esc(text).split('\n'); const html = []; let list = null, table = null;
    const flush = () => { if (list) { html.push(`<ul>${list.join('')}</ul>`); list = null; } if (table) { html.push(`<table>${table.join('')}</table>`); table = null; } };
    for (const l of lines) {
      if (/^\s*\|.*\|\s*$/.test(l)) { if (/^\s*\|[\s:|-]+\|\s*$/.test(l)) continue; (table = table || []).push('<tr>' + l.trim().slice(1, -1).split('|').map(c => `<td>${c.trim()}</td>`).join('') + '</tr>'); continue; }
      const b = l.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)/);
      if (b) { if (table) flush(); (list = list || []).push(`<li>${b[1]}</li>`); continue; }
      flush(); html.push(l.trim() ? `<p>${l}</p>` : '');
    }
    flush();
    return html.join('').replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<i>$2</i>').replace(/^#{1,4}\s*/gm, '');
  }
  function actionOf(text) {
    const m = text.match(/^\s*ACTION:\s*(\{.*\})\s*$/m); if (!m) return { text, patch: null };
    let patch = null; try { patch = JSON.parse(m[1]); } catch (e) { }
    return { text: text.replace(m[0], '').trim(), patch };
  }
  function patchLabel(patch) {
    const d = (ctx.modelEntry(app.modelFile) || {}).design, cfg = d && app.designNotes?.[d]?.edit; if (!cfg) return null;
    const parts = [];
    for (const [k, v] of Object.entries(patch)) {
      const g = [...cfg.groups, ...cfg.colours].find(x => x.key === k); const o = g?.options.find(x => x.id === v);
      if (!o) return null; parts.push(`${g.label} → ${o.label}`);
    }
    return parts.join(', ');
  }
  function render() {
    btn.textContent = T('💬 Ask', '💬 पूछें');
    box.innerHTML = `<div class="c-head"><b>${T('Ask about your flat', 'अपने फ़्लैट के बारे में पूछें')}</b><span>
        <button class="small" data-clear title="${T('New chat', 'नई बातचीत')}">↺</button><button class="small" data-x>✕</button></span></div>
      <div class="c-list" id="chatList">${msgs.length ? '' : `<div class="c-hint">${T('I know all six designs, their budgets and materials, your ✏️ Customise choices, and what you have selected. Ask anything — in English or Hindi.', 'मुझे छहों डिज़ाइन, उनके बजट और सामग्री, आपकी ✏️ बदलें पसंद, और आपने जो चुना है, सब पता है। कुछ भी पूछें — हिंदी या अंग्रेज़ी में।')}</div>`}` +
      msgs.map((m, i) => {
        if (m.role === 'user') return `<div class="c-msg u">${esc(m.content)}</div>`;
        if (m.role === 'error') return `<div class="c-msg e">${esc(m.content)}</div>`;
        const a = actionOf(m.content), lbl = a.patch && patchLabel(a.patch);
        return `<div class="c-msg a">${md(a.text)}${lbl ? `<button class="small c-apply" data-i="${i}">✓ ${T('Apply', 'लागू करें')}: ${esc(lbl)}</button>` : ''}</div>`;
      }).join('') + (busy ? `<div class="c-msg a c-typing">${T('Thinking…', 'सोच रहा हूँ…')}</div>` : '') + `</div>` +
      (needPass ? `<div class="c-pass"><input id="chatPass" type="password" placeholder="${T('Chat passcode', 'चैट पासकोड')}"><button class="small" data-pass>OK</button></div>` : '') +
      `<div class="c-sug">${busy ? '' : suggestions().map(s => `<button class="c-chip">${esc(s)}</button>`).join('')}</div>
      <form class="c-form"><textarea id="chatIn" rows="2" placeholder="${T('Type a question…', 'अपना सवाल लिखें…')}"></textarea><button class="c-send" ${busy ? 'disabled' : ''}>➤</button></form>`;
    box.querySelector('[data-x]').onclick = () => setOpen(false);
    box.querySelector('[data-clear]').onclick = () => { msgs = []; save(); render(); };
    box.querySelectorAll('.c-chip').forEach(b => b.onclick = () => ask(b.textContent));
    box.querySelectorAll('.c-apply').forEach(b => b.onclick = () => { const a = actionOf(msgs[+b.dataset.i].content); if (a.patch && ctx.edit) { ctx.edit.set(a.patch); ctx.edit.setOpen(true); b.disabled = true; b.textContent = '✓ ' + T('Applied', 'लागू हुआ'); } });
    const pb = box.querySelector('[data-pass]'); if (pb) pb.onclick = () => { store.set('chatPass', $('chatPass').value.trim()); needPass = false; const last = [...msgs].reverse().find(m => m.role === 'user'); msgs = msgs.filter(m => m.role !== 'error'); if (last) { msgs.pop(); ask(last.content); } else render(); };
    const f = box.querySelector('.c-form'), ta = $('chatIn');
    f.onsubmit = (e) => { e.preventDefault(); ask(ta.value); };
    ta.onkeydown = (e) => { e.stopPropagation(); if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(ta.value); } };
    ta.onkeyup = ta.onkeypress = (e) => e.stopPropagation();          // don't walk / toggle while typing
    const list = $('chatList'); list.scrollTop = list.scrollHeight;
  }
  async function ask(q) {
    q = (q || '').trim(); if (!q || busy) return;
    msgs = msgs.filter(m => m.role !== 'error'); msgs.push({ role: 'user', content: q }); busy = true; render();
    try {
      const r = await fetch('./api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Chat-Passcode': store.get('chatPass') || '' },
        body: JSON.stringify({ knowledge: await knowledge(), state: state(), lang, messages: msgs.filter(m => m.role !== 'error').map(m => ({ role: m.role, content: m.content })) }) });
      const j = await r.json().catch(() => ({ error: r.status === 404 ? 'no-api' : 'HTTP ' + r.status }));
      if (r.status === 401 && j.error === 'passcode') { needPass = true; msgs.push({ role: 'error', content: T('This chat needs the passcode (set as CHAT_PASSCODE on Vercel).', 'इस चैट के लिए पासकोड चाहिए (Vercel में CHAT_PASSCODE)।') }); }
      else if (!r.ok || j.error) msgs.push({ role: 'error', content: j.error === 'no-api' || r.status === 404 || r.status === 501
        ? T('The chat server is not running here. On Vercel it needs OPENAI_API_KEY; locally, start scripts/serve.py with a .env file.', 'यहाँ चैट सर्वर नहीं चल रहा। Vercel पर OPENAI_API_KEY चाहिए; लोकल में .env फ़ाइल के साथ scripts/serve.py चलाएँ।') : (j.error || 'Error ' + r.status) });
      else msgs.push({ role: 'assistant', content: j.reply || '…' });
    } catch (e) { msgs.push({ role: 'error', content: T('Could not reach the chat server: ', 'चैट सर्वर तक नहीं पहुँच सका: ') + (e.message || e) }); }
    busy = false; save(); render();
  }
  let open = false;
  function setOpen(v) { open = v; box.classList.toggle('hidden', !open); btn.classList.toggle('on', open); if (open) { render(); setTimeout(() => $('chatIn')?.focus(), 50); } }
  btn.onclick = () => setOpen(!open);
  render();
  return { setOpen, ask, setLang: (l) => { lang = l; render(); }, knowledge, state, messages: () => msgs };
}
