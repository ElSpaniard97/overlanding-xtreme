# Unreal Engine 5 migration

Status: an initial UE5.8.3 Blueprint offroad project has been created under unreal/OverlandingXtreme from Epic’s installed template and shared content packs. Editor opening and standalone map/vehicle spawn are verified; full driving and streaming validation remain. A generated RedRockRun canyon blockout now loads locally, with verified starting ground and a dedicated PlayCanyon.command launcher. No packaged Unreal executable, imported 4Runner asset, or finished canyon environment has been created. The playable Three.js game remains at the repository root.

## Delivery decision

User selected both desktop packaging and browser delivery through Pixel Streaming. Build one shared UE5 game and deliver it in two forms. GitHub Pages can serve a landing page or streaming client; it cannot run the Unreal application or the streaming/signalling service. Browser delivery needs a compatible game host, network/signalling infrastructure, and a hosting budget. Do not allocate paid infrastructure until the user chooses it.

## Local prerequisites

UE5.8.3 is installed through Epic Games Launcher. The editor completed first launch and opened the offroad project. Xcode 26.1.1 (17B100) is installed and selected, and its Clang compiler was verified. Metal Toolchain 17B54 is installed and its compiler was verified. See SETUP.md for current status. Do not label the project compiled or tested until it has actually opened and run in the editor.

## First playable milestone

1. Create a Games → Vehicle template project with Chaos Vehicles and Enhanced Input. Pin the installed engine version.
2. Replace the template vehicle with a rigged 4Runner asset whose use is licensed for this project. Until that asset is available, label the template vehicle as a placeholder. Build wheel bones, suspension travel, tire friction, mass, center of gravity, and drivetrain around the actual mesh rather than hard-coding generic dimensions.
3. Import RedRockRun.json as a spline/checkpoint source. Convert into a landscape-following route and place two water pickups, summit trigger, and campsite. The source trail has 1.5 km of physical length but displays 4.8 km; preserve the distinction explicitly until the level is redesigned.
4. Port mission completion, fuel, water, vehicle condition, 4H/4L, differential lock, and camp interactions to Blueprint components or C++ with Blueprint exposure. Keep mission and resource state separate from vehicle physics.
5. Use a Spring Arm chase camera with rotation lag and collision probing; retain steering-dependent camera framing and reverse look-back. Drive wheel animation from Chaos wheel outputs in the Animation Blueprint.
6. Verify start, acceleration, steering, brake-before-reverse, camera collision, all five mission goals, and restart in a packaged development build.

## Graphics target from the supplied reference

- Realistic, weathered 4Runner with roof cargo, recovery boards, rear spare, mud, glass reflections, and working lights.
- Sculpted red-rock canyon with a readable rocky trail, layered distant mountains, and a river/lake visible below the lookout.
- Sunset Sky Atmosphere, directional light, volumetric clouds, atmospheric haze, and restrained exposure; the vehicle and trail must remain readable in shadow.
- Landscape material with rock, dirt, gravel, and worn trail blends. Use licensed scanned surfaces and assets. Enable Lumen/Nanite only where supported by the chosen engine, hardware, assets, and performance target.
- Foliage with appropriate distance culling, campsite fabric/props, emissive string lights, campfire, and Niagara dust.
- Rebuild the HUD in UMG with a prominent Start button, compass, objectives, minimap, speedometer, resources, and clearly explained input.

## Repository and release strategy

Keep UE5 files under unreal/OverlandingXtreme once the project exists. Keep large .uasset/.umap and source art in Git LFS or an appropriate asset store, and exclude Binaries, Intermediate, Saved, and DerivedDataCache. Do not commit licensed source assets until their redistribution terms are verified. Keep the existing Pages workflow for the browser prototype until the UE5 build has been validated and its delivery target selected. Publish packaged desktop builds as releases, or publish a streaming client only after a streaming host is operational.

## Sources

- https://dev.epicgames.com/documentation/en-us/unreal-engine/install-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/macos-development-requirements-for-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/pixel-streaming-in-unreal-engine
