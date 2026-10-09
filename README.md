# Overlanding Xtreme

A playable browser overlanding prototype inspired by the supplied canyon sunset reference. Drive a stylized fifth-generation Toyota 4Runner TRD Off-Road through a procedural 3D red-rock canyon. Follow the 4.8 km expedition, collect two water caches, reach the summit, and set up camp.

Two editions live in this repository:

- **Browser:** [play on GitHub Pages](https://elspaniard97.github.io/overlanding-xtreme/). The Three.js game runs directly in a browser.
- **Unreal Engine 5.8:** the desktop prototype in [unreal/OverlandingXtreme](unreal/OverlandingXtreme/README.md), with an imported Toyota 4Runner, independent tire rotation, front-wheel steering, Chaos suspension/4WD, a chase camera, and canyon scenery. Requires Unreal Engine and a native build; GitHub Pages does not run the Unreal executable.

The shared Unreal maps use original procedural sandstone and include the prepared CC-BY 4Runner assets in Git LFS. Optional Quixel scans and the richer local development maps remain local. See [asset credits](unreal/OverlandingXtreme/ASSET_NOTICES.md) and the Unreal setup instructions.

## Run locally

Requires Node.js 22 or newer.

```sh
npm ci
npm run dev
```

## Controls

- W / arrow up: accelerate
- S / arrow down: brake, then reverse
- A / D or left / right arrows: steer
- Space: brake
- E: interact with water caches and camp when stopped
- L: toggle 4H / 4L
- F: toggle rear differential lock
- Escape: pause
- R: restart

On-screen driving buttons are available on every device. DRIVE engages automatic throttle; STOP applies the brakes. Steering uses the vehicle heading, with speed-dependent steering and a camera that follows turns and looks behind while reversing. Tires rotate with actual travel, front wheels steer, and the body follows terrain slope. Water caches have blue markers. Stop within 32 world meters of a cache and press E. All earlier objectives must be complete before camping. Fast driving outside the trail damages suspension; 4L protects it. The locker improves traction off the trail. Fuel depletion or vehicle damage ends the expedition.

## Verify and deploy

```sh
npm test
npm run build
npm run preview
```

The GitHub Actions workflow tests, builds, and deploys to GitHub Pages on pushes to `main`. In repository Settings → Pages, select **GitHub Actions** as the source. Relative asset paths support the `/overlanding-xtreme/` project URL.

Each Pages deployment writes `build-info.json` containing its Git commit and build time, so the live browser version can be checked against the repository. Unreal changes are published as project source and assets, separately from the Pages build.

This is a stylized game prototype. The browser edition combines optimized external vehicle and scenery models with generated terrain, campsite, and map graphics. Google Fonts enhance the interface when available; local font fallbacks remain usable offline. `assets/reference.png` preserves the user-supplied visual reference and is not used as the playable scene.

### Browser expedition update

The web edition includes an optimized, independently animated Toyota 4Runner,
wheel suspension, brake lights, layered sandstone, desert foliage, solid trail
obstacles, slope resistance, loose-ground traction, and a hill-climb detour
between 500–780 m (dashed line on the map). The course is 1.5 km.

- **WASD / arrows** drive, **Space** brakes, **E** collects water / sets up camp.
- **L** switches 4H/4L; **F** engages the locker. Both improve loose-ground traction.
- **Q** uses one of two recovery kits to return to the last safe trail position.
- **C** cycles chase, wide and hood cameras. **Esc** pauses; **R** starts fresh.
- Sound is optional and starts only when enabled. Graphics Low disables shadows;
  Medium enables shadows; High adds water reflections and higher resolution.
- Progress saves in this browser every three seconds and when leaving the tab.
  Choose **Resume saved expedition** on return. Starting fresh replaces the save.

The 1.55 MB model has 156,125 triangles versus 878,504 in the source.
Attribution appears in **View Rig**, and in [the asset notices](public/models/ATTRIBUTION.md).
To regenerate it from the locally acquired split source, run
`node scripts/prepare-web-4runner.mjs`. Geometry simplification uses
[glTF Transform](https://gltf-transform.dev/modules/functions/functions/simplify),
and Three.js loads its [Meshopt compression](https://threejs.org/docs/pages/GLTFLoader.html).

### Textured canyon scenery

The browser edition uses **Desert Cliff 6** by WireframeArt and juniper and
ponderosa models from **Mountain Trees** by Jagobo, licensed CC BY 4.0.
[Source links and modification notices](public/models/environment/ATTRIBUTION.md)
are also available through View Rig.

The three optimized GLBs total approximately 3.1 MB. Meshopt compression,
smaller textures, instancing, and distance-based visibility keep the scenery
suitable for the browser. Trees preserve existing obstacle locations, and
procedural scenery remains available if model loading fails.

To regenerate from the locally downloaded sources in `.tools/assets/sketchfab-environment`,
run `node scripts/prepare-web-environment.mjs`. Raw source downloads are excluded
from the repository.

### Ground and ride refinement

Ground shading combines generated gravel, mineral grains, erosion cracks, bump
detail and broad color variation, with denser geometry around the driving corridor.
The vehicle body averages its wheel footprint and uses critically damped vertical
suspension, smooth heading/pitch/roll and smaller simulation substeps. The chase
camera stays behind the vehicle when reversing. Eastern bank height transitions
and loose-ground speed reductions are continuous.
