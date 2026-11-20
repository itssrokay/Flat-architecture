# Adds the "Tiles & stone" tab to Learn (EN + HI): all options, what we chose and why, comparison with ratings, granite,
# Papa's measurement list with a box calculator, buying/laying tips, links. Safe to re-run.
# Run from MyFlat_Viewer: python3 scripts/learn_tiles.py
import json

# Papa's list (sent 20 Nov 2026), as written, with our reading. a, b in feet; kind: floor / wall.
PAPA = [
 dict(t="12*19 Rom", a=12, b=19, k="floor", tile="600x600", en="A bedroom, 228 sq ft. Our plan: Room 2 bedroom ≈ 12 × 17, Room 1 ≈ 12.6 × 14.5. Which room is this?", hi="एक बेडरूम, 228 वर्ग फ़ुट। हमारे प्लान में कमरा 2 ≈ 12 × 17, कमरा 1 ≈ 12.6 × 14.5। यह कौन सा कमरा है?"),
 dict(t="17*15 rom 3rd flor", a=17, b=15, k="floor", tile="600x600", en="A room on the 3rd floor, 255 sq ft. Not in our flat model: is it a separate floor?", hi="तीसरी मंज़िल का कमरा, 255 वर्ग फ़ुट। हमारे फ़्लैट मॉडल में नहीं: क्या यह अलग मंज़िल है?"),
 dict(t="6*10", a=6, b=10, k="floor", tile="600x600", en="60 sq ft, no name. Passage (plan 5 × 14.5) or balcony?", hi="60 वर्ग फ़ुट, नाम नहीं। पैसेज (प्लान 5 × 14.5) या बालकनी?"),
 dict(t="4*5 holl flor tils", a=4, b=5, k="floor", tile="600x1200", en="Only 20 sq ft, but our hall is about 600 sq ft. Maybe '4×2 ft hall tiles' (our pick) or a small landing?", hi="सिर्फ़ 20 वर्ग फ़ुट, जबकि हॉल लगभग 600 वर्ग फ़ुट। शायद 'हॉल की 4×2 फीट टाइल' (हमारी पसंद) या छोटी लैंडिंग?"),
 dict(t="9*7flor", a=9, b=7, k="floor", tile="600x600", en="Kitchen floor, 63 sq ft. Matches our plan (9.7 × 7.1). ✓", hi="रसोई का फ़र्श, 63 वर्ग फ़ुट। हमारे प्लान (9.7 × 7.1) से मेल। ✓"),
 dict(t="10*7.25bath", a=10, b=7.25, k="floor", tile="300x600", en="The bigger bathroom (tub side), 72.5 sq ft. Plan ≈ 12.6 × 6.3. Close. ✓", hi="बड़ा बाथरूम (टब वाला), 72.5 वर्ग फ़ुट। प्लान ≈ 12.6 × 6.3। लगभग मेल। ✓"),
 dict(t="5*7 bhat flor", a=5, b=7, k="floor", tile="300x600", en="Small bathroom floor, 35 sq ft (Bath 1 ≈ 4 × 8.5 or Bath 2 ≈ 4.4 × 7.1). Only one listed: the other bathroom is missing.", hi="छोटे बाथरूम का फ़र्श, 35 वर्ग फ़ुट (बाथ 1 ≈ 4 × 8.5 या बाथ 2 ≈ 4.4 × 7.1)। एक ही लिखा है: दूसरा बाथरूम छूट गया।"),
 dict(t="52*7 bath diwal", a=52, b=7, k="wall", tile="300x600", en="Bathroom walls: 52 running ft tiled up to 7 ft = 364 sq ft. Our three wet rooms add up to about 78 ft of wall after doors, so this may cover only two of them.", hi="बाथरूम की दीवारें: 52 रनिंग फ़ुट, 7 फ़ुट ऊँचाई तक = 364 वर्ग फ़ुट। हमारे तीनों बाथरूम मिलाकर दरवाज़े घटाकर लगभग 78 फ़ुट दीवार, तो शायद दो ही गिने हैं।"),
 dict(t="27*6 किचन दिवाल", a=27, b=6, k="wall", tile="300x600", en="Kitchen walls: 27 running ft tiled up to 6 ft = 162 sq ft. Matches the kitchen walls minus door and window. ✓", hi="रसोई की दीवारें: 27 रनिंग फ़ुट, 6 फ़ुट ऊँचाई तक = 162 वर्ग फ़ुट। दरवाज़ा-खिड़की घटाकर रसोई की दीवारों से मेल। ✓"),
]
MISSING = [
 dict(t="Hall (not in the list)", a=16.5, b=30, k="floor", tile="600x1200", en="Hall ≈ 16.5 × 30 ft in our plan (~500 sq ft) plus the strip by the pillars. The biggest area; please measure.", hi="हॉल हमारे प्लान में ≈ 16.5 × 30 फ़ुट (~500 वर्ग फ़ुट) और खंभों के पास की पट्टी। सबसे बड़ा हिस्सा; कृपया नापें।"),
 dict(t="Second small bathroom", a=4.4, b=7.1, k="floor", tile="300x600", en="Bath 2 floor, if not counted above.", hi="बाथ 2 का फ़र्श, अगर ऊपर नहीं गिना।"),
 dict(t="Skirting (running ft)", a=150, b=0.33, k="wall", tile="600x1200", en="4-inch skirting cut from the floor tile along every room wall; about 150 running ft.", hi="हर कमरे की दीवार के साथ फ़र्श की टाइल से कटी 4 इंच स्कर्टिंग; लगभग 150 रनिंग फ़ुट।"),
]
SIZES = {"600x1200": [2, 15.5, "2 × 4 ft"], "600x600": [4, 15.5, "2 × 2 ft"], "800x1600": [2, 27.6, "2.6 × 5.2 ft"], "300x600": [8, 15.5, "1 × 2 ft"], "300x300": [10, 9.7, "1 × 1 ft"]}

SRC = [["https://www.studiomatrx.org/guides/gvt-vs-pgvt-india", "GVT vs PGVT (Studio Matrx)", "GVT बनाम PGVT (Studio Matrx)"],
       ["https://www.orientbell.com/tile-guide/tile-price-per-square-foot-india", "Tile prices per sq ft (Orientbell, May 2026)", "टाइल के दाम प्रति वर्ग फ़ुट (Orientbell, मई 2026)"],
       ["https://materialdepot.com/qna/what-sets-gvt-tiles-apart-from-vitrified-tiles-tiles", "GVT, PGVT, double-charge, full-body: the difference", "GVT, PGVT, डबल-चार्ज, फ़ुल-बॉडी: अंतर"],
       ["https://www.studiomatrx.org/guides/double-charged-vitrified-tiles-india", "Double-charge vitrified tiles", "डबल-चार्ज विट्रीफाइड टाइल"],
       ["https://www.studiomatrx.org/guides/granite-flooring-india", "Granite in India: types and prices", "भारत में ग्रेनाइट: प्रकार और दाम"],
       ["https://www.studiomatrx.org/guides/granite-vs-vitrified-tiles-india", "Granite vs vitrified tiles", "ग्रेनाइट बनाम विट्रीफाइड टाइल"],
       ["https://materialdepot.com/qna/how-much-extra-should-i-account-for-wastage-when-making-a-purchase-tiles", "How much extra tile to buy", "कितनी अतिरिक्त टाइल लें"],
       ["https://www.youtube.com/watch?v=aWRHGDvTzXc", "▶ Video: laying vitrified floor tiles", "▶ वीडियो: विट्रीफाइड फ़र्श टाइल लगाना"],
       ["https://www.youtube.com/watch?v=YcOsKoWAjyY", "▶ Video: tile adhesive vs cement", "▶ वीडियो: टाइल एडहेसिव बनाम सीमेंट"]]
L = lambda i, lang: [[u, (e if lang == 0 else h)] for (u, e, h) in [SRC[j] for j in i]]

def cards(lang):
    E = lang == 0
    t = lambda en, hi: en if E else hi
    return [
     dict(h=t("Tile words, in simple terms", "टाइल के शब्द, आसान भाषा में"),
          p=[t("Almost every Indian floor today is <b>vitrified tile</b>: clay and glass powder fired at about 1,200 °C until it hardly soaks up water. The names differ in <b>where the pattern is</b> and <b>how shiny</b> the top is.",
               "आज लगभग हर भारतीय फ़र्श <b>विट्रीफाइड टाइल</b> है: मिट्टी और काँच का पाउडर लगभग 1,200 °C पर पका, जो पानी लगभग नहीं सोखता। नामों में फ़र्क है कि <b>डिज़ाइन कहाँ है</b> और ऊपर <b>कितनी चमक</b> है।")],
          table=[[t("Name", "नाम"), t("What it really is", "असल में क्या है"), t("₹ / sq ft (tile only)", "₹ / वर्ग फ़ुट (सिर्फ़ टाइल)")],
                 [t("Ceramic", "सिरेमिक"), t("Softer clay tile; walls and budget floors", "नरम मिट्टी की टाइल; दीवार और सस्ते फ़र्श"), "₹20–50"],
                 [t("Double-charge", "डबल-चार्ज"), t("Colour pressed 3–4 mm deep; very tough, few designs", "रंग 3–4 mm गहराई तक दबाया; बहुत मज़बूत, डिज़ाइन कम"), "₹45–90"],
                 [t("GVT (matt / satin)", "GVT (मैट / साटिन)"), t("Printed design under a glaze; huge choice, not slippery in matt", "ग्लेज़ के नीचे छपा डिज़ाइन; बहुत विकल्प, मैट में फिसलन कम"), "₹40–100"],
                 [t("PGVT (glossy)", "PGVT (चमकदार)"), t("GVT polished to a mirror shine; marble look, slippery when wet, shows scratches", "GVT पर शीशे जैसी पॉलिश; मार्बल जैसा, गीले में फिसलन, खरोंच दिखती है"), "₹50–160"],
                 [t("Full-body", "फ़ुल-बॉडी"), t("Same colour through the whole thickness; chips hardly show", "पूरी मोटाई में एक रंग; टूट-फूट मुश्किल से दिखती है"), t("more than double-charge", "डबल-चार्ज से ज़्यादा")],
                 [t("Big slab (800×1600)", "बड़ी स्लैब (800×1600)"), t("Very few joints, luxury look; needs skilled laying", "बहुत कम जोड़, शानदार; कुशल मिस्त्री चाहिए"), "₹80–180"],
                 [t("Anti-skid (R10/R11)", "एंटी-स्किड (R10/R11)"), t("Rough matt surface for bathrooms", "बाथरूम के लिए खुरदुरी मैट सतह"), "₹35–65"],
                 [t("Granite", "ग्रेनाइट"), t("Natural hard stone, 16–20 mm slabs", "प्राकृतिक सख़्त पत्थर, 16–20 mm स्लैब"), "₹60–300"],
                 [t("Kota stone", "कोटा स्टोन"), t("Grey-green natural limestone; outdoor, not slippery", "हरा-ग्रे प्राकृतिक पत्थर; बाहर के लिए, फिसलन कम"), t("cheap", "सस्ता")],
                 [t("Marble", "मार्बल"), t("Natural stone, beautiful, stains and needs polishing", "प्राकृतिक पत्थर, सुंदर, दाग लगते हैं, पॉलिश चाहिए"), t("varies widely", "बहुत अलग-अलग")]],
          notes=[t("Prices are material only from 2025–26 Indian guides; laying adds about ₹15–40 per sq ft, adhesive ₹10–30. Add 18% GST.", "दाम 2025–26 की भारतीय गाइड से, सिर्फ़ माल; लगवाई ₹15–40 प्रति वर्ग फ़ुट, एडहेसिव ₹10–30। 18% GST जोड़ें।")],
          links=L([0, 2, 1], lang)),
     dict(h=t("What we chose, room by room, and why", "हमने क्या चुना, कमरे के हिसाब से, और क्यों"),
          table=[[t("Place", "जगह"), t("Our choice", "हमारी पसंद"), t("Why", "क्यों")],
                 [t("Hall + passage", "हॉल + पैसेज"), t("Matt GVT, 600×1200 (2 × 4 ft), warm light shade", "मैट GVT, 600×1200 (2 × 4 फ़ुट), हल्का गर्म शेड"), t("Big room: big tiles mean fewer joints and a calmer look. Matt is not slippery and hides footprints; PGVT shines but is slippery and scratches.", "बड़ा कमरा: बड़ी टाइल मतलब कम जोड़, शांत लुक। मैट फिसलता नहीं और पैरों के निशान छिपाता है; PGVT चमकता है पर फिसलन और खरोंच।")],
                 [t("Room 1, Room 2, kitchen floor", "कमरा 1, कमरा 2, रसोई फ़र्श"), t("Same matt GVT in 600×600 (2 × 2 ft)", "वही मैट GVT, 600×600 (2 × 2 फ़ुट)"), t("Smaller rooms: less cutting and waste; same shade so the flat feels connected.", "छोटे कमरे: कम कटाई, कम बर्बादी; एक ही शेड से पूरा फ़्लैट जुड़ा लगता है।")],
                 [t("Bathrooms floor", "बाथरूम फ़र्श"), t("Anti-skid R11, 300×600 + epoxy grout", "एंटी-स्किड R11, 300×600 + एपॉक्सी ग्राउट"), t("Safety for parents on wet floors; epoxy grout doesn't turn black or let water through.", "गीले फ़र्श पर माता-पिता की सुरक्षा; एपॉक्सी ग्राउट काला नहीं होता, पानी नहीं जाने देता।")],
                 [t("Bathroom walls", "बाथरूम दीवारें"), t("Matt wall tile 300×600, up to 7 ft", "मैट वॉल टाइल 300×600, 7 फ़ुट तक"), t("Full splash height, easy to wipe.", "पूरी छींटे वाली ऊँचाई, पोंछना आसान।")],
                 [t("Kitchen walls", "रसोई दीवारें"), t("Wall tile 300×600 above the counter (2 ft band) or to 6 ft", "काउंटर के ऊपर 2 फ़ुट पट्टी या 6 फ़ुट तक वॉल टाइल"), t("Oil and steam wipe off. The band is cheaper; 6 ft (Papa's plan) is easier to keep clean.", "तेल-भाप पोंछ जाती है। पट्टी सस्ती; 6 फ़ुट (पापा का प्लान) साफ़ रखना आसान।")],
                 [t("Kitchen counter, stair, sills, thresholds", "रसोई काउंटर, सीढ़ी, सिल, चौखट"), t("Granite", "ग्रेनाइट"), t("Hardest common stone: heat, knives and feet don't hurt it.", "सबसे सख़्त आम पत्थर: गर्मी, चाकू और पैरों से ख़राब नहीं।")],
                 [t("Balcony, open square", "बालकनी, खुला आँगन"), t("Kota stone", "कोटा स्टोन"), t("Cheap, outdoor-proof, not slippery in rain.", "सस्ता, बाहर टिकाऊ, बारिश में फिसलन कम।")],
                 [t("Skirting", "स्कर्टिंग"), t("4 inch, cut from the floor tile", "4 इंच, फ़र्श की टाइल से कटी"), t("Protects the wall from mop water and kicks; matches the floor.", "पोंछे के पानी और ठोकर से दीवार बचती है; फ़र्श से मेल।")]],
          notes=[t("Not chosen: PGVT (slippery, scratches), marble (stains, upkeep), plain ceramic on floors (chips), wooden-look tiles in bathrooms.", "नहीं चुना: PGVT (फिसलन, खरोंच), मार्बल (दाग, देखभाल), फ़र्श पर सादा सिरेमिक (टूटता है), बाथरूम में लकड़ी-लुक टाइल।")],
          links=[]),
     dict(h=t("Comparison with my ratings", "तुलना और मेरी रेटिंग"),
          p=[t("Out of 5 for your flat. Higher is better (for 'slippery', higher means safer).", "आपके फ़्लैट के लिए 5 में से। ज़्यादा बेहतर ('फिसलन' में ज़्यादा = सुरक्षित)।")],
          table=[[t("Option", "विकल्प"), t("Looks", "लुक"), t("Safe when wet", "गीले में सुरक्षित"), t("Scratch / chip", "खरोंच / टूट"), t("Easy cleaning", "सफ़ाई"), t("Cost", "दाम"), t("Hall", "हॉल")],
                 ["Matt GVT", "4", "4", "3", "4", "4", "★ 4.5"], ["PGVT", "5", "2", "2", "3", "3", "3"], [t("Double-charge", "डबल-चार्ज"), "3", "3", "5", "4", "4", "3.5"],
                 [t("Full-body", "फ़ुल-बॉडी"), "3", "4", "5", "4", "3", "4"], [t("Big slab", "बड़ी स्लैब"), "5", "3", "3", "5", "2", "3.5"], [t("Granite floor", "ग्रेनाइट फ़र्श"), "4", "2", "5", "4", "2", "3"],
                 [t("Marble", "मार्बल"), "5", "2", "2", "2", "2", "2.5"], [t("Ceramic", "सिरेमिक"), "2", "3", "2", "3", "5", "2"]],
          notes=[t("If money is tight in the hall, double-charge 600×600 is the tough budget option; full-body is the 'never shows a chip' upgrade.", "हॉल में पैसे कम हों तो डबल-चार्ज 600×600 मज़बूत सस्ता विकल्प; फ़ुल-बॉडी 'टूट कभी न दिखे' वाला अपग्रेड।")],
          links=L([3, 5], lang)),
     dict(h=t("Granite: where it goes (the '3' places)", "ग्रेनाइट: कहाँ लगेगा ('3' जगहें)"),
          p=[t("Papa's 'ग्रेनाइट 3' most likely means the usual three granite jobs: <b>1. kitchen counter</b>, <b>2. stair steps</b>, <b>3. window sills and door thresholds</b>. (If he meant 3 slabs or 3 ft, the calculator below still works: add a line.)",
               "पापा का 'ग्रेनाइट 3' शायद ग्रेनाइट की आम तीन जगहें हैं: <b>1. रसोई काउंटर</b>, <b>2. सीढ़ी</b>, <b>3. खिड़की की सिल और दरवाज़े की चौखट</b>। (अगर उनका मतलब 3 स्लैब या 3 फ़ुट था, नीचे के कैलकुलेटर में लाइन जोड़ें।)")],
          table=[[t("Granite", "ग्रेनाइट"), t("Looks", "लुक"), t("₹ / sq ft", "₹ / वर्ग फ़ुट"), t("Best for", "किसके लिए")],
                 [t("Black Galaxy", "ब्लैक गैलेक्सी"), t("Black with gold flecks; hides crumbs and water marks", "सुनहरे कण वाला काला; टुकड़े और पानी के निशान छिपाता है"), "₹120–300", t("Kitchen counter ★", "रसोई काउंटर ★")],
                 [t("Absolute / Jet black", "एब्सोल्यूट / जेट ब्लैक"), t("Plain deep black; shows dust and water spots", "सादा गहरा काला; धूल और पानी के धब्बे दिखते हैं"), "₹110–300", t("Counter, sills", "काउंटर, सिल")],
                 [t("Tan Brown", "टैन ब्राउन"), t("Brown with black-red grains", "काले-लाल दानों वाला भूरा"), "₹60–150", t("Stairs, counters", "सीढ़ी, काउंटर")],
                 [t("Steel Grey", "स्टील ग्रे"), t("Grey with dark dots; modern", "गहरे बिंदुओं वाला ग्रे; मॉडर्न"), "₹60–140", t("Stairs, thresholds", "सीढ़ी, चौखट")],
                 [t("Local grey / green", "लोकल ग्रे / हरा"), t("Plain, cheapest", "सादा, सबसे सस्ता"), "₹50–90", t("Sills, utility", "सिल, यूटिलिटी")]],
          notes=[t("Ask for 18–20 mm thickness, a polished and rounded front edge, and a flamed or leather (non-shiny) finish on stair treads so they're not slippery. Seal the kitchen counter every 1–3 years.",
                   "18–20 mm मोटाई, आगे का किनारा पॉलिश और गोल माँगें; सीढ़ी पर फ़्लेम्ड या लेदर (बिना चमक) फ़िनिश ताकि फिसलन न हो। रसोई काउंटर हर 1–3 साल में सील करें।")],
          links=L([4], lang)),
     dict(h=t("Papa's measurement list: what it means", "पापा की नाप की सूची: इसका मतलब"),
          p=[t("Each line is <b>length × width in feet</b> for a floor, or <b>running length × tiling height</b> for walls. Below, each line is read against our measured plan. Edit any number, the tile size or the pieces per box (check the box label); totals add <b>10% for cutting and breakage</b> and round up to full boxes.",
               "हर लाइन फ़र्श के लिए <b>लंबाई × चौड़ाई (फ़ुट)</b> है, या दीवार के लिए <b>रनिंग लंबाई × टाइल की ऊँचाई</b>। नीचे हर लाइन हमारे नापे प्लान से मिलाई गई है। कोई भी नंबर, टाइल साइज़ या एक डिब्बे में टुकड़े बदलें (डिब्बे का लेबल देखें); कुल में <b>10% कटाई-टूट</b> जुड़ती है और पूरे डिब्बे तक बढ़ाया जाता है।")],
          calc=True,
          notes=[t("Improvements to the list: (1) add the hall and passage, the biggest area; (2) say which bedroom is 12×19; (3) add the second small bathroom; (4) for walls, subtract doors and windows (a door is about 3 × 7 = 21 sq ft); (5) add skirting; (6) buy all boxes of one tile from the same batch and keep one spare box.",
                   "सूची में सुधार: (1) हॉल और पैसेज जोड़ें, सबसे बड़ा हिस्सा; (2) बताएँ 12×19 कौन सा बेडरूम है; (3) दूसरा छोटा बाथरूम जोड़ें; (4) दीवारों में दरवाज़े-खिड़की घटाएँ (एक दरवाज़ा लगभग 3 × 7 = 21 वर्ग फ़ुट); (5) स्कर्टिंग जोड़ें; (6) एक टाइल के सारे डिब्बे एक ही बैच के लें और एक डिब्बा अतिरिक्त रखें।")],
          links=L([6], lang)),
     dict(h=t("Buying and laying: checklist", "ख़रीद और लगवाई: चेकलिस्ट"),
          ul=[t("Same <b>batch / shade code</b> on every box of one tile (printed on the box). Different batches differ in colour.", "एक टाइल के हर डिब्बे पर एक ही <b>बैच / शेड कोड</b> (डिब्बे पर छपा)। अलग बैच का रंग अलग होता है।"),
              t("Open 2–3 boxes at the shop: look for chips, warped tiles and size differences.", "दुकान पर 2–3 डिब्बे खोलें: टूटी, टेढ़ी और अलग साइज़ की टाइल देखें।"),
              t("Big tiles on <b>tile adhesive</b>, not a thick cement bed, with levelling clips and 2–3 mm spacers.", "बड़ी टाइल <b>टाइल एडहेसिव</b> पर, मोटे सीमेंट बेड पर नहीं; लेवलिंग क्लिप और 2–3 mm स्पेसर के साथ।"),
              t("Bathrooms: waterproofing + 24-hour water test first, floor sloped to the drain, epoxy grout.", "बाथरूम: पहले वॉटरप्रूफ़िंग + 24 घंटे पानी टेस्ट, नाली की ओर ढलान, एपॉक्सी ग्राउट।"),
              t("Tap test with a coin before the final payment: a hollow 'tuk' means air under the tile.", "आख़िरी भुगतान से पहले सिक्के से ठोककर जाँचें: खोखली 'टुक' मतलब टाइल के नीचे हवा।"),
              t("Keep 1 spare box of every tile for future repairs; the same design may not be available later.", "भविष्य की मरम्मत के लिए हर टाइल का 1 डिब्बा रखें; बाद में वही डिज़ाइन शायद न मिले।")],
          links=L([7, 8], lang)),
    ]

def apply(path, lang):
    g = json.load(open(path)); ui = g["pages"]["ui"]
    tab = ["tiles", "Tiles & stone" if lang == 0 else "टाइल और पत्थर"]
    tabs = [x for x in ui["tabs"] if x[0] != "tiles"]
    i = next(k for k, x in enumerate(tabs) if x[0] == "floorpaint") + 1
    tabs.insert(i, tab); ui["tabs"] = tabs
    g["pages"]["tiles"] = cards(lang)
    g["pages"]["tilecalc"] = dict(rows=[dict(r, note=(r["en"] if lang == 0 else r["hi"])) for r in PAPA],
                                  extra=[dict(r, note=(r["en"] if lang == 0 else r["hi"])) for r in MISSING], sizes=SIZES,
                                  ui=(dict(line="Papa wrote", len="L ft", wid="W / H ft", area="sq ft", tile="Tile", per="pcs/box", boxes="boxes", meaning="Our reading", floor="Floor", wall="Wall",
                                           total="Papa's list, with 10% extra", total2="Including the missing lines", add="+ Add a line", missing="Missing from the list (suggested)")
                                      if lang == 0 else
                                      dict(line="पापा ने लिखा", len="लं. फ़ुट", wid="चौ. / ऊँ. फ़ुट", area="वर्ग फ़ुट", tile="टाइल", per="टुकड़े/डिब्बा", boxes="डिब्बे", meaning="हमारी समझ", floor="फ़र्श", wall="दीवार",
                                           total="पापा की सूची, 10% अतिरिक्त के साथ", total2="छूटी लाइनों के साथ कुल", add="+ लाइन जोड़ें", missing="सूची में छूटा (सुझाव)")))
    json.dump(g, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, [x[0] for x in ui["tabs"]])

apply("models/learn_guide.json", 0)
apply("models/learn_guide_hi.json", 1)

# learn.js: generic card renderer for 'tiles' + the calculator (once)
CALC = r"""  function calcHTML() {
    const c = guide.pages.tilecalc; if (!c) return '';
    const U2 = c.ui, sizes = Object.keys(c.sizes);
    const row = (r, i, extra) => `<div class="tc-row ${extra ? 'extra' : ''}" data-i="${i}" data-x="${extra ? 1 : 0}"><div class="tc-h"><b>${esc(r.t)}</b><span class="tc-res"></span></div>
      <div class="tc-in"><label>${esc(U2.len)} <input type="number" step="0.25" min="0" value="${r.a}" data-f="a"></label> × <label>${esc(U2.wid)} <input type="number" step="0.25" min="0" value="${r.b}" data-f="b"></label>
      <select data-f="k"><option value="floor" ${r.k === 'floor' ? 'selected' : ''}>${esc(U2.floor)}</option><option value="wall" ${r.k === 'wall' ? 'selected' : ''}>${esc(U2.wall)}</option></select>
      <select data-f="tile">${sizes.map((z) => `<option value="${z}" ${z === r.tile ? 'selected' : ''}>${z} (${c.sizes[z][2]})</option>`).join('')}</select>
      <label>${esc(U2.per)} <input type="number" min="1" value="${c.sizes[r.tile][0]}" data-f="per" class="sm"></label></div>
      <div class="tc-nt">${esc(r.note)}</div></div>`;
    return `<div class="tcalc">${c.rows.map((r, i) => row(r, i)).join('')}<div class="tc-tot" data-w="0"></div>
      <div class="tc-sep">${esc(U2.missing)}</div>${c.extra.map((r, i) => row(r, 100 + i, true)).join('')}<div class="tc-tot" data-w="1"></div></div>`;
  }
  function wireCalc(body) {
    const c = guide.pages.tilecalc, box = body.querySelector('.tcalc'); if (!c || !box) return;
    const upd = () => {
      const S = [{ fl: 0, wl: 0, by: {} }, { fl: 0, wl: 0, by: {} }];
      box.querySelectorAll('.tc-row').forEach((tr) => {
        const v = (f) => tr.querySelector(`[data-f="${f}"]`).value;
        const area = (+v('a') || 0) * (+v('b') || 0), z = v('tile'), per = +v('per') || 1, pc = c.sizes[z][1] / c.sizes[z][0];
        const need = area * 1.1 / (pc * per);
        tr.querySelector('.tc-res').textContent = area ? `${area.toFixed(0)} ${c.ui.area} → ${Math.ceil(need)} ${c.ui.boxes}` : '';
        for (const k of (tr.dataset.x === '1' ? [1] : [0, 1])) { const t = S[k]; if (v('k') === 'floor') t.fl += area; else t.wl += area; t.by[z] = (t.by[z] || 0) + need; }
      });
      box.querySelectorAll('.tc-tot').forEach((el) => { const t = S[+el.dataset.w];
        el.innerHTML = `<b>${esc(el.dataset.w === '1' ? c.ui.total2 : c.ui.total)}:</b> ${esc(c.ui.floor)} ${Math.round(t.fl * 1.1)} · ${esc(c.ui.wall)} ${Math.round(t.wl * 1.1)} ${esc(c.ui.area)}<br>` +
          Object.entries(t.by).map(([k, n]) => `${esc(k)} (${esc(c.sizes[k][2])}): <b>${Math.ceil(n)}</b> ${esc(c.ui.boxes)}`).join(' · '); });
    };
    box.querySelectorAll('input, select').forEach((el) => el.addEventListener('input', (e) => {
      if (e.target.dataset.f === 'tile') { const tr = e.target.closest('.tc-row'); tr.querySelector('[data-f="per"]').value = c.sizes[e.target.value][0]; }
      upd();
    }));
    upd();
  }
"""
p = "src/learn.js"; s = open(p).read()
if "renderTiles" in s and "tc-row" not in s:
    a0 = s.index("  function calcHTML() {"); a1 = s.index("  function renderCeiling() {")
    s = s[:a0] + CALC + s[a1:]; open(p, "w").write(s); print("calc replaced")
if "renderTiles" not in s:
    s = s.replace("  function renderCeiling() {", """  function renderTiles() {
    const saved = guide.pages.ceiling; guide.pages.ceiling = guide.pages.tiles || [];
    const h = renderCeiling(); guide.pages.ceiling = saved; return h;
  }
""" + CALC + """  function renderCeiling() {""", 1)
    s = s.replace("(b.notes || []).map(n => `<p class=\"where\">${n}</p>`).join('') +\n      ((b.links || []).length", "(b.calc ? calcHTML() : '') + (b.notes || []).map(n => `<p class=\"where\">${n}</p>`).join('') +\n      ((b.links || []).length", 1)
    s = s.replace("ceiling: renderCeiling, steps:", "tiles: renderTiles, ceiling: renderCeiling, steps:", 1)
    s = s.replace("    body.querySelectorAll('.showme').forEach(", "    wireCalc(body);\n    body.querySelectorAll('.showme').forEach(", 1)
    assert "tiles: renderTiles" in s and "(b.calc ? calcHTML()" in s and "wireCalc(body);" in s
    open(p, "w").write(s); print("learn.js patched")
c = "src/styles.css"; css = open(c).read()
if ".tc-row" not in css:
    css = css.split("/* ---- Learn: tile calculator")[0].rstrip() + "\n"
if ".tc-row" not in css:
    css += """
/* ---- Learn: tile calculator (20 Nov 2026) ---- */
#learn .tcalc { display: grid; gap: 6px; margin: 6px 0; }
#learn .tc-row { border: 1px solid #eadfcb; border-radius: 8px; padding: 6px 8px; background: #fff; }
#learn .tc-row.extra { background: #fbf7ee; border-style: dashed; }
#learn .tc-h { display: flex; justify-content: space-between; gap: 8px; font-size: 13px; }
#learn .tc-res { font-weight: 700; color: #1f6f54; white-space: nowrap; font-variant-numeric: tabular-nums; }
#learn .tc-in { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; margin: 4px 0; font-size: 12px; color: #666; }
#learn .tc-in input { width: 58px; padding: 2px 4px; font-size: 12.5px; border: 1px solid #d8cdb6; border-radius: 4px; }
#learn .tc-in input.sm { width: 42px; }
#learn .tc-in select { padding: 2px 4px; font-size: 12px; border: 1px solid #d8cdb6; border-radius: 4px; }
#learn .tc-nt { font-size: 12px; color: #555; }
#learn .tc-sep { font-weight: 700; color: #7a4d0f; margin-top: 6px; }
#learn .tc-tot { background: #eaf5ee; border: 1px solid #bfdcc9; border-radius: 8px; padding: 6px 9px; font-size: 12.5px; }
"""
    open(c, "w").write(css); print("css added")
