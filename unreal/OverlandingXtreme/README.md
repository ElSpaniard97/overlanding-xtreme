# Overlanding Xtreme UE5 prototype

Created from Epic’s installed UE5.8.3 Vehicle template, now with a native C++ 4Runner pawn. `PlayCanyon.command` opens the local 4Runner canyon variant; `Play.command` retains the original Epic buggy test map. Pixel Streaming 2 is enabled for later streaming validation.

Validated on this Mac: the native 4Runner drives, brakes, reverses, animates its wheels and suspension, and uses a following chase camera. The original Epic buggy remains in Lvl_Offroad. Mission interactions, resource gameplay, streaming, and packaged releases are pending. Migration route data is in ../Migration/RedRockRun.json.

## Canyon blockout

`PlayCanyon.command` launches `/Game/Overlanding/Maps/RedRockRun4Runner` on a fresh clone. If the optional scanned development map exists at `/Game/LocalOnly/Maps/RedRockRun4Runner`, the launcher uses it instead. This is an early layout, with the 1.5 km exported route, a broad canyon floor, sandstone formations, river placeholder, low-angle atmospheric sun, and five objective signs. Signs are placement markers; mission interactions are not implemented. The base `/Game/Overlanding/Maps/RedRockRun` map retains Epic's buggy.

`Scripts/build_red_rock.py` rebuilds this generated map in place. It loads an existing map, removes its actors, and regenerates the environment; hand edits to that map will be replaced. Creation and saving failures raise errors. Ground uses an explicit simple collision mesh. Keep custom work in a separate map until the generator is retired.

The existing `Play.command` still opens the template test map. The canyon is local development work and has not been deployed to Pages or packaged for desktop/streaming.

Validation: canyon generation and saving passed in UE5.8.3 (1,163 actors / 300 trail segments). A fresh standalone session loaded the new map and the vehicle remained on the starting ground across repeated observations; a W tap selected first gear. Sustained driving, the full route, wheel motion, and mission interactions remain unverified.

## Exit and mouse capture

In the standalone Development prototype, press **Esc** to quit the game and release the mouse. The game no longer captures the cursor automatically at launch or locks it to the window. Click the game viewport to focus driving controls. Escape uses an engine Development input binding; a packaged Shipping release will need a PlayerController pause/quit menu instead.

## Cloning from GitHub

Install Git LFS before cloning, or run `git lfs install` and `git lfs pull` after cloning. Unreal `.uasset` and `.umap` files, including the prepared CC-BY 4Runner, are stored in LFS. Generated caches and local streaming infrastructure are excluded. Open OverlandingXtreme.uproject with UE5.8.3 and build the OverlandingXtremeEditor target using a supported native compiler. On this Mac, `Engine/Build/BatchFiles/Mac/Build.sh OverlandingXtremeEditor Mac Development /absolute/path/OverlandingXtreme.uproject -WaitMutex` builds the runtime module for the editor. The command launchers use the default macOS engine installation path; other installations can open the project directly in Unreal Editor. The shared maps have no dependency on downloaded Quixel content.

## Continuous trail update (2026-10-08)

The canyon road now uses one continuous mesh instead of 300 overlapping boxes. Its 602 vertices and 600 triangles share boundaries, removing the stepped road seams. The broader canyon floor remains beneath it. F10 is assigned to restart the level in the standalone Development prototype; this reset still needs a full play-test. Esc remains the quit key.

Run the terrain generator in the full editor with `-ExecutePythonScript=/absolute/path/to/Scripts/build_red_rock.py`, not `-run=pythonscript`: Epic's OBJ importer requires Slate. Generated OBJ source is written to ignored Intermediate output. The helper checks mesh orientation before rebuilding the level. The canyon and vehicle still use placeholder art.

## Route navigation update

Amber reflector posts mark both road edges every 25 m. They have no collision, so clipping a post will not stop the vehicle. Signs warn before larger bends and show distance every 250 m. The starting area displays keyboard controls. The route ends at a broad parking plateau with a small lookout camp. These are navigation and scenery improvements; arrival scoring, camping interactions, and resource management are still pending. Distance signs use the actual 1.5 km prototype route rather than the browser's advertised 4.8 km expedition.

## Environment art pass

Generated layered sandstone replaces the stretched sphere walls and box shelves. Sand and rock have world-space procedural color variation. Clustered evergreen desert shrubs sit outside the road with collision disabled. A lower sun, reduced skylight, and atmospheric fog support a golden-hour lighting direction. The local canyon also uses an acquired Quixel cliff scan when available. Realistic trees, detailed water, expedition equipment, and the full expedition HUD are still pending.

## Playable 4Runner setup

The native pawn uses the acquired Toyota_4runner body with four individually centered tire meshes. Chaos drives a 2,200 kg prototype chassis with a box collision body, measured 2.87 m wheelbase, 42.1 cm tire radius, four-wheel drive, and front-wheel steering. These are game tuning values, not a claim of exact Toyota specifications. Tire rotation, steering, and suspension visuals read the live Chaos wheel state. The chase camera follows vehicle heading with position and rotation lag.

Controls: W/Up drives forward, S/Down brakes when traveling forward and then reverses, A/D or Left/Right steers, Space applies the rear handbrake, Esc exits, and F10 reloads the trail. Click the game window for keyboard focus. The cursor remains visible and unlocked.

Rebuild this local setup in order:

1. Acquire the credited glTF model and extract it to `.tools/assets/4runner` at the repository root. See ASSET_NOTICES.md for attribution and license.
2. Run `python3 Scripts/prepare_4runner.py` to create the oriented body and wheel meshes. The script leaves fixed axle pieces on the body and retains source materials.
3. Build the `OverlandingXtremeEditor` target for your platform using UE5.8 and its supported compiler.
4. Run `Scripts/import_prepared_4runner.py` through Unreal's `-ExecutePythonScript` full-editor mode, then run `Scripts/setup_4runner.py` the same way to create the separate 4Runner canyon map.
5. Launch `PlayCanyon.command` on this Mac or open `RedRockRun4Runner` in the editor.

Prepared CC-BY 4Runner assets under Content/Licensed/Toyota4Runner/Prepared are included in Git LFS with attribution. A fresh clone does not need to download or import this vehicle again; the steps above are for regenerating the meshes. Quixel source content, the initial unsplit vehicle import, raw downloads, and scanned maps under Content/LocalOnly remain excluded. Generated engine binaries and caches are excluded. This Unreal prototype is separate from the browser game on GitHub Pages.

The shared terrain generator defaults to procedural sandstone. To use locally acquired scans, set `OVERLANDING_USE_SCANS=1` when running build_red_rock.py and setup_4runner.py; these runs target Content/LocalOnly. `prepare_publication.py` preserves scanned maps locally and converts the shared maps to procedural canyon walls before publication. It checks that the shared maps do not depend on local-only or Quixel packages.

The source vehicle has about 878k triangles. Unreal's import builds Nanite data, but a dedicated lower-detail vehicle asset and broader performance validation remain future work. The simplified chassis collision does not reproduce individual body panels or a detailed drivetrain.

Validation: Mac Development editor build passed. The `-OverlandingDriveTest -UseFixedTimeStep -FPS=60` standalone simulation check passed acceleration, live tire spin, steering with actual heading change, sustained reverse, braking, four-wheel ground contact, upright stability, and camera heading. Its controlled first-bend sequence covered 73.6 m forward travel and 20.0 m reverse travel; this is not a full-route or performance test.
