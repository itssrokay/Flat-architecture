# V1.3c: fifth option, "Panelled hall" (HALL_PANEL). Run from the MyFlat folder. Safe to re-run.
import json, collections, sys, os
OD = collections.OrderedDict
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")
def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

P = "MyFlat_Viewer/models/models.json"
d = json.load(open(P, encoding="utf-8"), object_pairs_hook=OD)
d["models"] = [m for m in d["models"] if m["file"] != "MyFlat_V1_3_Hall_Panelled.glb"]
at = next(i for i, m in enumerate(d["models"]) if m["file"] == "MyFlat_V1_3_Hall_Marble.glb") + 1
d["models"].insert(at, OD([("file", "MyFlat_V1_3_Hall_Panelled.glb"), ("label", "V1.3 · Panelled hall: WPC feature wall, half-wall panels, wrapped pillars"),
    ("short", "V1.3 Panelled hall"), ("group", "version"), ("design", "HALL_PANEL"), ("startView", "Hall:0"), ("manifest", "MyFlat_V1_3_Hall_Panelled.manifest.json")]))
json.dump(d, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

EN = OD(title="V1.3 · Panelled hall",
  tagline="The whole TV wall in fluted WPC, 3 ft sage half-wall panelling with a champagne aluminium cap round the hall, and both pillars wrapped full height.",
  why="For a warm, finished, hotel-lobby look. The panels protect the lower walls from mops, chairs and scuffs, so only the top half ever needs paint. Floors are the same matt GVT as the Recommended plan. The main door (3 ft, middle of the west wall) opens between the TV wall and the entry shoe cabinet.",
  budget=OD(total="₹2,44,000–4,22,000", rows=[
    ["Floors", "Matt GVT 600×1200 in hall, passage, Room 2 and kitchen; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,35,000–2,27,000"],
    ["Skirting", "4 inch tile skirting outside the hall", "₹20,000–30,000"],
    ["Paint", "Premium washable emulsion above the panels", "₹18,000–30,000"],
    ["Feature wall", "Fluted WPC on the whole wall north of the door (about 110 sq ft), black profile, LED strip", "₹25,000–45,000"],
    ["Half-wall panels", "3 ft WPC / HDHMR panels with moulding strips, about 160 sq ft, champagne aluminium cap", "₹33,000–67,000"],
    ["Pillars", "Both pillars wrapped full height in fluted WPC (about 72 sq ft)", "₹13,000–23,000"]],
    note="Furniture, lights and the fan are drawn for the layout and are not in this total. Rough 2026 estimates, not quotes. Panel prices vary a lot between makes: get the panel brand and thickness written on the quote."),
  sections=OD([
    ("Pros", ul(["Warm, premium look with no extra furniture", "Half-wall panels take the knocks from mops, chairs and shoes; the lower wall never needs repainting", "WPC is waterproof and termite-proof, and hides uneven plaster and wiring", "Wrapped pillars stop chipped corners and look intentional"])),
    ("Cons", ul(["The most panel work, so one of the costliest plans", "Panels hide the wall: fix any damp first, or it will spread behind them", "Dust settles in the flutes; dust them weekly", "A lot of wood tone can feel heavy; keep the rest of the walls light"])),
    ("How long it lasts", ul(["WPC feature wall and pillar wraps: 12–15 years", "Half-wall panels: 10–15 years", "Floor tiles: 15–25 years", "Paint above the panels: 6–8 years"])),
    ("Verdict", "Pick this if you love panelling and the walls are dry. For a lighter budget, keep only the fluted TV wall (the Recommended plan) and add half-wall panels later."),
  ]))
HI = OD(title="V1.3 · पैनल वाला हॉल",
  tagline="पूरी TV दीवार पर फ्लूटेड WPC, हॉल में 3 फीट की सेज-हरी आधी दीवार पैनलिंग शैम्पेन एल्युमिनियम पट्टी के साथ, और दोनों खंभे पूरी ऊँचाई तक ढके।",
  why="गर्म, सजे हुए, होटल-लॉबी जैसे लुक के लिए। पैनल निचली दीवार को पोंछे, कुर्सी और रगड़ से बचाते हैं, इसलिए पेंट सिर्फ़ ऊपर के हिस्से पर करना पड़ता है। फ़र्श सुझाए गए प्लान वाली मैट GVT। मुख्य दरवाज़ा (3 फीट, पश्चिमी दीवार के बीच में) TV दीवार और जूते की अलमारी के बीच खुलता है।",
  budget=OD(total="₹2,44,000–4,22,000", rows=[
    ["फ़र्श", "हॉल, पैसेज, कमरा 2 और रसोई में मैट GVT 600×1200; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,35,000–2,27,000"],
    ["स्कर्टिंग", "हॉल के बाहर 4 इंच टाइल स्कर्टिंग", "₹20,000–30,000"],
    ["पेंट", "पैनल के ऊपर प्रीमियम धुलने वाला इमल्शन", "₹18,000–30,000"],
    ["फ़ीचर दीवार", "दरवाज़े के उत्तर वाली पूरी दीवार पर फ्लूटेड WPC (लगभग 110 वर्ग फुट), काली पट्टी, LED", "₹25,000–45,000"],
    ["आधी दीवार पैनल", "3 फीट के WPC / HDHMR पैनल, मोल्डिंग पट्टियाँ, लगभग 160 वर्ग फुट, शैम्पेन एल्युमिनियम कैप", "₹33,000–67,000"],
    ["खंभे", "दोनों खंभे पूरी ऊँचाई तक फ्लूटेड WPC से ढके (लगभग 72 वर्ग फुट)", "₹13,000–23,000"]],
    note="फ़र्नीचर, लाइट और पंखा सिर्फ़ लेआउट के लिए हैं, इस कुल में नहीं। 2026 के मोटे अंदाज़े, पक्का रेट नहीं। पैनल के दाम कंपनी-कंपनी बहुत बदलते हैं: कोटेशन पर पैनल की कंपनी और मोटाई लिखवाएँ।"),
  sections=OD([
    ("फ़ायदे", ul(["बिना ज़्यादा फ़र्नीचर के गर्म, शानदार लुक", "आधी दीवार के पैनल पोंछे, कुर्सी और जूतों की रगड़ झेलते हैं; निचली दीवार पर कभी पेंट नहीं", "WPC वॉटरप्रूफ़, दीमक नहीं लगती, टेढ़ा प्लास्टर और तार छिपाता है", "ढके खंभों के कोने नहीं टूटते और सुंदर लगते हैं"])),
    ("कमियाँ", ul(["सबसे ज़्यादा पैनल का काम, इसलिए महँगे प्लान में से एक", "पैनल दीवार ढक देते हैं: सीलन हो तो पहले ठीक करें, वरना पीछे फैलेगी", "धारियों में धूल जमती है; हफ़्ते में एक बार झाड़ें", "बहुत ज़्यादा लकड़ी का रंग भारी लग सकता है; बाक़ी दीवारें हल्की रखें"])),
    ("कितना चलेगा", ul(["WPC फ़ीचर दीवार और खंभे: 12–15 साल", "आधी दीवार पैनल: 10–15 साल", "फ़र्श टाइल: 15–25 साल", "पैनल के ऊपर पेंट: 6–8 साल"])),
    ("फ़ैसला", "पैनलिंग बहुत पसंद हो और दीवारें सूखी हों तो यही लें। कम बजट में सिर्फ़ फ्लूटेड TV दीवार रखें (सुझाया गया प्लान) और आधी दीवार पैनल बाद में लगवाएँ।"),
  ]))
for f, v in (("MyFlat_Viewer/models/room1_designs.json", EN), ("MyFlat_Viewer/models/room1_designs_hi.json", HI)):
    d = json.load(open(f, encoding="utf-8"), object_pairs_hook=OD); d["HALL_PANEL"] = v
    json.dump(d, open(f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for f in ("MyFlat_Viewer/index.html", "MyFlat_Viewer/src/main.js"):
    t = open(f, encoding="utf-8").read().replace("?v=18", "?v=19").replace("BUILD = '18'", "BUILD = '19'")
    open(f, "w", encoding="utf-8").write(t)
print("viewer updated (v1.3c)")
