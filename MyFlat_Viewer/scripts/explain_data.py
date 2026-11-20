# Plain-language explanations + video/article links for every layer kind in the "What's inside" layer cards (20 Nov 2026).
# Video/article links were checked on 20 Nov 2026 (open and on-topic). "More videos" opens a YouTube search, which never goes stale.
# Run from MyFlat_Viewer: python3 scripts/explain_data.py models  -> models/explain.json
import json, os, sys, urllib.parse
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
def P(en, hi): return [en, hi]
def V(name, url): return dict(t="video", n=name, url=url)
def A(name, url): return dict(t="article", n=name, url=url)
def YT(q): return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)

K = {}
K["putty"] = dict(
 simple=P("Think of it as the 'smoothing cream' for a wall. Cement plaster is rough like sandpaper, with tiny holes and waves. Putty is a fine white paste (white cement + polymer) spread thin with a steel blade and sanded smooth. Paint only shows what is under it, so putty is what makes a wall look glass-smooth instead of grainy.",
          "इसे दीवार की 'चिकनी करने वाली क्रीम' समझें। सीमेंट प्लास्टर रेगमाल जैसा खुरदुरा होता है, छोटे छेद और लहरें। पुट्टी बारीक सफ़ेद पेस्ट (सफ़ेद सीमेंट + पॉलिमर) है जो स्टील की पत्ती से पतली फैलाकर रेगमाल से घिसी जाती है। पेंट नीचे की सतह ही दिखाता है, इसलिए दीवार शीशे जैसी चिकनी पुट्टी से बनती है।"),
 why=P("Why 2 coats? The 1st coat fills the holes and dips; the 2nd, thinner coat at right angles levels it out. Each coat is kept under about 1.5 mm, because one thick coat cracks and peels.",
       "2 कोट क्यों? पहला कोट छेद और गड्ढे भरता है; दूसरा, पतला कोट उल्टी दिशा में लगकर सतह बराबर करता है। हर कोट लगभग 1.5 mm से कम, क्योंकि एक मोटा कोट फटता और उखड़ता है।"),
 how=[P("Plaster must be dry (about 3–4 weeks old); wet the wall lightly", "प्लास्टर सूखा हो (लगभग 3–4 हफ़्ते पुराना); दीवार हल्की गीली करें"), P("Coat 1 with a steel blade, let it dry 4–6 hours", "स्टील पत्ती से पहला कोट, 4–6 घंटे सूखने दें"),
      P("Coat 2 across the first one, dry overnight", "पहले के आड़े दूसरा कोट, रात भर सूखने दें"), P("Sand with fine paper (180–220), dust off, then primer", "बारीक रेगमाल (180–220) से घिसें, धूल हटाएँ, फिर प्राइमर")],
 check=P("Shine a mobile torch sideways along the wall: waves and blade marks show up as shadows. Fix them now; after paint it's too late.",
         "मोबाइल टॉर्च दीवार के साथ तिरछी चमकाएँ: लहरें और पत्ती के निशान छाया में दिखते हैं। अभी ठीक कराएँ; पेंट के बाद देर हो जाती है।"),
 note=P("Brands differ on order: Asian Paints shows putty → primer → paint; Birla White adds a primer before the putty too. Both work; just don't skip the primer after putty.",
        "क्रम पर ब्रांड अलग कहते हैं: Asian Paints पुट्टी → प्राइमर → पेंट; Birla White पुट्टी से पहले भी प्राइमर। दोनों सही; बस पुट्टी के बाद प्राइमर न छोड़ें।"),
 links=[V("Use wall putty like a pro (Hindi)", "https://www.youtube.com/watch?v=a6kYGt60Mv0"), A("Asian Paints: why primer and putty matter", "https://www.asianpaints.com/blogs/importance-of-primers-and-putty-in-painting.html"),
        A("JK Cement: wall putty types and how many coats", "https://www.jkcement.com/blog/material-guide/wall-putty-guide/"), A("Nerolac: precautions while applying putty", "https://www.nerolac.com/blog/precautions-to-take-for-applying-wall-putty")],
 yt="wall putty 2 coat kaise lagaye")
K["primer"] = dict(
 simple=P("Primer is a thin, watery first paint coat. It soaks into the putty and seals it, like a base coat under nail polish. Then the real paint sticks evenly and doesn't get sucked in patchily.",
          "प्राइमर पतला, पानी जैसा पहला कोट है। यह पुट्टी में समाकर उसे सील करता है, जैसे नेल-पॉलिश के नीचे बेस कोट। फिर असली पेंट बराबर चिपकता है और धब्बों में नहीं सोखता।"),
 why=P("Without it, paint looks blotchy, needs extra coats and peels sooner. It is cheaper than paint, so it also saves money.", "इसके बिना पेंट धब्बेदार दिखता है, ज़्यादा कोट लगते हैं और जल्दी उखड़ता है। पेंट से सस्ता है, तो पैसे भी बचाता है।"),
 how=[P("Dust off the sanded putty", "घिसी पुट्टी की धूल हटाएँ"), P("One coat by roller or brush, thinned as written on the can", "डिब्बे पर लिखे अनुसार पतला कर रोलर/ब्रश से एक कोट"), P("Let it dry 4–6 hours before paint", "पेंट से पहले 4–6 घंटे सूखने दें")],
 check=P("The whole wall should look one even, matt white. Shiny or dark patches mean those spots soaked it up and need a touch-up.", "पूरी दीवार एक जैसी मैट सफ़ेद दिखे। चमकते या गहरे धब्बे मतलब वहाँ ज़्यादा सोखा, वहाँ दोबारा लगाएँ।"),
 links=[V("How to apply interior wall primer", "https://www.youtube.com/watch?v=Jcqtw_f0dgU"), A("Birla White: putty or primer first? step by step", "https://www.birlawhite.com/en/blogs/which-comes-first-putty-or-primer-a-step-by-step-guide-to-perfect-wall-preparatio")],
 yt="wall primer before paint process")
K["paint"] = dict(
 simple=P("Emulsion is the coloured paint you actually see: water-based, so it dries fast and doesn't smell much. Two coats give full, even colour; washable grades let you wipe stains off.",
          "इमल्शन वह रंगीन पेंट है जो दिखता है: पानी वाला, जल्दी सूखता है और कम गंध। दो कोट से पूरा, बराबर रंग आता है; धुलने वाले ग्रेड पर दाग पोंछ सकते हैं।"),
 why=P("One coat looks thin and shows the primer through. The second coat evens out the colour and roller marks.", "एक कोट पतला लगता है और प्राइमर झलकता है। दूसरा कोट रंग और रोलर के निशान बराबर करता है।"),
 how=[P("Coat 1, dry 2–4 hours", "पहला कोट, 2–4 घंटे सूखने दें"), P("Coat 2, roll top to bottom in one direction", "दूसरा कोट, एक दिशा में ऊपर से नीचे रोल करें"), P("Keep a small tin of the same batch for touch-ups", "बाद के टच-अप के लिए उसी बैच का छोटा डिब्बा रखें")],
 check=P("Look at the wall from an angle in daylight: the colour should be even, with no lap lines or roller stripes.", "दिन की रोशनी में तिरछे देखें: रंग एक जैसा, कहीं परत या रोलर की धारियाँ न हों।"),
 links=[V("Asian Paints: how to paint interior walls", "https://www.youtube.com/watch?v=HdPTB8wSW8Y")], yt="interior wall painting process putty primer emulsion")
K["plaster"] = dict(
 simple=P("Cement plaster is the 12–15 mm layer of sand + cement (1 part cement to 6 parts sand) that the mason spreads over the bricks. It makes the wall straight and protects the bricks. Damp shows here first.",
          "सीमेंट प्लास्टर ईंटों पर लगी 12–15 mm की रेत + सीमेंट (1 भाग सीमेंट, 6 भाग रेत) की परत है। यह दीवार सीधी करता है और ईंटों को बचाता है। सीलन सबसे पहले यहीं दिखती है।"),
 why=P("Bricks are uneven; plaster gives a flat base for putty and tiles.", "ईंटें ऊबड़-खाबड़ होती हैं; प्लास्टर पुट्टी और टाइल के लिए सपाट आधार देता है।"),
 how=[P("Wet the bricks so they don't suck water from the plaster", "ईंटें गीली करें ताकि प्लास्टर का पानी न सोखें"), P("Fix level dots, throw and level with a straight aluminium bar", "लेवल के निशान, मसाला फेंककर सीधी एल्युमिनियम पट्टी से बराबर"), P("Cure with water for 7–8 days", "7–8 दिन पानी से तराई करें")],
 check=P("Tap with a coin: a hollow sound means the plaster isn't stuck to the brick. Hold a long straight bar on the wall; gaps over 3 mm need fixing.", "सिक्के से ठोकें: खोखली आवाज़ मतलब प्लास्टर ईंट से नहीं चिपका। लंबी सीधी पट्टी दीवार पर रखें; 3 mm से ज़्यादा गैप ठीक कराएँ।"),
 links=[V("How to plaster a wall with cement, step by step", "https://www.youtube.com/watch?v=gV37Svo3Www"), A("UltraTech: tips for supervising plastering", "https://www.ultratechcement.com/for-homebuilders/home-building-explained-single/phase-2-articles/how-to-plaster-a-wall"),
        A("BricknBolt: 10 things to know before plastering", "https://www.bricknbolt.com/blogs-and-articles/construction-guide/top-ten-things-to-know-before-plastering-your-home")], yt="cement plaster wall process hindi")
K["brick"] = dict(
 simple=P("The actual wall. 9-inch walls are two bricks thick (outer walls); 4½-inch walls are one brick thick (inside partitions). Already built in your flat.", "असली दीवार। 9 इंच की दीवार दो ईंट मोटी (बाहरी); 4½ इंच की एक ईंट मोटी (अंदर की)। आपके फ़्लैट में बनी हुई है।"),
 why=P("It holds the wall's shape and carries shelves and TV units; heavy things should be fixed into brick, not just plaster.", "यह दीवार का आकार रखती है और शेल्फ़/TV यूनिट का भार उठाती है; भारी चीज़ें ईंट में कसें, सिर्फ़ प्लास्टर में नहीं।"),
 how=[], check=P("Before drilling, find wires: they run straight up/down from switches.", "ड्रिल से पहले तार ढूँढें: स्विच से सीधे ऊपर/नीचे जाते हैं।"), links=[], yt="brick wall construction 9 inch 4.5 inch difference")
K["concrete"] = dict(
 simple=P("RCC = concrete with steel bars (sariya) inside. Pillars, beams and the slab are RCC: they carry the whole building.", "RCC = अंदर सरिया वाला कंक्रीट। पिलर, बीम और स्लैब RCC हैं: पूरी इमारत का भार उठाते हैं।"),
 why=P("Never cut or break RCC for wires or pipes without an engineer. Small anchor holes (fan hook, false ceiling) are fine.", "इंजीनियर के बिना तार/पाइप के लिए RCC न काटें-तोड़ें। छोटे एंकर छेद (पंखा हुक, फ़ॉल्स सीलिंग) ठीक हैं।"),
 how=[], check=P("", ""), links=[A("JK Cement: what is an RCC slab", "https://www.jkcement.com/what-is-rcc-slab/")], yt="RCC slab beam column explained hindi")
K["screed"] = dict(
 simple=P("A bed of cement + sand laid on the slab to make the floor flat (and, in bathrooms, sloped to the drain). Tiles sit on it.", "स्लैब पर बिछाई सीमेंट + रेत की परत जो फ़र्श समतल करती है (बाथरूम में नाली की ओर ढलान)। टाइल इसी पर बैठती है।"),
 why=P("Slabs are never perfectly level; without a good screed tiles rock or crack.", "स्लैब कभी पूरी तरह समतल नहीं होता; अच्छे बेड के बिना टाइल हिलती या टूटती है।"),
 how=[P("Level marks, lay and compact the mortar", "लेवल निशान, मसाला बिछाकर दबाएँ"), P("Let it cure before tiling", "टाइल से पहले पकने दें")],
 check=P("Pour a little water in the bathroom: it should run to the drain, not pool.", "बाथरूम में थोड़ा पानी डालें: नाली की ओर बहे, जमा न हो।"), links=[], yt="floor screed before tiles process")
K["adhesive"] = dict(
 simple=P("Tile adhesive is a ready-mix 'glue cement' spread 3–6 mm thick with a toothed trowel. It grips tiles much better than the old thick cement bed, especially big tiles and wall tiles.",
          "टाइल एडहेसिव तैयार 'गोंद वाला सीमेंट' है जो दाँतेदार करनी से 3–6 mm फैलाया जाता है। पुराने मोटे सीमेंट बेड से बहुत अच्छा पकड़ता है, ख़ासकर बड़ी और दीवार की टाइल।"),
 why=P("Big vitrified tiles hardly absorb water, so plain cement doesn't stick well; tiles go hollow and pop. Adhesive fixes that.", "बड़ी विट्रीफाइड टाइल पानी नहीं सोखती, इसलिए सादा सीमेंट ठीक नहीं चिपकता; टाइल खोखली होकर उखड़ती है। एडहेसिव यह रोकता है।"),
 how=[P("Spread on the floor with a notched trowel", "दाँतेदार करनी से फ़र्श पर फैलाएँ"), P("Also 'back-butter' big tiles", "बड़ी टाइल के पीछे भी लगाएँ"), P("Press and tap with a rubber mallet", "दबाकर रबर हथौड़ी से ठोकें")],
 check=P("Coin-tap test after 2 days: a dull hollow sound means air under the tile.", "2 दिन बाद सिक्का टेस्ट: खोखली आवाज़ मतलब टाइल के नीचे हवा।"),
 links=[V("Tile adhesive vs cement: the difference", "https://www.youtube.com/watch?v=YcOsKoWAjyY")], yt="tile adhesive kaise lagaye")
K["tile"] = dict(
 simple=P("The finish you walk on or see. Vitrified/GVT tiles are clay fired very hot until glass-like: hard, hardly absorb water. GVT = the pattern is a printed glaze on top; full-body = the colour goes all the way through.",
          "जो दिखती है या जिस पर चलते हैं। विट्रीफाइड/GVT टाइल बहुत गर्मी में पकी मिट्टी है, काँच जैसी: सख़्त, पानी लगभग नहीं सोखती। GVT में डिज़ाइन ऊपर छपा ग्लेज़ है; फ़ुल-बॉडी में रंग पूरी मोटाई में।"),
 why=P("Easy to clean, lasts decades. Joints of 2–3 mm are filled with grout (cement or epoxy).", "साफ़ करना आसान, दशकों चलती है। 2–3 mm जोड़ ग्राउट (सीमेंट या एपॉक्सी) से भरे जाते हैं।"),
 how=[P("Check all boxes are the same batch/shade code", "सभी डिब्बे एक ही बैच/शेड कोड के हों"), P("Lay with spacers and levelling clips", "स्पेसर और लेवलिंग क्लिप से बिछाएँ"), P("Grout after 24 hours", "24 घंटे बाद ग्राउट")],
 check=P("Look along the floor at eye level: edges shouldn't stick up (lippage). Coin-tap for hollow tiles.", "आँख की ऊँचाई से फ़र्श देखें: किनारे उभरे न हों। सिक्के से खोखली टाइल जाँचें।"),
 links=[V("How to install vitrified tiles on the floor", "https://www.youtube.com/watch?v=aWRHGDvTzXc"), A("Studio Matrx: epoxy vs cement grout in India", "https://www.studiomatrx.org/guides/epoxy-grouts-and-tile-grouts-india")], yt="vitrified tile laying process")
K["membrane"] = dict(
 simple=P("A rubbery waterproof coat brushed on the bathroom floor and the lower walls before tiling, so water that seeps through grout can't reach the slab or the room below.",
          "रबर जैसा पानी-रोधी कोट जो टाइल से पहले बाथरूम के फ़र्श और नीचे की दीवारों पर ब्रश से लगता है, ताकि ग्राउट से रिसा पानी स्लैब या नीचे के कमरे तक न पहुँचे।"),
 why=P("Grout is not waterproof. Without this, damp shows on the walls next to the bathroom in a year or two.", "ग्राउट पानी-रोधी नहीं है। इसके बिना एक-दो साल में बाथरूम के पास की दीवारों पर सीलन दिखती है।"),
 how=[P("Clean surface, seal corners and pipe edges with tape", "सतह साफ़, कोनों और पाइप के किनारों पर टेप"), P("2 coats, the 2nd at right angles", "2 कोट, दूसरा आड़ा"), P("Flood test: fill 2 inches of water for 24 h before tiling", "फ़्लड टेस्ट: टाइल से पहले 24 घंटे 2 इंच पानी भरकर रखें")],
 check=P("Insist on the 24-hour water (flood) test and check the ceiling/walls below.", "24 घंटे का पानी टेस्ट ज़रूर कराएँ और नीचे की छत/दीवार देखें।"),
 links=[V("Dr. Fixit waterproofing on bathroom wall and floor before tiling", "https://www.youtube.com/watch?v=9OZ9V5xuD9U")], yt="bathroom waterproofing before tiling hindi")
K["wpc"] = dict(
 simple=P("WPC = Wood-Plastic Composite: wood powder mixed with PVC, pressed into panels with a printed wood film. Looks like wood, but water and termites can't harm it. Fluted = vertical grooves.",
          "WPC = वुड-प्लास्टिक कम्पोज़िट: लकड़ी का बुरादा + PVC, ऊपर लकड़ी की छपी फ़िल्म। लकड़ी जैसा दिखता है, पर पानी और दीमक नुकसान नहीं करते। फ़्लूटेड = खड़ी नालियाँ।"),
 why=P("Quick, clean feature wall without carpentry; light. Grooves collect dust and cheap films can fade in sun.", "बिना बढ़ईगिरी के जल्दी, साफ़ फ़ीचर वॉल; हल्का। नालियों में धूल जमती है और सस्ती फ़िल्म धूप में फीकी पड़ सकती है।"),
 how=[P("Screw battens to the wall, or glue directly on a flat wall", "दीवार पर पट्टियाँ कसें, या सपाट दीवार पर सीधे चिपकाएँ"), P("Click panels together, cover ends with trims", "पैनल एक-दूसरे में फँसाएँ, किनारों पर ट्रिम"), P("Leave a small gap for expansion", "फैलाव के लिए छोटा गैप छोड़ें")],
 check=P("Panels should be straight (use a level) with no gaps between grooves.", "पैनल सीधे हों (लेवल से जाँचें), नालियों के बीच गैप न हो।"),
 links=[V("How to install WPC fluted wall panels, step by step", "https://www.youtube.com/watch?v=cqOAkgZWy4Q")], yt="wpc fluted panel installation hindi")
K["frame"] = dict(
 simple=P("The hidden skeleton: thin steel strips (battens, GI channels) or clips that hold panels or boards a little away from the wall or ceiling.", "छिपा ढाँचा: पतली स्टील पट्टियाँ (बैटन, GI चैनल) या क्लिप जो पैनल या बोर्ड को दीवार/छत से थोड़ा दूर पकड़ती हैं।"),
 why=P("Makes a straight surface even if the wall is wavy, and leaves room for wires.", "दीवार टेढ़ी हो तब भी सीधी सतह, और तारों के लिए जगह।"),
 how=[], check=P("Ask for galvanised (GI) steel: plain black steel rusts and stains.", "गैल्वनाइज़्ड (GI) स्टील माँगें: सादा काला स्टील जंग लगकर दाग छोड़ता है।"), links=[], yt="GI channel framing false ceiling wall panel")
K["gypsum"] = dict(
 simple=P("Gypsum board is a 12.5 mm white board (gypsum between two paper sheets) screwed to a steel frame to make false ceilings and partitions.", "जिप्सम बोर्ड 12.5 mm का सफ़ेद बोर्ड (दो काग़ज़ों के बीच जिप्सम), स्टील फ़्रेम पर कसकर फ़ॉल्स सीलिंग और पार्टिशन बनते हैं।"),
 why=P("Fast, clean, fire-resistant; hides wiring for lights. Not for wet areas (use the green moisture-resistant board).", "तेज़, साफ़, आग-रोधी; लाइट की वायरिंग छिपाता है। गीली जगह के लिए नहीं (हरा नमी-रोधी बोर्ड लें)।"),
 how=[P("Frame on GI channels", "GI चैनल पर फ़्रेम"), P("Screw boards, tape and fill joints", "बोर्ड कसें, जोड़ों पर टेप और भराई"), P("Putty, primer, paint", "पुट्टी, प्राइमर, पेंट")],
 check=P("No visible joint lines after paint; a torch along the ceiling shows dips.", "पेंट के बाद जोड़ की लाइनें न दिखें; छत के साथ टॉर्च से गड्ढे दिखते हैं।"),
 links=[V("Gypsum false ceiling: installation, material, cost", "https://www.youtube.com/watch?v=Tfz2pWR8K6M")], yt="gypsum false ceiling installation hindi")
K["tape"] = dict(
 simple=P("Paper tape pressed into a filler paste over every board joint, then sanded flat.", "हर बोर्ड जोड़ पर भराई पेस्ट में दबाया काग़ज़ी टेप, फिर घिसकर सपाट।"),
 why=P("This is what stops the hairline cracks people complain about in false ceilings.", "फ़ॉल्स सीलिंग की बाल जैसी दरारें यही रोकता है।"), how=[], check=P("", ""), links=[], yt="gypsum board joint taping")
K["laminate"] = dict(
 simple=P("HPL laminate ('sunmica') is a 1 mm hard printed sheet glued onto plywood. It gives the wood look and protects from scratches and spills. A thin 'balancing' sheet on the back stops the board from bending.",
          "HPL लैमिनेट ('सनमाइका') 1 mm की सख़्त छपी शीट जो प्लाइवुड पर चिपकती है। लकड़ी जैसा लुक, खरोंच और दाग से बचाव। पीछे की पतली 'बैलेंसिंग' शीट बोर्ड को मुड़ने से रोकती है।"),
 why=P("Cheaper and tougher than real veneer; matt finishes hide fingerprints.", "असली विनियर से सस्ता और मज़बूत; मैट फ़िनिश उँगलियों के निशान छिपाती है।"),
 how=[P("Glue both faces, press evenly (roller or press)", "दोनों सतहों पर गोंद, बराबर दबाएँ (रोलर या प्रेस)"), P("Edges finished with edge-banding tape", "किनारों पर एज-बैंडिंग टेप")],
 check=P("Press with your palm across the panel: no hollow or bubbled spots.", "हथेली से पूरे पैनल को दबाएँ: कहीं खोखला या बुलबुला न हो।"),
 links=[V("How to paste laminate on plywood (avoid problems)", "https://www.youtube.com/watch?v=yVb4KJ6jT00")], yt="sunmica plywood par kaise chipkaye")
K["ply"] = dict(
 simple=P("Plywood is thin wood sheets glued in layers. BWP grade (boiling-water-proof) uses waterproof glue: it survives damp walls and kitchens. 18 mm is the usual thickness for panels and cabinets.",
          "प्लाइवुड लकड़ी की पतली परतें गोंद से जुड़ी। BWP ग्रेड (उबलते पानी-रोधी) में वॉटरप्रूफ़ गोंद: नम दीवार और रसोई में टिकता है। पैनल और कैबिनेट के लिए आमतौर पर 18 mm।"),
 why=P("MR grade is cheaper but swells if it gets wet; HDHMR is a dense board, good for dry furniture.", "MR ग्रेड सस्ता पर गीला होने पर फूलता है; HDHMR घना बोर्ड, सूखे फ़र्नीचर के लिए ठीक।"), how=[],
 check=P("Look for 'IS:710' (BWP) printed on the sheet.", "शीट पर 'IS:710' (BWP) छपा देखें।"),
 links=[A("Greenply: BWP plywood vs HDHMR", "https://www.greenply.com/blogs/bwp-plywood-vs-hdhmr-board-durability-and-water-resistance-compared")], yt="BWP vs MR plywood difference hindi")
K["glue"] = dict(
 simple=P("Contact adhesive (like Fevicol Heatx/SR) spread on both surfaces, left to get tacky, then pressed together.", "कॉन्टैक्ट गोंद (जैसे Fevicol Heatx/SR) दोनों सतहों पर, चिपचिपा होने दें, फिर दबाकर जोड़ें।"),
 why=P("Holds laminate or panels permanently; too little glue leaves hollow spots.", "लैमिनेट या पैनल पक्का पकड़ता है; कम गोंद से खोखले हिस्से रह जाते हैं।"), how=[], check=P("", ""), links=[], yt="fevicol heatx laminate pasting")
K["lime"] = dict(
 simple=P("Limewash is a natural lime paint brushed on in criss-cross strokes, giving a soft, cloudy, suede-like look instead of a flat colour.", "लाइमवॉश प्राकृतिक चूने का पेंट है जो आड़े-तिरछे ब्रश से लगता है, सपाट रंग की जगह नरम, बादल जैसा लुक।"),
 why=P("Beautiful texture and breathable; but it marks more easily and needs a special primer and skilled hands.", "सुंदर बनावट, दीवार साँस लेती है; पर निशान जल्दी पड़ते हैं और ख़ास प्राइमर व कुशल हाथ चाहिए।"),
 how=[P("Lime primer, then 2–3 thin coats with a big brush in X strokes", "लाइम प्राइमर, फिर बड़े ब्रश से X आकार में 2–3 पतले कोट")],
 check=P("Ask the painter for a 2 × 2 ft sample first: every painter's limewash looks different.", "पहले 2 × 2 फीट का सैंपल लगवाएँ: हर पेंटर का लाइमवॉश अलग दिखता है।"),
 links=[V("How to limewash interior walls", "https://www.youtube.com/watch?v=YzTSrFVJ6I0")], yt="limewash paint wall india")
K["kota"] = dict(
 simple=P("Kota is a natural grey-green limestone from Rajasthan, 20–25 mm thick. Very hard-wearing and not slippery when wet, so it's used outdoors and in utility areas.", "कोटा राजस्थान का प्राकृतिक हरा-ग्रे चूना पत्थर, 20–25 mm मोटा। बहुत टिकाऊ और गीला होने पर फिसलन कम, इसलिए बाहर और यूटिलिटी में।"),
 why=P("Cheap, lasts generations; looks plain unless polished.", "सस्ता, पीढ़ियों तक चलता है; पॉलिश बिना सादा लगता है।"), how=[P("Laid on a cement mortar bed, then machine-polished", "सीमेंट मसाले पर बिछाकर मशीन से पॉलिश")],
 check=P("", ""), links=[V("Kota stone fixing method", "https://www.youtube.com/watch?v=cUo-HcsBBFk")], yt="kota stone flooring polishing")
K["marble"] = dict(
 simple=P("Natural stone (Indian white marble, 18 mm). Beautiful and cool, but porous: lemon, oil and tea can stain it, and it needs re-polishing every few years.", "प्राकृतिक पत्थर (भारतीय सफ़ेद मार्बल, 18 mm)। सुंदर और ठंडा, पर छिद्रयुक्त: नींबू, तेल, चाय से दाग, और कुछ साल में दोबारा पॉलिश।"),
 why=P("Lasts a lifetime with care; costs more than tiles and takes longer to lay.", "देखभाल से जीवनभर; टाइल से महँगा और बिछाने में ज़्यादा समय।"), how=[], check=P("", ""), links=[], yt="marble flooring installation polishing india")
K["pipe"] = dict(
 simple=P("Electric wires run inside PVC pipes (conduits) so they can be pulled out and replaced later without breaking the wall.", "बिजली के तार PVC पाइप (कंड्यूट) के अंदर, ताकि बाद में दीवार तोड़े बिना बदले जा सकें।"),
 why=P("Never let an electrician bury bare wires in plaster.", "इलेक्ट्रीशियन को कभी खुले तार प्लास्टर में दबाने न दें।"), how=[], check=P("", ""), links=[], yt="concealed wiring conduit process")
K["gap"] = dict(simple=P("An empty space left for wires, light drivers and pipes.", "तारों, लाइट ड्राइवर और पाइप के लिए छोड़ी खाली जगह।"), why=P("", ""), how=[], check=P("", ""), links=[], yt="")

for k, v in K.items():
    if v.get("yt"): v["more"] = YT(v["yt"])
os.makedirs(OUT, exist_ok=True)
json.dump(K, open(os.path.join(OUT, "explain.json"), "w"), ensure_ascii=False, indent=1)
print("kinds", len(K))
