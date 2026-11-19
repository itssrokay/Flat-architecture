# V1.3b: main door on the hall west wall, TV wall moved north of it, 4 hall/flat options with pros, cons, lifespan and verdict.
# Run from the MyFlat folder after apply_v13_viewer.py. Safe to re-run.
import json, collections, re, sys, os
OD = collections.OrderedDict
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")

def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

# ---------------- models.json: four V1.3 entries after V1.2
P = "MyFlat_Viewer/models/models.json"
d = json.load(open(P, encoding="utf-8"), object_pairs_hook=OD)
d["models"] = [m for m in d["models"] if not m["file"].startswith("MyFlat_V1_3_")]
at = next((i for i, m in enumerate(d["models"]) if m["file"] == "MyFlat_V1_2_Room2_Ensuite.glb"), len(d["models"]) - 1) + 1
def entry(f, label, short, design): return OD([("file", f), ("label", label), ("short", short), ("group", "version"), ("design", design), ("startView", "Hall:0"), ("manifest", f.replace(".glb", ".manifest.json"))])
d["models"][at:at] = [
    entry("MyFlat_V1_3_Hall_Recommended.glb", "V1.3 · Recommended: matt tiles + WPC TV wall", "V1.3 Recommended", "HALL_REC"),
    entry("MyFlat_V1_3_Hall_Budget.glb", "V1.3 · Budget plain: double-charge tiles + plain paint", "V1.3 Budget plain", "HALL_BUDGET"),
    entry("MyFlat_V1_3_Hall_LongLasting.glb", "V1.3 · Long-lasting: full-body tiles + porcelain slab TV wall", "V1.3 Long-lasting", "HALL_LONG"),
    entry("MyFlat_V1_3_Hall_Marble.glb", "V1.3 · Marble classic: marble hall + limewash TV wall", "V1.3 Marble classic", "HALL_MARBLE"),
]
json.dump(d, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

NOTE_EN = "Furniture, lights and the fan are drawn for the layout and are not in this total. Rough 2026 estimates, not quotes."
NOTE_HI = "फ़र्नीचर, लाइट और पंखा सिर्फ़ लेआउट दिखाने के लिए हैं, इस कुल में नहीं। 2026 के मोटे अंदाज़े, पक्का रेट नहीं।"
DOOR_EN = "The main door (3 ft, middle of the hall's west wall) opens into an entry with a shoe cabinet. The TV wall sits north of the door, centred under the beam; the dining table sits south, near window W7."
DOOR_HI = "मुख्य दरवाज़ा (3 फीट, हॉल की पश्चिमी दीवार के बीच में) खुलते ही जूते की अलमारी वाली जगह। TV दीवार दरवाज़े के उत्तर में, बीम के ठीक नीचे; डाइनिंग टेबल दक्षिण में, खिड़की W7 के पास।"
OPT = {
 "HALL_REC": dict(
  en=OD(title="V1.3 · Recommended", tagline="Matt GVT tiles through the flat, an 8 ft WPC fluted TV wall with a metal frame, anti-skid bathrooms and Kota outside.",
    why="My pick for most families: it looks finished, needs almost no upkeep and sits in the middle on cost. " + DOOR_EN,
    budget=OD(total="₹1,95,000–3,26,000", rows=[
      ["Floors", "Matt GVT 600×1200 in hall, passage, Room 2 and kitchen; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,35,000–2,27,000"],
      ["Skirting", "4 inch tile skirting, whole flat", "₹20,000–30,000"],
      ["Hall paint", "Premium washable emulsion over putty and primer, about 900 sq ft", "₹22,000–36,000"],
      ["TV wall", "WPC fluted panel 8 ft × 8'5\" (about 70 sq ft), black aluminium frame, LED strip", "₹16,000–29,000"],
      ["Pillars", "304 steel corner guards on both pillars", "₹2,000–4,000"]], note=NOTE_EN),
    sections=OD([
      ("Pros", ul(["Matt tile hides Bihar's dust and is safe with wet feet", "One tile through the flat makes it look bigger", "WPC is waterproof and termite-proof and hides the TV wires", "Almost no upkeep: mop and wipe"])),
      ("Cons", ul(["A deep chip in GVT shows the body colour (keep a spare box)", "WPC looks like wood from far, not up close", "Paint needs redoing every 6–8 years"])),
      ("How long it lasts", ul(["Floor tiles: 15–25 years", "WPC TV wall: 12–15 years", "Premium paint: 6–8 years before a repaint"])),
      ("Verdict", "Best value. Pick this unless money is very tight or you want to build once for 25 years."),
    ])),
  hi=OD(title="V1.3 · सुझाया गया", tagline="पूरे घर में मैट GVT टाइल, धातु की पट्टी वाली 8 फीट की WPC फ्लूटेड TV दीवार, बाथरूम में एंटी-स्किड और बाहर कोटा।",
    why="ज़्यादातर परिवारों के लिए मेरी पसंद: अच्छा दिखता है, देखभाल लगभग नहीं, और ख़र्च बीच का। " + DOOR_HI,
    budget=OD(total="₹1,95,000–3,26,000", rows=[
      ["फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई में मैट GVT 600×1200; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,35,000–2,27,000"],
      ["स्कर्टिंग", "पूरे घर में 4 इंच टाइल स्कर्टिंग", "₹20,000–30,000"],
      ["हॉल पेंट", "पुट्टी और प्राइमर पर प्रीमियम धुलने वाला इमल्शन, लगभग 900 वर्ग फुट", "₹22,000–36,000"],
      ["TV दीवार", "WPC फ्लूटेड पैनल 8 फीट × 8'5\" (लगभग 70 वर्ग फुट), काली एल्युमिनियम पट्टी, LED पट्टी", "₹16,000–29,000"],
      ["खंभे", "दोनों खंभों पर 304 स्टील कॉर्नर गार्ड", "₹2,000–4,000"]], note=NOTE_HI),
    sections=OD([
      ("फ़ायदे", ul(["मैट टाइल धूल छिपाती है और गीले पैर से सुरक्षित है", "पूरे घर में एक टाइल से घर बड़ा लगता है", "WPC वॉटरप्रूफ़ है, दीमक नहीं लगती, TV के तार छिपाता है", "देखभाल लगभग नहीं: पोंछा और कपड़ा"])),
      ("कमियाँ", ul(["GVT में गहरा चटका लगे तो नीचे का रंग दिखता है (एक डिब्बा बचाकर रखें)", "WPC दूर से लकड़ी जैसा, पास से नहीं", "पेंट हर 6–8 साल में दोबारा"])),
      ("कितना चलेगा", ul(["फ़र्श टाइल: 15–25 साल", "WPC TV दीवार: 12–15 साल", "प्रीमियम पेंट: 6–8 साल"])),
      ("फ़ैसला", "पैसे के हिसाब से सबसे बढ़िया। बहुत तंग बजट न हो, या 25 साल के लिए एक बार में काम न कराना हो, तो यही लें।"),
    ]))),
 "HALL_BUDGET": dict(
  en=OD(title="V1.3 · Budget plain", tagline="Double-charge tiles, plain washable paint, a TV on the wall and nothing extra. Room 1 shows Option D (Smart Budget).",
    why="Spends money only where it lasts: tough tiles, anti-skid bathrooms and Kota outside. Everything else can be upgraded later without breaking anything. " + DOOR_EN,
    budget=OD(total="₹1,58,000–2,47,000", rows=[
      ["Floors", "Double-charge vitrified 600×600 in hall, passage, Room 2 and kitchen; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,24,000–1,94,000"],
      ["Skirting", "4 inch tile skirting, whole flat", "₹20,000–30,000"],
      ["Hall paint", "Economy washable emulsion (for example Asian Paints Tractor Emulsion or Berger Bison Glow), about 900 sq ft", "₹11,000–18,000"],
      ["TV", "Wall bracket, PVC wire casing, laminated shelf", "₹3,000–5,000"]], note=NOTE_EN),
    sections=OD([
      ("Pros", ul(["Lowest cost", "Double-charge tile is very tough and small chips barely show", "Nothing to maintain except paint", "Add the WPC TV wall later without touching the floor"])),
      ("Cons", ul(["Plain look; 2 × 2 ft tiles show more joints", "Few stone or wood looks in double charge", "Economy paint needs redoing every 4–5 years", "Visible TV wires unless cased"])),
      ("How long it lasts", ul(["Floor tiles: 20–25 years", "Economy paint: 4–5 years before a repaint"])),
      ("Verdict", "Pick this if money is tight now. The floor will outlast the Recommended one; the looks can come later."),
    ])),
  hi=OD(title="V1.3 · सादा बजट", tagline="डबल चार्ज टाइल, सादा धुलने वाला पेंट, दीवार पर TV, और कुछ फ़ालतू नहीं। कमरा 1 में ऑप्शन D (स्मार्ट बजट)।",
    why="पैसा वहीं लगता है जहाँ टिकाऊ हो: मज़बूत टाइल, बाथरूम में एंटी-स्किड और बाहर कोटा। बाक़ी सब बाद में, कुछ तोड़े बिना, अपग्रेड हो सकता है। " + DOOR_HI,
    budget=OD(total="₹1,58,000–2,47,000", rows=[
      ["फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई में डबल चार्ज 600×600; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,24,000–1,94,000"],
      ["स्कर्टिंग", "पूरे घर में 4 इंच टाइल स्कर्टिंग", "₹20,000–30,000"],
      ["हॉल पेंट", "किफ़ायती धुलने वाला इमल्शन (जैसे एशियन पेंट्स ट्रैक्टर इमल्शन या बर्जर बाइसन ग्लो), लगभग 900 वर्ग फुट", "₹11,000–18,000"],
      ["TV", "दीवार ब्रैकेट, तार के लिए PVC केसिंग, लैमिनेट शेल्फ़", "₹3,000–5,000"]], note=NOTE_HI),
    sections=OD([
      ("फ़ायदे", ul(["सबसे कम ख़र्च", "डबल चार्ज टाइल बहुत मज़बूत, छोटे चटके मुश्किल से दिखते", "पेंट के अलावा कोई देखभाल नहीं", "WPC TV दीवार बाद में, फ़र्श छेड़े बिना"])),
      ("कमियाँ", ul(["सादा लुक; 2 × 2 फीट टाइल में जोड़ ज़्यादा दिखते", "डबल चार्ज में पत्थर या लकड़ी वाले लुक कम", "किफ़ायती पेंट हर 4–5 साल में दोबारा", "केसिंग न हो तो TV के तार दिखते"])),
      ("कितना चलेगा", ul(["फ़र्श टाइल: 20–25 साल", "किफ़ायती पेंट: 4–5 साल"])),
      ("फ़ैसला", "अभी बजट तंग हो तो यही लें। फ़र्श सुझाए गए प्लान से भी ज़्यादा चलेगा; सजावट बाद में हो सकती है।"),
    ]))),
 "HALL_LONG": dict(
  en=OD(title="V1.3 · Long-lasting", tagline="Full-body vitrified floors, a porcelain-slab TV wall with steel profiles and steel guards. Built once, left alone for 25 years.",
    why="For a family that wants to do the work once. Every surface is the toughest of its kind: colour that runs through the tile, a wall finish that never fades or swells, and stainless steel that never rusts. " + DOOR_EN,
    budget=OD(total="₹2,30,000–3,85,000", rows=[
      ["Floors", "Full-body vitrified 600×1200 matt in hall, passage, Room 2 and kitchen; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,68,000–2,81,000"],
      ["Skirting", "4 inch full-body tile skirting, whole flat", "₹20,000–30,000"],
      ["Hall paint", "Premium washable emulsion over putty and primer, about 900 sq ft", "₹22,000–36,000"],
      ["TV wall", "Porcelain slabs 800×1600 (about 70 sq ft) with 304 brushed steel profiles, granite-top console", "₹17,000–33,000"],
      ["Pillars", "304 steel corner guards to 5 ft on both pillars", "₹3,000–5,000"]], note=NOTE_EN),
    sections=OD([
      ("Pros", ul(["Longest life of any tile: chips and scratches hardly show", "Porcelain slab wall is waterproof, fade-proof and wipes clean", "Stainless steel profiles and guards never rust", "Nothing to polish, seal or replace"])),
      ("Cons", ul(["About ₹35,000–60,000 more than Recommended", "Large slabs need a skilled mason and careful handling", "Hard to change the look later", "Fewer designs in full-body tiles"])),
      ("How long it lasts", ul(["Floor tiles: 25–30+ years", "Porcelain TV wall: 25+ years", "Steel trims: life of the flat", "Paint: 6–8 years"])),
      ("Verdict", "Pick this if you want to build once and not touch the hall for 20–25 years. It costs more up front but has the lowest cost over time."),
    ])),
  hi=OD(title="V1.3 · लंबे समय तक चलने वाला", tagline="फुल बॉडी टाइल का फ़र्श, स्टील पट्टी वाली पोर्सलेन स्लैब TV दीवार और स्टील गार्ड। एक बार बनवाएँ, 25 साल छोड़ दें।",
    why="उस परिवार के लिए जो काम एक ही बार कराना चाहता है। हर चीज़ अपनी तरह की सबसे मज़बूत: टाइल में पूरा रंग, ऐसी दीवार जो न फीकी पड़े न फूले, और स्टील जिसमें जंग नहीं। " + DOOR_HI,
    budget=OD(total="₹2,30,000–3,85,000", rows=[
      ["फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई में फुल बॉडी मैट 600×1200; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,68,000–2,81,000"],
      ["स्कर्टिंग", "पूरे घर में 4 इंच फुल बॉडी टाइल स्कर्टिंग", "₹20,000–30,000"],
      ["हॉल पेंट", "पुट्टी और प्राइमर पर प्रीमियम धुलने वाला इमल्शन, लगभग 900 वर्ग फुट", "₹22,000–36,000"],
      ["TV दीवार", "पोर्सलेन स्लैब 800×1600 (लगभग 70 वर्ग फुट), 304 ब्रश्ड स्टील पट्टी, ग्रेनाइट टॉप वाली कंसोल", "₹17,000–33,000"],
      ["खंभे", "दोनों खंभों पर 5 फीट तक 304 स्टील कॉर्नर गार्ड", "₹3,000–5,000"]], note=NOTE_HI),
    sections=OD([
      ("फ़ायदे", ul(["सबसे लंबी उम्र वाली टाइल: चटके और खरोंच मुश्किल से दिखते", "पोर्सलेन स्लैब दीवार वॉटरप्रूफ़, फीकी नहीं पड़ती, पोंछकर साफ़", "स्टेनलेस स्टील की पट्टी और गार्ड में कभी जंग नहीं", "न पॉलिश, न सीलिंग, न बदलना"])),
      ("कमियाँ", ul(["सुझाए गए प्लान से लगभग ₹35,000–60,000 ज़्यादा", "बड़ी स्लैब के लिए माहिर मिस्त्री और सावधानी चाहिए", "बाद में लुक बदलना मुश्किल", "फुल बॉडी में डिज़ाइन कम"])),
      ("कितना चलेगा", ul(["फ़र्श टाइल: 25–30+ साल", "पोर्सलेन TV दीवार: 25+ साल", "स्टील पट्टी: घर की पूरी उम्र", "पेंट: 6–8 साल"])),
      ("फ़ैसला", "अगर हॉल का काम एक बार कराकर 20–25 साल न छूना हो तो यही लें। शुरू में महँगा, पर लंबे समय में सबसे सस्ता पड़ता है।"),
    ]))),
 "HALL_MARBLE": dict(
  en=OD(title="V1.3 · Marble classic", tagline="Indian white marble in the hall and passage with a green border, a limewash TV wall with teak shelves. Room 1 shows Option C (Indian Modern).",
    why="The traditional look many Bihar homes love: seamless polished marble, cool in summer, that can be re-polished to look new. The rest of the flat stays on matt GVT to keep cost and upkeep down. " + DOOR_EN,
    budget=OD(total="₹2,47,000–4,58,000", rows=[
      ["Floors", "Indian white marble (Rajnagar / Makrana) in hall and passage, ground and polished; matt GVT in Room 2 and kitchen; anti-skid in the bathrooms; Kota in the open square (installed)", "₹1,83,000–3,49,000"],
      ["Border", "6 inch green marble border inlay round the hall", "₹9,000–15,000"],
      ["Skirting", "4 inch marble / tile skirting, whole flat", "₹20,000–30,000"],
      ["Hall paint", "Premium washable emulsion over putty and primer, about 900 sq ft", "₹22,000–36,000"],
      ["TV wall", "Limewash feature wall 8 ft wide in warm clay, four solid teak floating shelves", "₹11,000–24,000"],
      ["Pillars", "304 steel corner guards on both pillars", "₹2,000–4,000"]], note=NOTE_EN),
    sections=OD([
      ("Pros", ul(["Classic, seamless look with no grout grid", "Can be ground and re-polished to look new again", "Cool underfoot in Bihar's summer", "Limewash and teak feel warm and natural"])),
      ("Cons", ul(["Stains from haldi and oil, etches from lemon and curd", "Icy in winter; needs rugs", "Re-polish every 8–12 years; hard water dulls it", "Most expensive here and slowest to lay"])),
      ("How long it lasts", ul(["Marble: 50+ years, with a re-polish every 8–12 years", "Limewash: recoat every 5–8 years", "Teak shelves: decades with occasional polish"])),
      ("Verdict", "Pick this only if the family really wants marble and is ready for the upkeep. For the same look with far less work, use glossy marble-look tiles in the hall instead."),
    ])),
  hi=OD(title="V1.3 · मार्बल क्लासिक", tagline="हॉल और पैसेज में हरे बॉर्डर वाला देसी सफ़ेद मार्बल, सागौन शेल्फ़ वाली लाइमवॉश TV दीवार। कमरा 1 में ऑप्शन C (भारतीय मॉडर्न)।",
    why="बिहार के बहुत से घरों का पसंदीदा पारंपरिक लुक: बिना जोड़ वाला चमकदार मार्बल, गर्मी में ठंडा, और घिसाई से फिर नया जैसा। ख़र्च और देखभाल कम रखने के लिए बाक़ी घर में मैट GVT। " + DOOR_HI,
    budget=OD(total="₹2,47,000–4,58,000", rows=[
      ["फ़र्श", "हॉल और पैसेज में देसी सफ़ेद मार्बल (राजनगर / मकराना), घिसाई-पॉलिश समेत; कमरा 2 और रसोई में मैट GVT; बाथरूम में एंटी-स्किड; आँगन में कोटा (बिछाई समेत)", "₹1,83,000–3,49,000"],
      ["बॉर्डर", "हॉल के चारों ओर 6 इंच हरे मार्बल का बॉर्डर", "₹9,000–15,000"],
      ["स्कर्टिंग", "पूरे घर में 4 इंच मार्बल / टाइल स्कर्टिंग", "₹20,000–30,000"],
      ["हॉल पेंट", "पुट्टी और प्राइमर पर प्रीमियम धुलने वाला इमल्शन, लगभग 900 वर्ग फुट", "₹22,000–36,000"],
      ["TV दीवार", "8 फीट चौड़ी गर्म मिट्टी रंग की लाइमवॉश दीवार, सागौन की चार लटकती शेल्फ़", "₹11,000–24,000"],
      ["खंभे", "दोनों खंभों पर 304 स्टील कॉर्नर गार्ड", "₹2,000–4,000"]], note=NOTE_HI),
    sections=OD([
      ("फ़ायदे", ul(["पुराना शानदार लुक, टाइल जैसे जोड़ नहीं", "घिसाई-पॉलिश से फिर नया जैसा", "बिहार की गर्मी में पैर को ठंडा", "लाइमवॉश और सागौन से गर्म, प्राकृतिक एहसास"])),
      ("कमियाँ", ul(["हल्दी, तेल से दाग; नींबू, दही से धब्बे", "जाड़े में बर्फ़ जैसा ठंडा; दरी चाहिए", "हर 8–12 साल में घिसाई; खारा पानी चमक मार देता है", "यहाँ सबसे महँगा और बिछाई में सबसे ज़्यादा समय"])),
      ("कितना चलेगा", ul(["मार्बल: 50+ साल, हर 8–12 साल में घिसाई", "लाइमवॉश: हर 5–8 साल में नया कोट", "सागौन शेल्फ़: कभी-कभी पॉलिश के साथ दशकों"])),
      ("फ़ैसला", "तभी लें जब परिवार सच में मार्बल चाहता हो और देखभाल के लिए तैयार हो। वैसा ही लुक बहुत कम झंझट में चाहिए तो हॉल में चमकदार मार्बल-लुक टाइल लें।"),
    ]))),
}
for f, lang in (("MyFlat_Viewer/models/room1_designs.json", "en"), ("MyFlat_Viewer/models/room1_designs_hi.json", "hi")):
    d = json.load(open(f, encoding="utf-8"), object_pairs_hook=OD)
    for k, v in OPT.items(): d[k] = v[lang]
    json.dump(d, open(f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------------- config: hall viewpoints for the new layout (three.js metres: x, height, -y)
C = "MyFlat_Viewer/src/config.js"
s = open(C, encoding="utf-8").read()
new_vp = ("    'Hall': [\n"
          "      { name: 'TV wall (from the sofa)', pos: [4.05, 1.5, 6.32], target: [1.19, 1.25, 6.32] },\n"
          "      { name: 'Main door (just inside)', pos: [1.7, 1.6, 9.22], target: [6.4, 1.3, 7.6] },\n"
          "      { name: 'Whole hall (from the south-east corner)', pos: [5.79, 1.65, 13.41], target: [2.44, 0.9, 6.1] },\n"
          "    ],\n")
s2 = re.sub(r"    'Hall': \[\n.*?    \],\n", new_vp, s, count=1, flags=re.S)
if s2 == s and new_vp not in s: raise SystemExit("Hall viewpoints block not found")
open(C, "w", encoding="utf-8").write(s2)

for f in ("MyFlat_Viewer/index.html", "MyFlat_Viewer/src/main.js"):
    t = open(f, encoding="utf-8").read().replace("?v=17", "?v=18").replace("BUILD = '17'", "BUILD = '18'")
    open(f, "w", encoding="utf-8").write(t)
print("viewer updated (v1.3b)")
