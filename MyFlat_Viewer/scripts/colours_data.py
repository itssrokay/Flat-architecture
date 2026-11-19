# Wall colour schemes for the "🎨 Wall colours" tool (19 Nov 2026). Brighter, family-friendly options in real Asian Paints shades.
# Hex values were read from Asian Paints' own colour-catalogue data (asianpaints.com, Nov 2026). Asian Paints says screen colours are
# indicative only: always check the shade card / a sample patch on the wall.
# Run: python3 scripts/colours_data.py models   -> models/colours.json
import json, os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
def P(en, hi): return [en, hi]
AP = "https://www.asianpaints.com/colour-catalogue/"
FAM = {"orange": "orange-wall-colours", "yellow": "yellow-wall-colours", "green": "green-wall-colours", "blue": "blue-wall-colours",
       "purple": "purple-wall-colours", "pink": "pink-wall-colours", "red": "red-wall-colours", "white": "off-white-wall-colours"}
def S(code, name, hexv, fam, slug=None, uf=None):
    slug = slug or name.lower().replace(" ", "-")
    return dict(code=code, n=name, hex=hexv, fam=fam, url=f"{AP}{FAM[uf or fam]}/{slug}.html")
SHADES = [
 # peach / orange
 S("9909", "Hint of Peach", "#FCE2CB", "orange", "hint-of-peach-n"), S("8019", "Coral Rocks", "#F7DCC6", "pink"), S("7986", "Marigold", "#FCDAB7", "orange"),
 S("7960", "Mango Shake", "#FEC882", "orange"), S("8017", "Peach Carnation", "#EFBE9F", "pink"), S("9910", "Peach Pie", "#FEBD8E", "orange", "peach-pie-n"),
 S("9936", "Peach Bellini", "#FEBC85", "orange", "peach-bellini-n"), S("8000", "Perfect Peach", "#F8B592", "orange"), S("7999", "Orange Silk", "#F0A27C", "orange"),
 S("7998", "String of Beads", "#E68D60", "orange"), S("9920", "Deccan Earth", "#D5825C", "orange", "deccan-earth-n"), S("9982", "Russet Rust", "#C05F54", "red", "russet-rust-n"),
 # yellow
 S("7865", "Wild Yellow", "#FCECB3", "yellow"), S("7912", "Yellow Tulip", "#FEE19D", "yellow"), S("7864", "Lemon Burst", "#FEE795", "yellow"),
 S("7830", "Lemonade", "#EDCD61", "yellow"), S("9874", "Tangerine Yellow", "#F2D15D", "yellow", "tangerine-yellow-n"), S("7894", "Sunny Day", "#F9C455", "yellow"),
 # green / aqua
 S("9758", "Mint Frosting", "#DEF0DB", "green", "mint-frosting-n"), S("7588", "Alpine Green", "#DDECDE", "green"), S("7516", "Fresh Mint", "#D1EBE1", "green"),
 S("7460", "Crystal River", "#D1E8E2", "green"), S("7507", "Baby Aqua", "#C2E8E2", "green"), S("7562", "Sea Nymph", "#B7D9C8", "green"),
 S("7506", "Aqua Fusion", "#A8E3DE", "green"), S("7505", "Turquoise Treat", "#84D9D5", "green"), S("7504", "Ocean Breeze", "#72CECB", "green"),
 S("7512", "Caribbean Green", "#63CCC3", "green"),
 # blue
 S("7362", "Sky Watch", "#A4D4E3", "blue"), S("7361", "Morning Frost", "#82C5DD", "blue"), S("7409", "Paradise Bay", "#7BCBDD", "blue"),
 S("9209", "Water Jet", "#78C6E6", "blue"), S("7326", "Soothing Sapphire", "#2B88BE", "blue"), S("9666", "Dal Lake Blue", "#078BBE", "blue", "dal-lake-blue-n"),
 S("9651", "Pangong Blue", "#407EB6", "blue", "pangong-blue-n"),
 # lavender / pink
 S("7147", "Lavender Laugh", "#DED6DC", "purple"), S("9609", "Lilac Tint", "#D8CDE2", "purple", "lilac-tint-n"), S("9602", "Catmint Blossom", "#CAB1DA", "purple", "catmint-blossom-n"),
 S("7112", "Wisteria", "#C8A8CF", "purple"), S("9610", "Lavender Lyric", "#B1A0C2", "purple", "lavender-lyric-n"),
 S("8049", "Rose Glow", "#FAC9C1", "pink"), S("8122", "Peach Blossom", "#EDC4CB", "pink"), S("9409", "Pink Essence", "#F3B7B9", "pink"),
 S("9416", "Twilight Pink", "#E1A5CA", "pink"), S("9414", "Pink Flower", "#CF78AA", "pink"),
 # off-whites (ceilings, trim, the "safe" look)
 S("L145", "White Cameo", "#F7F0E6", "white"), S("8116", "Soft Breeze", "#F7EAE5", "white"), S("9436", "Air Breeze", "#F3EDE8", "white"), S("7940", "Pale Pearl", "#F2ECDE", "white"),
 # --- added 19 Nov 2026 (taste research): richer Indian shades, hex verbatim from AP shade feeds ---
 # haldi / mustard / gold
 S("7831", "Brazen Gold", "#F0D579", "earth", uf="yellow"), S("7880", "Honey Mustard", "#EBCB8E", "earth", uf="yellow"), S("9896", "Marigold Garland", "#FEBF69", "earth", "marigold-garland-n", "yellow"),
 S("7942", "Lily Gold", "#FEBB39", "earth", uf="yellow"), S("7926", "Light Ochre", "#E2A754", "earth", uf="yellow"), S("7925", "True Ochre", "#D2953C", "earth", uf="yellow"),
 S("9886", "Mustard Wood", "#C4943B", "earth", "mustard-wood-n", "yellow"),
 # terracotta / brick
 S("9988", "Rich Maple", "#CB6755", "earth", "rich-maple-n", "pink"), S("8053", "Ginger Pop", "#C65C51", "earth", uf="pink"), S("8029", "Red Earth", "#B9584B", "earth", uf="pink"),
 # sage / mehendi / deep green / teal
 S("7624", "Dry Sage", "#A2BFA6", "deep", uf="green"), S("2463", "Opaline Green", "#88A68B", "deep", uf="green"), S("7622", "Olive Path", "#6F8D6E", "deep", uf="green"),
 S("2361", "Mehendi", "#5A6D52", "deep", "mehendi-n", "green"), S("9755", "Pine Lake", "#2F805B", "deep", "pine-lake-n", "green"), S("7509", "Emerald Accent", "#007364", "deep", uf="green"),
 S("9703", "Hawaiian Blue", "#3AB4B9", "deep", "hawaiian-blue-n", "green"), S("9697", "Ajrakh Blue", "#008B95", "deep", "ajrakh-blue-n", "green"),
 S("9692", "Signature Teal", "#007A7D", "deep", "signature-teal-n", "green"), S("9700", "Prussian Teal", "#235F69", "deep", "prussian-teal-n", "green"),
 # royal blue
 S("7246", "Ink Blue", "#507BB2", "deep", uf="blue"), S("9637", "Placid Blue", "#5981B6", "deep", "placid-blue-n", "blue"), S("9647", "Naval Club", "#305B90", "deep", "naval-club-n", "blue"),
 S("1306", "Oriental Blue", "#2E5282", "deep", uf="blue"),
 # rani pink / plum
 S("8132", "Pale Blush", "#F4E8E7", "pink"), S("9426", "Candy Floss", "#EFCFE4", "pink"), S("8064", "Tinker Bell", "#FAADAB", "pink"), S("8063", "Pink Candy", "#F29495", "pink"),
 S("9593", "Pastell Rosa", "#CCA1C8", "purple", "pastell-rosa-n", "pink"), S("9594", "True Violet", "#B987B7", "purple", "true-violet-n", "pink"),
 S("9597", "Blue Plum", "#955D8F", "purple", "blue-plum-n", "pink"), S("9584", "Fervent Fuchsia", "#B05987", "pink", "fervent-fuchsia-n"), S("8165", "Royal Satin", "#6D4358", "purple", uf="pink"),
 # warm ivory / cream
 S("L124", "Pure Ivory", "#F3EEDD", "white"), S("L134", "Double Cream", "#F0EADA", "white"), S("7860", "Thick Cream", "#F4EED9", "white"), S("8020", "Desert Ivory", "#F5E8D9", "white"),
 S("0307", "Cream", "#F1E3C8", "white"),
]
FAMILIES = [("orange", P("Peach & orange", "पीच और नारंगी")), ("yellow", P("Yellow", "पीला")), ("green", P("Mint, pista & sea green", "पुदीना, पिस्ता और समुद्री हरा")),
            ("blue", P("Sky & blue", "आसमानी और नीला")), ("purple", P("Lavender", "लैवेंडर")), ("pink", P("Pink & rose", "गुलाबी")), ("red", P("Earthy red", "मिट्टी जैसा लाल")), ("earth", P("Haldi, ochre & terracotta", "हल्दी, गेरुआ और टेराकोटा")), ("deep", P("Deep greens, teal & royal blue (accent only)", "गहरा हरा, टील और रॉयल नीला (सिर्फ़ एक्सेंट)")), ("white", P("Off-white", "ऑफ़-व्हाइट"))]
# rooms the tool paints: hall (+ passage), Room 1, Room 2 bedroom, bathrooms (walls above the tiles). Kitchen stays as is.
ROOMS = [dict(k="hall", n=P("Hall + passage", "हॉल + पैसेज"), rooms=["Hall", "Passage"], acc="N", accN=P("arch wall (north), seen as you enter", "मेहराब वाली दीवार (उत्तर), घुसते ही दिखती है")),
         dict(k="room1", n=P("Room 1", "कमरा 1"), rooms=["Room 1"], acc="E", accN=P("bed-head wall (east)", "बेड के सिरहाने की दीवार (पूर्व)")),
         dict(k="room2", n=P("Room 2 bedroom", "कमरा 2 बेडरूम"), rooms=["Room 2"], acc="N", accN=P("bed-head wall (the cross wall, north)", "बेड के सिरहाने की दीवार (आड़ी दीवार, उत्तर)")),
         dict(k="bath", n=P("Bathrooms (above tiles)", "बाथरूम (टाइल के ऊपर)"), rooms=["Room 2 Bath", "Bathroom 1", "Bathroom 2"], acc="", accN=P("no accent", "एक्सेंट नहीं"))]
KEEP = ["Kitchen", "Stair", "Open Square", "Balcony"]
def sc(k, n, mood, hall, room1, room2, bath, why, tags=()):
    return dict(k=k, n=n, mood=mood, rooms=dict(hall=hall, room1=room1, room2=room2, bath=bath), why=why, tags=list(tags))
SCHEMES = [
 sc("peach", P("Peach welcome", "पीच स्वागत"), P("warm, festive, glows in evening light", "गर्म, त्योहार जैसा, शाम की रोशनी में चमकता"),
    ("9909", "8000"), ("7865", "7960"), ("8019", "9409"), ("7940", None),
    P("Peach is the most-recommended cheerful wall colour for Indian halls (Asian Paints, Berger); Berger also calls it a good Vastu shade. Light Hint of Peach on most walls, deeper Perfect Peach only on the arch wall.",
      "भारतीय हॉल के लिए पीच सबसे ज़्यादा सुझाया जाने वाला खुशनुमा रंग है (Asian Paints, Berger); Berger इसे वास्तु के लिए भी अच्छा बताता है। ज़्यादातर दीवारों पर हल्का Hint of Peach, गहरा Perfect Peach सिर्फ़ मेहराब वाली दीवार पर।")),
 sc("mint", P("Pista & sea green", "पिस्ता और समुद्री हरा"), P("cool and fresh for Bihar's summer", "बिहार की गर्मी में ठंडा और ताज़ा"),
    ("9758", "7505"), ("7516", "7562"), ("7507", "7504"), ("7460", None),
    P("Greens feel cooler in hot months and go well with wooden furniture. Pale Mint Frosting keeps the hall bright; Turquoise Treat gives one lively wall.",
      "हरे रंग गर्मी में ठंडे लगते हैं और लकड़ी के फ़र्नीचर के साथ अच्छे लगते हैं। हल्का Mint Frosting हॉल को उजला रखता है; Turquoise Treat एक दीवार को जीवंत बनाता है।")),
 sc("sunsky", P("Sunshine & sky", "धूप और आसमान"), P("bright and happy, kids love it", "चमकीला और खुशहाल, बच्चों को पसंद"),
    ("7865", "7362"), ("7912", "7361"), ("7362", "7894"), ("9758", None),
    P("Yellow + blue is the classic warm-cool pair Asian Paints suggests for lively rooms; yellow walls make a hall feel sunny even on cloudy days.",
      "पीला + नीला वह क्लासिक गर्म-ठंडा जोड़ा है जो Asian Paints जीवंत कमरों के लिए सुझाता है; पीली दीवारें बादल वाले दिन भी हॉल को धूप जैसा बनाती हैं।")),
 sc("lavender", P("Lavender & rose", "लैवेंडर और गुलाब"), P("soft, traditional, restful bedrooms", "नरम, पारंपरिक, आरामदायक बेडरूम"),
    ("7147", "9602"), ("9609", "9610"), ("8049", "9416"), ("9436", None),
    P("Pink + lavender is one of Asian Paints' suggested pairs for bedrooms and relaxed living; light pinks, blues and greens are the usual Vastu-friendly bedroom colours.",
      "गुलाबी + लैवेंडर बेडरूम और आरामदायक बैठक के लिए Asian Paints का सुझाया जोड़ा है; हल्के गुलाबी, नीले और हरे रंग बेडरूम के लिए वास्तु के अनुकूल माने जाते हैं।")),
 sc("festive", P("Marigold festive", "गेंदा उत्सव"), P("rich Indian colours, bold accent walls", "गहरे भारतीय रंग, बोल्ड एक्सेंट दीवार"),
    ("7986", "9920"), ("7960", "9666"), ("9910", "9651"), ("7865", None),
    P("Marigold with an earthy Deccan Earth wall echoes Indian festive colours; deep blue accents in the bedrooms balance the warmth. Deep accents need 3 coats.",
      "गेंदा रंग के साथ मिट्टी जैसी Deccan Earth दीवार त्योहार वाले भारतीय रंग देती है; बेडरूम में गहरा नीला एक्सेंट गर्मी को संतुलित करता है। गहरे एक्सेंट को 3 कोट चाहिए।")),
 sc("coral", P("Coral & teal", "कोरल और टील"), P("modern and lively", "मॉडर्न और जीवंत"),
    ("8019", "7512"), ("8017", "7504"), ("8122", "9416"), ("7460", None),
    P("Coral + peach is an Asian Paints living-room pick; a teal accent adds contrast that still feels fresh.",
      "कोरल + पीच Asian Paints का बैठक वाला सुझाव है; टील एक्सेंट ताज़ा लगने वाला कंट्रास्ट जोड़ता है।")),
 sc("haldi", P("Haldi & mehendi", "हल्दी और मेहंदी"), P("traditional North-Indian warmth, wedding-house feel", "पारंपरिक उत्तर भारतीय गर्माहट, शादी वाले घर जैसा"),
    ("7880", "9886"), ("9758", "7622"), ("7865", "2361"), ("7865", None),
    P("Turmeric yellow with henna green, two colours every Indian family knows. Honey Mustard on the hall with a Mustard Wood arch wall; sage-olive greens in the bedrooms keep it calm. Designers in Asian Paints' magazine note mustard/ochre and sage are back in Indian homes.",
      "हल्दी जैसा पीला और मेहंदी जैसा हरा, दो रंग जो हर भारतीय परिवार जानता है। हॉल में Honey Mustard, मेहराब पर Mustard Wood; बेडरूम में सेज-ऑलिव हरा शांत रखता है।"), ("bright", "parents", "trend")),
 sc("royal", P("Royal blue & cream", "रॉयल नीला और क्रीम"), P("rich, classy, cool in summer", "शाही, क्लासी, गर्मी में ठंडा"),
    ("L134", "1306"), ("7362", "9647"), ("8132", "7246"), ("9436", None),
    P("Cream walls with one deep royal-blue wall look rich without making the room dark; blue is cooling and a Vastu-friendly bedroom colour. Deep blue needs 3 coats over a tinted primer.",
      "क्रीम दीवारें और एक गहरी रॉयल नीली दीवार, कमरा गहरा किए बिना शाही लगता है; नीला ठंडक देता है और बेडरूम के लिए वास्तु-अनुकूल है। गहरे नीले को टिंटेड प्राइमर पर 3 कोट चाहिए।"), ("bold", "calm")),
 sc("terracotta", P("Terracotta & ivory", "टेराकोटा और आइवरी"), P("earthy, mitti-ghar warmth", "मिट्टी के घर जैसी गर्माहट"),
    ("8020", "8029"), ("0307", "9988"), ("8049", "8053"), ("7940", None),
    P("Brick and clay reds on ivory: a warm, grounded Indian look that Asian Paints' designers say is replacing grey-beige. Keep terracotta to one wall per room; it hides marks well in the hall.",
      "आइवरी पर ईंट-मिट्टी जैसा लाल: गर्म, ज़मीनी भारतीय लुक, जिसे Asian Paints के डिज़ाइनर ग्रे-बेज की जगह ले रहा बताते हैं। हर कमरे में टेराकोटा एक दीवार पर रखें; हॉल में दाग भी कम दिखते हैं।"), ("bold", "trend")),
 sc("rani", P("Rani pink & gold", "रानी गुलाबी और सुनहरा"), P("festive, joyful, for those who love pink", "उत्सव जैसा, खुशनुमा, गुलाबी पसंद करने वालों के लिए"),
    ("7865", "9584"), ("9426", "9597"), ("8064", "8063"), ("8132", None),
    P("Bright pink with golden yellow is the classic Indian festive pair (think wedding marigolds and rani-pink saris). Fuchsia only on the hall arch wall; softer Candy Floss and Tinker Bell in bedrooms.",
      "चमकीला गुलाबी और सुनहरा पीला क्लासिक भारतीय उत्सव जोड़ा है (शादी के गेंदे और रानी-गुलाबी साड़ी)। फ़ुशिया सिर्फ़ हॉल की मेहराब दीवार पर; बेडरूम में हल्का Candy Floss और Tinker Bell।"), ("bright", "parents", "bold")),
 sc("peacock", P("Peacock teal & yellow", "मोरपंखी टील और पीला"), P("vivid, artistic, Ajrakh-print colours", "चटक, कलात्मक, अजरख प्रिंट जैसे रंग"),
    ("7865", "9692"), ("7516", "7509"), ("9758", "9697"), ("7460", None),
    P("Peacock teal against sunny yellow echoes Indian textiles (Ajrakh, Banarasi). One deep teal wall per room, pale mint or yellow on the rest.",
      "धूप जैसे पीले के साथ मोरपंखी टील भारतीय कपड़ों (अजरख, बनारसी) जैसा है। हर कमरे में एक गहरी टील दीवार, बाकी पर हल्का पुदीना या पीला।"), ("bold", "bright")),
 sc("sage", P("Sage & ivory (2026 trend)", "सेज और आइवरी (2026 ट्रेंड)"), P("calm, modern, the young-couple pick", "शांत, मॉडर्न, युवाओं की पसंद"),
    ("L124", "7624"), ("7860", "2463"), ("7624", "9755"), ("L124", None),
    P("Asian Paints' Colour of the Year 2026, Moonlit Silk, is a warm luminous neutral green (its exact shade isn't published online yet, so Dry Sage is used as the closest verified shade). Pantone's 2026 pick is a soft white. A middle ground between 'dull' off-white and loud colours.",
      "Asian Paints का 2026 का कलर ऑफ़ द ईयर Moonlit Silk एक गर्म, चमकदार न्यूट्रल हरा है (उसका सही शेड अभी ऑनलाइन नहीं, इसलिए सबसे करीब Dry Sage लिया है)। फीके ऑफ़-व्हाइट और तेज़ रंगों के बीच का रास्ता।"), ("calm", "trend")),
 sc("vastu", P("Vastu-safe light", "वास्तु-अनुकूल हल्के रंग"), P("light colours by the Vastu book", "वास्तु के हिसाब से हल्के रंग"),
    ("0307", "7588"), ("7362", None), ("8049", None), ("9436", None),
    P("Asian Paints' Vastu guide says living rooms do best in light shades (cream, light green, soft yellow, light blue) and pairs cream with light green; bedrooms in light blue and pink. Avoid dark red, black, heavy grey and deep purple in the hall.",
      "Asian Paints की वास्तु गाइड के अनुसार बैठक में हल्के रंग (क्रीम, हल्का हरा, हल्का पीला, हल्का नीला) सबसे अच्छे, क्रीम के साथ हल्का हरा; बेडरूम में हल्का नीला और गुलाबी। हॉल में गहरा लाल, काला, ज़्यादा ग्रे और गहरा बैंगनी न लगाएँ।"), ("vastu", "calm", "parents")),
 sc("white", P("Safe white (the old plan)", "सादा सफ़ेद (पुराना प्लान)"), P("for comparison only", "सिर्फ़ तुलना के लिए"),
    ("7940", "8116"), ("L145", None), ("L145", None), ("L145", None),
    P("The quiet off-white look from the earlier plan, kept here so you can compare.", "पहले प्लान का शांत ऑफ़-व्हाइट लुक, तुलना के लिए।")),
]
TAGS = {"peach": ("bright", "parents", "vastu"), "mint": ("calm", "bright"), "sunsky": ("bright",), "lavender": ("calm",), "festive": ("bold", "bright", "parents"), "coral": ("bold", "trend"), "white": ("calm",)}
for s_ in SCHEMES:
    if s_["k"] in TAGS: s_["tags"] = list(TAGS[s_["k"]])
TAGN = {"bright": P("Bright & cheerful", "चमकीले"), "parents": P("Parents' pick", "माता-पिता की पसंद"), "calm": P("Calm", "शांत"),
        "bold": P("Bold accent", "बोल्ड"), "trend": P("Trending 2026", "2026 ट्रेंड"), "vastu": P("Vastu", "वास्तु")}
# What people say: paraphrased from forums / designers (Reddit itself could not be fetched from here)
VOICES = [
 P("Indian designers: 'Colour is culture, particularly in India'; the all-beige look is called a Western, social-media-driven trend (Asian Paints Beautiful Homes).", "भारतीय डिज़ाइनर: 'रंग संस्कृति है, ख़ासकर भारत में'; सब-कुछ बेज वाला लुक पश्चिमी, सोशल-मीडिया ट्रेंड कहा गया (Beautiful Homes)।"),
 P("Indians abroad: plain grey-white homes feel uncomfortable; colour is tied to festivals like Diwali and Holi (Blind thread). Realtors still advise neutrals for resale.", "विदेश में रहने वाले भारतीय: सादे ग्रे-सफ़ेद घर अजीब लगते हैं; रंग दिवाली-होली से जुड़ा है (Blind)। प्रॉपर्टी वाले बेचने के लिए फिर भी हल्के रंग सुझाते हैं।"),
 P("Homeowners: an off-white living room started looking 'really dull' after 4 years; ivory + muted gold, ocean blue + cream, or sunny yellow were the suggested fixes (NoBroker forum).", "घर-मालिक: ऑफ़-व्हाइट बैठक 4 साल बाद 'बहुत फीकी' लगने लगी; आइवरी + सुनहरा, समुद्री नीला + क्रीम या धूप जैसा पीला सुझाया गया (NoBroker)।"),
 P("Families often split: one wants bright yellow, the other something soothing. The usual compromise is one bright accent wall, not the whole room (NoBroker kids-room thread).", "परिवार में अक्सर मतभेद: एक को चटक पीला, दूसरे को शांत रंग। आम समझौता: पूरा कमरा नहीं, एक चटक एक्सेंट दीवार (NoBroker)।"),
 P("Parents following Vastu chose cream, beige and pastel shades and avoided black and grey (NoBroker). Sage green living rooms get good reviews from people who painted them.", "वास्तु मानने वाले माता-पिता ने क्रीम, बेज और पेस्टल चुने, काला-ग्रे नहीं (NoBroker)। जिन्होंने सेज ग्रीन बैठक बनाई, उन्हें पसंद आई।"),
 P("Designer pairs suggested for living rooms: Dry Sage 7624 + light grey, Light Sky 7331 + white, Terracotta 0427 + Desert Dune 8754, Beige 0302 + Diced Olive 7784 (NoBroker).", "बैठक के लिए डिज़ाइनर जोड़े: Dry Sage 7624 + हल्का ग्रे, Light Sky 7331 + सफ़ेद, Terracotta 0427 + Desert Dune 8754, Beige 0302 + Diced Olive 7784 (NoBroker)।"),
]
TIPS = [P("Screen colours are only indicative (Asian Paints says so). Buy sample pots of 2–3 favourites and paint a 2 × 2 ft patch on two walls; look in morning and evening light before deciding.",
          "स्क्रीन के रंग सिर्फ़ अंदाज़ा हैं (Asian Paints भी यही कहता है)। 2–3 पसंदीदा रंगों के सैंपल डिब्बे लेकर दो दीवारों पर 2 × 2 फीट का पैच लगाएँ; फ़ैसले से पहले सुबह और शाम की रोशनी में देखें।"),
        P("Keep the bright colour on one accent wall per room and a lighter shade of the same family on the rest; the room looks colourful but not small.",
          "हर कमरे में चमकीला रंग एक एक्सेंट दीवार पर, बाकी पर उसी परिवार का हल्का रंग; कमरा रंगीन लगेगा पर छोटा नहीं।"),
        P("Ceilings stay white (White Cameo or similar) so the room stays bright.", "छत सफ़ेद रखें (White Cameo या ऐसा), ताकि कमरा उजला रहे।"),
        P("Deep accents (Deccan Earth, Dal Lake Blue, Pangong Blue) need 3 coats and a tinted primer; pastels need 2 coats over white putty.",
          "गहरे एक्सेंट (Deccan Earth, Dal Lake Blue, Pangong Blue) को 3 कोट और टिंटेड प्राइमर चाहिए; हल्के रंगों को सफ़ेद पुट्टी पर 2 कोट।"),
        P("Bedrooms: light blue, pink, green or yellow are the usual Vastu-friendly picks; avoid black, grey and brown there.", "बेडरूम: हल्का नीला, गुलाबी, हरा या पीला आमतौर पर वास्तु के अनुकूल; वहाँ काला, ग्रे और भूरा न लगाएँ।"),
        P("Use the same product grade everywhere (Apcolite Premium or Royale) so colours look even; ask the dealer to tint by code, not by 'similar shade'.",
          "हर जगह एक ही ग्रेड (Apcolite Premium या Royale) ताकि रंग एक जैसे दिखें; डीलर से कोड से टिंट कराएँ, 'मिलता-जुलता रंग' से नहीं।"),
        P("Use at most three colours in a room (two light + one accent), keep neighbouring rooms in related colour families, and never paint the ceiling dark (Asian Paints, 6 mistakes).", "एक कमरे में ज़्यादा से ज़्यादा तीन रंग (दो हल्के + एक एक्सेंट), पास वाले कमरों में मिलते-जुलते रंग, और छत कभी गहरी नहीं (Asian Paints)।")]
SOURCES = [("Asian Paints colour catalogue (shade data)", "https://www.asianpaints.com/colour-catalogue.html"),
           ("Asian Paints: colour combinations for your living room", "https://www.asianpaints.com/blogs/colour-combinations-for-your-living-room.html"),
           ("Asian Paints: best interior colour combinations for Indian homes", "https://www.asianpaints.com/blogs/best-interior-colour-combination-for-indian-homes.html"),
           ("Berger: peach colour combinations", "https://www.bergerpaints.com/blogs/peach-colour-combination-for-walls"),
           ("Urban Company: Asian Paints combinations for Indian homes", "https://www.urbancompany.com/blog/our-favourite-asian-paints-colour-combination-for-indian-homes"),
           ("Square Yards: wall colour combinations (incl. Vastu notes)", "https://www.squareyards.com/blog/wall-colour-combination-decart"),
           ("Beautiful Homes: Indian homes broke up with brown", "https://www.beautifulhomes.asianpaints.com/magazine/lifestyle/features/have-indian-homes-finally-broken-up-with-brown.html"),
           ("Beautiful Homes: Sarah Sham, beige to bright", "https://www.beautifulhomes.asianpaints.com/magazine/decor-advice/design-and-style/sarah-sham-on-indian-homes-going-from-beige-to-bright"),
           ("Beautiful Homes: neutrals vs bright, designers' views", "https://beautifulhomes.asianpaints.com/magazine/lifestyle/features/soothing-neutrals-vs-bright-colours-opinion-by-interior-designers.html"),
           ("Asian Paints: living room Vastu colours", "https://www.asianpaints.com/blogs/living-room-vastu-colours.html"),
           ("Asian Paints: 6 mistakes picking wall colours", "https://www.asianpaints.com/blogs/6-mistakes-to-avoid-when-picking-wall-paint-colours.html"),
           ("Asian Paints ColourNext 2026 (Moonlit Silk)", "https://www.asianpaints.com/content/ap/en/home/colour-next.html"),
           ("NoBroker forum: best living room colour", "https://www.nobroker.in/forum/which-color-is-best-for-living-room-asian-paints/"),
           ("NoBroker forum: kids' room colour", "https://www.nobroker.in/forum/which-colour-is-best-for-kids-room/"),
           ("Blind: why Indians paint rooms in bright colours", "https://www.teamblind.com/post/why-do-indians-paint-bedrooms-in-different-bright-colors-kcubod7e")]
codes = {s["code"] for s in SHADES}
for s_ in SCHEMES:
    for r, (b, a) in s_["rooms"].items():
        assert b in codes and (a is None or a in codes), (s_["k"], r, b, a)
os.makedirs(OUT, exist_ok=True)
json.dump(dict(shades=SHADES, families=FAMILIES, rooms=ROOMS, keep=KEEP, schemes=SCHEMES, tagn=TAGN, voices=VOICES, tips=TIPS, sources=SOURCES), open(os.path.join(OUT, "colours.json"), "w"), ensure_ascii=False, indent=1)
print("shades", len(SHADES), "schemes", len(SCHEMES))
