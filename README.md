# Overlanding Xtreme

A playable browser overlanding prototype inspired by the supplied canyon sunset reference. Drive a stylized fifth-generation Toyota 4Runner TRD Off-Road through a procedural 3D red-rock canyon. Follow the 4.8 km expedition, collect two water caches, reach the summit, and set up camp.

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

This is an initial stylized game prototype, not a photorealistic simulator. The vehicle is modeled from primitive geometry, and the terrain, vegetation, campsite, and map are generated locally. No external 3D models are required. Google Fonts enhance the interface when available; local font fallbacks remain usable offline. `assets/reference.png` preserves the user-supplied visual reference and is not used as the playable scene.
