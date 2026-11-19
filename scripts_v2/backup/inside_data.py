# Single source for "What's inside" layer build-ups and the shopping list.
# Writes layers.json + shop.json (viewer models/ folder and the guide page embed the same data).
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from advice import ADVICE, SHOP_ADVICE
from urllib.parse import quote_plus

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# ---------------------------------------------------------------- layer kinds (texture / colour used to draw each layer)
# kind: tile, paint, primer, putty, plaster, brick, concrete, screed, adhesive, membrane, laminate, ply, wpc, frame, gypsum, tape, marble, kota, metal, lime, glue, pipe
def L(en, hi, mm, kind, what_en, what_hi, cost=None, color=None):
    d = {"n": [en, hi], "mm": mm, "kind": kind, "what": [what_en, what_hi]}
    if cost: d["cost"] = cost
    if color: d["color"] = color
    return d

PAINT = L("Washable emulsion, 2 coats", "धुलने वाला इमल्शन, 2 कोट", 0.1, "paint",
          "The colour you see and touch: matt or low sheen, about the thickness of a sheet of paper.", "जो रंग आप देखते और छूते हैं: मैट या हल्की चमक, लगभग काग़ज़ जितना पतला।", "₹14–35 / sq ft with labour")
PRIMER = L("Primer, 1 coat", "प्राइमर, 1 कोट", 0.05, "primer", "A sealer so the paint sticks evenly and does not soak in patchily.", "सीलर, ताकि पेंट बराबर चिपके और कहीं-कहीं सोखे नहीं।")
PUTTY = L("Wall putty, 2 coats, sanded", "वॉल पुट्टी, 2 कोट, घिसाई", 1.5, "putty",
          "White cement-based paste, sanded smooth. This is what makes a wall feel glass-smooth.", "सफ़ेद सीमेंट वाला पेस्ट, घिसकर चिकना। दीवार इसी से शीशे जैसी चिकनी लगती है।")
PLASTER_IN = L("Cement plaster", "सीमेंट प्लास्टर", 12, "plaster",
               "Sand and cement (1:6) that covers the bricks and makes the wall straight. Damp shows here first.", "रेत-सीमेंट (1:6) की परत, जो ईंट ढकती है और दीवार सीधी करती है। सीलन सबसे पहले यहीं दिखती है।")
BRICK_IN = L("Brick wall, 4½ inch", "ईंट की दीवार, 4½ इंच", 115, "brick", "Burnt clay bricks in cement mortar. Already built.", "सीमेंट मसाले में पक्की ईंट। पहले से बनी है।")
BRICK_EX = L("Brick wall, 9 inch", "ईंट की दीवार, 9 इंच", 230, "brick", "Outer walls are two bricks thick. Already built.", "बाहर की दीवार दो ईंट मोटी। पहले से बनी है।")
PLASTER_EX = L("Outside plaster", "बाहर का प्लास्टर", 18, "plaster", "Thicker plaster facing the rain, with a waterproof additive.", "बारिश की तरफ़ मोटा प्लास्टर, वॉटरप्रूफ़ मसाले के साथ।")
EXT_PAINT = L("Exterior emulsion", "बाहर का पेंट", 0.15, "paint", "Weather-proof paint outside.", "मौसम झेलने वाला बाहर का पेंट।", color="#D9CDB8")
RCC_SLAB = L("RCC slab", "RCC छत / स्लैब", 125, "concrete", "Concrete with steel bars: the structure. Already built.", "सरिया वाला कंक्रीट: ढाँचा। पहले से बना है।")
SCREED = L("Cement-sand screed", "सीमेंट-रेत का लेवल मसाला", 40, "screed", "Levels the slab. It must be cured and flat before tiling.", "स्लैब को समतल करता है। टाइल से पहले पका और सपाट होना चाहिए।", "₹15–30 / sq ft")
ADH = L("Tile adhesive (C2)", "टाइल एडहेसिव (C2)", 4, "adhesive",
        "Polymer cement paste spread with a notched trowel. The tile is pressed in fully so no air stays under it.", "दाँतेदार करनी से फैलाया पॉलिमर सीमेंट पेस्ट। टाइल पूरी दबाई जाती है ताकि नीचे हवा न रहे।", "₹12–25 / sq ft")

def tile(en, hi, mm, what_en, what_hi, cost, color):
    return L(en, hi, mm, "tile", what_en, what_hi, cost, color)

LAYERS = {
  "gvt": {"title": ["Tiled floor: matt GVT", "टाइल वाला फ़र्श: मैट GVT"], "axis": "floor",
          "feel": ["Smooth with a soft, low sheen; cool underfoot. Tap it with a coin: a clear 'tak' is good, a dull hollow 'tuk' means air under the tile.",
                   "चिकना, हल्की धीमी चमक; पैर के नीचे ठंडा। सिक्के से ठोकें: साफ़ 'टक' सही है, खोखली 'टुक' मतलब टाइल के नीचे हवा।"],
          "layers": [tile("Matt GVT tile, 9 mm", "मैट GVT टाइल, 9 mm", 9, "Vitrified body with a printed glaze on top. The stone look is only the top glaze. 2 mm joints filled with grout.",
                          "विट्रीफाइड बॉडी, ऊपर छपा हुआ ग्लेज़। पत्थर जैसा लुक सिर्फ़ ऊपर की परत में। 2 mm जोड़ में ग्राउट।", "₹55–100 / sq ft (tile)", "#CFC6B8"), ADH, SCREED, RCC_SLAB]},
  "dc": {"title": ["Tiled floor: double-charge", "टाइल वाला फ़र्श: डबल चार्ज"], "axis": "floor",
         "feel": ["Shiny and hard; colour goes 3–4 mm deep, so wear marks don't show.", "चमकदार और सख़्त; रंग 3–4 mm गहरा, घिसाव नहीं दिखता।"],
         "layers": [tile("Double-charge tile, 10 mm", "डबल चार्ज टाइल, 10 mm", 10, "Two layers of colour pressed together, 3–4 mm deep. Polished on top.", "रंग की दो परतें दबाकर, 3–4 mm गहरी। ऊपर पॉलिश।", "₹40–60 / sq ft (tile)", "#D6CDBC"), ADH, SCREED, RCC_SLAB]},
  "fb": {"title": ["Tiled floor: full-body vitrified", "टाइल वाला फ़र्श: फुल बॉडी"], "axis": "floor",
         "feel": ["Matt and hard; the colour runs right through, so a chip looks like the top.", "मैट और सख़्त; रंग पूरी टाइल में, चटका भी ऊपर जैसा दिखता है।"],
         "layers": [tile("Full-body tile, 10 mm", "फुल बॉडी टाइल, 10 mm", 10, "Same colour through the whole thickness.", "पूरी मोटाई में एक ही रंग।", "₹80–150 / sq ft (tile)", "#BDBBB6"), ADH, SCREED, RCC_SLAB]},
  "marble": {"title": ["Marble floor", "मार्बल फ़र्श"], "axis": "floor",
             "feel": ["Very smooth and cold; glossy after polishing. Haldi or lemon left on it stains.", "बहुत चिकना और ठंडा; घिसाई के बाद चमकदार। हल्दी या नींबू पड़ा रहे तो दाग।"],
             "layers": [L("Indian marble, 18 mm", "देसी मार्बल, 18 mm", 18, "marble", "Natural stone slabs, ground and polished on site after laying.", "प्राकृतिक पत्थर की स्लैब, बिछाने के बाद घिसाई और पॉलिश।", "₹120–250 / sq ft (stone)"),
                        L("Cement mortar bed", "सीमेंट मसाले का बेड", 25, "screed", "Stone is laid on a thick mortar bed.", "पत्थर मोटे मसाले पर बिछता है।"), RCC_SLAB]},
  "wet": {"title": ["Bathroom floor", "बाथरूम का फ़र्श"], "axis": "floor",
          "feel": ["Slightly rough and grippy, even with wet feet. Water runs to the drain, no puddles.", "हल्का खुरदरा, गीले पैर में भी पकड़। पानी नाली की ओर बहता है, जमता नहीं।"],
          "layers": [tile("Anti-skid tile R11, 8 mm", "एंटी-स्किड टाइल R11, 8 mm", 8, "Textured matt tile; joints filled with epoxy grout that doesn't turn black.", "खुरदरी मैट टाइल; जोड़ों में इपॉक्सी ग्राउट, काला नहीं पड़ता।", "₹50–90 / sq ft (tile)", "#A9BEC4"),
                     ADH,
                     L("Waterproofing coat", "वॉटरप्रूफिंग की परत", 2, "membrane", "Two coats of polymer waterproofing, turned 1 ft up the walls (3 ft at the tub). Tested with standing water before tiling.",
                       "पॉलिमर वॉटरप्रूफिंग के दो कोट, दीवार पर 1 फीट ऊपर तक (टब के पास 3 फीट)। टाइल से पहले पानी भरकर जाँच।", "₹40–80 / sq ft"),
                     L("Screed sloped to the drain", "नाली की ओर ढलान वाला मसाला", 40, "screed", "Gives the fall towards the drain (about 1 in 100).", "नाली की ओर ढलान देता है (लगभग 100 में 1)।"), RCC_SLAB]},
  "kota": {"title": ["Kota stone floor (outside)", "कोटा पत्थर का फ़र्श (बाहर)"], "axis": "floor",
           "feel": ["Natural, slightly textured stone; not slippery; stays cool.", "प्राकृतिक, हल्का खुरदरा पत्थर; फिसलता नहीं; ठंडा रहता है।"],
           "layers": [L("Kota stone, 25 mm", "कोटा पत्थर, 25 mm", 25, "kota", "Green-grey limestone slabs, natural or leather finish.", "हरा-भूरा पत्थर, नेचुरल या लेदर फ़िनिश।", "₹70–120 / sq ft installed"),
                      L("Cement mortar bed", "सीमेंट मसाले का बेड", 25, "screed", "Laid on mortar, sloped to the drain.", "मसाले पर, नाली की ओर ढलान।"), RCC_SLAB]},
  "wall_int": {"title": ["Painted inside wall", "अंदर की पेंट वाली दीवार"], "axis": "wall",
               "feel": ["Smooth and matt like an eggshell, with a faint dimple from the paint roller. Cool to touch. Knock: solid brick, not hollow.",
                        "अंडे के छिलके जैसी चिकनी और मैट, रोलर से हल्के-हल्के दाने। छूने में ठंडी। ठोकें: ठोस ईंट, खोखली नहीं।"],
               "layers": [PAINT, PRIMER, PUTTY, PLASTER_IN, BRICK_IN], "note": ["The other face of the wall has the same plaster, putty and paint.", "दीवार के दूसरी तरफ़ भी यही प्लास्टर, पुट्टी और पेंट।"]},
  "wall_ext": {"title": ["Painted outer wall", "बाहर वाली पेंट की दीवार"], "axis": "wall",
               "feel": ["Inside it feels like any painted wall. Outer walls get damp first in the monsoon: watch for dark patches near the floor.",
                        "अंदर से आम पेंट वाली दीवार जैसी। बरसात में बाहर की दीवार में सीलन पहले आती है: फ़र्श के पास गहरे धब्बे देखें।"],
               "layers": [PAINT, PRIMER, PUTTY, PLASTER_IN, BRICK_EX, PLASTER_EX, EXT_PAINT]},
  "rcc": {"title": ["Painted pillar or beam", "पेंट वाला खंभा या बीम"], "axis": "wall",
          "feel": ["Same smooth paint as the walls; corners chip easily, hence steel corner guards.", "दीवार जैसा ही चिकना पेंट; कोने जल्दी टूटते हैं, इसलिए स्टील कॉर्नर गार्ड।"],
          "layers": [PAINT, PRIMER, PUTTY, L("Plaster", "प्लास्टर", 10, "plaster", "Thin plaster over the concrete.", "कंक्रीट पर पतला प्लास्टर।"),
                     L("RCC column / beam", "RCC खंभा / बीम", 230, "concrete", "Concrete with steel bars: carries the building. Never cut into it.", "सरिया वाला कंक्रीट: बिल्डिंग का भार उठाता है। इसमें कभी काट-छाँट नहीं।")]},
  "ceiling": {"title": ["Painted ceiling", "पेंट वाली छत"], "axis": "ceiling",
              "feel": ["Flat and matt white; any crack or damp patch here means a leak above.", "सपाट मैट सफ़ेद; दरार या सीलन यानी ऊपर से रिसाव।"],
              "layers": [PAINT, PRIMER, PUTTY, L("Ceiling plaster / POP punning", "छत का प्लास्टर / POP", 6, "plaster", "Thin smoothing coat under the slab.", "स्लैब के नीचे पतली चिकनी परत।"), RCC_SLAB]},
  "tv_laminate": {"title": ["Flat laminate TV panel", "सपाट लैमिनेट TV पैनल"], "axis": "wall",
                  "feel": ["Smooth, dry and slightly warm, with a printed wood grain you can see but barely feel. Knock: a duller wooden sound than the wall.",
                           "चिकना, सूखा और हल्का गर्म; लकड़ी जैसी छपाई दिखती है, छूने में मुश्किल से। ठोकें: दीवार से धीमी लकड़ी जैसी आवाज़।"],
                  "layers": [L("HPL laminate (sunmica), 1 mm, matt", "HPL लैमिनेट (सनमाइका), 1 mm, मैट", 1, "laminate", "The face you see: printed light oak with a tough clear top. Wipes clean.", "जो दिखता है: हल्का ओक छपा, ऊपर सख़्त परत। पोंछने से साफ़।", "₹1,200–3,000 per 8×4 sheet"),
                             L("Contact adhesive", "कॉन्टैक्ट गोंद", 0.3, "glue", "Glues the laminate to the plywood.", "लैमिनेट को प्लाई पर चिपकाता है।"),
                             L("BWP plywood, 18 mm", "BWP प्लाई, 18 mm", 18, "ply", "Boiling-water-proof ply with termite treatment: the strong core. Write the brand and grade on the quote.", "उबलते पानी में भी न ख़राब होने वाली, दीमक-रोधी प्लाई: मज़बूत कोर। कोटेशन पर ब्रांड और ग्रेड लिखवाएँ।", "₹110–180 / sq ft"),
                             L("Balancing laminate, 0.8 mm", "पीछे का बैलेंसिंग लैमिनेट, 0.8 mm", 0.8, "laminate", "A plain sheet on the back so the board doesn't bend.", "पीछे सादी शीट, ताकि बोर्ड टेढ़ा न हो।", color="#E9E4DA"),
                             L("Cable gap with PVC conduit", "तार के लिए गैप और PVC पाइप", 25, "pipe", "TV, HDMI and power cables run here; keep an access flap at the socket.", "TV, HDMI और बिजली के तार यहीं; सॉकेट पर खुलने वाला ढक्कन रखें।"),
                             PAINT, PUTTY, PLASTER_IN, BRICK_EX]},
  "tv_wpc": {"title": ["WPC fluted panel", "WPC फ्लूटेड पैनल"], "axis": "wall",
             "feel": ["Ribbed under your hand, plasticky-smooth, light. Dust settles in the grooves.", "हाथ में धारीदार, प्लास्टिक जैसा चिकना, हल्का। धारियों में धूल बैठती है।"],
             "layers": [L("WPC fluted panel, 12 mm", "WPC फ्लूटेड पैनल, 12 mm", 12, "wpc", "Wood-plastic composite with a printed wood film; waterproof and termite-proof.", "लकड़ी-प्लास्टिक का पैनल, ऊपर लकड़ी जैसी फ़िल्म; पानी और दीमक से सुरक्षित।", "₹180–320 / sq ft installed"),
                        L("Battens or clips", "पट्टियाँ या क्लिप", 20, "frame", "Panels click onto battens screwed to the wall, or are glued directly.", "पैनल दीवार पर लगी पट्टियों पर फँसते हैं, या सीधे चिपकते हैं।"),
                        PUTTY, PLASTER_IN, BRICK_EX]},
  "porcelain": {"title": ["Porcelain slab TV wall", "पोर्सलेन स्लैब TV दीवार"], "axis": "wall",
                "feel": ["Glass-hard, cool and smooth like a tile. Knock: solid.", "काँच जैसा सख़्त, ठंडा और चिकना, टाइल जैसा। ठोकें: ठोस।"],
                "layers": [tile("Porcelain slab, 9 mm", "पोर्सलेन स्लैब, 9 mm", 9, "Large 800×1600 slabs with a marble print.", "800×1600 की बड़ी स्लैब, मार्बल जैसी छपाई।", "₹200–400 / sq ft installed", "#ECEBE8"),
                           L("Wall tile adhesive (C2TE S1)", "दीवार टाइल एडहेसिव (C2TE S1)", 6, "adhesive", "Flexible adhesive for heavy wall slabs.", "भारी स्लैब के लिए लचीला एडहेसिव।"), PLASTER_IN, BRICK_EX]},
  "limewash": {"title": ["Limewash feature wall", "लाइमवॉश फ़ीचर दीवार"], "axis": "wall",
               "feel": ["Soft, chalky and cloudy; slightly powdery to touch.", "मुलायम, चॉक जैसी, बादलों जैसे रंग; छूने में हल्की पाउडर जैसी।"],
               "layers": [L("Limewash, 2–3 coats", "लाइमवॉश, 2–3 कोट", 0.3, "lime", "Lime paint brushed on in crossing strokes.", "चूने का पेंट, आड़े-तिरछे ब्रश से।", "₹60–150 / sq ft"),
                          L("Lime primer", "लाइम प्राइमर", 0.1, "primer", "Helps the lime grip.", "चूने की पकड़ के लिए।"), PLASTER_IN, BRICK_EX]},
  "entry_dado": {"title": ["Entry tile band", "एंट्री की टाइल पट्टी"], "axis": "wall",
                 "feel": ["Hard, cool and wipeable; the aluminium trim on top feels like a smooth metal edge.", "सख़्त, ठंडी, पोंछने लायक; ऊपर की एल्युमिनियम पट्टी चिकना धातु का किनारा।"],
                 "layers": [tile("Matt wall tile 300×600, 8 mm", "मैट दीवार टाइल 300×600, 8 mm", 8, "Light stone look; joints matched to the tile colour.", "हल्का पत्थर जैसा; जोड़ टाइल के रंग के।", "₹40–80 / sq ft (tile)", "#DAD5CC"),
                            L("Tile adhesive", "टाइल एडहेसिव", 4, "adhesive", "Fixed with adhesive, not a thick cement bed.", "मोटे सीमेंट की जगह एडहेसिव से।"), PLASTER_IN, BRICK_EX]},
  "gypsum": {"title": ["Gypsum ceiling border", "जिप्सम छत बॉर्डर"], "axis": "ceiling",
             "feel": ["Looks like the plastered ceiling; knock and it sounds hollow, because it hangs below the slab.", "प्लास्टर वाली छत जैसा दिखता है; ठोकें तो खोखला, क्योंकि यह स्लैब के नीचे लटकता है।"],
             "layers": [PAINT, PUTTY, L("Joint tape + compound", "जोड़ टेप + कंपाउंड", 1, "tape", "Hides the board joints so no cracks show.", "बोर्ड के जोड़ छिपाता है, दरार नहीं दिखती।"),
                        L("Gypsum board, 12.5 mm", "जिप्सम बोर्ड, 12.5 mm", 12.5, "gypsum", "Factory-made plaster board screwed to the frame.", "फ़ैक्ट्री का प्लास्टर बोर्ड, फ्रेम पर स्क्रू से।", "₹90–160 / sq ft with frame"),
                        L("GI ceiling frame", "GI फ्रेम", 50, "frame", "Galvanised steel channels hung from the slab. LED cove sits in an aluminium channel at the edge.", "स्लैब से लटकी जस्ती स्टील की चैनलें। किनारे पर एल्युमिनियम चैनल में LED।"),
                        L("Air gap (wires, lights)", "खाली जगह (तार, लाइट)", 150, "gap", "Room for wiring and downlights; keep an access panel.", "तार और लाइट के लिए जगह; खोलने का ढक्कन रखें।"), RCC_SLAB]},
  "wainscot": {"title": ["Half-wall panelling (wainscot)", "आधी दीवार पैनलिंग"], "axis": "wall",
               "feel": ["Smooth painted panels with raised moulding strips; takes mop and chair knocks.", "चिकने पेंट वाले पैनल, उभरी पट्टियाँ; पोंछे और कुर्सी की रगड़ झेलते हैं।"],
               "layers": [L("WPC / HDHMR panel with moulding, 9 mm", "मोल्डिंग वाला WPC / HDHMR पैनल, 9 mm", 9, "wpc", "Satin-painted panels; champagne aluminium cap on top.", "सैटिन पेंट वाले पैनल; ऊपर शैम्पेन एल्युमिनियम कैप।", "₹180–350 / sq ft", "#8E9E86"),
                          L("Adhesive", "गोंद", 1, "glue", "Glued to a dry wall.", "सूखी दीवार पर चिपकाया।"), PLASTER_IN, BRICK_IN]},
  "skirting": {"title": ["Tile skirting", "टाइल स्कर्टिंग"], "axis": "wall",
               "feel": ["A 4 inch strip of floor tile at the bottom of the wall; takes mop knocks.", "दीवार के नीचे फ़र्श टाइल की 4 इंच पट्टी; पोंछे की रगड़ झेलती है।"],
               "layers": [tile("Floor tile strip, 9 mm", "फ़र्श टाइल की पट्टी, 9 mm", 9, "Cut from the same floor tile.", "उसी फ़र्श टाइल से कटी।", "₹25–45 / running ft", "#CFC6B8"), ADH, PLASTER_IN, BRICK_IN]},
}

RULES = [  # first match wins; name / spec are regexes (case-insensitive), cat and sub exact
  {"name": "TV_PANEL(?!_)", "id": "tv_laminate"}, {"name": "TV_WALL_SLABS", "id": "porcelain"}, {"name": "LIMEWASH", "id": "limewash"},
  {"name": "FLUTE|TV_WALL_PANEL|FEATURE_WALL_PANEL|PILLAR_WRAP", "id": "tv_wpc"}, {"name": "WAINSCOT", "id": "wainscot"},
  {"name": "ENTRY_DADO", "id": "entry_dado"}, {"name": "GYPSUM_BORDER", "id": "gypsum"}, {"name": "SKIRTING", "id": "skirting"},
  {"spec": "anti-skid", "id": "wet"}, {"spec": "kota", "id": "kota"}, {"spec": "marble", "id": "marble", "name": "FINISH"},
  {"spec": "double-charge", "id": "dc"}, {"spec": "full-body", "id": "fb"}, {"spec": "GVT|vitrified", "id": "gvt", "name": "FINISH"},
  {"cat": "floors", "id": "gvt"}, {"cat": "walls", "sub": "external", "id": "wall_ext"}, {"cat": "walls", "id": "wall_int"},
  {"cat": "pillars", "id": "rcc"}, {"cat": "beams", "id": "rcc"}, {"cat": "ceiling", "id": "ceiling"},
]
ORDER = ["wall_int", "wall_ext", "ceiling", "gvt", "wet", "kota", "tv_laminate", "tv_wpc", "porcelain", "entry_dado", "gypsum", "skirting", "rcc", "dc", "fb", "marble", "limewash", "wainscot"]

# ---------------------------------------------------------------- shopping list
def az(q, lo=None, hi=None):
    u = "https://www.amazon.in/s?k=" + quote_plus(q)
    if lo is not None: u += f"&rh=p_36%3A{lo * 100}-{hi * 100}"
    return u
def dp(asin): return f"https://www.amazon.in/dp/{asin}"
def item(k, match, en, hi, size_en, size_hi, q_b, b, q_m, m, examples=(), note=None, qty=1):
    d = {"k": k, "match": match, "n": [en, hi], "size": [size_en, size_hi], "qty": qty,
         "budget": {"band": f"₹{b[0]:,}–{b[1]:,}", "url": az(q_b, *b)}, "mid": {"band": f"₹{m[0]:,}–{m[1]:,}", "url": az(q_m, *m)},
         "ex": [{"t": t, "url": dp(a)} for t, a in examples]}
    if note: d["note"] = note
    return d

SHOP = [
  item("sofa", "SOFA", "3-seater sofa", "3-सीटर सोफ़ा", "about 7 ft, fabric, oatmeal / beige", "लगभग 7 फीट, कपड़ा, बेज", "3 seater fabric sofa beige", (12000, 25000), "3 seater fabric sofa premium", (25000, 50000),
       [("Sofa Architect Chilly 3-seater, beige", "B08DR7NKQG"), ("Sofa Architect Harlem 3-seater, beige", "B08BXLMWLM")]),
  item("bed", "_BED_", "Queen bed with storage", "स्टोरेज वाला क्वीन बेड", "5 × 6½ ft (Room 1)", "5 × 6½ फीट (कमरा 1)", "queen size bed with storage engineered wood", (10000, 20000), "sheesham wood queen size bed with storage", (20000, 40000),
       [("WOODLAB sheesham queen bed, 4 drawers", "B08ZJJ5NJ2"), ("TG Furniture sheesham queen bed, pull-out storage", "B09CQ17VXR")], ["Mattress not included: budget ₹8–15k (6 inch).", "गद्दा अलग: ₹8–15 हज़ार (6 इंच)।"]),
  item("coffee", "COFFEE_TABLE", "Coffee table with shelf", "शेल्फ़ वाली सेंटर टेबल", "about 4 × 2½ ft", "लगभग 4 × 2½ फीट", "wooden coffee table with shelf", (2000, 6000), "solid wood coffee table with shelf", (6000, 15000)),
  item("side", "SIDE_TABLE", "Round side table", "गोल साइड टेबल", "about 1½ ft across", "लगभग 1½ फीट", "round side table metal base wooden top", (1000, 3000), "round side table metal base wooden top", (3000, 8000)),
  item("lamp", "FLOOR_LAMP", "Floor lamp", "फ़्लोर लैंप", "about 5½ ft, fabric shade", "लगभग 5½ फीट, कपड़े का शेड", "tripod floor lamp fabric shade", (1500, 4000), "floor lamp linen shade living room", (4000, 10000),
       [("VDIX tripod floor lamp, wooden stand", "B0BH1449NG"), ("Wooden tripod floor lamp with shelves, beige shade", "B0H18V3JNX")]),
  item("pendant", "PENDANT", "Pendant lights over the dining table", "डाइनिंग के ऊपर लटकती लाइट", "black metal cone, about 10–12 inch; need 2", "काला धातु का कोन, 10–12 इंच; 2 चाहिए", "black metal cone pendant light", (500, 1500), "black metal pendant light dining", (1500, 5000),
       [("Lexton metal cone pendant light", "B0CB1D1MHR")], qty=2),
  item("dining", "DINING_", "Dining set", "डाइनिंग सेट", "6-seater about 6 × 3 ft (budget plan: 4-seater)", "6-सीटर लगभग 6 × 3 फीट (बजट: 4-सीटर)", "4 seater dining table set wooden", (10000, 20000), "sheesham 6 seater dining table set cushioned chairs", (25000, 55000),
       [("WOODSTAGE sheesham 6-seater with cushioned chairs", "B0BNX5346F")]),
  item("tvunit", "TV_(CABINET|CONSOLE|UNIT)", "Low TV cabinet", "नीची TV कैबिनेट", "about 6 ft, closed, floor-standing", "लगभग 6 फीट, बंद, ज़मीन पर", "tv unit floor standing 6 feet", (5000, 10000), "tv unit floor standing 6 feet solid wood", (10000, 25000)),
  item("curtains", "CURTAIN", "Curtains for window W7", "खिड़की W7 के पर्दे", "7 ft, set of 2, blackout", "7 फीट, 2 का सेट, ब्लैकआउट", "blackout curtains 7 feet set of 2 beige", (700, 1500), "linen curtains 7 feet set of 2", (1500, 4000),
       [("Cortina 80–90% blackout door curtains, 7 ft, set of 2", "B0F23RVLCS"), ("LINENWALAS 100% blackout curtains, 7 ft, set of 2", "B0F3DG85RP")]),
  item("rug", "RUG", "Rug under the sofa", "सोफ़े के नीचे दरी", "6 × 9 ft or 8 × 8 ft, cotton (washable)", "6 × 9 या 8 × 8 फीट, सूती (धुलने वाली)", "cotton dhurrie 6x9 feet", (2000, 5000), "handwoven rug 6x9 feet living room", (5000, 16000),
       [("Jaipur Rugs soft dhurrie, striped, 6 × 9 ft", "B0DTDQ3J16")]),
  item("art", "WALL_ART", "Framed wall art", "फ़्रेम वाली पेंटिंग", "about 3 × 2½ ft, or a set of 3", "लगभग 3 × 2½ फीट, या 3 का सेट", "boho abstract framed wall art", (500, 1500), "boho abstract framed canvas wall art large", (1500, 5000),
       [("Livin'luxe boho arch print, golden frame", "B0F8B46H82")]),
  item("plant", "PLANT", "Plant pots", "गमले", "12–14 inch pot; buy the areca palm / snake plant at a local nursery", "12–14 इंच गमला; पौधा (एरेका पाम / स्नेक प्लांट) लोकल नर्सरी से", "ceramic planter pot 12 inch", (500, 1500), "large ceramic planter pot with stand", (1500, 4000)),
  item("fan", "FAN_", "BLDC ceiling fan", "BLDC पंखा", "1200 mm, 5-star (about 30 W)", "1200 mm, 5-स्टार (लगभग 30 W)", "BLDC ceiling fan 1200mm", (2500, 4000), "BLDC ceiling fan 1200mm remote premium", (4000, 7000),
       [("atomberg Efficio 1200 mm BLDC", "B071Y7K862"), ("atomberg Renesa Enzel 1200 mm BLDC", "B0CHJNJJDP")]),
  item("downlight", "DOWNLIGHT", "LED downlights", "LED डाउनलाइट", "10–12 W, 3000K warm white; about 8 for the hall", "10–12 W, 3000K गर्म रोशनी; हॉल में लगभग 8", "12W LED round panel downlight warm white", (150, 400), "COB LED downlight 12W 3000K anti glare", (400, 1200), qty=8),
  item("cove", "COVE_LED|_LED$|TV_PANEL_LED|TV_WALL_LED", "LED strip (cove / TV wall)", "LED पट्टी (कोव / TV दीवार)", "warm white 3000K, 5 m with driver", "गर्म सफ़ेद 3000K, 5 मीटर, ड्राइवर के साथ", "LED strip light warm white 5 meter with adapter", (500, 1200), "COB LED strip 24V warm white 5 meter", (1200, 3000)),
  item("shoe", "SHOE_(CABINET|RACK)", "Shoe cabinet", "जूते की अलमारी", "about 3½ ft wide, with doors", "लगभग 3½ फीट चौड़ी, दरवाज़े वाली", "shoe cabinet with doors engineered wood", (2000, 5000), "shoe cabinet with doors wooden large", (5000, 12000),
       [("LERIMO Elano 2-door shoe cabinet", "B0FHW9ZXGG")]),
  item("geyser", "GEYSER", "Geyser for the tub room", "टब वाले बाथरूम का गीज़र", "50 L, 5-star, vertical", "50 लीटर, 5-स्टार, खड़ा", "50 litre geyser 5 star", (6000, 10000), "50 litre geyser 5 star vertical glass lined", (10000, 18000),
       [("Bajaj Arrmand 50 L", "B0D49Q51WN"), ("Racold Platinum Nxt 50 L vertical", "B0CYLH96QR")]),
  item("mesh", "", "Mosquito mesh door", "मच्छर-जाली दरवाज़ा", "one per room door; measure each door", "हर कमरे के दरवाज़े पर एक; हर दरवाज़ा नापें", "magnetic mosquito net for door", (300, 1000), "aluminium frame mosquito net door", (2000, 6000),
       [("LifeKrafts magnetic mosquito net for door", "B08M5TTT9P")], ["A hinged aluminium door from a local fabricator is sturdier: about ₹4–6k per door.", "लोकल कारीगर से कब्ज़े वाला एल्युमिनियम दरवाज़ा ज़्यादा मज़बूत: लगभग ₹4–6 हज़ार प्रति दरवाज़ा।"]),
]
SHOP_NOTE = ["Amazon doesn't let me read its pages, so I couldn't check today's prices. The two links open Amazon already filtered to a budget band and a mid-range band; the examples are real listings to compare. Check size, reviews and return policy before buying.",
             "Amazon अपने पेज मुझे पढ़ने नहीं देता, इसलिए आज का दाम जाँच नहीं पाया। दोनों लिंक Amazon को बजट और मिड-रेंज दाम पर छाँटकर खोलते हैं; उदाहरण असली लिस्टिंग हैं। ख़रीदने से पहले साइज़, रिव्यू और रिटर्न पॉलिसी देखें।"]

for k, v in ADVICE.items():
    assert k in LAYERS, k
    LAYERS[k].update(v)
missing = [k for k in LAYERS if k not in ADVICE]
assert not missing, missing
for it in SHOP:
    w, t = SHOP_ADVICE[it["k"]]; it["why"] = w; it["tip"] = t
os.makedirs(OUT, exist_ok=True)
json.dump({"layers": LAYERS, "rules": RULES, "order": ORDER}, open(os.path.join(OUT, "layers.json"), "w"), ensure_ascii=False, indent=1)
json.dump({"items": SHOP, "note": SHOP_NOTE}, open(os.path.join(OUT, "shop.json"), "w"), ensure_ascii=False, indent=1)
print("layers", len(LAYERS), "shop", len(SHOP))
