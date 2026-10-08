# Pause checkpoint — 2026-10-07

Work resumed on 2026-10-08 at the user's request. GitHub checkpoint 72b5d01 and its Pages deployment were confirmed successful.

## Completed

- UE5.8.3 Blueprint project and Epic offroad vehicle template content.
- RedRockRun canyon blockout generated from the 301 route samples: 300 trail segments, continuous underlying canyon floor, starting platform/barrier, sandstone shapes, river placeholder, and five objective signs.
- Generator loads and rebuilds the existing map and checks creation/saving success.
- Play.command opens the template map; PlayCanyon.command opens the canyon.
- Esc quits the standalone Development prototype. Automatic mouse capture on launch and window cursor locking disabled.
- Local map opening, stable starting ground, and Esc shutdown verified. User confirmed game opening and exit behavior work.

## Known limits / next work

- Terrain is a blockout with flat materials and visible segment edges; it does not yet match the realistic reference.
- Vehicle remains Epic's buggy. Add the 4Runner mesh and rig before representing it as the final vehicle.
- Objective signs are markers; mission progression, pickups, camp, fuel/water, and vehicle condition are not implemented in UE.
- Sustained driving, full route traversal, wheel animation, and camera behavior need validation and refinement.
- Escape uses a Development-only engine binding. Implement a PlayerController pause/quit menu before Shipping builds.
- PixelStreaming2 is enabled and infrastructure tools are installed locally, but no working stream or packaged release exists. GitHub Pages still serves the separate browser prototype.
- Generated map hand edits are replaced when rebuilding. Preserve custom level work separately.

## 2026-10-08 continuation

- Replaced the 300 overlapping trail boxes with one continuous road ribbon (602 shared vertices, 600 upward-facing triangles) with complex-as-simple static collision. Canyon floor remains underneath.
- Level now contains 864 actors. Imported road axes are checked before the map is replaced.
- Generator now requires full editor execution with -ExecutePythonScript because the OBJ importer uses Slate. Commandlet mode crashes inside Epic's importer.
- Added F10 RestartLevel binding for the standalone Development prototype; end-to-end reset remains unverified because preview focus changed during testing.
- Corrected imported mesh coordinates after bounds and visual inspection showed the legacy OBJ importer uses Z-up and flips Y.
- Corrected map loaded and was observed with the vehicle driving at 83 km/h on the continuous road. Full expedition traversal remains unverified.

## Route guidance continuation

- Added non-colliding amber roadside reflectors, bend warnings, 250 m distance signs, a starting controls board, and summit parking with placeholder camp scenery.
- These are static navigation aids. Mission completion and camp interaction remain future work.
- Visual inspection exposed positional Rotator arguments applying the intended yaw as pitch. Generator now uses explicit pitch/yaw/roll keywords for signs, player start, floor, canyon walls, sun, and camp roof.

## Reference graphics continuation

- Added deterministic layered sandstone OBJ geometry with convex collision; replaced stretched sphere canyon walls and removed the 200 box shelves.
- Added world-space procedural color variation to new sand and sandstone materials.
- UE full-editor generation passed: 931 actors. Diff whitespace validation passed.
- Preview launched, but visual inspection was blocked by the Mac lock screen. Rendered materials and new rock silhouettes still need review after unlocking.
- Reference parity remains incomplete: vehicle is the Epic buggy, and realistic vegetation, rock textures, sunset composition, HUD, and interactive campsite remain pending.

## Vegetation and atmosphere continuation

- Unlocked preview confirmed layered rock silhouettes and sand/rock color variation render.
- Added 202 non-colliding clustered desert shrubs, lowered sun pitch to -4 degrees, reduced skylight intensity, and configured height fog.
- Fixed missing UV data in both procedural mesh exporters after an Unreal OBJ importer ensure; generated geometry now supplies a UV index for every face vertex.
- These procedural shrubs remain prototype art, not realistic scanned foliage.
- Corrected exporter rebuild passed with 1,133 actors and no importer errors. Rendered preview confirmed shrubs and warmer rock lighting.
- Preview exposed dark road shadows and a virtual-shadow non-Nanite queue overflow. Raised skylight to 0.65 and configured standard shadow maps; final rendered verification remains pending.

## Acquired cliff integration

- User supplied the Fab UE high-quality archive from Downloads after approving licensing.
- Imported scanned cliff, material, and 4K textures under ignored Content/Licensed/QuixelCliff. Added convex collision and checked dimensions.
- Generator uses the scan for canyon walls when available, with original procedural fallback. Rebuild and game map load succeeded. Rendered inspection remains pending because the preview closed during UI lookup.
- Do not push a map referencing ignored licensed assets without making the repository reproducible (provide acquisition instructions or rebuild fallback map).

## Toyota 4Runner import

- User downloaded Toyota_4runner by sadiqminhas911 from Sketchfab. Extracted `.tools/assets/4runner/scene.gltf`, binary geometry, and CC-BY-4.0 license; attribution added to ASSET_NOTICES.md.
- `Scripts/import_4runner.py` imported all 17 static meshes successfully into ignored `/Game/Licensed/Toyota4Runner/scene`.
- `Scripts/preview_4runner.py` assembles all parts beside the canyon start without collision. Unreal logged FOURRUNNER_PREVIEW_OK parts=17 and saved the map. Python syntax validation passed. Visual alignment still requires rendered review.
- This is a parked art preview. The playable pawn remains the working Epic buggy. Source has 878.5k triangles, no skeleton, and wheels grouped by material across all four corners. Separate wheels, optimize geometry, and adapt to Chaos suspension before replacing the pawn.

## Playable 4Runner continuation

- Added native runtime module and game/editor targets. `AFourRunnerPawn` uses a hidden Epic skeletal chassis carrier with an original single-box SUV physics body. Separate imported static body and tire meshes provide visuals. This is a game approximation, not a detailed vehicle rig.
- `prepare_4runner.py` preserves all 878,504 triangles, reorients forward to +X, separates four wheels, centers their radial pivots, and leaves axle geometry fixed to the body. Prepared assets imported under ignored Content/Licensed/Toyota4Runner/Prepared.
- Correct Chaos wheel references use PhysWheel_FL/FR/BL/BR with measured offsets; never use the chassis root as a wheel reference, since Chaos makes referenced wheel bodies kinematic.
- Corrected excessive spring stiffness (65000 to 650 in the exposed Chaos value scale). Runtime suspension is stable in the current test.
- `setup_4runner.py` creates RedRockRun4Runner using the base canyon as a template and assigns the native game mode. PlayCanyon.command now opens this variant. Base canyon and Play.command retain the buggy.
- Final UE5.8 Mac Development editor build passed. Fixed-step 60 Hz simulation test passed: maximum travel 73.59 m, sustained reverse 19.98 m, steering deflection 2.9 degrees with 5.4 degree heading change, all four contacts, maximum roll 0.4 degrees, camera heading error 0.1 degrees. Script syntax, geometry conservation/dimensions, and Git diff whitespace checks passed.
- New native HUD shows vehicle label, speed/direction, keyboard controls, Esc exit and F10 restart. Cursor is visible and unlocked. Rendered review confirmed the assembled 4Runner and chase framing. Native keyboard tests confirmed W acceleration (9 mph), S braking/reverse (15 mph reverse), Esc exit during an earlier preview, and F10 reload; final preview left open for the user.
- Changes remain local and uncommitted. Neither GitHub Pages nor packaged Unreal deployment was changed. Acquired content remains excluded from Git; map/source setup reproducibility must be addressed before publishing.

## GitHub publication preparation

- User requested repository and Pages updates. Prepared CC-BY 4Runner meshes/materials are now included in Git LFS with source license notice, creator attribution, and modification details. Initial unsplit vehicle import and raw source remain local.
- Preserved the approved scanned environment in ignored Content/LocalOnly/Maps/RedRockRun and RedRockRun4Runner. PlayCanyon.command prefers the local scanned 4Runner map when present; fresh clones open the shared procedural map.
- Replaced all 200 Quixel cliffs in each shared map with original procedural sandstone while preserving placement dimensions. Saved both maps and recursively checked map dependencies: no Quixel or LocalOnly package references. Generator defaults to public procedural maps; OVERLANDING_USE_SCANS=1 targets local-only development maps.
- Public-map fixed-step driving check passed with the same 73.59 m maximum travel / 19.98 m sustained reverse, stable chassis and camera. Browser's 11 tests and production build passed.
- Pages remains the browser edition; native Unreal executable is not deployed on Pages. Workflow now records commit/build time in build-info.json for deployed-version verification.
