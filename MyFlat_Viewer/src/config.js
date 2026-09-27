// ------------------------------------------------------------------
// MyFlat Viewer configuration
// Change the model here, or add models to models/models.json and pick
// them from the dropdown, or open  index.html?model=MyFlat_V2_Architecture.glb
// ------------------------------------------------------------------
export const CONFIG = {
  modelsIndex: './models/models.json',        // list shown in the model dropdown
  modelDir: './models/',
  defaultModel: 'MyFlat_V1_Architecture.glb', // used when models.json has no "default"

  eyeHeight: 1.6,          // m above the floor under you (walkthrough + room views)
  walkSpeed: 1.5,          // m/s
  runMultiplier: 2.2,      // hold Shift
  bodyRadius: 0.22,        // m, collision radius in walkthrough
  maxStepUp: 0.32,         // m, highest step you can climb (stair riser is ~0.2 m)

  // Visibility groups, in panel order. Keys match the "category" written into
  // each object by scripts/export_glb.py. Categories found in a model but not
  // listed here (e.g. future "furniture", "lighting") get a toggle automatically.
  categories: [
    { key: 'walls',    label: 'Walls' },
    { key: 'floors',   label: 'Floors' },
    { key: 'roof',     label: 'Ceiling / Roof' },
    { key: 'doors',    label: 'Doors' },
    { key: 'windows',  label: 'Windows' },
    { key: 'pillars',  label: 'Pillars' },
    { key: 'beams',    label: 'Beams' },
    { key: 'stairs',   label: 'Stairs' },
    { key: 'railings', label: 'Railings' },
    { key: 'vents',    label: 'Vents' },
    { key: 'context',  label: 'Ground' },
    // interior-design categories (written by build_room1_interiors.py)
    { key: 'furniture',       label: 'Furniture' },
    { key: 'wardrobe',        label: 'Wardrobe' },
    { key: 'fenestration',    label: 'Window & door systems' },
    { key: 'soft_furnishing', label: 'Curtains & soft' },
    { key: 'ceiling',         label: 'False ceiling' },
    { key: 'lighting',        label: 'Lighting' },
    { key: 'finishes',        label: 'Finishes' },
    { key: 'balcony',         label: 'Balcony decor' },
    { key: 'plants',          label: 'Plants' },
    { key: 'decor',           label: 'Decor' },
  ],
  planCategory: 'plan_reference',            // handled by Plan Compare, not a toggle
  planOverlayName: 'PLAN_REFERENCE_OVERLAY', // object in the GLB carrying the plan image

  // Status values written in Blender (custom property "status")
  status: {
    CONFIRMED:   { label: 'Confirmed',   color: '#2fa84a' },
    PLAN:        { label: 'Plan value',  color: '#3b78e7' },
    DERIVED:     { label: 'Derived',     color: '#e9c21b' },
    PROVISIONAL: { label: 'Provisional', color: '#f26b0f' },
    REFERENCE:   { label: 'Reference',   color: '#9a9a9a' },
    DESIGN:      { label: 'Interior design', color: '#9b59d0' },
  },
  noStatus: { label: 'No status in model', color: '#d0d0d0' },

  collideCategories: ['walls', 'pillars', 'doors', 'windows', 'railings', 'stairs', 'furniture', 'wardrobe', 'fenestration', 'plants', 'balcony'],
  groundCategories: ['floors', 'stairs', 'roof'],

  roomOrder: ['Room 1', 'Kitchen', 'Bathroom 1', 'Bathroom 2', 'Passage', 'Hall', 'Room 2',
              'Balcony', 'Stair', 'Open Square'],

  // Optional hand-made viewpoints (model coordinates, metres, Y up, north = -Z).
  // Use "Copy current view" in the app to generate an entry, then paste it here.
  // Example: 'Room 1': [{ name: 'Balcony door', pos: [0.5, 1.6, -2], target: [-1, 1.5, -2] }]
  viewpoints: {
    'Room 1': [
      { name: 'Design view (from balcony door)', pos: [0.244, 1.585, 2.591], target: [3.505, 1.006, 0.914] },
      { name: 'Towards balcony (from door side)', pos: [3.597, 1.585, 2.804], target: [0.152, 1.158, 1.067] },
      { name: 'Wardrobe & thick wall', pos: [0.914, 1.585, 0.762], target: [3.048, 1.067, 3.962] },
      { name: 'Balcony (outside, looking south)', pos: [-1.219, 1.524, -0.061], target: [-0.762, 0.762, 3.81] },
    ],
  },
};
