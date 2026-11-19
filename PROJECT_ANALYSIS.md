# MyFlat project guide and analysis

Reviewed 6 October 2026. The local viewer is served at http://localhost:8080/.

## What this project is

A digital model of your flat, with six alternative interior designs for Room 1. Blender holds the editable building and furniture geometry. A lightweight browser app lets you walk around, compare designs, inspect materials, open moving parts, learn interior terminology, and customise Option E with a live estimated budget.

The flow is:

`Floor plan + site observations → Blender build scripts → .blend model → GLB export + manifest → browser viewer`

The browser does not rebuild the building or write changes back into Blender. Customisation changes which exported objects are visible and their colours; choices are saved in browser storage and can be shared through a URL.

## Root folder: what each thing contains

| File or folder | Purpose |
|---|---|
| `floorplan_reference.png` | Original 2D reference plan; not a reliable scaled measurement drawing. |
| `MyFlat_Trial_V0.blend` | First trial model. |
| `MyFlat_V1_Architecture.blend` | Original architecture baseline. |
| `MyFlat_V1_1_Architecture.blend` | Corrected architecture: Room 1 south/west geometry, balcony opening, corner column and hall corner. |
| `MyFlat_V1_1_Room1_Interiors.blend` | Architecture plus all six Room 1 design collections. |
| `*.blend1` | Blender's backup versions; generally keep them for recovery. |
| `build_MyFlat_Trial_V0.py` | Rebuilds the trial geometry inside Blender. |
| `build_MyFlat_V1_Architecture.py` | Rebuilds baseline architecture. Its `P` table contains dimensions in feet. |
| `build_MyFlat_V1_1_Architecture.py` | Rebuilds the corrected architecture. Its `P` table includes the raised wall and enlarged balcony opening. |
| `build_room1_interiors.py` | Creates beds, wardrobes, desks, windows, ceilings, lights and balcony furniture for all six options. Adds interaction and variant metadata. Defines `run()`; invoke that function when executing this script to build the collections. |
| `make_trial_v0.py` | Trial-model creation wrapper. |
| `render_views.py`, `render_views_v1.py` | Blender rendering helpers. |
| `TRIAL_ASSUMPTIONS.txt` | Trial measurements and guesses. |
| `V1_STATUS_AND_ASSUMPTIONS.txt` | Baseline V1 confirmed, plan, derived and provisional measurements. It describes V1, not the later V1.1 Room 1 correction. |
| `renders/` | Trial images. |
| `renders_v1/` | Baseline architecture images, room views and status map. |
| `renders_v1_1/` | Corrected architecture and Room 1 images. |
| `renders_room1/` | Earlier interior views for DEFAULT and A–C. |
| `Claude outputs/` | Archived screenshots, ZIP deliveries and intermediate script snippets. The active viewer is in `MyFlat_Viewer/`. |
| `MyFlat_Viewer/` | Runnable browser app, exported models, data, server and tests. |

## Viewer: where to change what

| Path inside `MyFlat_Viewer/` | Responsibility |
|---|---|
| `index.html` | Page structure, buttons and panels; import map points to local Three.js. |
| `src/styles.css` | Desktop/mobile layout and appearance. |
| `src/config.js` | Navigation speed, eye height, collision settings, category labels, status colours and fallback model. |
| `src/main.js` | Central controller: renderer, model loading, rooms, cameras, visibility, inspector, section cut, plan overlay and side-by-side comparison. |
| `src/walk.js` | First-person movement, floor/step detection and obstacle collisions. |
| `src/immersive.js` | Openable assemblies, lights/night mode, dimensions and immersive controls. |
| `src/extras.js` | Panel behaviour, zoom, lens/ceiling view, hover explanations, room dimensions and touch features. |
| `src/simple.js` | Easy mode: large walking/turning buttons and tap-to-walk navigation. |
| `src/learn.js` | Beginner guide, dictionary, surface explanations and “Show me” actions. |
| `src/i18n.js` | English/Hindi interface switching. |
| `src/edit.js` | Option E choices, colour changes, variant visibility, compatibility rules, live budget and share links. |
| `src/chat.js` | Chat interface; builds design knowledge and current-view context, sends questions to the backend, and presents optional Apply actions. |
| `models/models.json` | Eight model choices and startup model. DEFAULT is the actual startup model; config.js's V1 value is only a fallback. |
| `models/*.glb` | Browser-ready geometry, materials, embedded assets and object metadata. |
| `models/*.manifest.json` | Export records: source Blender file, object names, categories, statuses and counts. |
| `models/room1_designs.json` | Design descriptions, material schedules, D/E budgets and E customisation definitions. |
| `models/room1_designs_hi.json` | Hindi design data. Keep it aligned with the English file when editing. |
| `models/learn_guide.json`, `learn_guide_hi.json` | Learning content and dictionary in both languages. |
| `vendor/three/` | Bundled Three.js and addons; core viewer works without an internet connection. |
| `scripts/export_glb.py` | Blender exporter. Writes GLB and manifest; exports one interior option at a time. Does not save the source .blend. |
| `scripts/serve.py` | Python local server, no-cache headers and local POST /api/chat backend. |
| `start.command` | Mac launcher: chooses Python, finds a free port, opens a browser and enables LAN access. |
| `api/chat.js` | Vercel chat function: API credentials, optional passcode, per-instance rate limit and upstream OpenAI request. |
| `vercel.json` | Hosting cache headers and chat-function time limit. |
| `scripts/test_*.py` | Existing Playwright checks for architecture, interiors, navigation, immersion, comfort, learning, mobile, language, easy mode, customisation and chat. |

There is no npm build step, frontend framework or database. The app uses JavaScript modules, Three.js, HTML/CSS and JSON; Python serves it locally. Hosted chat uses a JavaScript serverless function.

## What the designs have

| Design | Main idea | Recorded itemised total |
|---|---|---|
| DEFAULT | Warm contemporary; bed faces balcony, wardrobe in alcove, study/dresser on thick wall. | No itemised total supplied. |
| A | Japandi; low bed on slatted south wall, desk beneath window, sliding wardrobe. | No itemised total supplied. |
| B | Minimal modern; bed on north wall, TV/dresser on thick wall and balcony lounge corner. | No itemised total supplied. |
| C | Indian modern heritage; cane headboard, built-in diwan and folding balcony doors. | No itemised total supplied. |
| D | Budget version of DEFAULT using ready-made furniture and local carpentry. | ₹1,93,300 |
| E | Simple/practical; painted surfaces, sliding wardrobe with mirror, standing desk, builder window and no false ceiling. | ₹1,47,900 recommended; ₹1,28,400 budget preset; ₹1,13,900 tightest preset. |

These are the project's stored estimates, not newly verified supplier quotes. In E, gypsum plaster means smoothing the existing slab, not adding a suspended false ceiling. Some customisation choices affect cost only; the UI labels those “budget only”.

## Measurements and confidence

V1.1 Room 1 has a 12′7″ × 11′2″ main area and an approximately 5′4″ × 3′4″ alcove. The balcony opening is approximately 10′5″ wide. Earlier V1 assumptions describe a different Room 1 depth and opening; use the correct version's data.

Object statuses distinguish evidence from proposals: CONFIRMED = recorded observations/answers; PLAN = drawing values; DERIVED = calculated; PROVISIONAL = assumptions; DESIGN = proposed interior work. The corrected architecture export still has 75 provisional objects. Do not treat all displayed geometry as site-verified dimensions. Room labels based on bounding boxes also overstate usable area for irregular rooms such as Room 1.

## Findings worth addressing

1. **Chat is not configured locally.** No API key or viewer `.env` file was found. The 3D viewer works independently.
2. **Chat's fixed facts conflict with the design data.** `src/chat.js` says the bed can only go on the east wall, while A places it on the south wall and B on the north wall. This can produce misleading explanations. Prefer model/design-specific facts.
3. **The local server can serve a future `.env` file.** It inherits Python's static file handler without blocking dotfiles. Git ignoring `.env` does not prevent an HTTP download. Block secret files before using chat credentials with the LAN launcher. The server started for this review is bound to localhost.
4. **Shared/saved choices skip compatibility rules on initial load.** `stateFor()` validates allowed IDs but does not call `applyRules()`. A manually formed link combining hinged doors with a mirror on the slider can load an inconsistent state. Normal UI changes do apply the rule.
5. **Model comparison has cleanup/race risks.** Comparison roots are removed without disposing their geometry/materials/textures. Main model replacement disposes geometry but not materials/textures. Rapid asynchronous model changes also lack an explicit request guard. These are code-review concerns; memory growth and rapid-switch failures were not measured.
6. **Local chat validation is weaker than hosted chat.** There is no request-size limit, passcode or rate limit in serve.py, and malformed field types can raise exceptions. Reasonable for a private prototype, but worth hardening before broader access.
7. **Portability/documentation could improve.** Blender scripts use hard-coded `~/Documents/MyFlat` paths. The README layout omits some newer modules and earlier sections still refer to five/four designs. Test scripts default to port 8765, so pass the actual URL when testing port 8080.

## Validation performed

- Local server responded HTTP 200.
- All eight GLB headers and lengths were valid; all manifest object names existed in their corresponding GLBs.
- All model-directory JSON files parsed; D and E budget rows sum to their stored totals.
- Headless Chrome loaded DEFAULT with 248 objects, ten named spaces, no missing objects and active walk mode.
- All six interior designs loaded and retained camera position.
- Learn opened with eight surface cards.
- Option E recommended total was ₹1,47,900. Choosing hinged wardrobe doors changed the mirror to cabinet and the total to ₹1,40,900.
- Hindi switch changed the language button to EN.
- A fresh mobile browser context loaded the model, found ten spaces and enabled touch/easy/walk modes with no JavaScript errors. An earlier mobile reload after repeated desktop model switching timed out; that reload path needs further investigation.
- Existing Python Playwright suites were not run: the Python environments checked did not include Playwright. Browser checks used the available Node Playwright library and installed Chrome instead.
- Blender models were not rebuilt, and source .blend contents were not independently inspected in Blender. Export checks validate the supplied browser assets, not construction accuracy.

## How to use and restart

Open http://localhost:8080/. Drag to look around; WASD/arrows move; click interactive doors or wardrobes to open them. Use the left panel to switch designs. Top gives a whole-flat view. Learn explains materials. Pick E for Customise.

To restart from a terminal:

```sh
cd /Users/shraj/Documents/MyFlat/MyFlat_Viewer
python3 scripts/serve.py 8080
```

Keep the server terminal running; Ctrl+C stops it. Add `--lan` only when you want another device on the same Wi-Fi to connect. For a slower device, use http://localhost:8080/?lowq=1.
