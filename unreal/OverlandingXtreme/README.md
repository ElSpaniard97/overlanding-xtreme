# Overlanding Xtreme UE5 prototype

Created from Epic’s installed UE5.8.3 Blueprint Vehicle template with its Vehicles, Input, and Offroad content packs. Opens the Offroad map. The template vehicle is a placeholder, not a Toyota 4Runner. Pixel Streaming 2 is enabled for later local streaming validation.

Validated on this Mac: project opens in the editor; standalone game loads Lvl_Offroad and spawns the buggy with a chase camera and speed/gear HUD. Keyboard driving, wheel motion, suspension, and streaming have not yet been fully verified. Double-click Play.command to run with the installed editor; this is not a packaged desktop release. The canyon art, missions, resources, and licensed 4Runner asset remain to be implemented. Migration route data is in ../Migration/RedRockRun.json.

## Canyon blockout

`PlayCanyon.command` launches `/Game/Overlanding/Maps/RedRockRun` directly. This is an early layout, with the 1.5 km exported route, a broad canyon floor, sandstone formations, river placeholder, low-angle atmospheric sun, and five objective signs. Signs are placement markers; mission interactions are not implemented. The vehicle remains Epic's buggy.

`Scripts/build_red_rock.py` rebuilds this generated map in place. It loads an existing map, removes its actors, and regenerates the environment; hand edits to that map will be replaced. Creation and saving failures raise errors. Ground uses an explicit simple collision mesh. Keep custom work in a separate map until the generator is retired.

The existing `Play.command` still opens the template test map. The canyon is local development work and has not been deployed to Pages or packaged for desktop/streaming.

Validation: canyon generation and saving passed in UE5.8.3 (1,163 actors / 300 trail segments). A fresh standalone session loaded the new map and the vehicle remained on the starting ground across repeated observations; a W tap selected first gear. Sustained driving, the full route, wheel motion, and mission interactions remain unverified.

## Exit and mouse capture

In the standalone Development prototype, press **Esc** to quit the game and release the mouse. The game no longer captures the cursor automatically at launch or locks it to the window. Click the game viewport to focus driving controls. Escape uses an engine Development input binding; a packaged Shipping release will need a PlayerController pause/quit menu instead.

## Cloning from GitHub

Install Git LFS before cloning, or run `git lfs install` and `git lfs pull` after cloning. Unreal `.uasset` and `.umap` files are stored in LFS. Generated caches and local streaming infrastructure are excluded. Open OverlandingXtreme.uproject with UE5.8.3. The command launchers currently use the default macOS engine installation path; other installations can open the project directly in Unreal Editor.
