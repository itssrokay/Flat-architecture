# MyFlat Viewer

A local, browser-based 3D inspection tool for the MyFlat architecture model.
The Blender file is the source of truth; this viewer only displays the GLB exported from it.

## Start it

**Easiest:** double-click `start.command` in Finder. It starts a local web server and opens your browser.

**Or in Terminal:**

```bash
cd ~/Documents/MyFlat/MyFlat_Viewer
python3 scripts/serve.py 8080
```

(`scripts/serve.py` is a plain local server that tells the browser not to cache, so you always see the latest version.) Then open <http://localhost:8080> in Chrome, Safari or Firefox. Press `Ctrl+C` in the terminal to stop.

If `python3` isn't installed, use Blender's own Python instead:

```bash
cd ~/Documents/MyFlat/MyFlat_Viewer
"$(ls /Applications/Blender.app/Contents/Resources/*/python/bin/python3* | head -1)" -m http.server 8080
```

No `npm install` or internet is needed. Three.js is included in `vendor/`.
The page must be served over http://; opening `index.html` directly as a file will not load the model.

## New to home interiors? Press 📘 Learn

**📘 Learn** (top-left, or **G**) opens a beginner's guide next to the 3D view:

- **Your room**: every surface of the design you're looking at (floor, walls, bed wall, ceiling, wardrobe, window, balcony door, balcony). Each one says what you'll see, what it's made of layer by layer (from the concrete up to what you touch), and exactly where the putty and paint go. **Show me** flies to that part.
- **How homes are built**: pillars, beams, slab and brick walls; your Room 1 plan explained (the thick "raised" wall, the alcove, the balcony opening, the pillar); what goes on a wall, a floor and a ceiling.
- **Step by step**: the order the work happens in, and who does each step.
- **Compare designs**: the 5 designs side by side in plain words.
- **Dictionary**: about 60 terms (putty, vitrified tile, HDHMR, domal, 2700K …), searchable, with **Show me** where the thing exists in the model.

With **Hover info** on, pointing at anything also gives a one-line plain explanation. The inspector shows the same under *In simple words*. The content is in `models/learn_guide.json`, so it can be edited without touching code.

## Put it online (Vercel)

The whole viewer is a static website, so you can host it anywhere.

1. Go to <https://vercel.com/drop> and sign in.
2. Drag the **`MyFlat_Viewer`** folder (the one with `index.html` inside) onto the page.
3. Give it a project name and click **Deploy**. You get a link like `https://myflat-viewer.vercel.app`.

To update it later, drop the folder again. Each drop makes a new project and link; to keep one link, connect the GitHub repo in Vercel instead, with the root directory set to `MyFlat_Viewer`. `vercel.json` sets sensible caching. The site is public to anyone who has the link, and it shows your flat's layout, so share it carefully.

There's one link for every device. The viewer picks the layout itself:

- **Phones and tablets** (touch screen): joystick and touch controls, and no shadows, to stay smooth.
- **Narrow screens** (≤ 900 px wide): a short top bar, with the side panels sliding in from the ‹ › tabs.
- **Computers**: the full layout.

Add `?touch=1` to force touch controls, `?hq=1` for shadows on a phone, and `?lang=hi` to open in Hindi.

## हिंदी / English

The **हिंदी** button in the top bar switches the whole interface, the design notes and the 📘 Learn guide to Hindi; **EN** switches back. Your choice is remembered. The technical spec lines in the material schedule stay in English, because contractors use those terms.

## On a phone or tablet

Start the viewer with `start.command` (or `python3 scripts/serve.py 8080 --lan`). It prints an address like `http://192.168.1.23:8080/`: open that on a phone on the same Wi-Fi. If macOS asks whether Python may accept incoming connections, click Allow. The viewer switches to touch controls on its own:

| Action | How |
|---|---|
| Walk | the **joystick** at the bottom left (push further to walk faster) |
| Look around | drag anywhere with one finger |
| Wider lens (see the whole ceiling) | **pinch** with two fingers, or ⤒ for *Look at ceiling* |
| Raise / lower your eyes | ⬆ / ⬇ (hold) |
| Open / close doors, windows, wardrobes | tap them, or ✋ for what the circle points at |
| What is this? | tap anything: a card shows its name, size and a plain explanation |
| Overview | one finger rotates, two fingers pinch-zoom and pan; **double-tap a floor** to go in there |
| Panels (designs, rooms, notes) | the **›** and **‹** tabs at the edges slide them over the view; tap the view to close them |

The "Inside" box starts minimised on phones. Tap it to see its buttons, or tap **–** on a computer to minimise it. Shadows are off on phones to keep them smooth; add `?hq=1` to the address to turn them on.

## Controls

There are two ways to look at the flat.

**Inside (walk mode).** This is where the viewer opens, and where every room button takes you. You stand in the room at eye level.

| Action | How |
|---|---|
| Look around, including up at the ceiling | drag with the mouse (or one finger) |
| Move | WASD or the arrow keys. Shift to run. |
| Step forward / back | mouse wheel |
| Raise / lower your eyes (to study the ceiling, or a low view) | **R** / **V** (or PageUp / PageDown). It stops short of the ceiling. |
| See the whole ceiling | **Look at ceiling** in the HUD (or **C**): you stand in the middle of the room, eyes low, looking straight up through a wide lens. Press again to go back. |
| Wider / narrower lens | trackpad pinch, Ctrl+wheel, **−** / **+**, or the **Lens** slider (35°–110°) |
| Open / close a door, sash, wardrobe or curtain | click it, or look at it and press **E** |
| Select a part for the inspector | click it |
| Leave | **Overview** (top bar or HUD) |

Walls, furniture and closed glass doors block you. Floors and stairs carry you.

**Overview (orbit).** Use this to see the whole flat from outside.

| Action | How |
|---|---|
| Orbit | left-drag. The camera can't go under the ground. |
| Pan | right-drag (or two-finger drag) |
| Zoom | mouse wheel or pinch, **like zooming a photo**: the point under the cursor stays under the cursor, so you can zoom straight into e.g. the right end of the balcony |
| Slide the view | WASD or the arrow keys. **Q** / **E** (or PageDown / PageUp) move down / up. Shift is faster. |
| Go inside at a spot | **double-click a floor** |
| Preset views | **Top** (plan, roof hidden) · **N S E W** (views *from* that side) · **Iso** |
| Perspective / orthographic | **Persp / Ortho** button |
| Room views | left panel: click a room to stand inside it. ▸ shows more viewpoints (corners, centre, from above). |

Solid parts such as walls, slabs and ceilings are drawn one-sided. If the overview camera passes into a wall you see through it instead of a white screen.

**Panels**

| Action | How |
|---|---|
| Hide / show the left panel | the **‹** tab on the left edge of the view, or **[** |
| Hide / show the right panel | the **›** tab on the right edge, or **]** |
| Minimise a control box (Visibility, Section cut, Open / close, Floor plan) | click its title |
| Fold a side-panel block (Interior design, Rooms, Inspector) | click its title |
| Hide all bottom controls | **Hide controls** |

These choices are remembered in your browser.

**Information**

| Action | How |
|---|---|
| Hover info | **Hover info** (or **I**): point at anything to see its name, type, size, specification, room, design option and status. It works inside and in the overview. |
| Room size | **Room size** (or **M**): wall-by-wall lengths of the room you're in (or the last room you visited or selected), its overall size, area in sq ft and floor-to-ceiling height. The lines are drawn on the floor and show through furniture. |
| Part dimensions | **Dimensions**: W × D × H labels on nearby furniture, windows and doors; select an object for dimension lines |

**Other controls**

| Action | How |
|---|---|
| Roof | **Roof ON/OFF**. It comes back on automatically when you go inside. |
| Section cut | bottom panel: tick **Cut above** and drag the height slider |
| Visibility | category chips, plus **Show all**, **Hide all** and **Reset** |
| Labels / Edges | toggles in the top bar |
| Status mode | **Status** colours objects by the Blender `status` property, with a legend and counts |
| Plan compare | **Plan compare**: top orthographic view, roof off, original plan overlaid; opacity slider; plan over the model or on the floor |
| Inspector | click any object. **Part of** jumps to the door or window assembly. **Focus** and **Isolate category** buttons. |
| Debug | **Debug**: name, status and size labels on every object, plus a searchable object list |
| Save a viewpoint | **Copy current view** copies JSON you can paste into `src/config.js → viewpoints` |
| Slow computer | open `http://localhost:8080/?lowq=1` (no shadows) |

## Project layout

```
MyFlat_Viewer/
  index.html            page + UI layout
  start.command         double-click launcher (macOS)
  src/
    config.js           ALL settings: model list, categories, colours, eye height…
    main.js             viewer: loading, cameras, rooms, visibility, status, plan, inspector
    walk.js             first-person walkthrough with collision
    immersive.js        openable parts (with collisions), lights / night, dimensions, immersive mode
    extras.js           panels, photo-style zoom, lens / ceiling view, hover info, room size
    learn.js            beginner's guide (📘 Learn) + plain-language explanations
    i18n.js             English / Hindi switch for the interface
    styles.css
  models/
    models.json         list of models shown in the dropdown (+ default)
    MyFlat_V1_Architecture.glb             exported from Blender
    MyFlat_V1_Architecture.manifest.json   export report: every object, category, status
  scripts/
    export_glb.py       Blender → GLB exporter (never saves the .blend)
    test_viewer.py      automated browser test (optional, needs Playwright)
  vendor/three/         Three.js r180 (MIT), used offline
```

## Replacing the model (V2, V3 …)

1. Open `MyFlat_V2_Architecture.blend` in Blender.
2. In Blender's Text Editor, open `MyFlat_Viewer/scripts/export_glb.py` and click **Run Script**.
   It writes `models/MyFlat_V2_Architecture.glb` and a `.manifest.json` next to it, then reverts the .blend so nothing is saved.
   To run it without opening Blender:
   ```bash
   /Applications/Blender.app/Contents/MacOS/Blender -b ~/Documents/MyFlat/MyFlat_V2_Architecture.blend \
       --python ~/Documents/MyFlat/MyFlat_Viewer/scripts/export_glb.py
   ```
3. Add it to `models/models.json` (and make it the default if you like):
   ```json
   { "default": "MyFlat_V2_Architecture.glb",
     "models": [
       { "file": "MyFlat_V2_Architecture.glb", "label": "V2 Architecture", "manifest": "MyFlat_V2_Architecture.manifest.json" },
       { "file": "MyFlat_V1_Architecture.glb", "label": "V1 Architecture", "manifest": "MyFlat_V1_Architecture.manifest.json" } ] }
   ```
4. Reload the browser and pick it from the dropdown. You can also open `?model=MyFlat_V2_Architecture.glb` directly.

Nothing in the viewer is tied to V1's object names. Rooms, labels, viewpoints, visibility groups, status colours and the plan overlay all come from metadata in the GLB:

- `category`, `room`, `status`, `basis` and `dims_ft` are written by the exporter.
- The plan overlay is the object named `PLAN_REFERENCE_OVERLAY`.

The status bar checks that every object listed in the manifest is present in the GLB.

## Interior-design variants later

Export a design file, for example `MyFlat_V1_Room1_Japandi.blend`, the same way and add it to `models.json`.
Objects in collections the exporter doesn't recognise (for example `13_FURNITURE`, `14_LIGHTING`) get a category from the collection name, such as `furniture` or `lighting`. They appear as new visibility chips automatically.
Glass, colours and textures come through as standard glTF materials.

## Notes and limits

- The floor plan image is **not to scale**. It is stretched to the model extents exactly as in Blender, so treat it as a visual cross-check, not a measurement.
- Walkthrough collides with walls, pillars, doors, windows, railings and stair parts, and follows floors and steps. Doors are modelled open, so you can walk through doorways.
- Touch: one-finger drag looks around when you're inside; orbit, pan and zoom work with touch.
- The section cut is a clean clipping plane. Cut faces are hollow rather than filled.

## Interior design (Room 1)

The viewer opens in **Room 1 · DEFAULT** at eye level. In the left panel, under **Interior design**:

- **DEFAULT / A / B / C / D** switch between the five Room 1 designs. **D (Smart Budget)** is the value option at about ₹1.93 lakh; its notes include an itemised **Budget** table (and where to cut if it runs over). The camera stays exactly where it is, so you can flip between designs from the same spot.
- **V1.1 arch / V1 baseline** show the bare architecture. V1 is the untouched baseline.
- **Compare side by side with** splits the view: the current model on the left, the chosen one on the right, both driven by the same camera. Set it back to *— off —* to return to a single view.
- The right panel shows the chosen design's notes: why it is the default, layout, wardrobe, window, balcony door, ceiling and lighting, balcony, and palette.
- Room 1 has extra viewpoints (Rooms → Room 1 ▸): design view, towards the balcony, wardrobe and thick wall, and the balcony.

The designs come from `~/Documents/MyFlat/MyFlat_V1_1_Room1_Interiors.blend`, which holds one collection per option (13_ROOM1_DEFAULT … 17_ROOM1_OPTION_D). They are built by `build_room1_interiors.py`. The architecture files are not modified.
To re-export after editing the designs, open that .blend and in the Python console run:

```python
for opt in ["DEFAULT", "OPTION_A", "OPTION_B", "OPTION_C", "OPTION_D"]:
    exec(open(bpy.path.abspath("//MyFlat_Viewer/scripts/export_glb.py")).read(),
         {"DESIGN": opt, "OUT_NAME": "MyFlat_V1_1_Room1_" + opt})
```

Tests: `python3 scripts/test_viewer.py` (architecture), `python3 scripts/test_interiors.py` (designs), `python3 scripts/test_navigation.py` (navigation) `python3 scripts/test_comfort.py` (panels, zoom, ceiling view, hover info, collisions, room size) `python3 scripts/test_learn.py` (beginner's guide) and `python3 scripts/test_mobile.py` (phone + window closing) and `python3 scripts/test_lang.py` (Hindi switch, phone top bar). All need Playwright.

## Immersive features

| Feature | How |
|---|---|
| Full-screen immersive mode | **⛶ Immersive** (or **F**): hides all panels and shows a small floating toolbar (Overview, Walk, Room 1, Balcony, Open all, Close all, Lights, Night, Dims, Exit). Esc also exits. |
| Open / close things | **Double-click** a wardrobe door, loft door, window sash, sliding balcony panel or sheer curtain (a sash that has slid behind a fixed pane is closed by clicking anywhere on that window). In walk mode, click it, or look at it (crosshair) and press **E**. **Open all / Close all** are in the bottom panel. The inspector has an Open / close button for the selected part. |
| Walk onto the balcony | Open the balcony door first (double-click it, or E in Walk mode). A closed door is solid glass, just like the real one. |
| Real-world clearances | Opening parts collide with furniture, lamps, plants and decor. A sash or door that meets something stops there and a red note says what it hit, so the viewer also checks the design. (Option B's bedside pendant was in the window's swing, so it was replaced by a wall-mounted reading light. The wardrobe-front downlight in DEFAULT and Option C was moved 1'7" out, clear of the loft doors.) |
| Lights | **Lights ON/OFF** (**L**) switches every light fitting. **Day / Night** (**N**) darkens the sky; at night the downlights, lamps, cove strips and pendants actually light the room. |
| Dimensions | **Dimensions**: labels show W × D × H of the nearest visible furniture, wardrobe, window and door parts, plus opening sizes and room sizes. Select any object to get W / D / H dimension lines on it. |
| Material details | The right panel's **Material & finish schedule** lists, for each design, floor, walls, ceiling, wardrobe, furniture, window, balcony door, lighting and balcony specifications. |

Openable parts and light fittings are defined in Blender (custom properties `interact`, `group`, `open_deg`, `slide_ft`, `light`, `lumens` set by `build_room1_interiors.py`), so new designs get the same behaviour automatically.
Test: `python3 scripts/test_immersive.py`.
