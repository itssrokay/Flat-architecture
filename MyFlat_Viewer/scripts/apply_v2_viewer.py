"""V2 (site-measured layout, 14 Nov 2026): model list, per-model viewpoints and design-note wording for the V2 exports.
Run from MyFlat_Viewer:  python3 scripts/apply_v2_viewer.py   (safe to re-run)"""
import json, re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ft = 0.3048
def P(x, y, h): return [round(x * ft, 3), h, round(-y * ft, 3)]
VP = {
  'Hall': [
    {'name': 'TV wall (from the sofa)', 'pos': P(14.2, -30.1, 1.5), 'target': P(6.6, -30.1, 1.25)},
    {'name': 'Main door (just inside)', 'pos': P(8.3, -22.84, 1.6), 'target': P(17.0, -31.0, 1.2)},
    {'name': 'Whole hall (from the south-east corner)', 'pos': P(22.0, -44.0, 1.65), 'target': P(10.0, -24.0, 0.9)},
    {'name': 'Dining & window', 'pos': P(16.8, -35.5, 1.6), 'target': P(11.5, -42.0, 0.9)},
    {'name': 'Towards the arch', 'pos': P(12.0, -27.0, 1.6), 'target': P(15.8, -13.0, 1.4)},
  ],
  'Room 2': [
    {'name': 'Bedroom towards the bathroom door', 'pos': P(29.4, -22.6, 1.6), 'target': P(31.0, -6.7, 1.2)},
  ],
  'Room 2 Bath': [
    {'name': 'Tub (from the door)', 'pos': P(29.3, -5.5, 1.6), 'target': P(39.5, -1.2, 0.8)},
    {'name': 'Vanity & door (from the tub)', 'pos': P(37.5, -3.6, 1.6), 'target': P(30.0, -6.0, 1.0)},
  ],
}
HALLS = [("BestOfBoth", "HALL_BEST", "★ Best of both", "Best of both: 2×4 / 2×2 matt GVT, flat laminate TV wall, gypsum border"),
         ("Recommended", "HALL_REC", "Recommended", "Recommended: matt tiles + WPC TV wall"),
         ("Budget", "HALL_BUDGET", "Budget plain", "Budget plain: double-charge tiles + plain paint"),
         ("LongLasting", "HALL_LONG", "Long-lasting", "Long-lasting: full-body tiles + porcelain slab TV wall"),
         ("Marble", "HALL_MARBLE", "Marble classic", "Marble classic: marble hall + limewash TV wall"),
         ("Panelled", "HALL_PANEL", "Panelled hall", "Panelled hall: WPC feature wall, half-wall panels, wrapped pillars")]
R1 = [("DEFAULT", "DEFAULT", "DEFAULT (Warm Contemporary)"), ("OPTION_A", "A", "Option A (Japandi Calm)"), ("OPTION_B", "B", "Option B (Minimal Modern)"),
      ("OPTION_C", "C", "Option C (Indian Modern Heritage)"), ("OPTION_D", "D", "Option D (Smart Budget)"), ("OPTION_E", "E", "Option E (Simple & Practical)")]
old = json.load(open("models/models.json"))
oldlab = {m["file"]: m for m in old["models"]}
models = []
for key, design, short, label in HALLS:
    f = f"MyFlat_V2_Hall_{key}.glb"
    models.append({"file": f, "label": "V2 · " + label, "short": short, "group": "version", "design": design, "startView": "Hall:0",
                   "manifest": f.replace(".glb", ".manifest.json"), "viewpoints": VP})
models.append({"file": "MyFlat_V2_Room2_Ensuite.glb", "label": "V2 · Room 2 en-suite bath with tub (behind the cross wall)", "short": "Room 2 bath",
               "group": "version", "design": "ROOM2_ENSUITE", "startView": "Room 2 Bath:0", "manifest": "MyFlat_V2_Room2_Ensuite.manifest.json", "viewpoints": VP})
for opt, short, label in R1:
    f = f"MyFlat_V2_Room1_{opt}.glb"
    lab = (oldlab.get(f"MyFlat_V1_1_Room1_{opt}.glb") or {}).get("label") or ("Room 1 · " + label)
    models.append({"file": f, "label": lab, "short": short, "group": "interior", "design": opt, "startView": "Room 1:0",
                   "manifest": f.replace(".glb", ".manifest.json"), "viewpoints": VP})
models.append({"file": "MyFlat_V2_Architecture.glb", "label": "V2 · Bare structure (site-measured, 13 Nov)", "short": "V2 bare structure", "group": "architecture",
               "startView": "Hall:1", "manifest": "MyFlat_V2_Architecture.manifest.json", "viewpoints": VP})
json.dump({"default": "MyFlat_V2_Hall_BestOfBoth.glb", "designNotes": old.get("designNotes", "room1_designs.json"), "models": models},
          open("models/models.json", "w"), indent=1, ensure_ascii=False)

def patch(fn, pairs, edit):
    d = json.load(open(fn)); s = json.dumps(d, ensure_ascii=False); miss = []
    for a, b in pairs:
        a_, b_ = json.dumps(a, ensure_ascii=False)[1:-1], json.dumps(b, ensure_ascii=False)[1:-1]
        if a_ in s: s = s.replace(a_, b_)
        elif b_ not in s: miss.append(a[:50])
    d = json.loads(s); edit(d); json.dump(d, open(fn, "w"), indent=1, ensure_ascii=False); return miss

EN = [
 ("The main door (3 ft, middle of the hall's west wall) opens into an entry with a shoe cabinet. The TV wall sits north of the door, centred under the beam; the dining table sits south, near window W7.",
  "The main door (108 cm, on the hall's west wall, just south of Pillar 2's line) opens into an entry with a shoe cabinet on its north side. The TV wall sits south of the door, between the door and the wall column; the dining table sits further south, near window W7."),
 ("The main door (3 ft, middle of the west wall) opens between the TV wall and the entry shoe cabinet.", "The main door (108 cm, west wall) opens between the entry shoe cabinet on its north side and the TV wall on its south side."),
 ("Fluted WPC on the whole wall north of the door (about 110 sq ft)", "Fluted WPC on the wall between the main door and the wall column (about 90 sq ft)"),
 ("A wall across the north end of Room 2 turns Bath 2 and a new tub room into one bathroom, with a single door into Room 2.",
  "The cross wall already built at the north end of Room 2 turns Bath 2 and the tub side into one bathroom, with a single door from the bedroom."),
 ("A 5\" wall 4'11\" from the north wall makes a tub room right next to Bath 2. The old Bath 2 doorway stays open, so the WC and the tub room work as one bathroom. The only way in or out is the new 2'6\" door. The wall can't go further south: the east window W5 starts 5'5\" from the north wall.",
  "The cross wall built on site, 6'3\" (191 cm) from the north wall, makes a tub room right next to Bath 2. Bath 2's side facing it is open (130 cm), so the WC and the tub room work as one bathroom. The only way in or out is a 2'6\" door in the doorway at the wall's west end. A short brick infill closes the last 10 inches of Bath 2's open side, which would otherwise show into the bedroom."),
 ("Tub room 12'7\" (north) narrowing to 12'2\" × 4'11\" clear.", "Tub room 12'7\" (north) narrowing to 12'0\" × 6'3\" clear."),
 ("Vanity with a mirror on the new wall, beside the door.", "Vanity with a mirror on the cross wall, beside the door."),
 ("reached through its old doorway, which now has no door leaf.", "reached through its open side beside the column."),
 ("The new door is in the new wall, 9\" from Room 2's west wall.", "The door is in the doorway at the west end of the cross wall."),
 ("Room 2 becomes 18'3\" long, 12'1\" wide at the new wall narrowing to 10'6\".", "The bedroom is about 17' long, 12'0\" wide at the cross wall narrowing to 10'6\"."),
 ("It loses the north window W4 to the bathroom.", "The north window W4 (127 × 94 cm) belongs to the bathroom."),
]
HI = [
 ("मुख्य दरवाज़ा (3 फीट, हॉल की पश्चिमी दीवार के बीच में) खुलते ही जूते की अलमारी वाली जगह। TV दीवार दरवाज़े के उत्तर में, बीम के ठीक नीचे; डाइनिंग टेबल दक्षिण में, खिड़की W7 के पास।",
  "मुख्य दरवाज़ा (108 सेमी, हॉल की पश्चिमी दीवार पर, पिलर 2 की लाइन से ठीक दक्षिण में) खुलते ही उत्तर की तरफ़ जूते की अलमारी। TV दीवार दरवाज़े के दक्षिण में, दरवाज़े और दीवार के कॉलम के बीच; डाइनिंग टेबल और दक्षिण में, खिड़की W7 के पास।"),
 ("दरवाज़े के उत्तर वाली पूरी दीवार पर फ्लूटेड WPC (लगभग 110 वर्ग फुट)", "मुख्य दरवाज़े और दीवार के कॉलम के बीच की दीवार पर फ्लूटेड WPC (लगभग 90 वर्ग फुट)"),
 ("कमरा 2 के उत्तरी सिरे पर एक दीवार से Bath 2 और नया टब-रूम मिलकर एक बाथरूम बन जाते हैं, और कमरा 2 में बस एक दरवाज़ा खुलता है।",
  "कमरा 2 के उत्तरी सिरे पर पहले से बनी आड़ी दीवार से Bath 2 और टब वाला हिस्सा मिलकर एक बाथरूम बन जाते हैं, और बेडरूम से बस एक दरवाज़ा खुलता है।"),
 ("उत्तरी दीवार से 4'11\" पर 5\" की दीवार बनाने से Bath 2 के ठीक बगल में टब-रूम बन जाता है। Bath 2 का पुराना दरवाज़ा खुला रहता है, इसलिए WC और टब-रूम एक ही बाथरूम की तरह काम करते हैं। अंदर आने-जाने का रास्ता बस नया 2'6\" का दरवाज़ा है। दीवार इससे आगे दक्षिण में नहीं जा सकती: पूर्वी खिड़की W5 उत्तरी दीवार से 5'5\" पर शुरू होती है।",
  "साइट पर बनी आड़ी दीवार, उत्तरी दीवार से 6'3\" (191 सेमी) पर, Bath 2 के ठीक बगल में टब-रूम बनाती है। Bath 2 की उस तरफ़ वाली साइड खुली है (130 सेमी), इसलिए WC और टब-रूम एक ही बाथरूम की तरह काम करते हैं। अंदर आने-जाने का रास्ता बस दीवार के पश्चिमी सिरे के रास्ते में लगा 2'6\" का दरवाज़ा है। Bath 2 की खुली साइड के आख़िरी 10 इंच ईंट से बंद किए गए हैं, वरना वह बेडरूम में दिखती।"),
 ("टब-रूम उत्तर में 12'7\" से घटकर 12'2\" × 4'11\" खुली जगह।", "टब-रूम उत्तर में 12'7\" से घटकर 12'0\" × 6'3\" खुली जगह।"),
 ("आईने वाली वैनिटी नई दीवार पर, दरवाज़े के बगल में।", "आईने वाली वैनिटी आड़ी दीवार पर, दरवाज़े के बगल में।"),
 ("वहाँ उसके पुराने दरवाज़े से जाते हैं, जिसमें अब पल्ला नहीं है।", "वहाँ कॉलम के बगल वाली उसकी खुली साइड से जाते हैं।"),
 ("नया दरवाज़ा नई दीवार में है, कमरा 2 की पश्चिमी दीवार से 9\" पर।", "दरवाज़ा आड़ी दीवार के पश्चिमी सिरे वाले रास्ते में है।"),
 ("कमरा 2 अब 18'3\" लंबा है; नई दीवार के पास 12'1\" चौड़ा, आगे घटकर 10'6\"।", "बेडरूम लगभग 17' लंबा है; आड़ी दीवार के पास 12'0\" चौड़ा, आगे घटकर 10'6\"।"),
 ("उत्तरी खिड़की W4 बाथरूम में चली जाती है।", "उत्तरी खिड़की W4 (127 × 94 सेमी) बाथरूम की है।"),
]
def ed_en(d):
    n = d.get("ROOM2_ENSUITE") or {}; n["title"] = "V2 · Room 2 En-suite (bath with tub)"
    for it in sum((a.get("items", []) for a in n.get("schedule", [])), []):
        if it[0] == "Doorway": it[1] = "Open side 130 cm beside the column; last 10 inches bricked up"
        if it[0] == "Geyser": it[1] = "50 L storage, 5-star, 16 A point"
def ed_hi(d):
    n = d.get("ROOM2_ENSUITE") or {}; n["title"] = "V2 · कमरा 2 अटैच्ड बाथ (टब के साथ)"
    ed_en({"ROOM2_ENSUITE": {"schedule": n.get("schedule", [])}})
print("missing EN:", patch("models/room1_designs.json", EN, ed_en))
print("missing HI:", patch("models/room1_designs_hi.json", HI, ed_hi))

for fn, a, b in (("src/main.js", r"const BUILD = '\d+';", "const BUILD = '25';"), ("src/inside.js", r"const V = '\d+';", "const V = '25';"), ("index.html", r"\?v=\d+", "?v=25")):
    s = open(fn).read(); s2 = re.sub(a, b, s); open(fn, "w").write(s2)
print("models:", len(models))
