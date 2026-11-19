# Ceiling options for the Compare → "Ceilings" tab (19 Nov 2026).
# Rates are installed ₹/sq ft from Indian 2025-26 cost guides (Studio Matrx = SM, HouseYog = HY, Design Cafe = DC).
# Rough figures for a tier-1 city; Sheikhpura labour is usually cheaper, so get 2-3 local quotes.
# Run: python3 scripts/ceilings_data.py models  -> models/ceilings.json
import json, os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
def P(en, hi): return [en, hi]
# Areas from the V2 model: hall ~16'5" x 30' main area (west of the pillars) ~490 sq ft; hall + passage ~670 sq ft;
# Room 1 ~182; Room 2 bedroom ~190; tub room ~84. Slab at 10 ft, two hall beams with bottoms at 9 ft.
OPTS = [
 dict(k="plain", n=P("Plain slab: good paint + surface lights", "सादी छत: अच्छा पेंट + सतह वाली लाइट"), rate="₹15–30 (paint, in paint budget) + lights",
      hall="₹5k–15k (lights only)", height=P("none lost (10 ft)", "कोई कमी नहीं (10 फीट)"), life=P("repaint every 5–7 yrs", "हर 5–7 साल पेंट"),
      pros=[P("Cheapest; full 10 ft height", "सबसे सस्ता; पूरी 10 फीट ऊँचाई"), P("Nothing to crack, sag or hide insects", "टूटने, लटकने या कीड़े छिपने की जगह नहीं"), P("Fan hangs straight from the slab hook", "पंखा सीधे स्लैब के हुक से")],
      cons=[P("Looks basic; wiring must be in the slab or in surface conduit", "सादा लगता है; वायरिंग स्लैब में या बाहर पाइप में"), P("No hidden glow", "छिपी रोशनी नहीं")],
      rate10=dict(hall=6, bed=9, wet=7), src="SM"),
 dict(k="border", n=P("Gypsum border (2 ft band) + cove LED", "जिप्सम बॉर्डर (2 फीट पट्टी) + कोव LED"), rate="₹110–190 per sq ft of band (gypsum on GI); ₹80–140 per sq ft of room (SM)",
      hall="₹40k–90k incl. ~90 ft cove LED + 8 downlights", height=P("centre keeps 10 ft; band at ~8'11\"", "बीच में 10 फीट; पट्टी ~8'11\""), life=P("15–20+ yrs if the joints are taped well", "जोड़ ठीक टेप हों तो 15–20+ साल"),
      pros=[P("The 'designer' look for about a third of a full ceiling", "पूरी छत के लगभग एक-तिहाई दाम में डिज़ाइनर लुक"), P("Hides wiring for downlights; warm cove glow", "डाउनलाइट की वायरिंग छिपती है; गर्म कोव रोशनी"), P("Lines up with the 9 ft beams so they look planned", "9 फीट बीम के साथ मिलकर बीम सोची-समझी लगती हैं")],
      cons=[P("Dust collects in the cove; wipe twice a year", "कोव में धूल; साल में दो बार साफ़"), P("Joint cracks if the frame is cheap or the slab moves", "सस्ता फ़्रेम या स्लैब हिले तो जोड़ में दरार")],
      rate10=dict(hall=9, bed=6, wet=1), src="SM"),
 dict(k="beam", n=P("Beam boxing + LED only", "सिर्फ़ बीम पर बॉक्स + LED"), rate="≈₹110–190 per sq ft of box + LED ₹120–300 per running ft (SM rates; our estimate)",
      hall="≈₹17k–36k for the two hall beams", height=P("none lost", "कोई कमी नहीं"), life=P("15+ yrs", "15+ साल"),
      pros=[P("Cheapest decorative option; turns the existing beams into a feature", "सबसे सस्ता सजावटी विकल्प; मौजूदा बीम ही डिज़ाइन बन जाती हैं"), P("Indirect light along the beams", "बीम के साथ छिपी रोशनी")],
      cons=[P("Less polished than a full border; corners stay plain", "पूरे बॉर्डर जितना साफ़-सुथरा नहीं; कोने सादे"), P("Estimate only: no guide quotes this exact job", "सिर्फ़ अनुमान: किसी गाइड में इसका सीधा दाम नहीं")],
      rate10=dict(hall=8, bed=3, wet=1), src="SM (rates), estimate"),
 dict(k="full", n=P("Full flat gypsum ceiling + cove", "पूरी जिप्सम फ़ॉल्स सीलिंग + कोव"), rate="₹110–170 plain; ₹140–210 with one cove (SM); ₹75–150 (HY)",
      hall="₹1.1–1.75 L for hall + passage; ~₹1.7–2.6 L for hall, passage and both bedrooms", height=P("must hang below the 9 ft beams: ~8'8\" everywhere", "9 फीट बीम के नीचे लटकानी पड़ेगी: हर जगह ~8'8\""), life=P("15–20+ yrs", "15–20+ साल"),
      pros=[P("Hides everything: wiring, AC pipes, beams", "सब छिपता है: वायरिंग, AC पाइप, बीम"), P("Clean, hotel-like look", "साफ़, होटल जैसा लुक")],
      cons=[P("Most expensive; loses 1'4\" of height in the hall", "सबसे महँगा; हॉल में 1'4\" ऊँचाई कम"), P("Gap above can hold lizards and insects; repairs mean cutting a panel", "ऊपर की खाली जगह में छिपकली-कीड़े; मरम्मत में पैनल काटना"), P("Standard board is not for damp rooms", "साधारण बोर्ड नमी वाले कमरों के लिए नहीं")],
      rate10=dict(hall=5, bed=4, wet=1), src="SM, HY, DC"),
 dict(k="pop", n=P("POP (plaster of Paris) on mesh", "POP (प्लास्टर ऑफ़ पेरिस) जाली पर"), rate="₹90–160 (SM); ₹65–120 (HY); ₹75–120 (DC)",
      hall="border ₹30k–70k; full ₹60k–1.07 L", height=P("same as gypsum", "जिप्सम जैसा"), life=P("long if mixed and cured well", "सही मिलावट-सुखाई हो तो लंबा"),
      pros=[P("Any curved or carved shape; local mistris know it", "कोई भी गोल/नक्काशी वाला आकार; स्थानीय मिस्त्री जानते हैं"), P("Often a bit cheaper than gypsum locally", "स्थानीय तौर पर जिप्सम से थोड़ा सस्ता")],
      cons=[P("Cracks if mixed or cured badly; very dusty and messy, slow", "ग़लत मिलावट/सुखाई पर दरार; बहुत धूल-गंदगी, धीमा"), P("Absorbs moisture", "नमी सोखता है")],
      rate10=dict(hall=6, bed=4, wet=1), src="SM, HY, DC, JK Cement, NoBroker"),
 dict(k="pvc", n=P("PVC panels", "PVC पैनल"), rate="₹70–120 (SM); ₹70–150 (HY); ₹70–160 (DC)",
      hall="tub room (~84 sq ft) ₹6k–13k", height=P("~4–6 in", "~4–6 इंच"), life=P("8–12 yrs (may yellow)", "8–12 साल (पीला पड़ सकता है)"),
      pros=[P("Waterproof, termite-proof, wipe clean", "पानी और दीमक से बचा, पोंछकर साफ़"), P("Hides exhaust duct and geyser pipes in wet rooms", "बाथरूम में एग्ज़ॉस्ट और गीज़र पाइप छिपाता है")],
      cons=[P("Visible joints; looks cheap in a living room", "जोड़ दिखते हैं; बैठक में सस्ता लगता है"), P("Can sag near heat", "गर्मी के पास लटक सकता है")],
      rate10=dict(hall=2, bed=3, wet=8), src="SM, HY, DC, Bonito"),
 dict(k="wood", n=P("Wooden / WPC slats or panels", "लकड़ी / WPC पट्टियाँ या पैनल"), rate="₹220–600 (SM); ₹120–350 (HY); ₹500–1,200 (DC)",
      hall="a 4 × 8 ft strip over the sofa ≈ ₹7k–19k", height=P("2–4 in", "2–4 इंच"), life=P("long; real wood can warp or get termites", "लंबा; असली लकड़ी टेढ़ी हो सकती है या दीमक"),
      pros=[P("Warm, rich look; good as one small feature", "गर्म, शानदार लुक; एक छोटे हिस्से में अच्छा")],
      cons=[P("Costly over a whole room; grooves collect dust", "पूरे कमरे में महँगा; खाँचों में धूल"), P("Not for wet rooms", "गीले कमरों के लिए नहीं")],
      rate10=dict(hall=4, bed=4, wet=1), src="SM, HY, DC, Bonito"),
 dict(k="grid", n=P("Grid / mineral-fibre tiles", "ग्रिड / मिनरल-फ़ाइबर टाइल"), rate="₹85–150 (DC); ₹130–280 with metal tiles (SM)",
      hall="—", height=P("8–12 in", "8–12 इंच"), life=P("tiles swap out one by one", "टाइल एक-एक कर बदलें"),
      pros=[P("Easy access above; cheap repairs", "ऊपर पहुँचना आसान; मरम्मत सस्ती")], cons=[P("Office look; not for a home", "दफ़्तर जैसा; घर के लिए नहीं")],
      rate10=dict(hall=1, bed=1, wet=3), src="SM, DC"),
 dict(k="metal", n=P("Metal / aluminium panels", "मेटल / एल्युमिनियम पैनल"), rate="₹90–250 (HY); ₹150–300 (DC)",
      hall="—", height=P("4–8 in", "4–8 इंच"), life=P("very long; does not rot", "बहुत लंबा; सड़ता नहीं"),
      pros=[P("Moisture-proof, no cracks", "नमी-रोधी, दरार नहीं")], cons=[P("Feels cold and commercial; costs more than PVC", "ठंडा, व्यावसायिक लगता है; PVC से महँगा")],
      rate10=dict(hall=2, bed=2, wet=6), src="HY, DC, Bonito"),
]
PLAN = [
 dict(room=P("Hall", "हॉल"), pick="border", cost="₹40k–90k", why=P("The hall is where guests sit and the 9 ft beams are visible. A 2 ft gypsum band with cove LED and 8 downlights matches the beams and keeps 10 ft in the middle. Too tight? Do just the beam boxing + LED (≈₹17k–36k).",
      "मेहमान हॉल में बैठते हैं और 9 फीट की बीम दिखती हैं। 2 फीट जिप्सम पट्टी, कोव LED और 8 डाउनलाइट बीम से मेल खाती है और बीच में 10 फीट रहती है। बजट कम? सिर्फ़ बीम बॉक्स + LED (≈₹17k–36k)।")),
 dict(room=P("Passage", "पैसेज"), pick="plain", cost="₹2k–4k", why=P("Narrow 5 ft strip: two surface downlights are enough.", "5 फीट चौड़ी पट्टी: दो सतह वाली डाउनलाइट काफ़ी।")),
 dict(room=P("Room 1 and Room 2", "कमरा 1 और कमरा 2"), pick="plain", cost="₹3k–8k each (lights)", why=P("Bedrooms are used with the lights off; a false ceiling adds little. White ceiling, one slim LED panel or profile light, fan from the slab hook.",
      "बेडरूम ज़्यादातर बत्ती बंद रखकर इस्तेमाल होते हैं; फ़ॉल्स सीलिंग से फ़ायदा कम। सफ़ेद छत, एक पतला LED पैनल या प्रोफ़ाइल लाइट, स्लैब के हुक से पंखा।")),
 dict(room=P("Tub room (Room 2 bath)", "टब वाला कमरा (कमरा 2 बाथ)"), pick="pvc", cost="₹6k–13k", why=P("Steam from the tub and geyser; PVC hides the exhaust duct and pipes and can't rot.", "टब और गीज़र की भाप; PVC एग्ज़ॉस्ट और पाइप छिपाता है और सड़ता नहीं।")),
 dict(room=P("Bathrooms 1 and 2, kitchen", "बाथरूम 1 और 2, रसोई"), pick="plain", cost="in paint budget", why=P("Small and damp: anti-fungal / washable paint on the slab is enough.", "छोटे और नम: स्लैब पर एंटी-फ़ंगल / धुलने वाला पेंट काफ़ी।")),
]
SUMMARY = P("My pick: spend on the hall only, keep every other ceiling plain. About ₹50k–1.1 L in all, against about ₹1.7–2.6 L for full false ceilings in the hall, passage and both bedrooms, a saving of roughly ₹1.2–1.5 L.",
            "मेरी पसंद: सिर्फ़ हॉल पर ख़र्च, बाकी सब छत सादी। कुल लगभग ₹50k–1.1 लाख, जबकि हॉल, पैसेज और दोनों बेडरूम में पूरी फ़ॉल्स सीलिंग ≈₹1.7–2.6 लाख; लगभग ₹1.2–1.5 लाख की बचत।")
TIPS = [P("Fix fan hooks, AC pipe sleeves and all wiring in the slab before any ceiling work.", "छत का कोई भी काम शुरू करने से पहले पंखे के हुक, AC पाइप स्लीव और सारी वायरिंग स्लैब में तय कर लें।"),
        P("Gypsum: ask for branded board (Gyproc / USG Boral) on GI channels, joints taped and filled; moisture-resistant (green) board near bathrooms.", "जिप्सम: GI चैनल पर ब्रांडेड बोर्ड (Gyproc / USG Boral), जोड़ टेप और भरे हुए; बाथरूम के पास नमी-रोधी (हरा) बोर्ड।"),
        P("Cove LED: warm white 3000 K, 12 V or 24 V strip with a good driver; leave an access hatch near the driver.", "कोव LED: गर्म सफ़ेद 3000 K, 12 V या 24 V स्ट्रिप और अच्छा ड्राइवर; ड्राइवर के पास खोलने का ढक्कन छोड़ें।"),
        P("Rates here are from metro cost guides; get 2–3 local quotes in Sheikhpura and compare per running foot / per sq ft of band.", "ये दाम महानगर की गाइड से हैं; शेखपुरा में 2–3 स्थानीय कोटेशन लें और प्रति रनिंग फ़ुट / पट्टी के प्रति वर्ग फ़ुट से तुलना करें।")]
SOURCES = [("Studio Matrx: false ceiling cost guide India", "https://www.studiomatrx.org/guides/false-ceiling-cost-guide-india"),
           ("HouseYog: false ceiling cost per sq ft 2026", "https://www.houseyog.com/blog/?p=1941"),
           ("Design Cafe: false ceiling cost", "https://www.designcafe.com/blog/home-interiors/false-ceiling-cost/"),
           ("Urban Company: false ceiling cost in India", "https://www.urbancompany.com/blog/how-much-does-a-false-ceiling-cost-in-india"),
           ("JK Cement: POP vs gypsum", "https://www.jkcement.com/blog/interior-design/pop-vs-gypsum-ceiling/"),
           ("Bonito: which ceiling material lasts", "https://bonito.in/blog/pop-vs-gypsum-vs-wood-vs-metal-which-false-ceiling-material-actually-lasts/"),
           ("NoBroker forum: gypsum or POP", "https://www.nobroker.in/forum/gypsum-or-pop-which-is-better")]
os.makedirs(OUT, exist_ok=True)
json.dump(dict(opts=OPTS, plan=PLAN, summary=SUMMARY, tips=TIPS, sources=SOURCES), open(os.path.join(OUT, "ceilings.json"), "w"), ensure_ascii=False, indent=1)
print("options", len(OPTS))
