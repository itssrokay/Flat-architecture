# MyFlat

A Blender model of my single-floor flat, built from the 2D floor plan and site photos. It is the source of truth for interior-design experiments, and comes with a local 3D web viewer.

## What's here

| Path | What it is |
|---|---|
| `MyFlat_V1_Architecture.blend` | V1 architecture master (baseline, never modified) |
| `MyFlat_V1_1_Architecture.blend` | V1.1: Room 1 / balcony side corrected from photos |
| `MyFlat_V1_1_Room1_Interiors.blend` | V1.1 + four Room 1 interior designs (DEFAULT, A, B, C) |
| `MyFlat_Trial_V0.blend` | first trial model |
| `build_*.py` | parametric Blender scripts that rebuild each model (dimensions in feet) |
| `*_ASSUMPTIONS.txt` | what is confirmed, taken from the plan, derived or provisional |
| `floorplan_reference.png` | the original plan (not to scale) |
| `renders*/` | validation renders |
| `MyFlat_Viewer/` | browser viewer: walk inside, open wardrobes/doors, lights, night mode, dimensions, design compare |

## Run the viewer

```bash
cd MyFlat_Viewer
python3 -m http.server 8080
```

Then open http://localhost:8080. On a Mac you can also double-click `start.command`. See `MyFlat_Viewer/README.md` for the controls and for how to re-export models from Blender.
