# Reference environment asset integration

Selected replacement for procedural canyon walls:

- Quixel Megascans, Desert Western Cliff Layered XL 14
- https://www.fab.com/listings/23639c4c-ca70-49f1-b462-afaa454252b2
- Listing checked 2026-10-08: Free, FBX/glTF and source texture maps; physical dimensions 13.57 x 25.7 x 14.84 m.
- User approved licensing and supplied the downloaded UE high-quality package on 2026-10-08. Imported glTF, material, and four 4K textures successfully. Static mesh bounds validated and convex collision added.
- Rendered local canyon inspection passed. Scanned maps now live under ignored Content/LocalOnly; public maps use original procedural walls. Set OVERLANDING_USE_SCANS=1 when generating the optional scanned local maps.

After approval: download FBX tier and basecolor/normal/roughness maps, import into a separate scanned-asset folder, build a PBR material, inspect mesh bounds and collision, then replace canyon formations while preserving road clearance. Keep the procedural fallback until the imported asset renders correctly. Review redistribution terms before committing raw or imported licensed assets to the public GitHub repository.

The smaller Canyon Sandstone Rock listing's free tier is UEFN reference-only; do not treat it as free downloadable UE content. Personal download license was $1.99; no purchase is authorized.

The free CC-BY 4Runner below is now imported and playable. No vehicle purchase has been made.

## Free vehicle shortlist (2026-10-08)

- Toyota_4runner by sadiqminhas: https://sketchfab.com/3d-models/toyota-4runner-3afb8daa0a4a4bfea99e1af74eca1bdb — downloadable, CC Attribution; 878.5k triangles. Closest by vehicle identity, but requires optimization and wheel/rig inspection before playable use.
- Low Poly Suv by hakbux265: https://sketchfab.com/3d-models/low-poly-suv-2091b31981864c51b9860516556ce2b2 — downloadable, CC Attribution; 10.8k triangles. Lightweight generic SUV candidate; visual fit and separate wheels remain unverified.
- Low Poly Detailed SUV by HardSurface3D: https://sketchfab.com/3d-models/low-poly-detailed-suv-7a68a80963504bd3b8b312976ac623bb — downloadable, CC Attribution; 47.8k triangles, not animated. Author reports door/preview issues. Inspect before selecting.

User downloaded the actual Toyota_4runner. The model is adapted into a forward-X body and four pivoted wheel meshes with a native Chaos pawn. Driving, reverse, steering, braking, suspension stability, and chase-camera checks passed. Prepared derivative assets are included in Git LFS with source attribution and the CC-BY-4.0 license link; original download remains local.
