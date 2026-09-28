// English / Hindi switch for the viewer's interface.
// Static and dynamic interface text is translated in place (a MutationObserver catches text the app writes later,
// e.g. "Lights OFF"); the original English is remembered so switching back is exact.
// Long content (design notes, the Learn guide) comes from separate Hindi JSON files, not from here.

const ROOMS = { 'Room 1': 'कमरा 1', 'Room 2': 'कमरा 2', 'Kitchen': 'रसोई', 'Bathroom 1': 'बाथरूम 1', 'Bathroom 2': 'बाथरूम 2', 'Passage': 'गलियारा',
  'Hall': 'हॉल', 'Balcony': 'बालकनी', 'Stair': 'सीढ़ी', 'Open Square': 'खुला आँगन' };
const LABELS = {
  'Open / close window': 'खिड़की खोलें / बंद करें', 'Open / close wardrobe door': 'अलमारी का दरवाज़ा खोलें / बंद करें', 'Open / close loft': 'लॉफ़्ट खोलें / बंद करें',
  'Slide door open / closed': 'दरवाज़ा सरकाएँ', 'Slide window open / closed': 'खिड़की सरकाएँ', 'Slide wardrobe door': 'अलमारी का दरवाज़ा सरकाएँ',
  'Draw / open sheer': 'पर्दा खींचें / हटाएँ', 'Open': 'खोलें', 'Close': 'बंद करें', 'Open / close': 'खोलें / बंद करें',
};
const D = {
  ...ROOMS, ...LABELS,
  // top bar & toolbar
  '📘 Learn': '📘 सीखें', 'Top': 'ऊपर से', 'Iso': 'तिरछा', 'Persp': 'पर्सपेक्टिव', 'Ortho': 'ऑर्थो', 'Roof ON': 'छत चालू', 'Roof OFF': 'छत बंद', 'Labels': 'नाम',
  'Edges': 'किनारे', 'Status': 'स्थिति', 'Plan compare': 'नक्शे से तुलना', 'Debug': 'डीबग', 'Overview': 'बाहर से', 'Walk': 'अंदर चलें', 'Lights ON': 'लाइट चालू',
  'Lights OFF': 'लाइट बंद', 'Day': 'दिन', 'Night': 'रात', 'Room size': 'कमरे का नाप', 'Dimensions': 'नाप', 'Hover info': 'जानकारी', '⛶ Immersive': '⛶ पूरी स्क्रीन', 'Reset': 'रीसेट',
  '🏠 Overview': '🏠 बाहर से', '🚶 Walk': '🚶 अंदर', '💡 Lights': '💡 लाइट', '🌙 Night': '🌙 रात', '📐 Room size': '📐 कमरे का नाप', '📏 Dims': '📏 नाप',
  '🛈 Hover info': '🛈 जानकारी', '✕ Exit': '✕ बाहर', 'Room 1': 'कमरा 1', 'Balcony': 'बालकनी', 'Open all': 'सब खोलें', 'Close all': 'सब बंद करें',
  // left panel
  'Interior design': 'इंटीरियर डिज़ाइन', 'Room 1 interior': 'कमरा 1 इंटीरियर', 'Architecture only': 'सिर्फ़ ढाँचा', 'Compare side by side with': 'इसके साथ तुलना करें',
  '— off —': '— बंद —', 'Rooms': 'कमरे', 'Click a room for an eye-level view. Arrows show extra viewpoints.': 'कमरे पर क्लिक करें और अंदर पहुँचें। तीर से और जगहें दिखती हैं।',
  'Copy current view': 'यह व्यू कॉपी करें', 'Copied ✓': 'कॉपी हुआ ✓',
  'Design view (from balcony door)': 'डिज़ाइन व्यू (बालकनी दरवाज़े से)', 'Towards balcony (from door side)': 'बालकनी की ओर (दरवाज़े से)', 'Wardrobe & thick wall': 'अलमारी और मोटी दीवार',
  'Balcony (outside, looking south)': 'बालकनी (बाहर, दक्षिण की ओर)', 'From NE corner': 'उत्तर-पूर्व कोने से', 'From SE corner': 'दक्षिण-पूर्व कोने से', 'From NW corner': 'उत्तर-पश्चिम कोने से',
  'From SW corner': 'दक्षिण-पश्चिम कोने से', 'Centre': 'बीच से', 'From above (roof off)': 'ऊपर से (छत हटाकर)',
  // right panel
  'Inspector': 'विवरण', 'Click any wall, door, window, pillar, beam or step.': 'किसी भी दीवार, दरवाज़े, खिड़की, पिलर, बीम या सीढ़ी पर क्लिक करें।',
  'Click any wall, door, window, pillar, beam, step or piece of furniture.': 'किसी भी दीवार, दरवाज़े, खिड़की, पिलर, बीम, सीढ़ी या फ़र्नीचर पर क्लिक करें।',
  'Category': 'श्रेणी', 'Basis': 'आधार', 'Design option': 'डिज़ाइन विकल्प', 'Specification': 'विवरण', 'In simple words': 'आसान शब्दों में', 'Room': 'कमरा', 'Size': 'नाप',
  'Thickness': 'मोटाई', 'Section': 'सेक्शन', 'Collection': 'संग्रह', 'Part of': 'इसका हिस्सा', 'Parts': 'हिस्से', 'Opening width': 'खुली चौड़ाई', 'Opening height': 'खुली ऊँचाई',
  'Sill': 'सिल', 'Head': 'ऊपरी किनारा', 'Swing': 'खुलने की दिशा', 'Focus': 'पास जाएँ', 'Isolate category': 'सिर्फ़ यह श्रेणी', 'Clear': 'हटाएँ',
  'Why this is the default': 'यह डिफ़ॉल्ट क्यों है', 'Concept': 'सोच', 'Material & finish schedule': 'सामग्री और फ़िनिश सूची', 'Total': 'कुल', 'If it runs over:': 'बजट बढ़े तो:',
  // dock
  'Visibility': 'दिखाएँ / छुपाएँ', 'Show all': 'सब दिखाएँ', 'Hide all': 'सब छुपाएँ', 'Section cut': 'काटकर देखें', 'Cut above': 'ऊपर से काटें', 'Model opacity': 'मॉडल की पारदर्शिता',
  'Open / close': 'खोलें / बंद करें', 'Floor plan': 'फ़्लोर प्लान', 'Show plan': 'नक्शा दिखाएँ', 'Over model': 'मॉडल के ऊपर', 'On floor': 'फ़र्श पर',
  'Hide controls ▾': 'कंट्रोल छुपाएँ ▾', 'Controls ▴': 'कंट्रोल ▴', 'Off – drag to set height, tick to cut': 'बंद – ऊँचाई चुनें, टिक करके काटें', 'No openable parts in this model': 'इस मॉडल में खुलने वाले हिस्से नहीं',
  "The original plan is not to scale. It is stretched to the model's extents exactly as in Blender (PLAN_REFERENCE_OVERLAY).": 'असली नक्शा स्केल में नहीं है; इसे मॉडल के नाप पर फैलाया गया है।',
  // categories
  'Walls': 'दीवारें', 'Floors': 'फ़र्श', 'Ceiling / Roof': 'छत', 'Doors': 'दरवाज़े', 'Windows': 'खिड़कियाँ', 'Pillars': 'पिलर', 'Beams': 'बीम', 'Stairs': 'सीढ़ियाँ',
  'Railings': 'रेलिंग', 'Vents': 'रोशनदान', 'Ground': 'ज़मीन', 'Furniture': 'फ़र्नीचर', 'Wardrobe': 'अलमारी', 'Window & door systems': 'खिड़की-दरवाज़े', 'Curtains & soft': 'पर्दे और कपड़े',
  'False ceiling': 'फ़ॉल्स सीलिंग', 'Lighting': 'रोशनी', 'Finishes': 'फ़िनिश', 'Balcony decor': 'बालकनी सजावट', 'Plants': 'पौधे', 'Decor': 'सजावट',
  // status names
  'Confirmed': 'पक्का', 'Plan value': 'नक्शे से', 'Derived': 'निकाला गया', 'Provisional': 'अनुमान', 'Reference': 'संदर्भ', 'Interior design': 'इंटीरियर डिज़ाइन',
  // walk HUD, touch, cards
  'Look at ceiling': 'छत देखें', 'Lens': 'लेंस', 'Overview (step outside)': 'बाहर से देखें', 'Inside': 'अंदर',
  'Type': 'प्रकार', 'Spec': 'विवरण', 'Design': 'डिज़ाइन', 'Simply': 'आसान शब्दों में', 'All details': 'पूरा विवरण',
  'Loading model…': 'मॉडल लोड हो रहा है…', '🖼 See pictures': '🖼 तस्वीरें देखें', 'See pictures': 'तस्वीरें देखें',
};
const TITLES = {
  "Beginner's guide: what everything is made of, how homes are built, dictionary (G)": 'शुरुआती गाइड: हर चीज़ किससे बनी है, घर कैसे बनता है, शब्दकोश (G)',
  'Step outside and see the whole flat (orbit)': 'बाहर से पूरा फ़्लैट देखें', 'Stand inside at eye level': 'अंदर आँखों की ऊँचाई पर खड़े हों',
  'Light fittings on/off (L)': 'लाइट चालू/बंद (L)', 'Day / night (N)': 'दिन / रात (N)', 'Wall-by-wall size of the room you are in (M)': 'जिस कमरे में हैं उसकी हर दीवार का नाप (M)',
  'Show dimensions of parts; select an object for W/D/H lines': 'चीज़ों के नाप दिखाएँ', 'Point at anything to see what it is (I)': 'किसी चीज़ पर माउस रखें और जानें (I)',
  'Full-screen immersive mode (F)': 'पूरी स्क्रीन (F)', 'Reset camera and visibility': 'कैमरा और दृश्य रीसेट करें', 'Minimise this box': 'यह बॉक्स छोटा करें', 'Show the controls': 'कंट्रोल दिखाएँ',
  'Stand in the middle, look straight up with a wide lens (C)': 'बीच में खड़े होकर ऊपर छत देखें (C)', 'Raise eyes': 'आँखें ऊपर', 'Lower eyes': 'आँखें नीचे',
  'Open / close what the circle points at': 'गोले वाली चीज़ खोलें / बंद करें', 'Hide left panel ( [ )': 'बायाँ पैनल छुपाएँ', 'Hide right panel ( ] )': 'दायाँ पैनल छुपाएँ',
  'Show left panel ( [ )': 'बायाँ पैनल दिखाएँ', 'Show right panel ( ] )': 'दायाँ पैनल दिखाएँ', 'Minimise / expand': 'छोटा / बड़ा करें', 'Double-click to stand here': 'यहाँ खड़े होने के लिए डबल-क्लिक करें',
};
const rt = (s) => ROOMS[s] || s;
const RX = [
  [/^In (.+?) · eye ([\d.]+) ft above floor$/, (m, r, e) => `${rt(r)} में · आँखें फ़र्श से ${e} फ़ुट`],
  [/^In (.+)$/, (m, r) => ROOMS[r] ? `${rt(r)} में` : null],
  [/^On (.+?) · eye ([\d.]+) ft above floor$/, (m, r, e) => `${r} पर · आँखें फ़र्श से ${e} फ़ुट`],
  [/^(E|✋) · (.+)$/, (m, k, l) => `${k} · ${LABELS[l] || l}`],
  [/^(\d+) openable parts in this model$/, (m, n) => `इस मॉडल में ${n} खुलने वाले हिस्से`],
  [/^Cut at (.+) \((.+) m\) above floor level$/, (m, a, b) => `फ़र्श से ${a} (${b} मी) पर काट`],
  [/^(.+) wide × (.+) deep × (.+) high$/, (m, a, b, c) => `${a} चौड़ा × ${b} गहरा × ${c} ऊँचा`],
  [/^(.+) × (.+) overall · (\d+) sq ft$/, (m, a, b, c) => `${a} × ${b} कुल · ${c} वर्ग फ़ुट`],
  [/^floor to ceiling (.+)$/, (m, a) => `फ़र्श से छत ${a}`],
  [/^Budget · (.+)$/, (m, a) => `बजट · ${a}`],
  [/^(.+) can't open further: it hits the (.+)$/, (m, a, b) => `${a} और नहीं खुल सकता: ${b} से टकरा रहा है`],
  [/^double-click \(or click inside\) to open \/ close$/, () => 'खोलने / बंद करने के लिए डबल-क्लिक करें'],
  [/^Room 1 · (DEFAULT|Option [A-D]) \((.+)\)$/, (m, a, b) => `कमरा 1 · ${a.replace('Option', 'विकल्प')} (${({ 'Warm Contemporary': 'गर्म समकालीन', 'Japandi Calm': 'जापांडी शांत', 'Minimal Modern': 'मिनिमल मॉडर्न', 'Indian Modern': 'भारतीय आधुनिक', 'Smart Budget': 'स्मार्ट बजट' })[b] || b})`],
  [/^V1\.1 Architecture \(Room 1 corrected\)$/, () => 'V1.1 ढाँचा (कमरा 1 सुधारा हुआ)'], [/^V1 Architecture \(untouched baseline\)$/, () => 'V1 ढाँचा (मूल)'],
];
const HTML_BLOCKS = {
  '.hint-desk': '<b>अंदर</b> · <b>ड्रैग</b> करके चारों ओर (छत भी) देखें · <b>WASD</b> / तीर या <b>माउस व्हील</b> से चलें · Shift तेज़ · <b>R / V</b> आँखें ऊपर / नीचे · दरवाज़े, खिड़की या अलमारी पर <b>क्लिक</b> (या <b>E</b>) करके खोलें / बंद करें · <b>C</b> छत · <b>पिंच / Ctrl+व्हील</b> या − / + लेंस · L लाइट · N रात',
  '.hint-touch': '<b>अंदर</b> · एक उँगली से घुमाकर देखें · नीचे बाएँ <b>जॉयस्टिक</b> से चलें · दरवाज़े, खिड़की या अलमारी को <b>टैप</b> करके खोलें / बंद करें · <b>पिंच</b> से चौड़ा लेंस · ⬆ ⬇ आँखें ऊपर / नीचे',
  '#dockOpenNote': 'अलमारी का दरवाज़ा, खिड़की, बालकनी दरवाज़ा या पर्दा खोलने के लिए डबल-क्लिक करें। अंदर (वॉक मोड) में बस क्लिक करें, या उसकी ओर देखकर <b>E</b> दबाएँ।',
};

export function setupI18n({ onChange } = {}) {
  let lang = 'en';
  try { lang = new URLSearchParams(location.search).get('lang') || localStorage.getItem('myflat.lang') || 'en'; } catch (e) { }
  if (lang !== 'hi') lang = 'en';
  const orig = new WeakMap(), mine = new WeakMap(), origAttr = new WeakMap(), origHTML = new Map();
  const SKIP = (el) => el && el.closest && el.closest('script,style,#statusbar,#learn,textarea,input,.why,.bnote,.sched td:nth-child(2),.budget .bd');
  function tr(s) {
    const t = s.trim(); if (!t) return null;
    let out = D[t];
    if (!out) for (const [re, fn] of RX) { const m = t.match(re); if (m) { out = fn(...m); if (out) break; } }
    if (!out || out === t) return null;
    return s.replace(t, out);
  }
  function doText(n) {
    if (SKIP(n.parentElement)) return;
    if (lang === 'hi') {
      if (mine.get(n) === n.nodeValue) return;           // already ours
      orig.set(n, n.nodeValue);
      const t = tr(n.nodeValue); if (t) { mine.set(n, t); n.nodeValue = t; } else mine.delete(n);
    } else if (orig.has(n) && mine.get(n) === n.nodeValue) { n.nodeValue = orig.get(n); mine.delete(n); }
  }
  function doAttrs(el) {
    if (!el.getAttribute) return;
    for (const a of ['title', 'placeholder']) {
      const v = el.getAttribute(a); if (v == null) continue;
      const rec = origAttr.get(el) || {};
      if (lang === 'hi') { if (rec[a + '_mine'] === v) continue; const h = TITLES[v] || D[v]; rec[a] = v; if (h) { rec[a + '_mine'] = h; el.setAttribute(a, h); } origAttr.set(el, rec); }
      else if (rec[a + '_mine'] === v) { el.setAttribute(a, rec[a]); delete rec[a + '_mine']; }
    }
  }
  function walk(root) {
    if (root.nodeType === 3) { doText(root); return; }
    if (root.nodeType !== 1 || SKIP(root)) return;
    doAttrs(root);
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    for (let n = w.nextNode(); n; n = w.nextNode()) { if (n.nodeType === 3) doText(n); else doAttrs(n); }
  }
  function blocks() {
    for (const [sel, hi] of Object.entries(HTML_BLOCKS)) document.querySelectorAll(sel).forEach(el => {
      if (!origHTML.has(el)) origHTML.set(el, el.innerHTML);
      el.innerHTML = lang === 'hi' ? hi : origHTML.get(el);
    });
  }
  const mo = new MutationObserver((list) => {
    if (lang !== 'hi') return;
    for (const m of list) {
      if (m.type === 'characterData') doText(m.target);
      else if (m.type === 'attributes') doAttrs(m.target);
      else m.addedNodes.forEach(walk);
    }
  });
  function apply() {
    document.documentElement.lang = lang;
    document.body.classList.toggle('lang-hi', lang === 'hi');
    blocks(); walk(document.body);
    const b = document.getElementById('langBtn'); if (b) { b.textContent = lang === 'hi' ? 'EN' : 'हिंदी'; b.title = lang === 'hi' ? 'Switch to English' : 'हिंदी में देखें'; }
  }
  function setLang(l) {
    lang = l === 'hi' ? 'hi' : 'en';
    try { localStorage.setItem('myflat.lang', lang); } catch (e) { }
    apply(); onChange && onChange(lang);
  }
  mo.observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ['title', 'placeholder'] });
  document.getElementById('langBtn').onclick = () => setLang(lang === 'hi' ? 'en' : 'hi');
  apply();
  return { get lang() { return lang; }, setLang, apply, tr };
}
