# Adds the "🏠 Ceilings" tab to src/compare.js (run from MyFlat_Viewer).
import re
p = 'src/compare.js'; s = open(p).read()
def R(a, b):
    global s; assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
R("  inPlan: ['In this plan only', 'सिर्फ़ इस प्लान का'],", """  inPlan: ['In this plan only', 'सिर्फ़ इस प्लान का'], ceil: ['🏠 Ceilings', '🏠 छत'], option: ['Option', 'विकल्प'], rate: ['Rate (₹/sq ft, installed)', 'दाम (₹/वर्ग फ़ुट, लगवाकर)'], forUs: ['For our flat', 'हमारे फ़्लैट के लिए'],
  height: ['Height', 'ऊँचाई'], life: ['Lasts', 'चलेगा'], score: ['My rating /10', 'मेरी रेटिंग /10'], sHall: ['Hall', 'हॉल'], sBed: ['Bedroom', 'बेडरूम'], sWet: ['Bath', 'बाथ'], why: ['Why', 'क्यों'], prosC: ['Pros', 'फ़ायदे'], consC: ['Cons', 'नुक़सान'], myPlan: ['My choice, room by room', 'मेरा चुनाव, कमरे के हिसाब से'], pick: ['Pick', 'चुनाव'], tipsC: ['Before you start', 'शुरू करने से पहले'], srcC: ['Sources', 'स्रोत'],""")
R("let DATA = null, SHOP = null,", "let CEIL = null;\nfetch('./models/ceilings.json?v=34').then((r) => r.json()).then((d) => { CEIL = d; }).catch((e) => console.warn('ceilings', e));\nlet DATA = null, SHOP = null,")
R("['checks', L.checks]];", "['checks', L.checks], ['ceil', L.ceil]];")
R("  else { bar.innerHTML = `<div class=\"cm-note\">${esc(T(L.checkNote))}</div>`; drawChecks(body); }",
  "  else if (state.tab === 'ceil') { bar.innerHTML = `<div class=\"cm-note\"><b>${esc(T(CEIL?.summary || ''))}</b></div>`; drawCeil(body); }\n  else { bar.innerHTML = `<div class=\"cm-note\">${esc(T(L.checkNote))}</div>`; drawChecks(body); }")
R("window.compare = { openCompare };", r"""function drawCeil(body) {
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
window.compare = { openCompare };""")
open(p, 'w').write(s); print('patched')
