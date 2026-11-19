# Adds the "Ceiling" tab to Learn (EN + HI) and ceiling words to the Dictionary. Safe to re-run.
# Also patches src/learn.js once so the tab renders. Run from MyFlat_Viewer: python3 scripts/learn_ceiling.py
import json

SVG = """<svg viewBox="0 0 520 210" style="width:100%;max-width:560px;background:#fbf8f2;border-radius:8px" font-family="sans-serif" font-size="11">
<rect x="10" y="20" width="500" height="16" fill="#b9b4aa"/><text x="16" y="15" fill="#555">{slab}</text>
<rect x="150" y="36" width="34" height="34" fill="#a39d92"/><rect x="336" y="36" width="34" height="34" fill="#a39d92"/>
<text x="140" y="84" fill="#555">{beam}</text>
<rect x="10" y="36" width="8" height="170" fill="#d8d2c6"/><rect x="502" y="36" width="8" height="170" fill="#d8d2c6"/>
<rect x="18" y="66" width="70" height="8" fill="#fff" stroke="#999"/><rect x="432" y="66" width="70" height="8" fill="#fff" stroke="#999"/>
<line x1="40" y1="36" x2="40" y2="66" stroke="#777"/><line x1="70" y1="36" x2="70" y2="66" stroke="#777"/><line x1="480" y1="36" x2="480" y2="66" stroke="#777"/><line x1="450" y1="36" x2="450" y2="66" stroke="#777"/>
<rect x="84" y="58" width="6" height="8" fill="#f2b33d"/><rect x="430" y="58" width="6" height="8" fill="#f2b33d"/>
<path d="M90 60 Q130 45 150 40" stroke="#f2b33d" stroke-width="2" fill="none" opacity=".7"/><path d="M430 60 Q390 45 370 40" stroke="#f2b33d" stroke-width="2" fill="none" opacity=".7"/>
<circle cx="52" cy="76" r="3" fill="#f2b33d"/><circle cx="468" cy="76" r="3" fill="#f2b33d"/>
<text x="20" y="96" fill="#7a4d0f">{band}</text><text x="20" y="112" fill="#a06d00">{cove}</text>
<line x1="260" y1="36" x2="260" y2="206" stroke="#1f6f54" stroke-dasharray="4 3"/><text x="266" y="140" fill="#1f6f54">{h10}</text>
<line x1="60" y1="74" x2="60" y2="206" stroke="#7a4d0f" stroke-dasharray="2 3"/><text x="66" y="190" fill="#7a4d0f">{h9}</text>
<rect x="10" y="206" width="500" height="4" fill="#9a8f7c"/></svg>"""

EN = dict(
 tab=["ceiling", "Ceiling"],
 svg=dict(slab="concrete slab (10 ft from floor)", beam="beam, bottom at 9 ft", band="2 ft gypsum band, 8'11\"", cove="cove LED glows up", h10="middle stays 10 ft", h9="~8'11\" at the band"),
 cards=[
  dict(h="Ceiling words, in simple terms", p=["Your real ceiling is the concrete <b>slab</b>. Anything hung below it is a <b>false ceiling</b>. It is a light steel frame with boards screwed to it, with a gap above for wires. You don't have to cover the whole room: a <b>border</b> (peripheral) ceiling covers only a 1.5–2 ft band along the walls."],
       table=[["Word", "What it means"], ["False ceiling", "A second ceiling hung below the slab on steel channels"], ["Border / peripheral ceiling", "False ceiling only along the walls; the middle stays at full height"], ["Cove", "A small open lip in the false ceiling with a hidden LED strip that lights the ceiling softly"],
              ["Downlight", "Small round light set into the false ceiling, pointing down"], ["Profile light", "A thin aluminium strip light, surface-fixed or set in a groove"], ["GI channel", "Galvanised (rust-proof) steel sections that make the frame"], ["Gypsum board", "12.5 mm white board (Gyproc, USG Boral) screwed to the frame"],
              ["POP", "Plaster of Paris, poured or moulded on a mesh by hand"], ["PVC panels", "Plastic click-together strips: waterproof, cheap"], ["Beam boxing", "Wrapping an existing beam in board, often with LED along its sides"]],
       links=[["https://www.google.com/search?tbm=isch&q=peripheral+gypsum+false+ceiling+cove+light+living+room+India", "See border ceilings with cove light"], ["https://www.google.com/search?tbm=isch&q=beam+false+ceiling+design+living+room+India", "See beam ceiling designs"]]),
  dict(h="Your hall: why only a border, not a full false ceiling", p=["{SVG}", "Your hall slab is at <b>10 ft</b>, but two beams hang down to <b>9 ft</b>. A full false ceiling must pass <i>under</i> the beams, so the whole hall would drop to about <b>8'8\"</b>. That makes a big room feel squashed, and it's the most expensive choice.",
       "A <b>2 ft border</b> sits just under beam level, hides the wiring for the downlights, and its cove LED washes the middle with soft light. The beams then look like part of the design. The middle keeps its full 10 ft."],
       notes=["Too tight on money? Skip the border and just <b>box the two beams</b> with an LED strip along their sides (≈₹17k–36k)."], links=[["https://www.google.com/search?tbm=isch&q=false+ceiling+with+beam+living+room", "See ceilings built round beams"]]),
  dict(h="All the options side by side", p=["Rates are installed prices from Indian cost guides (2025–26, big cities). Local Sheikhpura rates are usually lower, so get 2–3 quotes. My rating is for <b>your</b> flat (hall / bedroom / bath, out of 10)."],
       table=[["Option", "What you get", "₹ per sq ft", "Rating H/B/Bath"], ["Plain slab + good lights", "Paint only; surface downlights or a slim panel", "₹15–30 (paint)", "6 / 9 / 7"], ["Gypsum border + cove", "Designer look, full height in the middle", "₹110–190 per sq ft of band", "9 / 6 / 1"],
              ["Beam boxing + LED", "Cheapest decorative option, uses your beams", "estimate", "8 / 3 / 1"], ["Full gypsum + cove", "Hides everything, hotel look; loses height", "₹140–210", "5 / 4 / 1"], ["POP on mesh", "Any shape; messy, can crack", "₹65–160", "6 / 4 / 1"],
              ["PVC panels", "Waterproof, cheap; looks plasticky", "₹70–160", "2 / 3 / 8"], ["Wood / WPC slats", "Rich and warm; costly, dusty grooves", "₹120–1,200", "4 / 4 / 1"], ["Metal / grid tiles", "Commercial look", "₹85–300", "2 / 1 / 6"]],
       notes=["Full comparison with pros and cons: 📊 Compare → 🏠 Ceilings."], links=[["https://www.studiomatrx.org/guides/false-ceiling-cost-guide-india", "Cost guide (Studio Matrx)"]]),
  dict(h="Can we do this after plastering? Yes", p=["<b>Yes, every ceiling option goes on after plaster.</b> A false ceiling, beam boxing or PVC panels are screwed onto the finished, plastered slab with anchor bolts. Ceiling work normally comes <b>after plaster and wiring</b>, and <b>before the final putty and paint</b>. Your plaster being done is the normal starting point.",
       "What matters is the <b>order of the other jobs</b>:"],
       table=[["Your situation", "Can we?", "What to do"], ["Plaster done, nothing else", "Yes, ideal", "Wiring and AC pipes first, then the ceiling frame, then putty and paint everywhere"], ["Fresh plaster (under 3–4 weeks)", "Wait a bit", "Let it cure and dry; boards on damp plaster grow fungus"],
              ["No wire pipes in the slab", "Yes", "Above the border, wires run in loose pipe, so no cutting. In plain rooms use a neat surface conduit painted ceiling-white, or cut only into the plaster, never into the concrete"],
              ["No fan hook in the slab", "Yes", "The electrician fixes an anchor-fastener fan hook into the slab (drill 10–12 mm). The fan always hangs from the slab, never from the false ceiling"],
              ["Walls already painted", "Yes, with care", "Ceiling work makes dust and scratches; plan one final touch-up coat after it"], ["Floor tiles already laid", "Yes", "Cover the floor with sheets or cardboard; the contractor works on scaffolding"],
              ["Damp patch or leak on the ceiling", "Fix first", "Find and repair the leak (roof, bathroom above, pipe) before covering it, or it will spread under the board"]],
       links=[["https://www.google.com/search?tbm=isch&q=anchor+fastener+fan+hook+concrete+ceiling", "See anchor-fastener fan hooks"]]),
  dict(h="How a gypsum border is made, step by step", ul=["<b>Mark</b> the level line on all walls with a laser (8'11\" for your hall).", "<b>Perimeter angle</b>: an L-shaped steel strip screwed to the walls on that line.", "<b>Hangers</b>: rods from the slab on anchor bolts, holding the GI channels.",
       "<b>Boards</b>: 12.5 mm gypsum screwed on, with the cove lip and the downlight holes cut out.", "<b>Joints</b>: paper tape + jointing compound, sanded smooth (this stops cracks).", "<b>Finish</b>: putty, primer and paint, at the same time as the walls.", "<b>Lights last</b>: LED strip and driver in the cove, downlights in their holes. Leave a small <b>access panel</b> near each driver."],
       p=["About 3–5 working days for a hall your size, plus paint time."], links=[["https://www.google.com/search?q=gypsum+false+ceiling+installation+process+video", "Watch the process (videos)"]]),
  dict(h="Mistakes to avoid", ul=["Cheap black (non-galvanised) channels: they rust and stain the board. Ask for GI.", "No access panel: when an LED driver fails you have to cut the ceiling open.", "Cove too shallow: you see a row of LED dots. Ask for a 5–6 in deep cove and a COB or diffused strip.",
       "Cool-white (6000 K) cove: looks like a shop. Use warm white 3000 K.", "Too many downlights: 8 in the hall band is enough; use separate switches for cove, downlights and the main light.", "Plain gypsum near bathrooms or the kitchen: use moisture-resistant (green) board or PVC there.",
       "Starting the ceiling before the wiring and the AC pipe are decided."], p=[], links=[]),
 ])

HI = dict(
 tab=["ceiling", "छत (सीलिंग)"],
 svg=dict(slab="कंक्रीट स्लैब (फ़र्श से 10 फीट)", beam="बीम, नीचे 9 फीट", band="2 फीट जिप्सम पट्टी, 8'11\"", cove="कोव LED ऊपर रोशनी", h10="बीच में 10 फीट", h9="पट्टी पर ~8'11\""),
 cards=[
  dict(h="छत के शब्द, आसान भाषा में", p=["आपकी असली छत कंक्रीट का <b>स्लैब</b> है। उसके नीचे लटकाई गई कोई भी छत <b>फ़ॉल्स सीलिंग</b> है: हल्का स्टील फ़्रेम जिस पर बोर्ड कसे होते हैं, ऊपर तारों के लिए खाली जगह। पूरा कमरा ढकना ज़रूरी नहीं: <b>बॉर्डर</b> (पेरिफ़ेरल) सीलिंग सिर्फ़ दीवारों के साथ 1.5–2 फीट की पट्टी होती है।"],
       table=[["शब्द", "मतलब"], ["फ़ॉल्स सीलिंग", "स्टील चैनल पर स्लैब के नीचे लटकी दूसरी छत"], ["बॉर्डर / पेरिफ़ेरल सीलिंग", "सिर्फ़ दीवारों के साथ फ़ॉल्स सीलिंग; बीच में पूरी ऊँचाई"], ["कोव", "फ़ॉल्स सीलिंग में छोटा खुला किनारा, जिसमें छिपी LED पट्टी छत को हल्की रोशनी देती है"],
              ["डाउनलाइट", "फ़ॉल्स सीलिंग में लगी छोटी गोल लाइट, नीचे की ओर"], ["प्रोफ़ाइल लाइट", "पतली एल्युमिनियम पट्टी वाली लाइट, सतह पर या खाँचे में"], ["GI चैनल", "गैल्वनाइज़्ड (जंग-रोधी) स्टील, जिससे फ़्रेम बनता है"], ["जिप्सम बोर्ड", "12.5 mm सफ़ेद बोर्ड (Gyproc, USG Boral), फ़्रेम पर कसा"],
              ["POP", "प्लास्टर ऑफ़ पेरिस, हाथ से जाली पर ढाला"], ["PVC पैनल", "प्लास्टिक की जुड़ने वाली पट्टियाँ: पानी-रोधी, सस्ती"], ["बीम बॉक्सिंग", "मौजूदा बीम को बोर्ड से ढकना, अक्सर किनारों पर LED के साथ"]],
       links=[["https://www.google.com/search?tbm=isch&q=peripheral+gypsum+false+ceiling+cove+light+living+room+India", "कोव लाइट वाली बॉर्डर सीलिंग देखें"], ["https://www.google.com/search?tbm=isch&q=beam+false+ceiling+design+living+room+India", "बीम वाली सीलिंग डिज़ाइन देखें"]]),
  dict(h="आपका हॉल: पूरी फ़ॉल्स सीलिंग नहीं, सिर्फ़ बॉर्डर क्यों", p=["{SVG}", "हॉल का स्लैब <b>10 फीट</b> पर है, पर दो बीम <b>9 फीट</b> तक नीचे हैं। पूरी फ़ॉल्स सीलिंग को बीम के <i>नीचे</i> से जाना पड़ेगा, तो पूरा हॉल लगभग <b>8'8\"</b> का हो जाएगा: बड़ा कमरा दबा हुआ लगेगा, और सबसे महँगा भी।",
       "<b>2 फीट का बॉर्डर</b> बीम के ठीक नीचे रहता है, डाउनलाइट की वायरिंग छिपाता है, और उसकी कोव LED बीच वाले हिस्से पर हल्की रोशनी डालती है। बीम डिज़ाइन का हिस्सा लगती हैं, और बीच में पूरे 10 फीट रहते हैं।"],
       notes=["पैसे कम हों? बॉर्डर छोड़ें, सिर्फ़ <b>दोनों बीम पर बॉक्स</b> और किनारों पर LED पट्टी (≈₹17k–36k)।"], links=[["https://www.google.com/search?tbm=isch&q=false+ceiling+with+beam+living+room", "बीम के साथ बनी सीलिंग देखें"]]),
  dict(h="सभी विकल्प एक साथ", p=["दाम भारतीय कॉस्ट गाइड (2025–26, बड़े शहर) से, लगवाकर। शेखपुरा में आमतौर पर कम; 2–3 कोटेशन लें। मेरी रेटिंग <b>आपके</b> फ़्लैट के लिए है (हॉल / बेडरूम / बाथ, 10 में से)।"],
       table=[["विकल्प", "क्या मिलता है", "₹ प्रति वर्ग फ़ुट", "रेटिंग हॉ/बे/बा"], ["सादा स्लैब + अच्छी लाइट", "सिर्फ़ पेंट; सतह वाली डाउनलाइट या पतला पैनल", "₹15–30 (पेंट)", "6 / 9 / 7"], ["जिप्सम बॉर्डर + कोव", "डिज़ाइनर लुक, बीच में पूरी ऊँचाई", "पट्टी के ₹110–190", "9 / 6 / 1"],
              ["बीम बॉक्स + LED", "सबसे सस्ता सजावटी, आपकी बीम का इस्तेमाल", "अनुमान", "8 / 3 / 1"], ["पूरी जिप्सम + कोव", "सब छिपे, होटल जैसा; ऊँचाई कम", "₹140–210", "5 / 4 / 1"], ["POP जाली पर", "कोई भी आकार; गंदगी, दरार", "₹65–160", "6 / 4 / 1"],
              ["PVC पैनल", "पानी-रोधी, सस्ता; प्लास्टिक जैसा", "₹70–160", "2 / 3 / 8"], ["लकड़ी / WPC पट्टियाँ", "गर्म, शानदार; महँगा, खाँचों में धूल", "₹120–1,200", "4 / 4 / 1"], ["मेटल / ग्रिड टाइल", "दफ़्तर जैसा", "₹85–300", "2 / 1 / 6"]],
       notes=["फ़ायदे-नुक़सान के साथ पूरी तुलना: 📊 तुलना → 🏠 छत।"], links=[["https://www.studiomatrx.org/guides/false-ceiling-cost-guide-india", "कॉस्ट गाइड (Studio Matrx)"]]),
  dict(h="क्या प्लास्टर के बाद यह हो सकता है? हाँ", p=["<b>हाँ, छत का हर विकल्प प्लास्टर के बाद ही लगता है।</b> फ़ॉल्स सीलिंग, बीम बॉक्स या PVC पैनल तैयार, प्लास्टर हुए स्लैब पर एंकर बोल्ट से कसे जाते हैं। छत का काम आमतौर पर <b>प्लास्टर और वायरिंग के बाद</b>, और <b>आख़िरी पुट्टी-पेंट से पहले</b> होता है। प्लास्टर हो जाना सामान्य शुरुआत है।",
       "ज़रूरी है <b>बाकी कामों का क्रम</b>:"],
       table=[["आपकी स्थिति", "हो सकता है?", "क्या करें"], ["सिर्फ़ प्लास्टर हुआ है", "हाँ, सबसे अच्छा", "पहले वायरिंग और AC पाइप, फिर सीलिंग फ़्रेम, फिर हर जगह पुट्टी-पेंट"], ["ताज़ा प्लास्टर (3–4 हफ़्ते से कम)", "थोड़ा रुकें", "सूखने दें; गीले प्लास्टर पर बोर्ड से फफूँद"],
              ["स्लैब में तार के पाइप नहीं", "हाँ", "बॉर्डर के ऊपर तार ढीले पाइप में, कोई कटाई नहीं। सादे कमरों में साफ़ सतह वाला कंड्यूट (छत के रंग में), या सिर्फ़ प्लास्टर में कटाई, कंक्रीट में कभी नहीं"],
              ["स्लैब में पंखे का हुक नहीं", "हाँ", "इलेक्ट्रीशियन स्लैब में एंकर-फ़ास्टनर हुक लगाए (10–12 mm ड्रिल)। पंखा हमेशा स्लैब से, फ़ॉल्स सीलिंग से कभी नहीं"],
              ["दीवारें पेंट हो चुकी", "हाँ, ध्यान से", "छत के काम से धूल-खरोंच; बाद में एक टच-अप कोट रखें"], ["फ़र्श की टाइल लग चुकी", "हाँ", "फ़र्श को चादर/कार्डबोर्ड से ढकें; ठेकेदार मचान पर काम करे"],
              ["छत पर सीलन या रिसाव", "पहले ठीक करें", "ढकने से पहले रिसाव (छत, ऊपर का बाथरूम, पाइप) ठीक करें, वरना बोर्ड के नीचे फैलेगा"]],
       links=[["https://www.google.com/search?tbm=isch&q=anchor+fastener+fan+hook+concrete+ceiling", "एंकर-फ़ास्टनर पंखा हुक देखें"]]),
  dict(h="जिप्सम बॉर्डर कैसे बनता है, क्रम से", ul=["<b>निशान</b>: लेज़र से सभी दीवारों पर लेवल लाइन (आपके हॉल में 8'11\")।", "<b>पेरिमीटर एंगल</b>: उस लाइन पर दीवार से कसी L-आकार की स्टील पट्टी।", "<b>हैंगर</b>: एंकर बोल्ट से स्लैब से लटकी छड़ें, जो GI चैनल पकड़ती हैं।",
       "<b>बोर्ड</b>: 12.5 mm जिप्सम कसा जाता है, कोव का किनारा और डाउनलाइट के छेद काटे जाते हैं।", "<b>जोड़</b>: पेपर टेप + जॉइंटिंग कंपाउंड, घिसकर चिकना (यही दरार रोकता है)।", "<b>फ़िनिश</b>: पुट्टी, प्राइमर, पेंट, दीवारों के साथ।", "<b>लाइट सबसे आख़िर</b>: कोव में LED पट्टी और ड्राइवर, छेदों में डाउनलाइट। हर ड्राइवर के पास छोटा <b>खोलने का ढक्कन</b>।"],
       p=["आपके हॉल जितने आकार के लिए लगभग 3–5 कामकाजी दिन, फिर पेंट का समय।"], links=[["https://www.google.com/search?q=gypsum+false+ceiling+installation+process+video", "प्रक्रिया देखें (वीडियो)"]]),
  dict(h="इन ग़लतियों से बचें", ul=["सस्ते काले (बिना गैल्वनाइज़) चैनल: जंग लगकर बोर्ड पर दाग। GI माँगें।", "खोलने का ढक्कन नहीं: LED ड्राइवर ख़राब होने पर छत काटनी पड़ेगी।", "कम गहरा कोव: LED के बिंदु दिखते हैं। 5–6 इंच गहरा कोव और COB/डिफ़्यूज़्ड पट्टी लें।",
       "ठंडी सफ़ेद (6000 K) कोव: दुकान जैसी लगती है। गर्म सफ़ेद 3000 K लें।", "बहुत ज़्यादा डाउनलाइट: हॉल की पट्टी में 8 काफ़ी; कोव, डाउनलाइट और मुख्य लाइट के अलग स्विच।", "बाथरूम या रसोई के पास साधारण जिप्सम: वहाँ नमी-रोधी (हरा) बोर्ड या PVC।",
       "वायरिंग और AC पाइप तय होने से पहले सीलिंग शुरू करना।"], p=[], links=[]),
 ])

GLOSS_EN = [
 ("Peripheral (border) ceiling", ["border ceiling"], "CEILING_BAND", "A false ceiling only along the walls, usually 1.5–2 ft wide, so the middle keeps the full height. Cheaper than a full false ceiling and still hides the wiring for the downlights."),
 ("GI channel", ["ceiling section", "perimeter angle"], None, "Galvanised (rust-proof) steel sections that form the frame of a gypsum false ceiling. They hang from the slab on rods and anchor bolts."),
 ("Anchor fastener", ["anchor bolt", "fan hook"], None, "A steel bolt that expands inside a drilled hole in concrete. Used to hang the false-ceiling frame and to fix a fan hook into a slab that has none."),
 ("Beam boxing", ["beam cladding"], None, "Wrapping an existing beam in gypsum or wood, often with an LED strip along its sides. A cheap way to make beams look designed."),
 ("Jointing tape & compound", [], None, "Paper tape and a filler paste used on gypsum-board joints. Done well, it stops the hairline cracks people complain about."),
 ("Access panel", ["service hatch"], None, "A small openable square in a false ceiling so the electrician can reach an LED driver or junction box without cutting the ceiling."),
 ("PVC ceiling panel", ["PVC false ceiling"], None, "Plastic interlocking strips used as a ceiling in bathrooms and balconies. Waterproof and cheap, but the joints show."),
]
GLOSS_HI = [
 ("पेरिफ़ेरल (बॉर्डर) सीलिंग", ["border ceiling"], "CEILING_BAND", "सिर्फ़ दीवारों के साथ, आमतौर पर 1.5–2 फीट चौड़ी फ़ॉल्स सीलिंग; बीच में पूरी ऊँचाई रहती है। पूरी फ़ॉल्स सीलिंग से सस्ती, फिर भी डाउनलाइट की वायरिंग छिपती है।"),
 ("GI चैनल", ["ceiling section", "perimeter angle"], None, "गैल्वनाइज़्ड (जंग-रोधी) स्टील, जिससे जिप्सम फ़ॉल्स सीलिंग का फ़्रेम बनता है। छड़ों और एंकर बोल्ट से स्लैब से लटकता है।"),
 ("एंकर फ़ास्टनर", ["anchor bolt", "fan hook"], None, "कंक्रीट में ड्रिल किए छेद में फैलने वाला स्टील बोल्ट। फ़ॉल्स सीलिंग फ़्रेम लटकाने और बिना हुक वाले स्लैब में पंखे का हुक लगाने में काम आता है।"),
 ("बीम बॉक्सिंग", ["beam cladding"], None, "मौजूदा बीम को जिप्सम या लकड़ी से ढकना, अक्सर किनारों पर LED पट्टी के साथ। बीम को डिज़ाइन जैसा दिखाने का सस्ता तरीका।"),
 ("जॉइंटिंग टेप और कंपाउंड", [], None, "जिप्सम बोर्ड के जोड़ों पर लगने वाला पेपर टेप और भराई का पेस्ट। सही लगे तो बाल जैसी दरारें नहीं आतीं।"),
 ("एक्सेस पैनल", ["service hatch"], None, "फ़ॉल्स सीलिंग में खुलने वाला छोटा चौकोर ढक्कन, ताकि इलेक्ट्रीशियन छत काटे बिना LED ड्राइवर या जंक्शन बॉक्स तक पहुँचे।"),
 ("PVC सीलिंग पैनल", ["PVC false ceiling"], None, "बाथरूम और बालकनी की छत के लिए प्लास्टिक की जुड़ने वाली पट्टियाँ। पानी-रोधी और सस्ती, पर जोड़ दिखते हैं।"),
]

def apply(path, D, gloss, grpLabel):
    g = json.load(open(path))
    pages, ui = g["pages"], g["pages"]["ui"]
    tabs = [t for t in ui["tabs"] if t[0] != "ceiling"]
    i = next(k for k, t in enumerate(tabs) if t[0] == "floorpaint") + 1
    tabs.insert(i, D["tab"]); ui["tabs"] = tabs
    svg = SVG.format(**D["svg"])
    pages["ceiling"] = [dict(c, p=[x.replace("{SVG}", svg) for x in c.get("p", [])]) for c in D["cards"]]
    names = {t[0] for t in gloss}
    g["glossary"] = [t for t in g["glossary"] if t["term"] not in names]
    for term, aka, match, plain in gloss:
        q = term.split("(")[0].strip().replace(" ", "+")
        g["glossary"].append(dict(term=term, plain=plain, match=match, aka=aka, group="Ceiling", groupLabel=grpLabel,
            img="https://www.google.com/search?tbm=isch&q=" + (aka[0] if aka else term).replace(" ", "+") + "+false+ceiling+India", wiki=None))
    json.dump(g, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "tabs", [t[0] for t in ui["tabs"]], "cards", len(pages["ceiling"]))

hiLabel = next((t["groupLabel"] for t in json.load(open("models/learn_guide_hi.json"))["glossary"] if t["group"] == "Ceiling"), "छत")
apply("models/learn_guide.json", EN, GLOSS_EN, "Ceiling")
apply("models/learn_guide_hi.json", HI, GLOSS_HI, hiLabel)

# learn.js: generic card renderer for the new tab (once)
p = "src/learn.js"; s = open(p).read()
if "renderCeiling" not in s:
    s = s.replace("  function renderSteps() {", """  function renderCeiling() {
    return (guide.pages.ceiling || []).map(b => `<div class="lcard"><h4>${esc(b.h)}</h4>` + (b.p || []).map(p => `<p>${p}</p>`).join('') +
      (b.ul ? `<ul>${b.ul.map(x => `<li>${x}</li>`).join('')}</ul>` : '') +
      (b.table ? `<div class="ctable"><table class="ftable">${b.table.map((r, i) => `<tr>${r.map(c => i === 0 ? `<th>${esc(c)}</th>` : `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>` : '') +
      (b.notes || []).map(n => `<p class="where">${n}</p>`).join('') +
      ((b.links || []).length ? `<div class="lrow">${b.links.map(([u, t]) => `<a class="small lbtn" href="${esc(u)}" target="_blank" rel="noopener">🖼 ${esc(t)}</a>`).join('')}</div>` : '') + `</div>`).join('');
  }
  function renderSteps() {""", 1)
    s = s.replace("floorpaint: renderFloorPaint, steps: renderSteps,", "floorpaint: renderFloorPaint, ceiling: renderCeiling, steps: renderSteps,", 1)
    assert "ceiling: renderCeiling" in s
    open(p, "w").write(s); print("learn.js patched")
