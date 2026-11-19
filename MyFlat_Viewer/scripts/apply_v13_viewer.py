# Applies the V1.3 hall-design changes to MyFlat_Viewer (run from the MyFlat folder). Safe to re-run.
import json, collections, re, sys, os
OD = collections.OrderedDict
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")

def rep(path, a, b, optional=False):
    s = open(path, encoding="utf-8").read()
    if b in s: return
    if s.count(a) != 1:
        if optional: return
        raise SystemExit(f"{path}: expected one '{a[:60]}', found {s.count(a)}")
    open(path, "w", encoding="utf-8").write(s.replace(a, b))

# 1. exporter: DESIGNS = several design options in one GLB (Room 1 design + hall design)
E = "MyFlat_Viewer/scripts/export_glb.py"
rep(E, 'DESIGN = globals().get("DESIGN")        # None -> architecture (+ nothing tagged as design)',
       'DESIGN = globals().get("DESIGN")        # None -> architecture (+ nothing tagged as design)\n'
       'DESIGNS = list(globals().get("DESIGNS") or ([DESIGN] if DESIGN else []))   # several options in one GLB, e.g. ["DEFAULT", "HALL_REC"]')
rep(E, 'if DESIGN and c.get("design_option") == DESIGN and c.get("replaces"):', 'if c.get("design_option") in DESIGNS and c.get("replaces"):')
rep(E, 'if opt and opt != DESIGN: continue', 'if opt and opt not in DESIGNS: continue')
rep(E, '"design_option": DESIGN,', '"design_option": "+".join(DESIGNS) or None,')

# 2. models.json
P = "MyFlat_Viewer/models/models.json"
d = json.load(open(P, encoding="utf-8"), object_pairs_hook=OD)
d["models"] = [m for m in d["models"] if not m["file"].startswith("MyFlat_V1_3_")]
at = next((i for i, m in enumerate(d["models"]) if m["file"] == "MyFlat_V1_2_Room2_Ensuite.glb"), len(d["models"]) - 1) + 1
d["models"][at:at] = [
    OD([("file", "MyFlat_V1_3_Hall_Recommended.glb"), ("label", "V1.3 · Recommended: matt tiles + WPC TV wall"), ("short", "V1.3 Recommended"),
        ("group", "version"), ("design", "HALL_REC"), ("startView", "Hall:0"), ("manifest", "MyFlat_V1_3_Hall_Recommended.manifest.json")]),
    OD([("file", "MyFlat_V1_3_Hall_Budget.glb"), ("label", "V1.3 · Budget plain: double-charge tiles + plain paint"), ("short", "V1.3 Budget plain"),
        ("group", "version"), ("design", "HALL_BUDGET"), ("startView", "Hall:0"), ("manifest", "MyFlat_V1_3_Hall_Budget.manifest.json")]),
]
json.dump(d, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# 3. design notes (English + Hindi)
REC_EN = OD(title="V1.3 · Recommended floors + hall",
  tagline="Matt GVT tiles through the flat, a WPC fluted TV wall with a metal frame, anti-skid baths and Kota stone outside.",
  why="This is the plan from the floor and wall guide. One light greige matt tile (2 × 4 ft) runs through the hall, passage, Room 2 and kitchen, so the flat reads as one space and hides Bihar's dust. The hall's west wall has no doors or windows, so it takes the TV: a 10 ft WPC fluted panel centred under the beam, framed in black aluminium, with a warm LED strip. The pillars get steel corner guards. Room 1 shows the DEFAULT design.",
  budget=OD(total="₹1,99,000–3,35,000", rows=[
    ["Floors", "Matt GVT 600×1200 in hall, passage, Room 2 and kitchen; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,35,000–2,27,000"],
    ["Skirting", "4 inch tile skirting, whole flat", "₹20,000–30,000"],
    ["Hall paint", "Premium washable emulsion over putty and primer, about 900 sq ft", "₹22,000–36,000"],
    ["TV wall", "WPC fluted panel about 100 sq ft, black aluminium frame, LED strip", "₹20,000–38,000"],
    ["Pillars", "304 steel corner guards on both pillars", "₹2,000–4,000"]],
    note="Furniture, lights and the fan are drawn for the layout and are not in this total. Rough 2026 estimates, not quotes."),
  sections=OD([
    ("Floors", "Hall, passage, Room 2 and kitchen: matt GVT 600 × 1200, light warm greige, rectified, 2 mm joints. Bathroom 1 and 2: anti-skid R11 600 × 600 with epoxy grout. Open square: Kota stone. 4 inch skirting from the same tile."),
    ("TV wall", "West wall of the hall, 10 ft wide and 8'5\" high, stopping under the 9 ft beam. Teak-tone WPC fluted panel, black anodised aluminium frame, warm LED strip behind the top profile. TV at 4 ft centre height on a floating walnut console; wires run inside the panel."),
    ("Layout", "3-seater sofa facing the TV about 9 ft away, coffee table and an 8 × 8 ft rug. 6-seater dining table near Room 1 and the hall gate. Areca palm in the south-west corner."),
    ("Walls and pillars", "Premium washable emulsion in a light warm off-white, low sheen. 304 stainless steel corner guards to 4 ft on both pillars."),
    ("Lights", "Eight 12 W LED downlights at 3000K, the LED strip on the TV wall and a BLDC ceiling fan."),
  ]))
BUD_EN = OD(title="V1.3 · Budget plain",
  tagline="Double-charge tiles, plain washable paint, a TV on the wall and nothing extra. Room 1 shows Option D (Smart Budget).",
  why="This spends money only where it lasts: tough double-charge tiles that hide chips, anti-skid floors in the bathrooms and Kota outside. The walls are plain painted, the TV hangs on a bracket above a ready-made unit, and LED battens light the hall. You can add the WPC TV wall later without touching the floor.",
  budget=OD(total="₹1,58,000–2,47,000", rows=[
    ["Floors", "Double-charge vitrified 600×600 in hall, passage, Room 2 and kitchen; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,24,000–1,94,000"],
    ["Skirting", "4 inch tile skirting, whole flat", "₹20,000–30,000"],
    ["Hall paint", "Economy washable emulsion (for example Asian Paints Tractor Emulsion or Berger Bison Glow), about 900 sq ft", "₹11,000–18,000"],
    ["TV", "Wall bracket, PVC wire casing, laminated shelf", "₹3,000–5,000"]],
    note="Furniture, lights and the fan are drawn for the layout and are not in this total. Rough 2026 estimates, not quotes."),
  sections=OD([
    ("Floors", "Hall, passage, Room 2 and kitchen: double-charge vitrified 600 × 600 in a beige speckle that hides dust and small chips. Bathrooms: anti-skid R11. Open square: Kota stone. 4 inch skirting from the same tile."),
    ("Walls", "Plain economy washable emulsion in light cream. No panels. If a wall is damp, fix the source and use a damp-proof primer first."),
    ("TV", "TV on a wall bracket with the wires in a PVC casing, a laminated shelf and a ready-made TV unit below."),
    ("Layout", "6 ft ready-made sofa, small centre table, 4-seater dining table."),
    ("Lights", "Three 20 W LED battens and a BLDC ceiling fan."),
    ("Upgrade later", "Add the WPC TV wall (about ₹20,000–38,000) and steel corner guards whenever the budget allows. Nothing in this plan needs breaking."),
  ]))
REC_HI = OD(title="V1.3 · सुझाया गया फ़र्श + हॉल",
  tagline="पूरे घर में मैट GVT टाइल, धातु की पट्टी वाली WPC फ्लूटेड TV दीवार, बाथरूम में एंटी-स्किड और बाहर कोटा पत्थर।",
  why="यह फ़र्श और दीवार गाइड वाला प्लान है। हॉल, पैसेज, कमरा 2 और रसोई में एक ही हल्की ग्रे-बेज मैट टाइल (2 × 4 फीट), ताकि घर एक जैसा और बड़ा लगे और धूल न दिखे। हॉल की पश्चिमी दीवार में न दरवाज़ा है न खिड़की, इसलिए TV वहीं: बीम के ठीक नीचे 10 फीट का WPC फ्लूटेड पैनल, काली एल्युमिनियम पट्टी और गर्म LED पट्टी के साथ। खंभों पर स्टील कॉर्नर गार्ड। कमरा 1 में DEFAULT डिज़ाइन है।",
  budget=OD(total="₹1,99,000–3,35,000", rows=[
    ["फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई में मैट GVT 600×1200; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,35,000–2,27,000"],
    ["स्कर्टिंग", "पूरे घर में 4 इंच टाइल स्कर्टिंग", "₹20,000–30,000"],
    ["हॉल पेंट", "पुट्टी और प्राइमर पर प्रीमियम धुलने वाला इमल्शन, लगभग 900 वर्ग फुट", "₹22,000–36,000"],
    ["TV दीवार", "WPC फ्लूटेड पैनल लगभग 100 वर्ग फुट, काली एल्युमिनियम पट्टी, LED पट्टी", "₹20,000–38,000"],
    ["खंभे", "दोनों खंभों पर 304 स्टील कॉर्नर गार्ड", "₹2,000–4,000"]],
    note="फ़र्नीचर, लाइट और पंखा सिर्फ़ लेआउट दिखाने के लिए हैं, इस कुल में नहीं। 2026 के मोटे अंदाज़े, पक्का रेट नहीं।"),
  sections=OD([
    ("फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई: मैट GVT 600 × 1200, हल्का ग्रे-बेज, रेक्टिफाइड, 2 mm जोड़। बाथरूम 1 और 2: एंटी-स्किड R11 600 × 600, इपॉक्सी ग्राउट। खुला आँगन: कोटा पत्थर। उसी टाइल से 4 इंच स्कर्टिंग।"),
    ("TV दीवार", "हॉल की पश्चिमी दीवार, 10 फीट चौड़ी और 8'5\" ऊँची, 9 फीट वाले बीम के नीचे तक। सागौन रंग का WPC फ्लूटेड पैनल, काली एनोडाइज़्ड एल्युमिनियम पट्टी, ऊपर की पट्टी के पीछे गर्म LED। TV का बीच 4 फीट ऊँचाई पर, नीचे अखरोट रंग की लटकती कंसोल; तार पैनल के अंदर।"),
    ("लेआउट", "TV से लगभग 9 फीट दूर 3 सीट वाला सोफ़ा, सेंटर टेबल और 8 × 8 फीट की दरी। कमरा 1 और हॉल गेट के पास 6 सीट वाली डाइनिंग टेबल। दक्षिण-पश्चिम कोने में अरेका पाम।"),
    ("दीवार और खंभे", "हल्का गर्म ऑफ़-व्हाइट प्रीमियम धुलने वाला इमल्शन, कम चमक। दोनों खंभों पर 4 फीट तक 304 स्टील कॉर्नर गार्ड।"),
    ("लाइट", "आठ 12 W LED डाउनलाइट (3000K), TV दीवार की LED पट्टी और BLDC पंखा।"),
  ]))
BUD_HI = OD(title="V1.3 · सादा बजट प्लान",
  tagline="डबल चार्ज टाइल, सादा धुलने वाला पेंट, दीवार पर TV, और कुछ फ़ालतू नहीं। कमरा 1 में ऑप्शन D (स्मार्ट बजट)।",
  why="पैसा वहीं लगता है जहाँ टिकाऊ हो: मज़बूत डबल चार्ज टाइल जिस पर चटके नहीं दिखते, बाथरूम में एंटी-स्किड और बाहर कोटा। दीवारें सादे पेंट की, TV ब्रैकेट पर रेडीमेड यूनिट के ऊपर, और हॉल में LED बैटन। WPC TV दीवार बाद में भी लग सकती है, फ़र्श छेड़े बिना।",
  budget=OD(total="₹1,58,000–2,47,000", rows=[
    ["फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई में डबल चार्ज 600×600; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,24,000–1,94,000"],
    ["स्कर्टिंग", "पूरे घर में 4 इंच टाइल स्कर्टिंग", "₹20,000–30,000"],
    ["हॉल पेंट", "किफ़ायती धुलने वाला इमल्शन (जैसे एशियन पेंट्स ट्रैक्टर इमल्शन या बर्जर बाइसन ग्लो), लगभग 900 वर्ग फुट", "₹11,000–18,000"],
    ["TV", "दीवार ब्रैकेट, तार के लिए PVC केसिंग, लैमिनेट शेल्फ़", "₹3,000–5,000"]],
    note="फ़र्नीचर, लाइट और पंखा सिर्फ़ लेआउट दिखाने के लिए हैं, इस कुल में नहीं। 2026 के मोटे अंदाज़े, पक्का रेट नहीं।"),
  sections=OD([
    ("फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई: डबल चार्ज 600 × 600, बेज दानेदार, धूल और छोटे चटके छिपाती है। बाथरूम: एंटी-स्किड R11। खुला आँगन: कोटा पत्थर। उसी टाइल से 4 इंच स्कर्टिंग।"),
    ("दीवारें", "हल्के क्रीम रंग का किफ़ायती धुलने वाला इमल्शन। कोई पैनल नहीं। दीवार में सीलन हो तो पहले जड़ ठीक करें और डैम्प-प्रूफ़ प्राइमर लगाएँ।"),
    ("TV", "ब्रैकेट पर TV, तार PVC केसिंग में, लैमिनेट शेल्फ़ और नीचे रेडीमेड TV यूनिट।"),
    ("लेआउट", "6 फीट का रेडीमेड सोफ़ा, छोटी सेंटर टेबल, 4 सीट वाली डाइनिंग टेबल।"),
    ("लाइट", "तीन 20 W LED बैटन और BLDC पंखा।"),
    ("बाद में अपग्रेड", "बजट हो तब WPC TV दीवार (लगभग ₹20,000–38,000) और स्टील कॉर्नर गार्ड लगवा लें। इस प्लान में कुछ भी तोड़ना नहीं पड़ेगा।"),
  ]))
for f, rec, bud in (("MyFlat_Viewer/models/room1_designs.json", REC_EN, BUD_EN), ("MyFlat_Viewer/models/room1_designs_hi.json", REC_HI, BUD_HI)):
    d = json.load(open(f, encoding="utf-8"), object_pairs_hook=OD); d["HALL_REC"] = rec; d["HALL_BUDGET"] = bud
    json.dump(d, open(f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# 4. config: hall viewpoints + wall-finish category label
C = "MyFlat_Viewer/src/config.js"
rep(C, "    { key: 'sanitaryware',    label: 'Bathroom fittings' },\n",
       "    { key: 'sanitaryware',    label: 'Bathroom fittings' },\n    { key: 'wall_finish',     label: 'Wall panels & trims' },\n")
rep(C, "  viewpoints: {\n",
    "  viewpoints: {\n"
    "    'Hall': [\n"
    "      { name: 'TV wall (from the sofa)', pos: [4.42, 1.5, 9.22], target: [1.19, 1.25, 9.22] },\n"
    "      { name: 'Whole hall (from the south-east corner)', pos: [5.79, 1.65, 13.41], target: [2.44, 0.9, 6.1] },\n"
    "    ],\n")
I = "MyFlat_Viewer/src/i18n.js"
rep(I, "'Bathroom fittings': 'बाथरूम फ़िटिंग', ", "'Bathroom fittings': 'बाथरूम फ़िटिंग', 'Wall panels & trims': 'दीवार पैनल और पट्टी', ", optional=True)

# 5. cache-bust the viewer scripts
for f in ("MyFlat_Viewer/index.html", "MyFlat_Viewer/src/main.js"):
    s = open(f, encoding="utf-8").read()
    s = s.replace("?v=16", "?v=17").replace("BUILD = '16'", "BUILD = '17'")
    open(f, "w", encoding="utf-8").write(s)
print("viewer updated")
