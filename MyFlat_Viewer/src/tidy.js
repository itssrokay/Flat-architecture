// Declutter pass (19 Nov 2026). Moves nothing that other modules rely on: ids and handlers stay; this file only
// shortens labels, adds a compact walk hint, and sets body classes that src/tidy.css.part (in styles.css) uses.
const $ = (id) => document.getElementById(id);
const hi = () => document.documentElement.lang === 'hi';
const body = document.body;
body.classList.add('tidy');
if (/[?&]debug\b/.test(location.search)) body.classList.add('dbg');
$('debugBtn')?.addEventListener('click', () => setTimeout(() => body.classList.toggle('dbg', $('debugBtn').classList.contains('on')), 0));

// 1. Plan picker: show the short plan name; the full description stays in the tooltip.
const sel = $('modelSelect');
function shorten() {
  for (const o of sel?.options || []) {
    const full = o.dataset.full || o.textContent;
    const short = full.replace(/^V\d+(\.\d+)?\s*·\s*/, '').split(':')[0].trim();
    if (!o.dataset.full) o.dataset.full = full;
    if (o.textContent !== short) { o.textContent = short; o.title = full; }
  }
  if (sel) sel.title = sel.selectedOptions[0]?.dataset.full || sel.title;
}
if (sel) { new MutationObserver(shorten).observe(sel, { childList: true }); sel.addEventListener('change', shorten); shorten(); }

// 2. Lights / day-night become icon toggles (CSS draws the icon); keep an accessible name.
function lightLabels() {
  const l = $('lightsBtn'), n = $('nightBtn'); if (!l || !n) return;
  l.setAttribute('aria-label', hi() ? 'लाइट चालू/बंद (L)' : 'Lights on/off (L)');
  n.setAttribute('aria-label', hi() ? 'दिन / रात (N)' : 'Day / night (N)');
  l.title = l.getAttribute('aria-label'); n.title = n.getAttribute('aria-label');
}
lightLabels();

// 3. Walk box: one short line by default, full key list on demand.
const hud = $('walkHud'), full = hud?.querySelector('.hudFull');
if (full && !full.querySelector('.hint-short')) {
  const s = document.createElement('div'); s.className = 'hint-short';
  const k = document.createElement('button'); k.className = 'small keysBtn'; k.type = 'button';
  const txt = () => {
    const touch = matchMedia('(pointer: coarse)').matches;
    s.innerHTML = touch
      ? (hi() ? '<b>अंदर</b> · खींचकर देखें · <b>जॉयस्टिक</b> से चलें · दरवाज़े पर <b>टैप</b> करके खोलें' : '<b>Inside</b> · drag to look · <b>joystick</b> to walk · <b>tap</b> a door or window to open it')
      : (hi() ? '<b>अंदर</b> · खींचकर देखें · <b>W A S D</b> से चलें · दरवाज़े पर <b>क्लिक</b> करके खोलें' : '<b>Inside</b> · drag to look · <b>W A S D</b> to walk · <b>click</b> a door or window to open it');
    k.textContent = full.classList.contains('keys') ? (hi() ? 'कम दिखाएँ' : 'Fewer tips') : (hi() ? 'सभी कुंजियाँ' : 'All keys');
  };
  k.onclick = () => { full.classList.toggle('keys'); txt(); };
  full.prepend(s); full.querySelector('.hudRow')?.prepend(k); txt();
  new MutationObserver(() => { txt(); lightLabels(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
}
