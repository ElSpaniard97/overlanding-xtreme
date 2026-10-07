# Desktop and browser setup

The selected delivery targets are a downloadable desktop build and a browser version of the same UE5 game using Pixel Streaming.

## Downloaded

- Epic Games Launcher: installed at `/Applications/Epic Games Launcher.app`; updated and signed in. UE5.8.3 is installed; Engine/Build/Build.version confirms 5.8.3. The editor completed first launch and opened the offroad project.
- Official Pixel Streaming Infrastructure: `.tools/PixelStreamingInfrastructure`, UE5.8 branch, initial commit `6b8cfb460bda09703e85178f1f77aa6faec9e890`. This is a local tooling checkout excluded from the game repository. Its version must match the UE version installed in the launcher.
- Node.js and Git: already available.

## Pending installation

- The project opened in the editor and standalone mode loaded Lvl_Offroad and spawned the buggy/HUD. Complete driving and streaming verification, then package the desktop build.
- Xcode 26.1.1 (17B100) is installed at `/Applications/Xcode.app` and selected as the active developer directory. First-run agreement/setup completed by the user. `xcodebuild -version` and Clang were verified.
- Apple Metal Toolchain 17B54 is installed. Refreshed the tool lookup cache with `xcrun --kill-cache`; `xcrun metal --version` verified Apple Metal 32023.830, and `xcodebuild -showComponent MetalToolchain -json` confirmed installed status.

## Browser tooling

Dependency download uses `npm ci --ignore-scripts` from the infrastructure root. Install scripts are deferred; the downloaded SFU/native modules are not thereby verified as runnable. The initial local browser prototype will use the signalling server and TypeScript frontend, without the optional SFU. Build Common, Signalling, SignallingWebServer, Frontend/library, Frontend/ui-library and the TypeScript implementation in that order using the repository's documented scripts. Do not claim streaming works until an Unreal application is connected and input/video are tested.

Start with local streaming on this Mac. Public streaming infrastructure, network access and a hosting budget remain to be chosen before production deployment. GitHub Pages can host the website but cannot execute the Unreal game or signalling service. Windows packaging needs a Windows build machine; begin desktop validation on macOS.

## Verified results

`npm ci --ignore-scripts` completed, and `npm run build:all:cjs` successfully built the shared libraries, signalling server and TypeScript browser frontend. Unreal streaming has not been tested because no Unreal streamer is connected to the signalling service yet. The dependency audit reported 62 vulnerabilities across the monorepo; assess production reachability and use patched, engine-compatible releases before exposing a streaming server publicly.
