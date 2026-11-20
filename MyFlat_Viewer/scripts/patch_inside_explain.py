# Adds "Explain this layer" (plain words, why, steps, how to check, video + article links) to each row of the layer cards.
# Run from MyFlat_Viewer: python3 scripts/patch_inside_explain.py   (safe to re-run)
p = 'src/inside.js'; s = open(p).read()
if 'EXPLAIN' not in s:
    def R(a, b):
        global s; assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
    R("let DATA = null, SHOP = null;", "let DATA = null, SHOP = null, EXPLAIN = {};\nfetch(`./models/explain.json?v=${V}`).then((r) => r.json()).then((e) => { EXPLAIN = e; }).catch(() => {});")
    R("  tLayers: ['Layers', 'परतें'],", """  exMore: ['Explain ▾', 'समझाएँ ▾'], exLess: ['Hide ▴', 'छिपाएँ ▴'], exWhy: ['Why it matters', 'क्यों ज़रूरी'], exHow: ['How it is done', 'कैसे होता है'], exCheck: ['How to check it', 'कैसे जाँचें'],
  exVideo: ['▶ Video', '▶ वीडियो'], exRead: ['📄 Read', '📄 पढ़ें'], exMoreVid: ['More videos on YouTube', 'YouTube पर और वीडियो'], exNote: ['Note', 'ध्यान दें'],
  tLayers: ['Layers', 'परतें'],""")
    R("""<div class="w">${esc(T(l.what))}</div>${l.cost ? `<div class="c">${esc(l.cost)}</div>` : ''}</div></li>`).join('')}</ol>""",
      """<div class="w">${esc(T(l.what))}</div>${l.cost ? `<div class="c">${esc(l.cost)}</div>` : ''}${exHTML(l)}</div></li>`).join('')}</ol>""")
    R("  side.querySelectorAll('.im-list li').forEach((li) => {", """  side.querySelectorAll('.im-exb').forEach((b) => b.onclick = (e) => { e.stopPropagation(); const box = b.nextElementSibling; const open = box.classList.toggle('open'); b.textContent = T(open ? L10N.exLess : L10N.exMore);
    const li = b.closest('li'); if (open && three) three.highlight(+li.dataset.i, true); });
  side.querySelectorAll('.im-ex a').forEach((a) => a.onclick = (e) => e.stopPropagation());
  side.querySelectorAll('.im-list li').forEach((li) => {""")
    R("function swatch(l) {", """function exHTML(l) {
  const x = EXPLAIN[l.kind]; if (!x || !T(x.simple)) return '';
  const sec = (h, t) => (t && T(t) ? `<h6>${T(h)}</h6><p>${esc(T(t))}</p>` : '');
  const steps = (x.how || []).length ? `<h6>${T(L10N.exHow)}</h6><ol>${x.how.map((s) => `<li>${esc(T(s))}</li>`).join('')}</ol>` : '';
  const links = (x.links || []).map((k) => `<a class="ex-${k.t}" href="${esc(k.url)}" target="_blank" rel="noopener">${T(k.t === 'video' ? L10N.exVideo : L10N.exRead)} · ${esc(k.n)}</a>`).join('')
    + (x.more ? `<a class="ex-more" href="${esc(x.more)}" target="_blank" rel="noopener">🔎 ${T(L10N.exMoreVid)}</a>` : '');
  return `<button class="im-exb" type="button">${T(L10N.exMore)}</button><div class="im-ex"><p class="ex-simple">${esc(T(x.simple))}</p>${sec(L10N.exWhy, x.why)}${steps}${sec(L10N.exCheck, x.check)}${sec(L10N.exNote, x.note)}${links ? `<div class="ex-links">${links}</div>` : ''}</div>`;
}
function swatch(l) {""")
    open(p, 'w').write(s); print('inside.js patched')
if "querySelectorAll('.im-list > li')" not in s:
    s = s.replace("side.querySelectorAll('.im-list li').forEach((li) => { li.onmouseenter", "side.querySelectorAll('.im-list > li').forEach((li) => { li.onmouseenter", 1)
    s = s.replace("modal.querySelectorAll('.im-list li').forEach((li) => li.classList.toggle", "modal.querySelectorAll('.im-list > li').forEach((li) => li.classList.toggle", 1)
    open(p, 'w').write(s); print('nested li fix')
c = 'src/styles.css'; css = open(c).read()
if '.im-ex ol li' not in css:
    css = css.split('/* ---- layer "Explain"')[0].rstrip() + '\n'
if '.im-exb' not in css:
    css += """
/* ---- layer "Explain" (20 Nov 2026) ---- */
#insideModal .im-exb { margin-top: 6px; padding: 3px 10px; font-size: 12.5px; border-radius: 999px; border: 1px solid #d9c7a0; background: #fffaf0; color: #7a4d0f; cursor: pointer; }
#insideModal .im-exb:hover { background: #fbefd6; }
#insideModal .im-ex { display: none; margin-top: 8px; padding: 10px 12px; background: #fff; border: 1px solid #eadfcb; border-radius: 10px; font-size: 13px; line-height: 1.5; cursor: auto; }
#insideModal .im-ex.open { display: block; }
#insideModal .im-ex .ex-simple { margin: 0 0 6px; font-size: 13.5px; }
#insideModal .im-ex h6 { margin: 8px 0 2px; font-size: 12px; color: #7a4d0f; }
#insideModal .im-ex p { margin: 0; }
#insideModal .im-ex ol { margin: 2px 0 0; padding-left: 18px; }
#insideModal .ex-links { display: flex; flex-direction: column; gap: 5px; margin-top: 10px; }
#insideModal .ex-links a { display: block; padding: 6px 9px; border-radius: 8px; text-decoration: none; font-size: 12.5px; border: 1px solid #e3e3e3; color: #1f2328; background: #fafafa; }
#insideModal .ex-links a.ex-video { border-color: #f1c4c4; background: #fff5f5; }
#insideModal .ex-links a.ex-article { border-color: #c9d8f0; background: #f4f8ff; }
#insideModal .ex-links a:hover { filter: brightness(.97); }
#insideModal .ex-links a.ex-more { color: #555; }
#insideModal .im-ex ol li, #insideModal .im-ex ol li:hover { display: list-item; padding: 1px 0; border: 0; background: none; border-radius: 0; cursor: auto; }
"""
    open(c, 'w').write(css); print('css added')
