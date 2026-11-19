# V1.4 "Best of both" plan (HALL_BEST) in the viewer: first in Flat plans, opens by default. Run from the MyFlat folder. Safe to re-run.
import json, collections, os, sys
OD = collections.OrderedDict
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")
V = "MyFlat_Viewer/"
def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

P = V + "models/models.json"
d = json.load(open(P, encoding="utf-8"), object_pairs_hook=OD)
FILE = "MyFlat_V1_4_Hall_BestOfBoth.glb"
d["models"] = [m for m in d["models"] if m["file"] != FILE]
d["models"].insert(0, OD([("file", FILE), ("label", "V1.4 · Best of both: 2×4 / 2×2 matt GVT, flat laminate TV wall, gypsum border"),
    ("short", "★ Best of both"), ("group", "version"), ("design", "HALL_BEST"), ("startView", "Hall:0"), ("manifest", "MyFlat_V1_4_Hall_BestOfBoth.manifest.json")]))
for m in d["models"]:
    if m["file"] == "MyFlat_V1_3_Hall_Recommended.glb": m["short"] = "Recommended"
d["default"] = FILE
json.dump(d, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

EN = OD(title="V1.4 · Best of both",
  tagline="Smooth matt GVT (2×4 ft in the hall and passage, 2×2 ft in the rooms), one flat laminate TV panel over a low cabinet, a tile band at the entry, steel pillar guards and a slim gypsum border with cove light.",
  why="This mixes my guide's Bihar-proof floor and wall picks with the Materials Field Guide's cheaper, easier-to-clean TV wall, its caution on tile size and its ceiling advice. Every surface is smooth, so there are no grooves to dust. The tub room geyser is now 50 L, because a 15 L geyser cannot fill the tub.",
  budget=OD(total="₹2,12,000–3,55,000", rows=[
    ["Floors", "Smooth matt GVT: 600×1200 in the hall and passage, 600×600 in Room 2 and the kitchen, same shade; anti-skid R11 in the bathrooms; Kota in the open square (installed)", "₹1,30,000–2,15,000"],
    ["Skirting", "4 inch tile skirting", "₹20,000–30,000"],
    ["Hall paint", "Washable emulsion over putty and primer, about 900 sq ft", "₹22,000–36,000"],
    ["TV wall", "Flat matt HPL laminate (light oak) on 18 mm BWP plywood, 7 × 7 ft, black top profile, LED strip", "₹13,000–25,000"],
    ["Entry tile band", "3'6\" matt wall tile on the entry wall (about 47 sq ft), aluminium top trim", "₹6,000–10,000"],
    ["Pillars", "304 steel corner guards, 4 ft", "₹2,000–4,000"],
    ["Ceiling border", "2 ft gypsum border on GI framing round the hall (about 170 sq ft) with cove LED", "₹19,000–35,000"]],
    note="Skip the gypsum border and the total drops to about ₹1,93,000–3,20,000. Furniture, lights, the fan, mesh doors and the geyser are not in this total. Rough 2026 estimates at Patna rates, not quotes; outside Patna add transport."),
  sections=OD([
    ("Pros", ul(["Smooth faces everywhere: no grooves collecting dust", "2×2 tiles in the rooms are easy for a local mason; 2×4 only where it shows", "TV wall costs about half of a WPC fluted wall and is easy to change later",
                 "Entry wall takes shoe and bag knocks; pillar corners don't chip", "The border hides wiring and gives soft evening light"])),
    ("Cons", ul(["Laminate looks flatter than real wood or fluting", "The border lowers the ceiling edge and adds joints to look after",
                 "Two tile sizes mean two orders in the same shade: match the batch codes", "Costs a little more than Recommended because of the ceiling"])),
    ("How long it lasts", ul(["Floor tiles: 15–25 years", "Laminate TV panel: about 10–15 years if the wall stays dry (estimate)", "Gypsum border: 15–20 years without leaks, repainted with the walls",
                              "Paint: 6–8 years", "Steel guards and tile band: for life"])),
    ("Also plan", ul(["Mosquito mesh doors: hinged, aluminium frame, replaceable mesh. Fit one room first", "Tub room geyser: 50 L (shown in the model)",
                      "Before buying tiles, take two samples home and test tea, haldi and oil on them"])),
    ("Verdict", "My pick now: the best mix of looks, easy cleaning and cost. If money is tight, drop the ceiling border first."),
  ]))
HI = OD(title="V1.4 · दोनों का सबसे अच्छा",
  tagline="चिकनी मैट GVT (हॉल और पैसेज में 2×4 फीट, कमरों में 2×2 फीट), नीची कैबिनेट के ऊपर एक सपाट लैमिनेट TV पैनल, एंट्री पर टाइल की पट्टी, खंभों पर स्टील गार्ड, और कोव लाइट वाला पतला जिप्सम बॉर्डर।",
  why="इसमें मेरी गाइड के बिहार के हिसाब से चुने फ़र्श और दीवार, और Materials Field Guide की सस्ती, आसानी से साफ़ होने वाली TV दीवार, टाइल साइज़ की सावधानी और छत की सलाह मिलाई है। हर सतह चिकनी है, धारियों में धूल नहीं। टब वाले बाथरूम का गीज़र अब 50 लीटर है, क्योंकि 15 लीटर से टब नहीं भरता।",
  budget=OD(total="₹2,12,000–3,55,000", rows=[
    ["फ़र्श", "चिकनी मैट GVT: हॉल और पैसेज में 600×1200, कमरा 2 और रसोई में 600×600, एक ही शेड; बाथरूम में एंटी-स्किड R11; आँगन में कोटा (बिछाई समेत)", "₹1,30,000–2,15,000"],
    ["स्कर्टिंग", "4 इंच टाइल स्कर्टिंग", "₹20,000–30,000"],
    ["हॉल का पेंट", "पुट्टी और प्राइमर पर धुलने वाला इमल्शन, लगभग 900 वर्ग फुट", "₹22,000–36,000"],
    ["TV दीवार", "18 mm BWP प्लाई पर सपाट मैट HPL लैमिनेट (हल्का ओक), 7 × 7 फीट, ऊपर काली पट्टी, LED", "₹13,000–25,000"],
    ["एंट्री टाइल पट्टी", "एंट्री की दीवार पर 3.5 फीट मैट दीवार टाइल (लगभग 47 वर्ग फुट), ऊपर एल्युमिनियम ट्रिम", "₹6,000–10,000"],
    ["खंभे", "304 स्टील कॉर्नर गार्ड, 4 फीट", "₹2,000–4,000"],
    ["छत का बॉर्डर", "हॉल के चारों ओर GI फ्रेम पर 2 फीट जिप्सम बॉर्डर (लगभग 170 वर्ग फुट), कोव LED के साथ", "₹19,000–35,000"]],
    note="जिप्सम बॉर्डर छोड़ दें तो कुल लगभग ₹1,93,000–3,20,000। फ़र्नीचर, लाइट, पंखा, मच्छर-जाली दरवाज़े और गीज़र इसमें नहीं हैं। पटना रेट पर 2026 के मोटे अंदाज़े, पक्का रेट नहीं; पटना से बाहर ढुलाई जोड़ें।"),
  sections=OD([
    ("फ़ायदे", ul(["हर सतह चिकनी: धारियों में धूल नहीं", "कमरों में 2×2 टाइल लोकल मिस्त्री आराम से लगाता है; 2×4 सिर्फ़ वहाँ जहाँ दिखती है", "TV दीवार WPC फ्लूटेड से लगभग आधे दाम में, बाद में बदलना आसान",
                   "एंट्री की दीवार जूते-बैग की रगड़ झेलती है; खंभों के कोने नहीं टूटते", "बॉर्डर तार छिपाता है और शाम को हल्की रोशनी देता है"])),
    ("कमियाँ", ul(["लैमिनेट असली लकड़ी या धारियों से सपाट दिखता है", "बॉर्डर छत का किनारा नीचा करता है और जोड़ों की देखभाल चाहिए",
                   "दो साइज़ की टाइल = एक ही शेड के दो ऑर्डर: बैच कोड मिलाएँ", "छत की वजह से सुझाए गए प्लान से थोड़ा महँगा"])),
    ("कितना चलेगा", ul(["फ़र्श टाइल: 15–25 साल", "लैमिनेट TV पैनल: दीवार सूखी रहे तो लगभग 10–15 साल (अंदाज़ा)", "जिप्सम बॉर्डर: लीकेज न हो तो 15–20 साल, दीवारों के साथ पेंट",
                        "पेंट: 6–8 साल", "स्टील गार्ड और टाइल पट्टी: पूरी उम्र"])),
    ("यह भी सोचें", ul(["मच्छर-जाली दरवाज़े: खुलने वाले, एल्युमिनियम फ्रेम, बदलने वाली जाली। पहले एक कमरे में लगवाएँ", "टब वाले बाथरूम का गीज़र: 50 लीटर (मॉडल में दिखाया है)",
                        "टाइल ख़रीदने से पहले दो सैंपल घर लाएँ और चाय, हल्दी, तेल डालकर देखें"])),
    ("फ़ैसला", "अब मेरी पसंद यही: लुक, सफ़ाई और ख़र्च का सबसे अच्छा मेल। पैसा कम हो तो पहले छत का बॉर्डर छोड़ें।"),
  ]))
for f, v in (("models/room1_designs.json", EN), ("models/room1_designs_hi.json", HI)):
    dd = json.load(open(V + f, encoding="utf-8"), object_pairs_hook=OD); dd["HALL_BEST"] = v
    json.dump(dd, open(V + f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

p = V + "src/i18n.js"; s = open(p, encoding="utf-8").read()
if "'★ Best of both'" not in s:
    s = s.replace("  // left panel\n", "  // left panel\n  '★ Best of both': '★ दोनों का सबसे अच्छा', 'Recommended': 'सुझाया गया',\n", 1)
open(p, "w", encoding="utf-8").write(s)
for f in ("index.html", "src/main.js"):
    t = open(V + f, encoding="utf-8").read().replace("?v=20", "?v=21").replace("BUILD = '20'", "BUILD = '21'")
    open(V + f, "w", encoding="utf-8").write(t)
print("viewer updated (v1.4 best of both)")
