// "Customise" panel for designs whose notes carry an `edit` block (Option E):
//  - variant choices (wardrobe doors, loft, mirror, desk, window, balcony) show / hide model parts tagged
//    in Blender with a custom property  variant = "key=value" (several joined with '&')
//  - budget-only choices (ceiling finish, wall condition) change budget rows
//  - colour choices recolour one material each (walls, bed wall, curtains, wood, wardrobe laminate)
// The budget table in the design notes is recomputed from the choices. Choices are saved on this
// device (localStorage) and can be shared as a link (?e=wardrobe:hinged,desk:fold,...).
export function setupEdit(ctx) {
  const { app, $ } = ctx;
  const store = { get(k) { try { return localStorage.getItem('myflat.' + k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem('myflat.' + k, v); } catch (e) { } } };
  const panel = $('editPanel'), btn = $('editBtn');
  const state = {};                     // design -> { key: optionId }
  let open = store.get('editOpen') !== '0';
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const num = (s) => +String(s).replace(/[^0-9]/g, '') || 0;
  const inr = (n) => { const s = String(Math.round(n)); if (s.length <= 3) return '₹' + s; const last = s.slice(-3); let rest = s.slice(0, -3); const parts = [];
    while (rest.length > 2) { parts.unshift(rest.slice(-2)); rest = rest.slice(0, -2); } if (rest) parts.unshift(rest); return '₹' + parts.join(',') + ',' + last; };

  const designOf = (file) => (ctx.modelEntry(file || app.modelFile) || {}).design || null;
  const cfgOf = (design) => (design && app.designNotes?.[design]?.edit) || null;
  function defaults(cfg) {
    const s = {}; for (const g of cfg.groups) s[g.key] = g.default; for (const c of cfg.colours) s[c.key] = c.default; return s;
  }
  function stateFor(design) {
    const cfg = cfgOf(design); if (!cfg) return null;
    if (!state[design]) {
      let s = defaults(cfg);
      try { Object.assign(s, JSON.parse(store.get('edit.' + design) || '{}')); } catch (e) { }
      const q = new URLSearchParams(location.search).get('e');          // shared link wins
      if (q && design === designOf()) for (const kv of q.split(',')) { const [k, v] = kv.split(':'); if (k in s) s[k] = v; }
      state[design] = sanitize(cfg, s);
    }
    return state[design];
  }
  function sanitize(cfg, s) {
    for (const g of [...cfg.groups, ...cfg.colours]) if (!g.options.some(o => o.id === s[g.key])) s[g.key] = g.default;
    return s;
  }
  // "when mirror=wardrobe, wardrobe must be sliding": fix the other key, or fall back
  function applyRules(cfg, s, changed) {
    for (const r of cfg.requires || []) {
      const [wk, wv] = r.when, [nk, nv] = r.need, [ek, ev] = r.else;
      if (s[wk] === wv && s[nk] !== nv) { if (changed === wk) s[nk] = nv; else s[ek] = ev; }
    }
  }

  // ---------------------------------------------------------------- model: variants + colours
  function variantOk(tag, s) { return tag.split('&').every(c => { const [k, v] = c.split('='); return s[k] === v; }); }
  function applyTo(root, design, meshes) {
    const s = stateFor(design); const cfg = cfgOf(design);
    root.traverse(o => { const t = o.userData?.variant; o.userData._variantOff = !!(t && s && !variantOk(t, s)); });
    if (!cfg || !s) return;
    const rgbOf = (c) => { const o = c.options.find(x => x.id === s[c.key]); if (o?.rgb) return o.rgb;
      const w = cfg.colours[0]; return (w.options.find(x => x.id === s[w.key]) || w.options[0]).rgb; };   // "same as walls"
    for (const c of cfg.colours) {
      const re = new RegExp(`_${c.mat}(\\.\\d+)?$`), rgb = rgbOf(c);
      for (const m of meshes) for (const mat of new Set([m.material, m.userData._origMat, m.userData._dbl])) if (mat?.color && re.test(mat.name)) mat.color.setRGB(rgb[0], rgb[1], rgb[2]);
    }
  }
  function onModel(root) {
    const d = designOf(); applyTo(root, d, app.meshes);
    render();
  }
  function onCompare(root, file, meshes) { applyTo(root, designOf(file), meshes); }

  // ---------------------------------------------------------------- budget
  function budget(design, base) {
    const cfg = cfgOf(design), s = stateFor(design); if (!cfg || !base) return base;
    const rows = new Map(base.rows.map(r => [r[3] || r[0], r.slice(0, 3)]));
    for (const g of cfg.groups) {
      const o = g.options.find(x => x.id === s[g.key]) || g.options[0];
      for (const [k, r] of Object.entries(o.rows)) { if (r) rows.set(k, r); else rows.delete(k); }
    }
    const order = cfg.order || [...rows.keys()];
    const out = order.filter(k => rows.has(k)).map(k => rows.get(k));
    for (const [k, r] of rows) if (!order.includes(k)) out.push(r);
    const total = out.reduce((a, r) => a + num(r[2]), 0);
    return { ...base, rows: out, total: inr(total), _sum: total, _base: base.rows.reduce((a, r) => a + num(r[2]), 0) };
  }

  // ---------------------------------------------------------------- UI
  function render() {
    const d = designOf(), cfg = cfgOf(d);
    btn.classList.toggle('hidden', !cfg);
    if (!cfg) { panel.classList.add('hidden'); panel.innerHTML = ''; return; }
    const s = stateFor(d), U = cfg.ui, B = budget(d, app.designNotes[d].budget), diff = B._sum - B._base;
    panel.classList.toggle('hidden', !open); btn.classList.toggle('on', open);
    const presetOn = (p) => { const want = { ...defaults(cfg), ...p.choices }; return cfg.groups.every(g => s[g.key] === want[g.key]); };
    panel.innerHTML = `<div class="e-head"><b>${esc(U.title)}</b><button class="small" data-x title="Close">✕</button></div>
      <div class="e-intro">${esc(U.intro)}</div>
      <div class="e-total"><span>${esc(U.total)}</span><b>${B.total}</b><em class="${diff > 0 ? 'up' : diff < 0 ? 'down' : ''}">${diff ? (diff > 0 ? '+' : '−') + inr(Math.abs(diff)) + ' ' + esc(U.vs) : ''}</em></div>
      <div class="e-lbl">${esc(U.presets)}</div><div class="e-chips">${cfg.presets.map(p => `<button class="e-chip ${presetOn(p) ? 'on' : ''}" data-p="${p.id}">${esc(p.label)}</button>`).join('')}</div>` +
      cfg.groups.map(g => {
        const cur = g.options.find(o => o.id === s[g.key]);
        return `<div class="e-grp"><div class="e-lbl">${esc(g.label)}${g.visual ? '' : ` <span class="e-bo">${esc(U.budgetOnly)}</span>`}</div>
          <div class="e-chips">${g.options.map(o => { const r = Object.values(o.rows).find(Boolean); return `<button class="e-chip ${o.id === s[g.key] ? 'on' : ''}" data-g="${g.key}" data-o="${o.id}">${esc(o.label)}</button>`; }).join('')}</div>
          ${cur?.note ? `<div class="e-note">${esc(cur.note)}</div>` : ''}</div>`;
      }).join('') +
      `<div class="e-lbl e-sec">${esc(U.colours)}</div>` +
      cfg.colours.map(c => `<div class="e-grp"><div class="e-lbl">${esc(c.label)}: <span class="e-cur">${esc((c.options.find(o => o.id === s[c.key]) || {}).label)}</span></div><div class="e-sw">` +
        c.options.map(o => { const rgb = o.rgb || rgbFirst(cfg, s); return `<button class="e-dot ${o.id === s[c.key] ? 'on' : ''}" data-c="${c.key}" data-o="${o.id}" title="${esc(o.label)}" style="background:${css(rgb)}">${o.rgb ? '' : '='}</button>`; }).join('') + `</div></div>`).join('') +
      `<div class="e-foot"><button class="small" data-reset>${esc(U.reset)}</button><button class="small" data-copy>🔗 ${esc(U.copy)}</button></div>`;
    panel.querySelector('[data-x]').onclick = () => setOpen(false);
    panel.querySelectorAll('[data-p]').forEach(b => b.onclick = () => { const p = cfg.presets.find(x => x.id === b.dataset.p); const c = { ...s };
      for (const g of cfg.groups) c[g.key] = g.default; Object.assign(c, p.choices); set(d, c, null); });
    panel.querySelectorAll('[data-g]').forEach(b => b.onclick = () => set(d, { ...s, [b.dataset.g]: b.dataset.o }, b.dataset.g));
    panel.querySelectorAll('[data-c]').forEach(b => b.onclick = () => set(d, { ...s, [b.dataset.c]: b.dataset.o }, b.dataset.c));
    panel.querySelector('[data-reset]').onclick = () => set(d, defaults(cfg), null);
    panel.querySelector('[data-copy]').onclick = async (e) => {
      const u = new URL(location); u.searchParams.set('model', app.modelFile);
      u.searchParams.set('e', Object.entries(s).filter(([k, v]) => v !== defaults(cfg)[k]).map(([k, v]) => `${k}:${v}`).join(','));
      try { await navigator.clipboard.writeText(u.toString()); } catch (x) { }
      history.replaceState(null, '', u); e.target.textContent = '✓ ' + U.copied;
    };
  }
  const css = (rgb) => { const g = (v) => Math.round(255 * (v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055)); return `rgb(${g(rgb[0])},${g(rgb[1])},${g(rgb[2])})`; };
  const rgbFirst = (cfg, s) => { const w = cfg.colours[0]; return (w.options.find(x => x.id === s[w.key]) || w.options[0]).rgb; };

  function set(design, next, changed) {
    const cfg = cfgOf(design); applyRules(cfg, next, changed); sanitize(cfg, next);
    const prev = state[design]; state[design] = next;
    store.set('edit.' + design, JSON.stringify(next));
    const variantsChanged = !prev || cfg.groups.some(g => g.visual && prev[g.key] !== next[g.key]);
    applyTo(app.model, design, app.meshes);
    if (variantsChanged) { ctx.applyVisibility(); ctx.imm.onModel(app.model); }
    if (app.compare && designOf(app.compare.file) === design) { applyTo(app.compare.root, design, app.compare.meshes); ctx.applyVisibility(); }
    ctx.updateDesignUI(); render();
  }
  function setOpen(v) { open = v; store.set('editOpen', v ? 1 : 0); render(); if (v) { ctx.showRight && ctx.showRight(); panel.scrollIntoView({ block: 'nearest' }); } }
  btn.onclick = () => setOpen(!open);

  app.editBudget = (design, base) => budget(design, base);
  return { onModel, onCompare, render, setOpen, state: (d) => ({ ...stateFor(d || designOf()) }), set: (patch) => { const d = designOf(); set(d, { ...stateFor(d), ...patch }, Object.keys(patch)[0]); } };
}
